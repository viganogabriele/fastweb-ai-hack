from datetime import date
from typing import Literal, Self

from pydantic import JsonValue, model_validator

from .common import (
    ArtifactRef,
    Contract,
    DerivedRecord,
    Instant,
    NonNegative,
    Text,
    Unit,
    ordered,
    require_reason,
)


class ScenarioValues(Contract):
    low: NonNegative
    base: NonNegative
    high: NonNegative

    @model_validator(mode="after")
    def scenario_order(self) -> Self:
        if not self.low <= self.base <= self.high:
            raise ValueError("scenarios must satisfy low <= base <= high")
        return self


class ForecastPoint(Contract):
    date: date
    baseline: NonNegative | None
    latent: ScenarioValues | None
    servable: ScenarioValues | None
    actual: NonNegative | None = None

    @model_validator(mode="after")
    def exposure(self) -> Self:
        if self.baseline is None and (self.latent is not None or self.servable is not None):
            raise ValueError("missing baseline cannot produce quantified scenarios")
        if self.servable is not None:
            if self.latent is None:
                raise ValueError("servable scenarios require latent scenarios")
            if any(
                getattr(self.servable, s) > getattr(self.latent, s) for s in ("low", "base", "high")
            ):
                raise ValueError("servable demand cannot exceed latent demand")
        return self


class AdjustmentComponent(Contract):
    type: Text
    episode_refs: tuple[ArtifactRef, ...]
    evidence_refs: tuple[ArtifactRef, ...]
    params: dict[str, JsonValue]
    unit: Unit
    effective_from: Instant
    effective_until: Instant
    reference_time: Instant
    formula_version: Text
    explanation: Text

    @model_validator(mode="after")
    def interval(self) -> Self:
        ordered(self.effective_from, self.effective_until)
        return self


class ForecastAdjustment(DerivedRecord):
    case_ids: tuple[Text, ...]
    store_id: Text
    sku: Text
    baseline_ref: ArtifactRef | None
    forecast_target: Literal["sales_baseline"] = "sales_baseline"
    horizon_start: date
    horizon_end: date
    status: Literal["computed", "unchanged", "not_estimable"]
    reason: str | None = None
    series: tuple[ForecastPoint, ...]
    components: tuple[AdjustmentComponent, ...]
    proposal_source: Literal["code", "agent", "human"]

    @model_validator(mode="after")
    def horizon(self) -> Self:
        if self.horizon_end < self.horizon_start:
            raise ValueError("horizon_end must not precede horizon_start")
        days = [point.date for point in self.series]
        if days != sorted(set(days)):
            raise ValueError("forecast dates must be unique and ordered")
        if any(not self.horizon_start <= day <= self.horizon_end for day in days):
            raise ValueError("forecast dates must lie within the horizon")
        require_reason(self.status, self.reason, ("unchanged", "not_estimable"))
        if self.status in ("computed", "unchanged"):
            if (
                self.baseline_ref is None
                or len(days) != (self.horizon_end - self.horizon_start).days + 1
            ):
                raise ValueError("estimable forecast requires a baseline and every horizon day")
            for point in self.series:
                if point.baseline is None or point.latent is None or point.servable is None:
                    raise ValueError("estimable forecast cannot contain missing values")
                if self.status == "unchanged" and any(
                    value != point.baseline
                    for values in (point.latent, point.servable)
                    for value in (values.low, values.base, values.high)
                ):
                    raise ValueError("unchanged scenarios must equal baseline")
        return self
