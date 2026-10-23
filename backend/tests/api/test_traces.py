"""Agent trace reads use the published run clock, namespace and case boundary."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert

from tesseract.api.main import create_app
from tesseract.core.config import Settings
from tesseract.core.contracts import AgentStep, AgentTrace, ArtifactRef, Case, RunSpec
from tesseract.core.db import artifacts, connect
from tesseract.core.registry import Registry
from tesseract.core.run_repo import repo_session


@pytest.fixture
def service(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'traces.db'}")
    app = create_app(
        engine=engine,
        fixture_engine=engine,
        registry=Registry(),
        settings=Settings(_env_file=None, fixture_mode=True),
    )
    with TestClient(app) as client:
        yield client, engine, app
    engine.dispose()


def spec(run_id="one", mode="recorded"):
    return RunSpec(
        run_id=run_id,
        scenario_id="historical",
        as_of="2026-10-22T20:00:00Z",
        stores=("MIL01",),
        source_manifest_hash="s",
        config_hash="c",
        code_version="t",
        mode=mode,
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )


def common(run):
    return dict(
        version="v1",
        available_at=run.as_of,
        availability_basis="test",
        source_refs=(),
        run_id=run.run_id,
        scenario_id=run.scenario_id,
        computed_at=run.as_of,
        input_refs=(),
        producer="test",
        producer_version="1",
    )


def case(run, id="case-1", store="MIL01"):
    return Case(
        id=id,
        **common(run),
        case_type="unmet_demand",
        store_id=store,
        scope_level="sku",
        scope_id="SKU-999",
        window_start=run.as_of,
        window_end=run.as_of,
        status="open",
        owner="allocation",
        priority="medium",
        priority_reason="test",
        first_available_at=run.as_of,
        last_received_at=run.as_of,
        supporting=(),
        contradicting=(),
        n_documents=1,
        n_origin_groups=1,
        n_unknown_origins=0,
        blocking_uncertainties=(),
        context_refs=(),
    )


def trace(run, id="trace-1", case_id="case-1", version="v1", mode="recorded"):
    fields = common(run) | {"version": version}
    fields["input_refs"] = (ArtifactRef(kind="Case", id=case_id, version="v1"),)
    return AgentTrace(
        id=id,
        **fields,
        case_id=case_id,
        steps=(
            AgentStep(
                tool="get_stock",
                arguments={"sku": "SKU-999"},
                input_refs=fields["input_refs"],
                output_refs=(),
                duration_ms=12,
                error="Stock unavailable",
            ),
        ),
        outcome=f"verify stock {version}",
        fallback_used=True,
        mode=mode,
        tokens_in=10,
        tokens_out=4,
    )


def seed(engine, run_id="one", *, mode="recorded", published=True, with_traces=True):
    run = spec(run_id, mode)
    with repo_session(engine, run, fixture_mode=mode == "fixture") as repo:
        repo.put(case(run), case(run, "case-2"))
        if with_traces:
            repo.put(
                trace(run),
                trace(run, version="v2"),
                trace(run, version="v10"),
                trace(run, id="trace-2", case_id="case-2"),
            )
        if published:
            repo.publish()
    return run


def test_list_and_detail_preserve_payload_and_select_latest_publication(service):
    client, engine, _ = service
    run = seed(engine)
    response = client.get("/api/runs/one/cases/case-1/traces")
    assert response.status_code == 200
    assert response.json() == [trace(run, version="v10").model_dump(mode="json")]
    detail = "/api/runs/one/cases/case-1/traces/trace-1"
    assert client.get(detail).json() == response.json()[0]
    assert client.get(detail + "?version=v1").json() == trace(run).model_dump(mode="json")
    assert client.get(detail + "?version=missing").status_code == 404
    assert response.json()[0]["steps"][0]["error"] == "Stock unavailable"
    assert response.json()[0]["fallback_used"] is True


@pytest.mark.parametrize("path", ["traces", "traces/trace-1"])
def test_publication_case_namespace_and_fixture_guards(service, path):
    client, engine, app = service
    seed(engine)
    seed(engine, "pending", published=False)
    seed(engine, "fixture", mode="fixture")
    assert client.get(f"/api/runs/pending/cases/case-1/{path}").status_code == 409
    assert client.get(f"/api/runs/missing/cases/case-1/{path}").status_code == 404
    assert client.get(f"/api/runs/one/cases/missing/{path}").status_code == 404
    assert client.get(f"/api/runs/fixture/cases/case-1/{path}").status_code == 404
    assert client.get(f"/api/runs/fixture/cases/case-1/{path}?fixture=true").status_code == 200
    app.state.settings = Settings(_env_file=None, fixture_mode=False)
    assert client.get(f"/api/runs/fixture/cases/case-1/{path}?fixture=true").status_code == 403


def test_trace_cannot_be_read_through_another_case_or_run(service):
    client, engine, _ = service
    seed(engine)
    seed(engine, "empty", with_traces=False)
    assert client.get("/api/runs/one/cases/case-1/traces/trace-2").status_code == 404
    assert client.get("/api/runs/one/cases/case-2/traces/trace-1?version=v1").status_code == 404
    assert client.get("/api/runs/empty/cases/case-1/traces/trace-1").status_code == 404
    assert client.get("/api/runs/empty/cases/case-1/traces").json() == []
    with repo_session(engine, "empty") as repo:
        assert repo.list(AgentTrace) == []  # GETs never execute an investigator or write.


def raw(repo, record, store):
    repo.session.execute(
        insert(artifacts).values(
            run_id=repo.spec.run_id,
            kind=type(record).__name__,
            id=record.id,
            version=record.version,
            store_id=store,
            case_id=getattr(record, "case_id", None),
            available_at=record.available_at,
            payload=record.model_dump(mode="json"),
            input_refs=[],
        )
    )


def test_future_and_foreign_store_records_are_not_exposed(service):
    client, engine, _ = service
    run = spec()
    with repo_session(engine, run) as repo:
        repo.put(case(run))
        raw(repo, case(run, "foreign-case", store="NYC01"), "NYC01")
        raw(
            repo,
            trace(run, id="future").model_copy(
                update={
                    "available_at": run.as_of.replace(day=23),
                }
            ),
            "MIL01",
        )
        raw(repo, trace(run, id="foreign", case_id="foreign-case"), "NYC01")
        repo.publish()
    assert client.get("/api/runs/one/cases/case-1/traces").json() == []
    assert client.get("/api/runs/one/cases/case-1/traces/future").status_code == 404
    assert client.get("/api/runs/one/cases/foreign-case/traces").status_code == 404
    assert client.get("/api/runs/one/cases/foreign-case/traces/foreign").status_code == 404


def test_latest_version_is_selected_before_case_filtering(service):
    client, engine, _ = service
    run = spec()
    with repo_session(engine, run) as repo:
        repo.put(
            case(run), case(run, "case-2"), trace(run), trace(run, version="v2", case_id="case-2")
        )
        repo.publish()
    assert client.get("/api/runs/one/cases/case-1/traces").json() == []
    assert client.get("/api/runs/one/cases/case-1/traces/trace-1").status_code == 404
    assert client.get("/api/runs/one/cases/case-1/traces/trace-1?version=v1").status_code == 200
    assert client.get("/api/runs/one/cases/case-2/traces").json()[0]["version"] == "v2"
