"""Run submission, metadata and published artifact reads."""

import logging
from collections.abc import Iterator
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from jsonschema.exceptions import ValidationError as SchemaError
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError

from tesseract.api.artifacts import CurrentArtifacts
from tesseract.api.models import (
    CreateRun,
    DocumentDetail,
    ReportDetail,
    ResolvedReportCitation,
    RunView,
)
from tesseract.core.config import Settings, get_settings
from tesseract.core.contracts import (
    AgentTrace,
    Case,
    EntityLink,
    ForecastAdjustment,
    ModuleManifest,
    Observation,
    Report,
    RunSpec,
    Segment,
    SourceDocument,
)
from tesseract.core.orchestrator import run
from tesseract.core.registry import Registry
from tesseract.core.repo import KINDS, RunNotFound, latest
from tesseract.core.repo import list_runs as stored_runs
from tesseract.core.run_repo import RunRepo as Repo
from tesseract.core.run_repo import repo_session

router = APIRouter(prefix="/api")
logger = logging.getLogger("tesseract.api")


def engine_for(request: Request, ns: str = "product"):
    from tesseract.api.main import app_engine

    return app_engine(request.app, ns)


def registry_for(request: Request) -> Registry:
    return (
        request.app.state.registry
        if request.app.state.registry is not None
        else Registry.discover()
    )


def namespace(request: Request, fixture: bool = False) -> str:
    settings = request.app.state.settings or get_settings()
    if fixture and not settings.fixture_mode:
        raise HTTPException(403, "Fixture namespace requires FIXTURE_MODE=1")
    return "fixture" if fixture else "product"


Namespace = Annotated[str, Depends(namespace)]


def view(repo: Repo) -> RunView:
    return RunView(**repo.run_state(), namespace=repo.namespace, module_runs=repo.module_runs())


def run_repo(request: Request, run_id: str, ns: Namespace) -> Iterator[Repo]:
    engine = engine_for(request, ns)
    try:
        with repo_session(engine, run_id, fixture_mode=ns == "fixture") as repo:
            yield repo
    except RunNotFound:
        raise HTTPException(404, "Run not found") from None


RunRepo = Annotated[Repo, Depends(run_repo)]


def published_repo(repo: RunRepo) -> CurrentArtifacts:
    state = repo.run_state()
    if not state["published"] or state["status"] not in {"succeeded", "degraded"}:
        raise HTTPException(409, "Run is not published")
    return CurrentArtifacts(repo)


PublishedRepo = Annotated[CurrentArtifacts, Depends(published_repo)]


def execute(spec: RunSpec, engine, registry: Registry, settings: Settings) -> None:
    try:
        run(spec, engine=engine, registry=registry, settings=settings)
    except Exception:
        logger.exception("run %s failed outside module execution", spec.run_id)
        # An infrastructure failure must not leave a job claiming to be running.
        with repo_session(engine, spec, fixture_mode=spec.mode == "fixture", write=True) as repo:
            if repo.run_state()["status"] in {"pending", "running"}:
                repo.set_run_status("failed")


@router.get("/modules", response_model=tuple[ModuleManifest, ...])
def modules(request: Request):
    return registry_for(request).manifests()


@router.post("/runs", response_model=RunView, status_code=202)
def create_run(request: Request, body: CreateRun, tasks: BackgroundTasks, ns: Namespace):
    try:
        spec = RunSpec(run_id=str(uuid4()), **body.model_dump())
        if spec.scenario_id == "live-voice":
            # Only /api/voice/process can authorize and freeze a live inbox batch.
            raise ValueError("Live voice runs must be queued through /api/voice/process")
        if (spec.mode == "fixture") != (ns == "fixture"):
            raise ValueError("Run mode must match the explicitly selected namespace")
        if spec.mode == "unavailable":
            raise ValueError("Unavailable mode cannot execute")
        if ns == "product" and spec.authorized_fixture_refs:
            raise ValueError("Product runs cannot authorize fixtures")
        registry = registry_for(request)
        if not any(m.manifest.enabled and m.manifest.mode != "unavailable" for m in spec.modules):
            raise ValueError("At least one enabled, available module is required")
        for snapshot in spec.modules:
            if snapshot.manifest.enabled and snapshot.manifest.mode != "unavailable":
                # Disabled/unavailable snapshots run as blocked and need no installed code.
                registry.resolve(snapshot)
            if ns == "product" and snapshot.manifest.mode == "fixture":
                raise ValueError("Fixture modules require a fixture run")
    except (ValueError, ValidationError, SchemaError) as error:
        raise HTTPException(422, str(error)) from None
    engine = engine_for(request, ns)
    try:
        with repo_session(engine, spec, fixture_mode=ns == "fixture", write=True) as repo:
            result = view(repo)
    except OperationalError as error:
        if "locked" not in str(error.orig):
            raise
        # A module transaction held the write lock past the busy timeout.
        raise HTTPException(503, "Pipeline is writing; retry", {"Retry-After": "5"}) from None
    tasks.add_task(execute, spec, engine, registry, request.app.state.settings or get_settings())
    return result


@router.get("/runs", response_model=tuple[RunView, ...])
def list_runs(request: Request, ns: Namespace):
    engine = engine_for(request, ns)
    result = []
    for spec, _status in stored_runs(engine):
        if (spec.mode == "fixture") != (ns == "fixture"):
            continue
        try:
            with repo_session(engine, spec.run_id, fixture_mode=ns == "fixture") as repo:
                result.append(view(repo))
        except RunNotFound:
            # A reset after enumeration must not recreate this run from its old spec.
            continue
    return tuple(result)


@router.get("/runs/{run_id}", response_model=RunView)
def get_run(repo: RunRepo):
    return view(repo)


@router.get("/runs/{run_id}/documents", response_model=tuple[SourceDocument, ...])
def documents(repo: PublishedRepo, store: str | None = None):
    if store is not None and store not in repo.spec.stores:
        raise HTTPException(422, "Store is outside this run")
    return repo.list(SourceDocument, store_id=store)


@router.get("/runs/{run_id}/documents/{document_id}", response_model=DocumentDetail)
def document(document_id: str, repo: PublishedRepo, version: str | None = None):
    item = repo.get(SourceDocument, document_id, version)
    if item is None:
        raise HTTPException(404, "Document not found")
    segments = tuple(
        s
        for s in repo.list(Segment)
        if s.document_id == item.id and s.text_version == item.text_version
    )
    observations = tuple(
        observation
        for observation in repo.list(Observation)
        if observation.document_id == item.id
        and any(evidence.document_version == item.version for evidence in observation.evidence)
    )
    observation_versions = {(observation.id, observation.version) for observation in observations}
    links = tuple(
        link
        for link in repo.list(EntityLink)
        if any(
            ref.kind == "Observation" and (ref.id, ref.version) in observation_versions
            for ref in link.input_refs
        )
    )
    return DocumentDetail(document=item, segments=segments, observations=observations, links=links)


@router.get("/runs/{run_id}/cases", response_model=tuple[Case, ...])
def cases(repo: PublishedRepo, store: str | None = None, status: str | None = None):
    if store is not None and store not in repo.spec.stores:
        raise HTTPException(422, "Store is outside this run")
    found = latest(repo.list(Case, store_id=store))
    return tuple(c for c in found if status is None or c.status == status)


@router.get("/runs/{run_id}/cases/{case_id}", response_model=Case)
def case(case_id: str, repo: PublishedRepo, version: str | None = None):
    item = repo.get(Case, case_id, version)
    if item is None:
        raise HTTPException(404, "Case not found")
    return item


@router.get("/runs/{run_id}/forecast", response_model=tuple[ForecastAdjustment, ...])
def forecast(repo: PublishedRepo, store: str | None = None, sku: str | None = None):
    """Stored baselines and overlays, including abstentions, from this complete snapshot.

    Producer, case_ids and baseline_ref preserve the distinction between a baseline and
    case-specific scenarios. An absent forecast stays absent: reads never recompute it.
    """
    if store is not None and store not in repo.spec.stores:
        raise HTTPException(422, "Store is outside this run")
    return repo.list(ForecastAdjustment, store_id=store, sku=sku)


def report_detail(item: Report, repo: Repo) -> ReportDetail:
    resolved = []
    for citation in item.citations:
        ref = citation.ref
        kind = KINDS.get(ref.kind)
        artifact = repo.get(kind, ref.id, ref.version) if kind else None
        if artifact is None:
            raise HTTPException(409, "Report citation is unavailable in this run")
        resolved.append(
            ResolvedReportCitation(
                citation=citation,
                artifact=artifact.model_dump(mode="json"),
            )
        )
    return ReportDetail(report=item, citations=tuple(resolved))


def latest_reports(repo: Repo, view: str | None = None) -> tuple[Report, ...]:
    # Repository order is publication order, not a lexical sort of v1/v2/.../v10.
    return tuple(
        sorted(
            (item for item in latest(repo.list(Report)) if view is None or item.view == view),
            key=lambda item: (item.view, item.id),
        )
    )


@router.get("/runs/{run_id}/reports", response_model=tuple[Report, ...])
def reports(repo: PublishedRepo, view: str | None = None):
    items = latest_reports(repo, view)
    for item in items:
        report_detail(item, repo)
    return items


@router.get("/runs/{run_id}/reports/{owner}", response_model=tuple[ReportDetail, ...])
def owner_reports(owner: str, repo: PublishedRepo, view: str | None = None):
    # OUT-01 stores complete briefs grouped by office/priority, rather than one
    # artifact per owner. Select the persisted briefs citing this owner's cases;
    # preserve their text and numbering instead of regenerating on a GET.
    result = []
    for item in latest_reports(repo, view):
        owners = {
            case.owner
            for citation in item.citations
            if citation.ref.kind == "Case"
            if (case := repo.get(Case, citation.ref.id, citation.ref.version)) is not None
        }
        if owner in owners:
            result.append(report_detail(item, repo))
    if not result:
        raise HTTPException(404, "No report for this owner")
    return tuple(result)


@router.get("/runs/{run_id}/cases/{case_id}/traces", response_model=tuple[AgentTrace, ...])
def case_traces(case_id: str, repo: PublishedRepo):
    if repo.get(Case, case_id) is None:
        raise HTTPException(404, "Case not found")
    return tuple(
        sorted(
            (trace for trace in latest(repo.list(AgentTrace)) if trace.case_id == case_id),
            key=lambda trace: trace.id,
        )
    )


@router.get("/runs/{run_id}/cases/{case_id}/traces/{trace_id}", response_model=AgentTrace)
def case_trace(case_id: str, trace_id: str, repo: PublishedRepo, version: str | None = None):
    if version is None and repo.get(Case, case_id) is None:
        raise HTTPException(404, "Case not found")
    trace = repo.get(AgentTrace, trace_id, version)
    if trace is None or trace.case_id != case_id:
        raise HTTPException(404, "Trace not found")
    return trace
