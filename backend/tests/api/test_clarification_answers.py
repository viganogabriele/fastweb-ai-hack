"""HTTP answer acceptance, durable retries and real isolated follow-up execution."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update

from tessera.api.main import create_app
from tessera.api.routers import clarifications
from tessera.core.config import Settings
from tessera.core.contracts import Clarification, SourceDocument
from tessera.core.db import runs
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.run_repo import repo_session
from tessera.modules.agents.answer_registry import register_recorded_answer, submit_answer
from tests.modules.agents import test_answer_registry

# Register the shared pytest fixture without an unused fixture-function import.
answer_setup = test_answer_registry.setup

PATH = "/api/runs/parent/cases/case/clarifications/question/answer"


def client_for(engine, registry):
    return TestClient(
        create_app(
            engine=engine,
            fixture_engine=engine,
            registry=registry,
            settings=Settings(_env_file=None, fixture_mode=True),
        )
    )


def test_answer_document_new_run_and_parent_immutability(answer_setup):
    engine, body, registry, seed, seen, originals = answer_setup
    parent = seed()
    with client_for(engine, registry) as client:
        response = client.post(PATH, json=body.model_dump(mode="json"))
        assert response.status_code == 202
        job = response.json()
        assert job["simulated"] is True
        assert job["run"]["run_id"] != parent.run_id
        assert seen == ["ing.extract", "int.link", "fc.overlay", "act.options"]
        run_id = job["run"]["run_id"]
        state = client.get(f"/api/runs/{run_id}").json()
        assert state["published"] is True
        assert state["spec"] == job["run"]
        document = client.get(f"/api/runs/{run_id}/documents/{job['document']['id']}").json()[
            "document"
        ]
        assert document["text"] == body.text
        assert document["source_type"] == "clarification_reply"
        assert document["meta"]["simulated"] is True
        question = client.get(f"/api/runs/{run_id}/cases/case/clarifications/question").json()
        assert question["status"] == "answered"
        assert question["answer_document_id"] == document["id"]
        assert question["answered_at"] == body.model_dump(mode="json")["received_at"]
        # A retry returns the same immutable job and doesn't run the graph again.
        assert client.post(PATH, json=body.model_dump(mode="json")).json() == job
        assert len(seen) == 4
        changed = body.model_dump(mode="json") | {"text": "Different answer"}
        assert client.post(PATH, json=changed).status_code == 409
    with repo_session(engine, parent.run_id) as repo:
        assert repo.get(Clarification, "question") == originals[-1]
        assert repo.list(SourceDocument) == [originals[0]]


@pytest.mark.parametrize("field", ["run_id", "case_id", "clarification_id"])
def test_route_and_body_must_identify_same_context(answer_setup, field):
    engine, body, registry, seed, seen, _ = answer_setup
    seed()
    with client_for(engine, registry) as client:
        response = client.post(PATH, json=body.model_dump(mode="json") | {field: "other"})
        assert response.status_code == 422
        assert seen == []


@pytest.mark.parametrize(
    "change,expected",
    [
        ({"case_version": "stale"}, 409),
        ({"clarification_version": "stale"}, 409),
        ({"scenario_id": "foreign"}, 422),
        ({"received_at": "2026-10-22T21:00:00"}, 422),
        ({"as_of": "2026-10-22T20:00:00Z"}, 422),
        ({"text": "  "}, 422),
    ],
)
def test_validation_and_stale_errors_do_not_queue_work(answer_setup, change, expected):
    engine, body, registry, seed, seen, _ = answer_setup
    seed()
    with client_for(engine, registry) as client:
        assert client.post(PATH, json=body.model_dump(mode="json") | change).status_code == expected
        assert seen == []


def test_replay_miss_is_explicit_and_registered_event_can_execute(answer_setup):
    engine, body, registry, seed, seen, _ = answer_setup
    seed(mode="recorded")
    with client_for(engine, registry) as client:
        encoded = body.model_dump(mode="json")
        assert client.post(PATH, json=encoded).status_code == 424
        assert seen == []
        register_recorded_answer(engine, body)
        assert client.post(PATH, json=encoded).status_code == 202
        assert len(seen) == 4


def test_namespace_isolation_and_unavailable_pipeline(answer_setup):
    engine, body, registry, seed, seen, _ = answer_setup
    seed()
    with client_for(engine, registry) as client:
        assert (
            client.post(PATH + "?fixture=true", json=body.model_dump(mode="json")).status_code
            == 503
        )
        client.app.state.settings = Settings(_env_file=None, fixture_mode=False)
        assert (
            client.post(PATH + "?fixture=true", json=body.model_dump(mode="json")).status_code
            == 403
        )
        client.app.state.registry = Registry()
        assert client.post(PATH, json=body.model_dump(mode="json")).status_code == 503
        assert seen == []


def test_invalid_frozen_parameters_are_unavailable_without_accepting_input(answer_setup):
    engine, body, registry, seed, seen, _ = answer_setup
    parent = seed()
    entries = []
    snapshots = []
    for snapshot in parent.modules:
        entry = registry.resolve(snapshot)
        manifest = entry.manifest.model_copy(
            update={"params_schema": {"type": "object", "additionalProperties": False}}
        )
        entries.append(RegisteredModule(manifest, entry.run))
        snapshots.append(snapshot.model_copy(update={"manifest": manifest, "params": {"bad": 1}}))
    # ModelSnapshot stores JSON; Registry.resolve validates it against the installed schema.
    frozen = parent.model_copy(update={"modules": tuple(snapshots)})
    with engine.begin() as conn:
        conn.execute(update(runs).values(spec=frozen.model_dump(mode="json")))
    with client_for(engine, Registry(entries)) as client:
        response = client.post(PATH, json=body.model_dump(mode="json"))
        assert response.status_code == 503
        assert response.json()["detail"] == "Frozen pipeline implementation is unavailable"
        assert seen == []
    with engine.connect() as conn:
        assert conn.execute(select(runs.c.run_id)).scalars().all() == [parent.run_id]


def test_registry_discovery_failure_is_unavailable(answer_setup, monkeypatch):
    engine, body, registry, seed, seen, _ = answer_setup
    seed()

    def unavailable(_request):
        raise ValueError("duplicate module implementation")

    monkeypatch.setattr(clarifications, "registry_for", unavailable)
    with client_for(engine, registry) as client:
        assert client.post(PATH, json=body.model_dump(mode="json")).status_code == 503
        assert seen == []


def test_busy_database_is_retryable_without_queuing_work(answer_setup, monkeypatch):
    from sqlite3 import OperationalError as SQLiteError

    from sqlalchemy.exc import OperationalError

    engine, body, registry, seed, seen, _ = answer_setup
    seed()

    def busy(*args, **kwargs):
        raise OperationalError("BEGIN IMMEDIATE", {}, SQLiteError("database is locked"))

    monkeypatch.setattr(clarifications, "submit_answer", busy)
    with client_for(engine, registry) as client:
        response = client.post(PATH, json=body.model_dump(mode="json"))
        assert response.status_code == 503
        assert response.headers["Retry-After"] == "5"
        assert seen == []


@pytest.mark.parametrize("field", ["mode", "fixture_mode", "replay_ready", "store_id"])
def test_client_cannot_override_server_execution_scope(answer_setup, field):
    engine, body, registry, seed, seen, _ = answer_setup
    seed(mode="recorded")
    with client_for(engine, registry) as client:
        response = client.post(PATH, json=body.model_dump(mode="json") | {field: "live"})
        assert response.status_code == 422
        assert seen == []


def test_fixture_answer_executes_and_retries_in_its_namespace(answer_setup):
    engine, body, registry, seed, seen, _ = answer_setup
    seed(mode="fixture")
    register_recorded_answer(engine, body, fixture_mode=True)
    with client_for(engine, registry) as client:
        encoded = body.model_dump(mode="json")
        assert client.post(PATH, json=encoded).status_code == 503
        response = client.post(PATH + "?fixture=true", json=encoded)
        assert response.status_code == 202
        job = response.json()
        assert job["run"]["mode"] == "fixture"
        run_path = f"/api/runs/{job['run']['run_id']}"
        assert client.get(run_path).status_code == 404
        assert client.get(run_path + "?fixture=true").json()["published"] is True
        assert client.post(PATH + "?fixture=true", json=encoded).json() == job
        assert len(seen) == 4


def test_background_failure_preserves_accepted_job_for_same_key_retry(answer_setup, monkeypatch):
    engine, body, registry, seed, seen, _ = answer_setup
    seed()

    def interrupted(*args, **kwargs):
        raise RuntimeError("worker interrupted before claiming the job")

    with client_for(engine, registry) as client:
        encoded = body.model_dump(mode="json")
        with monkeypatch.context() as patch:
            patch.setattr(clarifications, "execute_follow_up", interrupted)
            response = client.post(PATH, json=encoded)
        assert response.status_code == 202
        job = response.json()
        run_path = f"/api/runs/{job['run']['run_id']}"
        state = client.get(run_path).json()
        assert state["status"] == "pending" and state["published"] is False
        assert seen == []
        assert client.post(PATH, json=encoded).json() == job
        assert client.get(run_path).json()["published"] is True
        assert len(seen) == 4


def test_question_cannot_be_answered_through_another_case(answer_setup):
    engine, body, registry, seed, seen, originals = answer_setup
    seed(extra=(originals[-2].model_copy(update={"id": "other-case"}),))
    with client_for(engine, registry) as client:
        response = client.post(
            PATH.replace("/case/", "/other-case/"),
            json=body.model_dump(mode="json") | {"case_id": "other-case"},
        )
        assert response.status_code == 422
        assert seen == []


@pytest.mark.parametrize("mode", ["live", "fixture"])
def test_startup_recovers_accepted_pending_answer_jobs(answer_setup, mode):
    from threading import Event

    engine, body, registry, seed, seen, _ = answer_setup
    seed(mode=mode)
    fixture = mode == "fixture"
    if fixture:
        register_recorded_answer(engine, body, fixture_mode=True)
    job = submit_answer(engine, body, fixture_mode=fixture, registry=registry)
    started, release = Event(), Event()

    def execute(entry):
        def run(ctx):
            started.set()
            assert release.wait(5)
            return entry.run(ctx)

        return RegisteredModule(entry.manifest, run)

    blocking = Registry(execute(registry.resolve(s)) for s in job.run.modules)
    # Startup queues recovery without waiting for the pipeline to finish.
    with client_for(engine, blocking):
        try:
            assert started.wait(5)
        finally:
            release.set()
    with repo_session(engine, job.run.run_id, fixture_mode=fixture) as repo:
        assert repo.run_state()["published"] is True
    assert seen == ["ing.extract", "int.link", "fc.overlay", "act.options"]
    # A second server start cannot re-execute an already published answer job.
    with client_for(engine, registry):
        pass
    assert len(seen) == 4


def test_startup_does_not_recover_an_unauthorized_fixture_job(answer_setup):
    engine, body, registry, seed, seen, _ = answer_setup
    seed(mode="fixture")
    register_recorded_answer(engine, body, fixture_mode=True)
    job = submit_answer(engine, body, fixture_mode=True, registry=registry)
    app = create_app(
        engine=engine,
        fixture_engine=engine,
        registry=registry,
        settings=Settings(_env_file=None, fixture_mode=False),
    )
    with TestClient(app):
        pass
    assert seen == []
    with repo_session(engine, job.run.run_id, fixture_mode=True) as repo:
        assert repo.run_state()["status"] == "pending"


def test_restart_recovers_from_existing_database_without_an_injected_engine(answer_setup, tmp_path):
    from pathlib import Path

    engine, body, registry, seed, seen, _ = answer_setup
    seed()
    job = submit_answer(engine, body, registry=registry)
    settings = Settings(_env_file=None, data_dir=tmp_path)
    engine.dispose()
    Path(engine.url.database).rename(settings.db_path)
    app = create_app(registry=registry, settings=settings)
    assert app.state.engines["product"] is None
    try:
        with TestClient(app):
            pass
        restored = app.state.engines["product"]
        with repo_session(restored, job.run.run_id) as repo:
            assert repo.run_state()["published"] is True
        assert len(seen) == 4
        assert app.state.engines["fixture"] is None
    finally:
        if app.state.engines["product"] is not None:
            app.state.engines["product"].dispose()


def test_startup_preserves_lazy_database_creation(tmp_path):
    settings = Settings(_env_file=None, data_dir=tmp_path / "new", fixture_mode=True)
    app = create_app(registry=Registry(), settings=settings)
    with TestClient(app):
        assert app.state.engines == {"product": None, "fixture": None}
    assert not settings.data_dir.exists()
