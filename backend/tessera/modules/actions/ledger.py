"""Durable, scenario-scoped local drafts, separate from resettable run projections.

These additive tables use their own metadata and deliberately have no run foreign key:
``reset_run`` must preserve decisions and held units. No external booking is performed.
"""

from sqlalchemy import (
    JSON,
    Column,
    Engine,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    inspect,
    select,
)

from tessera.core.contracts import Reservation

metadata = MetaData()
drafts = Table(
    "action_drafts",
    metadata,
    Column("scenario_id", String, primary_key=True),
    Column("idempotency_key", String, primary_key=True),
    Column("run_id", String, nullable=False),
    Column("option_id", String, nullable=False),
    Column("request", JSON, nullable=False),
    Column("payload", JSON, nullable=False),
    UniqueConstraint("scenario_id", "run_id", "option_id"),
)


def reservations(engine: Engine, scenario_id: str) -> tuple[Reservation, ...]:
    """Read the session ledger, including decisions made after the snapshot's as_of."""
    if not inspect(engine).has_table(drafts.name):
        return ()
    with engine.connect() as conn:
        payloads = conn.execute(
            select(drafts.c.payload).where(drafts.c.scenario_id == scenario_id)
        ).scalars()
        return tuple(
            Reservation.model_validate(r) for payload in payloads for r in payload["reservations"]
        )
