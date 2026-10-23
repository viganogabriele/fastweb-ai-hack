"""HTTP answer acceptance, durable retries and real isolated follow-up execution."""

import pytest
from fastapi.testclient import TestClient

from tessera.api.main import create_app
from tessera.core.config import Settings
from tessera.core.contracts import Clarification, SourceDocument
from tessera.core.run_repo import repo_session
from tessera.modules.agents.answer_registry import register_recorded_answer
from tests.modules.agents.test_answer_registry import setup as answer_setup  # noqa: F401

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
        from tessera.core.registry import Registry

        client.app.state.registry = Registry()
        assert client.post(PATH, json=body.model_dump(mode="json")).status_code == 503
        assert seen == []
