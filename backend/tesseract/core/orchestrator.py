"""One-worker, snapshot-bound DAG execution with atomic run publication."""

import logging
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from typing import Any

from sqlalchemy import Engine

from tesseract.core.config import Settings, get_settings
from tesseract.core.contracts import ModuleManifest, ModuleResult, ModuleRun, RunSpec
from tesseract.core.registry import Registry
from tesseract.core.run_repo import RunRepo as Repo
from tesseract.core.run_repo import repo_session

_WORKER = Lock()
_SUCCESS = {"succeeded", "degraded"}


def worker_slot() -> Lock:
    """Share the prototype's single worker with snapshot-bound API jobs."""
    return _WORKER


@dataclass(frozen=True)
class RunContext:
    spec: RunSpec
    repo: Repo
    clients: Mapping[str, Any]
    logger: logging.Logger
    manifest: ModuleManifest
    params: Mapping[str, Any]
    missing_optional_inputs: tuple[str, ...] = ()

    @property
    def run_spec(self) -> RunSpec:
        return self.spec


def _plan(spec: RunSpec, modules: Sequence[str] | None) -> tuple[str, ...]:
    snapshots = {snapshot.manifest.id: snapshot for snapshot in spec.modules}
    requested = (
        [
            key
            for key, snapshot in snapshots.items()
            if snapshot.manifest.enabled and snapshot.manifest.mode != "unavailable"
        ]
        if modules is None
        else list(modules)
    )
    unknown = set(requested) - snapshots.keys()
    if unknown:
        raise ValueError(f"unknown selected modules: {', '.join(sorted(unknown))}")
    ordered: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(module_id: str) -> None:
        if module_id in visiting:
            raise ValueError(f"cyclic module dependency: {module_id}")
        if module_id in visited or module_id not in snapshots:
            return
        visiting.add(module_id)
        manifest = snapshots[module_id].manifest
        for dependency in manifest.requires:
            visit(dependency)
        for dependency in manifest.optional_inputs:
            if (
                dependency in snapshots
                and snapshots[dependency].manifest.enabled
                and snapshots[dependency].manifest.mode != "unavailable"
            ):
                visit(dependency)
        visiting.remove(module_id)
        visited.add(module_id)
        ordered.append(module_id)

    for module_id in requested:
        visit(module_id)
    return tuple(ordered)


class _UnsuccessfulResult(Exception):
    def __init__(self, result: ModuleResult) -> None:
        self.result = result


def run(
    spec: RunSpec,
    *,
    engine: Engine,
    registry: Registry | None = None,
    clients: Mapping[str, Any] | None = None,
    modules: Sequence[str] | None = None,
    logger: logging.Logger | None = None,
    settings: Settings | None = None,
) -> tuple[ModuleRun, ...]:
    """Execute the frozen module graph; failed/blocked snapshots stay unpublished.

    ``modules`` selects roots and includes their declared prerequisites. No output
    from another run and no fixture is used to satisfy a missing prerequisite.
    """
    spec = RunSpec.model_validate(spec.model_dump(mode="json"))
    registry = registry if registry is not None else Registry.discover()
    snapshots = {snapshot.manifest.id: snapshot for snapshot in spec.modules}
    plan = _plan(spec, modules)
    roots = (
        [
            key
            for key, snapshot in snapshots.items()
            if snapshot.manifest.enabled and snapshot.manifest.mode != "unavailable"
        ]
        if modules is None
        else list(modules)
    )
    required: set[str] = set()

    def require(module_id: str) -> None:
        if module_id not in snapshots or module_id in required:
            return
        required.add(module_id)
        for dependency in snapshots[module_id].manifest.requires:
            require(dependency)

    for module_id in roots:
        require(module_id)
    runnable = [
        module_id
        for module_id in plan
        if snapshots[module_id].manifest.enabled
        and snapshots[module_id].manifest.mode != "unavailable"
    ]
    # Disabled/unavailable snapshots become blocked; they need no installed code.
    entries = {module_id: registry.resolve(snapshots[module_id]) for module_id in runnable}
    if spec.mode != "fixture" and any(
        snapshots[module_id].manifest.mode == "fixture" for module_id in plan
    ):
        raise ValueError("fixture modules require a fixture run")
    fixture_mode = spec.mode == "fixture"

    def session(*, module_scope: bool = False):
        return repo_session(
            engine, spec, fixture_mode=fixture_mode, module_scope=module_scope, write=True
        )

    statuses: dict[str, ModuleRun] = {}

    def record(status: ModuleRun) -> None:
        # Lifecycle rows commit at once: progress is visible and the write lock is short.
        statuses[status.module_id] = status
        with session() as repo:
            repo.save_module_run(status)

    with worker_slot():
        with session() as repo:
            if repo.run_state()["status"] != "pending":
                raise ValueError("run has already been executed; create a new run_id")
            if clients is None:
                from tesseract.core.llm import LLMClient
                from tesseract.core.systems_cache import systems_factory

                llm_settings = settings or get_settings()
                if spec.mode != "live":
                    llm_settings = llm_settings.model_copy(update={"llm_mode": "replay"})
                clients = {
                    "llm": LLMClient(
                        llm_settings, concurrency=llm_settings.llm_concurrency
                    ).for_run(spec),
                    "systems": systems_factory(llm_settings, spec),
                }
            repo.set_run_status("running")
            for module_id in plan:
                statuses[module_id] = ModuleRun(
                    run_id=spec.run_id,
                    module_id=module_id,
                    mode=snapshots[module_id].manifest.mode,
                    status="pending",
                )
                repo.save_module_run(statuses[module_id])
        try:
            for module_id in plan:
                _execute(
                    module_id,
                    snapshots[module_id],
                    entries,
                    statuses,
                    record,
                    session,
                    spec,
                    clients,
                    logger,
                )
        except BaseException:
            with session() as repo:
                repo.discard_artifacts()
                repo.set_run_status("failed")
            raise
        final = {statuses[module_id].status for module_id in required}
        with session() as repo:
            if final & {"failed", "blocked"}:
                # Unpublished partial outputs of earlier modules are not kept.
                repo.discard_artifacts()
                repo.set_run_status("failed" if "failed" in final else "blocked")
            else:
                degraded = any(status.status != "succeeded" for status in statuses.values())
                repo.publish(status="degraded" if degraded else "succeeded")
    return tuple(statuses.values())


def _execute(module_id, snapshot, entries, statuses, record, session, spec, clients, logger):
    """Run one module in its own transaction; any non-success rolls its writes back."""
    manifest = snapshot.manifest
    started = datetime.now(UTC)
    blockers = [
        dependency
        for dependency in manifest.requires
        if dependency not in statuses or statuses[dependency].status not in _SUCCESS
    ]
    missing_optional = tuple(
        dependency
        for dependency in manifest.optional_inputs
        if dependency not in statuses or statuses[dependency].status not in _SUCCESS
    )
    if not manifest.enabled or manifest.mode == "unavailable" or blockers:
        reason = (
            "module disabled or unavailable"
            if not manifest.enabled or manifest.mode == "unavailable"
            else f"required modules unavailable: {', '.join(blockers)}"
        )
        result = ModuleResult(
            module_id=module_id,
            module_version=manifest.version,
            status="blocked",
            counts={},
            errors=(reason,),
            abstentions=(),
        )
    else:
        record(
            ModuleRun(
                run_id=spec.run_id,
                module_id=module_id,
                mode=manifest.mode,
                status="running",
                started_at=started,
            )
        )
        recordings = getattr((clients or {}).get("systems"), "recordings", None)
        previous_failures = recordings.failures if recordings is not None else 0
        try:
            with session(module_scope=True) as repo:
                result = entries[module_id].run(
                    RunContext(
                        spec=spec.model_copy(deep=True),
                        repo=repo,
                        clients=clients or {},
                        logger=logger or logging.getLogger("tesseract.pipeline"),
                        manifest=manifest.model_copy(deep=True),
                        params=deepcopy(snapshot.params),
                        missing_optional_inputs=missing_optional,
                    )
                )
                if recordings is not None and recordings.failures != previous_failures:
                    recordings.require_complete()
                if not isinstance(result, ModuleResult):
                    raise TypeError("module must return ModuleResult")
                if (result.module_id, result.module_version) != (module_id, manifest.version):
                    raise ValueError("module result identity/version differs from snapshot")
                if result.status not in _SUCCESS:
                    raise _UnsuccessfulResult(result)
                if missing_optional:
                    result = result.model_copy(
                        update={
                            "status": "degraded",
                            "abstentions": (
                                *result.abstentions,
                                "optional modules unavailable: " + ", ".join(missing_optional),
                            ),
                        }
                    )
        except _UnsuccessfulResult as exc:
            result = exc.result
        except Exception as exc:
            logging.getLogger("tesseract.pipeline").exception("module %s failed", module_id)
            result = ModuleResult(
                module_id=module_id,
                module_version=manifest.version,
                status="failed",
                counts={},
                errors=(f"module raised {type(exc).__name__}",),
                abstentions=(),
            )
    record(
        ModuleRun(
            run_id=spec.run_id,
            module_id=module_id,
            mode=manifest.mode,
            status=result.status,
            started_at=started,
            finished_at=datetime.now(UTC),
            result=result,
        )
    )
