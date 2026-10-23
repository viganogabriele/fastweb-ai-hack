"""Explicit investigator jobs on isolated copies of complete run snapshots."""

from dataclasses import dataclass
from datetime import UTC, datetime

import yaml
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import OperationalError

from tesseract.api.artifacts import CurrentArtifacts
from tesseract.api.models import RunView
from tesseract.api.routers.runs import Namespace, engine_for, published_repo, view
from tesseract.core.cache import ReplayMiss, cache_key
from tesseract.core.config import Settings, get_settings
from tesseract.core.contracts import (
    Case,
    ModuleResult,
    ModuleRun,
    ModuleSnapshot,
    Reservation,
    RunSpec,
)
from tesseract.core.db import erp_rows, runs
from tesseract.core.llm import LLMClient
from tesseract.core.orchestrator import worker_slot
from tesseract.core.repo import Repo, RunNotFound
from tesseract.core.run_repo import RunRepo, repo_session
from tesseract.core.systems_cache import SystemsCache, systems_factory
from tesseract.modules.actions import ledger
from tesseract.modules.actions.options import OptionsPolicy, policy_from
from tesseract.modules.agents import investigator
from tesseract.modules.agents.chat_model import model_for_run
from tesseract.modules.agents.runtime import Budget, ToolError
from tesseract.modules.sources.systems_client import (
    SystemsReader,
    Unknown,
    crosswalk_at,
    crosswalk_rows,
)

router = APIRouter(prefix="/api")


@dataclass(frozen=True)
class JobInputs:
    prompt: str
    crosswalk: tuple[dict[str, str], ...]
    policy: OptionsPolicy
    horizon: int
    reservations: tuple[Reservation, ...]
    generation: datetime


def reader_for(repo: RunRepo, settings: Settings, rows):
    crosswalk = crosswalk_at(repo, rows)
    if isinstance(crosswalk, Unknown):
        return investigator.UnavailableReader(crosswalk)
    cache = SystemsCache(settings.data_dir / "systems_cache")
    reader = SystemsReader(
        repo, systems_factory(settings, repo.spec, cache, allow_recording=True)(crosswalk)
    )
    reader.recordings = cache
    return reader


def job_spec(
    parent: RunSpec,
    case: Case,
    settings: Settings,
    domain: dict,
    *,
    prompt: str,
    crosswalk,
    reservations,
    erp_max_seq: int,
) -> RunSpec:
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
                    "prompt": prompt,
                    "crosswalk": crosswalk,
                    "reservations": [r.model_dump(mode="json") for r in reservations],
                    "provider": settings.fastweb_base_url.rstrip("/"),
                    "systems": settings.mocks_base_url.rstrip("/"),
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
            "erp_max_seq": erp_max_seq,
        }
    )
    # Execution mode does not change admissible evidence. Stable job IDs also keep
    # run IDs appearing in tool payloads stable when rebuilding from recordings.
    identity = spec.model_dump(mode="json", exclude={"mode"})
    for module in identity["modules"]:
        module["manifest"].pop("mode", None)
    identity["case"] = case.model_dump(mode="json")
    return spec.model_copy(update={"run_id": "investigate-" + cache_key(identity)})


def execute(job: RunSpec, case_id: str, engine, settings: Settings, inputs: JobInputs) -> None:
    fixture = job.mode == "fixture"
    module_id = "ag.investigator"
    snapshot = next(item for item in job.modules if item.manifest.id == module_id)
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
                generation = repo.session.execute(
                    select(runs.c.created_at).where(runs.c.run_id == job.run_id)
                ).scalar_one()
                if generation != inputs.generation or repo.run_state()["status"] != "pending":
                    return
                repo.set_run_status("running")
                repo.save_module_run(module("running"))
            with repo_session(engine, job.run_id, fixture_mode=fixture, write=True) as repo:
                generation = repo.session.execute(
                    select(runs.c.created_at).where(runs.c.run_id == job.run_id)
                ).scalar_one()
                if generation != inputs.generation:
                    return
                budget = Budget()
                client = LLMClient(
                    settings,
                    concurrency=settings.llm_concurrency,
                    deadline_seconds=min(settings.llm_deadline_seconds, budget.max_seconds),
                ).for_run(job)
                current = CurrentArtifacts(repo)
                case = investigator.visible_case(current, case_id)
                model = model_for_run(
                    client,
                    prompt_version=job.prompt_versions[module_id],
                    model=job.model_versions[module_id],
                    cache_context={"case": case.model_dump(mode="json")},
                )
                reader = reader_for(current, settings, inputs.crosswalk)
                try:
                    outcome = investigator.investigate(
                        current,
                        case_id,
                        model=model,
                        reader=reader,
                        policy=inputs.policy,
                        horizon_days=inputs.horizon,
                        prompt=inputs.prompt,
                        reservations=inputs.reservations,
                        budget=budget,
                    )
                    # AgentLoop may catch tool failures to produce a safe fallback. Missing
                    # recordings still mean this job is not a reproducible investigation.
                    recordings = getattr(reader, "recordings", None)
                    if recordings is not None:
                        recordings.require_complete()
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
                    module_version=snapshot.manifest.version,
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
                "Missing LLM or systems recording (replay miss)"
                if isinstance(error, ReplayMiss)
                else (f"Investigation failed ({type(error).__name__})")
            )
            try:
                with repo_session(engine, job.run_id, fixture_mode=fixture, write=True) as repo:
                    generation = repo.session.execute(
                        select(runs.c.created_at).where(runs.c.run_id == job.run_id)
                    ).scalar_one()
                    if generation != inputs.generation or repo.run_state()["status"] not in {
                        "pending",
                        "running",
                    }:
                        return
                    repo.discard_artifacts()
                    result = ModuleResult(
                        module_id=module_id,
                        module_version=snapshot.manifest.version,
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
            current = published_repo(parent)
            if current.get(Case, case_id) is None:
                raise HTTPException(404, "Case not found")
            try:
                case = investigator.visible_case(current, case_id)
            except ToolError:
                raise HTTPException(409, "Case is not actionable") from None
            if inspect(parent.session).has_table(ledger.drafts.name):
                decisions = parent.session.execute(
                    select(ledger.drafts.c.payload).where(
                        ledger.drafts.c.scenario_id == parent.spec.scenario_id,
                        ledger.drafts.c.run_id == run_id,
                    )
                ).scalars()
                if any(item["option"]["case_id"] == case_id for item in decisions):
                    raise HTTPException(409, "Case already decided")
            if parent.spec.mode != "live":
                settings = settings.model_copy(update={"llm_mode": "replay"})
            domain = yaml.safe_load(
                (settings.config_dir / "domain.yaml").read_text(encoding="utf-8")
            )
            policy = policy_from(domain["policy"].get("options") or {})
            horizon = int(domain["policy"]["horizon"]["days"]["value"])
            prompt = investigator.PROMPT_PATH.read_text(encoding="utf-8")
            rows, _ = crosswalk_rows(settings.sources_dir)
            reservations = ledger.reservations(parent.engine, parent.spec.scenario_id)
            erp_max_seq = parent.session.execute(select(func.max(erp_rows.c.seq))).scalar() or 0
            if parent.spec.erp_max_seq is not None:
                erp_max_seq = min(erp_max_seq, parent.spec.erp_max_seq)
            spec = job_spec(
                parent.spec,
                case,
                settings,
                domain,
                prompt=prompt,
                crosswalk=rows,
                reservations=reservations,
                erp_max_seq=erp_max_seq,
            )
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
                generation = parent.session.execute(
                    select(runs.c.created_at).where(runs.c.run_id == spec.run_id)
                ).scalar_one()
                inputs = JobInputs(prompt, tuple(rows), policy, horizon, reservations, generation)
                tasks.add_task(
                    execute, spec, case_id, engine, settings.model_copy(deep=True), inputs
                )
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
