"""DATA-01c: stock facts, options and agent trace validate against their contracts, match the
sources they cite and respect availability (rebuild with `data/fixtures/build_data01c.py`)."""

import csv
import hashlib
import json
from datetime import date, timedelta
from functools import cache
from pathlib import Path

import pytest
import yaml

from tessera.core.contracts import (
    ActionOption,
    AgentTrace,
    ArtifactRef,
    Case,
    EntityLink,
    ForecastAdjustment,
    Leg,
    Observation,
    StockFact,
)
from tessera.core.contracts.common import SourceRecord
from tessera.core.fixtures import FIXTURE_RUN_ID, FIXTURE_SCENARIO_ID, read_fixtures

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "data" / "fixtures"
SOURCES = ROOT / "generated" / "sources"
MASTER = SOURCES / "erp" / "master_data"
STOCK_DIR = SOURCES / "erp" / "inventory" / "store_stock_daily"
POS_DIR = SOURCES / "erp" / "sales" / "pos_lines"
ATP = SOURCES / "systems" / "warehouse" / "atp" / "ATP_projection_20261005.csv"
LANES = SOURCES / "systems" / "logistics" / "lane_matrix_lead_time_cost.csv"
MIN_PRES = SOURCES / "systems" / "planning" / "min_presentation_by_store_category.csv"
CROSSWALK = SOURCES / "systems" / "reference" / "store_code_crosswalk_MDM.csv"
CASE_ID = "case-mil01-i10919b00011-20261008"
FORECAST_ID = "fc-mil01-i10919b00011-999-20261010"
STORE, DONOR, DC = "MIL01", "MIL02", "IT10"
SIZE = "M"
SKU = "I10919B00011-999"
SKU_BLUE = "I10919B00011-742"
SIZES = (SKU, SKU_BLUE)
FOLDERS = {
    "stock": (StockFact,),
    "options": (ActionOption,),
    "traces": (AgentTrace,),
}
OTHER_KINDS = {
    "Case": Case,
    "Observation": Observation,
    "EntityLink": EntityLink,
    "ForecastAdjustment": ForecastAdjustment,
}
KINDS = {cls.__name__: cls for classes in FOLDERS.values() for cls in classes} | OTHER_KINDS
# A check may cite a source file that has no contract (`SourceFile`, uri + content hash), the way
# DATA-01b cites a `ForecastVintage` row. Everything else must be a stored record.
EXTERNAL_KINDS = {"SourceFile", "ForecastVintage"}
MOVEMENTS = {"replenish_dc", "transfer", "combo"}
MANDATORY_CHECKS = {
    "identity_crosswalk",
    "reservations",
    "quality_hold",
    "min_presentation_safety",
    "scarcity_assortment",
    "lane_ibt",
    "calendar_cutoff",
    "eta_required_by",
    "donor_protected",
    "size_curve",
    "shared_resources",
}
TOOLS = {
    "get_case_evidence",
    "get_available_stock",
    "get_lane_and_eta",
    "evaluate_options",
    "request_clarification",
    "finish",
}


def load(folder: str) -> list[SourceRecord]:
    records = []
    for path in sorted((FIXTURES / folder).glob("*.json")):
        for rec in json.loads(path.read_text(encoding="utf-8")):
            assert rec["kind"] in {c.__name__ for c in FOLDERS[folder]}, (path, rec["kind"])
            records.append(KINDS[rec["kind"]].model_validate(rec["payload"]))
    return records


@cache
def everything() -> dict[tuple[str, str], SourceRecord]:
    records = [r for folder in FOLDERS for r in load(folder)]
    for folder in ("documents", "observations", "links", "cases", "forecast", "reports"):
        for path in sorted((FIXTURES / folder).glob("*.json")):
            for rec in json.loads(path.read_text(encoding="utf-8")):
                if rec["kind"] in KINDS:
                    records.append(KINDS[rec["kind"]].model_validate(rec["payload"]))
    return {(type(r).__name__, r.id): r for r in records}


def of(kind: type) -> list:
    return [r for r in everything().values() if type(r) is kind]


def resolve(ref: ArtifactRef) -> SourceRecord:
    record = everything()[(ref.kind, ref.id)]
    assert record.version == ref.version, ref
    return record


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@cache
def lanes() -> dict[str, dict[str, str]]:
    return {r["lane_id"]: r for r in read_csv(LANES)}


@cache
def case() -> Case:
    return everything()[("Case", CASE_ID)]


@cache
def forecast() -> ForecastAdjustment:
    return everything()[("ForecastAdjustment", FORECAST_ID)]


@cache
def size_share(store: str) -> float:
    """The curve the fixtures use: size M units / colour units on days size M opened in stock."""
    units: dict[str, int] = {}
    stock: dict[tuple[date, str, str, str], float] = {}

    def on_hand(day: date, size: str) -> float:
        key = (day, store, SKU, size)
        if key not in stock:
            for row in read_csv(STOCK_DIR / f"stock_eod_{day.isoformat()}.csv"):
                stock[(day, row["store_id"], row["sku"], row["size"])] = float(row["on_hand"])
        return stock[key]

    for week in (36, 37, 38, 39, 40):
        for row in read_csv(POS_DIR / f"pos_lines_2026-W{week}.csv"):
            day = date.fromisoformat(row["business_date"])
            if not (date(2026, 8, 31) <= day <= date(2026, 10, 4)):
                continue
            if (row["store_id"], row["sku"]) != (store, SKU):
                continue
            if on_hand(day - timedelta(days=1), SIZE) <= 0:
                continue
            sign = -1 if row["line_type"] == "RETURN" else 1
            units[row["size"]] = units.get(row["size"], 0) + sign * int(row["qty"])
    return units[SIZE] / sum(units.values())


def numbers(outcome) -> tuple:
    return (
        outcome.lost_units_dest,
        outcome.lost_units_donor,
        outcome.leftover_units_dest,
        outcome.leftover_units_donor,
    )


def test_folders_hold_their_contracts_with_unique_ids() -> None:
    for folder in FOLDERS:
        records = load(folder)
        assert records, folder
        ids = [(type(r).__name__, r.id) for r in records]
        assert len(ids) == len(set(ids)), folder


def test_stock_facts_are_sourced_and_match_the_exported_quantities() -> None:
    facts = of(StockFact)
    assert {f.basis for f in facts} == {"on_hand", "sellable", "atp"}
    assert {(f.location_id, f.sku) for f in facts} == {
        (location, sku) for location in (STORE, DONOR, DC) for sku in SIZES
    }
    ean = {r["sku_size"]: r["ean"] for r in read_csv(MASTER / "sku_size_ean.csv")}
    eod = read_csv(STOCK_DIR / "stock_eod_2026-10-08.csv")
    atp = {r["MATNR"]: r for r in read_csv(ATP) if r["WERKS"] == DC and r["J_3ASIZE"] == SIZE}
    for fact in facts:
        assert fact.source_refs == (fact.source_ref,)
        assert fact.source_ref.uri.startswith("dataset://") and fact.source_ref.locator
        assert fact.snapshot_at == fact.available_at
        assert fact.ean == ean[f"{fact.sku}-{SIZE}"]
        if fact.location_id == DC:
            row = atp[fact.sku.replace("-", "")]
            column = "LABST_0001" if fact.basis == "on_hand" else "ATP_NOW"
            expected: float | None = float(row[column])
            assert fact.snapshot_at.date() == date.fromisoformat(row["SNAPSHOT"][:10])
            assert fact.reservations_included is (fact.basis == "atp")
        else:
            (row,) = [
                r
                for r in eod
                if (r["store_id"], r["sku"], r["size"]) == (fact.location_id, fact.sku, SIZE)
            ]
            expected = float(row["on_hand"]) if fact.basis == "on_hand" else None
            assert fact.snapshot_at.date() == date(2026, 10, 8)
            assert fact.reservations_included is (False if fact.basis == "on_hand" else None)
        assert fact.qty == expected, fact.id
        if fact.basis == "sellable":  # no store-level sellable export: unknown, not zero
            assert fact.qty is None and fact.availability_basis.startswith("no_store_level")


def test_options_reference_existing_inputs_and_are_available_with_the_case() -> None:
    for option in of(ActionOption):
        assert (option.run_id, option.scenario_id) == (FIXTURE_RUN_ID, FIXTURE_SCENARIO_ID)
        assert option.case_id == case().id
        assert option.valid_until == case().valid_until
        inputs = [resolve(r) for r in option.input_refs if r.kind not in EXTERNAL_KINDS]
        assert inputs, option.id
        assert option.available_at == max(i.available_at for i in inputs)
        for input_ in inputs:  # every input's provenance travels with the option
            assert set(input_.source_refs) <= set(option.source_refs), (option.id, input_.id)
        assert option.forecast_ref == ArtifactRef(
            kind="ForecastAdjustment", id=forecast().id, version=forecast().version
        )
        keys = sorted(f"{r.kind}:{r.id}@{r.version}" for r in option.input_refs)
        digest = hashlib.sha256("\n".join(keys).encode()).hexdigest()
        assert option.input_version_hash == f"sha256:{digest}", option.id


def test_each_option_covers_the_rfc_checks_and_its_kind() -> None:
    crosswalk = {r["store_id"]: r["sap_plant_werks"] for r in read_csv(CROSSWALK)}
    ean = {r["sku_size"]: r["ean"] for r in read_csv(MASTER / "sku_size_ean.csv")}
    donor_min = float(
        next(r for r in read_csv(MIN_PRES) if (r["store"], r["category"]) == (DONOR, "Knitwear"))[
            "min_pres_per_core_size"
        ]
    )
    for option in of(ActionOption):
        names = [c.name for c in option.checks]
        assert len(names) == len(set(names)), option.id
        assert option.assumptions and option.rationale
        if option.kind in MOVEMENTS:
            assert option.legs, option.id
            assert MANDATORY_CHECKS <= set(names), sorted(MANDATORY_CHECKS - set(names))
            assert any(c.mandatory for c in option.checks)
            for leg in option.legs:
                assert_movement_leg(leg, crosswalk, ean)
        else:  # informational options move nothing (RFC §4.10)
            assert not option.legs, option.id
    transfer = everything()[("ActionOption", "opt-d1-mil01-mil02-999-m-q2")]
    (leg,) = transfer.legs
    (donor_stock,) = [
        f.qty
        for f in of(StockFact)
        if (f.location_id, f.sku, f.size, f.basis) == (DONOR, SKU, SIZE, "on_hand")
    ]
    # Quantity is limited by policy, not chosen by a model: donor stock minus its minimum.
    assert donor_stock is not None
    assert leg.qty == donor_stock - donor_min == 2


def plant(location: str, crosswalk: dict) -> str:
    # A DC is its own SAP plant, so it is not in the store crosswalk.
    return crosswalk.get(location, location)


def assert_movement_leg(leg: Leg, crosswalk: dict, ean: dict) -> None:
    lane = lanes()[leg.lane_id]
    assert {lane["origin"], lane["dest"]} == {
        plant(leg.origin, crosswalk),
        plant(leg.dest, crosswalk),
    }
    assert leg.dest == STORE and leg.origin != leg.dest
    assert leg.sku == SKU and leg.size == SIZE
    assert leg.ean == ean[f"{leg.sku}-{SIZE}"]
    assert leg.pickup_at <= leg.eta_at <= leg.sellable_at
    assert leg.cost_eur == pytest.approx(
        float(lane["cost_fixed_eur"]) + float(lane["cost_per_unit_eur"]) * leg.qty
    )
    assert lane["customs_required"] == "N"  # cross-border stays out of the MVP (RFC §4.10)


def test_blocked_move_and_feasible_move_have_the_documented_check_outcomes() -> None:
    movements = [o for o in of(ActionOption) if o.kind in MOVEMENTS]
    assert {o.kind for o in movements} == {"transfer", "replenish_dc"}
    (blocked,) = [o for o in movements if any(c.mandatory and c.status == "fail" for c in o.checks)]
    (feasible,) = [
        o for o in movements if not any(c.mandatory and c.status == "fail" for c in o.checks)
    ]
    assert blocked.kind == "replenish_dc" and blocked.legs[0].origin == DC
    assert {c.name for c in blocked.checks if c.status == "fail"} == {
        "availability_atp",
        "eta_required_by",
    }
    # The feasible move is mechanically possible, but the donor's sellable state is not exported.
    assert {c.name for c in feasible.checks if c.mandatory and c.status == "unknown"} == {
        "reservations",
        "quality_hold",
    }
    assert not any(o.recommended for o in movements)
    (recommended,) = [o for o in of(ActionOption) if o.recommended]
    assert recommended.kind == "verify_stock" and recommended.outcomes is None


def test_outcomes_follow_the_formula_and_the_ranking_of_the_move() -> None:
    hold = everything()[("ActionOption", "opt-d1-mil01-hold")]
    transfer = everything()[("ActionOption", "opt-d1-mil01-mil02-999-m-q2")]
    assert {o.scenario_id for o in hold.outcomes} == {"low", "base", "high"}
    hold_out = {o.scenario_id: o for o in hold.outcomes}
    baseline = {o.scenario_id: o for o in transfer.baseline_outcomes}
    move_out = {o.scenario_id: o for o in transfer.outcomes}
    for scenario in hold_out:  # no overlay: every scenario coincides with the hold baseline
        assert numbers(baseline[scenario]) == numbers(hold_out[scenario])
        assert numbers(move_out[scenario]) == numbers(move_out["base"])
    (leg,) = transfer.legs
    base, moved = hold_out["base"], move_out["base"]
    # Destination: no stock and no arrival on hold; the leg makes exactly `qty` units servable.
    assert moved.lost_units_dest == pytest.approx(base.lost_units_dest - leg.qty, abs=1e-3)
    # Donor: keeps stock minus qty and its own size-M demand is documented, so its loss is too.
    assert moved.lost_units_donor > base.lost_units_donor
    assert moved.leftover_units_donor == pytest.approx(
        max(0.0, base.leftover_units_donor - leg.qty), abs=1e-3
    )
    assert moved.transport_cost_eur == leg.cost_eur > 0
    # The move reduces total unserved units, but by less than the units it moves.
    gain = (base.lost_units_dest + base.lost_units_donor) - (
        moved.lost_units_dest + moved.lost_units_donor
    )
    assert 0 < gain < leg.qty


def test_hold_losses_are_the_forecast_of_the_fixture_run_times_the_size_curve() -> None:
    hold = everything()[("ActionOption", "opt-d1-mil01-hold")]
    series = [day.baseline for day in forecast().series]
    assert len(series) == 7
    (base,) = [o for o in hold.outcomes if o.scenario_id == "base"]
    assert base.lost_units_dest == pytest.approx(sum(series) * size_share(STORE), abs=1e-2)
    assert base.lost_units_dest == pytest.approx(2.409, abs=1e-3)
    assert size_share(DONOR) == pytest.approx(12 / 39)


def test_trace_follows_the_rfc_tool_allowlist_and_ends_on_the_recommendation() -> None:
    (trace,) = of(AgentTrace)
    assert (trace.run_id, trace.scenario_id) == (FIXTURE_RUN_ID, FIXTURE_SCENARIO_ID)
    assert trace.case_id == CASE_ID and trace.mode == "fixture"
    assert trace.fallback_used is True  # RFC §4.8.1: the deterministic path records it
    assert trace.tokens_in is None and trace.tokens_out is None
    assert [s.tool for s in trace.steps] == [
        "get_case_evidence",
        "get_available_stock",
        "get_lane_and_eta",
        "evaluate_options",
        "finish",
    ]
    assert {s.tool for s in trace.steps} <= TOOLS
    for step in trace.steps:
        assert step.duration_ms >= 0
        for ref in (*step.input_refs, *step.output_refs):
            if ref.kind not in EXTERNAL_KINDS:
                resolve(ref)
    (recommended,) = [o for o in of(ActionOption) if o.recommended]
    finish = trace.steps[-1]
    assert finish.arguments["option_id"] == recommended.id
    assert finish.arguments["status"] == "verify"
    assert "verify_stock" in trace.outcome
    inputs = [resolve(r) for r in trace.input_refs if r.kind not in EXTERNAL_KINDS]
    assert trace.available_at == max(r.available_at for r in inputs)
    stock_step = trace.steps[1]
    assert {f.basis for f in map(resolve, stock_step.output_refs)} == {"on_hand", "atp"}


def test_only_dev_stores_and_no_look_ahead() -> None:
    split = yaml.safe_load((ROOT / "config" / "eval_split.yaml").read_text(encoding="utf-8"))
    allowed = set(split["dev"])
    for fact in of(StockFact):
        if fact.location_id != DC:
            assert fact.location_id in allowed
    for option in of(ActionOption):
        for leg in option.legs:
            assert {leg.origin, leg.dest} <= allowed | {DC}
    as_of = max(r.available_at for r in everything().values() if r.available_at is not None)
    assert as_of == case().available_at  # the case is the last input of this family
    for folder in FOLDERS:
        for path in (FIXTURES / folder).glob("*.json"):
            text = path.read_text(encoding="utf-8").lower()
            for store in split["holdout"]:
                assert store.lower() not in text, (path.name, store)


def test_the_loader_accepts_the_new_folders() -> None:
    paths, records = read_fixtures(FIXTURES)
    names = {p.relative_to(FIXTURES).as_posix() for p in paths}
    for folder in FOLDERS:
        assert any(name.startswith(f"{folder}/") for name in names), folder
    assert {type(r).__name__ for r in records} >= {"StockFact", "ActionOption", "AgentTrace"}
