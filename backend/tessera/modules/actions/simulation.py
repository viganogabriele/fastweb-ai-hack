"""Recursive daily stock simulation for one location × SKU-size (RFC §4.10, ACT-01 pure).

For each day h of the horizon:

    available_h = ending_(h-1) + sellable_arrivals_h - outbound_h
    served_h    = min(demand_h, available_h)
    lost_h      = demand_h - served_h
    ending_h    = available_h - served_h

The starting stock is used once, never reset per day. Lost sales are not backlog: a later arrival
does not recover them. An arrival is sellable on its day only if it lands before opening; a
closing arrival becomes sellable the next day. Outbound leaves before the day's sales (conservative
for the donor; the RFC does not fix the intra-day order). Outbound larger than available stock
makes the plan infeasible: the simulation stops there instead of clamping. Because earlier sales
drain stock, the same outbound can be feasible in one demand scenario and not in another.

Counts accept any integer type (numpy/pandas included) and are normalised to `int`; demand accepts
any real number and is normalised to `float`.

Pure code: no DB, no API, no LLM. Building the initial stock and the demand series (snapshot
bridge, scenarios, size curve) is the caller's job.
"""

import math
import numbers
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

ArrivalTiming = Literal["opening", "closing"]


@dataclass(frozen=True)
class Arrival:
    """Sellable units landing at the location. `closing` arrivals sell from the next day."""

    on: date
    qty: int
    timing: ArrivalTiming = "opening"

    @property
    def sellable_on(self) -> date:
        return self.on if self.timing == "opening" else self.on + timedelta(days=1)


@dataclass(frozen=True)
class StockDay:
    day: date
    opening: float
    arrivals: int
    outbound: int
    available: float
    demand: float
    served: float
    lost: float
    ending: float


@dataclass(frozen=True)
class StockSimulation:
    """Trajectory over the horizon. If `feasible` is False, `days` stops before `infeasible_on`
    and the totals cover only the simulated days: do not compare them with other options."""

    initial_stock: int
    days: tuple[StockDay, ...]
    feasible: bool = True
    infeasible_on: date | None = None
    arrivals_after_horizon: int = 0

    @property
    def served(self) -> float:
        return sum(d.served for d in self.days)

    @property
    def lost(self) -> float:
        return sum(d.lost for d in self.days)

    @property
    def ending(self) -> float:
        return self.days[-1].ending if self.days else float(self.initial_stock)


def simulate_stock(
    initial_stock: int,
    start: date,
    demand: Sequence[float],
    arrivals: Sequence[Arrival] = (),
    outbound: Mapping[date, int] | None = None,
) -> StockSimulation:
    """Simulate `len(demand)` consecutive days from `start`; `demand[i]` is for `start + i`.

    Closed days are demand 0. Arrivals sellable before `start` belong in `initial_stock` and are
    rejected; those sellable after the horizon are counted in `arrivals_after_horizon`.
    """
    initial_stock = _check_count("initial_stock", initial_stock, allow_zero=True)
    demand = [_check_demand(i, d) for i, d in enumerate(demand)]
    outbound = {
        day: _check_count(f"outbound on {day}", qty, allow_zero=True)
        for day, qty in (outbound or {}).items()
    }
    horizon = [start + timedelta(days=i) for i in range(len(demand))]
    end = horizon[-1] if horizon else start - timedelta(days=1)

    arriving: dict[date, int] = {}
    after_horizon = 0
    for a in arrivals:
        qty = _check_count("arrival qty", a.qty, allow_zero=False)
        if a.sellable_on < start:
            raise ValueError(f"arrival sellable on {a.sellable_on} precedes the horizon start")
        if a.sellable_on > end:
            after_horizon += qty
        else:
            arriving[a.sellable_on] = arriving.get(a.sellable_on, 0) + qty
    for day in outbound:
        if not start <= day <= end:
            raise ValueError(f"outbound on {day} is outside the horizon {start}..{end}")

    days: list[StockDay] = []
    ending = float(initial_stock)
    for day, dem in zip(horizon, demand, strict=True):
        arr = arriving.get(day, 0)
        out = outbound.get(day, 0)
        if out > ending + arr:
            return StockSimulation(initial_stock, tuple(days), False, day, after_horizon)
        available = ending + arr - out
        served = min(dem, available)
        days.append(
            StockDay(
                day=day,
                opening=ending,
                arrivals=arr,
                outbound=out,
                available=available,
                demand=dem,
                served=served,
                lost=dem - served,
                ending=available - served,
            )
        )
        ending = available - served
    return StockSimulation(initial_stock, tuple(days), arrivals_after_horizon=after_horizon)


def simulate_scenarios(
    initial_stock: int,
    start: date,
    demand_by_scenario: Mapping[str, Sequence[float]],
    arrivals: Sequence[Arrival] = (),
    outbound: Mapping[date, int] | None = None,
) -> dict[str, StockSimulation]:
    """Same stock, arrivals and outbound under each demand scenario (e.g. low/base/high)."""
    lengths = {len(d) for d in demand_by_scenario.values()}
    if len(lengths) > 1:
        raise ValueError(f"scenarios cover different horizons: {sorted(lengths)} days")
    return {
        sid: simulate_stock(initial_stock, start, dem, arrivals, outbound)
        for sid, dem in demand_by_scenario.items()
    }


def _check_count(name: str, value: object, *, allow_zero: bool) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, numbers.Integral)
        or value < (0 if allow_zero else 1)
    ):
        bound = ">= 0" if allow_zero else ">= 1"
        raise ValueError(f"{name} must be an integer {bound}, got {value!r}")
    return int(value)


def _check_demand(i: int, value: object) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, numbers.Real)
        or not math.isfinite(value)
        or value < 0
    ):
        raise ValueError(f"demand[{i}] must be a finite number >= 0, got {value!r}")
    return float(value)
