"""Build the DATA-01c fixtures: stock facts, options and one agent trace for D1.

Run from the repo root after DATA-01b (rewrites `data/fixtures/{stock,options,traces}/`):

    backend/.venv/bin/python data/fixtures/build_data01c.py

What it is. Hand-labelled records for the seams lane E and WEB-05 build against: `act.options`
(ACT-02), approval (ACT-03), `ag.investigator` (AG-03) and the case detail (WEB-05). They are
what a correct engine should return for case `case-mil01-i10919b00011-20261008` at D, not model
output. See `data/fixtures/README.md` for what each record exercises.

Every number is computed here from `generated/sources/`, so the fixtures can be re-derived instead
of trusted:

- demand per day: colour `sales_baseline` of the vintage admissible at D (run date + 1 day 06:00
  local, RFC §4.3) split `/7` over the days of its ISO week (RFC §4.9 step 1: on a partial week
  only the horizon days are selected, the week total is not redistributed);
- size curve: units of size M as a share of the colour's units sold in the surveyed window, on
  days when size M was on hand at opening (RFC §4.9 "raccordo con la taglia"). The same method is
  applied to the donor, so donor protection is size-aware;
- per location and day: `available = stock_(h-1) + sellable_arrivals_h`, `served = min(demand,
  available)`, `lost = demand - served`, `leftover = available - served` (RFC §4.10). A leg
  arrives on its `sellable_at` day, before the sales; the donor's stock drops at pickup.

Only dev stores (`MIL01`, `MIL02`), the Italian DC `IT10` and `generated/sources/`. `ROM01`, also
addressed by the source email, is a hold-out store: no ROM01 record appears here (RFC §5.1).
No look-ahead: every record is available at D 10:35 Europe/Rome (the case's instant) or earlier;
later facts (the 2026-10-09 IBT request, the 2026-10-12 ATP projection) are not used.
"""

import csv
import hashlib
import json
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from tesseract.core.contracts import (
    ActionOption,
    AgentStep,
    AgentTrace,
    ArtifactRef,
    Case,
    Check,
    ForecastAdjustment,
    Leg,
    ScenarioOutcome,
    SourceRef,
    StockFact,
)
from tesseract.core.contracts.common import SourceRecord

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "generated" / "sources"
OUT = ROOT / "data" / "fixtures"
MASTER = SOURCES / "erp" / "master_data"
STOCK_DIR = SOURCES / "erp" / "inventory" / "store_stock_daily"
POS_DIR = SOURCES / "erp" / "sales" / "pos_lines"
FCST = SOURCES / "erp" / "forecast" / "sku_store_weekly"
ATP = SOURCES / "systems" / "warehouse" / "atp" / "ATP_projection_20261005.csv"
RESERVATIONS = SOURCES / "systems" / "warehouse" / "reservations" / "ZRESV_reservations_export.csv"
QUALITY = SOURCES / "systems" / "warehouse" / "quality" / "QMEL_quality_notifications.csv"
LANES = SOURCES / "systems" / "logistics" / "lane_matrix_lead_time_cost.csv"
IBT = SOURCES / "systems" / "logistics" / "ibt_transfers_storelink_export.csv"
CROSSWALK = SOURCES / "systems" / "reference" / "store_code_crosswalk_MDM.csv"
MIN_PRES = SOURCES / "systems" / "planning" / "min_presentation_by_store_category.csv"

VERSION = "v1"
RUN_ID = "fixture"
SCENARIO_ID = "historical"
COMPUTED_AT = datetime(2026, 10, 22, 12, 0, tzinfo=UTC)
PRODUCER = "fixture.data01c"
PRODUCER_VERSION = "1"
SCENARIOS = ("low", "base", "high")  # RFC §4.9: no overlay here, so all three coincide

STORE = "MIL01"  # destination: Milano Montenapoleone
DONOR = "MIL02"  # only Italian dev store with size M on hand (Rinascente Duomo)
DC = "IT10"  # DC Castel San Giovanni, the store's supplying DC (MDM crosswalk)
SKUS = {"999": "I10919B00011-999", "742": "I10919B00011-742"}
STYLE = "I10919B00011"
SIZE = "M"
D = date(2026, 10, 9)  # case day: the source email of 2026-10-09 10:35 local
CASE_ID = "case-mil01-i10919b00011-20261008"
TZ = ZoneInfo("Europe/Rome")
HORIZON = [D + timedelta(days=k) for k in range(1, 8)]  # D+1..D+7, RFC §4.9
POS_WEEKS = (36, 37, 38, 39, 40)  # complete weeks before D, all out by 2026-10-05 06:00 local
CURVE_FIRST, CURVE_LAST = date(2026, 8, 31), date(2026, 10, 4)  # 2026-W36 .. 2026-W40
BASIS_TOKEN = {"on_hand": "onhand", "sellable": "sellable", "atp": "atp"}
OPENING, CLOSING = time(10, 0), time(19, 0)  # store opening and closing, local time
WEEKDAYS = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4, "SAT": 5, "SUN": 6}


# --- reading the sources ---------------------------------------------------------------


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def file_ref(path: Path, locator: str | None = None) -> SourceRef:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    uri = "dataset://" + path.relative_to(SOURCES).as_posix()
    return SourceRef(uri=uri, content_hash=f"sha256:{digest}", locator=locator)


def stock_csv(day: date) -> Path:
    return STOCK_DIR / f"stock_eod_{day.isoformat()}.csv"


def pos_csv(week: int) -> Path:
    return POS_DIR / f"pos_lines_2026-W{week}.csv"


def ref(record: SourceRecord) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


def merge_sources(*groups) -> tuple[SourceRef, ...]:
    return tuple(dict.fromkeys(s for group in groups for s in group))


def derived(inputs: list[SourceRecord], extra_sources=(), extra_refs=()) -> dict:
    """Common fields: available at the latest input, never before any of them."""
    return {
        "version": VERSION,
        "available_at": max(r.available_at for r in inputs if r.available_at is not None),
        "availability_basis": "max_input_available_at",
        "source_refs": merge_sources(*(r.source_refs for r in inputs), extra_sources),
        "run_id": RUN_ID,
        "scenario_id": SCENARIO_ID,
        "computed_at": COMPUTED_AT,
        "input_refs": (*(ref(r) for r in inputs), *extra_refs),
        "producer": PRODUCER,
        "producer_version": PRODUCER_VERSION,
    }


def option_fields(inputs: list[SourceRecord], extra_sources=()) -> dict:
    """`derived()` plus the version hash of everything the option was computed from.

    The hash covers the stored inputs and the source rows/files behind them, so an approval
    against it is stale as soon as either changes (RFC §4.10 approval).
    """
    fields = derived(inputs, extra_sources=extra_sources)
    fields["input_version_hash"] = input_version_hash(
        [*fields["input_refs"], *(as_ref(item) for item in fields["source_refs"])]
    )
    return fields


def input_version_hash(refs) -> str:
    keys = sorted(f"{r.kind}:{r.id}@{r.version}" for r in refs)
    return "sha256:" + hashlib.sha256("\n".join(keys).encode()).hexdigest()


def local_instant(day: date, at: time) -> datetime:
    """`day` at local time `at` in the store's time zone, serialized in UTC."""
    return datetime.combine(day, at, TZ).astimezone(UTC)


def pickup_weekdays(spec: str) -> set[int]:
    """A lane `pickup_days` value (`MON-SAT`, `MON-FRI`) as ISO weekdays."""
    first, _, last = spec.partition("-")
    assert first in WEEKDAYS and last in WEEKDAYS, spec
    return set(range(WEEKDAYS[first], WEEKDAYS[last] + 1))


def next_pickup_day(day: date, spec: str) -> date:
    """First day on or after `day` when the lane loads (RFC §4.10 `decision_due_at`)."""
    allowed = pickup_weekdays(spec)
    while day.weekday() not in allowed:
        day += timedelta(days=1)
    return day


class Sources:
    """The source rows this fixture family cites, read once and checked against the story."""

    def __init__(self) -> None:
        self.ean = {r["sku_size"]: r["ean"] for r in read_csv(MASTER / "sku_size_ean.csv")}
        self.styles = {r["style_code"]: r for r in read_csv(MASTER / "styles.csv")}
        self.stores = {r["store_id"]: r for r in read_csv(MASTER / "stores.csv")}
        self.assortment = {
            (r["store_id"], r["sku"]) for r in read_csv(MASTER / "store_assortment.csv")
        }
        self.werks = {r["store_id"]: r["sap_plant_werks"] for r in read_csv(CROSSWALK)}
        category = self.styles[STYLE]["category"]
        self.min_pres = {
            r["store"]: r for r in read_csv(MIN_PRES) if r["category"] == category
        }
        self.lanes = {(r["origin"], r["dest"]): r for r in read_csv(LANES)}
        self.fcst = read_csv(FCST / "fcst_sku_store_run_2026-10-05.csv")
        self.atp = [r for r in read_csv(ATP) if r["WERKS"] == DC]
        self.reservations = read_csv(RESERVATIONS)
        self.quality = read_csv(QUALITY)
        self.ibt = read_csv(IBT)
        self._on_hand: dict[tuple[str, str, str, date], float] = {}

    def units(self, store: str, sku: str, size: str, day: date) -> float:
        key = (store, sku, size, day)
        if key not in self._on_hand:
            for row in read_csv(stock_csv(day)):
                self._on_hand[(row["store_id"], row["sku"], row["size"], day)] = float(
                    row["on_hand"]
                )
        return self._on_hand[key]

    def atp_row(self, colour: str) -> dict[str, str]:
        matnr = SKUS[colour].replace("-", "")
        (row,) = [r for r in self.atp if r["MATNR"] == matnr and r["J_3ASIZE"] == SIZE]
        return row

    def weekly(self, store: str, sku: str, week_start: date) -> float:
        (row,) = [
            r
            for r in self.fcst
            if r["store_id"] == store
            and r["sku"] == sku
            and date.fromisoformat(r["week_start"]) == week_start
        ]
        return float(row["fcst_units"])


# --- the two pieces of arithmetic behind the options -----------------------------------


def size_shares(src: Sources, store: str, sku: str) -> tuple[dict[str, float], dict[str, int]]:
    """RFC §4.9 "raccordo con la taglia": colour units by size on days size M opened.

    Two traps of the POS export: `qty` is already signed (a `RETURN` line carries -1) and
    some weeks repeat whole lines verbatim, so `qty` is added as it comes and exact
    duplicates are counted once. A day enters the curve only if size M was on hand at
    opening, because a size that is sold out cannot sell.
    """
    units: dict[str, int] = {}
    seen: set[tuple[tuple[str, str], ...]] = set()
    for week in POS_WEEKS:
        for row in read_csv(pos_csv(week)):
            day = date.fromisoformat(row["business_date"])
            if not (CURVE_FIRST <= day <= CURVE_LAST):
                continue
            if row["store_id"] != store or row["sku"] != sku:
                continue
            key = tuple(sorted(row.items()))
            if key in seen:  # the export repeats the line: one sale, not two
                continue
            seen.add(key)
            if src.units(store, sku, SIZE, day - timedelta(days=1)) <= 0:
                continue
            units[row["size"]] = units.get(row["size"], 0) + int(row["qty"])
    total = sum(units.values())
    assert total > 0 and all(qty >= 0 for qty in units.values())
    return {size: qty / total for size, qty in units.items()}, units


def daily_demand(src: Sources, store: str, sku: str, share: float) -> dict[date, float]:
    """Colour forecast / days of its week, times the size share (RFC §4.9 steps 1 and 8)."""
    return {
        day: src.weekly(store, sku, day - timedelta(days=day.weekday())) / 7 * share
        for day in HORIZON
    }


def simulate(
    start: float, arrivals: dict[date, float], demand: dict[date, float]
) -> tuple[float, float]:
    """`lost`, `leftover` over the horizon (RFC §4.10): recursive stock, no backlog, no reset."""
    stock, lost = start, 0.0
    for day in sorted(demand):
        stock += arrivals.get(day, 0.0)
        served = min(demand[day], stock)
        lost += demand[day] - served
        stock -= served
    return lost, stock


def rounded(value: float) -> float:
    return round(value, 3)


def fmt(value: float) -> str:
    return f"{value:.2f}"


# --- records ---------------------------------------------------------------------------


def stock_fact(
    src: Sources,
    location: str,
    colour: str,
    basis: str,
    qty: float | None,
    day: date,
    at: time,
    source_ref: SourceRef,
    availability_basis: str,
    reserves: bool | None,
    quality: bool | None,
) -> StockFact:
    sku_size = f"{SKUS[colour]}-{SIZE}"
    return StockFact(
        id=f"stock-{location}-{SKUS[colour]}-{SIZE}-{BASIS_TOKEN[basis]}-"
        f"{day.strftime('%Y%m%d')}".lower(),
        version=VERSION,
        available_at=local_instant(day, at),
        availability_basis=availability_basis,
        source_refs=(source_ref,),
        source_ref=source_ref,
        location_id=location,
        sku=SKUS[colour],
        size=SIZE,
        ean=src.ean[sku_size],
        snapshot_at=local_instant(day, at),
        qty=qty,
        basis=basis,  # type: ignore[arg-type]
        reservations_included=reserves,
        quality_holds_included=quality,
    )


def build_stock(src: Sources) -> list[StockFact]:
    """Visible stock at D: EOD 2026-10-08 for the stores, the 2026-10-05 ATP projection for IT10."""
    facts: list[StockFact] = []
    eod = D - timedelta(days=1)
    eod_at = time(23, 59, 59)  # the EOD snapshot is the end of the local day
    for colour in SKUS:
        for store in (STORE, DONOR):
            locator = (
                f"store_id={store};sku={SKUS[colour]};size={SIZE};"
                f"snapshot_date={eod.isoformat()}"
            )
            facts.append(
                stock_fact(
                    src,
                    store,
                    colour,
                    "on_hand",
                    src.units(store, SKUS[colour], SIZE, eod),
                    eod,
                    eod_at,
                    file_ref(stock_csv(eod), f"{locator};column=on_hand"),
                    "erp_store_eod_snapshot",
                    False,
                    False,
                )
            )
            # The ERP export has no store-level reservations, holds or sellable quantity.
            facts.append(
                stock_fact(
                    src,
                    store,
                    colour,
                    "sellable",
                    None,
                    eod,
                    eod_at,
                    file_ref(stock_csv(eod), locator),
                    "no_store_level_sellable_export",
                    None,
                    None,
                )
            )
        row = src.atp_row(colour)
        snapshot = datetime.strptime(row["SNAPSHOT"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
        locator = f"WERKS={DC};MATNR={row['MATNR']};J_3ASIZE={SIZE}"
        facts.append(
            stock_fact(
                src,
                DC,
                colour,
                "on_hand",
                float(row["LABST_0001"]),
                snapshot.date(),
                snapshot.time(),
                file_ref(ATP, f"{locator};column=LABST_0001"),
                "sap_stock_projection",
                False,
                False,
            )
        )
        facts.append(
            stock_fact(
                src,
                DC,
                colour,
                "atp",
                float(row["ATP_NOW"]),
                snapshot.date(),
                snapshot.time(),
                file_ref(ATP, f"{locator};column=ATP_NOW"),
                "warehouse_atp_projection",
                True,
                True,
            )
        )
    return facts


def outcome(
    scenario: str,
    dest_lost: float | None,
    donor_lost: float | None,
    dest_left: float | None,
    donor_left: float | None,
    cost: float | None,
    demand_basis: str,
    size_basis: str,
) -> ScenarioOutcome:
    return ScenarioOutcome(
        scenario_id=scenario,
        lost_units_dest=dest_lost,
        lost_units_donor=donor_lost,
        leftover_units_dest=dest_left,
        leftover_units_donor=donor_left,
        transport_cost_eur=cost,
        demand_basis=demand_basis,
        size_allocation_basis=size_basis,
    )


def as_ref(evidence) -> ArtifactRef:
    """Evidence of a check: a stored artifact, or a source file that has no contract.

    A source file has no record version, so the reference carries the dataset uri plus the row
    locator as id and the file content hash as version (the convention `ForecastVintage` uses for
    source rows). Keeping the locator in the id keeps two rows of the same file apart.
    """
    if isinstance(evidence, ArtifactRef):
        return evidence
    if isinstance(evidence, SourceRecord):
        return ref(evidence)
    if isinstance(evidence, SourceRef):
        ident = evidence.uri if evidence.locator is None else f"{evidence.uri}#{evidence.locator}"
        return ArtifactRef(kind="SourceFile", id=ident, version=evidence.content_hash)
    raise TypeError(evidence)


def check(name: str, status: str, mandatory: bool, detail: str, *evidence) -> Check:
    return Check(
        name=name,
        status=status,  # type: ignore[arg-type]
        mandatory=mandatory,
        detail=detail,
        source_refs=tuple(dict.fromkeys(as_ref(item) for item in evidence)),
    )


def main() -> None:
    src = Sources()
    case = next(
        Case.model_validate(rec["payload"])
        for rec in json.loads((OUT / "cases" / f"{CASE_ID}.json").read_text(encoding="utf-8"))
        if rec["kind"] == "Case"
    )
    # Only the black 999 forecast is an option input: the 742 facts are counts from the EOD
    # export, so the 742 forecast is not loaded (an unused input would blur `available_at`).
    (forecast_rec,) = [
        rec
        for rec in json.loads(
            (OUT / "forecast" / "fc-mil01-i10919b00011-999-20261010.json").read_text(
                encoding="utf-8"
            )
        )
        if rec["kind"] == "ForecastAdjustment"
    ]
    forecast = ForecastAdjustment.model_validate(forecast_rec["payload"])
    # The vague unmet demand lives in the case's observation; the POS export cannot show it.
    (unmet_obs,) = [item for item in case.supporting if item.id.endswith("unmet-demand")]

    # The story, checked against the sources: D1 says size M is gone at MIL01 in both colours,
    # MIL02 can spare size M only in black, and the DC cannot send any before the end of October.
    eod = D - timedelta(days=1)
    before = D - timedelta(days=2)
    assert src.units(STORE, SKUS["999"], SIZE, eod) == 0
    assert src.units(STORE, SKUS["742"], SIZE, eod) == 0
    assert src.units(DONOR, SKUS["999"], SIZE, eod) == 3
    assert src.units(DONOR, SKUS["742"], SIZE, eod) == 0
    assert src.units(STORE, SKUS["999"], SIZE, before) == 8
    for store in (STORE, DONOR):
        assert not src.stores[store]["closed_dow"]  # open every day, so /7 splits a week
        for colour in SKUS:
            assert (store, SKUS[colour]) in src.assortment
    for colour in SKUS:
        row = src.atp_row(colour)
        assert float(row["LABST_0001"]) == 0 and float(row["ATP_NOW"]) == 0
        assert date.fromisoformat(row["NEXT_RCPT_DATE"]) == date(2026, 10, 30)
    (backorder,) = [
        r
        for r in src.reservations
        if r["MATNR"] == SKUS["999"].replace("-", "") and r["J_3ASIZE"] == SIZE
    ]
    assert backorder["WERKS"] == DC and backorder["QTY"] == "4"
    assert backorder["REQUESTER"] == f"Store {src.werks[STORE]}"  # 1001
    assert not [r for r in src.quality if r["MATNR"].startswith(STYLE)]
    # The IBT requests for this size all arrive after D 10:35 (the first one at 17:32): they are
    # not inputs of these options and must not be read back into them (no look-ahead).
    later = [r for r in src.ibt if r["sku"].startswith(SKUS["999"])]
    assert later and all(
        datetime.fromisoformat(r["created_at_local"]) > datetime.combine(D, time(10, 35))
        for r in later
    ), later

    dest_before = src.units(STORE, SKUS["999"], SIZE, before)
    donor_before = src.units(DONOR, SKUS["999"], SIZE, before)
    bridged = [
        row
        for row in read_csv(pos_csv(41))
        if (row["store_id"], row["sku"], row["size"], row["business_date"])
        == (STORE, SKUS["999"], SIZE, eod.isoformat())
    ]
    (bridged_sale,) = [row for row in bridged if row["line_type"] == "SALE"]
    donor_eod_sales = [
        row
        for row in read_csv(pos_csv(41))
        if (row["store_id"], row["sku"], row["size"], row["business_date"])
        == (DONOR, SKUS["999"], SIZE, eod.isoformat())
        and row["line_type"] == "SALE"
    ]
    bridge_gap = dest_before - src.units(STORE, SKUS["999"], SIZE, eod) - len(bridged)

    facts = build_stock(src)
    by_key = {(f.location_id, f.sku, f.basis): f for f in facts}
    dest_on_hand = by_key[(STORE, SKUS["999"], "on_hand")]
    donor_on_hand = by_key[(DONOR, SKUS["999"], "on_hand")]
    dest_sellable = by_key[(STORE, SKUS["999"], "sellable")]
    donor_sellable = by_key[(DONOR, SKUS["999"], "sellable")]
    atp = by_key[(DC, SKUS["999"], "atp")]
    dc_on_hand = by_key[(DC, SKUS["999"], "on_hand")]

    # --- the numbers the options carry (RFC §4.9/§4.10) -------------------------------
    dest_share, dest_units = size_shares(src, STORE, SKUS["999"])
    donor_share, donor_units = size_shares(src, DONOR, SKUS["999"])
    p_dest, p_donor = dest_share[SIZE], donor_share[SIZE]
    demand_dest = daily_demand(src, STORE, SKUS["999"], p_dest)
    demand_donor = daily_demand(src, DONOR, SKUS["999"], p_donor)

    hold_dest_lost, hold_dest_left = simulate(0.0, {}, demand_dest)
    hold_donor_lost, hold_donor_left = simulate(3.0, {}, demand_donor)

    transfer_lane = src.lanes[(src.werks[DONOR], src.werks[STORE])]
    dc_lane = src.lanes[(DC, src.werks[STORE])]
    donor_min = src.min_pres[DONOR]
    store_min = src.min_pres[STORE]
    donor_units_eod = src.units(DONOR, SKUS["999"], SIZE, eod)
    donor_demand_total = sum(demand_donor.values())
    # Availability and the minimum at dispatch cap the quantity at 2 (the email asks for 1-2);
    # donor protection over the horizon is a separate check and it does not pass (see below).
    q_transfer = int(donor_units_eod - float(donor_min["min_pres_per_core_size"]))
    sellable = HORIZON[0]  # the leg arrives at closing on D: sellable from the next opening
    transfer_dest_lost, transfer_dest_left = simulate(
        0.0, {sellable: float(q_transfer)}, demand_dest
    )
    transfer_donor_lost, transfer_donor_left = simulate(
        float(donor_units_eod - q_transfer), {}, demand_donor
    )
    donor_after_move = float(donor_units_eod - q_transfer)
    # Stock the donor would need to serve its own horizon demand and still hold its minimum.
    donor_deficit = (
        donor_demand_total + float(donor_min["min_pres_per_core_size"]) - donor_units_eod
    )
    assert donor_deficit > 0
    cumulative, donor_sold_out = 0.0, HORIZON[-1]
    for day in HORIZON:
        cumulative += demand_donor[day]
        if cumulative > donor_after_move:
            donor_sold_out = day
            break

    q_dc = int(backorder["QTY"])  # unit count MIL01 already has a backorder line for
    dc_dest_lost, dc_dest_left = simulate(0.0, {}, demand_dest)  # no arrival inside the horizon

    transfer_cost = round(
        float(transfer_lane["cost_fixed_eur"])
        + float(transfer_lane["cost_per_unit_eur"]) * q_transfer,
        2,
    )
    dc_cost = round(
        float(dc_lane["cost_fixed_eur"]) + float(dc_lane["cost_per_unit_eur"]) * q_dc, 2
    )
    assert float(donor_min["min_pres_per_core_size"]) == 1 and SIZE in donor_min["core_sizes"]
    assert float(store_min["min_pres_per_core_size"]) == 2 and SIZE in store_min["core_sizes"]
    assert donor_units_eod - q_transfer >= float(donor_min["min_pres_per_core_size"])
    # The donor's own demand over the horizon exceeds what a dispatch of q would leave: RFC §4.10
    # protection cannot hold for any positive integer, which the check below records as `fail`.
    assert donor_demand_total > donor_units_eod - q_transfer
    assert transfer_lane["ibt_allowed"] == "Y" and transfer_lane["customs_required"] == "N"
    assert float(transfer_lane["transit_days_contract"]) == 0
    assert transfer_lane["observed_n"] == "0"  # same-day courier: no observed history yet

    matnr = SKUS["999"].replace("-", "")
    receipt = src.atp_row("999")
    receipt_units = int(float(receipt["NEXT_RCPT_QTY"]))
    receipt_day = date.fromisoformat(receipt["NEXT_RCPT_DATE"])
    projection_day = date.fromisoformat(receipt["SNAPSHOT"][:10])
    projection_lag = (D - projection_day).days
    backorder_qty = int(backorder["QTY"])
    backorder_needed = date.fromisoformat(backorder["NEEDED"])
    atp_sources = (file_ref(ATP, f"WERKS={DC};MATNR={matnr};J_3ASIZE={SIZE}"),)
    resv_sources = (
        file_ref(RESERVATIONS, f"RSNUM={backorder['RSNUM']};WERKS={DC};J_3ASIZE={SIZE}"),
    )
    bridge_sources = (
        file_ref(stock_csv(before), f"store_id={STORE};sku={SKUS['999']};size={SIZE}"),
        file_ref(stock_csv(eod), f"store_id={STORE};sku={SKUS['999']};size={SIZE}"),
        file_ref(pos_csv(41), f"store_id={STORE};sku={SKUS['999']};business_date<={eod}"),
    )
    ean = src.ean[f"{SKUS['999']}-{SIZE}"]

    demand_basis = (
        "colour sales_baseline of forecast vintage 2026-10-05 (run date + 1 day 06:00 local), "
        "split /7 over its ISO week; scenarios equal the baseline (vague unmet demand gives no "
        "numeric uplift), so low, base and high coincide (RFC §4.9 steps 1, 5 and 7)"
    )
    size_basis = (
        f"MIL01 {SKUS['999']}: size {SIZE} is {dest_units[SIZE]}/{sum(dest_units.values())} = "
        f"{p_dest:.4f} of the colour units sold {CURVE_FIRST}..{CURVE_LAST} on days it opened in "
        f"stock; donor MIL02 curve {donor_units[SIZE]}/{sum(donor_units.values())} = "
        f"{p_donor:.4f} (RFC §4.9 raccordo con la taglia)"
    )
    no_arrival = (
        f"no sellable arrival inside D+1..D+7: the DC receipt is {receipt_day.isoformat()}, so "
        "the destination's losses equal hold and no transport cost falls inside the horizon"
    )
    dc_counterpart = (
        "DC counterpart demand is not modelled from a source, so its losses stay unknown; the "
        "option is not a recommendation (RFC §4.10: insufficient data on a counterpart)"
    )

    curve_sources = tuple(
        file_ref(pos_csv(week), f"store_id={STORE};business_date<={CURVE_LAST}")
        for week in POS_WEEKS
    )
    donor_curve_sources = tuple(
        file_ref(pos_csv(week), f"store_id={DONOR};business_date<={CURVE_LAST}")
        for week in POS_WEEKS
    )
    donor_demand_sources = (
        file_ref(
            FCST / "fcst_sku_store_run_2026-10-05.csv",
            f"store_id={DONOR};sku={SKUS['999']};run_date=2026-10-05",
        ),
    )
    donor_min_sources = (file_ref(MIN_PRES, f"WERKS={src.werks[DONOR]};category=Knitwear"),)
    store_min_sources = (file_ref(MIN_PRES, f"WERKS={src.werks[STORE]};category=Knitwear"),)
    lane_sources = (file_ref(LANES, f"lane_id={transfer_lane['lane_id']}"),)
    dc_lane_sources = (file_ref(LANES, f"lane_id={dc_lane['lane_id']}"),)

    # --- options ---------------------------------------------------------------------
    # Sensitivity of the curve: with a flat 1/6 share the destination's hold loss would differ,
    # but no option is recommended on the strength of the numbers (see the unknown checks), so a
    # different but admissible curve cannot flip the answer.
    flat_dest_lost, _ = simulate(
        0.0,
        {},
        {day: value / p_dest / len(dest_units) for day, value in demand_dest.items()},
    )
    curve_check = check(
        "size_curve",
        "pass",
        True,
        f"size {SIZE} is {p_dest:.1%} of the colour units sold {CURVE_FIRST}..{CURVE_LAST} on "
        f"the days it opened in stock ({dest_units[SIZE]}/{sum(dest_units.values())}); the five "
        f"complete POS weeks W{min(POS_WEEKS)}-W{max(POS_WEEKS)} were out before D, the shares "
        "sum to 1 and the colour total reconciles. Sensitivity: a flat "
        f"1/{len(dest_units)} curve would put the destination's hold loss at "
        f"{fmt(flat_dest_lost)} instead of {fmt(hold_dest_lost)}, and it changes no status "
        "(nothing is recommended on these numbers)",
        *curve_sources,
        *donor_curve_sources,
    )

    hold = ActionOption(
        id="opt-d1-mil01-hold",
        **option_fields(
            [case, forecast, dest_on_hand, dest_sellable],
            extra_sources=merge_sources(curve_sources, resv_sources),
        ),
        case_id=case.id,
        forecast_ref=ref(forecast),
        kind="hold",
        legs=(),
        checks=(
            curve_check,
            check(
                "demand_uplift",
                "not_applicable",
                False,
                "unmet demand is vague ('in continuazione'): no count, no unit uplift, scenarios "
                "stay on the baseline (RFC §4.9 step 5)",
                unmet_obs,
            ),
        ),
        outcomes=tuple(
            outcome(
                scenario,
                rounded(hold_dest_lost),
                rounded(hold_donor_lost),
                rounded(hold_dest_left),
                rounded(hold_donor_left),
                0.0,
                demand_basis,
                size_basis,
            )
            for scenario in SCENARIOS
        ),
        baseline_outcomes=None,
        assumptions=(
            f"starting stock is the EOD {eod.isoformat()} snapshot: {dest_on_hand.qty:.0f} units "
            f"of size {SIZE} at {STORE}, {donor_on_hand.qty:.0f} at {DONOR}, in both colours: "
            f"742 is {src.units(STORE, SKUS['742'], SIZE, eod):.0f} at {STORE} and "
            f"{src.units(DONOR, SKUS['742'], SIZE, eod):.0f} at {DONOR}, so black "
            f"carries the whole store loss (RFC §4.10 initial state)",
            f"the {backorder_qty} units MIL01 has on backorder at {DC} are not stock: ATP is 0 "
            f"until the {receipt_day.isoformat()} receipt",
            "hold is the ranking baseline: every movement is compared against these losses",
        ),
        valid_until=case.valid_until,  # type: ignore[arg-type]
        recommended=False,
        rationale=(
            f"no stock action: {fmt(hold_dest_lost)} units of size {SIZE} stay unserved at "
            f"{STORE} over D+1..D+7 while {DONOR} keeps {fmt(hold_donor_left)} units. It is the "
            "baseline for the other options, not a proposal: the store keeps asking for size M "
            "and the DC receipt is too late to help inside the horizon"
        ),
    )

    verify = ActionOption(
        id="opt-d1-mil01-verify-stock",
        **option_fields(
            [case, dest_on_hand, dest_sellable, donor_on_hand, donor_sellable, atp],
            extra_sources=merge_sources(curve_sources, resv_sources, atp_sources),
        ),
        case_id=case.id,
        forecast_ref=ref(forecast),
        kind="verify_stock",
        legs=(),
        checks=(
            check(
                "snapshot_bridge",
                "unknown",
                False,
                f"MIL01 {SKUS['999']} had {dest_before:.0f} units of size {SIZE} at EOD "
                f"{before.isoformat()} and {dest_on_hand.qty:.0f} at EOD {eod.isoformat()}, while "
                f"POS records {len(bridged)} sale of size {SIZE} on "
                f"{bridged_sale['ts_local']}: {bridge_gap:.0f} units are unaccounted for (no "
                "inbound, no IBT line, no return), so the last snapshot is not current stock",
                *bridge_sources,
            ),
            check(
                "donor_discrepancy",
                "unknown",
                False,
                f"MIL02 went from {donor_before:.0f} units of size {SIZE} at EOD "
                f"{before.isoformat()} to {donor_on_hand.qty:.0f} at EOD {eod.isoformat()} with "
                f"{len(donor_eod_sales)} size-{SIZE} sales on {eod.isoformat()}, so the "
                "arithmetic reconciles; store-level sellable quantity, reservations and quality "
                "holds are not exported, so those units are physical stock, not certified "
                "sellable, and the donor count must be confirmed before any movement",
                donor_on_hand,
                file_ref(pos_csv(41), f"store_id={DONOR};business_date={eod}"),
            ),
            check(
                "dc_projection_freshness",
                "unknown",
                False,
                f"the last ATP projection for {DC} is dated {projection_day.isoformat()}, "
                f"{projection_lag} days before D: ATP_NOW is 0 and the next receipt of "
                f"{receipt_units} units is {receipt_day.isoformat()}, while MIL01 has "
                f"{backorder_qty} units on backorder for {backorder_needed.isoformat()}",
                *atp_sources,
                *resv_sources,
            ),
            check(
                "open_backorder",
                "pass",
                False,
                f"MIL01 already has an open backorder line at the DC for {backorder_qty} units "
                f"of size {SIZE}, needed {backorder_needed.isoformat()}: documented demand, not "
                "forecast uplift",
                *resv_sources,
            ),
            curve_check,
        ),
        outcomes=None,  # not quantifiable: the option does not move stock (RFC §4.10)
        baseline_outcomes=None,
        assumptions=(
            f"the verification is a physical count at both stores, plus a check that the "
            f"{backorder_qty} backordered units are still expected on "
            f"{backorder_needed.isoformat()}",
            "nothing is dispatched: the review UI shows this option as informational",
        ),
        valid_until=case.valid_until,  # type: ignore[arg-type]
        recommended=True,
        rationale=(
            f"the data do not support a movement yet: {bridge_gap:.0f} units of size {SIZE} "
            f"disappeared from MIL01 between the last two snapshots, the donor's sellable "
            f"quantity is not exported and the DC ATP projection is {projection_lag} days old. "
            f"Count at {STORE} and {DONOR} first, then re-run the options: a movement approved "
            "now would rest on a snapshot that is already wrong"
        ),
    )

    transfer_cutoff = time.fromisoformat(transfer_lane["pickup_cutoff_local"])
    assert D.weekday() in pickup_weekdays(transfer_lane["pickup_days"])
    assert case.available_at < local_instant(D, transfer_cutoff)  # the run is before the cutoff
    transfer_pickup = local_instant(D, transfer_cutoff)
    # The lane has 0 contract days: the courier lands at closing, so the goods sell from the
    # next opening. Arrival hour and the 19:00 closing are stated assumptions, not lane fields.
    transfer_eta = local_instant(D, CLOSING)
    transfer_sellable = local_instant(sellable, OPENING)
    transfer = ActionOption(
        id="opt-d1-mil01-mil02-999-m-q2",
        **option_fields(
            [
                case,
                forecast,
                dest_on_hand,
                dest_sellable,
                donor_on_hand,
                donor_sellable,
            ],
            extra_sources=merge_sources(
                curve_sources, lane_sources, donor_min_sources, resv_sources
            ),
        ),
        case_id=case.id,
        forecast_ref=ref(forecast),
        kind="transfer",
        legs=(
            Leg(
                origin=DONOR,
                dest=STORE,
                sku=SKUS["999"],
                size=SIZE,
                ean=ean,
                qty=q_transfer,
                pickup_at=transfer_pickup,
                eta_at=transfer_eta,
                sellable_at=transfer_sellable,
                lane_id=transfer_lane["lane_id"],
                cost_eur=transfer_cost,
            ),
        ),
        checks=(
            check(
                "identity_crosswalk",
                "pass",
                True,
                f"EAN {ean} matches sku_size_ean.csv for {SKUS['999']}-{SIZE}; MIL01 and MIL02 are "
                f"SAP plants {src.werks[STORE]} and {src.werks[DONOR]} in the MDM crosswalk",
                file_ref(MASTER / "sku_size_ean.csv", f"sku_size={SKUS['999']}-{SIZE}"),
                file_ref(CROSSWALK, f"store_id={STORE}|{DONOR}"),
            ),
            check(
                "availability_freshness",
                "pass",
                True,
                f"donor {donor_on_hand.qty:.0f} units of size {SIZE} on hand at EOD "
                f"{eod.isoformat()} (D-1); destination {dest_before:.0f} at EOD "
                f"{before.isoformat()} and {dest_on_hand.qty:.0f} at EOD {eod.isoformat()} (see "
                "the snapshot bridge in the verification option)",
                donor_on_hand,
                dest_on_hand,
            ),
            check(
                "reservations",
                "unknown",
                True,
                f"the DC reservation export has no open line for {DONOR} (only MIL01's "
                f"{backorder_qty}-unit backorder), but store-level reservations are not exported "
                "either: the donor's sellable quantity is unknown, not assumed equal to on hand",
                *resv_sources,
                donor_sellable,
            ),
            check(
                "quality_hold",
                "unknown",
                True,
                f"QMEL has no quality notification for {STYLE}, but store-level quality holds are "
                "not exported either, so the check cannot pass",
                file_ref(QUALITY, f"MATNR starts with {STYLE}"),
            ),
            check(
                "min_presentation_safety",
                "pass",
                True,
                f"MIL02 {donor_min['category']} minimum is "
                f"{donor_min['min_pres_per_core_size']} unit per core size "
                f"({donor_min['core_sizes']}): at dispatch, sending {q_transfer} of "
                f"{donor_units_eod:.0f} leaves exactly that minimum, and the destination reaches "
                f"its own minimum of {store_min['min_pres_per_core_size']} for size {SIZE}",
                *donor_min_sources,
                *store_min_sources,
            ),
            check(
                "scarcity_assortment",
                "pass",
                True,
                "the style is in both stores' assortment and size M is a core size for both; "
                "scarcity is at the destination (0 units, below minimum), not at the donor",
                file_ref(MASTER / "store_assortment.csv", f"store_id={STORE}|{DONOR}"),
            ),
            check(
                "donor_protected",
                "pass",
                True,
                f"at dispatch the donor keeps its policy minimum: {donor_units_eod:.0f} units "
                f"minus the {q_transfer} moved leave {donor_after_move:.0f}, MIL02's minimum for "
                f"size {SIZE}. Over D+1..D+7 its own demand for size {SIZE} is "
                f"{fmt(donor_demand_total)} units ({p_donor:.1%} of its colour forecast), so it "
                f"sells out on {donor_sold_out.isoformat()} and loses "
                f"{fmt(transfer_donor_lost)} units against {fmt(hold_donor_lost)} on hold: that "
                f"additional damage is in the outcomes. Even with no transfer the donor ends "
                f"the horizon {fmt(donor_deficit)} units short of its demand at its minimum, so "
                "no positive integer holds the minimum for the whole horizon (see the "
                "assumptions)",
                donor_on_hand,
                *donor_min_sources,
                *donor_curve_sources,
                *donor_demand_sources,
            ),
            check(
                "lane_ibt",
                "pass",
                True,
                f"{transfer_lane['lane_id']}: {transfer_lane['mode']}, IBT allowed "
                f"{transfer_lane['ibt_allowed']}, customs {transfer_lane['customs_required']}, "
                f"{transfer_lane['distance_km']} km",
                *lane_sources,
            ),
            check(
                "calendar_cutoff",
                "pass",
                True,
                f"cutoff {transfer_lane['pickup_cutoff_local']} local on "
                f"{transfer_lane['pickup_days']}: {D.strftime('%A %Y-%m-%d')} is a pickup day and "
                f"the run computes at {case.available_at.astimezone(TZ):%H:%M}, so the pickup is "
                "the same day",
                *lane_sources,
            ),
            check(
                "eta_required_by",
                "pass",
                True,
                f"arrival at closing on {D.isoformat()}, sellable from {sellable.isoformat()}: "
                f"before the case's valid_until {case.valid_until.date().isoformat()}",
                *lane_sources,
            ),
            curve_check,
            check(
                "shared_resources",
                "pass",
                True,
                "one leg and one donor, and no other option in this run reserves the same units: "
                "options are alternatives, nothing is pre-booked. No IBT line exists yet for "
                "MIL02 size M, so there is no competing reservation",
                file_ref(IBT, f"scope=source_store:{DONOR}"),
            ),
        ),
        outcomes=tuple(
            outcome(
                scenario,
                rounded(transfer_dest_lost),
                rounded(transfer_donor_lost),
                rounded(transfer_dest_left),
                rounded(transfer_donor_left),
                transfer_cost,
                demand_basis,
                size_basis,
            )
            for scenario in SCENARIOS
        ),
        baseline_outcomes=tuple(
            outcome(
                scenario,
                rounded(hold_dest_lost),
                rounded(hold_donor_lost),
                rounded(hold_dest_left),
                rounded(hold_donor_left),
                0.0,
                demand_basis,
                size_basis,
            )
            for scenario in SCENARIOS
        ),
        assumptions=(
            f"q is limited by availability and the minimum at dispatch, not by the model: "
            f"{donor_units_eod:.0f} units on hand at {DONOR} minus its minimum of "
            f"{donor_min['min_pres_per_core_size']} for size {SIZE} = {q_transfer}, which is the "
            "top of the 1..2 the source email asks for",
            "donor demand uses the donor's own colour forecast and its own size curve: the move is "
            "judged against the donor's loss, not only the destination's gain",
            "RFC §4.10 reads `donor_protected` at dispatch and asks to compare the "
            "additional damage against hold: MIL02's own demand exceeds what a dispatch leaves, "
            f"so its stock floor breaks on {donor_sold_out.isoformat()} whatever quantity is "
            f"moved. The check records the floor the stock can keep and the "
            f"{fmt(transfer_donor_lost)}-unit horizon loss the outcomes carry",
            "two mandatory checks are unknown (store-level reservations and quality holds are "
            f"not exported), so the move is never recommended, even though it cuts unserved "
            f"units by "
            f"{fmt(hold_dest_lost + hold_donor_lost - transfer_dest_lost - transfer_donor_lost)} "
            f"for {fmt(transfer_cost)} EUR",
            "a human may still decide the cut is worth confirming the counts first; the engine "
            "cannot recommend it (RFC §4.10 insufficient data on a counterpart)",
        ),
        valid_until=case.valid_until,  # type: ignore[arg-type]
        recommended=False,
        rationale=(
            f"legs and lane work: {q_transfer} of the {donor_units_eod:.0f} units at {DONOR}, by "
            f"same-day courier before the {transfer_lane['pickup_cutoff_local']} cutoff, sellable "
            f"at {sellable.isoformat()}. It leaves {fmt(transfer_dest_lost)} units of size {SIZE} "
            f"unserved at {STORE} instead of {fmt(hold_dest_lost)} and keeps the donor's policy "
            f"minimum at dispatch, but the donor sells out on {donor_sold_out.isoformat()} and "
            f"loses {fmt(transfer_donor_lost)} units against {fmt(hold_donor_lost)} on hold for "
            f"{fmt(transfer_cost)} EUR, and its sellable quantity and quality state are unknown: "
            "no recommendation while the counts are unconfirmed"
        ),
    )

    # The DC leg is dated from the sources: first loading day on or after the receipt, the lane's
    # cutoff and contract days, then the first opening after arrival (RFC §4.10
    # `decision_due_at`).
    dc_cutoff = time.fromisoformat(dc_lane["pickup_cutoff_local"])
    dc_transit = int(float(dc_lane["transit_days_contract"]))
    dc_pickup_day = next_pickup_day(receipt_day, dc_lane["pickup_days"])
    dc_pickup = local_instant(dc_pickup_day, dc_cutoff)
    dc_arrival = dc_pickup_day + timedelta(days=dc_transit)
    dc_eta = local_instant(dc_arrival, dc_cutoff)
    dc_sellable = local_instant(dc_arrival + timedelta(days=1), OPENING)
    assert dc_sellable.date() > case.valid_until.date()  # nothing arrives inside the horizon
    replenish = ActionOption(
        id="opt-d1-mil01-dc-999-m-q4",
        **option_fields(
            [case, forecast, dest_on_hand, dest_sellable, atp, dc_on_hand],
            extra_sources=merge_sources(curve_sources, dc_lane_sources, atp_sources, resv_sources),
        ),
        case_id=case.id,
        forecast_ref=ref(forecast),
        kind="replenish_dc",
        legs=(
            Leg(
                origin=DC,
                dest=STORE,
                sku=SKUS["999"],
                size=SIZE,
                ean=ean,
                qty=q_dc,
                pickup_at=dc_pickup,
                eta_at=dc_eta,
                sellable_at=dc_sellable,
                lane_id=dc_lane["lane_id"],
                cost_eur=dc_cost,
            ),
        ),
        checks=(
            check(
                "identity_crosswalk",
                "pass",
                True,
                f"same EAN {ean}; {DC} is MIL01's supplying DC in the MDM crosswalk",
                file_ref(MASTER / "sku_size_ean.csv", f"sku_size={SKUS['999']}-{SIZE}"),
                file_ref(CROSSWALK, f"store_id={STORE}"),
            ),
            check(
                "availability_atp",
                "fail",
                True,
                f"ATP_NOW is 0 for {DC} {SKUS['999']} size {SIZE} (physical 0, blocked QI 0, no "
                f"open deliveries) and the next receipt of {receipt_units} units is "
                f"{receipt_day.isoformat()}",
                *atp_sources,
            ),
            check(
                "reservations",
                "pass",
                True,
                f"the {q_dc} units requested match MIL01's existing open backorder line for "
                f"{backorder_needed.isoformat()}: the leg promises no more than the line asks",
                *resv_sources,
            ),
            check(
                "quality_hold",
                "pass",
                True,
                "blocked QI stock for this plant, article and size is 0 and QMEL has no "
                f"notification for {STYLE}",
                *atp_sources,
                file_ref(QUALITY, f"MATNR starts with {STYLE}"),
            ),
            check(
                "min_presentation_safety",
                "pass",
                True,
                f"{q_dc} units cover MIL01's minimum of "
                f"{store_min['min_pres_per_core_size']} per core size for size {SIZE}",
                *store_min_sources,
            ),
            check(
                "scarcity_assortment",
                "pass",
                True,
                "the destination carries the style and size M is a core size for its category",
                file_ref(MASTER / "store_assortment.csv", f"store_id={STORE}"),
            ),
            check(
                "donor_protected",
                "not_applicable",
                True,
                "the origin is a distribution centre, not a store: it has no minimum "
                "presentation to protect and no own sales to cannibalise",
                *dc_lane_sources,
            ),
            check(
                "lane_ibt",
                "pass",
                True,
                f"{dc_lane['lane_id']}: {dc_lane['mode']}, customs "
                f"{dc_lane['customs_required']}; IBT rules do not apply to a DC replenishment",
                *dc_lane_sources,
            ),
            check(
                "calendar_cutoff",
                "pass",
                True,
                f"cutoff {dc_lane['pickup_cutoff_local']} local on {dc_lane['pickup_days']}: the "
                f"first loading day after the {receipt_day.isoformat()} receipt is "
                f"{dc_pickup_day.isoformat()}",
                *dc_lane_sources,
            ),
            check(
                "eta_required_by",
                "fail",
                True,
                f"sellable at {dc_sellable.date().isoformat()}, after the case's valid_until "
                f"{case.valid_until.date().isoformat()}: inside D+1..D+7 nothing can arrive",
                *dc_lane_sources,
            ),
            curve_check,
            check(
                "shared_resources",
                "pass",
                True,
                "one leg from the DC, and MIL01's backorder line is the only open request for "
                "this article and size: the alternatives in this run are not pre-booked",
                *resv_sources,
            ),
        ),
        outcomes=tuple(
            outcome(
                scenario,
                rounded(dc_dest_lost),
                None,
                rounded(dc_dest_left),
                None,
                0.0,  # the leg is outside the horizon: its cost is not charged to these losses
                no_arrival,
                size_basis,
            )
            for scenario in SCENARIOS
        ),
        baseline_outcomes=tuple(
            outcome(
                scenario,
                rounded(hold_dest_lost),
                None,
                rounded(hold_dest_left),
                None,
                0.0,
                dc_counterpart,
                size_basis,
            )
            for scenario in SCENARIOS
        ),
        assumptions=(
            f"the leg is dated on the first loading day the lane calendar allows after the "
            f"receipt ({dc_pickup_day.isoformat()}), not on D, and it costs {fmt(dc_cost)} EUR: "
            "showing the real ETA is the point of the option",
            "DC-side outcomes stay unknown (no per-location DC demand in the sources) and the "
            "option is not recommended, so no numerical claim is made on the counterpart",
        ),
        valid_until=case.valid_until,  # type: ignore[arg-type]
        recommended=False,
        rationale=(
            f"blocked: {DC} has 0 ATP for size {SIZE} and the {receipt_units}-unit receipt lands "
            f"on {receipt_day.isoformat()}, so the earliest sellable date is "
            f"{dc_sellable.date().isoformat()}, after "
            "the case's due date. Inside D+1..D+7 it changes nothing versus hold: the "
            f"{q_dc}-unit backorder cannot be served from the DC"
        ),
    )

    options = [hold, verify, transfer, replenish]

    # --- one agent trace: the deterministic fallback of RFC §4.8.1 ---------------------
    trace = AgentTrace(
        id="trace-20261009-mil01-i10919b00011-verify",
        **derived(
            [case, *facts, *options],
            extra_sources=merge_sources(curve_sources, lane_sources, resv_sources),
        ),
        case_id=case.id,
        steps=(
            AgentStep(
                tool="get_case_evidence",
                arguments={"case_id": case.id},
                input_refs=(ref(case),),
                output_refs=(
                    ref(case),
                    *(
                        ArtifactRef(kind="Observation", id=item.id, version=item.version)
                        for item in case.supporting
                    ),
                    *(
                        ArtifactRef(kind="EntityLink", id=item.id, version=item.version)
                        for item in case.context_refs
                    ),
                ),
                duration_ms=12,
            ),
            AgentStep(
                tool="get_available_stock",
                arguments={"sku": SKUS["999"], "size": SIZE, "locations": [STORE, DONOR, DC]},
                input_refs=(),
                # The whole visible stock view of the article, including the unknown
                # `sellable` facts: they are what makes the verification necessary.
                output_refs=tuple(
                    ref(fact) for fact in facts if fact.sku == SKUS["999"]
                ),
                duration_ms=8,
            ),
            AgentStep(
                tool="get_lane_and_eta",
                arguments={
                    "origin": DONOR,
                    "dest": STORE,
                    "requested_at": case.available_at.isoformat(),  # the run instant
                    "required_by": case.valid_until.isoformat(),  # type: ignore[union-attr]
                },
                input_refs=(),
                # A lane row is a source row, not a stored artifact: it travels as the
                # `SourceFile` reference the checks also use.
                output_refs=(as_ref(lane_sources[0]),),
                duration_ms=5,
            ),
            AgentStep(
                tool="evaluate_options",
                arguments={"case_id": case.id, "candidate_donors": [DONOR]},
                input_refs=(ref(case), *(ref(fact) for fact in facts)),
                output_refs=tuple(ref(option) for option in options),
                duration_ms=34,
            ),
            AgentStep(
                tool="finish",
                arguments={
                    "option_id": verify.id,
                    "status": "verify",
                    "evidence_refs": [
                        f"{item.kind}:{item.id}@{item.version}"
                        for item in (
                            ref(case),
                            ref(dest_on_hand),
                            ref(dest_sellable),
                            ref(donor_on_hand),
                            ref(donor_sellable),
                            ref(atp),
                            ref(transfer),
                        )
                    ],
                    "rationale": verify.rationale,
                },
                input_refs=(ref(verify),),
                output_refs=(ref(verify),),
                duration_ms=3,
            ),
        ),
        outcome=(
            "verify_stock: the transfer's legs work and it clears every mandatory check that the "
            "sources can decide, but the donor's sellable quantity and quality state are unknown, "
            "the destination snapshot is unexplained and the DC can only serve the open "
            f"{q_dc}-unit backorder after {receipt_day.isoformat()}: count first, then re-run"
        ),
        fallback_used=True,
        mode="fixture",
        tokens_in=None,
        tokens_out=None,
    )

    # --- write -------------------------------------------------------------------------
    for folder in ("stock", "options", "traces"):
        for old in (OUT / folder).glob("*.json"):
            old.unlink()
    for fact in facts:
        write(OUT / "stock" / f"{fact.id}.json", [record(fact)])
    for option in options:
        write(OUT / "options" / f"{option.id}.json", [record(option)])
    write(OUT / "traces" / f"{trace.id}.json", [record(trace)])
    print(
        f"{len(facts)} stock facts, {len(options)} options, 1 trace; size {SIZE}: "
        f"dest lost {fmt(hold_dest_lost)} -> {fmt(transfer_dest_lost)} (q={q_transfer}, "
        f"{fmt(transfer_cost)} EUR), donor lost {fmt(hold_donor_lost)} -> "
        f"{fmt(transfer_donor_lost)}"
    )


def record(dto) -> dict:
    return {"kind": type(dto).__name__, "payload": dto.model_dump(mode="json")}


def write(path: Path, records: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
