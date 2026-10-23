"""RFC §7.3 gate test 6 (TST-06): sizes, missing curves, zero/missing forecast, closed days,
partial horizon.

Each clause of the RFC item is one group of tests below:

1. quantities per size add up to the colour;
2. a missing size curve blocks every per-size estimate (no invented split);
3. a zero forecast and a missing forecast are different, explicit outcomes;
4. closed days and a partial horizon are handled explicitly.

Run evening: Wed 2026-10-14 20:00 in Milan, horizon Thu 15 → Wed 21 (ISO weeks 10-12 and 10-19).
"""

from dataclasses import replace
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import (
    AdjustmentComponent,
    ArtifactRef,
    Case,
    Evidence,
    ForecastAdjustment,
    ForecastPoint,
    Observation,
    Quantity,
    RunSpec,
    ScenarioValues,
    SourceRef,
    StockFact,
)
from tesseract.core.repo import ErpRecord
from tesseract.modules.actions import options
from tesseract.modules.actions.options import (
    OptionInputs,
    Position,
    Route,
    SizeCurve,
    evaluate_options,
)
from tesseract.modules.intelligence import baseline, overlay
from tesseract.modules.intelligence.disaggregation import disaggregate
from tesseract.modules.sources.systems_client import Lane, LaneEta, Unknown, eta

ROME = ZoneInfo("Europe/Rome")
AS_OF = datetime(2026, 10, 14, 18, tzinfo=UTC)
START = date(2026, 10, 15)
DAYS = tuple(START + timedelta(days=i) for i in range(7))
HORIZON = (DAYS[0], DAYS[-1])
WEEK1, WEEK2 = date(2026, 10, 12), date(2026, 10, 19)
SUNDAY = date(2026, 10, 18)
SKU = "J20931A00012-999"
SIZES = ("00", "0", "1", "2", "3", "4")
CURVE = SizeCurve({"00": 0.1, "0": 0.2, "1": 0.3, "2": 0.2, "3": 0.1, "4": 0.1}, "test curve")
REF = SourceRef(uri="test://fcst_sku_store_run_2026-10-12.csv", content_hash="sha256:test")
POLICY = replace(options.load_policy(REPO_ROOT / "config"), scarce_skus=frozenset())


def spec() -> RunSpec:
    return RunSpec(
        run_id="gate-6", scenario_id="historical", as_of=AS_OF, stores=("MIL01", "PAR01"),
        source_manifest_hash="s", config_hash="c", code_version="0", mode="fixture", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


def derived(id_: str, at: datetime) -> dict:
    return dict(
        id=id_, version="v1", available_at=at, availability_basis="test", source_refs=(),
        run_id="gate-6", scenario_id="historical", computed_at=at, input_refs=(),
        producer="test", producer_version="1",
    )  # fmt: skip


# fc.baseline over ERP rows


def store_row(store_id: str, closed_dow: str = "") -> ErpRecord:
    data = {"store_id": store_id, "timezone": "Europe/Rome", "closed_dow": closed_dow}
    return ErpRecord("stores", store_id, "v1", AS_OF - timedelta(days=30), "test", (REF,), data)


def fcst(store_id: str, sku: str, week: date, units: float) -> ErpRecord:
    data = {
        "store_id": store_id, "sku": sku, "run_date": WEEK1, "target_week": week.strftime("%G-W%V"),
        "week_start": week, "fcst_units": units,
    }  # fmt: skip
    at = AS_OF - timedelta(days=2)
    return ErpRecord("forecast", f"{store_id}/{sku}/{week}", "v1", at, "test", (REF,), data)


def baselines(store: ErpRecord, rows, assortment) -> dict[str, ForecastAdjustment]:
    built = baseline.build_store(spec(), store, rows, assortment, 7)
    return {r.sku: r for r in built}


def values(record: ForecastAdjustment) -> list[float | None]:
    return [p.baseline for p in record.series]


# act.options inputs


def forecast(store: str, daily, *, covers=7, scenarios=None) -> ForecastAdjustment:
    series = []
    for day in DAYS[:covers]:
        low, base, high = scenarios if scenarios else (daily, daily, daily)
        latent = ScenarioValues(low=low, base=base, high=high)
        series.append(ForecastPoint(date=day, baseline=daily, latent=latent, servable=latent))
    return ForecastAdjustment(
        **derived(f"fc-{store.lower()}", AS_OF - timedelta(days=2)),
        case_ids=(), store_id=store, sku=SKU,
        baseline_ref=ArtifactRef(kind="ForecastVintage", id="v", version="1"),
        horizon_start=DAYS[0], horizon_end=DAYS[covers - 1],
        status="computed" if scenarios else "unchanged", reason=None if scenarios else "baseline",
        series=tuple(series), components=(UPLIFT,) if scenarios else (), proposal_source="code",
    )  # fmt: skip


UPLIFT = AdjustmentComponent(
    type="incremental", episode_refs=(), evidence_refs=(), params={}, unit="units",
    effective_from=AS_OF, effective_until=AS_OF + timedelta(days=7), reference_time=AS_OF,
    formula_version="test", explanation="test scenarios",
)  # fmt: skip


def stock(store: str, size: str, qty: int) -> StockFact:
    snapshot = datetime(2026, 10, 13, 23, 59, 59, tzinfo=ROME)
    return StockFact(
        id=f"stock:{store}:{size}", version="v1", available_at=snapshot + timedelta(hours=7),
        availability_basis="test", source_refs=(REF,), location_id=store, sku=SKU, size=size,
        snapshot_at=snapshot, qty=qty, basis="sellable", reservations_included=False,
        quality_holds_included=False, source_ref=REF,
    )  # fmt: skip


def position(store: str, qty: dict[str, int], fc, curve=CURVE) -> Position:
    return Position(
        store_id=store, country="IT", timezone=ROME, forecast=fc,
        stock={s: stock(store, s, q) for s, q in qty.items()}, in_transit={s: 0 for s in qty},
        in_assortment=True, size_curve=curve,
    )  # fmt: skip


def lane() -> LaneEta:
    ln = Lane(
        lane_id="LN-1002-1001", origin="1002", dest="1001", origin_tz=ROME, mode="ROAD_EXPRESS",
        carrier="BRT", transit_days=1, transit_days_p90=2, pickup_cutoff=time(12),
        pickup_days=frozenset(range(5)), customs_required=False, documents=None, ibt_allowed=True,
        ibt_note=None, cost_fixed_eur=30.0, cost_per_unit_eur=1.0, last_reviewed=date(2026, 7, 15),
        source_ref=SourceRef(uri="test://lane", content_hash="sha256:lane"),
    )  # fmt: skip
    got = eta(ln, AS_OF)
    assert not isinstance(got, Unknown)
    return LaneEta(ln, got, None, None)


def case() -> Case:
    at = AS_OF - timedelta(hours=2)
    return Case(
        **derived("case-mil01", at), case_type="unmet_demand", store_id="MIL01",
        scope_level="sku", scope_id=SKU, window_start=at, window_end=at, status="open",
        owner="merch", priority="high", priority_reason="test", first_available_at=at,
        last_received_at=at, last_independent_evidence_at=at,
        valid_until=at + timedelta(days=7), supporting=(), contradicting=(), n_documents=1,
        n_origin_groups=1, n_unknown_origins=0, blocking_uncertainties=(), context_refs=(),
    )  # fmt: skip


def inputs(dest: Position, donor: Position | None = None) -> OptionInputs:
    donor = donor or position("MIL02", {s: 3 for s in SIZES}, forecast("MIL02", 1.0))
    return OptionInputs(
        case=case(), run_id="gate-6", scenario_id="historical", as_of=AS_OF, horizon=HORIZON,
        sku=SKU, size=None, eans={s: f"80000000{i}" for i, s in enumerate(SIZES)}, dest=dest,
        routes=(Route(donor, lane()),), policy=POLICY,
    )  # fmt: skip


def by_kind(opts):
    return {o.kind: o for o in opts}


def check(option, name):
    return next(c for c in option.checks if c.name == name)


EMPTY = {s: 0 for s in SIZES}


# 1. Quantities per size add up to the colour


def test_size_curve_must_split_the_whole_colour():
    with pytest.raises(ValueError, match="sum to 1"):
        SizeCurve({"0": 0.5, "1": 0.4}, "leaks 10% of the colour")
    with pytest.raises(ValueError, match="non-negative"):
        SizeCurve({"0": 1.2, "1": -0.2}, "negative size")


def test_per_size_demand_adds_up_to_the_colour_demand():
    colour = (1.0, 2.0, 3.5, 0.0, 2.0, 2.0, 4.0)
    per_size = [options._share(colour, CURVE.weights[s]) for s in SIZES]
    assert [sum(day) for day in zip(*per_size, strict=True)] == pytest.approx(colour)


def test_lost_units_over_the_sizes_equal_the_colour_demand_when_nothing_is_on_hand():
    fc = forecast("MIL01", 2.0, scenarios=(1.0, 2.0, 3.0))
    hold = by_kind(evaluate_options(inputs(position("MIL01", EMPTY, fc))))["hold"]
    lost = {o.scenario_id: o.lost_units_dest for o in hold.outcomes}
    # Colour demand over 7 days: 7 / 14 / 21. Every unit is lost exactly once across the sizes.
    assert lost == pytest.approx({"low": 7.0, "base": 14.0, "high": 21.0})
    assert all(o.leftover_units_dest == 0 for o in hold.outcomes)


# 2. A missing size curve blocks per-size estimates


@pytest.mark.parametrize("missing", ["dest", "donor"])
def test_missing_curve_blocks_every_size_estimate_and_asks_the_store(missing):
    dest_curve = None if missing == "dest" else CURVE
    donor_curve = None if missing == "donor" else CURVE
    dest = position("MIL01", EMPTY, forecast("MIL01", 2.0), curve=dest_curve)
    donor = position("MIL02", {s: 3 for s in SIZES}, forecast("MIL02", 1.0), curve=donor_curve)
    opts = by_kind(evaluate_options(inputs(dest, donor)))
    transfer = opts["transfer"]
    curve = check(transfer, "size_curve")
    assert curve.status == "unknown" and "size_demand_unknown" in curve.detail
    assert transfer.outcomes is None and transfer.baseline_outcomes is None
    assert not transfer.recommended
    assert opts["ask_store"].recommended
    if missing == "dest":
        assert opts["hold"].outcomes is None  # no lost units per size without the curve


def test_size_outside_the_curve_fails_instead_of_getting_a_share():
    partial = SizeCurve({"0": 0.5, "2": 0.5}, "two sizes only")
    dest = position("MIL01", EMPTY, forecast("MIL01", 2.0), curve=partial)
    opts = by_kind(evaluate_options(replace(inputs(dest), size="1")))
    curve = check(opts["transfer"], "size_curve")
    assert curve.status == "fail" and "size 1 not in the curve" in curve.detail
    assert opts["transfer"].outcomes is None


# 3. Zero forecast and missing forecast are different, explicit outcomes


def test_zero_forecast_is_a_zero_baseline_and_missing_forecast_is_not_estimable():
    daily = disaggregate({WEEK1: 0.0, WEEK2: 0.0}, START, 7)
    assert daily.status == "computed" and daily.total == 0.0
    assert all(p.baseline == 0.0 for p in daily.points)

    gap = disaggregate({WEEK1: 0.0}, START, 7)
    assert gap.status == "not_estimable" and gap.total is None
    assert gap.reasons == (f"missing_forecast:{WEEK2}",)
    assert all(p.baseline is None for p in gap.points if p.week_start == WEEK2)

    nan = disaggregate({WEEK1: 7.0, WEEK2: float("nan")}, START, 7)
    assert nan.status == "not_estimable"  # NaN is missing, never 0


def test_baseline_module_keeps_zero_and_missing_apart():
    rows = [fcst("MIL01", "J1-000", w, 0.0) for w in (WEEK1, WEEK2)]
    built = baselines(store_row("MIL01"), rows, {"J1-000", "J1-404"})
    zero, missing = built["J1-000"], built["J1-404"]
    assert zero.status == "unchanged" and values(zero) == [0.0] * 7
    assert all(p.servable == ScenarioValues(low=0, base=0, high=0) for p in zero.series)
    assert missing.status == "not_estimable" and "sku_not_in_vintage" in missing.reason
    assert values(missing) == [None] * 7
    assert all(p.latent is None and p.servable is None for p in missing.series)


def test_options_quantify_a_zero_forecast_but_not_a_missing_one():
    zero = by_kind(evaluate_options(inputs(position("MIL01", EMPTY, forecast("MIL01", 0.0)))))
    assert check(zero["transfer"], "dest_forecast").status == "pass"
    assert all(o.lost_units_dest == 0 for o in zero["hold"].outcomes)

    missing = by_kind(evaluate_options(inputs(position("MIL01", EMPTY, None))))
    dest_check = check(missing["transfer"], "dest_forecast")
    assert dest_check.status == "unknown" and "no forecast at as_of" in dest_check.detail
    assert missing["hold"].outcomes is None and missing["transfer"].outcomes is None


def test_zero_baseline_on_an_open_day_with_an_uplift_is_not_a_hidden_increase():
    record = overlay_record([0.0] * 7, closed=frozenset())
    assert record.status == "not_estimable" and record.reason.startswith("cold_start")
    assert all(p.latent is None for p in record.series)


# 4. Closed days and a partial horizon


def test_closed_days_are_zero_and_the_week_is_spread_over_open_days_only():
    closed = {SUNDAY, WEEK2 + timedelta(days=6)}
    daily = disaggregate({WEEK1: 12.0, WEEK2: 12.0}, WEEK1, 14, closed)
    week = [p for p in daily.points if p.week_start == WEEK1]
    assert [p.baseline for p in week] == [2.0] * 6 + [0.0]
    assert sum(p.baseline for p in week) == pytest.approx(12.0)
    assert not week[-1].open

    all_closed = disaggregate({WEEK1: 5.0}, WEEK1, 7, {WEEK1 + timedelta(days=i) for i in range(7)})
    assert all_closed.status == "not_estimable"
    assert all_closed.reasons == (f"closed_week_with_forecast:{WEEK1}",)


def test_baseline_module_reads_the_closed_weekday_from_the_store_master():
    rows = [fcst("PAR01", SKU, w, 12.0) for w in (WEEK1, WEEK2)]
    record = baselines(store_row("PAR01", "Sun"), rows, {SKU})[SKU]
    assert record.status == "unchanged"
    by_day = dict(zip(DAYS, values(record), strict=True))
    assert by_day[SUNDAY] == 0.0
    assert all(v == 2.0 for d, v in by_day.items() if d != SUNDAY)


def test_partial_week_takes_only_the_horizon_days_never_the_whole_week():
    daily = disaggregate({WEEK1: 14.0, WEEK2: 14.0}, START, 7)
    # Thu 15..Sun 18 of week 10-12 carry 4/7 of it; the weekly total is not squeezed into them.
    assert [p.baseline for p in daily.points[:4]] == [2.0] * 4
    assert daily.total == pytest.approx(14.0)


def test_horizon_beyond_the_vintage_is_not_estimable_not_truncated():
    rows = [fcst("MIL01", SKU, WEEK1, 14.0)]
    record = baselines(store_row("MIL01"), rows, {SKU})[SKU]
    assert record.status == "not_estimable" and f"missing_forecast:{WEEK2}" in record.reason
    assert values(record)[:4] == [2.0] * 4 and values(record)[4:] == [None] * 3
    assert all(p.servable is None for p in record.series)
    assert (record.horizon_start, record.horizon_end) == HORIZON


def test_options_refuse_a_forecast_that_covers_only_part_of_the_horizon():
    short = forecast("MIL01", 2.0, covers=4)
    opts = by_kind(evaluate_options(inputs(position("MIL01", EMPTY, short))))
    dest_check = check(opts["transfer"], "dest_forecast")
    assert dest_check.status == "unknown" and "does not cover" in dest_check.detail
    assert opts["hold"].outcomes is None and opts["transfer"].outcomes is None


def test_closed_day_gets_no_uplift_and_its_zero_baseline_is_not_a_cold_start():
    by_day = [0.0 if d == SUNDAY else 2.0 for d in DAYS]
    record = overlay_record(by_day, closed=frozenset({6}))
    assert record.status == "computed"
    sunday = next(p for p in record.series if p.date == SUNDAY)
    assert sunday.latent == ScenarioValues(low=0, base=0, high=0)
    (daily,) = [c.params["daily"] for c in record.components if c.type == "incremental_episode"]
    assert next(d for d in daily if d["date"] == SUNDAY.isoformat())["w"] == 0.0


def overlay_record(daily: list[float], closed: frozenset[int]) -> ForecastAdjustment:
    """One admissible episode (6 units over Tue 13 + Wed 14) on a given daily baseline."""
    store = overlay.Store("MIL01", ROME, closed)
    at = datetime(2026, 10, 14, 20, tzinfo=ROME)
    obs = Observation(
        **derived("obs-maire", at), document_id="doc-maire", kind="unmet_demand",
        store_id="MIL01", period_start=datetime(2026, 10, 13, tzinfo=ROME),
        period_end=datetime(2026, 10, 14, 23, 59, 59, tzinfo=ROME), product_mention="Maire nera",
        quantity=Quantity(kind="exact", value=6, unit="units"), direction="up",
        attribution="store_staff", negated=False, extractor_version="test",
        evidence=(Evidence(document_id="doc-maire", document_version="v1", segment_id="seg",
                           quote="x", char_start=0, char_end=1),),
    )  # fmt: skip
    points = tuple(
        ForecastPoint(date=d, baseline=v, latent=flat, servable=flat)
        for d, v in zip(DAYS, daily, strict=True)
        for flat in (ScenarioValues(low=v, base=v, high=v),)
    )
    base = forecast("MIL01", 0.0).model_copy(
        update={"series": points, "producer": baseline.MANIFEST.id, "status": "unchanged"}
    )
    episode = overlay.gate(obs, store)
    assert isinstance(episode, overlay.Episode)
    policy = overlay.load_policy(REPO_ROOT / "config")
    return overlay.build_overlay(spec(), case(), base, store, policy, [episode], [])
