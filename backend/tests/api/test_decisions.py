"""PLT-14: saved local drafts are read back exactly, per run and namespace."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

import pytest
from sqlalchemy import func, select

from tesseract.api.routers.options import decision_clock
from tesseract.core.config import Settings
from tesseract.core.repo import reset_run
from tesseract.core.run_repo import RunRepo, repo_session
from tesseract.modules.actions import ledger
from tests.api import test_options as decided
from tests.modules.actions.test_options import AS_OF

service = decided.service
prepare, body, endpoint = decided.prepare, decided.body, decided.endpoint
JOB = "investigate-job"


def listed(client, run_id="run", **params):
    response = client.get(f"/api/runs/{run_id}/decisions", params=params)
    assert response.status_code == 200, response.text
    return response.json()


def test_no_saved_decision_reads_as_empty_not_synthesized(service):
    client, value, _ = prepare(service)
    assert listed(client) == []
    assert listed(client, case_id=value.case.id) == []
    assert client.get("/api/runs/run/decisions/decision-missing").status_code == 404
    assert client.get("/api/runs/run/decisions", params={"case_id": "missing"}).status_code == 404


def test_saved_draft_and_idempotent_retry_read_back_once_and_exactly(service):
    client, value, options = prepare(service)
    option = options["transfer"]
    draft = client.post(endpoint(value), json=body(option)).json()
    assert client.post(endpoint(value), json=body(option)).json() == draft
    service[2].dependency_overrides[decision_clock] = lambda: AS_OF + timedelta(minutes=1)
    rejected = client.post(
        f"/api/runs/run/options/{options['hold'].id}/decision",
        json=body(options["hold"], decision="rejected", key="other-key"),
    ).json()
    assert listed(client) == [draft, rejected]
    assert listed(client, case_id=value.case.id) == listed(client)
    item = client.get(f"/api/runs/run/decisions/{draft['decision']['id']}")
    assert item.status_code == 200 and item.json() == draft
    saved = item.json()
    assert saved["simulated"] is True
    assert saved["decision"]["dispatch_status"] == "draft"
    assert saved["decision"]["version"] == "1"
    assert saved["decision"]["by"] == "test human"
    assert saved["decision"]["at"] == AS_OF.isoformat().replace("+00:00", "Z")
    assert saved["decision"]["input_refs"] == [
        {"kind": "ActionOption", "id": option.id, "version": option.version}
    ]
    assert saved["option"] == option.model_dump(mode="json")
    assert saved["reservations"] and not rejected["reservations"]


def test_conflicting_attempts_persist_nothing(service):
    client, value, options = prepare(service)
    option = options["transfer"]
    stale = {**body(option), "input_version_hash": "stale"}
    assert client.post(endpoint(value), json=stale).status_code == 409
    assert listed(client) == []
    draft = client.post(endpoint(value), json=body(option)).json()
    assert client.post(endpoint(value), json=body(option, decision="rejected")).status_code == 409
    assert client.post(endpoint(value), json=body(option, key="new-key")).status_code == 409
    assert listed(client) == [draft]


def test_runs_and_namespaces_do_not_share_decisions(service):
    client, value, options = prepare(service)
    fixture_value, fixture_options = decided.seed(service[1]["fixture"], mode="fixture")
    service[3][(fixture_value.run_id, fixture_value.case.id)] = fixture_value
    draft = client.post(endpoint(value), json=body(options["transfer"])).json()
    # Same run, case and option IDs in the fixture namespace: nothing is visible there.
    assert listed(client, fixture=True) == []
    assert client.get(f"/api/runs/run/decisions/{draft['decision']['id']}?fixture=true").json() == {
        "detail": "Decision not found"
    }
    fixture = client.post(
        endpoint(fixture_value) + "?fixture=true", json=body(fixture_options["transfer"])
    ).json()
    assert listed(client, fixture=True) == [fixture]
    assert listed(client) == [draft]
    # A newer run of the scenario has no decisions; the older published run keeps its own.
    prepare(service, run_id="new-run")
    prepare(service, run_id="pending", published=False)
    assert listed(client, "new-run") == []
    assert listed(client) == [draft]
    assert client.get("/api/runs/pending/decisions").status_code == 409
    assert client.get("/api/runs/missing/decisions").status_code == 404
    service[2].state.settings = Settings(_env_file=None, fixture_mode=False)
    assert client.get("/api/runs/run/decisions?fixture=true").status_code == 403


def test_drafts_of_a_reset_run_do_not_attach_to_a_recreated_snapshot(service):
    client, value, options = prepare(service)
    draft = client.post(endpoint(value), json=body(options["transfer"])).json()
    # The scenario ledger deliberately survives the reset; the new snapshot never
    # published the decided option, so its draft must not be presented as this run's.
    reset_run(service[1]["product"], "run")
    prepare(service, case_id="recreated-case")
    assert listed(client) == []
    assert client.get(f"/api/runs/run/decisions/{draft['decision']['id']}").status_code == 404


def parent_with_two_cases(service):
    """Published parent with cases A and B, as an investigation would see it."""
    client, value, options = prepare(service, also=("case-b",))
    service[3][("run", "case-b")] = decided.scoped("run", case_id="case-b")
    return client, value, options


def publish_job(service, case_ids):
    """The investigation job for case B: a same-scenario copy of the parent, published."""
    with repo_session(service[1]["product"], "run", write=True) as parent:
        job = RunRepo(parent.session, parent.spec.model_copy(update={"run_id": JOB}))
        job.copy_snapshot(parent)
        job.publish()
    for case_id in case_ids:
        service[3][(JOB, case_id)] = decided.scoped(JOB, case_id=case_id)


def ledger_rows(service):
    with service[1]["product"].connect() as conn:
        return conn.execute(select(func.count()).select_from(ledger.drafts)).scalar_one()


@pytest.mark.parametrize(
    ("kind", "first", "again"),
    [
        ("hold", "approved", "approved"),  # legless approvals pass revalidation
        ("hold", "rejected", "approved"),
        ("transfer", "approved", "rejected"),  # rejections skip revalidation
        ("transfer", "rejected", "rejected"),
    ],
)
def test_option_decided_on_parent_cannot_be_decided_again_on_a_job_run(service, kind, first, again):
    client, value, options = parent_with_two_cases(service)
    option = options[kind]
    draft = client.post(endpoint(value), json=body(option, decision=first)).json()
    publish_job(service, (value.case.id, "case-b"))
    copied = client.get(f"/api/runs/{JOB}/cases/{value.case.id}/options").json()
    assert option.model_dump(mode="json") | {"run_id": JOB} in copied
    held = ledger.reservations(service[1]["product"], value.scenario_id)

    retry = body(option, decision=again, key="job-key")
    for url in (
        f"/api/runs/{JOB}/cases/{value.case.id}/decisions",
        f"/api/runs/{JOB}/options/{option.id}/decision",
    ):
        response = client.post(url, json=retry)
        assert response.status_code == 409, response.text
        assert response.json() == {
            "detail": "option already decided in an earlier run of this scenario"
        }
    assert listed(client, JOB) == [] and listed(client) == [draft]
    assert ledger_rows(service) == 1
    assert ledger.reservations(service[1]["product"], value.scenario_id) == held
    # The original command stays idempotent, though the parent is no longer current.
    assert client.post(endpoint(value), json=body(option, decision=first)).json() == draft
    # The job's own case is still decidable.
    other = next(
        o for o in client.get(f"/api/runs/{JOB}/cases/case-b/options").json() if o["kind"] == "hold"
    )
    saved = client.post(
        f"/api/runs/{JOB}/cases/case-b/decisions",
        json={**retry, "option_id": other["id"], "input_version_hash": other["input_version_hash"]},
    )
    assert saved.status_code == 200, saved.text
    assert listed(client, JOB) == [saved.json()] and ledger_rows(service) == 2


def test_racing_redecisions_on_a_job_run_leave_exactly_one_draft(service):
    client, value, options = parent_with_two_cases(service)
    option = options["hold"]
    draft = client.post(endpoint(value), json=body(option)).json()
    publish_job(service, (value.case.id,))
    barrier = Barrier(2)

    def attempt(decision):
        barrier.wait(timeout=10)
        return client.post(
            f"/api/runs/{JOB}/cases/{value.case.id}/decisions",
            json=body(option, decision=decision, key=f"race-{decision}"),
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(attempt, ("approved", "rejected"))) == [409, 409]
    assert listed(client) == [draft] and listed(client, JOB) == []
    assert ledger_rows(service) == 1
