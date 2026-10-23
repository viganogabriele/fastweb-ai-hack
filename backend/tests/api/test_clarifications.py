"""Read-only clarification API: frozen questions, versioning and run boundaries."""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert

from tessera.api.main import create_app
from tessera.core.config import Settings
from tessera.core.contracts import ArtifactRef, Case, Clarification, RunSpec
from tessera.core.db import artifacts, connect
from tessera.core.registry import Registry
from tessera.core.run_repo import repo_session


@pytest.fixture
def service(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'clarifications.db'}")
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
        status="verify",
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


def clarification(run, id="clarification-1", case_id="case-1", version="v1", status="draft"):
    fields = common(run) | {
        "version": version,
        "input_refs": (ArtifactRef(kind="Case", id=case_id, version="v1"),),
    }
    return Clarification(
        id=id,
        **fields,
        case_id=case_id,
        observation_refs=(),
        question="Quale taglia manca? 🧥",
        asked_at=run.as_of - timedelta(hours=1),
        status=status,
        simulated=True,
    )


def seed(engine, run_id="one", *, mode="recorded", published=True, questions=True):
    run = spec(run_id, mode)
    with repo_session(engine, run, fixture_mode=mode == "fixture") as repo:
        repo.put(case(run), case(run, "case-2"))
        if questions:
            repo.put(
                clarification(run),
                clarification(run, version="v2", status="asked"),
                clarification(run, version="v10", status="cancelled"),
                clarification(run, id="clarification-2", case_id="case-2"),
            )
        if published:
            repo.publish()
    return run


def test_latest_version_status_filter_and_original_unicode_payload(service):
    client, engine, _ = service
    run = seed(engine)
    path = "/api/runs/one/cases/case-1/clarifications"
    assert client.get(path).json() == [
        clarification(
            run,
            version="v10",
            status="cancelled",
        ).model_dump(mode="json")
    ]
    assert client.get(path + "?status=draft").json() == []
    assert client.get(path + "?status=cancelled").json() == client.get(path).json()
    assert client.get(path + "?status=invalid").status_code == 422
    assert client.get(path + "/clarification-1").json() == client.get(path).json()[0]
    assert client.get(path + "/clarification-1?version=v1").json() == (
        clarification(run).model_dump(mode="json")
    )
    assert client.get(path + "/clarification-1?version=absent").status_code == 404


@pytest.mark.parametrize("suffix", ["clarifications", "clarifications/clarification-1"])
def test_publication_namespace_and_missing_case_guards(service, suffix):
    client, engine, app = service
    seed(engine)
    seed(engine, "pending", published=False)
    seed(engine, "fixture", mode="fixture")
    assert client.get(f"/api/runs/pending/cases/case-1/{suffix}").status_code == 409
    assert client.get(f"/api/runs/missing/cases/case-1/{suffix}").status_code == 404
    assert client.get(f"/api/runs/one/cases/missing/{suffix}").status_code == 404
    assert client.get(f"/api/runs/fixture/cases/case-1/{suffix}").status_code == 404
    assert client.get(f"/api/runs/fixture/cases/case-1/{suffix}?fixture=true").status_code == 200
    app.state.settings = Settings(_env_file=None, fixture_mode=False)
    assert client.get(f"/api/runs/fixture/cases/case-1/{suffix}?fixture=true").status_code == 403


def test_case_and_run_membership_and_empty_reads_have_no_side_effects(service):
    client, engine, _ = service
    seed(engine)
    seed(engine, "empty", questions=False)
    assert (
        client.get("/api/runs/one/cases/case-1/clarifications/clarification-2").status_code == 404
    )
    assert (
        client.get("/api/runs/one/cases/case-2/clarifications/clarification-1").status_code == 404
    )
    assert (
        client.get("/api/runs/empty/cases/case-1/clarifications/clarification-1").status_code == 404
    )
    assert client.get("/api/runs/empty/cases/case-1/clarifications").json() == []
    with repo_session(engine, "empty") as repo:
        assert repo.list(Clarification) == []


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


def test_future_questions_and_foreign_store_are_not_exposed(service):
    client, engine, _ = service
    run = spec()
    with repo_session(engine, run) as repo:
        repo.put(case(run))
        raw(
            repo,
            clarification(run, id="future").model_copy(
                update={
                    "available_at": run.as_of + timedelta(days=1),
                }
            ),
            "MIL01",
        )
        raw(repo, case(run, "foreign-case", store="NYC01"), "NYC01")
        raw(repo, clarification(run, id="foreign", case_id="foreign-case"), "NYC01")
        repo.publish()
    assert client.get("/api/runs/one/cases/case-1/clarifications").json() == []
    assert client.get("/api/runs/one/cases/case-1/clarifications/future").status_code == 404
    assert client.get("/api/runs/one/cases/foreign-case/clarifications").status_code == 404
    assert client.get("/api/runs/one/cases/foreign-case/clarifications/foreign").status_code == 404


def test_latest_selection_precedes_case_filtering(service):
    client, engine, _ = service
    run = spec()
    with repo_session(engine, run) as repo:
        repo.put(
            case(run),
            case(run, "case-2"),
            clarification(run),
            clarification(run, version="v2", case_id="case-2"),
        )
        repo.publish()
    assert client.get("/api/runs/one/cases/case-1/clarifications").json() == []
    assert (
        client.get("/api/runs/one/cases/case-1/clarifications/clarification-1").status_code == 404
    )
    assert (
        client.get(
            "/api/runs/one/cases/case-1/clarifications/clarification-1?version=v1",
        ).status_code
        == 200
    )
