"""HTTP boundary regressions: execute snapshots, publish atomically, isolate reads."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tessera.api.main import create_app
from tessera.core.config import Settings
from tessera.core.contracts import (
    Case,
    EntityLink,
    ModuleManifest,
    ModuleResult,
    Observation,
    RunSpec,
    SourceDocument,
)
from tessera.core.db import create_schema, make_engine
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.repo import repo_session

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
    engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    create_schema(engine)
    app = create_app(engine=engine, registry=Registry(), settings=Settings(fixture_mode=True))
    with TestClient(app) as client:
        yield client, engine, app
    engine.dispose()


def seed(engine, run_id="run-1", *, published=True, mode="recorded", as_of=None):
    values = body(mode)
    if as_of:
        values["as_of"] = as_of
    spec = RunSpec(run_id=run_id, **values)
    with repo_session(engine, spec, fixture_mode=mode == "fixture") as repo:
        repo.put(document())
        repo.put(document("future", "2026-10-23T00:00:00Z"))
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
    assert client.get("/api/runs/run-1/documents?store=NYC01").status_code == 422
    assert client.get("/api/runs/pending/documents").status_code == 409
    assert client.get("/api/runs/pending/cases").status_code == 409
    assert client.get("/api/runs/fixture-run/documents").status_code == 404
    assert client.get("/api/runs/fixture-run/documents?fixture=true").status_code == 200
    assert client.get("/api/runs/earlier/documents").json() == []
    assert client.get("/api/runs/no-run/documents/doc-1").status_code == 404
    assert client.get("/api/runs/run-1/documents/doc-1").json()["segments"] == []
    assert client.get("/api/runs/run-1/documents/../../etc/passwd").status_code == 404
    assert len(client.get("/api/runs").json()) == 3
    assert len(client.get("/api/runs?fixture=true").json()) == 1


def test_fixture_access_requires_configuration(service):
    client, _, app = service
    app.state.settings = Settings(fixture_mode=False)
    assert client.get("/api/runs?fixture=true").status_code == 403


def test_submission_validates_snapshot_and_executes_persisted_run(service):
    client, engine, app = service
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
    from tessera.core.contracts import Segment

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
