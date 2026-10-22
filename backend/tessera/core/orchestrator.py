"""One-worker, snapshot-bound DAG execution with atomic run publication."""

import logging
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from typing import Any

from sqlalchemy import Engine

from tessera.core.config import Settings, get_settings
from tessera.core.contracts import ModuleManifest, ModuleResult, ModuleRun, RunSpec
from tessera.core.registry import Registry
from tessera.core.repo import Repo, repo_session

_WORKER = Lock()
_SUCCESS = {"succeeded", "degraded"}


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
    entries = {module_id: registry.resolve(snapshots[module_id]) for module_id in plan}
    if spec.mode != "fixture" and any(
        snapshots[module_id].manifest.mode == "fixture" for module_id in plan
    ):
        raise ValueError("fixture modules require a fixture run")
    statuses: dict[str, ModuleRun] = {}
    with _WORKER, repo_session(engine, spec, fixture_mode=spec.mode == "fixture") as repo:
        state = repo.run_state()
        if state["status"] != "pending":
            raise ValueError("run has already been executed; create a new run_id")
        if clients is None:
            from tessera.core.llm import LLMClient

            llm_settings = settings or get_settings()
            if spec.mode != "live":
                llm_settings = llm_settings.model_copy(update={"llm_mode": "replay"})
            clients = {"llm": LLMClient(llm_settings).for_run(spec)}
        repo.set_run_status("running")
        for module_id in plan:
            manifest = snapshots[module_id].manifest
            statuses[module_id] = ModuleRun(
                run_id=spec.run_id, module_id=module_id, mode=manifest.mode, status="pending"
            )
            repo.save_module_run(statuses[module_id])
        for module_id in plan:
            snapshot = snapshots[module_id]
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
                repo.save_module_run(
                    ModuleRun(
                        run_id=spec.run_id,
                        module_id=module_id,
                        mode=manifest.mode,
                        status="running",
                        started_at=started,
                    )
                )
                try:
                    with repo.session.begin_nested():
                        result = entries[module_id].run(
                            RunContext(
                                spec=spec.model_copy(deep=True),
                                repo=repo,
                                clients=clients or {},
                                logger=logger or logging.getLogger("tessera.pipeline"),
                                manifest=manifest.model_copy(deep=True),
                                params=deepcopy(snapshot.params),
                                missing_optional_inputs=missing_optional,
                            )
                        )
                        if not isinstance(result, ModuleResult):
                            raise TypeError("module must return ModuleResult")
                        if (result.module_id, result.module_version) != (
                            module_id,
                            manifest.version,
                        ):
                            raise ValueError("module result identity/version differs from snapshot")
                        if result.status not in _SUCCESS:
                            raise _UnsuccessfulResult(result)
                        if missing_optional:
                            result = result.model_copy(
                                update={
                                    "status": "degraded",
                                    "abstentions": (
                                        *result.abstentions,
                                        "optional modules unavailable: "
                                        + ", ".join(missing_optional),
                                    ),
                                }
                            )
                except _UnsuccessfulResult as exc:
                    result = exc.result
                except Exception as exc:
                    result = ModuleResult(
                        module_id=module_id,
                        module_version=manifest.version,
                        status="failed",
                        counts={},
                        errors=(f"module raised {type(exc).__name__}",),
                        abstentions=(),
                    )
            statuses[module_id] = ModuleRun(
                run_id=spec.run_id,
                module_id=module_id,
                mode=manifest.mode,
                status=result.status,
                started_at=started,
                finished_at=datetime.now(UTC),
                result=result,
            )
            repo.save_module_run(statuses[module_id])
        final = {statuses[module_id].status for module_id in required}
        if "failed" in final:
            repo.set_run_status("failed")
        elif "blocked" in final:
            repo.set_run_status("blocked")
        else:
            degraded = any(status.status != "succeeded" for status in statuses.values())
            repo.publish(status="degraded" if degraded else "succeeded")
    return tuple(statuses.values())
