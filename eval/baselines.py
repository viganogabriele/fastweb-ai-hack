"""EVL-04 comparison baselines, computed from `generated/sources/` only (RFC §7.2).

Both detectors replay the evening of each day without look-ahead (`generated/README.md` §4):
ERP sales and stock for business date B are certified the next day, so an alert computed
from B is available at `B + 1` 20:00 store-local time, never earlier.

- **Stock baseline** (operational stock policy): a store×SKU-size whose end-of-day on-hand
  falls from above `threshold` to `threshold` or below. One alert per store×SKU per day,
  carrying the sizes that crossed; a size re-arms only after it is restocked above it.
- **Sales detector**: trailing-mean Poisson test on the last `window` days of units sold
  against the previous `history` days, per store×SKU (upward only: one or two units a day
  are too few to read a fall) and per store total (both directions). A key and direction
  stay silent for `cooldown` days after an alert. Sales are censored by stock, by design.

No answer key is read here. Thresholds are protocol parameters, fixed on dev stores.
"""

import csv
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from functools import cache
from math import sqrt
from pathlib import Path
from zoneinfo import ZoneInfo

ERP = Path("generated/sources/erp")
CERTIFIED_AT = time(20, 0)  # ERP facts of day B are usable on the evening of B + 1


@dataclass(frozen=True)
class Alert:
    """One alert from any method, in a common shape for matching to oracle events."""

    method: str
    store_id: str
    at: datetime  # UTC instant at which the alert is available
    scope_level: str  # sku_size | sku | style | category | store | unknown
    skus: frozenset[str] = frozenset()  # resolved SKU-colour set, empty for store/unknown
    sizes: frozenset[str] = frozenset()  # empty means any size
    direction: str | None = None  # up | down | stockout | None (unknown)
    ref: str = ""
    decision_due_at: datetime | None = None
    sources: tuple[str, ...] = field(default=(), compare=False)


@cache
def store_zones(root: Path) -> dict[str, ZoneInfo]:
    with (root / ERP / "master_data/stores.csv").open(encoding="utf-8") as stream:
        return {row["store_id"]: ZoneInfo(row["timezone"]) for row in csv.DictReader(stream)}


def local_instant(root: Path, store_id: str, day: date, at: time) -> datetime:
    return datetime.combine(day, at, store_zones(root)[store_id]).astimezone(UTC)


def certified(root: Path, store_id: str, business_date: date) -> datetime:
    """When an ERP fact of `business_date` becomes available to the evening replay."""
    return local_instant(root, store_id, business_date + timedelta(days=1), CERTIFIED_AT)


def _days(start: date, end: date):
    day = start
    while day <= end:
        yield day
        day += timedelta(days=1)


def stock_alerts(
    root: Path, stores: frozenset[str], start: date, end: date, threshold: int = 0
) -> list[Alert]:
    """Snapshots from `start - 1` (arming state) to `end`; alerts on dates `start..end`."""
    armed: dict[tuple[str, str, str], bool] = {}
    alerts = []
    for day in _days(start - timedelta(days=1), end):
        path = root / ERP / f"inventory/store_stock_daily/stock_eod_{day.isoformat()}.csv"
        if not path.exists():
            continue  # Missing snapshot: no evidence either way, state carries over.
        crossed: dict[tuple[str, str], set[str]] = defaultdict(set)
        with path.open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                if row["store_id"] not in stores:
                    continue
                key = (row["store_id"], row["sku"], row["size"])
                above = int(row["on_hand"]) > threshold
                if not above and armed.get(key) and day >= start:
                    crossed[key[:2]].add(key[2])
                armed[key] = above
        for (store_id, sku), sizes in sorted(crossed.items()):
            alerts.append(
                Alert(
                    method="stock",
                    store_id=store_id,
                    at=certified(root, store_id, day),
                    scope_level="sku_size",
                    skus=frozenset({sku}),
                    sizes=frozenset(sizes),
                    direction="stockout",
                    ref=f"stock:{store_id}:{sku}:{day.isoformat()}",
                )
            )
    return alerts


def _sales(root: Path, stores: frozenset[str], first: date, last: date):
    """Units sold per (store, sku) and day; absent rows are zero sales."""
    units: dict[tuple[str, str], dict[date, int]] = defaultdict(dict)
    month = date(first.year, first.month, 1)
    while month <= last:
        path = root / ERP / f"sales/daily_store_sku/sales_daily_{month:%Y_%m}.csv"
        if path.exists():
            with path.open(encoding="utf-8") as stream:
                for row in csv.DictReader(stream):
                    day = date.fromisoformat(row["business_date"])
                    if row["store_id"] in stores and first <= day <= last:
                        series = units[(row["store_id"], row["sku"])]
                        series[day] = series.get(day, 0) + int(row["units_sold"])
        month = (month + timedelta(days=32)).replace(day=1)
    return units


def _surprise(observed: float, expected: float, z: float, min_units: int) -> str | None:
    spread = z * sqrt(expected + 1)
    if observed >= min_units and observed - expected >= spread:
        return "up"
    if expected >= min_units and expected - observed >= spread:
        return "down"
    return None


def sales_alerts(
    root: Path,
    stores: frozenset[str],
    start: date,
    end: date,
    z: float = 3.0,
    history: int = 28,
    window: int = 3,
    min_units: int = 3,
    cooldown: int = 7,
) -> list[Alert]:
    """Alerts for business dates `start - 1..end`, computed from that date and before only."""
    first = start - timedelta(days=1 + window + history)
    units = _sales(root, stores, first, end)
    totals: dict[tuple[str, str], dict[date, int]] = defaultdict(dict)
    for (store_id, _), series in units.items():
        total = totals[(store_id, "*")]
        for day, value in series.items():
            total[day] = total.get(day, 0) + value
    alerts = []
    for level, table in (("sku", units), ("store", totals)):
        for (store_id, sku), series in sorted(table.items()):
            silent_until: dict[str, date] = {}
            for day in _days(start - timedelta(days=1), end):
                recent = sum(series.get(day - timedelta(days=i), 0) for i in range(window))
                past = sum(series.get(day - timedelta(days=window + i), 0) for i in range(history))
                direction = _surprise(recent, past * window / history, z, min_units)
                if direction is None or (level == "sku" and direction == "down"):
                    continue
                if day < silent_until.get(direction, date.min):
                    continue
                silent_until[direction] = day + timedelta(days=cooldown)
                alerts.append(
                    Alert(
                        method="sales",
                        store_id=store_id,
                        at=certified(root, store_id, day),
                        scope_level=level,
                        skus=frozenset({sku}) if level == "sku" else frozenset(),
                        direction=direction,
                        ref=f"sales:{store_id}:{sku}:{day.isoformat()}:{direction}",
                    )
                )
    return alerts
