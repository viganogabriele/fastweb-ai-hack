"""Investigator HTTP jobs: snapshot isolation, atomic publication and offline cache."""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier, Event
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from openai.types.chat import ChatCompletion
from sqlalchemy import insert, select, update

from tessera.api.main import create_app
from tessera.api.routers import investigations as api
from tessera.core.cache import ReplayMiss
from tessera.core.config import Settings
from tessera.core.contracts import (
    ActionOption,
    AgentTrace,
    ArtifactRef,
    Case,
    Clarification,
    Reservation,
)
from tessera.core.db import artifacts, connect, runs
from tessera.core.llm import LLMClient
from tessera.core.repo import ErpRecord, Repo, put_erp, reset_run
from tessera.core.run_repo import repo_session
from tessera.modules.actions import approval
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


def test_historical_support_cannot_start_an_investigation(service, monkeypatch):
    client, engine, _ = service
    parent = spec()
    with repo_session(engine, parent) as repo:
        repo.put(case(parent).model_copy(update={"version": "parent:answer:1"}))
        repo.publish()
    forbid_provider(monkeypatch)
    assert client.post(PATH).status_code == 404
    assert client.get("/api/runs/one/cases").json() == []


def test_investigation_worker_filters_support_and_keeps_exact_citations(service, monkeypatch):
    client, engine, _ = service
    parent = spec()
    historical = case(parent, "gone").model_copy(update={"version": "parent:answer:1"})
    with repo_session(engine, parent) as repo:
        repo.put(case(parent), historical)
        repo.publish()
    inspected = []

    def investigate(repo, case_id, **_):
        assert [c.id for c in repo.list(Case)] == ["case-1"]
        assert repo.get(Case, "gone") is None
        pin = repo.get(Case, "gone", historical.version)
        assert pin is not None and pin.run_id == repo.run_id
        output = trace(repo.spec).model_copy(
            update={
                "id": "fresh-trace",
                "input_refs": (
                    ArtifactRef(
                        kind="Case",
                        id=pin.id,
                        version=pin.version,
                    ),
                ),
            }
        )
        repo.put(output)
        inspected.append(repo.run_id)
        return SimpleNamespace(trace=output)

    forbid_provider(monkeypatch)
    monkeypatch.setattr(api.investigator, "investigate", investigate)
    response = client.post(PATH)
    assert response.status_code == 202
    job_id = response.json()["spec"]["run_id"]
    assert inspected == [job_id]
    assert client.get(f"/api/runs/{job_id}").json()["published"]
    assert [c["id"] for c in client.get(f"/api/runs/{job_id}/cases").json()] == ["case-1"]
    pinned = client.get(f"/api/runs/{job_id}/cases/gone", params={"version": historical.version})
    assert pinned.status_code == 200 and pinned.json()["run_id"] == job_id


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


def test_queued_job_uses_submitted_prompt_model_crosswalk_and_settings(
    service, monkeypatch, tmp_path
):
    client, engine, app = service
    seed(engine, mode="live")
    original_model = api.investigator.MODEL
    app.state.settings.fastweb_keys_file.write_text(json.dumps({original_model: "fake-key"}))
    app.state.settings = app.state.settings.model_copy(update={"llm_mode": "record"})
    prompt = tmp_path / "prompt.md"
    prompt.write_text("The frozen investigator prompt")
    monkeypatch.setattr(api.investigator, "PROMPT_PATH", prompt)
    monkeypatch.setattr(api, "crosswalk_rows", lambda _: ([{"test": "original"}], {}))
    queued, payloads, reader_rows = [], [], []
    execute, reader_for = api.execute, api.reader_for
    monkeypatch.setattr(api, "execute", lambda *args: queued.append(args))

    class InspectProvider(Provider):
        def create(self, **payload):
            payloads.append(payload)
            return super().create(**payload)

    monkeypatch.setattr(
        api,
        "LLMClient",
        lambda settings, **kw: LLMClient(settings, client_factory=InspectProvider, **kw),
    )

    def reader(repo, settings, rows):
        reader_rows.append(rows)
        return reader_for(repo, settings, rows)

    monkeypatch.setattr(api, "reader_for", reader)
    response = client.post(PATH)
    job = response.json()["spec"]["run_id"]
    prompt.write_text("A later prompt must not execute in this job")
    monkeypatch.setattr(api.investigator, "MODEL", "changed-model")
    monkeypatch.setattr(api.investigator, "PROMPT_VERSION", "changed-version")
    monkeypatch.setattr(api, "crosswalk_rows", lambda _: pytest.fail("crosswalk reread"))
    app.state.settings.llm_mode = "replay"
    execute(*queued[0])
    state = client.get(response.headers["location"]).json()
    assert state["published"]
    assert all(p["model"] == original_model for p in payloads)
    assert payloads[0]["messages"][0]["content"] == "The frozen investigator prompt"
    assert reader_rows == [({"test": "original"},)]
    assert client.get(f"/api/runs/{job}/cases/case-1/traces").status_code == 200


def test_erp_boundary_survives_new_loads_and_reopening(service, monkeypatch):
    client, engine, _ = service
    parent = seed(engine)

    def row(id, store="MIL01", available=None):
        return ErpRecord(
            "sales",
            id,
            "v1",
            available or parent.as_of,
            "test",
            (),
            {"store_id": store, "sku": "SKU-999"},
        )

    put_erp(
        engine,
        [
            row("original"),
            row("foreign", "NYC01"),
            row("future", available=parent.as_of + timedelta(days=1)),
        ],
    )
    monkeypatch.setattr(api, "execute", lambda *_: None)
    response = client.post(PATH)
    job = response.json()["spec"]["run_id"]
    put_erp(engine, [row("late-loaded-but-historically-available")])
    # The canonical repo applies the insertion boundary as well as availability.
    assert {r.id for r in Repo.open(engine, job).erp("sales")} == {"original", "foreign"}
    with repo_session(engine, job) as repo:
        assert [r.id for r in repo.erp("sales")] == ["original"]
    with repo_session(engine, "one") as repo:
        assert len(repo.erp("sales")) == 2
    # Changed admissible ERP input creates another job, rather than reusing stale output.
    assert client.post(PATH).json()["spec"]["run_id"] != job
    with repo_session(engine, job) as repo:
        repo.save_module_run(repo.module_runs()[-1].model_copy(update={"status": "succeeded"}))
        repo.publish()
    child = client.post(f"/api/runs/{job}/cases/case-1/investigate").json()["spec"]["run_id"]
    with repo_session(engine, child) as repo:
        assert [r.id for r in repo.erp("sales")] == ["original"]


def test_stale_queued_task_cannot_execute_a_reset_recreated_job(service, monkeypatch):
    client, engine, _ = service
    seed(engine)
    queued, calls = [], []
    execute = api.execute
    monkeypatch.setattr(api, "execute", lambda *args: queued.append(args))
    monkeypatch.setattr(api.investigator, "investigate", lambda *a, **kw: calls.append(a))
    job = client.post(PATH).json()["spec"]["run_id"]
    reset_run(engine, job)
    assert client.post(PATH).json()["spec"]["run_id"] == job
    execute(*queued[0])
    assert calls == []
    assert client.get(f"/api/runs/{job}").json()["status"] == "pending"


def test_simultaneous_submissions_create_and_queue_one_job(service, monkeypatch):
    client, engine, _ = service
    seed(engine)
    queued = []
    monkeypatch.setattr(api, "execute", lambda *args: queued.append(args))
    barrier = Barrier(2)

    def submit():
        barrier.wait(timeout=5)
        return client.post(PATH)

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: submit(), range(2)))
    assert [r.status_code for r in responses] == [202, 202]
    assert responses[0].json() == responses[1].json()
    assert len(queued) == 1


def test_running_outputs_are_hidden_until_atomic_publication(service, monkeypatch):
    client, engine, _ = service
    seed(engine, with_traces=False)
    queued = []
    execute = api.execute
    monkeypatch.setattr(api, "execute", lambda *args: queued.append(args))
    entered, release = Event(), Event()

    def investigate(repo, case_id, **_):
        record = trace(repo.spec)
        repo.put(record)
        entered.set()
        assert release.wait(timeout=10)
        return SimpleNamespace(trace=record)

    monkeypatch.setattr(api.investigator, "investigate", investigate)
    response = client.post(PATH)
    job = response.json()["spec"]["run_id"]
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending = pool.submit(execute, *queued[0])
        try:
            assert entered.wait(timeout=5)
            assert client.get(response.headers["location"]).json()["status"] == "running"
            assert client.get(f"/api/runs/{job}/cases/case-1/traces").status_code == 409
            assert client.get("/api/runs/one/cases/case-1").status_code == 200
        finally:
            release.set()
        pending.result(timeout=5)
    assert client.get(f"/api/runs/{job}/cases/case-1/traces").json()[0]["id"] == "trace-1"


def test_failed_job_sanitizes_errors_and_reuses_failure_without_new_execution(service, monkeypatch):
    client, engine, _ = service
    seed(engine)
    calls = []

    def investigate(*_, **kwargs):
        calls.append(kwargs)
        raise RuntimeError("sensitive-provider-body")

    monkeypatch.setattr(api.investigator, "investigate", investigate)
    response = client.post(PATH)
    state = client.get(response.headers["location"])
    assert state.json()["status"] == "failed"
    assert "sensitive-provider-body" not in state.text
    assert state.json()["module_runs"][-1]["result"]["errors"] == [
        "Investigation failed (RuntimeError)"
    ]
    assert client.post(PATH).json()["spec"]["run_id"] == response.json()["spec"]["run_id"]
    assert len(calls) == 1


def test_snapshot_preserves_all_versions_order_and_exact_references(service, monkeypatch):
    client, engine, _ = service
    parent = seed(engine)
    queued = []
    monkeypatch.setattr(api, "execute", lambda *args: queued.append(args))
    job = client.post(PATH).json()["spec"]["run_id"]
    with repo_session(engine, job) as copied, repo_session(engine, "one") as source:
        assert [t.version for t in copied.list(AgentTrace, case_id="case-1")] == ["v1", "v2", "v10"]
        for original in source.list(AgentTrace):
            record = copied.get(AgentTrace, original.id, original.version)
            assert record == original.model_copy(update={"run_id": job})
            for ref in record.input_refs:
                assert copied.get(Case, ref.id, ref.version) is not None
        assert copied.spec.scenario_id == parent.scenario_id


def test_existing_database_specs_without_optional_boundary_still_open(service):
    _, engine, _ = service
    parent = seed(engine)
    old = parent.model_dump(mode="json", exclude={"erp_max_seq"})
    with engine.begin() as conn:
        conn.execute(update(runs).where(runs.c.run_id == parent.run_id).values(spec=old))
    with repo_session(engine, "one") as repo:
        assert repo.spec.erp_max_seq is None
        assert repo.get(Case, "case-1") is not None


def test_submission_rollback_does_not_leave_a_partial_job(service, monkeypatch):
    client, engine, _ = service
    seed(engine)
    original = api.RunRepo.copy_snapshot

    def fail(self, source):
        original(self, source)
        raise RuntimeError("copy failed")

    monkeypatch.setattr(api.RunRepo, "copy_snapshot", fail)
    with pytest.raises(RuntimeError, match="copy failed"):
        client.post(PATH)
    with engine.connect() as conn:
        assert conn.execute(select(runs.c.run_id)).scalars().all() == ["one"]
        assert set(conn.execute(select(artifacts.c.run_id)).scalars()) == {"one"}


def test_decided_case_is_rejected_and_other_cases_remain_actionable(service, monkeypatch):
    client, engine, _ = service
    parent = spec()
    option = ActionOption(
        id="decided",
        **common(parent),
        case_id="case-1",
        kind="hold",
        legs=(),
        checks=(),
        assumptions=(),
        valid_until=parent.as_of + timedelta(days=1),
        recommended=False,
        rationale="Hold",
        input_version_hash="hash",
    )
    with repo_session(engine, parent) as repo:
        repo.put(case(parent), case(parent, "case-2"), option)
        repo.publish()
    approval.decide(
        engine,
        approval.DecisionRequest(
            run_id="one",
            scenario_id="historical",
            option_id=option.id,
            input_version_hash="hash",
            decision="rejected",
            by="reviewer",
            idempotency_key="decision",
        ),
        now=parent.as_of,
    )
    monkeypatch.setattr(api, "execute", lambda *_: None)
    assert client.post(PATH).status_code == 409
    assert client.post(PATH.replace("case-1", "case-2")).status_code == 202


def test_ledger_snapshot_changes_job_identity_and_freezes_reservations(service, monkeypatch):
    client, engine, _ = service
    parent = seed(engine)
    queued = []
    monkeypatch.setattr(api, "execute", lambda *args: queued.append(args))
    first = client.post(PATH).json()["spec"]["run_id"]
    reservation = Reservation(
        id="held",
        **common(parent),
        decision_id="decision",
        location="MIL01",
        sku="SKU-999",
        size="M",
        qty=1,
        status="pending",
        idempotency_key="held",
        created_at=parent.as_of,
    )
    with engine.begin() as conn:
        api.ledger.metadata.create_all(conn)
        conn.execute(
            insert(api.ledger.drafts).values(
                scenario_id="historical",
                idempotency_key="held",
                run_id="another-run",
                option_id="another-case",
                request={},
                payload={
                    "option": {"case_id": "other"},
                    "reservations": [reservation.model_dump(mode="json")],
                },
            )
        )
    second = client.post(PATH).json()["spec"]["run_id"]
    assert first != second
    assert queued[0][-1].reservations == ()
    assert queued[1][-1].reservations == (reservation,)
