"""Weekly → daily baseline for one store × SKU-colour (RFC §4.9 step 1, FC-01 pure).

    b_d = F_week * p_d,  p_d uniform over the open days of the complete ISO week (MVP)

- Partial week: only the horizon days are taken; the weekly total is not squeezed into them.
- Closed days are 0. A week with every day closed but F_week > 0 is incoherent: not estimable.
- Missing forecast for any horizon day makes the series `not_estimable`: never filled with 0.
  A forecast of 0 stays 0 (it is not missing).
- The target is `sales_baseline`: a proxy for demand, not latent demand.

Dates may be `date`, `datetime` or `pandas.Timestamp` (midnight); they are normalised to `date` so
that keys parsed by pandas still match. Forecast values may be any real number (numpy included).

Pure code: no DB, no dataset access. Reading vintages and the store calendar is the caller's job.
"""

import math
import numbers
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Literal

FORECAST_TARGET = "sales_baseline"
DEFAULT_HORIZON_DAYS = 7

Status = Literal["computed", "not_estimable"]


@dataclass(frozen=True)
class DailyBaselinePoint:
    day: date
    week_start: date
    open: bool
    baseline: float | None  # None = missing, 0.0 = zero


@dataclass(frozen=True)
class DailyBaseline:
    status: Status
    points: tuple[DailyBaselinePoint, ...]
    reasons: tuple[str, ...] = ()
    target: str = FORECAST_TARGET

    @property
    def total(self) -> float | None:
        if self.status != "computed":
            return None
        return sum(p.baseline or 0.0 for p in self.points)


def week_start(day: date) -> date:
    """Monday of the ISO week containing `day` (the forecast files' `week_start`)."""
    day = _as_date(day, "day")
    return day - timedelta(days=day.weekday())


def latest_vintage(run_dates: Iterable[date], as_of: date) -> date | None:
    """Most recent forecast run available at `as_of` (`run_date <= as_of`), or None."""
    as_of = _as_date(as_of, "as_of")
    return max((d for d in map(_as_run_date, run_dates) if d <= as_of), default=None)


def disaggregate(
    weekly: Mapping[date, float | None],
    start: date,
    days: int = DEFAULT_HORIZON_DAYS,
    closed_days: Collection[date] = (),
) -> DailyBaseline:
    """Daily baseline for `days` consecutive days from `start` (usually D+1).

    `weekly` maps ISO week start (Monday) → forecast units for that week, from one vintage.
    Absent keys, None and NaN mean missing. `closed_days` are the store's closed dates.
    """
    if days < 0:
        raise ValueError(f"days must be >= 0, got {days}")
    start = _as_date(start, "start")
    forecast: dict[date, float | None] = {}
    for key, units in weekly.items():
        ws = _as_date(key, "week key")
        if ws.weekday() != 0:
            raise ValueError(f"week key {ws} is not a Monday")
        if ws in forecast:
            raise ValueError(f"week {ws} appears twice")
        forecast[ws] = _as_units(ws, units)

    closed = {_as_date(c, "closed day") for c in closed_days}
    points: list[DailyBaselinePoint] = []
    reasons: list[str] = []
    for i in range(days):
        day = start + timedelta(days=i)
        ws = week_start(day)
        is_open = day not in closed
        units = forecast.get(ws)
        if units is None:
            _add(reasons, f"missing_forecast:{ws}")
            points.append(DailyBaselinePoint(day, ws, is_open, None))
            continue
        n_open = sum(ws + timedelta(days=k) not in closed for k in range(7))
        if n_open == 0 and units > 0:
            _add(reasons, f"closed_week_with_forecast:{ws}")
            points.append(DailyBaselinePoint(day, ws, is_open, None))
            continue
        points.append(DailyBaselinePoint(day, ws, is_open, units / n_open if is_open else 0.0))

    status: Status = "not_estimable" if reasons else "computed"
    return DailyBaseline(status, tuple(points), tuple(reasons))


def _as_date(value: object, name: str) -> date:
    if isinstance(value, datetime):  # pandas.Timestamp is a datetime subclass
        if value.time() != time(0):
            raise ValueError(f"{name} must be a calendar date, got {value!r}")
        return value.date()
    if isinstance(value, date):
        return value
    raise ValueError(f"{name} must be a date, got {value!r}")


def _as_run_date(value: object) -> date:
    return _as_date(value, "run_date")


def _as_units(ws: date, units: object) -> float | None:
    """None or NaN = missing; otherwise a finite real >= 0, returned as float."""
    if units is None:
        return None
    if isinstance(units, bool) or not isinstance(units, numbers.Real):
        raise ValueError(f"forecast for week {ws} must be a number, got {units!r}")
    value = float(units)
    if math.isnan(value):
        return None
    if math.isinf(value) or value < 0:
        raise ValueError(f"forecast for week {ws} must be finite and >= 0, got {units!r}")
    return value


def _add(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)
