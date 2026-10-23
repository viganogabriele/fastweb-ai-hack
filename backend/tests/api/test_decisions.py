"""PLT-14: saved local drafts are read back exactly, per run and namespace."""

from tesseract.core.config import Settings
from tests.api import test_options as decided
from tests.modules.actions.test_options import AS_OF

service = decided.service
prepare, body, endpoint = decided.prepare, decided.body, decided.endpoint


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
    rejected = client.post(
        f"/api/runs/run/options/{options['hold'].id}/decision",
        json=body(options["hold"], decision="rejected", key="other-key"),
    ).json()
    assert listed(client) == sorted([draft, rejected], key=lambda d: d["decision"]["id"])
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
