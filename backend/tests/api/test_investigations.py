"""Investigator HTTP jobs: snapshot isolation, atomic publication and offline cache."""

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from openai.types.chat import ChatCompletion

from tessera.api.main import create_app
from tessera.api.routers import investigations as api
from tessera.core.cache import ReplayMiss
from tessera.core.config import Settings
from tessera.core.contracts import ActionOption, AgentTrace, ArtifactRef, Case, Clarification
from tessera.core.db import connect
from tessera.core.llm import LLMClient
from tessera.core.repo import reset_run
from tessera.core.run_repo import repo_session
from tests.api.test_traces import case, common, raw, seed, spec, trace

PATH = "/api/runs/one/cases/case-1/investigate"


@pytest.fixture
def service(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'investigations.db'}")
    settings = Settings(
        _env_file=None,
        fixture_mode=True,
        data_dir=tmp_path,
        fastweb_keys_file=tmp_path / "fake-keys.json",
    )
    app = create_app(engine=engine, fixture_engine=engine, settings=settings)
    with TestClient(app) as client:
        yield client, engine, app
    engine.dispose()


class Provider:
    """Synthetic provider responses, recorded locally; no real-model claim."""

    calls = 0

    def __init__(self, **kwargs):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def create(self, **payload):
        Provider.calls += 1
        if payload["messages"][-1]["role"] == "user":
            tool, args = "get_case_evidence", {"case_id": "case-1"}
        else:
            tool, args = "finish", {"status": "monitor", "rationale": "No action"}
        return ChatCompletion.model_validate(
            {
                "id": "fake-completion",
                "object": "chat.completion",
                "created": 0,
                "model": api.investigator.MODEL,
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "tool_calls",
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": tool,
                                    "type": "function",
                                    "function": {"name": tool, "arguments": json.dumps(args)},
                                }
                            ],
                        },
                    }
                ],
                "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
            }
        )


def use_provider(monkeypatch):
    monkeypatch.setattr(
        api, "LLMClient", lambda settings, **kw: LLMClient(settings, client_factory=Provider, **kw)
    )


def forbid_provider(monkeypatch):
    def forbidden(**_):
        pytest.fail("Replay must not construct a provider client")

    monkeypatch.setattr(
        api, "LLMClient", lambda settings, **kw: LLMClient(settings, client_factory=forbidden, **kw)
    )


def test_record_then_rebuild_job_from_cache_without_provider(service, monkeypatch):
    client, engine, app = service
    parent = seed(engine, mode="live")
    settings = app.state.settings
    settings.fastweb_keys_file.write_text(json.dumps({api.investigator.MODEL: "fake-key"}))
    app.state.settings = settings.model_copy(update={"llm_mode": "record"})
    use_provider(monkeypatch)
    Provider.calls = 0
    response = client.post(PATH)
    assert response.status_code == 202
    job = response.json()["spec"]["run_id"]
    assert job != parent.run_id
    assert response.json()["status"] == "pending"
    assert response.headers["location"] == f"/api/runs/{job}"
    state = client.get(response.headers["location"]).json()
    assert state["published"] and state["status"] == "degraded"  # no ERP systems reader
    traces_url = f"/api/runs/{job}/cases/case-1/traces"
    first = client.get(traces_url).json()
    new = next(t for t in first if t["producer"] == api.investigator.MANIFEST.id)
    assert new["mode"] == "recorded" and new["outcome"] == "monitor"
    assert not new["fallback_used"]
    assert [s["tool"] for s in new["steps"]] == ["get_case_evidence", "finish"]
    assert Provider.calls == 2
    assert client.get("/api/runs/one/cases/case-1/traces").json() == [
        trace(parent, version="v10", mode="recorded").model_dump(mode="json")
    ]
    copied = client.get(f"/api/runs/{job}/cases/case-1").json()
    assert copied == {**case(parent).model_dump(mode="json"), "run_id": job}
    assert client.post(PATH).json()["spec"]["run_id"] == job
    assert Provider.calls == 2  # repeated clicks reuse the completed job

    reset_run(engine, job)
    app.state.settings = settings.model_copy(update={"llm_mode": "replay"})
    forbid_provider(monkeypatch)
    rebuilt = client.post(PATH)
    assert rebuilt.status_code == 202 and rebuilt.json()["spec"]["run_id"] == job
    replayed = client.get(traces_url).json()
    new_replay = next(t for t in replayed if t["producer"] == api.investigator.MANIFEST.id)
    assert new_replay["outcome"] == new["outcome"]
    assert [(s["tool"], s["arguments"]) for s in new_replay["steps"]] == [
        (s["tool"], s["arguments"]) for s in new["steps"]
    ]
    assert Provider.calls == 2


def test_replay_miss_is_explicit_and_discards_the_job_snapshot(service, monkeypatch):
    client, engine, app = service
    seed(engine)
    app.state.settings = app.state.settings.model_copy(update={"llm_mode": "live"})
    forbid_provider(monkeypatch)
    response = client.post(PATH)
    job = response.json()["spec"]["run_id"]
    state = client.get(f"/api/runs/{job}").json()
    assert state["status"] == "failed" and not state["published"]
    assert state["module_runs"][-1]["result"]["errors"] == ["Missing LLM recording (replay miss)"]
    assert client.get(f"/api/runs/{job}/cases/case-1/traces").status_code == 409
    with repo_session(engine, job) as repo:
        assert repo.list(Case) == []
        assert repo.list(AgentTrace) == []
    assert client.get("/api/runs/one/cases/case-1").status_code == 200


def test_pending_job_reuse_and_frozen_scope(service, monkeypatch):
    client, engine, _ = service
    parent = spec()
    with repo_session(engine, parent) as repo:
        repo.put(case(parent))
        raw(
            repo,
            trace(parent, id="future").model_copy(
                update={"available_at": parent.as_of.replace(day=23)}
            ),
            "MIL01",
        )
        raw(repo, case(parent, "foreign", store="NYC01"), "NYC01")
        repo.publish()
    queued = []
    monkeypatch.setattr(api, "execute", lambda *args: queued.append(args))
    response = client.post(PATH)
    job = response.json()["spec"]["run_id"]
    assert client.post(PATH).json() == response.json()
    assert len(queued) == 1
    assert client.get(f"/api/runs/{job}/cases/case-1/traces").status_code == 409
    with repo_session(engine, job) as repo:
        assert repo.spec.as_of == parent.as_of and repo.spec.stores == parent.stores
        assert [c.id for c in repo.list(Case)] == ["case-1"]
        assert repo.list(AgentTrace) == []
    assert client.post("/api/runs/one/cases/foreign/investigate").status_code == 404


@pytest.mark.parametrize("fail", [False, True])
def test_output_artifacts_publish_together_or_roll_back(service, monkeypatch, fail):
    client, engine, _ = service
    seed(engine, with_traces=False)

    def investigate(repo, case_id, **_):
        fields = common(repo.spec) | {
            "input_refs": (ArtifactRef(kind="Case", id=case_id, version="v1"),)
        }
        repo.put(
            ActionOption(
                id="new-option",
                **fields,
                case_id=case_id,
                kind="hold",
                legs=(),
                checks=(),
                assumptions=(),
                valid_until=repo.spec.as_of.replace(day=23),
                recommended=True,
                rationale="Hold",
                input_version_hash="hash",
            ),
            Clarification(
                id="new-question",
                **fields,
                case_id=case_id,
                observation_refs=(),
                question="Which size?",
                asked_at=repo.spec.as_of,
                status="draft",
                simulated=True,
            ),
        )
        if fail:
            raise ReplayMiss("must not expose partial writes")
        record = trace(repo.spec).model_copy(update={"fallback_used": False})
        repo.put(record)
        return SimpleNamespace(trace=record)

    monkeypatch.setattr(api.investigator, "investigate", investigate)
    response = client.post(PATH)
    job = response.json()["spec"]["run_id"]
    base = f"/api/runs/{job}/cases/case-1"
    if fail:
        assert client.get(base + "/options").status_code == 409
        with repo_session(engine, job) as repo:
            assert repo.list(ActionOption) == [] and repo.list(Clarification) == []
    else:
        assert client.get(base + "/options").json()[0]["id"] == "new-option"
        assert client.get(base + "/clarifications").json()[0]["id"] == "new-question"
        assert client.get(base + "/traces").json()[0]["id"] == "trace-1"
    with repo_session(engine, "one") as repo:
        assert repo.list(ActionOption) == [] and repo.list(Clarification) == []


def test_missing_unpublished_closed_cases_and_fixture_guards(service, monkeypatch):
    client, engine, app = service
    seed(engine)
    seed(engine, "pending", published=False)
    seed(engine, "fixture", mode="fixture")
    closed = spec("closed")
    with repo_session(engine, closed) as repo:
        repo.put(case(closed).model_copy(update={"status": "closed"}))
        repo.publish()
    monkeypatch.setattr(api, "execute", lambda *_: None)
    assert client.post("/api/runs/missing/cases/case-1/investigate").status_code == 404
    assert client.post("/api/runs/one/cases/missing/investigate").status_code == 404
    assert client.post("/api/runs/pending/cases/case-1/investigate").status_code == 409
    assert client.post("/api/runs/closed/cases/case-1/investigate").status_code == 409
    path = "/api/runs/fixture/cases/case-1/investigate"
    assert client.post(path).status_code == 404
    response = client.post(path + "?fixture=true")
    assert response.status_code == 202
    assert response.json()["namespace"] == "fixture"
    job = response.json()["spec"]["run_id"]
    assert client.get(f"/api/runs/{job}").status_code == 404
    assert client.get(response.headers["location"]).status_code == 200
    app.state.settings = app.state.settings.model_copy(update={"fixture_mode": False})
    assert client.post(path + "?fixture=true").status_code == 403
