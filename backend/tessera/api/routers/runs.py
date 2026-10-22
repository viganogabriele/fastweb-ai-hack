"""Run submission, metadata and published artifact reads."""

from collections.abc import Iterator
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from jsonschema.exceptions import ValidationError as SchemaError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from tessera.api.models import CreateRun, DocumentDetail, RunView
from tessera.core.config import get_settings
from tessera.core.contracts import (
    Case,
    EntityLink,
    ModuleManifest,
    Observation,
    RunSpec,
    Segment,
    SourceDocument,
)
from tessera.core.db import RunRow
from tessera.core.orchestrator import run
from tessera.core.registry import Registry
from tessera.core.repo import Repo, repo_session

router = APIRouter(prefix="/api")


def engine_for(request: Request):
    from tessera.api.main import app_engine

    return app_engine(request.app)


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
    with Session(engine_for(request)) as session:
        row = session.get(RunRow, (ns, run_id))
        if row is None:
            raise HTTPException(404, "Run not found")
        yield Repo(RunSpec.model_validate(row.spec), session, fixture_mode=ns == "fixture")


RunRepo = Annotated[Repo, Depends(run_repo)]


def published_repo(repo: RunRepo) -> Repo:
    state = repo.run_state()
    if not state["published"] or state["status"] not in {"succeeded", "degraded"}:
        raise HTTPException(409, "Run is not published")
    return repo


PublishedRepo = Annotated[Repo, Depends(published_repo)]


def execute(spec: RunSpec, engine, registry: Registry) -> None:
    try:
        run(spec, engine=engine, registry=registry)
    except Exception:
        # An infrastructure failure must not leave a job claiming to be running.
        with repo_session(engine, spec, fixture_mode=spec.mode == "fixture") as repo:
            if not repo.run_state()["published"]:
                repo.set_run_status("failed")


@router.get("/modules", response_model=tuple[ModuleManifest, ...])
def modules(request: Request):
    return registry_for(request).manifests()


@router.post("/runs", response_model=RunView, status_code=202)
def create_run(request: Request, body: CreateRun, tasks: BackgroundTasks, ns: Namespace):
    try:
        spec = RunSpec(run_id=str(uuid4()), **body.model_dump())
        if (spec.mode == "fixture") != (ns == "fixture"):
            raise ValueError("Run mode must match the explicitly selected namespace")
        if spec.mode == "unavailable":
            raise ValueError("Unavailable mode cannot execute")
        if ns == "product" and spec.authorized_fixture_refs:
            raise ValueError("Product runs cannot authorize fixtures")
        registry = registry_for(request)
        if not any(m.manifest.enabled for m in spec.modules):
            raise ValueError("At least one enabled module is required")
        for snapshot in spec.modules:
            registry.resolve(snapshot)
            if ns == "product" and snapshot.manifest.mode == "fixture":
                raise ValueError("Fixture modules require a fixture run")
    except (ValueError, ValidationError, SchemaError) as error:
        raise HTTPException(422, str(error)) from None
    engine = engine_for(request)
    with repo_session(engine, spec, fixture_mode=ns == "fixture") as repo:
        result = view(repo)
    tasks.add_task(execute, spec, engine, registry)
    return result


@router.get("/runs", response_model=tuple[RunView, ...])
def list_runs(request: Request, ns: Namespace):
    with Session(engine_for(request)) as session:
        rows = session.scalars(select(RunRow).where(RunRow.namespace == ns).order_by(RunRow.run_id))
        return tuple(
            view(Repo(RunSpec.model_validate(row.spec), session, fixture_mode=ns == "fixture"))
            for row in rows
        )


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
    return tuple(c for c in repo.list(Case, store_id=store) if status is None or c.status == status)


@router.get("/runs/{run_id}/cases/{case_id}", response_model=Case)
def case(case_id: str, repo: PublishedRepo, version: str | None = None):
    item = repo.get(Case, case_id, version)
    if item is None:
        raise HTTPException(404, "Case not found")
    return item
