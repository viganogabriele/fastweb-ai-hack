"""PLT-10: real HTTP decisions use the transactional ACT-03 ledger."""

from dataclasses import replace
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert
from sqlalchemy.exc import OperationalError

from tessera.api.main import create_app
from tessera.api.routers.options import decision_clock, option_input_loader
from tessera.core.config import Settings
from tessera.core.contracts import RunSpec
from tessera.core.db import artifacts, connect
from tessera.core.run_repo import repo_session
from tessera.modules.actions import approval, ledger
from tessera.modules.actions.options import evaluate_case
from tests.modules.actions.test_options import AS_OF, inputs


def seed(engine, run_id="run", *, mode="recorded", published=True, blocked=False, case_id=None):
    value = inputs()
    value = replace(
        value,
        run_id=run_id,
        case=value.case.model_copy(
            update={
                "run_id": run_id,
                "input_refs": (),
                "id": case_id or value.case.id,
            }
        ),
    )
    if blocked:
        value = replace(value, policy=replace(value.policy, max_transfer_cost_eur=0))
    value = replace(
        value,
        dest=replace(
            value.dest,
            forecast=value.dest.forecast.model_copy(
                update={
                    "run_id": run_id,
                }
            ),
        ),
        routes=tuple(
            replace(
                route,
                donor=replace(
                    route.donor, forecast=route.donor.forecast.model_copy(update={"run_id": run_id})
                ),
            )
            for route in value.routes
        ),
    )
    spec = RunSpec(
        run_id=run_id,
        scenario_id=value.scenario_id,
        as_of=AS_OF,
        stores=("MIL01", "MIL02"),
        source_manifest_hash="test",
        config_hash="test",
        code_version="test",
        mode=mode,
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    options = evaluate_case([value])
    with repo_session(engine, spec, fixture_mode=mode == "fixture") as current:
        current.put(value.case)
        for position in (value.dest, *(route.donor for route in value.routes)):
            current.put(position.forecast, *position.stock.values())
        current.put(*options)
        if published:
            current.publish()
    return value, {option.kind: option for option in options}


@pytest.fixture
def service(tmp_path):
    engines = {
        name: connect(f"sqlite:///{tmp_path / (name + '.db')}") for name in ("product", "fixture")
    }
    app = create_app(
        engine=engines["product"],
        fixture_engine=engines["fixture"],
        settings=Settings(_env_file=None, fixture_mode=True),
    )
    values = {}

    def load(current, case):
        return [values[(current.run_id, case.id)]]

    app.dependency_overrides[option_input_loader] = lambda: load
    app.dependency_overrides[decision_clock] = lambda: AS_OF
    with TestClient(app) as client:
        yield client, engines, app, values
    for engine in engines.values():
        engine.dispose()


def prepare(service, **kwargs):
    client, engines, _, values = service
    value, options = seed(
        engines["fixture" if kwargs.get("mode") == "fixture" else "product"], **kwargs
    )
    values[(value.run_id, value.case.id)] = value
    return client, value, options


def body(option, *, decision="approved", key="test-key"):
    return dict(
        option_id=option.id,
        input_version_hash=option.input_version_hash,
        decision=decision,
        by="test human",
        idempotency_key=key,
    )


def endpoint(value):
    return f"/api/runs/{value.run_id}/cases/{value.case.id}/decisions"


def test_read_returns_stored_options_and_does_not_reserve(service):
    client, value, options = prepare(service)
    response = client.get(f"/api/runs/run/cases/{value.case.id}/options")
    assert response.status_code == 200
    assert response.json() == [option.model_dump(mode="json") for option in options.values()]
    assert ledger.reservations(service[1]["product"], value.scenario_id) == ()
    assert client.get("/api/runs/run/cases/missing/options").status_code == 404


def test_approval_and_retry_use_real_ledger_and_return_exact_local_draft(service):
    client, value, options = prepare(service)
    response = client.post(endpoint(value), json=body(options["transfer"]))
    assert response.status_code == 200, response.text
    draft = response.json()
    assert draft["decision"]["dispatch_status"] == "draft"
    assert draft["decision"]["by"] == "test human"
    assert draft["simulated"] is True
    assert draft["reservations"]
    retry = client.post(endpoint(value), json=body(options["transfer"]))
    assert retry.status_code == 200
    assert retry.json() == draft
    held = ledger.reservations(service[1]["product"], value.scenario_id)
    assert [r.model_dump(mode="json") for r in held] == draft["reservations"]


def test_rejection_via_rfc_route_creates_no_reservation(service):
    client, value, options = prepare(service)
    option = options["transfer"]
    response = client.post(
        f"/api/runs/run/options/{option.id}/decision", json=body(option, decision="rejected")
    )
    assert response.status_code == 200, response.text
    assert response.json()["decision"]["decision"] == "rejected"
    assert response.json()["reservations"] == []
    assert ledger.reservations(service[1]["product"], value.scenario_id) == ()


def test_stale_hash_and_reused_key_return_conflict(service):
    client, value, options = prepare(service)
    option = options["transfer"]
    stale = {**body(option), "input_version_hash": "stale"}
    assert client.post(endpoint(value), json=stale).status_code == 409
    assert client.post(endpoint(value), json=body(option)).status_code == 200
    different = body(option, decision="rejected")
    assert client.post(endpoint(value), json=different).status_code == 409
    assert client.post(endpoint(value), json=body(option, key="new-key")).status_code == 409


@pytest.mark.parametrize("change", ["expired", "stock", "blocked", "new-run"])
def test_current_validation_cannot_be_bypassed_by_http(service, change):
    client, value, options = prepare(service, blocked=change == "blocked")
    if change == "expired":
        service[2].dependency_overrides[decision_clock] = lambda: AS_OF + timedelta(days=30)
    elif change == "stock":
        route = value.routes[0]
        donor = replace(
            route.donor,
            stock={
                size: fact.model_copy(update={"qty": 0}) for size, fact in route.donor.stock.items()
            },
        )
        service[3][(value.run_id, value.case.id)] = replace(
            value, routes=(replace(route, donor=donor),)
        )
    elif change == "new-run":
        prepare(service, run_id="new-run")
    response = client.post(endpoint(value), json=body(options["transfer"]))
    assert response.status_code == 409, response.text
    assert ledger.reservations(service[1]["product"], value.scenario_id) == ()


def test_publication_namespace_and_case_guards(service):
    client, value, options = prepare(service)
    prepare(service, run_id="pending", published=False)
    fixture_value, fixture_options = seed(service[1]["fixture"], mode="fixture")
    # Same IDs and scenario in two physical namespaces must not share decisions or stock.
    service[3][(fixture_value.run_id, fixture_value.case.id)] = fixture_value
    assert client.get(f"/api/runs/pending/cases/{value.case.id}/options").status_code == 409
    assert (
        client.post(
            endpoint(value).replace("/run/", "/pending/"), json=body(options["transfer"])
        ).status_code
        == 409
    )
    assert (
        client.post(
            endpoint(value).replace("/run/", "/missing/"), json=body(options["transfer"])
        ).status_code
        == 404
    )
    assert (
        client.post(
            endpoint(value).replace(value.case.id, "wrong-case"), json=body(options["transfer"])
        ).status_code
        == 404
    )
    fixture = client.post(
        endpoint(fixture_value) + "?fixture=true", json=body(fixture_options["transfer"])
    )
    assert fixture.status_code == 200, fixture.text
    assert ledger.reservations(service[1]["product"], value.scenario_id) == ()
    assert client.post(endpoint(value), json=body(options["transfer"])).status_code == 200
    service[2].state.settings = Settings(_env_file=None, fixture_mode=False)
    assert (
        client.post(endpoint(value) + "?fixture=true", json=body(options["transfer"])).status_code
        == 403
    )


def test_option_id_cannot_point_outside_url_case_or_override_snapshot(service):
    client, value, options = prepare(service)
    url = f"/api/runs/run/options/{options['hold'].id}/decision"
    assert client.post(url, json=body(options["transfer"])).status_code == 422
    assert (
        client.post(endpoint(value), json={**body(options["hold"]), "run_id": "other"}).status_code
        == 422
    )
    assert (
        client.post(
            endpoint(value), json={**body(options["hold"]), "scenario_id": "other"}
        ).status_code
        == 422
    )
    assert (
        client.post(
            endpoint(value), json={**body(options["hold"]), "decision": "dispatch"}
        ).status_code
        == 422
    )


def test_hidden_foreign_case_and_future_options_are_not_exposed(service):
    client, value, options = prepare(service)
    foreign = value.case.model_copy(update={"id": "foreign", "store_id": "NYC01"})
    future = options["hold"].model_copy(
        update={"id": "future", "available_at": AS_OF + timedelta(days=1)}
    )
    hidden_option = options["hold"].model_copy(update={"id": "hidden-option", "case_id": "foreign"})
    with service[1]["product"].begin() as conn:
        for artifact in (foreign, future, hidden_option):
            conn.execute(
                insert(artifacts).values(
                    run_id=value.run_id,
                    kind=type(artifact).__name__,
                    id=artifact.id,
                    version=artifact.version,
                    store_id=getattr(artifact, "store_id", None),
                    case_id=getattr(artifact, "case_id", artifact.id),
                    available_at=artifact.available_at,
                    payload=artifact.model_dump(mode="json"),
                    input_refs=[],
                )
            )
    response = client.get(f"/api/runs/run/cases/{value.case.id}/options")
    assert "future" not in {option["id"] for option in response.json()}
    assert client.get("/api/runs/run/cases/foreign/options").status_code == 404
    assert (
        client.post(
            "/api/runs/run/options/hidden-option/decision", json=body(hidden_option)
        ).status_code
        == 404
    )
    assert client.post(endpoint(value), json=body(future)).status_code == 404


def test_busy_ledger_is_retryable_without_silent_resubmission(service, monkeypatch):
    client, value, options = prepare(service)

    def busy(*args, **kwargs):
        raise OperationalError("BEGIN IMMEDIATE", {}, Exception("database is locked"))

    monkeypatch.setattr(approval, "decide", busy)
    response = client.post(endpoint(value), json=body(options["hold"]))
    assert response.status_code == 503
    assert response.headers["retry-after"] == "5"
    assert ledger.reservations(service[1]["product"], value.scenario_id) == ()


def test_approval_input_gathering_excludes_historical_derived_support(service):
    from tessera.core.contracts import ForecastAdjustment

    client, value, options = prepare(service)
    old = value.dest.forecast.model_copy(update={"version": "parent:answer:1"})
    # Insert support after the fresh version to exercise unversioned fallback.
    with service[1]["product"].begin() as conn:
        conn.execute(
            insert(artifacts).values(
                run_id=value.run_id,
                kind="ForecastAdjustment",
                id=old.id,
                version=old.version,
                store_id=old.store_id,
                sku=old.sku,
                available_at=old.available_at,
                payload=old.model_dump(mode="json"),
                input_refs=[],
            )
        )
    gathered = []

    def load(current, case):
        forecasts = current.list(ForecastAdjustment, store_id=old.store_id, sku=old.sku)
        assert forecasts and all(not f.version.startswith("parent:") for f in forecasts)
        assert current.get(ForecastAdjustment, old.id).version == value.dest.forecast.version
        assert current.get(ForecastAdjustment, old.id, old.version) == old
        gathered.append(case.id)
        return [value]

    service[2].dependency_overrides[option_input_loader] = lambda: load
    response = client.post(endpoint(value), json=body(options["hold"]))
    assert response.status_code == 200
    assert gathered == [value.case.id]
