"""TST-07 / RFC §7.3.7: independent processes contend for one donor unit.

Workers share only the SQLite file, not an Engine, connection, or Python lock. A
barrier releases them together, including the first creation of the durable ledger.
Dispatch remains draft-only; optional REST/outbox timeout reconciliation is not enabled.
"""

import multiprocessing
import os
from dataclasses import replace

import httpx
import pytest
from sqlalchemy import event, func, select

from tessera.core.contracts import ActionOption
from tessera.core.db import connect
from tessera.core.repo import Repo
from tessera.modules.actions import ledger
from tessera.modules.actions.approval import Conflict, LocalDraft, decide
from tests.modules.actions.test_approval import proposal, publish
from tests.modules.actions.test_options import AS_OF, POLICY, SIZES, forecast, inputs, position


def one_unit(case_id, *, run_id="race", scenario_id="historical"):
    donor = position("MIL02", {size: int(size == "1") for size in SIZES}, forecast("MIL02", 0))
    value = inputs(
        donor=donor,
        size="1",
        policy=replace(
            POLICY,
            donor_min_stock=0,
            max_units_per_transfer=1,
        ),
    )
    value = replace(
        value,
        run_id=run_id,
        scenario_id=scenario_id,
        case=value.case.model_copy(
            update={"id": case_id, "run_id": run_id, "scenario_id": scenario_id}
        ),
    )

    def scoped(where):
        return replace(
            where,
            forecast=where.forecast.model_copy(
                update={
                    "run_id": run_id,
                    "scenario_id": scenario_id,
                }
            ),
        )

    return replace(
        value,
        dest=scoped(value.dest),
        routes=tuple(replace(route, donor=scoped(route.donor)) for route in value.routes),
    )


def _worker(url, value, request, barrier, result):
    engine = connect(url)

    def meet_at_write_lock(_conn, _cursor, statement, _parameters, _context, _many):
        if statement.strip().upper() == "BEGIN IMMEDIATE":
            # Keep both independent processes poised at the lock acquisition. A
            # barrier only before decide() can release one process late enough
            # for the other to finish before it reaches SQLite.
            barrier.wait(timeout=15)

    event.listen(engine, "before_cursor_execute", meet_at_write_lock)
    try:
        try:
            draft = decide(engine, request, loader=lambda *_: [value], now=AS_OF)
        except Conflict as error:
            result.send({"pid": os.getpid(), "status": error.status_code, "detail": str(error)})
        else:
            result.send({"pid": os.getpid(), "status": 200, "draft": draft.model_dump(mode="json")})
    finally:
        result.close()
        engine.dispose()


def race(url, commands):
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(len(commands))
    processes = []
    readers = []
    try:
        for value, request in commands:
            reader, writer = context.Pipe(duplex=False)
            readers.append(reader)
            process = context.Process(target=_worker, args=(url, value, request, barrier, writer))
            process.start()
            writer.close()
            processes.append(process)
        results = []
        for reader in readers:
            assert reader.poll(15), "approval process did not return within the deadline"
            results.append(reader.recv())
        for process in processes:
            process.join(timeout=15)
            assert process.exitcode == 0, f"approval process failed: {process.exitcode}"
        assert len({result["pid"] for result in results}) == len(commands)
        return results
    finally:
        for reader in readers:
            reader.close()
        for process in processes:
            if process.is_alive():
                process.terminate()
            process.join(timeout=5)


@pytest.fixture
def database(tmp_path):
    url = f"sqlite:///{tmp_path / 'gate.db'}"
    engine = connect(url)
    yield engine, url
    engine.dispose()


def assert_single_unit(engine, scenario_id, draft):
    held = ledger.reservations(engine, scenario_id)
    assert len(held) == 1 and held[0].qty == 1
    assert (held[0].location, held[0].sku, held[0].size) == (
        draft.option.legs[0].origin,
        draft.option.legs[0].sku,
        "1",
    )
    assert held[0].decision_id == draft.decision.id
    assert held[0].status == "pending"
    assert draft.decision.dispatch_status == "draft"
    with engine.connect() as connection:
        assert (
            connection.execute(
                select(func.count())
                .select_from(ledger.drafts)
                .where(
                    ledger.drafts.c.scenario_id == scenario_id,
                )
            ).scalar_one()
            == 1
        )


def test_independent_approvers_cannot_reserve_the_same_last_unit(database):
    engine, url = database
    values = [one_unit("case-a"), one_unit("case-b")]
    publish(engine, values)
    commands = [(value, proposal(value, key=value.case.id)) for value in values]
    options_before = [
        Repo.open(engine, value.run_id).get(ActionOption, request.option_id)
        for value, request in commands
    ]
    # Both proposals must be individually feasible, for exactly the same single unit.
    for value, request in commands:
        option = Repo.open(engine, value.run_id).get(ActionOption, request.option_id)
        assert option.legs[0].qty == 1
        assert all(c.status in ("pass", "not_applicable") for c in option.checks if c.mandatory)
    results = race(url, commands)
    assert sorted(result["status"] for result in results) == [200, 409]
    winner = LocalDraft.model_validate(
        next(result["draft"] for result in results if result["status"] == 200)
    )
    assert_single_unit(engine, values[0].scenario_id, winner)

    loser_index = next(index for index, result in enumerate(results) if result["status"] == 409)
    value, stale = commands[loser_index]
    # The immutable proposal remains readable; its hash no longer authorizes a move.
    current = Repo.open(engine, value.run_id).get(ActionOption, stale.option_id)
    assert current is not None
    assert current == options_before[loser_index]
    with pytest.raises(Conflict, match="recompute"):
        decide(engine, stale, loader=lambda *_: [value], now=AS_OF)
    assert Repo.open(engine, value.run_id).get(ActionOption, stale.option_id) == current
    assert_single_unit(engine, value.scenario_id, winner)


def test_same_idempotency_key_from_independent_processes_returns_one_draft(database):
    engine, url = database
    value = one_unit("case-a")
    publish(engine, [value])
    command = (value, proposal(value))
    results = race(url, [command, command])
    assert [result["status"] for result in results] == [200, 200]
    assert results[0]["draft"] == results[1]["draft"]
    draft = LocalDraft.model_validate(results[0]["draft"])
    assert_single_unit(engine, value.scenario_id, draft)


def test_key_collision_between_different_commands_never_overwrites_a_decision(database):
    engine, url = database
    values = [one_unit("case-a"), one_unit("case-b")]
    publish(engine, values)
    results = race(url, [(value, proposal(value, key="same-key")) for value in values])
    assert sorted(result["status"] for result in results) == [200, 409]
    conflict = next(result for result in results if result["status"] == 409)
    assert "idempotency key" in conflict["detail"]
    draft = LocalDraft.model_validate(
        next(result["draft"] for result in results if result["status"] == 200)
    )
    assert_single_unit(engine, values[0].scenario_id, draft)


def test_independent_scenarios_do_not_share_the_single_unit_ledger(database):
    engine, url = database
    values = [
        one_unit("case-a", run_id="a", scenario_id="scenario-a"),
        one_unit("case-b", run_id="b", scenario_id="scenario-b"),
    ]
    for value in values:
        publish(engine, [value])
    # Even the same idempotency key belongs to separate decision namespaces.
    results = race(url, [(value, proposal(value, key="same-key")) for value in values])
    assert [result["status"] for result in results] == [200, 200]
    for value, result in zip(values, results, strict=True):
        draft = LocalDraft.model_validate(result["draft"])
        assert draft.decision.scenario_id == value.scenario_id
        assert_single_unit(engine, value.scenario_id, draft)
    assert results[0]["draft"]["decision"]["id"] != results[1]["draft"]["decision"]["id"]


def test_local_draft_and_retries_never_attempt_optional_network_dispatch(database, monkeypatch):
    engine, _ = database
    value = one_unit("case-a")
    publish(engine, [value])
    attempts = []

    def transport_timeout(*args, **kwargs):
        attempts.append("dispatch")
        raise httpx.ReadTimeout("ambiguous external result")

    monkeypatch.setattr(httpx.Client, "send", transport_timeout)
    command = proposal(value)
    first = decide(engine, command, loader=lambda *_: [value], now=AS_OF)
    retry = decide(engine, command, loader=lambda *_: [value], now=AS_OF)
    assert first == retry
    assert first.decision.dispatch_status == "draft"
    assert attempts == []
    assert_single_unit(engine, value.scenario_id, first)
