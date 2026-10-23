"""ACT-03b: ledger reads share the pipeline repository's connection and transaction."""

import pytest
from sqlalchemy import insert

from tesseract.core.contracts import Reservation, RunSpec
from tesseract.core.db import connect
from tesseract.core.run_repo import repo_session
from tesseract.modules.actions import ledger

AT = "2026-10-22T20:00:00Z"


@pytest.fixture
def database(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'ledger.db'}")
    spec = RunSpec(
        run_id="run",
        scenario_id="scenario",
        as_of=AT,
        stores=("MIL01",),
        source_manifest_hash="test",
        config_hash="test",
        code_version="test",
        mode="recorded",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    yield engine, spec
    engine.dispose()


def reservation(scenario_id):
    return Reservation(
        id=f"reservation-{scenario_id}",
        version="1",
        available_at=AT,
        availability_basis="decision time",
        source_refs=(),
        run_id="run",
        scenario_id=scenario_id,
        computed_at=AT,
        input_refs=(),
        producer="act.approval",
        producer_version="1",
        decision_id=f"decision-{scenario_id}",
        location="MIL01",
        sku="STYLE-999",
        size="1",
        qty=2,
        status="pending",
        idempotency_key=f"key-{scenario_id}",
        created_at=AT,
    )


def put_reservation(connection, record):
    connection.execute(
        insert(ledger.drafts).values(
            scenario_id=record.scenario_id,
            idempotency_key=record.idempotency_key,
            run_id=record.run_id,
            option_id=f"option-{record.scenario_id}",
            request={},
            payload={"reservations": [record.model_dump(mode="json")]},
        )
    )


def test_bound_repository_without_ledger_returns_empty_and_keeps_connection_open(database):
    engine, spec = database
    with repo_session(engine, spec) as current:
        assert ledger.reservations(current.engine, spec.scenario_id) == ()
        assert not current.session.closed
        assert current.session.in_transaction()
        current.publish()
    # The helper must leave the caller free to finish its transaction.
    with repo_session(engine, spec.run_id) as current:
        assert current.run_state()["published"]


def test_bound_repository_reads_current_transaction_and_only_requested_scenario(database):
    engine, spec = database
    own = reservation(spec.scenario_id)
    other = reservation("other-scenario")
    with repo_session(engine, spec, write=True) as current:
        # Schema and reservations are deliberately uncommitted, just like a worker job.
        ledger.metadata.create_all(current.session)
        put_reservation(current.session, own)
        put_reservation(current.session, other)
        assert ledger.reservations(current.engine, spec.scenario_id) == (own,)
        assert ledger.reservations(current.engine, "other-scenario") == (other,)
        assert ledger.reservations(current.engine, "missing-scenario") == ()
        assert not current.session.closed
        current.publish()
    assert ledger.reservations(engine, spec.scenario_id) == (own,)
    with repo_session(engine, spec.run_id) as current:
        assert ledger.reservations(current.engine, spec.scenario_id) == (own,)


def test_bound_read_never_commits_or_closes_the_worker_transaction(database):
    engine, spec = database
    ledger.metadata.create_all(engine)
    held = reservation(spec.scenario_id)
    with pytest.raises(RuntimeError, match="abort worker"):
        with repo_session(engine, spec, write=True) as current:
            put_reservation(current.session, held)
            assert ledger.reservations(current.engine, spec.scenario_id) == (held,)
            # Another connection cannot see the worker's uncommitted reservation.
            assert ledger.reservations(engine, spec.scenario_id) == ()
            current.publish()
            raise RuntimeError("abort worker")
    assert ledger.reservations(engine, spec.scenario_id) == ()
