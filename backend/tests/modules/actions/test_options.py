"""ACT-02: `evaluate_options()` on hand-built inputs, and `act.options` on a synthetic repo.

Case: the DATA-01b MAIRE black fixture (MIL01, unmet demand). Run evening: Wed 2026-10-14 20:00 in
Milan, horizon Thu 15 → Wed 21. Stock snapshots are end of Tue 13 (one day before the horizon).
Lane MIL02 → MIL01: pickup Mon-Fri 12:00, one transit day, so Thu 15 pickup, ETA Fri 16, sellable
Sat 17.
"""

import csv
import json
from dataclasses import replace
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import httpx
import pytest

from tessera.core.contracts import (
    ActionOption,
    AdjustmentComponent,
    ArtifactRef,
    Case,
    ForecastAdjustment,
    ForecastPoint,
    ModuleManifest,
    ModuleSnapshot,
    Reservation,
    RunSpec,
    ScenarioValues,
    SourceRef,
    StockFact,
)
from tessera.core.db import connect
from tessera.core.repo import Repo, create_run
from tessera.modules.actions import options
from tessera.modules.actions.options import (
    OptionInputs,
    OptionsPolicy,
    Position,
    Route,
    SizeCurve,
    evaluate_options,
    input_version_hash,
)
from tessera.modules.intelligence import baseline
from tessera.modules.sources import erp
from tessera.modules.sources.systems_client import (
    Crosswalk,
    Lane,
    LaneEta,
    SystemsClient,
    SystemsReader,
    Unknown,
    eta,
)

ROOT = Path(__file__).resolve().parents[4]
CASE_FILE = ROOT / "data/fixtures/cases/case-mil01-j20931a00012-999-20261002.json"
ROME = ZoneInfo("Europe/Rome")
AS_OF = datetime(2026, 10, 14, 18, tzinfo=UTC)
HORIZON = (date(2026, 10, 15), date(2026, 10, 21))
SKU = "J20931A00012-999"
SIZES = ("00", "0", "1", "2", "3", "4")
CURVE = SizeCurve(
    {"00": 0.1, "0": 0.2, "1": 0.3, "2": 0.2, "3": 0.1, "4": 0.1}, "declared test policy"
)
REF = SourceRef(uri="test://stock", content_hash="sha256:test")
POLICY = replace(
    options.load_policy(ROOT / "config"), scarce_skus=frozenset()
)  # allocation declares no scarce SKU in these tests


def fixture_case(**update) -> Case:
    payload = json.loads(CASE_FILE.read_text())[0]["payload"]
    return Case.model_validate(payload).model_copy(update=update)


def forecast(store: str, daily, scenarios=None) -> ForecastAdjustment:
    days = [HORIZON[0] + timedelta(days=i) for i in range(7)]
    series = []
    for i, day in enumerate(days):
        low, base, high = scenarios[i] if scenarios else (daily, daily, daily)
        latent = ScenarioValues(low=low, base=base, high=high)
        series.append(ForecastPoint(date=day, baseline=daily, latent=latent, servable=latent))
    component = AdjustmentComponent(
        type="incremental",
        episode_refs=(),
        evidence_refs=(),
        params={},
        unit="units",
        effective_from=AS_OF,
        effective_until=AS_OF + timedelta(days=7),
        reference_time=AS_OF,
        formula_version="test",
        explanation="test overlay",
    )
    return ForecastAdjustment(
        id=f"fc-{store.lower()}",
        version="v1",
        available_at=AS_OF - timedelta(days=2),
        availability_basis="test",
        source_refs=(),
        run_id="run",
        scenario_id="historical",
        computed_at=AS_OF,
        input_refs=(),
        producer="test",
        producer_version="1",
        case_ids=(),
        store_id=store,
        sku=SKU,
        baseline_ref=ArtifactRef(kind="ForecastVintage", id="v", version="1"),
        horizon_start=HORIZON[0],
        horizon_end=HORIZON[1],
        status="computed" if scenarios else "unchanged",
        reason=None if scenarios else "baseline",
        series=tuple(series),
        components=(component,) if scenarios else (),
        proposal_source="code",
    )


def fact(store, size, qty, day=date(2026, 10, 13), basis="sellable", netted=False) -> StockFact:
    return StockFact(
        id=f"stock:{store}:{size}:{day}",
        version="v1",
        available_at=datetime.combine(day + timedelta(days=1), time(6), ROME),
        availability_basis="test",
        source_refs=(REF,),
        location_id=store,
        sku=SKU,
        size=size,
        snapshot_at=datetime.combine(day, time(23, 59, 59), ROME),
        qty=qty,
        basis=basis,
        reservations_included=None if netted is None else netted,
        quality_holds_included=None if netted is None else netted,
        source_ref=REF,
    )


def position(store, stock, fc=None, curve=CURVE, country="IT", in_transit=0, netted=False):
    return Position(
        store_id=store,
        country=country,
        timezone=ROME,
        forecast=fc,
        stock={s: fact(store, s, q, netted=netted) for s, q in stock.items()},
        in_transit={s: in_transit for s in stock},
        in_assortment=True,
        size_curve=curve,
    )


def lane(transit=1, cost=(30.0, 1.0), customs=False, ibt=True) -> LaneEta:
    ln = Lane(
        lane_id="LN-1002-1001",
        origin="1002",
        dest="1001",
        origin_tz=ROME,
        mode="ROAD_EXPRESS",
        carrier="BRT",
        transit_days=transit,
        transit_days_p90=transit + 1,
        pickup_cutoff=time(12),
        pickup_days=frozenset(range(5)),
        customs_required=customs,
        documents=None,
        ibt_allowed=ibt,
        ibt_note=None,
        cost_fixed_eur=cost[0],
        cost_per_unit_eur=cost[1],
        last_reviewed=date(2026, 7, 15),
        source_ref=SourceRef(uri="test://lane", content_hash="sha256:lane"),
    )
    got = eta(ln, AS_OF)
    assert not isinstance(got, Unknown)
    return LaneEta(ln, got, None, None)


DEST_STOCK = {"00": 2, "0": 2, "1": 0, "2": 2, "3": 2, "4": 2}
DONOR_STOCK = {"00": 1, "0": 1, "1": 8, "2": 1, "3": 1, "4": 1}


def inputs(
    *,
    dest=None,
    donor=None,
    route_lane=None,
    policy=POLICY,
    case=None,
    reservations=(),
    size=None,
) -> OptionInputs:
    dest = dest or position("MIL01", DEST_STOCK, forecast("MIL01", 2.0))
    donor = donor or position("MIL02", DONOR_STOCK, forecast("MIL02", 1.0))
    return OptionInputs(
        case=case or fixture_case(),
        run_id="run",
        scenario_id="historical",
        as_of=AS_OF,
        horizon=HORIZON,
        sku=SKU,
        size=size,
        eans={s: f"80000000{i}" for i, s in enumerate(SIZES)},
        dest=dest,
        routes=(Route(donor, route_lane or lane()),),
        policy=policy,
        reservations=reservations,
    )


def by_kind(opts) -> dict[str, ActionOption]:
    assert len({o.kind for o in opts}) == len(opts)
    return {o.kind: o for o in opts}


def checks(option: ActionOption) -> dict[str, str]:
    return {c.name: c.status for c in option.checks}


def recommended(opts) -> list[str]:
    return [o.kind for o in opts if o.recommended]


# Pure service


def test_policy_is_read_from_domain_yaml():
    policy = options.load_policy(ROOT / "config")
    assert policy.max_units_per_transfer is not None and policy.donor_min_stock is not None
    assert policy.transfer_case_types == frozenset({"unmet_demand"})
    assert policy.scarce_skus == frozenset()
    assert policy.size_curve == "uniform" and policy.store_stock_netted is True
    assert options.policy_from({}) == OptionsPolicy()


def test_store_on_hand_counts_as_netted_only_by_declared_policy():
    donor = position("MIL02", DONOR_STOCK, forecast("MIL02", 1.0), netted=None)
    donor = replace(
        donor,
        stock={s: f.model_copy(update={"basis": "on_hand"}) for s, f in donor.stock.items()},
    )
    declared = by_kind(evaluate_options(inputs(donor=donor)))["transfer"]
    assert checks(declared)["reservations"] == checks(declared)["quality_hold"] == "pass"
    silent = replace(POLICY, store_stock_netted=None)
    t = by_kind(evaluate_options(inputs(donor=donor, policy=silent)))["transfer"]
    assert checks(t)["reservations"] == checks(t)["quality_hold"] == "unknown"


def test_admissible_transfer_is_recommended_with_whole_units_and_comparison():
    opts = evaluate_options(inputs())

    o = by_kind(opts)
    assert set(o) == {"hold", "verify_stock", "ask_store", "notify_owner", "transfer"}
    assert recommended(opts) == ["transfer"]
    t = o["transfer"]
    assert all(s == "pass" for s in checks(t).values()), checks(t)
    (leg,) = t.legs
    assert (leg.origin, leg.dest, leg.size, leg.qty) == ("MIL02", "MIL01", "1", 3)
    assert isinstance(leg.qty, int) and 1 <= leg.qty <= POLICY.max_units_per_transfer
    assert leg.pickup_at == datetime(2026, 10, 15, 12, tzinfo=ROME)
    assert leg.sellable_at == datetime(2026, 10, 17, tzinfo=ROME)
    assert leg.cost_eur == 33.0 and leg.ean == "800000002"
    assert [x.scenario_id for x in t.outcomes] == ["low", "base", "high"]
    base = {x.scenario_id: x for x in t.baseline_outcomes}["base"]
    moved = {x.scenario_id: x for x in t.outcomes}["base"]
    # Destination size 1: 0.6/day, out of stock. Hold loses 4.2; 3 units sellable from Sat 17
    # serve the 3.0 demand of Sat-Wed. The donor keeps its own demand (2.1) covered.
    assert base.lost_units_dest == pytest.approx(4.2)
    assert moved.lost_units_dest == pytest.approx(1.2)
    assert moved.lost_units_donor == base.lost_units_donor == 0
    # Donor: 8 minus 0.3 expected on the bridge day, rounded to 8; minus 3 moved, minus 2.1 sold.
    assert moved.leftover_units_donor == pytest.approx(8 - 3 - 2.1)
    assert "sellable 2026-10-17" in t.rationale
    assert t.valid_until == leg.pickup_at
    assert t.forecast_ref.id == "fc-mil01"


def test_informational_options_have_no_outcomes_and_hold_shows_destination_losses():
    o = by_kind(evaluate_options(inputs()))
    for kind in ("verify_stock", "ask_store", "notify_owner"):
        assert o[kind].outcomes is None and o[kind].legs == ()
    hold = {x.scenario_id: x for x in o["hold"].outcomes}
    # Size 1 loses 4.2; sizes 0 and 2 sell 2.8 each from 2 units; 00, 3 and 4 sell 1.4.
    assert hold["base"].lost_units_dest == pytest.approx(4.2 + 0.8 + 0.8)
    assert hold["base"].lost_units_donor is None


def test_missing_size_curve_blocks_the_move_and_asks_the_store():
    dest = position("MIL01", DEST_STOCK, forecast("MIL01", 2.0), curve=None)
    opts = evaluate_options(inputs(dest=dest))

    o = by_kind(opts)
    t = o["transfer"]
    assert checks(t)["size_curve"] == "unknown"
    assert "size_demand_unknown" in next(c.detail for c in t.checks if c.name == "size_curve")
    assert t.outcomes is None and t.baseline_outcomes is None and not t.recommended
    assert o["hold"].outcomes is None
    assert recommended(opts) == ["ask_store"]
    assert "MIL01 [0=2 00=2 1=0" in o["ask_store"].rationale
    assert t.legs[0].size == "1"  # the empty destination size, shown for confirmation


def test_missing_policy_is_unknown_never_permission():
    opts = evaluate_options(inputs(policy=OptionsPolicy()))

    t = by_kind(opts)["transfer"]
    status = checks(t)
    for name in ("quantity_policy", "transport_cost", "scarcity_policy", "stock_freshness"):
        assert status[name] == "unknown", name
    assert status["donor_protection"] == "unknown"
    assert not t.recommended


def test_q_max_is_bounded_by_policy_and_by_donor_availability():
    floor = replace(POLICY, donor_min_stock=1)
    donor = position("MIL02", DONOR_STOCK | {"1": 2}, forecast("MIL02", 0.0))
    t = by_kind(evaluate_options(inputs(donor=donor, policy=floor)))["transfer"]
    assert t.legs[0].qty == 1  # 2 on hand minus the donor floor of 1

    ledger = Reservation(
        id="res-1",
        version="v1",
        available_at=AS_OF,
        availability_basis="test",
        source_refs=(),
        run_id="run",
        scenario_id="historical",
        computed_at=AS_OF,
        input_refs=(),
        producer="act.approval",
        producer_version="1",
        decision_id="dec-1",
        location="MIL02",
        sku=SKU,
        size="1",
        qty=6,
        status="committed",
        idempotency_key="k",
        created_at=AS_OF,
    )
    t = by_kind(evaluate_options(inputs(reservations=(ledger,), policy=floor)))["transfer"]
    assert t.legs[0].qty == 1 and "6 unit(s) held" in str(t.checks)


def test_donor_is_protected_over_the_horizon_in_the_high_scenario():
    # Base: the donor sells 0.3/day of size 1 and could spare units. High: 0.9/day from 4 units
    # after the bridge day, so any unit moved is one more lost sale at the donor.
    donor_fc = forecast("MIL02", 1.0, [(0.0, 1.0, 3.0)] * 7)
    donor = position("MIL02", DONOR_STOCK | {"1": 5}, donor_fc)
    opts = evaluate_options(inputs(donor=donor))

    t = by_kind(opts)["transfer"]
    assert t.legs[0].size == "1"
    assert checks(t)["donor_protection"] == "fail" and not t.recommended
    detail = next(c.detail for c in t.checks if c.name == "donor_protection")
    assert detail.startswith("high scenario")
    hold = {x.scenario_id: x for x in t.baseline_outcomes}
    moved = {x.scenario_id: x for x in t.outcomes}
    assert moved["high"].lost_units_donor > hold["high"].lost_units_donor
    assert "transfer" not in recommended(opts)


def test_extra_donor_loss_fails_even_when_hold_already_stocks_out():
    # Donor size 1 sells 1.2/day in every scenario from 4 units: it stocks out under hold too.
    donor = position("MIL02", DONOR_STOCK | {"1": 4}, forecast("MIL02", 4.0))
    policy = replace(POLICY, donor_min_stock=0)
    cands = options._quantities(
        inputs(donor=donor, policy=policy),
        donor,
        lane(),
        "1",
        options._days(HORIZON),
        options.servable(forecast("MIL01", 2.0), options._days(HORIZON)),
    )
    for c in cands:
        if c.outcomes is None:  # more than the donor still holds on the pickup day
            assert ("donor_availability", "fail") in [(x.name, x.status) for x in c.checks]
            continue
        hold_lost = {x.scenario_id: x for x in c.baseline}["high"].lost_units_donor
        moved_lost = {x.scenario_id: x for x in c.outcomes}["high"].lost_units_donor
        assert hold_lost > 0
        protection = next(x for x in c.checks if x.name == "donor_protection")
        assert (protection.status == "fail") == (moved_lost > hold_lost)
    assert any(x.name == "donor_protection" and x.status == "fail" for c in cands for x in c.checks)


def test_unknown_stock_is_never_zero_and_asks_for_verification():
    dest = position("MIL01", DEST_STOCK, forecast("MIL01", 2.0))
    dest = replace(dest, stock=dict(dest.stock) | {"1": Unknown("unavailable", "down")})
    opts = evaluate_options(inputs(dest=dest))

    o = by_kind(opts)
    assert checks(o["transfer"])["dest_stock"] == "unknown"
    assert o["transfer"].outcomes is None
    assert recommended(opts) == ["verify_stock"]
    assert "unavailable" in o["verify_stock"].rationale


def test_store_on_hand_without_netting_blocks_on_reservations_and_quality_holds():
    donor = position("MIL02", DONOR_STOCK, forecast("MIL02", 1.0), netted=None)
    t = by_kind(evaluate_options(inputs(donor=donor)))["transfer"]
    assert checks(t)["reservations"] == checks(t)["quality_hold"] == "unknown"
    assert not t.recommended


def test_stale_snapshot_and_units_in_transit_block():
    dest = position("MIL01", DEST_STOCK, forecast("MIL01", 2.0), in_transit=2)
    t = by_kind(evaluate_options(inputs(dest=dest)))["transfer"]
    assert checks(t)["dest_inbound"] == "unknown"

    old = replace(
        dest,
        in_transit={s: 0 for s in SIZES},
        stock={s: fact("MIL01", s, q, day=date(2026, 10, 10)) for s, q in DEST_STOCK.items()},
    )
    t = by_kind(evaluate_options(inputs(dest=old)))["transfer"]
    assert checks(t)["stock_freshness"] == "fail"


def test_not_estimable_forecast_is_not_quantified():
    fc = forecast("MIL01", 2.0)
    blank = tuple(p.model_copy(update={"latent": None, "servable": None}) for p in fc.series)
    fc = fc.model_copy(update={"status": "not_estimable", "reason": "x", "series": blank})
    o = by_kind(evaluate_options(inputs(dest=position("MIL01", DEST_STOCK, fc))))
    assert checks(o["transfer"])["dest_forecast"] == "unknown"
    assert o["transfer"].outcomes is None and o["hold"].outcomes is None


def test_cross_border_late_eta_and_unknown_cost_block():
    t = by_kind(evaluate_options(inputs(route_lane=lane(customs=True))))["transfer"]
    assert checks(t)["domestic"] == "fail" and not t.recommended

    t = by_kind(evaluate_options(inputs(route_lane=lane(transit=6))))["transfer"]
    assert checks(t)["eta_in_time"] == "fail" and not t.recommended

    t = by_kind(evaluate_options(inputs(route_lane=lane(cost=(None, 1.0)))))["transfer"]
    assert checks(t)["transport_cost"] == "unknown" and t.legs[0].cost_eur is None
    assert not t.recommended


def test_pick_changing_between_scenarios_is_not_recommended():
    # Low: the destination sells nothing more, base/high: 1.4 and 4/day of colour.
    dest_fc = forecast("MIL01", 1.4, [(0.0, 1.4, 4.0)] * 7)
    opts = evaluate_options(inputs(dest=position("MIL01", DEST_STOCK, dest_fc)))

    o = by_kind(opts)
    assert not o["transfer"].recommended
    assert "changes between scenarios" in o["transfer"].rationale
    assert recommended(opts) == ["ask_store"]


def test_non_movable_case_type_gets_no_transfer():
    opts = evaluate_options(inputs(case=fixture_case(case_type="product_feedback")))
    assert "transfer" not in by_kind(opts)
    assert recommended(opts) == ["notify_owner"]


def test_pure_and_hash_follows_inputs():
    a, b = evaluate_options(inputs()), evaluate_options(inputs())
    assert a == b
    assert len({o.input_version_hash for o in a}) == 1
    donor = position("MIL02", DONOR_STOCK | {"1": 9}, forecast("MIL02", 1.0))
    changed = inputs(donor=donor)
    assert input_version_hash(changed) != a[0].input_version_hash
    assert evaluate_options(changed)[0].version != a[0].version


def test_wording_never_claims_optimal_or_roi():
    for opts in (evaluate_options(inputs()), evaluate_options(inputs(policy=OptionsPolicy()))):
        for o in opts:
            text = " ".join((o.rationale, *o.assumptions, *(c.detail for c in o.checks)))
            assert "optimal" not in text.lower() and "roi" not in text.lower().split()


def test_case_product_from_scope():
    assert options.case_product(fixture_case()) == (SKU, None)
    tib = fixture_case(scope_level="sku_size", scope_id="J10911A00305-742-4")
    assert options.case_product(tib) == ("J10911A00305-742", "4")
    style = fixture_case(scope_level="style", scope_id="J20931A00012")
    assert options.case_product(style) == (None, None)


# Module


T = AS_OF
STOCK = ("snapshot_date", "store_id", "sku", "size", "on_hand", "in_transit")
FORECAST = ("run_date", "target_week", "week_start", "store_id", "sku", "fcst_units")


def write(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


@pytest.fixture
def sources(tmp_path, monkeypatch):
    erp_dir = tmp_path / "sources" / "erp"
    master = erp_dir / "master_data"
    stores = [
        ("MIL01", "Europe/Rome", "EUR", "", "IT"),
        ("MIL02", "Europe/Rome", "EUR", "", "IT"),
        ("PAR01", "Europe/Paris", "EUR", "Sun", "FR"),
    ]
    write(
        master / "stores.csv",
        ("store_id", "timezone", "currency", "closed_dow", "country_code"),
        stores,
    )
    write(master / "styles.csv", ("style_code", "style_name"), [("J20931A00012", "MAIRE")])
    write(
        master / "sku_colour.csv",
        ("sku", "style_code", "color_code"),
        [(SKU, "J20931A00012", "999")],
    )
    write(
        master / "sku_size_ean.csv",
        ("sku", "size", "sku_size", "ean"),
        [(SKU, s, f"{SKU}-{s}", f"80000000{i}") for i, s in enumerate(SIZES)],
    )
    write(master / "store_assortment.csv", ("store_id", "sku"), [(s[0], SKU) for s in stores])
    write(
        master / "price_list_FW26.csv",
        ("store_id", "sku", "currency", "retail_price", "valid_from"),
        [("MIL01", SKU, "EUR", "1500.00", "2026-08-01")],
    )
    (erp_dir / "sales" / "daily_store_sku").mkdir(parents=True)
    write(
        erp_dir / "inventory" / "store_stock_daily" / "stock_eod_2026-10-13.csv",
        STOCK,
        [("2026-10-13", "MIL01", SKU, s, q, 0) for s, q in DEST_STOCK.items()]
        + [("2026-10-13", "MIL02", SKU, s, q, 0) for s, q in DONOR_STOCK.items()]
        + [("2026-10-13", "PAR01", SKU, s, 9, 0) for s in SIZES],
    )
    rows = []
    for store, units in (("MIL01", "14"), ("MIL02", "7"), ("PAR01", "7")):
        for ws in ("2026-10-12", "2026-10-19"):
            week = date.fromisoformat(ws).strftime("%G-W%V")
            rows.append(("2026-10-12", week, ws, store, SKU, units))
    write(
        erp_dir / "forecast" / "sku_store_weekly" / "fcst_sku_store_run_2026-10-12.csv",
        FORECAST,
        rows,
    )
    root = tmp_path / "sources"
    monkeypatch.setattr(erp, "get_settings", lambda: SimpleNamespace(sources_dir=root))
    return root


def lanes(seen: list[tuple[str, str]]):
    template = json.loads(
        (
            ROOT / "generated/sources/systems/agents/examples/logistics_get_lane_MIL02_MIL01.json"
        ).read_text()
    )["response"]

    def handler(request: httpx.Request) -> httpx.Response:
        origin, dest = request.url.params["origin"], request.url.params["dest"]
        seen.append((origin, dest))
        body = template | {
            "lane_id": f"LN-{origin}-{dest}",
            "origin": origin,
            "dest": dest,
            "mode": "ROAD_EXPRESS",
            "transit_days_contract": 1,
            "transit_days_p90_contract": 2,
            "pickup_cutoff_local": "12:00",
        }
        return httpx.Response(200, json=body)

    return handler


def test_module_writes_options_for_open_cases_with_domestic_donors_only(tmp_path, sources):
    spec = RunSpec(
        run_id="run-1014",
        scenario_id="historical",
        as_of=T,
        stores=("MIL01", "MIL02", "PAR01"),
        source_manifest_hash="sha256:test",
        config_hash="sha256:test",
        code_version="test",
        mode="live",
        modules=(
            ModuleSnapshot(manifest=erp.MANIFEST, params={}),
            ModuleSnapshot(manifest=baseline.MANIFEST, params={}),
            ModuleSnapshot(manifest=options.MANIFEST, params={}),
        ),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    engine = connect(f"sqlite:///{tmp_path / 'opt.db'}")
    create_run(engine, spec)
    erp.load_window(engine, spec, {}, sources_dir=sources)
    repo = Repo(engine, spec)
    baseline.write_baselines(repo, 7)
    repo.put(
        fixture_case(run_id=spec.run_id),
        fixture_case(run_id=spec.run_id, id="case-closed", status="closed"),
    )
    crosswalk = Crosswalk(
        store_plant={"MIL01": "1001", "MIL02": "1002", "PAR01": "2001"},
        timezones={"MIL01": "Europe/Rome", "MIL02": "Europe/Rome", "PAR01": "Europe/Paris"},
        sku_matnr={SKU: SKU.replace("-", "")},
        ean_sku_size={},
    )
    seen: list[tuple[str, str]] = []
    client = SystemsClient(crosswalk, transport=httpx.MockTransport(lanes(seen)))
    reader = SystemsReader(repo, client)

    result = options.build_options(repo, reader, options.load_policy(ROOT / "config"), 7)

    assert result.status == "succeeded", result
    assert result.counts["cases"] == 1 and result.counts["options"] == 5
    assert seen == [("1002", "1001")]  # PAR01 is cross-border: never asked
    stored = {o.kind: o for o in repo.list(ActionOption, case_id=fixture_case().id)}
    t = stored["transfer"]
    assert t.legs[0].origin == "MIL02" and t.run_id == spec.run_id
    # Declared policies stand in for the missing size curve and store reservations.
    assert all(v == "pass" for v in checks(t).values()), checks(t)
    detail = {c.name: c.detail for c in t.checks}
    assert "declared policy: uniform over 6 master sizes" in detail["size_curve"]
    assert "declared policy" in detail["reservations"]
    assert recommended(stored.values()) == ["transfer"]
    (leg,) = t.legs
    assert (leg.size, leg.qty, leg.lane_id) == ("1", 2, "LN-1002-1001")
    assert t.available_at <= T


def test_manifest_is_an_actions_module():
    assert isinstance(options.MANIFEST, ModuleManifest)
    assert options.MANIFEST.layer == "actions" and options.MANIFEST.produces == ("ActionOption",)
    assert callable(options.run)


def test_donor_with_nothing_to_give_is_no_transfer_but_a_stated_reason():
    donor = position("MIL02", {s: 0 for s in SIZES}, forecast("MIL02", 1.0))
    opts = evaluate_options(inputs(donor=donor))

    o = by_kind(opts)
    assert "transfer" not in o
    assert "MIL02: no unit of J20931A00012-999 to give in 0, 00, 1, 2, 3, 4" in (
        o["notify_owner"].rationale
    )
    assert recommended(opts) == ["notify_owner"]


def test_style_case_keeps_the_colour_with_a_useful_move():
    style = fixture_case(scope_level="style", scope_id="J20931A00012")
    # Colour 742: the destination is full, so moving brings nothing. Colour 999: size 1 is empty.
    full = position("MIL01", {s: 9 for s in SIZES}, forecast("MIL01", 2.0))
    useless = replace(inputs(case=style, dest=full), sku="J20931A00012-742")
    useful = inputs(case=style)

    opts = options.evaluate_case([useless, useful])

    o = by_kind(opts)
    assert recommended(opts) == ["transfer"] and o["transfer"].legs[0].sku == SKU
    assert any("Style case: colour J20931A00012-999 kept" in a for a in o["transfer"].assumptions)
    assert o["transfer"].input_version_hash != input_version_hash(useful)
    assert options.evaluate_case([useful]) == evaluate_options(useful)
