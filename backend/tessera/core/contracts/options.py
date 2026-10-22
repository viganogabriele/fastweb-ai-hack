from typing import Literal, Self

from pydantic import model_validator

from .common import (
    ArtifactRef,
    Contract,
    DerivedRecord,
    Instant,
    NonNegative,
    PositiveInt,
    Text,
    ordered,
)


class Check(Contract):
    name: Text
    status: Literal["pass", "fail", "unknown", "not_applicable"]
    mandatory: bool
    detail: Text
    source_refs: tuple[ArtifactRef, ...]


class Leg(Contract):
    origin: Text
    dest: Text
    sku: Text
    size: Text
    ean: str | None = None
    qty: PositiveInt
    pickup_at: Instant
    eta_at: Instant
    sellable_at: Instant
    lane_id: Text
    cost_eur: NonNegative | None = None

    @model_validator(mode="after")
    def route(self) -> Self:
        if self.origin == self.dest:
            raise ValueError("movement requires distinct locations")
        ordered(self.pickup_at, self.eta_at)
        ordered(self.eta_at, self.sellable_at)
        return self


class ScenarioOutcome(Contract):
    scenario_id: Text
    lost_units_dest: NonNegative | None
    lost_units_donor: NonNegative | None
    leftover_units_dest: NonNegative | None
    leftover_units_donor: NonNegative | None
    transport_cost_eur: NonNegative | None = None
    demand_basis: Text
    size_allocation_basis: Text


class ActionOption(DerivedRecord):
    case_id: Text
    forecast_ref: ArtifactRef | None = None
    kind: Literal[
        "hold",
        "verify_stock",
        "ask_store",
        "replenish_dc",
        "transfer",
        "combo",
        "notify_owner",
    ]
    legs: tuple[Leg, ...]
    checks: tuple[Check, ...]
    outcomes: tuple[ScenarioOutcome, ...] | None = None
    baseline_outcomes: tuple[ScenarioOutcome, ...] | None = None
    assumptions: tuple[Text, ...]
    valid_until: Instant
    recommended: bool
    rationale: Text
    input_version_hash: Text

    @model_validator(mode="after")
    def movement(self) -> Self:
        for outcomes in (self.outcomes, self.baseline_outcomes):
            if outcomes is not None:
                ids = [outcome.scenario_id for outcome in outcomes]
                if len(ids) != len(set(ids)):
                    raise ValueError("scenario outcomes must have unique scenario ids")
        if (
            self.outcomes is not None
            and self.baseline_outcomes is not None
            and {outcome.scenario_id for outcome in self.outcomes}
            != {outcome.scenario_id for outcome in self.baseline_outcomes}
        ):
            raise ValueError("option and baseline outcomes must cover the same scenarios")
        is_movement = self.kind in ("replenish_dc", "transfer", "combo")
        if is_movement != bool(self.legs):
            raise ValueError(
                "movement options require legs; informational options must not move stock"
            )
        if self.recommended and is_movement:
            if not self.checks or any(
                c.mandatory and c.status not in ("pass", "not_applicable") for c in self.checks
            ):
                raise ValueError("mandatory fail/unknown checks block movement recommendations")
            if self.forecast_ref is None or not self.outcomes or not self.baseline_outcomes:
                raise ValueError(
                    "movement recommendations require forecast and comparison outcomes"
                )
            if any(leg.cost_eur is None for leg in self.legs):
                raise ValueError("unknown transport cost requires human choice")
            if any(
                value is None
                for outcome in (*self.outcomes, *self.baseline_outcomes)
                for value in (
                    outcome.lost_units_dest,
                    outcome.lost_units_donor,
                    outcome.leftover_units_dest,
                    outcome.leftover_units_donor,
                )
            ):
                raise ValueError("unknown outcomes block numerical recommendations")
        return self


class Reservation(DerivedRecord):
    decision_id: Text
    location: Text
    sku: Text
    size: Text
    qty: PositiveInt
    status: Literal["pending", "committed", "released", "unknown"]
    idempotency_key: Text
    external_ref: str | None = None
    created_at: Instant
