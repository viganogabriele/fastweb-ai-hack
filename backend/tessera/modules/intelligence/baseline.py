"""FC-01 module: ``fc.baseline`` writes the daily forecast baseline of every store × SKU-colour.

For each store of the run, D is the ``as_of`` date in the store's timezone and the horizon is the
local days D+1..D+``horizon_days`` (RFC §4.9, ``policy.horizon.days`` in ``config/domain.yaml``).
The vintage is the latest forecast run of the store known at ``as_of`` (``src.erp`` rows, already
filtered by availability); it is chosen per store, never per SKU, so a SKU or week absent from it
stays missing and is never filled from an older run. Each week is split over the open days with
the FC-01 pure ``disaggregate``; ``closed_dow`` in ``stores.csv`` gives the closed weekdays.
Holidays and one-off closures are not read: the MVP treats those days as open.

One ``ForecastAdjustment`` per store × SKU, with no case and no overlay:

- every horizon day covered → ``unchanged``: latent and servable scenarios equal the baseline;
- a missing week, conflicting rows for one week or a closed week with a forecast →
  ``not_estimable`` with the reasons, never filled with zero;
- a SKU of the store's assortment absent from the vintage → ``not_estimable``, no baseline.

The target stays ``sales_baseline``: a proxy for demand, not latent demand. Residuals (step 2) are
off by default and not applied here. ``fc.overlay`` builds scenarios on top of these records;
``baseline`` reads one back.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Protocol
from zoneinfo import ZoneInfo

import yaml

from tessera.core import repo
from tessera.core.config import get_settings
from tessera.core.contracts import (
    ArtifactRef,
    ForecastAdjustment,
    ForecastPoint,
    ModuleManifest,
    ModuleResult,
    RunSpec,
    ScenarioValues,
)
from tessera.core.contracts.common import SourceRef
from tessera.modules.intelligence.disaggregation import disaggregate, week_start
from tessera.modules.sources import erp

MAX_HORIZON_DAYS = 14
WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
UNCHANGED_REASON = "Baseline only: no overlay applied, scenarios equal the forecast baseline."

MANIFEST = ModuleManifest(
    id="fc.baseline",
    version="1",
    layer="intelligence",
    description=(
        "Daily sales baseline D+1..D+7 per store × SKU-colour from the forecast vintage valid "
        "at as_of, split over open days; not_estimable when the vintage does not cover it"
    ),
    requires=("src.erp",),
    optional_inputs=(),
    produces=("ForecastAdjustment",),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {
            "horizon_days": {"type": "integer", "minimum": 1, "maximum": MAX_HORIZON_DAYS},
        },
        "additionalProperties": False,
    },
)


class Context(Protocol):
    """The part of PLT-04's ``RunContext`` this module uses."""

    @property
    def spec(self) -> RunSpec: ...

    @property
    def repo(self) -> repo.Repo: ...

    @property
    def params(self) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class Vintage:
    """The latest forecast run of one store at ``as_of``: SKU → week start → rows."""

    run_date: date
    rows: Mapping[str, Mapping[date, tuple[repo.ErpRecord, ...]]]


def default_horizon_days(config_dir: Path) -> int:
    domain = yaml.safe_load((config_dir / "domain.yaml").read_text(encoding="utf-8"))
    return int(domain["policy"]["horizon"]["days"]["value"])


def closed_weekdays(closed_dow: object) -> frozenset[int]:
    """``closed_dow`` ("Sun", "Sat|Sun", empty) as ``date.weekday()`` numbers."""
    if closed_dow is None:
        return frozenset()
    days = set()
    for token in re.split(r"[\s,;|/]+", str(closed_dow).strip()):
        if not token:
            continue
        name = token[:3].lower()
        if name not in WEEKDAYS:
            raise ValueError(f"unknown closed_dow {closed_dow!r}")
        days.add(WEEKDAYS.index(name))
    return frozenset(days)


def latest_vintage(rows: Iterable[repo.ErpRecord]) -> Vintage | None:
    """Rows of the newest ``run_date`` among the forecast rows given (all of one store)."""
    rows = list(rows)
    if not rows:
        return None
    run_date = max(row.data["run_date"] for row in rows)
    grouped: dict[str, dict[date, list[repo.ErpRecord]]] = {}
    for row in rows:
        if row.data["run_date"] == run_date:
            weeks = grouped.setdefault(str(row.data["sku"]), {})
            weeks.setdefault(row.data["week_start"], []).append(row)
    return Vintage(
        run_date,
        {sku: {ws: tuple(rs) for ws, rs in weeks.items()} for sku, weeks in grouped.items()},
    )


def build_store(
    spec: RunSpec,
    store: repo.ErpRecord,
    forecast: Iterable[repo.ErpRecord],
    assortment: Iterable[str],
    horizon_days: int,
) -> list[ForecastAdjustment]:
    """Baselines of one store at the run's ``as_of``. Pure: the rows are given."""
    store_id = str(store.data["store_id"])
    start = spec.as_of.astimezone(ZoneInfo(str(store.data["timezone"]))).date() + timedelta(1)
    end = start + timedelta(days=horizon_days - 1)
    closed_dow = closed_weekdays(store.data.get("closed_dow"))
    # Full weeks: disaggregate spreads each week over all its open days, not only the horizon's.
    first, last = week_start(start), week_start(end) + timedelta(days=6)
    closed = [
        first + timedelta(days=i)
        for i in range((last - first).days + 1)
        if (first + timedelta(days=i)).weekday() in closed_dow
    ]
    vintage = latest_vintage(forecast)
    skus = set(assortment) | set(vintage.rows if vintage else ())

    records = []
    for sku in sorted(skus):
        weeks = vintage.rows.get(sku, {}) if vintage else {}
        weekly: dict[date, float | None] = {}
        reasons: list[str] = []
        used: list[repo.ErpRecord] = []
        for ws, rows in sorted(weeks.items()):
            if not first <= ws <= last:
                continue
            used.extend(rows)
            values = {row.data["fcst_units"] for row in rows}
            if len(values) == 1:
                weekly[ws] = values.pop()  # exact duplicate rows exist in the source
            else:
                weekly[ws] = None
                reasons.append(f"conflicting_forecast:{ws}")
        daily = disaggregate(weekly, start, horizon_days, closed)
        if not weeks:
            reasons.append("sku_not_in_vintage" if vintage else "no_forecast_vintage")
        reasons = list(dict.fromkeys((*reasons, *daily.reasons)))

        vintage_ref = None
        if vintage is not None and weeks:
            row = next(iter(weeks.values()))[0]
            stem = Path(row.source_refs[0].uri).stem
            vintage_ref = ArtifactRef(
                kind="ForecastVintage",
                id=f"{stem}/{store_id}/{sku}",
                version=vintage.run_date.isoformat(),
            )
        inputs = (store, *used)
        source_refs = _unique(ref for row in inputs for ref in row.source_refs)
        series = []
        for point in daily.points:
            flat = None
            if not reasons and point.baseline is not None:
                flat = ScenarioValues(low=point.baseline, base=point.baseline, high=point.baseline)
            series.append(
                ForecastPoint(date=point.day, baseline=point.baseline, latent=flat, servable=flat)
            )
        records.append(
            ForecastAdjustment(
                id=f"baseline-{store_id.lower()}-{sku.lower()}-{start:%Y%m%d}",
                version="v1",
                available_at=max(row.available_at for row in inputs),
                availability_basis="max(store master, forecast vintage rows)",
                source_refs=source_refs,
                run_id=spec.run_id,
                scenario_id=spec.scenario_id,
                computed_at=spec.as_of,
                input_refs=(vintage_ref,) if vintage_ref else (),
                producer=MANIFEST.id,
                producer_version=MANIFEST.version,
                case_ids=(),
                store_id=store_id,
                sku=sku,
                baseline_ref=vintage_ref,
                horizon_start=start,
                horizon_end=end,
                status="not_estimable" if reasons else "unchanged",
                reason="; ".join(reasons) if reasons else UNCHANGED_REASON,
                series=tuple(series),
                components=(),
                proposal_source="code",
            )
        )
    return records


def write_baselines(run_repo: repo.Repo, horizon_days: int) -> ModuleResult:
    spec = run_repo.spec
    records: list[ForecastAdjustment] = []
    abstentions: list[str] = []
    for store_id in spec.stores:
        stores = erp.read(run_repo, "stores", store_id=store_id)
        if not stores:
            abstentions.append(f"{store_id}: store master not available at as_of")
            continue
        forecast = erp.read(run_repo, "forecast", store_id=store_id)
        assortment = erp.read(run_repo, "assortment", store_id=store_id)
        if not forecast:
            abstentions.append(f"{store_id}: no forecast vintage available at as_of")
        skus = {str(row.data["sku"]) for row in assortment}
        records += build_store(spec, stores[-1], forecast, skus, horizon_days)
    new = run_repo.put(*records) if records else 0
    unchanged = sum(r.status == "unchanged" for r in records)
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="blocked" if not unchanged else "degraded" if abstentions else "succeeded",
        counts={
            "baselines": len(records),
            "unchanged": unchanged,
            "not_estimable": len(records) - unchanged,
            "new": new,
        },
        errors=(),
        abstentions=tuple(abstentions),
    )


def run(ctx: Context) -> ModuleResult:
    horizon = ctx.params.get("horizon_days") or default_horizon_days(get_settings().config_dir)
    return write_baselines(ctx.repo, horizon)


def baseline(run_repo: repo.Repo, store_id: str, sku: str) -> ForecastAdjustment | None:
    """The run's ``fc.baseline`` record for one store × SKU-colour, if written and visible."""
    found = run_repo.list(
        ForecastAdjustment, store_id=store_id, sku=sku, where={"producer": MANIFEST.id}
    )
    return found[-1] if found else None


def _unique(refs: Iterable[SourceRef]) -> tuple[SourceRef, ...]:
    return tuple(dict.fromkeys(refs))
