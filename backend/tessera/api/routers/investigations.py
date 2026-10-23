"""Explicit investigator jobs on isolated copies of complete run snapshots."""

from datetime import UTC, datetime

import yaml
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response
from sqlalchemy.exc import OperationalError

from tessera.api.models import RunView
from tessera.api.routers.runs import Namespace, engine_for, published_repo, view
from tessera.core.cache import ReplayMiss, cache_key
from tessera.core.config import Settings, get_settings
from tessera.core.contracts import Case, ModuleResult, ModuleRun, ModuleSnapshot, RunSpec
from tessera.core.llm import LLMClient
from tessera.core.orchestrator import worker_slot
from tessera.core.repo import Repo, RunNotFound
from tessera.core.run_repo import RunRepo, repo_session
from tessera.modules.actions.options import policy_from
from tessera.modules.agents import investigator
from tessera.modules.agents.chat_model import model_for_run
from tessera.modules.agents.runtime import ToolError
from tessera.modules.sources.systems_client import (
    SystemsClient,
    SystemsReader,
    Unknown,
    crosswalk_at,
    crosswalk_rows,
)

router = APIRouter(prefix="/api")


def reader_for(repo: RunRepo, settings: Settings):
    rows, _ = crosswalk_rows(settings.sources_dir)
    crosswalk = crosswalk_at(repo, rows)
    if isinstance(crosswalk, Unknown):
        return investigator.UnavailableReader(crosswalk)
    return SystemsReader(repo, SystemsClient(crosswalk, base_url=settings.mocks_base_url))


def job_spec(parent: RunSpec, case: Case, settings: Settings, domain: dict) -> RunSpec:
    mode = (
        "fixture"
        if parent.mode == "fixture"
        else ("live" if settings.llm_mode == "live" else "recorded")
    )
    snapshot = ModuleSnapshot(
        manifest=investigator.MANIFEST.model_copy(update={"mode": mode}),
        params={"case_ids": [case.id]},
    )
    spec = parent.model_copy(
        update={
            "mode": mode,
            "config_hash": cache_key(
                {
                    "parent": parent.config_hash,
                    "domain": domain,
                    "prompt": investigator.PROMPT_PATH.read_text(encoding="utf-8"),
                }
            ),
            "modules": tuple(
                item for item in parent.modules if item.manifest.id != investigator.MANIFEST.id
            )
            + (snapshot,),
            "prompt_versions": {
                **parent.prompt_versions,
                investigator.MANIFEST.id: investigator.PROMPT_VERSION,
            },
            "model_versions": {
                **parent.model_versions,
                investigator.MANIFEST.id: investigator.MODEL,
            },
        }
    )
    # Execution mode does not change admissible evidence. Stable job IDs also keep
    # run IDs appearing in tool payloads stable when rebuilding from recordings.
    identity = spec.model_dump(mode="json", exclude={"mode"})
    for module in identity["modules"]:
        module["manifest"].pop("mode", None)
    identity["case_version"] = case.version
    return spec.model_copy(update={"run_id": "investigate-" + cache_key(identity)})


def execute(job: RunSpec, case_id: str, engine, settings: Settings, policy, horizon: int) -> None:
    fixture = job.mode == "fixture"
    module_id = investigator.MANIFEST.id
    started = datetime.now(UTC)

    def module(status, result=None):
        return ModuleRun(
            run_id=job.run_id,
            module_id=module_id,
            mode=job.mode,
            status=status,
            started_at=started,
            finished_at=datetime.now(UTC) if result is not None else None,
            result=result,
        )

    with worker_slot():
        try:
            with repo_session(engine, job.run_id, fixture_mode=fixture, write=True) as repo:
                if repo.run_state()["status"] != "pending":
                    return
                repo.set_run_status("running")
                repo.save_module_run(module("running"))
            with repo_session(engine, job.run_id, fixture_mode=fixture, write=True) as repo:
                client = LLMClient(settings, concurrency=settings.llm_concurrency).for_run(job)
                case = investigator.visible_case(repo, case_id)
                model = model_for_run(
                    client,
                    prompt_version=investigator.PROMPT_VERSION,
                    model=investigator.MODEL,
                    cache_context={"case": case.model_dump(mode="json")},
                )
                reader = reader_for(repo, settings)
                try:
                    outcome = investigator.investigate(
                        repo,
                        case_id,
                        model=model,
                        reader=reader,
                        policy=policy,
                        horizon_days=horizon,
                    )
                finally:
                    if isinstance(reader, SystemsReader):
                        reader.client.close()
                status = (
                    "degraded"
                    if (
                        outcome.trace.fallback_used
                        or isinstance(reader, investigator.UnavailableReader)
                    )
                    else "succeeded"
                )
                result = ModuleResult(
                    module_id=module_id,
                    module_version=investigator.MANIFEST.version,
                    status=status,
                    counts={"cases": 1, "traces": 1, "fallbacks": int(outcome.trace.fallback_used)},
                    errors=(),
                    abstentions=(),
                )
                repo.save_module_run(module(status, result))
                repo.publish(status)
        except Exception as error:
            # Do not expose provider bodies, credentials or arbitrary exception text.
            reason = (
                "Missing LLM recording (replay miss)"
                if isinstance(error, ReplayMiss)
                else (f"Investigation failed ({type(error).__name__})")
            )
            try:
                with repo_session(engine, job.run_id, fixture_mode=fixture, write=True) as repo:
                    repo.discard_artifacts()
                    result = ModuleResult(
                        module_id=module_id,
                        module_version=investigator.MANIFEST.version,
                        status="failed",
                        counts={},
                        errors=(reason,),
                        abstentions=(),
                    )
                    repo.save_module_run(module("failed", result))
                    repo.set_run_status("failed")
            except RunNotFound:
                pass  # A reset must not recreate an abandoned job.


@router.post("/runs/{run_id}/cases/{case_id}/investigate", response_model=RunView, status_code=202)
def investigate(
    run_id: str,
    case_id: str,
    request: Request,
    response: Response,
    tasks: BackgroundTasks,
    ns: Namespace,
):
    settings = request.app.state.settings or get_settings()
    engine = engine_for(request, ns)
    try:
        with repo_session(engine, run_id, fixture_mode=ns == "fixture", write=True) as parent:
            published_repo(parent)
            if parent.get(Case, case_id) is None:
                raise HTTPException(404, "Case not found")
            try:
                case = investigator.visible_case(parent, case_id)
            except ToolError:
                raise HTTPException(409, "Case is not actionable") from None
            if parent.spec.mode != "live":
                settings = settings.model_copy(update={"llm_mode": "replay"})
            domain = yaml.safe_load(
                (settings.config_dir / "domain.yaml").read_text(encoding="utf-8")
            )
            policy = policy_from(domain["policy"].get("options") or {})
            horizon = int(domain["policy"]["horizon"]["days"]["value"])
            spec = job_spec(parent.spec, case, settings, domain)
            try:
                existing = Repo.open(parent.engine, spec.run_id)
            except RunNotFound:
                job = RunRepo(parent.session, spec, fixture_mode=ns == "fixture")
                job.copy_snapshot(parent)
                job.save_module_run(
                    ModuleRun(
                        run_id=spec.run_id,
                        module_id=investigator.MANIFEST.id,
                        mode=spec.mode,
                        status="pending",
                    )
                )
                tasks.add_task(execute, spec, case_id, engine, settings, policy, horizon)
            else:
                job = RunRepo(parent.session, existing.spec, fixture_mode=ns == "fixture")
            result = view(job)
    except RunNotFound:
        raise HTTPException(404, "Run not found") from None
    except OperationalError as error:
        if "locked" not in str(error.orig):
            raise
        raise HTTPException(503, "Pipeline is writing; retry", {"Retry-After": "5"}) from None
    response.headers["Location"] = f"/api/runs/{result.spec.run_id}" + (
        "?fixture=true" if ns == "fixture" else ""
    )
    return result
