"""HTTP boundary regressions: execute snapshots, publish atomically, isolate reads."""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert

from tesseract.api.main import app_engine, create_app
from tesseract.core.config import Settings
from tesseract.core.contracts import (
    Case,
    EntityLink,
    ModuleManifest,
    ModuleResult,
    Observation,
    RunSpec,
    SourceDocument,
)
from tesseract.core.db import artifacts, connect
from tesseract.core.registry import RegisteredModule, Registry
from tesseract.core.run_repo import repo_session

ROOT = Path(__file__).resolve().parents[3]


def body(mode="recorded"):
    return dict(
        scenario_id="historical",
        as_of="2026-10-22T20:00:00Z",
        stores=["MIL01"],
        source_manifest_hash="sources-v1",
        config_hash="config-v1",
        code_version="test-v1",
        mode=mode,
        modules=[],
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=[],
    )


def document(id="doc-1", at="2026-10-22T19:00:00Z", store="MIL01"):
    return SourceDocument(
        id=id,
        version="v1",
        available_at=at,
        availability_basis="received",
        source_refs=(),
        source_type="email",
        connector="src.email",
        uri="dataset://mail",
        content_hash="hash",
        origin=None,
        text="Hi 🧥 店",
        text_version="v1",
        meta={"store_id": store},
    )


@pytest.fixture
def service(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'test.db'}")
    app = create_app(
        engine=engine,
        registry=Registry(),
        fixture_engine=engine,
        settings=Settings(fixture_mode=True),
    )
    with TestClient(app) as client:
        yield client, engine, app
    engine.dispose()


def seed(engine, run_id="run-1", *, published=True, mode="recorded", as_of=None):
    values = body(mode)
    if as_of:
        values["as_of"] = as_of
    spec = RunSpec(run_id=run_id, **values)
    with repo_session(engine, spec, fixture_mode=mode == "fixture") as repo:
        if not as_of:
            repo.put(document())
        # Canonical persistence rejects future writes before the API can expose them.
        with pytest.raises(ValueError):
            repo.put(document("future", "2026-10-23T00:00:00Z"))
        # Bypass the write guard to independently prove the HTTP read clock filter.
        future = document("future", "2026-10-23T00:00:00Z")
        repo.session.execute(
            insert(artifacts).values(
                run_id=spec.run_id,
                kind="SourceDocument",
                id=future.id,
                version=future.version,
                store_id="MIL01",
                available_at=future.available_at,
                payload=future.model_dump(mode="json"),
                input_refs=[],
            )
        )
        foreign = document("foreign", store="NYC01")
        repo.session.execute(
            insert(artifacts).values(
                run_id=spec.run_id,
                kind="SourceDocument",
                id=foreign.id,
                version=foreign.version,
                store_id="NYC01",
                available_at=foreign.available_at,
                payload=foreign.model_dump(mode="json"),
                input_refs=[],
            )
        )
        if published:
            repo.publish()
    return spec


def test_published_reads_are_bound_to_run_namespace_store_and_clock(service):
    client, engine, _ = service
    seed(engine)
    seed(engine, "pending", published=False)
    seed(engine, "fixture-run", mode="fixture")
    seed(engine, "earlier", as_of="2026-10-22T18:00:00Z")
    assert [d["id"] for d in client.get("/api/runs/run-1/documents").json()] == ["doc-1"]
    assert client.get("/api/runs/run-1/documents/future").status_code == 404
    assert client.get("/api/runs/run-1/documents/foreign").status_code == 404
    assert client.get("/api/runs/run-1/documents?store=NYC01").status_code == 422
    assert client.get("/api/runs/pending/documents").status_code == 409
    assert client.get("/api/runs/pending/cases").status_code == 409
    assert client.get("/api/runs/fixture-run/documents").status_code == 404
    assert client.get("/api/runs/fixture-run/documents?fixture=true").status_code == 200
    assert client.get("/api/runs/earlier/documents").json() == []
    assert client.get("/api/runs/no-run/documents/doc-1").status_code == 404
    assert client.get("/api/runs/run-1/documents/doc-1").json()["segments"] == []
    # Encoded dots survive client normalization and reach the handler as a run id.
    traversal = client.get("/api/runs/%2e%2e/documents")
    assert traversal.status_code == 404 and traversal.json()["detail"] == "Run not found"
    assert len(client.get("/api/runs").json()) == 3
    assert len(client.get("/api/runs?fixture=true").json()) == 1


def test_fixture_access_requires_configuration(service):
    client, _, app = service
    app.state.settings = Settings(fixture_mode=False)
    assert client.get("/api/runs?fixture=true").status_code == 403


def test_submission_validates_snapshot_and_executes_persisted_run(service, tmp_path):
    client, engine, app = service
    app.state.settings = Settings(
        _env_file=None, fixture_mode=True, data_dir=tmp_path, llm_mode="live"
    )
    manifest = ModuleManifest(
        id="src.test",
        version="v1",
        layer="sources",
        description="Test source",
        requires=(),
        optional_inputs=(),
        produces=("SourceDocument",),
        enabled=True,
        mode="recorded",
        params_schema={"type": "object", "additionalProperties": False},
    )

    def produce(ctx):
        assert ctx.clients["llm"].settings.data_dir == tmp_path
        assert ctx.clients["llm"].settings.llm_mode == "replay"
        ctx.repo.put(document())
        return ModuleResult(
            module_id="src.test",
            module_version="v1",
            status="succeeded",
            counts={"documents": 1},
            errors=(),
            abstentions=(),
        )

    app.state.registry = Registry([RegisteredModule(manifest, produce)])
    payload = body()
    payload["modules"] = [{"manifest": manifest.model_dump(mode="json"), "params": {}}]
    response = client.post("/api/runs", json=payload)
    assert response.status_code == 202, response.text
    assert response.json()["status"] == "pending"
    run_id = response.json()["spec"]["run_id"]
    metadata = client.get(f"/api/runs/{run_id}").json()
    assert metadata["status"] == "succeeded"
    assert metadata["published"] is True
    assert metadata["module_runs"][0]["result"]["counts"] == {"documents": 1}
    assert client.get(f"/api/runs/{run_id}/documents/doc-1").status_code == 200
    payload["modules"][0]["manifest"]["version"] = "changed"
    assert client.post("/api/runs", json=payload).status_code == 422
    payload["run_id"] = run_id
    assert client.post("/api/runs", json=payload).status_code == 422


def test_invalid_or_implicit_fixture_submissions_are_rejected(service):
    client, _, _ = service
    assert client.post("/api/runs", json=body()).status_code == 422
    assert client.post("/api/runs", json=body("fixture")).status_code == 422
    assert client.post("/api/runs?fixture=true", json=body()).status_code == 422
    payload = body()
    payload["stores"] = ["MIL01", "MIL01"]
    assert client.post("/api/runs", json=payload).status_code == 422


def test_real_data01a_document_fixture_is_served_without_filesystem_endpoint(service):
    client, engine, _ = service
    records = json.loads(
        (ROOT / "data/fixtures/documents/doc-20261002-2112-mil01.json").read_text()
    )
    spec = RunSpec(run_id="real-fixture", **body("fixture"))
    from tesseract.core.contracts import Segment

    kinds = {"SourceDocument": SourceDocument, "Segment": Segment}
    with repo_session(engine, spec, fixture_mode=True) as repo:
        for record in records:
            repo.put(kinds[record["kind"]].model_validate(record["payload"]))
        observations = json.loads(
            (ROOT / "data/fixtures/observations/doc-20261002-2112-mil01.json").read_text()
        )
        for record in observations:
            payload = dict(record["payload"], run_id=spec.run_id, scenario_id=spec.scenario_id)
            observation = Observation.model_validate(payload)
            repo.put(observation)
        link = EntityLink(
            id="link-1",
            version="v1",
            available_at=observation.available_at,
            availability_basis="fixture",
            source_refs=(),
            run_id=spec.run_id,
            scenario_id=spec.scenario_id,
            computed_at=spec.as_of,
            input_refs=(
                {"kind": "Observation", "id": observation.id, "version": observation.version},
            ),
            producer="int.link",
            producer_version="v1",
            observation_id=observation.id,
            status="unlinked",
            level=None,
            candidates=(),
            decided_by="test",
            rationale="No catalog match",
        )
        repo.put(link)
        repo.publish()
    response = client.get("/api/runs/real-fixture/documents/doc-20261002-2112-mil01?fixture=true")
    assert response.status_code == 200
    assert response.json()["segments"]
    assert response.json()["observations"]
    assert response.json()["links"][0]["id"] == "link-1"
    assert client.get("/api/runs/real-fixture/documents/doc-20261002-2112-mil01").status_code == 404


def test_cases_are_versioned_and_filtered(service):
    client, engine, _ = service
    spec = RunSpec(run_id="cases", **body())
    item = Case(
        id="case-1",
        version="v1",
        available_at=spec.as_of,
        availability_basis="test",
        source_refs=(),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=spec.as_of,
        input_refs=(),
        producer="int.cases",
        producer_version="v1",
        case_type="demand",
        store_id="MIL01",
        scope_level="unknown",
        window_start=spec.as_of,
        window_end=spec.as_of,
        status="verify",
        owner="review",
        priority="low",
        priority_reason="unknown SKU",
        first_available_at=spec.as_of,
        last_received_at=spec.as_of,
        supporting=(),
        contradicting=(),
        n_documents=0,
        n_origin_groups=0,
        n_unknown_origins=0,
        blocking_uncertainties=("SKU unknown",),
        context_refs=(),
    )
    with repo_session(engine, spec) as repo:
        repo.put(item)
        repo.publish()
    assert len(client.get("/api/runs/cases/cases?status=verify&store=MIL01").json()) == 1
    assert client.get("/api/runs/cases/cases?status=closed").json() == []
    assert client.get("/api/runs/cases/cases/case-1").json()["scope_level"] == "unknown"
    assert client.get("/api/runs/cases/cases/case-1?version=v2").status_code == 404


def test_failed_module_does_not_publish_partial_documents(service):
    client, _, app = service
    manifest = ModuleManifest(
        id="src.failure",
        version="v1",
        layer="sources",
        description="Failure source",
        requires=(),
        optional_inputs=(),
        produces=("SourceDocument",),
        enabled=True,
        mode="recorded",
        params_schema={"type": "object", "additionalProperties": False},
    )

    def fail(ctx):
        ctx.repo.put(document())
        raise RuntimeError("upstream unavailable")

    app.state.registry = Registry([RegisteredModule(manifest, fail)])
    payload = body()
    payload["modules"] = [{"manifest": manifest.model_dump(mode="json"), "params": {}}]
    response = client.post("/api/runs", json=payload)
    assert response.status_code == 202
    run_id = response.json()["spec"]["run_id"]
    assert client.get(f"/api/runs/{run_id}").json()["status"] == "failed"
    assert client.get(f"/api/runs/{run_id}/documents").status_code == 409
    payload["modules"][0]["params"] = {"unexpected": True}
    assert client.post("/api/runs", json=payload).status_code == 422


def test_health_and_schema_export_do_not_create_database(tmp_path):
    app = create_app(settings=Settings(data_dir=tmp_path / "absent"))
    assert TestClient(app).get("/api/health").status_code == 200
    assert "/api/runs" in app.openapi()["paths"]
    assert not (tmp_path / "absent").exists()


def test_default_engines_physically_isolate_fixture_and_product_with_same_id(tmp_path):
    app = create_app(settings=Settings(data_dir=tmp_path, fixture_mode=True), registry=Registry())
    product = app_engine(app, "product")
    fixture = app_engine(app, "fixture")
    try:
        assert product.url.database != fixture.url.database
        seed(product, "same-id")
        seed(fixture, "same-id", mode="fixture")
        client = TestClient(app)
        assert client.get("/api/runs/same-id").json()["spec"]["mode"] == "recorded"
        assert client.get("/api/runs/same-id?fixture=true").json()["spec"]["mode"] == "fixture"
    finally:
        product.dispose()
        fixture.dispose()


def test_submission_accepts_disabled_uninstalled_snapshot_and_503s_on_held_lock(tmp_path):
    from sqlalchemy import create_engine, event

    from tesseract.core.db import _sqlite_pragmas

    url = f"sqlite:///{tmp_path / 'locked.db'}"
    connect(url).dispose()
    engine = create_engine(url, connect_args={"timeout": 0.2})
    event.listen(engine, "connect", _sqlite_pragmas)
    source = ModuleManifest(
        id="src.test",
        version="v1",
        layer="sources",
        description="Test source",
        requires=(),
        optional_inputs=(),
        produces=("SourceDocument",),
        enabled=True,
        mode="recorded",
        params_schema={},
    )
    missing = source.model_copy(update={"id": "src.missing", "enabled": False})
    registry = Registry([RegisteredModule(source, lambda ctx: None)])
    app = create_app(engine=engine, registry=registry, settings=Settings(_env_file=None))
    payload = body()
    payload["modules"] = [
        {"manifest": m.model_dump(mode="json"), "params": {}} for m in (source, missing)
    ]
    holder = create_engine(url)
    with TestClient(app) as client, holder.connect() as connection:
        connection.exec_driver_sql("BEGIN IMMEDIATE")
        busy = client.post("/api/runs", json=payload)
        assert busy.status_code == 503 and busy.headers["retry-after"] == "5"
        connection.exec_driver_sql("ROLLBACK")
        assert client.post("/api/runs", json=payload).status_code == 202
    holder.dispose()
    engine.dispose()


@pytest.mark.parametrize("suffix", ["", "/documents", "/documents/doc-1", "/cases"])
def test_reset_during_lookup_preserves_snapshot_without_recreating_run(
    service, monkeypatch, suffix
):
    from tesseract.core.repo import Repo as StoredRepo
    from tesseract.core.repo import list_runs, reset_run

    client, engine, _ = service
    seed(engine)
    original = StoredRepo.open
    reset = False

    def open_then_reset(bound_engine, run_id):
        nonlocal reset
        repo = original(bound_engine, run_id)
        if not reset:
            reset = True
            reset_run(engine, run_id)
        return repo

    monkeypatch.setattr(StoredRepo, "open", open_then_reset)
    response = client.get(f"/api/runs/run-1{suffix}")
    assert response.status_code == 200, response.text
    if not suffix:
        assert response.json()["published"] is True
    elif suffix == "/documents":
        assert [item["id"] for item in response.json()] == ["doc-1"]
    elif suffix == "/documents/doc-1":
        assert response.json()["document"]["id"] == "doc-1"
    assert list_runs(engine) == []
    assert client.get(f"/api/runs/run-1{suffix}").status_code == 404


def test_listing_does_not_recreate_runs_reset_after_enumeration(service, monkeypatch):
    from tesseract.api.routers import runs as routes
    from tesseract.core.repo import list_runs, reset_run

    client, engine, _ = service
    seed(engine)
    original = routes.stored_runs

    def list_then_reset(bound_engine):
        result = original(bound_engine)
        reset_run(engine, "run-1")
        return result

    monkeypatch.setattr(routes, "stored_runs", list_then_reset)
    assert client.get("/api/runs").json() == []
    assert list_runs(engine) == []


@pytest.mark.parametrize("outcome", ["succeeded", "degraded", "blocked", "failed"])
def test_active_run_hides_partial_outputs_and_preserves_previous_session(service, outcome):
    from tesseract.core.orchestrator import run

    client, engine, _ = service
    previous = seed(engine, "previous-session")
    source = ModuleManifest(
        id="src.test",
        version="v1",
        layer="sources",
        description="Source committed before the next module completes",
        requires=(),
        optional_inputs=(),
        produces=("SourceDocument",),
        enabled=True,
        mode="recorded",
        params_schema={},
    )
    later = source.model_copy(update={"id": "ing.test", "requires": (source.id,)})
    spec = RunSpec(
        run_id="active-session",
        **dict(
            body(),
            scenario_id="another-session",
            modules=[{"manifest": manifest, "params": {}} for manifest in (source, later)],
        ),
    )
    entered, release = Event(), Event()

    def execute(ctx):
        if ctx.manifest.id == source.id:
            ctx.repo.put(document().model_copy(update={"text": "New session document"}))
            status = "succeeded"
        else:
            entered.set()
            assert release.wait(10), "Test did not release the active module"
            status = outcome
        return ModuleResult(
            module_id=ctx.manifest.id,
            module_version=ctx.manifest.version,
            status=status,
            counts={},
            errors=(),
            abstentions=(),
        )

    registry = Registry([RegisteredModule(manifest, execute) for manifest in (source, later)])
    with ThreadPoolExecutor(max_workers=1) as worker:
        future = worker.submit(run, spec, engine=engine, registry=registry, clients={})
        try:
            assert entered.wait(5), "Pipeline did not reach the second module"
            metadata = client.get("/api/runs/active-session").json()
            assert metadata["status"] == "running"
            assert metadata["published"] is False
            assert {m["module_id"]: m["status"] for m in metadata["module_runs"]} == {
                source.id: "succeeded",
                later.id: "running",
            }
            for suffix in ("documents", "documents/doc-1", "cases", "cases/case-1"):
                assert client.get(f"/api/runs/active-session/{suffix}").status_code == 409
            old = client.get("/api/runs/previous-session/documents/doc-1")
            assert old.status_code == 200
            assert old.json()["document"]["text"] == document().text
            assert client.get("/api/runs/previous-session").json()["spec"] == previous.model_dump(
                mode="json"
            )
        finally:
            release.set()
        future.result(timeout=10)

    metadata = client.get("/api/runs/active-session").json()
    assert metadata["status"] == outcome
    published = outcome in {"succeeded", "degraded"}
    assert metadata["published"] is published
    response = client.get("/api/runs/active-session/documents/doc-1")
    assert response.status_code == (200 if published else 409)
    if published:
        assert response.json()["document"]["text"] == "New session document"
    assert client.get("/api/runs/previous-session/documents/doc-1").json()["document"]["text"] == (
        document().text
    )
