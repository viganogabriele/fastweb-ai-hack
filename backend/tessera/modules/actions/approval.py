"""ACT-03 approval service, called by the thin API owned by platform.

``decide`` returns an immutable local draft or raises ``Conflict`` (HTTP 409).
The SQLite write lock covers current-run selection, input gathering, reevaluation and
the single durable write of decision, checked payload and reservations. Retries return
the exact saved draft, even after the run's projections have been reset.
"""

from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

import yaml
from sqlalchemy import Engine, insert, select

from tessera.core import repo
from tessera.core.config import get_settings
from tessera.core.contracts import ActionOption, ArtifactRef, Case, Decision, Reservation
from tessera.core.contracts.common import Contract, Text
from tessera.modules.actions import ledger
from tessera.modules.actions.options import (
    CLOSED_CASES,
    OptionInputs,
    case_products,
    evaluate_case,
    gather,
    load_policy,
)
from tessera.modules.sources.systems_client import SystemsReader, Unknown


class Conflict(ValueError):
    """A stale proposal, conflicting retry or unavailable resource; map to HTTP 409."""

    status_code = 409


class DecisionRequest(Contract):
    run_id: Text
    scenario_id: Text
    option_id: Text
    input_version_hash: Text
    decision: Literal["approved", "rejected"]
    by: Text
    idempotency_key: Text
    note: str | None = None


class LocalDraft(Contract):
    decision: Decision
    option: ActionOption
    reservations: tuple[Reservation, ...]
    simulated: Literal[True] = True


InputLoader = Callable[[repo.Repo, Case], Sequence[OptionInputs]]


def load_inputs(current: repo.Repo, case: Case) -> Sequence[OptionInputs]:
    """Production gathering with the same policy, source filters and evaluator as act.options."""
    settings = get_settings()
    reader = SystemsReader.open(current)
    if isinstance(reader, Unknown):
        raise Conflict(f"systems unavailable: {reader.reason}")
    try:
        domain = yaml.safe_load((settings.config_dir / "domain.yaml").read_text(encoding="utf-8"))
        horizon = int(domain["policy"]["horizon"]["days"]["value"])
        policy = load_policy(settings.config_dir)
        return [
            gather(current, reader, case, policy, horizon, product=product)
            for product in case_products(current, case)
        ]
    finally:
        reader.client.close()


def decide(
    engine: Engine,
    request: DecisionRequest,
    *,
    loader: InputLoader = load_inputs,
    now: datetime | None = None,
) -> LocalDraft:
    """Validate against the latest published state of the scenario; commit a local draft.

    ``loader`` is a trusted service dependency, never supplied by an HTTP caller. It must
    gather current facts, not cached options. ``now`` is the decision clock, independent
    of the historical run's as_of (tests/replay may supply an explicit clock).
    """
    at = now or datetime.now(UTC)
    if at.tzinfo is None:
        raise ValueError("decision clock must be timezone-aware")
    with engine.connect() as conn:
        # Acquire the write lock before any read: two approvers cannot validate the same units.
        conn.exec_driver_sql("BEGIN IMMEDIATE")
        # Serialize first-time table creation too; simultaneous first requests are safe.
        ledger.metadata.create_all(conn)
        saved = (
            conn.execute(
                select(ledger.drafts).where(
                    ledger.drafts.c.scenario_id == request.scenario_id,
                    ledger.drafts.c.idempotency_key == request.idempotency_key,
                )
            )
            .mappings()
            .first()
        )
        encoded = request.model_dump(mode="json")
        if saved is not None:
            if saved["request"] != encoded:
                raise Conflict("idempotency key already used for a different request")
            return LocalDraft.model_validate(saved["payload"])
        previous = conn.execute(
            select(ledger.drafts.c.option_id).where(
                ledger.drafts.c.scenario_id == request.scenario_id,
                ledger.drafts.c.run_id == request.run_id,
                ledger.drafts.c.option_id == request.option_id,
            )
        ).first()
        if previous:
            raise Conflict("option already decided")
        published = [
            spec
            for spec, _ in repo.list_runs(engine, status="published")
            if spec.scenario_id == request.scenario_id
        ]
        if not published or published[0].run_id != request.run_id:
            raise Conflict("option does not belong to the current published run of this scenario")
        current = repo.Repo(engine, published[0])
        option = current.get(ActionOption, request.option_id)
        if option is None or option.input_version_hash != request.input_version_hash:
            raise Conflict("option missing or input hash changed")
        if at >= option.valid_until:
            raise Conflict("option expired; recompute it")
        case = current.get(Case, option.case_id)
        if case is None or case.status in CLOSED_CASES:
            raise Conflict("case missing or closed")
        if request.decision == "approved":
            held = ledger.reservations(engine, request.scenario_id)
            colours = []
            for inputs in loader(current, case):
                if (inputs.run_id, inputs.scenario_id, inputs.case.id) != (
                    current.run_id,
                    request.scenario_id,
                    case.id,
                ):
                    raise Conflict("input loader returned a different snapshot or case")
                combined = {
                    r.id: r
                    for r in (*inputs.reservations, *held)
                    if inputs.sku is None or r.sku == inputs.sku
                }
                colours.append(replace(inputs, reservations=tuple(combined.values())))
            checked = next((o for o in evaluate_case(colours) if o.id == option.id), None)
            if checked is None or checked != option:
                raise Conflict("proposal inputs or checks changed; recompute it")
            if option.legs and (
                not option.checks
                or any(
                    c.mandatory and c.status not in ("pass", "not_applicable")
                    for c in option.checks
                )
            ):
                raise Conflict("mandatory movement checks do not pass")
        draft = _draft(request, option, at)
        conn.execute(
            insert(ledger.drafts).values(
                scenario_id=request.scenario_id,
                idempotency_key=request.idempotency_key,
                run_id=request.run_id,
                option_id=request.option_id,
                request=encoded,
                payload=draft.model_dump(mode="json"),
            )
        )
        conn.commit()
        return draft


def _draft(request: DecisionRequest, option: ActionOption, at: datetime) -> LocalDraft:
    common = dict(
        version="1",
        available_at=at,
        availability_basis="human decision time",
        source_refs=option.source_refs,
        run_id=request.run_id,
        scenario_id=request.scenario_id,
        computed_at=at,
        input_refs=(ArtifactRef(kind="ActionOption", id=option.id, version=option.version),),
        producer="act.approval",
        producer_version="1",
    )
    decision = Decision(
        **common,
        id=f"decision-{uuid4().hex}",
        option_id=option.id,
        input_version_hash=option.input_version_hash,
        decision=request.decision,
        by=request.by,
        at=at,
        idempotency_key=request.idempotency_key,
        note=request.note,
        dispatch_status="draft",
    )
    held = tuple(
        Reservation(
            **common,
            id=f"{decision.id}-leg-{index}",
            decision_id=decision.id,
            location=leg.origin,
            sku=leg.sku,
            size=leg.size,
            qty=leg.qty,
            status="pending",
            idempotency_key=request.idempotency_key,
            created_at=at,
        )
        for index, leg in enumerate(option.legs)
        if request.decision == "approved"
    )
    return LocalDraft(decision=decision, option=option, reservations=held)
