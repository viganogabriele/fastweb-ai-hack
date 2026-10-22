"""ACT-04 module: `sys.client` stores DC stock/ATP as `StockFact`; reads never pass `as_of`.

ERP master rows are written straight to `erp_rows`; the systems are an `httpx.MockTransport`
that answers for any day and plant, with the quirks of the mock server (SAP IT/US formats, the
HK 3PL feed delivered the next morning, `NO_FILE` for a day not delivered yet).
"""

import json
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import httpx
import pytest
from jsonschema import Draft202012Validator

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import ModuleRun, RunSpec, SourceRef, StockFact
from tessera.core.db import connect
from tessera.core.repo import ErpRecord, Repo, create_run, put_erp, put_module_run
from tessera.modules.sources import systems_client as sc
from tessera.modules.sources.systems_client import LaneEta, SystemsClient, SystemsReader, Unknown

ROME, HKT = ZoneInfo("Europe/Rome"), ZoneInfo("Asia/Hong_Kong")
SKU = "J20931A00012-999"
SIZES = ("00", "0", "1")
EAN = {"00": "800001276100", "0": "800001276101", "1": "800001276102"}
QTY = {"00": 1, "0": 3, "1": 7}
MASTER_AT = datetime(2026, 8, 1, tzinfo=UTC)
FRIDAY_EVENING = datetime(2026, 10, 16, 21, 0, tzinfo=ROME)
SOURCES = REPO_ROOT / "generated" / "sources"
EXAMPLES = SOURCES / "systems" / "agents" / "examples"
REF = SourceRef(uri="erp/test.csv", content_hash="h")


def erp(table: str, id: str, data: dict, available_at: datetime = MASTER_AT) -> ErpRecord:
    return ErpRecord(table, id, "v1", available_at, "test", (REF,), data)


def stock_row(store: str, size: str, day: date, on_hand: int) -> ErpRecord:
    published = datetime.combine(day + timedelta(days=1), datetime.min.time(), ROME)
    data = {"store_id": store, "sku": SKU, "size": size, "snapshot_date": day,
            "on_hand": on_hand, "in_transit": 0}  # fmt: skip
    return erp("stock", f"{store}-{size}-{day}", data, published.replace(hour=6))


def master_rows() -> list[ErpRecord]:
    rows = [
        erp("stores", s, {"store_id": s, "timezone": "Europe/Rome"}) for s in ("MIL01", "MIL02")
    ]
    rows += [
        erp("sku_size_ean", f"{SKU}-{z}",
            {"sku": SKU, "size": z, "sku_size": f"{SKU}-{z}", "ean": EAN[z]})
        for z in SIZES
    ]  # fmt: skip
    rows.append(erp("assortment", "MIL01", {"store_id": "MIL01", "sku": SKU}))
    return rows


def spec(as_of: datetime, run_id: str = "run-1") -> RunSpec:
    return RunSpec(
        run_id=run_id, scenario_id="historical", as_of=as_of, stores=("MIL01", "MIL02"),
        source_manifest_hash="s", config_hash="c", code_version="0", mode="live", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


class StrictRepo(Repo):
    """Like PLT-04's `RunRepo`: reading by a store outside the run is an error."""

    def list(self, kind, *, store_id=None, **kw):
        if store_id is not None and store_id not in self.spec.stores:
            raise ValueError("Store is outside this RunSpec")
        return super().list(kind, store_id=store_id, **kw)

    def erp(self, table, *, store_id=None, sku=None):
        if store_id is not None and store_id not in self.spec.stores:
            raise ValueError("Store is outside this RunSpec")
        return super().erp(table, store_id=store_id, sku=sku)


@pytest.fixture
def engine(tmp_path):
    return connect(f"sqlite:///{tmp_path / 't.db'}")


def make_repo(engine, as_of: datetime, master: bool = True) -> Repo:
    if master:
        put_erp(engine, master_rows())
    s = spec(as_of)
    create_run(engine, s)
    return StrictRepo(engine, s)


def sap_rows(plant: str, day: date, qty: dict[str, str] | None = None) -> list[dict]:
    us = plant == "US20"
    d = day.strftime("%m/%d/%Y" if us else "%d.%m.%Y")
    return [
        {"STICHTAG": d, "WERKS": plant, "LGORT": "0001", "MATNR": "J20931A00012999",
         "J_3ASIZE": z, "EAN11": EAN[z],
         "LABST": (qty or {}).get(z, f"{QTY[z]}.000" if us else f"{QTY[z]},000")}
        for z in SIZES
    ]  # fmt: skip


def systems(seen=None, no_extraction=frozenset(), down=False, rate_limited=0, labst=None):
    """Mock warehouse and logistics. `rate_limited` = how many requests answer 429 first."""
    budget = {"429": rate_limited}

    def handler(request: httpx.Request) -> httpx.Response:
        if down:
            raise httpx.ConnectError("refused")
        q = dict(request.url.params)
        if seen is not None:
            seen.append((request.url.path, q))
        if budget["429"] > 0:
            budget["429"] -= 1
            return httpx.Response(429, headers={"retry-after": "0"}, json={"error": "x"})
        if request.url.path == "/warehouse/v1/stock":
            plant, day = q["plant"], date.fromisoformat(q["date"])
            if q["date"] in no_extraction:
                if plant == "HK30":
                    return httpx.Response(200, json={"error": "NO_FILE", "message": "no 3PL file"})
                return httpx.Response(200, json={"positions": [], "note": "no extraction"})
            if plant == "HK30":  # delivered the next morning, one row per location type
                when = f"{day + timedelta(days=1)} 06:17"
                rows = [
                    {"Snapshot Time (HKT)": when, "Barcode": EAN[z], "Location Type": t,
                     "Available Qty": str(QTY[z])}
                    for z in SIZES for t in ("PICK", "ECOM")
                ]  # fmt: skip
                return httpx.Response(200, json={"positions": rows})
            return httpx.Response(200, json={"positions": sap_rows(plant, day, labst)})
        if request.url.path == "/warehouse/v1/atp":
            positions = [
                {"plant": q["plant"], "size": z, "unrestricted": QTY[z], "openDeliveries": 0,
                 "ecomReserve": 0, "blocked": 0, "atp": QTY[z] - 1}
                for z in SIZES
            ]  # fmt: skip
            body = {"snapshot": f"{q['asOf']}T06:00:00", "stale": False, "positions": positions}
            return httpx.Response(200, json=body)
        if request.url.path == "/logistics/v1/lanes":
            lane = json.loads((EXAMPLES / "logistics_get_lane_MIL02_MIL01.json").read_text())
            return httpx.Response(200, json=lane["response"])
        return httpx.Response(404, text="no route")

    return handler


def factory(handler):
    return lambda crosswalk: SystemsClient(crosswalk, transport=httpx.MockTransport(handler))


def run_module(repo: Repo, handler, params: dict | None = None):
    ctx = SimpleNamespace(spec=repo.spec, repo=repo, params=params or {},
                          clients={"systems": factory(handler)})  # fmt: skip
    result = sc.run(ctx)
    record = ModuleRun(
        run_id=repo.run_id, module_id="sys.client", mode="live", status=result.status,
        result=result,
    )  # fmt: skip
    put_module_run(repo.engine, record)
    return result


def reader(repo: Repo, handler=None) -> SystemsReader:
    got = SystemsReader.open(repo, factory(handler or systems()))
    assert isinstance(got, SystemsReader)
    return got


def facts_by(repo: Repo, basis: str) -> dict[str, StockFact]:
    return {f.size: f for f in repo.list(StockFact) if f.basis == basis}


def test_manifest_is_a_valid_source_module() -> None:
    assert sc.MANIFEST.id == "sys.client" and sc.MANIFEST.layer == "sources"
    assert sc.MANIFEST.requires == ("src.erp",) and sc.MANIFEST.boundary == "simulated"
    Draft202012Validator.check_schema(sc.MANIFEST.params_schema)
    Draft202012Validator(sc.MANIFEST.params_schema).validate({"skus": [SKU], "plants": ["IT10"]})


def test_run_stores_dc_stock_and_atp_for_assortment_and_supplying_dc(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    seen: list = []
    result = run_module(repo, systems(seen))

    assert result.status == "succeeded" and result.errors == (), result
    # MIL01 and MIL02 are supplied by DC-IT-CSG = IT10; only MIL01 lists the SKU.
    assert {(path, q["plant"]) for path, q in seen} == {
        ("/warehouse/v1/stock", "IT10"),
        ("/warehouse/v1/atp", "IT10"),
    }
    sellable, atp = facts_by(repo, "sellable"), facts_by(repo, "atp")
    assert {z: f.qty for z, f in sellable.items()} == {"00": 1.0, "0": 3.0, "1": 7.0}
    assert {z: f.qty for z, f in atp.items()} == {"00": 0.0, "0": 2.0, "1": 6.0}
    assert all(f.available_at <= FRIDAY_EVENING for f in repo.list(StockFact))
    assert result.counts["stock_facts"] == 6 and result.counts["stock_facts_new"] == 6


def test_early_morning_replay_falls_back_to_the_last_published_day(engine) -> None:
    # 05:00 in Rome: Thursday's EOD stock (published 06:00) and today's ATP are not known yet.
    as_of = datetime(2026, 10, 16, 5, 0, tzinfo=ROME)
    repo = make_repo(engine, as_of)
    assert run_module(repo, systems()).status == "succeeded"
    assert {f.snapshot_at.date() for f in facts_by(repo, "sellable").values()} == {
        date(2026, 10, 14)
    }
    assert {f.snapshot_at for f in facts_by(repo, "atp").values()} == {
        datetime(2026, 10, 15, 6, 0, tzinfo=ROME)
    }
    assert all(f.available_at <= as_of for f in repo.list(StockFact))


def test_missing_extraction_uses_the_previous_day_not_zero(engine) -> None:
    monday = datetime(2026, 10, 19, 21, 0, tzinfo=ROME)
    repo = make_repo(engine, monday)
    run_module(repo, systems(no_extraction=frozenset({"2026-10-18"})))  # no Sunday extraction
    assert {f.snapshot_at.date() for f in facts_by(repo, "sellable").values()} == {
        date(2026, 10, 17)
    }


def test_hk_feed_of_a_day_not_delivered_yet_falls_back(engine) -> None:
    # 21:00 in Rome is 03:00 HKT the next day: the 3PL file of Oct 22 is not there (NO_FILE).
    as_of = datetime(2026, 10, 22, 21, 0, tzinfo=ROME)
    repo = make_repo(engine, as_of)
    result = run_module(
        repo, systems(no_extraction=frozenset({"2026-10-22"})), {"plants": ["HK30"]}
    )
    assert result.status == "succeeded" and result.errors == (), result
    sellable = facts_by(repo, "sellable")
    assert {z: f.qty for z, f in sellable.items()} == {"00": 1.0, "0": 3.0, "1": 7.0}  # no ECOM
    assert {f.snapshot_at for f in sellable.values()} == {datetime(2026, 10, 22, 6, 17, tzinfo=HKT)}
    assert all(f.available_at <= as_of for f in repo.list(StockFact))


def test_us_sap_format_and_size_00(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    result = run_module(repo, systems(), {"plants": ["US20"]})
    assert result.status == "succeeded"
    sellable = facts_by(repo, "sellable")
    assert sellable["00"].qty == 1.0 and sellable["00"].ean == EAN["00"]
    # 21:00 Rome = 15:00 New York: Thursday's EOD is published at 06:00 NY on Friday.
    new_york = ZoneInfo("America/New_York")
    assert sellable["00"].snapshot_at.astimezone(new_york).date() == date(2026, 10, 15)


def test_extraction_missing_for_the_whole_lookback_is_an_abstention(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    days = frozenset({"2026-10-15", "2026-10-14"})
    result = run_module(repo, systems(no_extraction=days), {"lookback_days": 1})
    assert result.status == "succeeded"  # ATP still known; a missing extraction is not a failure
    assert result.abstentions == (f"dc_stock IT10 {SKU}: no_extraction",)
    assert {f.basis for f in repo.list(StockFact)} == {"atp"}
    assert reader(repo).stock(SKU, "1", ["IT10"])["IT10"][0].basis == "atp"


def test_systems_down_degrades_and_reader_says_unavailable_not_no_stock(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    result = run_module(repo, systems(down=True))
    assert result.status == "degraded"
    assert result.errors == (f"dc_stock IT10 {SKU}: unavailable", f"atp IT10 {SKU}: unavailable")
    assert repo.list(StockFact) == []
    assert reader(repo).stock(SKU, "1", ["IT10"])["IT10"].reason == "unavailable"


def test_malformed_feed_is_an_error_not_an_abstention(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    result = run_module(repo, systems(labst={"1": "1,500"}))  # fractional units
    assert result.status == "degraded"
    assert result.errors == (f"dc_stock IT10 {SKU}: unparseable",)


def test_rate_limit_is_retried_then_the_plant_is_not_hammered(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    client = factory(systems(rate_limited=1))
    sleeps: list[float] = []
    result = sc.load_stock(repo, client(sc.crosswalk_at(repo, sc.crosswalk_rows(SOURCES)[0])),
                           [SKU], ["IT10"], sleep=sleeps.append)  # fmt: skip
    assert result.status == "succeeded" and sleeps == [0.0]

    seen: list = []
    client = factory(systems(seen, rate_limited=100))
    crosswalk = sc.crosswalk_at(repo, sc.crosswalk_rows(SOURCES)[0])
    result = sc.load_stock(repo, client(crosswalk), [SKU], ["IT10"], sleep=lambda s: None)
    assert result.status == "degraded"
    assert len(seen) == 1 + sc.RATE_LIMIT_RETRIES  # dc_stock retried, then ATP is not asked
    assert result.errors == (f"dc_stock IT10 {SKU}: rate_limited", f"atp IT10 {SKU}: rate_limited")


def test_master_data_not_known_at_as_of_blocks(engine) -> None:
    repo = make_repo(engine, datetime(2026, 7, 1, tzinfo=UTC))  # before the master snapshot
    assert isinstance(sc.crosswalk_at(repo, sc.crosswalk_rows(SOURCES)[0]), Unknown)
    result = sc.run(SimpleNamespace(spec=repo.spec, repo=repo, params={}, clients={}))
    assert result.status == "blocked"
    assert isinstance(SystemsReader.open(repo), Unknown)


def test_params_override_scope(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    seen: list = []
    result = run_module(repo, systems(seen), {"skus": [SKU, "NOPE-000"], "plants": ["IT10"]})
    assert result.abstentions == (
        "dc_stock IT10 NOPE-000: unknown_sku",
        "atp IT10 NOPE-000: unknown_sku",
    )
    assert len(seen) == 2  # an unknown SKU never reaches the network


def test_reader_stock_for_dc_and_run_store_at_as_of(engine) -> None:
    put_erp(engine, [
        stock_row("MIL02", "1", date(2026, 10, 15), 4),
        stock_row("MIL02", "1", date(2026, 10, 16), 1),  # published Saturday 06:00: future
    ])  # fmt: skip
    repo = make_repo(engine, FRIDAY_EVENING)
    run_module(repo, systems())
    got = reader(repo).stock(SKU, "1", ["IT10", "DC-IT-CSG", "MIL02", "TYO01", "XX99"])

    assert [(f.basis, f.qty) for f in got["IT10"]] == [("atp", 6.0), ("sellable", 7.0)]
    assert got["DC-IT-CSG"] == got["IT10"]
    (store,) = got["MIL02"]
    assert (store.basis, store.qty) == ("on_hand", 4.0)
    assert store.snapshot_at == datetime(2026, 10, 15, 23, 59, 59, tzinfo=ROME)
    assert store.reservations_included is None  # ERP on_hand says nothing about reservations
    assert got["TYO01"].reason == "unknown_location"  # a real store, but not in this run
    assert got["XX99"].reason == "unknown_location"
    assert reader(repo).stock(SKU, "0", ["MIL02"])["MIL02"].reason == "not_loaded"


@pytest.mark.skipif(not EXAMPLES.exists(), reason="dataset not checked out")
def test_reader_lane_and_eta_against_required_by(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    r = reader(repo)

    # Asked "now" or earlier: Friday 21:00 is after the 15:30 cut-off, next pickup Monday.
    monday_noon = datetime(2026, 10, 19, 12, 0, tzinfo=ROME)
    got = r.lane_and_eta("MIL02", "MIL01", FRIDAY_EVENING - timedelta(days=1), monday_noon)
    assert isinstance(got, LaneEta)
    assert got.eta.pickup_at == datetime(2026, 10, 19, 15, 30, tzinfo=ROME)
    assert (got.eta.eta_date, got.on_time, got.on_time_p90) == (date(2026, 10, 19), True, False)
    assert r.lane_and_eta("MIL02", "MIL01", FRIDAY_EVENING).on_time is None
    assert r.lane_and_eta("XX99", "MIL01", FRIDAY_EVENING).reason == "unknown_location"
    # PAR01 has a plant but no time zone known in this run: no guessed due date.
    assert r.lane_and_eta("MIL02", "PAR01", FRIDAY_EVENING, monday_noon).reason == (
        "unknown_location"
    )
