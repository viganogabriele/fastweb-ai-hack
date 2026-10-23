"""FC-02: optional historical residuals (RFC §4.9.2).

The pure ``estimate`` uses D-14..D-1 in the store timezone and gross unit sales.
Each day uses the latest *store* vintage available strictly before local midnight;
missing SKU/weeks are never backfilled from an older vintage. Five complete,
uncensored observations are required. Unknown availability is not evidence of
availability; endpoint stock alone is deliberately insufficient.

``DayAssessment`` is an explicit caller-supplied, sourced whole-day assessment,
not a deduction from positive opening/closing stock. The current ERP adapter has
no intraday availability or reconciled movements, so the opt-in pipeline module
abstains with r=1. A future verified producer can feed assessments to ``estimate``;
no such facts are invented from the current snapshots. The module is disabled by
default and writes a separate proposal, never changes fc.baseline or adds an
unproven residual to an overlay. No contract or pipeline configuration changes.
"""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

from tesseract.core.contracts import (
    AdjustmentComponent,
    ArtifactRef,
    ForecastAdjustment,
    ModuleManifest,
    ModuleResult,
)
from tesseract.core.contracts.common import SourceRef
from tesseract.core.repo import ErpRecord, Repo
from tesseract.modules.intelligence.disaggregation import (
    closed_weekdays as parse_closed_weekdays,
)
from tesseract.modules.intelligence.disaggregation import (
    disaggregate,
    week_start,
)
from tesseract.modules.sources import erp

LOOKBACK_DAYS = 14
MIN_OBSERVATIONS = 5
KAPPA = 5.0

MANIFEST = ModuleManifest(
    id="fc.residuals",
    version="1",
    layer="intelligence",
    description="Optional historical-vintage residuals; r=1 without verified uncensored days",
    requires=("src.erp", "fc.baseline"),
    optional_inputs=(),
    produces=("ForecastAdjustment",),
    enabled=False,
    mode="live",
    params_schema={"type": "object", "properties": {}, "additionalProperties": False},
)


@dataclass(frozen=True)
class DayAssessment:
    """All checks must be explicitly known and sourced at the replay cutoff.

    ``available_all_day`` includes relevant sizes throughout opening hours.
    ``movements_reconciled`` covers stock/movements and ``complete`` all inputs.
    False excludes the day; None means unknown. Endpoint stock is not sufficient
    to set available_all_day=True. Assessments are for exactly one store/SKU/day.
    """

    store_id: str
    sku: str
    day: date
    available_at: datetime
    source_refs: tuple[SourceRef, ...]
    available_all_day: bool | None = None
    movements_reconciled: bool | None = None
    complete: bool | None = None
    disrupted: bool | None = None


@dataclass(frozen=True)
class ResidualDay:
    day: date
    sales: float | None
    baseline: float | None
    vintage: date | None
    reasons: tuple[str, ...]
    source_refs: tuple[SourceRef, ...]


@dataclass(frozen=True)
class ResidualEstimate:
    multiplier: float
    reason: str
    days: tuple[ResidualDay, ...] = ()

    @property
    def eligible(self) -> tuple[ResidualDay, ...]:
        return tuple(day for day in self.days if not day.reasons)


def _aware(value: datetime) -> datetime:
    if value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return value


def _visible(row: ErpRecord, cutoff: datetime) -> bool:
    return row.available_at is not None and _aware(row.available_at) <= cutoff


def _units(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) and value >= 0 else None


def estimate(
    *,
    store_id: str,
    sku: str,
    as_of: datetime,
    timezone: str,
    forecasts: Iterable[ErpRecord],
    sales: Iterable[ErpRecord],
    assessments: Iterable[DayAssessment] = (),
    closed_weekdays: frozenset[int] = frozenset(),
    enabled: bool = False,
) -> ResidualEstimate:
    """Pure, conservative estimator; disabled unless the caller explicitly opts in."""
    _aware(as_of)
    zone = ZoneInfo(timezone)
    if not enabled:
        return ResidualEstimate(1.0, "disabled")
    if not closed_weekdays <= set(range(7)):
        raise ValueError("closed weekdays must be in 0..6")
    today = as_of.astimezone(zone).date()
    forecasts = [
        r
        for r in forecasts
        if r.table == "forecast" and r.data["store_id"] == store_id and _visible(r, as_of)
    ]
    sales = [
        r
        for r in sales
        if r.table == "sales"
        and r.data["store_id"] == store_id
        and r.data["sku"] == sku
        and _visible(r, as_of)
    ]
    assessments = [
        a
        for a in assessments
        if a.store_id == store_id and a.sku == sku and _aware(a.available_at) <= as_of
    ]
    days = []
    for offset in range(LOOKBACK_DAYS, 0, -1):
        day = today - timedelta(days=offset)
        reasons = []
        refs = []
        if day.weekday() in closed_weekdays:
            reasons.append("closed_day")
        start = datetime.combine(day, time.min, tzinfo=zone)
        known = [r for r in forecasts if r.available_at < start and r.data["run_date"] < day]
        vintage = max((r.data["run_date"] for r in known), default=None)
        rows = [
            r
            for r in known
            if r.data["run_date"] == vintage
            and r.data["sku"] == sku
            and r.data["week_start"] == week_start(day)
        ]
        refs.extend(ref for row in rows for ref in row.source_refs)
        weekly = {_units(r.data["fcst_units"]) for r in rows}
        baseline = None
        if not rows:
            reasons.append("missing_historical_forecast")
        elif None in weekly or len(weekly) != 1:
            reasons.append("invalid_or_conflicting_forecast")
        else:
            ws = week_start(day)
            closed = [ws + timedelta(days=i) for i in closed_weekdays]
            daily = disaggregate({ws: weekly.pop()}, day, 1, closed)
            baseline = daily.points[0].baseline
            reasons.extend(daily.reasons)
        sold = [r for r in sales if r.data["business_date"] == day]
        refs.extend(ref for row in sold for ref in row.source_refs)
        values = {_units(r.data["units_sold"]) for r in sold}
        actual = None
        if not sold:
            reasons.append("missing_sales")
        elif None in values or len(values) != 1:
            reasons.append("invalid_or_conflicting_sales")
        else:
            actual = values.pop()  # gross units: returns are deliberately not subtracted
        checks = [a for a in assessments if a.day == day]
        if len(checks) != 1 or not checks[0].source_refs:
            reasons.append("availability_not_assessable")
        else:
            check = checks[0]
            refs.extend(check.source_refs)
            for value, good, reason in (
                (check.available_all_day, True, "stockout_or_size_availability_unknown"),
                (check.movements_reconciled, True, "movements_not_reconciled"),
                (check.complete, True, "incomplete_data"),
                (check.disrupted, False, "disruption_or_unknown"),
            ):
                if value is not good:
                    reasons.append(reason)
        days.append(
            ResidualDay(day, actual, baseline, vintage, tuple(reasons), tuple(dict.fromkeys(refs)))
        )
    eligible = [d for d in days if not d.reasons]
    if any(d.baseline == 0 and d.sales > 0 for d in eligible):
        return ResidualEstimate(1.0, "cold_start_or_forecast_bias", tuple(days))
    if len(eligible) < MIN_OBSERVATIONS:
        reason = "insufficient_complete_observations"
        if any("availability_not_assessable" in d.reasons for d in days):
            reason += "; availability_not_assessable"
        return ResidualEstimate(1.0, reason, tuple(days))
    ratio = (sum(d.sales for d in eligible) + KAPPA) / (sum(d.baseline for d in eligible) + KAPPA)
    return ResidualEstimate(min(2.0, max(0.5, ratio)), "estimated", tuple(days))


class Context(Protocol):
    @property
    def repo(self) -> Repo: ...


def run(ctx: Context) -> ModuleResult:
    """Persist an auditable r=1 proposal: current ERP cannot prove uncensored days.

    Eligibility checks are not exposed as user-configurable booleans. Until a
    verified assessment producer exists, enabling the module cannot authorize
    numerical correction. Existing baseline and overlay records are untouched.
    """
    records = []
    abstentions = []
    run_repo = ctx.repo
    for store_id in run_repo.spec.stores:
        stores = erp.read(run_repo, "stores", store_id=store_id)
        if not stores:
            abstentions.append(f"{store_id}: store master unavailable")
            continue
        forecasts = erp.read(run_repo, "forecast", store_id=store_id)
        sales = erp.read(run_repo, "sales", store_id=store_id)
        for base in run_repo.list(
            ForecastAdjustment, store_id=store_id, where={"producer": "fc.baseline"}
        ):
            result = estimate(
                store_id=store_id,
                sku=base.sku,
                as_of=run_repo.spec.as_of,
                timezone=str(stores[-1].data["timezone"]),
                forecasts=forecasts,
                sales=sales,
                closed_weekdays=parse_closed_weekdays(stores[-1].data.get("closed_dow")),
                enabled=True,
            )
            component = AdjustmentComponent(
                type="residual",
                episode_refs=(),
                evidence_refs=(),
                unit="units",
                effective_from=run_repo.spec.as_of,
                effective_until=run_repo.spec.as_of,
                reference_time=run_repo.spec.as_of,
                formula_version="FC-02-v1",
                explanation="Residual not applied: " + result.reason,
                params={
                    "multiplier": result.multiplier,
                    "reason": result.reason,
                    "kappa": KAPPA,
                    "lookback_days": LOOKBACK_DAYS,
                    "minimum_observations": MIN_OBSERVATIONS,
                    "days": [
                        {
                            "date": d.day.isoformat(),
                            "sales": d.sales,
                            "baseline": d.baseline,
                            "vintage": d.vintage.isoformat() if d.vintage else None,
                            "excluded_reasons": list(d.reasons),
                        }
                        for d in result.days
                    ],
                },
            )
            payload = base.model_dump()
            payload.update(
                id=f"residual-{base.id}",
                producer=MANIFEST.id,
                producer_version=MANIFEST.version,
                computed_at=run_repo.spec.as_of,
                available_at=run_repo.spec.as_of,
                availability_basis="residual assessment at run as_of",
                input_refs=(
                    ArtifactRef(kind="ForecastAdjustment", id=base.id, version=base.version),
                ),
                source_refs=tuple(
                    dict.fromkeys(
                        (
                            *base.source_refs,
                            *stores[-1].source_refs,
                            *(r for d in result.days for r in d.source_refs),
                        )
                    )
                ),
                components=(component,),
                reason=f"{base.reason or ''}; residual: {result.reason}",
            )
            records.append(ForecastAdjustment.model_validate(payload))
            abstentions.append(f"{store_id}/{base.sku}: {result.reason}")
    new = run_repo.put(*records) if records else 0
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if records else "blocked",
        counts={"proposals": len(records), "new": new, "corrected": 0},
        errors=(),
        abstentions=tuple(abstentions),
    )
