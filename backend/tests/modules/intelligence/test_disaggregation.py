from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from tessera.modules.intelligence.disaggregation import (
    disaggregate,
    latest_vintage,
    week_start,
)

MON = date(2026, 10, 19)  # Monday, ISO week 2026-W43
NEXT = MON + timedelta(days=7)


def d(i: int) -> date:
    return MON + timedelta(days=i)


def values(bl) -> list[float | None]:
    return [p.baseline for p in bl.points]


def test_week_start() -> None:
    assert week_start(date(2026, 10, 22)) == MON
    assert week_start(MON) == MON
    assert week_start(date(2026, 10, 25)) == MON


def test_full_week_uniform_sums_to_weekly_total() -> None:
    bl = disaggregate({MON: 14.0}, MON)
    assert bl.status == "computed"
    assert values(bl) == [2.0] * 7
    assert bl.total == pytest.approx(14.0)
    assert bl.target == "sales_baseline"


def test_partial_week_does_not_redistribute_total() -> None:
    # D = Thu Oct 22, horizon D+1..D+7 = Fri Oct 23 .. Thu Oct 29
    bl = disaggregate({MON: 7.0, NEXT: 14.0}, d(4))
    assert values(bl) == [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0]
    assert bl.total == pytest.approx(3.0 + 8.0)
    assert [p.week_start for p in bl.points] == [MON] * 3 + [NEXT] * 4


def test_closed_days_are_zero_and_weight_moves_to_open_days() -> None:
    bl = disaggregate({MON: 12.0}, MON, closed_days={d(6)})
    assert values(bl) == [2.0] * 6 + [0.0]
    assert bl.points[6].open is False
    assert bl.total == pytest.approx(12.0)


def test_closed_day_outside_horizon_still_counts_for_weights() -> None:
    bl = disaggregate({MON: 12.0}, d(4), days=2, closed_days={d(0)})
    assert values(bl) == [2.0, 2.0]


def test_missing_week_is_not_estimable_not_zero() -> None:
    bl = disaggregate({MON: 7.0}, d(4))
    assert bl.status == "not_estimable"
    assert bl.reasons == (f"missing_forecast:{NEXT}",)
    assert values(bl)[3:] == [None] * 4
    assert bl.total is None


@pytest.mark.parametrize("missing", [None, float("nan")])
def test_none_and_nan_mean_missing(missing) -> None:
    bl = disaggregate({MON: missing}, MON, days=2)
    assert bl.status == "not_estimable"
    assert values(bl) == [None, None]


def test_zero_forecast_stays_zero() -> None:
    bl = disaggregate({MON: 0.0}, MON)
    assert bl.status == "computed"
    assert values(bl) == [0.0] * 7
    assert bl.total == 0.0


def test_all_closed_week_with_positive_forecast_is_incoherent() -> None:
    bl = disaggregate({MON: 5.0}, MON, days=2, closed_days={d(k) for k in range(7)})
    assert bl.status == "not_estimable"
    assert bl.reasons == (f"closed_week_with_forecast:{MON}",)


def test_all_closed_week_with_zero_forecast_is_fine() -> None:
    bl = disaggregate({MON: 0.0}, MON, days=2, closed_days={d(k) for k in range(7)})
    assert bl.status == "computed"
    assert values(bl) == [0.0, 0.0]


def test_empty_horizon() -> None:
    bl = disaggregate({}, MON, days=0)
    assert bl.status == "computed" and bl.points == () and bl.total == 0


@pytest.mark.parametrize(
    ("weekly", "days"),
    [({d(1): 1.0}, 7), ({MON: -1.0}, 7), ({MON: float("inf")}, 7), ({MON: 1.0}, -1)],
)
def test_invalid_inputs_raise(weekly, days) -> None:
    with pytest.raises(ValueError):
        disaggregate(weekly, MON, days=days)


def test_latest_vintage_has_no_look_ahead() -> None:
    runs = [date(2026, 10, 5), date(2026, 10, 12), date(2026, 10, 19)]
    assert latest_vintage(runs, date(2026, 10, 22)) == date(2026, 10, 19)
    assert latest_vintage(runs, date(2026, 10, 18)) == date(2026, 10, 12)
    assert latest_vintage(runs, date(2026, 10, 19)) == date(2026, 10, 19)
    assert latest_vintage(runs, date(2026, 10, 1)) is None


def test_pandas_timestamps_and_numpy_values_match_plain_dates() -> None:
    weekly = {pd.Timestamp(MON): np.float64(7.0), pd.Timestamp(NEXT): np.int64(14)}
    bl = disaggregate(weekly, pd.Timestamp(d(4)), closed_days={pd.Timestamp(d(6))})
    assert bl == disaggregate({MON: 7.0, NEXT: 14.0}, d(4), closed_days={d(6)})
    assert bl.status == "computed"
    assert bl.points[2].open is False and bl.points[2].baseline == 0.0
    assert all(type(p.day) is date and type(p.week_start) is date for p in bl.points)


def test_week_start_and_vintage_accept_timestamps() -> None:
    assert week_start(pd.Timestamp("2026-10-22")) == MON
    runs = pd.to_datetime(pd.Series(["2026-10-12", "2026-10-19"]))
    assert latest_vintage(runs, pd.Timestamp("2026-10-22")) == date(2026, 10, 19)


@pytest.mark.parametrize(
    "weekly",
    [
        {pd.Timestamp("2026-10-19 12:00"): 1.0},  # not a calendar date
        {MON: 1.0, pd.Timestamp(MON): 2.0},  # same week twice
        {MON: "3.0"},  # not a number
        {MON: True},
        {"2026-10-19": 1.0},  # string key
    ],
)
def test_ambiguous_inputs_raise(weekly) -> None:
    with pytest.raises(ValueError):
        disaggregate(weekly, MON)
