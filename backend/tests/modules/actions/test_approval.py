"""ACT-03: real SQLite transactions, durable drafts and shared stock under contention."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta

import pytest
from sqlalchemy import event, func, select

from tesseract.core import repo
from tesseract.core.contracts import RunSpec
from tesseract.core.db import connect
from tesseract.modules.actions import ledger
from tesseract.modules.actions.approval import Conflict, DecisionRequest, decide
from tesseract.modules.actions.options import evaluate_case
from tests.modules.actions.test_options import AS_OF, inputs


def publish(engine, values):
    first = values[0]
    spec = RunSpec(
        run_id=first.run_id,
        scenario_id=first.scenario_id,
        as_of=first.as_of,
        stores=("MIL01", "MIL02"),
        source_manifest_hash="test",
        config_hash="test",
        code_version="test",
        mode="fixture",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    repo.create_run(engine, spec)
    current = repo.Repo(engine, spec)
    for value in values:
        current.put(value.case, *evaluate_case([value]))
    repo.set_run_status(engine, spec.run_id, "published")
    return current


def proposal(value, kind="transfer", key="request-1", decision="approved"):
    option = next(o for o in evaluate_case([value]) if o.kind == kind)
    return DecisionRequest(
        run_id=value.run_id,
        scenario_id=value.scenario_id,
        option_id=option.id,
        input_version_hash=option.input_version_hash,
        decision=decision,
        by="test user",
        idempotency_key=key,
    )


@pytest.fixture
def setup(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'approval.db'}")
    value = inputs()
    value = replace(value, case=value.case.model_copy(update={"run_id": value.run_id}))
    publish(engine, [value])
    return engine, value


def approve(engine, value, **kwargs):
    return decide(engine, proposal(value), loader=lambda *_: [value], now=AS_OF, **kwargs)


def test_approval_saves_exact_checks_and_holds_units_without_external_dispatch(setup):
    engine, value = setup
    draft = approve(engine, value)
    assert draft.decision.dispatch_status == "draft"
    assert draft.simulated
    assert (
        draft.option.checks
        == next(o for o in evaluate_case([value]) if o.kind == "transfer").checks
    )
    assert sum(r.qty for r in draft.reservations) == sum(leg.qty for leg in draft.option.legs)
    assert all(r.status == "pending" for r in draft.reservations)
    assert ledger.reservations(engine, value.scenario_id) == draft.reservations
    assert ledger.reservations(engine, "independent-what-if") == ()


def test_retry_is_exact_and_survives_run_reset(setup):
    engine, value = setup
    draft = approve(engine, value)
    repo.reset_run(engine, value.run_id)
    assert decide(engine, proposal(value), now=AS_OF + timedelta(days=30)) == draft
    assert ledger.reservations(engine, value.scenario_id) == draft.reservations


@pytest.mark.parametrize("update", [{"by": "another actor"}, {"decision": "rejected"}])
def test_same_key_different_request_is_conflict(setup, update):
    engine, value = setup
    approve(engine, value)
    with pytest.raises(Conflict, match="idempotency"):
        decide(engine, proposal(value).model_copy(update=update), now=AS_OF)


def test_different_key_cannot_decide_same_option_twice(setup):
    engine, value = setup
    approve(engine, value)
    with pytest.raises(Conflict, match="already decided"):
        decide(engine, proposal(value, key="retry-with-wrong-key"), now=AS_OF)


def test_rejection_and_information_do_not_hold_stock(setup):
    engine, value = setup
    for kind, decision in (("transfer", "rejected"), ("hold", "approved")):
        draft = decide(
            engine,
            proposal(value, kind, key=kind, decision=decision),
            loader=lambda *_: [value],
            now=AS_OF,
        )
        assert draft.reservations == ()
    assert ledger.reservations(engine, value.scenario_id) == ()


@pytest.mark.parametrize("change", ["hash", "expired", "stock", "eta", "closed"])
def test_changed_or_expired_inputs_are_conflict_without_write(setup, change):
    engine, value = setup
    request = proposal(value)
    at = AS_OF
    if change == "hash":
        request = request.model_copy(update={"input_version_hash": "stale"})
    elif change == "expired":
        at += timedelta(days=30)
    elif change == "stock":
        donor = value.routes[0].donor
        stock = {s: f.model_copy(update={"qty": 0}) for s, f in donor.stock.items()}
        value = replace(
            value, routes=(replace(value.routes[0], donor=replace(donor, stock=stock)),)
        )
    elif change == "eta":
        lane = value.routes[0].lane
        later = replace(
            lane, eta=replace(lane.eta, pickup_at=lane.eta.pickup_at + timedelta(days=1))
        )
        value = replace(value, routes=(replace(value.routes[0], lane=later),))
    else:
        # Current inputs represent the now closed case, so reevaluation must fail.
        value = replace(
            value, case=value.case.model_copy(update={"status": "closed", "version": "2"})
        )
    with pytest.raises(Conflict):
        decide(engine, request, loader=lambda *_: [value], now=at)
    assert ledger.reservations(engine, value.scenario_id) == ()


def test_old_published_run_is_readable_but_not_approvable(setup):
    engine, value = setup
    newer = replace(
        value, run_id="new-run", case=value.case.model_copy(update={"run_id": "new-run"})
    )
    publish(engine, [newer])
    assert repo.Repo.open(engine, value.run_id).get(type(value.case), value.case.id)
    with pytest.raises(Conflict, match="current published"):
        approve(engine, value)


def test_concurrent_cases_compete_for_stock_and_only_one_commits(setup):
    engine, first = setup
    second = replace(first, case=first.case.model_copy(update={"id": "another-case"}))
    # Publish both cases together in the new current snapshot.
    values = [
        replace(v, run_id="both", case=v.case.model_copy(update={"run_id": "both"}))
        for v in (first, second)
    ]
    publish(engine, values)

    def attempt(value):
        try:
            return approve(engine, value)
        except Conflict:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, values))
    assert sum(result is not None for result in results) == 1
    with engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(ledger.drafts)).scalar_one() == 1


def test_write_failure_rolls_back_decision_and_reservation(setup):
    engine, value = setup

    def fail_write(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO action_drafts"):
            raise RuntimeError("disk failure")

    event.listen(engine, "before_cursor_execute", fail_write)
    try:
        with pytest.raises(RuntimeError, match="disk failure"):
            approve(engine, value)
    finally:
        event.remove(engine, "before_cursor_execute", fail_write)
    assert ledger.reservations(engine, value.scenario_id) == ()
    assert approve(engine, value).decision.decision == "approved"


def test_concurrent_identical_retries_return_one_persisted_decision(setup):
    engine, value = setup
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: approve(engine, value), range(2)))
    assert results[0] == results[1]
    assert ledger.reservations(engine, value.scenario_id) == results[0].reservations


def test_current_but_blocked_movement_cannot_be_approved(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'blocked.db'}")
    value = inputs()
    value = replace(
        value,
        case=value.case.model_copy(update={"run_id": value.run_id}),
        policy=replace(value.policy, max_transfer_cost_eur=0),
    )
    publish(engine, [value])
    with pytest.raises(Conflict, match="mandatory movement"):
        approve(engine, value)
    assert ledger.reservations(engine, value.scenario_id) == ()


def test_durable_ledger_survives_engine_reconnect(setup):
    engine, value = setup
    draft = approve(engine, value)
    url = engine.url
    engine.dispose()
    reopened = connect(url)
    try:
        assert ledger.reservations(reopened, value.scenario_id) == draft.reservations
        assert decide(reopened, proposal(value), now=AS_OF) == draft
    finally:
        reopened.dispose()
