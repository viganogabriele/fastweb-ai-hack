from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from tessera.modules.actions.simulation import Arrival, simulate_scenarios, simulate_stock

D0 = date(2026, 10, 23)


def day(i: int) -> date:
    return D0 + timedelta(days=i)


def assert_conserved(sim, arrived: int = 0, shipped: int = 0) -> None:
    assert sim.initial_stock + arrived - shipped == pytest.approx(sim.served + sim.ending)
    for d in sim.days:
        assert d.served + d.lost == pytest.approx(d.demand)
        assert d.served >= 0 and d.lost >= 0 and d.ending >= 0


def test_rfc_7_3_test_5_conservation() -> None:
    sim = simulate_stock(2, D0, [1, 1, 1])
    assert (sim.served, sim.lost, sim.ending) == (2, 1, 0)
    assert [d.lost for d in sim.days] == [0, 0, 1]
    assert_conserved(sim)


def test_late_arrival_does_not_recover_lost_sale() -> None:
    sim = simulate_stock(2, D0, [1, 1, 1, 0], arrivals=[Arrival(day(3), 5)])
    assert sim.lost == 1
    assert sim.days[2].lost == 1
    assert sim.days[3].served == 0 and sim.ending == 5
    assert_conserved(sim, arrived=5)


def test_initial_stock_is_used_once_not_reset_daily() -> None:
    sim = simulate_stock(3, D0, [2, 2, 2])
    assert [d.opening for d in sim.days] == [3, 1, 0]
    assert sim.served == 3 and sim.lost == 3


def test_opening_arrival_sells_same_day() -> None:
    sim = simulate_stock(0, D0, [1, 1], arrivals=[Arrival(day(0), 1, "opening")])
    assert [d.served for d in sim.days] == [1, 0]


def test_closing_arrival_sells_next_day() -> None:
    sim = simulate_stock(0, D0, [1, 1], arrivals=[Arrival(day(0), 1, "closing")])
    assert [d.served for d in sim.days] == [0, 1]
    assert sim.days[1].arrivals == 1


def test_arrivals_after_horizon_are_reported_not_used() -> None:
    sim = simulate_stock(0, D0, [1, 1], arrivals=[Arrival(day(1), 2, "closing")])
    assert sim.served == 0 and sim.arrivals_after_horizon == 2
    assert_conserved(sim)


def test_arrival_before_horizon_is_rejected() -> None:
    with pytest.raises(ValueError, match="precedes"):
        simulate_stock(0, D0, [1], arrivals=[Arrival(day(-1), 1)])


def test_outbound_leaves_before_sales() -> None:
    sim = simulate_stock(3, D0, [2, 1], outbound={day(0): 2})
    assert sim.feasible
    assert [d.served for d in sim.days] == [1, 0]
    assert sim.lost == 2
    assert_conserved(sim, shipped=2)


def test_outbound_above_available_is_infeasible_not_clamped() -> None:
    sim = simulate_stock(2, D0, [1, 1, 1], outbound={day(1): 2})
    assert not sim.feasible
    assert sim.infeasible_on == day(1)
    assert len(sim.days) == 1


def test_outbound_outside_horizon_is_rejected() -> None:
    with pytest.raises(ValueError, match="outside the horizon"):
        simulate_stock(2, D0, [1], outbound={day(1): 1})


def test_fractional_scenario_demand_is_conserved() -> None:
    sim = simulate_stock(2, D0, [0.5, 1.25, 0.75, 0.0])
    assert sim.served == pytest.approx(2) and sim.lost == pytest.approx(0.5)
    assert_conserved(sim)


def test_empty_horizon() -> None:
    sim = simulate_stock(4, D0, [])
    assert sim.days == () and sim.ending == 4 and sim.lost == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"initial_stock": -1},
        {"initial_stock": 1.5},
        {"initial_stock": True},
        {"demand": [1, -1]},
        {"demand": [float("nan")]},
        {"demand": [float("inf")]},
        {"arrivals": [Arrival(D0, 0)]},
        {"arrivals": [Arrival(D0, 1.5)]},
        {"outbound": {D0: -1}},
    ],
)
def test_invalid_inputs_raise(kwargs) -> None:
    args = {"initial_stock": 1, "start": D0, "demand": [1]} | kwargs
    with pytest.raises(ValueError):
        simulate_stock(**args)


def test_scenarios_share_stock_and_keep_order() -> None:
    sims = simulate_scenarios(
        3, D0, {"low": [0, 0, 0], "base": [1, 1, 1], "high": [2, 2, 2]}, [Arrival(day(1), 1)]
    )
    assert [sims[s].lost for s in ("low", "base", "high")] == [0, 0, 2]
    assert [sims[s].ending for s in ("low", "base", "high")] == [4, 1, 0]
    for sim in sims.values():
        assert_conserved(sim, arrived=1)


def test_scenarios_with_different_horizons_are_rejected() -> None:
    with pytest.raises(ValueError, match="different horizons"):
        simulate_scenarios(1, D0, {"low": [1], "high": [1, 1]})


def test_numpy_and_pandas_inputs_are_accepted_and_normalised() -> None:
    stock = pd.DataFrame({"on_hand": [2]}).on_hand.iloc[0]
    demand = pd.Series([1, 1, 1], dtype="int64")
    sim = simulate_stock(
        stock,
        D0,
        list(demand.to_numpy()),
        arrivals=[Arrival(day(2), np.int64(1))],
        outbound={day(0): np.int32(1)},
    )
    assert (sim.served, sim.lost, sim.ending) == (2, 1, 0)
    assert type(sim.initial_stock) is int
    assert all(type(d.demand) is float and type(d.arrivals) is int for d in sim.days)
    assert_conserved(sim, arrived=1, shipped=1)


@pytest.mark.parametrize("bad", [np.float64(1.0), np.bool_(True)])
def test_non_integer_numpy_counts_are_rejected(bad) -> None:
    with pytest.raises(ValueError):
        simulate_stock(bad, D0, [1])


def test_outbound_can_be_feasible_in_one_scenario_only() -> None:
    sims = simulate_scenarios(3, D0, {"low": [0, 0], "high": [2, 0]}, outbound={day(1): 2})
    assert sims["low"].feasible
    assert not sims["high"].feasible and sims["high"].infeasible_on == day(1)
