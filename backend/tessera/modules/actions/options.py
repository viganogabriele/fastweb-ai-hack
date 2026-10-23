"""ACT-02: ``act.options`` and the shared ``evaluate_options()`` service (RFC §4.10).

``evaluate_options(inputs)`` is pure: everything it reads is in ``OptionInputs``, gathered at the
run's ``as_of`` by ``gather``. The investigator tools (AG-03) and approval (ACT-03) call it again
on the same or edited inputs; ``input_version_hash`` tells them whether an option is stale.

Options for one case, all alternatives (none reserves stock):

- ``hold``, ``verify_stock``, ``ask_store``, ``notify_owner`` always. Informational options have
  ``outcomes=None``; ``hold`` carries the destination's lost units when they are computable, so it
  never competes by pretending zero losses.
- At most one domestic ``transfer`` store → store: the top candidate over donors × sizes ×
  quantities ``1..q_max``. ``q_max`` = donor stock net of ledger reservations and of the donor
  floor, capped by ``max_units_per_transfer``: bounded by availability and policy, never chosen
  by a model. Cross-border donors are not candidates in the MVP, and a lane that needs customs
  fails. A donor without a lane known at ``as_of`` (a leg needs pickup and ETA), or a donor size
  with no unit left after the ledger, gives no candidate; the reason is stated instead.

Every movement check is mandatory and comes back ``pass``, ``fail`` or ``unknown``; missing data
or a missing policy entry is ``unknown``, never an implicit permission. Without a verified size
curve (``size_demand_unknown``) nothing is quantified per size and the move is blocked: the
option still shows the stock per size and the checks, and the store is asked to confirm. Policy
values come from ``policy.options`` in ``config/domain.yaml``; two of them are declarations that
stand in for missing data and are named as such in the checks: ``size_curve: uniform`` (colour
demand split evenly over the master sizes, used by ``gather`` when no verified curve is given)
and ``store_stock_netted`` (store ``on_hand`` taken as net of reservations and quality holds).

Simulation (ACT-01 ``simulate_stock``), per scenario low/base/high of servable demand × the
location's size share, over the destination's horizon D+1..D+n:

- the destination starts from its last known snapshot, with no consumption before the horizon
  (conservative: it understates the benefit of a move); units in transit to it with unknown
  timing make the check ``unknown``;
- the donor starts from its snapshot minus ledger reservations minus the scenario's mean daily
  demand for every day between the snapshot and the horizon, floored to whole units;
- outbound leaves the donor on the pickup day (the horizon start if earlier); the contract ETA is
  a date, so units arrive at closing and are sellable the next day.

The donor is protected over the whole horizon in the high scenario: on every day its ending stock
stays at or above ``min(donor_min_stock, ending under hold)``, and its extra lost units against
hold stay within ``donor_max_additional_lost``, also when hold already stocks out.

Ranking is transparent, never called optimal: drop candidates with a mandatory fail/unknown, then
keep a positive reduction of total unserved units (destination + donor) against hold in the base
scenario and no increase in any scenario; among those, more reduction, then less cost, then fewer
units. If that pick differs between scenarios, no move is recommended and the store is asked
to confirm the demand hypothesis that changes it. Otherwise exactly one informational option is
recommended, chosen by the first blocking check: product/size → ``ask_store``, stock →
``verify_stock``, lane, cost or policy → ``notify_owner``; no candidate → ``notify_owner``
(``ask_store`` when the case names no SKU-colour); no benefit → ``hold``. When blocked candidates
compete for display, a ``fail`` (final) ranks below an ``unknown`` (resolvable).

``act.options`` (bottom of this file) runs this for every open case of the run's stores, reading
cases, forecasts, ERP stock and master rows from the repo and lanes through ``SystemsReader``.
"""

import hashlib
import json
import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Literal, Protocol
from zoneinfo import ZoneInfo

import yaml

from tessera.core import repo
from tessera.core.config import get_settings
from tessera.core.contracts import (
    ActionOption,
    ArtifactRef,
    Case,
    Check,
    ForecastAdjustment,
    Leg,
    ModuleManifest,
    ModuleResult,
    Reservation,
    RunSpec,
    ScenarioOutcome,
    SourceRef,
    StockFact,
)
from tessera.modules.actions.simulation import Arrival, StockSimulation, simulate_stock
from tessera.modules.sources import erp
from tessera.modules.sources.systems_client import (
    ClientFactory,
    LaneEta,
    SystemsReader,
    Unknown,
    default_client,
)

SCENARIOS = ("low", "base", "high")
Status = Literal["pass", "fail", "unknown", "not_applicable"]
Kind = Literal["hold", "verify_stock", "ask_store", "notify_owner"]
LEDGER_HOLDS = frozenset({"pending", "committed"})

# Which informational option follows from the first blocking check of the transfer.
FOLLOW_UP: Mapping[str, Kind] = {
    "sku_identity": "ask_store",
    "size_curve": "ask_store",
    "assortment": "ask_store",
    "dest_stock": "verify_stock",
    "donor_stock": "verify_stock",
    "stock_freshness": "verify_stock",
    "dest_inbound": "verify_stock",
    "reservations": "verify_stock",
    "quality_hold": "verify_stock",
    "shared_resources": "verify_stock",
    "donor_availability": "verify_stock",
}


@dataclass(frozen=True)
class OptionsPolicy:
    """``policy.options`` of ``config/domain.yaml``; ``None`` = not declared = ``unknown``."""

    transfer_case_types: frozenset[str] | None = None
    max_units_per_transfer: int | None = None
    donor_min_stock: int | None = None
    donor_max_additional_lost: float | None = None
    max_transfer_cost_eur: float | None = None
    max_stock_age_days: int | None = None
    scarce_skus: frozenset[str] | None = None
    size_curve: Literal["uniform"] | None = None  # declared curve when no verified one exists
    store_stock_netted: bool | None = None  # declared: store on_hand is net of reservations/holds


@dataclass(frozen=True)
class SizeCurve:
    """Size shares of one location × SKU-colour: ``p_size >= 0`` summing to 1 (RFC §4.9)."""

    weights: Mapping[str, float]
    basis: str
    ref: ArtifactRef | None = None

    def __post_init__(self) -> None:
        if not self.weights or any(w < 0 or not math.isfinite(w) for w in self.weights.values()):
            raise ValueError("size curve needs finite non-negative weights")
        if abs(sum(self.weights.values()) - 1) > 1e-6:
            raise ValueError("size curve weights must sum to 1")


@dataclass(frozen=True)
class Position:
    """One store × SKU-colour as known at ``as_of``. Missing sizes in ``stock`` are unknown."""

    store_id: str
    country: str | None
    timezone: ZoneInfo
    forecast: ForecastAdjustment | None
    stock: Mapping[str, StockFact | Unknown]
    in_transit: Mapping[str, int | None]  # units in transit to it at the stock snapshot
    in_assortment: bool
    size_curve: SizeCurve | None = None


@dataclass(frozen=True)
class Route:
    donor: Position
    lane: LaneEta | Unknown


@dataclass(frozen=True)
class OptionInputs:
    case: Case
    run_id: str
    scenario_id: str
    as_of: datetime
    horizon: tuple[date, date]  # destination-local D+1..D+n
    sku: str | None  # SKU-colour of the case; None when its scope does not resolve one
    size: str | None  # the case's size when its scope is a SKU-size
    eans: Mapping[str, str | None]  # size → EAN from the master; sizes absent are not identified
    dest: Position
    routes: tuple[Route, ...]
    policy: OptionsPolicy
    reservations: tuple[Reservation, ...] = ()


@dataclass(frozen=True)
class _Candidate:
    donor: Position
    size: str
    leg: Leg
    checks: tuple[Check, ...]
    outcomes: tuple[ScenarioOutcome, ...] | None
    baseline: tuple[ScenarioOutcome, ...] | None
    reduction: Mapping[str, float] | None
    assumptions: tuple[str, ...] = field(default=())

    @property
    def blocking(self) -> tuple[Check, ...]:
        return tuple(c for c in self.checks if c.mandatory and c.status in ("fail", "unknown"))

    @property
    def beneficial(self) -> bool:
        return (
            self.reduction is not None
            and self.reduction["base"] > 0
            and all(v >= 0 for v in self.reduction.values())
        )


# Policy


def load_policy(config_dir: Path) -> OptionsPolicy:
    domain = yaml.safe_load((config_dir / "domain.yaml").read_text(encoding="utf-8"))
    return policy_from(domain.get("policy", {}).get("options") or {})


def policy_from(entries: Mapping[str, Any]) -> OptionsPolicy:
    def value(key: str) -> Any:
        entry = entries.get(key)
        return entry.get("value") if isinstance(entry, Mapping) else None

    def whole(key: str) -> int | None:
        v = value(key)
        return None if v is None else int(v)

    def real(key: str) -> float | None:
        v = value(key)
        return None if v is None else float(v)

    def names(key: str) -> frozenset[str] | None:
        v = value(key)
        return None if v is None else frozenset(str(x) for x in v)

    return OptionsPolicy(
        transfer_case_types=names("transfer_case_types"),
        max_units_per_transfer=whole("max_units_per_transfer"),
        donor_min_stock=whole("donor_min_stock"),
        donor_max_additional_lost=real("donor_max_additional_lost"),
        max_transfer_cost_eur=real("max_transfer_cost_eur"),
        max_stock_age_days=whole("max_stock_age_days"),
        scarce_skus=names("scarce_skus"),
        size_curve="uniform" if value("size_curve") == "uniform" else None,
        store_stock_netted=None
        if value("store_stock_netted") is None
        else bool(value("store_stock_netted")),
    )


# Pure service


def evaluate_options(inputs: OptionInputs) -> tuple[ActionOption, ...]:
    """All options of one case at ``inputs.as_of``. Pure: same inputs, same options."""
    digest = input_version_hash(inputs)
    days = _days(inputs.horizon)
    dest_demand = servable(inputs.dest.forecast, days)
    candidate, no_transfer, split = _transfer(inputs, days, dest_demand)

    recommended: Kind | Literal["transfer"] = "hold"
    verdict = ""
    if candidate is not None:
        recommended, verdict = _verdict(candidate, split)
    elif not _movable(inputs):
        recommended = "notify_owner"
    elif no_transfer:
        recommended = "ask_store" if inputs.sku is None else "notify_owner"

    hold = _hold_outcomes(inputs, days, dest_demand)
    blocking = candidate.blocking if candidate else ()
    options = [
        _informational(
            inputs, digest, "hold", hold, recommended, _hold_text(inputs, hold, verdict)
        ),
        _informational(
            inputs,
            digest,
            "verify_stock",
            None,
            recommended,
            _verify_text(inputs, blocking),
            checks=tuple(c for c in blocking if FOLLOW_UP.get(c.name) == "verify_stock"),
        ),
        _informational(
            inputs,
            digest,
            "ask_store",
            None,
            recommended,
            _ask_text(inputs, blocking),
            checks=tuple(c for c in blocking if FOLLOW_UP.get(c.name) == "ask_store"),
        ),
        _informational(
            inputs,
            digest,
            "notify_owner",
            None,
            recommended,
            _notify_text(inputs, verdict, no_transfer),
        ),
    ]
    if candidate is not None:
        options.append(_transfer_option(inputs, digest, candidate, recommended, verdict))
    return tuple(options)


def input_version_hash(inputs: OptionInputs) -> str:
    """SHA-256 over every input value the options depend on: changes when any fact changes."""

    def ref(record: Any) -> list[str] | None:
        return None if record is None else [type(record).__name__, record.id, record.version]

    def stock(value: StockFact | Unknown) -> Any:
        if isinstance(value, Unknown):
            return ["unknown", value.reason]
        return [*ref(value), value.qty, value.snapshot_at.isoformat()]

    def position(p: Position) -> Any:
        curve = p.size_curve
        return {
            "store": p.store_id,
            "forecast": ref(p.forecast),
            "stock": {s: stock(v) for s, v in sorted(p.stock.items())},
            "in_transit": dict(sorted(p.in_transit.items())),
            "assortment": p.in_assortment,
            "curve": None if curve is None else [sorted(curve.weights.items()), curve.basis],
        }

    def lane(value: LaneEta | Unknown) -> Any:
        if isinstance(value, Unknown):
            return ["unknown", value.reason]
        return [
            value.lane.lane_id,
            value.lane.last_reviewed.isoformat(),
            value.lane.source_ref.content_hash,
            value.eta.pickup_at.isoformat(),
            value.eta.eta_date.isoformat(),
        ]

    p = inputs.policy
    payload = {
        "case": ref(inputs.case),
        "as_of": inputs.as_of.isoformat(),
        "horizon": [d.isoformat() for d in inputs.horizon],
        "sku": inputs.sku,
        "size": inputs.size,
        "eans": dict(sorted(inputs.eans.items())),
        "dest": position(inputs.dest),
        "routes": [[position(r.donor), lane(r.lane)] for r in inputs.routes],
        "policy": {k: sorted(v) if isinstance(v, frozenset) else v for k, v in vars(p).items()},
        "ledger": sorted([*ref(r), r.status, r.qty] for r in inputs.reservations),
    }
    raw = json.dumps(payload, sort_keys=True, default=str).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def servable(
    forecast: ForecastAdjustment | None, days: Sequence[date]
) -> Mapping[str, tuple[float, ...]] | str:
    """Servable demand per scenario over ``days``, or why it is not available."""
    if forecast is None:
        return "no forecast at as_of"
    if forecast.status == "not_estimable":
        return f"forecast not_estimable ({forecast.reason})"
    points = {p.date: p for p in forecast.series}
    if any(d not in points or points[d].servable is None for d in days):
        return f"forecast {forecast.id} does not cover {days[0]}..{days[-1]}"
    return {s: tuple(getattr(points[d].servable, s) for d in days) for s in SCENARIOS}


def _days(horizon: tuple[date, date]) -> tuple[date, ...]:
    start, end = horizon
    return tuple(start + timedelta(days=i) for i in range((end - start).days + 1))


def _movable(inputs: OptionInputs) -> bool:
    types = inputs.policy.transfer_case_types
    return types is None or inputs.case.case_type in types


def _transfer(
    inputs: OptionInputs,
    days: Sequence[date],
    dest_demand: Mapping[str, tuple[float, ...]] | str,
) -> tuple[_Candidate | None, tuple[str, ...], str]:
    """The top transfer candidate, the reasons why there is none, and whether the pick changes
    between scenarios (empty if it does not)."""
    if not _movable(inputs):
        return None, (f"case type {inputs.case.case_type} does not lead to a stock move",), ""
    if inputs.sku is None:
        scope = inputs.case.scope_level
        return None, (f"case scope {scope} does not resolve one SKU-colour",), ""
    reasons = []
    candidates = []
    for route in inputs.routes:
        if isinstance(route.lane, Unknown):
            reasons.append(f"{route.donor.store_id}: lane unknown ({route.lane.reason})")
            continue
        empty = []
        for size in _sizes(inputs, route.donor):
            if _spare(inputs, route.donor, size) == 0:
                empty.append(size)
                continue
            candidates += _quantities(inputs, route.donor, route.lane, size, days, dest_demand)
        if empty:
            sizes = ", ".join(empty)
            reasons.append(f"{route.donor.store_id}: no unit of {inputs.sku} to give in {sizes}")
    if not candidates:
        if not inputs.routes:
            reasons.append("no domestic donor store in the run")
        return None, tuple(reasons), ""
    admissible = [c for c in candidates if not c.blocking and c.beneficial]
    split = ""
    if admissible:
        picks = {
            s: _label_move(min(admissible, key=lambda c, s=s: _rank_in(c, s))) for s in SCENARIOS
        }
        if len(set(picks.values())) > 1:
            split = ", ".join(f"{s}: {m}" for s, m in picks.items())
    return min(candidates, key=_rank), tuple(reasons), split


def _label_move(c: _Candidate) -> str:
    return f"{c.leg.qty} × size {c.size} from {c.donor.store_id}"


def _rank_in(c: _Candidate, scenario: str) -> tuple[Any, ...]:
    assert c.reduction is not None
    cost = c.leg.cost_eur if c.leg.cost_eur is not None else math.inf
    return (-c.reduction[scenario], cost, c.leg.qty, c.donor.store_id, c.size)


def _ledger(inputs: OptionInputs, donor: Position, size: str) -> list[Reservation]:
    return [
        r
        for r in inputs.reservations
        if r.location == donor.store_id and r.sku == inputs.sku and r.size == size
    ]


def _spare(inputs: OptionInputs, donor: Position, size: str) -> int | None:
    """Donor units of one size not held by the ledger, before any policy floor."""
    qty = _qty(donor.stock.get(size))
    if qty is None:
        return None
    held = sum(r.qty for r in _ledger(inputs, donor, size) if r.status in LEDGER_HOLDS)
    return max(0, math.floor(qty) - held)


def _sizes(inputs: OptionInputs, donor: Position) -> list[str]:
    """Sizes to evaluate: the case's size, else the curve's sizes, else one size to display."""
    if inputs.size is not None:
        return [inputs.size]
    curve = inputs.dest.size_curve
    if curve is not None:
        return sorted(s for s, w in curve.weights.items() if w > 0)
    known = sorted(set(inputs.dest.stock) | set(donor.stock))

    def shortfall(size: str) -> tuple[bool, float, float, str]:
        here, there = _qty(inputs.dest.stock.get(size)), _qty(donor.stock.get(size))
        return (not there, math.inf if here is None else here, -(there or 0), size)

    if not any(_qty(donor.stock.get(s)) for s in known):
        return known  # nothing anywhere: every size is reported as empty
    return [min(known, key=shortfall)]


def _rank(c: _Candidate) -> tuple[Any, ...]:
    """Admissible and beneficial first; then fewer fails (a fail is final, an unknown can be
    resolved), fewer unknowns, more reduction, less cost, fewer units."""
    reduction = c.reduction["base"] if c.reduction else 0.0
    cost = c.leg.cost_eur if c.leg.cost_eur is not None else math.inf
    fails = sum(x.status == "fail" for x in c.blocking)
    return (
        bool(c.blocking) or not c.beneficial,
        fails,
        len(c.blocking) - fails,
        -reduction,
        cost,
        c.leg.qty,
        c.donor.store_id,
        c.size,
    )


def _quantities(
    inputs: OptionInputs,
    donor: Position,
    lane: LaneEta,
    size: str,
    days: Sequence[date],
    dest_demand: Mapping[str, tuple[float, ...]] | str,
) -> list[_Candidate]:
    policy = inputs.policy
    sku = inputs.sku
    assert sku is not None
    dest_fact, donor_fact = inputs.dest.stock.get(size), donor.stock.get(size)
    dest_qty, donor_qty = _qty(dest_fact), _qty(donor_fact)
    ledger = _ledger(inputs, donor, size)
    reserved = sum(r.qty for r in ledger if r.status in LEDGER_HOLDS)
    floor = policy.donor_min_stock or 0
    available = None if donor_qty is None else math.floor(donor_qty) - reserved - floor
    cap = policy.max_units_per_transfer
    top = available if cap is None or available is None else min(available, cap)
    quantities = range(1, top + 1) if top is not None and top >= 1 else (1,)

    dest_curve, donor_curve = inputs.dest.size_curve, donor.size_curve
    donor_demand = servable(donor.forecast, days)
    shared = [
        _identity(inputs, size),
        _curve_check(inputs.dest, donor, size),
        _assortment(inputs, donor),
        _scarcity(policy, sku),
        _stock_check("dest_stock", inputs.dest.store_id, dest_fact),
        _stock_check("donor_stock", donor.store_id, donor_fact),
        _freshness(inputs, donor, size),
        _inbound(inputs.dest, size),
        _netting("reservations", donor_fact, "reservations_included", "reservations", policy),
        _netting("quality_hold", donor_fact, "quality_holds_included", "quality holds", policy),
        _shared_resources(ledger, reserved),
        _forecast_check("dest_forecast", inputs.dest, dest_demand),
        _forecast_check("donor_forecast", donor, donor_demand),
        *_lane_checks(inputs, donor, lane, days),
    ]

    quantified = (
        dest_curve is not None
        and donor_curve is not None
        and size in dest_curve.weights
        and size in donor_curve.weights
        and not isinstance(dest_demand, str)
        and not isinstance(donor_demand, str)
        and dest_qty is not None
        and donor_qty is not None
    )
    pickup_day = max(lane.eta.pickup_at.date(), days[0])
    arrival = Arrival(on=lane.eta.eta_date, qty=1, timing="closing")
    dest_series = donor_series = {}
    dest_start = donor_start = {}
    if quantified:
        assert dest_curve and donor_curve and dest_qty is not None and donor_qty is not None
        assert not isinstance(dest_demand, str) and not isinstance(donor_demand, str)
        dest_series = {s: _share(dest_demand[s], dest_curve.weights[size]) for s in SCENARIOS}
        donor_series = {s: _share(donor_demand[s], donor_curve.weights[size]) for s in SCENARIOS}
        gap = _gap_days(donor_fact, donor, days[0]) or 0
        dest_start = {s: math.floor(dest_qty) for s in SCENARIOS}
        donor_start = {
            s: max(
                0,
                math.floor(
                    donor_qty - reserved - gap * sum(donor_series[s]) / len(donor_series[s])
                ),
            )
            for s in SCENARIOS
        }
    hold = (
        {
            s: (
                simulate_stock(dest_start[s], days[0], dest_series[s]),
                simulate_stock(donor_start[s], days[0], donor_series[s]),
            )
            for s in SCENARIOS
        }
        if quantified
        else None
    )

    out = []
    for q in quantities:
        leg = _leg(inputs, donor, lane, size, q)
        checks = list(shared)
        checks.append(_quantity_check(policy, q, available, reserved, floor))
        checks.append(_cost_check(policy, leg.cost_eur))
        outcomes = baseline = reduction = None
        if hold is not None:
            arrivals = (Arrival(arrival.on, q, arrival.timing),)
            outbound = {pickup_day: q} if pickup_day <= days[-1] else {}
            moved = {
                s: (
                    simulate_stock(dest_start[s], days[0], dest_series[s], arrivals),
                    simulate_stock(donor_start[s], days[0], donor_series[s], outbound=outbound),
                )
                for s in SCENARIOS
            }
            feasible = all(sim.feasible for pair in moved.values() for sim in pair)
            checks.append(_availability(feasible, q, donor.store_id))
            checks.append(_protection(policy, hold["high"][1], moved["high"][1], feasible))
            if feasible:
                outcomes = _outcomes(moved, leg.cost_eur, inputs, size, donor)
                baseline = _outcomes(hold, None, inputs, size, donor)
                reduction = {
                    s: (hold[s][0].lost + hold[s][1].lost) - (moved[s][0].lost + moved[s][1].lost)
                    for s in SCENARIOS
                }
        else:
            checks.append(
                _check(
                    "donor_availability",
                    "unknown" if top is None else "pass" if top >= q else "fail",
                    "donor stock unknown"
                    if top is None
                    else f"{max(top, 0)} unit(s) movable at {donor.store_id} after reservations "
                    "and the donor floor; trajectory not simulated (demand per size unknown)",
                )
            )
            checks.append(
                _check(
                    "donor_protection",
                    "unknown",
                    "high-scenario trajectory of the donor not computable: "
                    "size_demand_unknown or forecast/stock missing",
                )
            )
        out.append(
            _Candidate(
                donor=donor,
                size=size,
                leg=leg,
                checks=tuple(_ordered(checks)),
                outcomes=outcomes,
                baseline=baseline,
                reduction=reduction,
                assumptions=_transfer_assumptions(quantified, lane),
            )
        )
    return out


def _ordered(checks: Iterable[Check]) -> list[Check]:
    order = list(FOLLOW_UP)
    return sorted(checks, key=lambda c: order.index(c.name) if c.name in order else len(order))


def _share(series: Sequence[float], weight: float) -> tuple[float, ...]:
    return tuple(weight * x for x in series)


def _qty(value: StockFact | Unknown | None) -> float | None:
    return value.qty if isinstance(value, StockFact) else None


def _gap_days(fact: StockFact | Unknown | None, where: Position, start: date) -> int | None:
    """Days between the stock snapshot and the horizon start, not covered by any fact."""
    if not isinstance(fact, StockFact):
        return None
    return (start - fact.snapshot_at.astimezone(where.timezone).date()).days - 1


def _leg(inputs: OptionInputs, donor: Position, lane: LaneEta, size: str, q: int) -> Leg:
    tz = inputs.dest.timezone
    eta_at = datetime.combine(lane.eta.eta_date, time(23, 59, 59), tz)
    sellable_at = datetime.combine(lane.eta.eta_date + timedelta(days=1), time(0, 0), tz)
    fixed, per_unit = lane.lane.cost_fixed_eur, lane.lane.cost_per_unit_eur
    cost = None if fixed is None or per_unit is None else round(fixed + per_unit * q, 2)
    assert inputs.sku is not None
    return Leg(
        origin=donor.store_id,
        dest=inputs.dest.store_id,
        sku=inputs.sku,
        size=size,
        ean=inputs.eans.get(size),
        qty=q,
        pickup_at=lane.eta.pickup_at,
        eta_at=max(eta_at, lane.eta.pickup_at),
        sellable_at=max(sellable_at, lane.eta.pickup_at),
        lane_id=lane.lane.lane_id,
        cost_eur=cost,
    )


def _outcomes(
    sims: Mapping[str, tuple[StockSimulation, StockSimulation]],
    cost: float | None,
    inputs: OptionInputs,
    size: str,
    donor: Position,
) -> tuple[ScenarioOutcome, ...]:
    dest_curve, donor_curve = inputs.dest.size_curve, donor.size_curve
    assert dest_curve is not None and donor_curve is not None
    return tuple(
        ScenarioOutcome(
            scenario_id=s,
            lost_units_dest=dest.lost,
            lost_units_donor=don.lost,
            leftover_units_dest=dest.ending,
            leftover_units_donor=don.ending,
            transport_cost_eur=cost,
            demand_basis=(
                f"servable {s} of {_label(inputs.dest.forecast)} and {_label(donor.forecast)}, "
                f"size {size}"
            ),
            size_allocation_basis=(
                f"{inputs.dest.store_id} p={dest_curve.weights[size]:.3f} ({dest_curve.basis}); "
                f"{donor.store_id} p={donor_curve.weights[size]:.3f} ({donor_curve.basis})"
            ),
        )
        for s, (dest, don) in sims.items()
    )


def _label(forecast: ForecastAdjustment | None) -> str:
    return "no forecast" if forecast is None else f"{forecast.id}@{forecast.version}"


def _hold_outcomes(
    inputs: OptionInputs,
    days: Sequence[date],
    dest_demand: Mapping[str, tuple[float, ...]] | str,
) -> tuple[ScenarioOutcome, ...] | None:
    """Destination lost units over the curve's sizes if nothing is done; None if not computable."""
    curve = inputs.dest.size_curve
    if curve is None or isinstance(dest_demand, str):
        return None
    sizes = [s for s, w in curve.weights.items() if w > 0]
    stock = {s: _qty(inputs.dest.stock.get(s)) for s in sizes}
    if any(q is None for q in stock.values()):
        return None
    out = []
    for s in SCENARIOS:
        sims = [
            simulate_stock(
                math.floor(stock[size] or 0), days[0], _share(dest_demand[s], curve.weights[size])
            )
            for size in sizes
        ]
        out.append(
            ScenarioOutcome(
                scenario_id=s,
                lost_units_dest=sum(sim.lost for sim in sims),
                lost_units_donor=None,
                leftover_units_dest=sum(sim.ending for sim in sims),
                leftover_units_donor=None,
                transport_cost_eur=0.0,
                demand_basis=f"servable {s} of {_label(inputs.dest.forecast)}",
                size_allocation_basis=f"{inputs.dest.store_id} sizes {','.join(sorted(sizes))} "
                f"({curve.basis})",
            )
        )
    return tuple(out)


# Checks


def _check(name: str, status: Status, detail: str, refs: Iterable[ArtifactRef] = ()) -> Check:
    return Check(name=name, status=status, mandatory=True, detail=detail, source_refs=tuple(refs))


def _fact_refs(*facts: StockFact | Unknown | None) -> list[ArtifactRef]:
    return [
        ArtifactRef(kind="StockFact", id=f.id, version=f.version)
        for f in facts
        if isinstance(f, StockFact)
    ]


def _identity(inputs: OptionInputs, size: str) -> Check:
    if size not in inputs.eans:
        return _check("sku_identity", "fail", f"{inputs.sku} has no size {size} in the master")
    if not inputs.eans[size]:
        return _check("sku_identity", "unknown", f"{inputs.sku}-{size}: no EAN in the master")
    return _check("sku_identity", "pass", f"{inputs.sku}-{size} EAN {inputs.eans[size]}")


def _curve_check(dest: Position, donor: Position, size: str) -> Check:
    missing = [p.store_id for p in (dest, donor) if p.size_curve is None]
    if missing:
        return _check(
            "size_curve",
            "unknown",
            f"size_demand_unknown at {', '.join(missing)}: no verified size curve, "
            "no lost units per size and no numeric move",
        )
    absent = [
        p.store_id for p in (dest, donor) if p.size_curve and size not in p.size_curve.weights
    ]
    if absent:
        return _check("size_curve", "fail", f"size {size} not in the curve of {', '.join(absent)}")
    assert dest.size_curve and donor.size_curve
    refs = [c.ref for c in (dest.size_curve, donor.size_curve) if c.ref is not None]
    return _check(
        "size_curve",
        "pass",
        f"{dest.store_id}: {dest.size_curve.basis}; {donor.store_id}: {donor.size_curve.basis}",
        refs,
    )


def _assortment(inputs: OptionInputs, donor: Position) -> Check:
    off = [p.store_id for p in (inputs.dest, donor) if not p.in_assortment]
    if off:
        return _check("assortment", "fail", f"{inputs.sku} not in the assortment of {off}")
    return _check("assortment", "pass", f"{inputs.sku} in both assortments")


def _scarcity(policy: OptionsPolicy, sku: str) -> Check:
    if policy.scarce_skus is None:
        return _check("scarcity_policy", "unknown", "no scarcity/allocation policy declared")
    if sku in policy.scarce_skus:
        return _check("scarcity_policy", "fail", f"{sku} is under strategic scarcity allocation")
    return _check("scarcity_policy", "pass", f"{sku} not in the declared scarcity list")


def _stock_check(name: str, store: str, fact: StockFact | Unknown | None) -> Check:
    if not isinstance(fact, StockFact) or fact.qty is None:
        reason = fact.reason if isinstance(fact, Unknown) else "no stock record"
        return _check(name, "unknown", f"{store}: stock unknown ({reason}), never read as zero")
    return _check(
        name,
        "pass",
        f"{store}: {fact.qty:g} {fact.basis} at {fact.snapshot_at.isoformat()}",
        _fact_refs(fact),
    )


def _freshness(inputs: OptionInputs, donor: Position, size: str) -> Check:
    limit = inputs.policy.max_stock_age_days
    gaps = {
        p.store_id: _gap_days(p.stock.get(size), p, inputs.horizon[0]) for p in (inputs.dest, donor)
    }
    if any(g is None for g in gaps.values()):
        return _check("stock_freshness", "unknown", "a snapshot is missing")
    detail = ", ".join(f"{s}: {g} day(s) between snapshot and horizon" for s, g in gaps.items())
    if limit is None:
        return _check("stock_freshness", "unknown", f"no max_stock_age_days policy; {detail}")
    stale = any(g is not None and g > limit for g in gaps.values())
    return _check("stock_freshness", "fail" if stale else "pass", f"{detail} (max {limit})")


def _inbound(dest: Position, size: str) -> Check:
    units = dest.in_transit.get(size)
    if units is None:
        return _check("dest_inbound", "unknown", f"{dest.store_id}: units in transit unknown")
    if units > 0:
        return _check(
            "dest_inbound",
            "unknown",
            f"{dest.store_id}: {units} unit(s) in transit with unknown arrival day",
        )
    return _check("dest_inbound", "pass", f"{dest.store_id}: nothing in transit at the snapshot")


def _netting(
    name: str, fact: StockFact | Unknown | None, attr: str, what: str, policy: OptionsPolicy
) -> Check:
    if not isinstance(fact, StockFact):
        return _check(name, "unknown", "donor stock unknown")
    included = getattr(fact, attr)
    if included is False:
        return _check(name, "pass", f"{fact.basis} is net of {what}", _fact_refs(fact))
    if included is None and fact.basis == "on_hand" and policy.store_stock_netted:
        return _check(
            name,
            "pass",
            f"{fact.location_id} on_hand taken as net of {what} (declared policy)",
            _fact_refs(fact),
        )
    state = "not stated by the source" if included is None else "included, amount unknown"
    return _check(
        name, "unknown", f"{fact.location_id} {fact.basis}: {what} {state}", _fact_refs(fact)
    )


def _shared_resources(ledger: Sequence[Reservation], reserved: int) -> Check:
    refs = [ArtifactRef(kind="Reservation", id=r.id, version=r.version) for r in ledger]
    if any(r.status == "unknown" for r in ledger):
        return _check(
            "shared_resources", "unknown", "a ledger reservation has unknown status", refs
        )
    return _check(
        "shared_resources", "pass", f"{reserved} unit(s) held by approved decisions", refs
    )


def _forecast_check(name: str, where: Position, demand: Mapping[str, Any] | str) -> Check:
    refs = [] if where.forecast is None else [_ref(where.forecast)]
    if isinstance(demand, str):
        return _check(name, "unknown", f"{where.store_id}: {demand}", refs)
    return _check(name, "pass", f"{where.store_id}: {_label(where.forecast)}", refs)


def _lane_checks(
    inputs: OptionInputs, donor: Position, lane: LaneEta, days: Sequence[date]
) -> list[Check]:
    ln, eta = lane.lane, lane.eta
    ref = ArtifactRef(kind="Lane", id=ln.lane_id, version=ln.last_reviewed.isoformat())
    ibt: Status = "unknown" if ln.ibt_allowed is None else "pass" if ln.ibt_allowed else "fail"
    domestic = donor.country is not None and donor.country == inputs.dest.country
    border: Status = (
        "fail"
        if not domestic or ln.customs_required
        else "unknown"
        if ln.customs_required is None
        else "pass"
    )
    sellable = eta.eta_date + timedelta(days=1)
    p90 = "" if eta.eta_p90_date is None else f", P90 {eta.eta_p90_date}"
    cutoff = " (cut-off missed: next pickup)" if eta.missed_cutoff else ""
    return [
        _check("lane", "pass", f"{ln.lane_id} {ln.mode}, reviewed {ln.last_reviewed}", [ref]),
        _check("ibt_allowed", ibt, f"{ln.lane_id}: ibt_allowed={ln.ibt_note or ln.ibt_allowed}"),
        _check(
            "domestic",
            border,
            f"{donor.store_id} ({donor.country}) → {inputs.dest.store_id} "
            f"({inputs.dest.country}), customs_required={ln.customs_required}; "
            "cross-border excluded in the MVP",
        ),
        _check(
            "pickup_calendar",
            "pass",
            f"pickup {eta.pickup_at.isoformat()}{cutoff}, ETA {eta.eta_date}{p90} ({eta.basis})",
        ),
        _check(
            "eta_in_time",
            "pass" if sellable <= days[-1] else "fail",
            f"sellable from {sellable}, horizon ends {days[-1]}",
        ),
    ]


def _quantity_check(
    policy: OptionsPolicy, q: int, available: int | None, reserved: int, floor: int
) -> Check:
    cap = policy.max_units_per_transfer
    bound = f"{max(available or 0, 0)} movable after {reserved} reserved and floor {floor}"
    if available is None:
        bound = "donor stock unknown"
    if cap is None or policy.donor_min_stock is None:
        return _check("quantity_policy", "unknown", f"q={q}: q_max policy not declared; {bound}")
    return _check(
        "quantity_policy", "pass" if q <= cap else "fail", f"q={q} within 1..{cap}; {bound}"
    )


def _cost_check(policy: OptionsPolicy, cost: float | None) -> Check:
    ceiling = policy.max_transfer_cost_eur
    if cost is None:
        return _check("transport_cost", "unknown", "lane cost unknown: human choice")
    if ceiling is None:
        return _check("transport_cost", "unknown", f"{cost:.2f} EUR, no cost ceiling declared")
    status: Status = "pass" if cost <= ceiling else "fail"
    return _check("transport_cost", status, f"{cost:.2f} EUR, ceiling {ceiling:.2f} EUR")


def _availability(feasible: bool, q: int, store: str) -> Check:
    if feasible:
        return _check("donor_availability", "pass", f"{q} unit(s) available at {store} on pickup")
    return _check(
        "donor_availability",
        "fail",
        f"{q} unit(s) exceed what {store} still holds on the pickup day in some scenario",
    )


def _protection(
    policy: OptionsPolicy, hold: StockSimulation, moved: StockSimulation, feasible: bool
) -> Check:
    floor, extra = policy.donor_min_stock, policy.donor_max_additional_lost
    if floor is None or extra is None:
        return _check("donor_protection", "unknown", "donor floor/extra-loss policy not declared")
    if not feasible:
        return _check("donor_protection", "fail", "move not feasible for the donor")
    added = moved.lost - hold.lost
    below = [
        m.day.isoformat()
        for h, m in zip(hold.days, moved.days, strict=True)
        if m.ending < min(floor, h.ending) - 1e-9
    ]
    ok = not below and added <= extra + 1e-9
    detail = (
        f"high scenario: extra donor lost {added:.2f} (max {extra:g}), "
        f"floor {floor} kept on every day"
        if not below
        else f"high scenario: donor below floor {floor} on {', '.join(below)}"
    )
    return _check("donor_protection", "pass" if ok else "fail", detail)


def _ref(record: Any) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


# Options


def _verdict(c: _Candidate, split: str) -> tuple[Kind | Literal["transfer"], str]:
    if c.blocking:
        first = c.blocking[0]
        return FOLLOW_UP.get(first.name, "notify_owner"), (
            f"transfer blocked by {', '.join(x.name for x in c.blocking)}"
        )
    if not c.beneficial:
        return "hold", "the move does not reduce total unserved units against hold"
    if split:
        return "ask_store", (
            f"the move to choose changes between scenarios ({split}): verify the demand "
            "hypothesis behind the scenarios first"
        )
    return "transfer", ""


def _common(inputs: OptionInputs, kind: str, digest: str) -> dict[str, Any]:
    case = inputs.case
    facts = [
        f
        for p in (inputs.dest, *(r.donor for r in inputs.routes))
        for f in p.stock.values()
        if isinstance(f, StockFact)
    ]
    forecasts = [
        p.forecast
        for p in (inputs.dest, *(r.donor for r in inputs.routes))
        if p.forecast is not None
    ]
    records: list[Any] = [case, *forecasts, *facts]
    available = [r.available_at for r in records if r.available_at is not None] or [None]
    lanes = [r.lane.lane.source_ref for r in inputs.routes if isinstance(r.lane, LaneEta)]
    sources: list[SourceRef] = list(case.source_refs)
    sources += [f.source_ref for f in facts] + lanes
    return {
        "id": f"opt-{case.id}-{kind}",
        "version": digest.removeprefix("sha256:")[:16],
        "available_at": max(available),
        "availability_basis": "max(input available_at)",
        "source_refs": tuple(dict.fromkeys(sources)),
        "run_id": inputs.run_id,
        "scenario_id": inputs.scenario_id,
        "computed_at": inputs.as_of,
        "input_refs": tuple(dict.fromkeys(_ref(r) for r in records)),
        "producer": MANIFEST.id,
        "producer_version": MANIFEST.version,
        "case_id": case.id,
        "forecast_ref": None if inputs.dest.forecast is None else _ref(inputs.dest.forecast),
        "input_version_hash": digest,
    }


def _valid_until(inputs: OptionInputs) -> datetime:
    return datetime.combine(inputs.horizon[1] + timedelta(days=1), time(0), inputs.dest.timezone)


def _informational(
    inputs: OptionInputs,
    digest: str,
    kind: Kind,
    outcomes: tuple[ScenarioOutcome, ...] | None,
    recommended: str,
    rationale: str,
    checks: tuple[Check, ...] = (),
) -> ActionOption:
    return ActionOption(
        **_common(inputs, kind, digest),
        kind=kind,
        legs=(),
        checks=checks,
        outcomes=outcomes,
        baseline_outcomes=None,
        assumptions=_assumptions(inputs),
        valid_until=_valid_until(inputs),
        recommended=recommended == kind,
        rationale=rationale,
    )


def _transfer_option(
    inputs: OptionInputs, digest: str, c: _Candidate, recommended: str, verdict: str
) -> ActionOption:
    leg = c.leg
    if c.reduction is not None:
        gains = ", ".join(f"{s} {c.reduction[s]:.2f}" for s in SCENARIOS)
        effect = f"Unserved units avoided against hold (dest + donor): {gains}."
    else:
        effect = "Not quantified: no lost units per size without a verified size curve."
    rationale = (
        f"Move {leg.qty} × {leg.sku}-{leg.size} {leg.origin} → {leg.dest} on {leg.lane_id}, "
        f"sellable {leg.sellable_at.date()}. {effect}"
        + (f" Not recommended: {verdict}." if verdict else "")
    )
    return ActionOption(
        **_common(inputs, "transfer", digest),
        kind="transfer",
        legs=(leg,),
        checks=c.checks,
        outcomes=c.outcomes,
        baseline_outcomes=c.baseline,
        assumptions=(*_assumptions(inputs), *c.assumptions),
        valid_until=min(leg.pickup_at, _valid_until(inputs)),
        recommended=recommended == "transfer",
        rationale=rationale,
    )


def _assumptions(inputs: OptionInputs) -> tuple[str, ...]:
    return (
        "Options are alternatives: none reserves stock until approved.",
        "Scenarios are servable demand low/base/high, not probabilities or confidence bands.",
        f"Horizon {inputs.horizon[0]}..{inputs.horizon[1]} in {inputs.dest.store_id} local days.",
    )


def _transfer_assumptions(quantified: bool, lane: LaneEta) -> tuple[str, ...]:
    out = [
        "Domestic store-to-store only: cross-border and DC sources are out of the MVP.",
        f"ETA is the contract date ({lane.eta.basis}); units arrive at closing and are sellable "
        "the next day. Outbound leaves the donor before that day's sales.",
    ]
    if quantified:
        out += [
            "Destination starts from its last snapshot with no consumption before the horizon.",
            "Donor starts from its snapshot minus ledger reservations minus the scenario's mean "
            "daily demand for each day before the horizon, floored to whole units.",
            "Lost sales are not backlog.",
        ]
    else:
        out.append("Quantity shown is the smallest move; it is not sized against demand.")
    return tuple(out)


def _hold_text(inputs: OptionInputs, hold: tuple[ScenarioOutcome, ...] | None, verdict: str) -> str:
    if hold is None:
        effect = "Lost units at the destination not quantified (size curve or forecast missing)."
    else:
        lost = ", ".join(f"{o.scenario_id} {o.lost_units_dest:.2f}" for o in hold)
        effect = f"Destination lost units if nothing is done: {lost}."
    return f"Keep stock as it is at {inputs.dest.store_id}. {effect}" + (
        f" {verdict[0].upper()}{verdict[1:]}." if verdict else ""
    )


def _stock_line(inputs: OptionInputs) -> str:
    def cell(p: Position, size: str) -> str:
        qty = _qty(p.stock[size])
        return f"{size}=?" if qty is None else f"{size}={qty:g}"

    def show(p: Position) -> str:
        cells = " ".join(cell(p, s) for s in sorted(p.stock))
        return f"{p.store_id} [{cells or 'no data'}]"

    return "; ".join(show(p) for p in (inputs.dest, *(r.donor for r in inputs.routes)))


def _verify_text(inputs: OptionInputs, blocking: Sequence[Check]) -> str:
    stock = [c for c in blocking if FOLLOW_UP.get(c.name) == "verify_stock"]
    what = "; ".join(c.detail for c in stock) or "confirm on-hand and reservations"
    return f"Verify stock of {inputs.sku or inputs.case.scope_id or 'the product'}: {what}."


def _ask_text(inputs: OptionInputs, blocking: Sequence[Check]) -> str:
    product = [c.detail for c in blocking if FOLLOW_UP.get(c.name) == "ask_store"]
    if inputs.sku is None:
        product.append(f"which product (scope {inputs.case.scope_level})")
    what = "; ".join(product) or "the sizes and quantities asked by customers"
    stock = f" Stock per size: {_stock_line(inputs)}." if inputs.sku else ""
    return f"Ask {inputs.dest.store_id} to confirm {what}.{stock}"


def _notify_text(inputs: OptionInputs, verdict: str, no_transfer: Sequence[str]) -> str:
    why = verdict or "; ".join(no_transfer) or "for information"
    return f"Notify {inputs.case.owner} about case {inputs.case.id}: {why}."


# Module

MANIFEST = ModuleManifest(
    id="act.options",
    version="1",
    layer="actions",
    description=(
        "Hold / verify_stock / ask_store / notify_owner and one domestic store transfer per open "
        "case, with every RFC §4.10 check; no size curve blocks the move"
    ),
    requires=("src.erp", "fc.baseline"),
    optional_inputs=("int.cases", "fc.overlay", "sys.client"),
    produces=("ActionOption",),
    enabled=True,
    mode="live",
    params_schema={"type": "object", "properties": {}, "additionalProperties": False},
)

CLOSED_CASES = frozenset({"decided", "closed"})


class Context(Protocol):
    """The part of PLT-04's ``RunContext`` this module uses."""

    @property
    def spec(self) -> RunSpec: ...

    @property
    def repo(self) -> repo.Repo: ...

    @property
    def params(self) -> Mapping[str, Any]: ...

    @property
    def clients(self) -> Mapping[str, Any]: ...


class Reader(Protocol):
    """``SystemsReader``'s read side: stock per location and lane/ETA at ``as_of``."""

    def stock(
        self, sku: str, size: str, locations: Iterable[str]
    ) -> Mapping[str, tuple[StockFact, ...] | Unknown]: ...

    def lane_and_eta(
        self,
        origin: str,
        dest: str,
        requested_at: datetime,
        required_by: datetime | None = None,
    ) -> LaneEta | Unknown: ...


def case_product(case: Case) -> tuple[str | None, str | None]:
    """SKU-colour and size of a case's scope; ``(None, None)`` above SKU-colour."""
    if case.scope_level == "sku" and case.scope_id:
        return case.scope_id, None
    if case.scope_level == "sku_size" and case.scope_id:
        style, colour, *size = case.scope_id.split("-")
        return f"{style}-{colour}", "-".join(size) or None
    return None, None


def case_forecast(run_repo: repo.Repo, store_id: str, sku: str, case_id: str | None):
    """The case's own adjustment if any, else the store × SKU baseline."""
    found = run_repo.list(ForecastAdjustment, store_id=store_id, sku=sku)
    own = [f for f in found if case_id is not None and case_id in f.case_ids]
    base = [f for f in found if not f.case_ids]
    return (own or base or [None])[-1]


def gather(
    run_repo: repo.Repo,
    reader: Reader,
    case: Case,
    policy: OptionsPolicy,
    horizon_days: int,
    size_curves: Mapping[str, SizeCurve] | None = None,
) -> OptionInputs:
    """Everything ``evaluate_options`` needs for one case, read at the run's ``as_of``."""
    spec = run_repo.spec
    stores = {str(r.data["store_id"]): r.data for r in erp.read(run_repo, "stores")}
    dest_id = case.store_id or ""
    tz = ZoneInfo(str(stores[dest_id]["timezone"]))
    start = spec.as_of.astimezone(tz).date() + timedelta(days=1)
    horizon = (start, start + timedelta(days=horizon_days - 1))
    sku, size = case_product(case)
    curves = dict(size_curves or {})

    eans: dict[str, str | None] = {}
    if sku is not None:
        for row in erp.read(run_repo, "sku_size_ean", sku=sku):
            eans[str(row.data["size"])] = str(row.data.get("ean") or "") or None

    def curve(store: str) -> SizeCurve | None:
        if store in curves:
            return curves[store]
        if policy.size_curve == "uniform" and eans:
            share = 1 / len(eans)
            basis = f"declared policy: uniform over {len(eans)} master sizes"
            return SizeCurve({s: share for s in eans}, basis)
        return None

    def position(store: str) -> Position:
        data = stores[store]
        assert sku is not None
        sizes = sorted(eans)
        stock: dict[str, StockFact | Unknown] = {}
        for s in sizes:
            got = reader.stock(sku, s, [store])[store]
            stock[s] = got if isinstance(got, Unknown) else _sellable_first(got)
        return Position(
            store_id=store,
            country=data.get("country_code"),
            timezone=ZoneInfo(str(data["timezone"])),
            forecast=case_forecast(run_repo, store, sku, case.id if store == dest_id else None),
            stock=stock,
            in_transit=_in_transit(run_repo, store, sku, sizes),
            in_assortment=any(
                str(r.data["sku"]) == sku for r in erp.read(run_repo, "assortment", store_id=store)
            ),
            size_curve=curve(store),
        )

    if sku is None:
        dest = Position(dest_id, stores[dest_id].get("country_code"), tz, None, {}, {}, False, None)
        routes: tuple[Route, ...] = ()
    else:
        dest = position(dest_id)
        routes = tuple(
            Route(position(store), reader.lane_and_eta(store, dest_id, spec.as_of))
            for store in spec.stores
            if store != dest_id
            and store in stores
            and stores[store].get("country_code") == dest.country  # cross-border: not in the MVP
        )

    reservations = tuple(r for r in run_repo.list(Reservation) if sku is None or r.sku == sku)
    return OptionInputs(
        case=case,
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        as_of=spec.as_of,
        horizon=horizon,
        sku=sku,
        size=size,
        eans=eans,
        dest=dest,
        routes=routes,
        policy=policy,
        reservations=reservations,
    )


def _sellable_first(facts: Sequence[StockFact]) -> StockFact | Unknown:
    """Prefer ATP, then sellable, then physical on-hand."""
    for basis in ("atp", "sellable", "on_hand"):
        for f in facts:
            if f.basis == basis:
                return f
    return Unknown("not_loaded", "no stock fact")


def _in_transit(
    run_repo: repo.Repo, store: str, sku: str, sizes: Iterable[str]
) -> dict[str, int | None]:
    latest: dict[str, tuple[date, Any]] = {}
    for row in run_repo.erp("stock", store_id=store, sku=sku):
        size, day = str(row.data["size"]), row.data["snapshot_date"]
        if size not in latest or day > latest[size][0]:
            latest[size] = (day, row.data.get("in_transit"))
    return {s: (None if s not in latest else latest[s][1]) for s in sizes}


def build_options(
    run_repo: repo.Repo,
    reader: Reader,
    policy: OptionsPolicy,
    horizon_days: int,
    size_curves: Mapping[str, SizeCurve] | None = None,
) -> ModuleResult:
    spec = run_repo.spec
    options: list[ActionOption] = []
    abstentions: list[str] = []
    cases = [
        c for c in run_repo.list(Case) if c.status not in CLOSED_CASES and c.store_id in spec.stores
    ]
    for case in cases:
        try:
            inputs = gather(run_repo, reader, case, policy, horizon_days, size_curves)
        except KeyError as e:
            abstentions.append(f"{case.id}: master data missing at as_of ({e})")
            continue
        options += evaluate_options(inputs)
    new = run_repo.put(*options) if options else 0
    transfers = [o for o in options if o.kind == "transfer"]
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if abstentions else "succeeded",
        counts={
            "cases": len(cases),
            "options": len(options),
            "transfers": len(transfers),
            "transfers_recommended": sum(o.recommended for o in transfers),
            "new": new,
        },
        errors=(),
        abstentions=tuple(abstentions),
    )


def run(ctx: Context) -> ModuleResult:
    settings = get_settings()
    factory: ClientFactory = ctx.clients.get("systems", default_client)
    reader = SystemsReader.open(ctx.repo, factory)
    if isinstance(reader, Unknown):
        return ModuleResult(
            module_id=MANIFEST.id,
            module_version=MANIFEST.version,
            status="blocked",
            counts={},
            errors=(f"systems reader: {reader.reason} {reader.detail}".strip(),),
            abstentions=(),
        )
    domain = yaml.safe_load((settings.config_dir / "domain.yaml").read_text(encoding="utf-8"))
    horizon = int(domain["policy"]["horizon"]["days"]["value"])
    try:
        return build_options(ctx.repo, reader, load_policy(settings.config_dir), horizon)
    finally:
        reader.client.close()
