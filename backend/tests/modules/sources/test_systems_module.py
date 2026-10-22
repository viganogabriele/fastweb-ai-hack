"""ACT-04 module: `sys.client` stores DC stock/ATP as `StockFact`; reads never pass `as_of`.

ERP master rows are written straight to `erp_rows`; the systems are an `httpx.MockTransport`
that answers for any day, like the mock server.
"""

import json
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import httpx
import pytest
from jsonschema import Draft202012Validator

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import RunSpec, SourceRef, StockFact
from tessera.core.db import connect
from tessera.core.repo import ErpRecord, Repo, create_run, put_erp
from tessera.modules.sources import systems_client as sc
from tessera.modules.sources.systems_client import LaneEta, SystemsClient, SystemsReader, Unknown

ROME = ZoneInfo("Europe/Rome")
SKU = "J20931A00012-999"
MASTER_AT = datetime(2026, 8, 1, tzinfo=UTC)
FRIDAY_EVENING = datetime(2026, 10, 16, 21, 0, tzinfo=ROME)
EXAMPLES = REPO_ROOT / "generated" / "sources" / "systems" / "agents" / "examples"
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
        erp(
            "sku_size_ean",
            f"{SKU}-{z}",
            {"sku": SKU, "size": z, "sku_size": f"{SKU}-{z}", "ean": f"80000127610{z}"},
        )  # fmt: skip
        for z in ("0", "1")
    ]
    rows.append(erp("assortment", "MIL01", {"store_id": "MIL01", "sku": SKU}))
    return rows


def spec(as_of: datetime, run_id: str = "run-1") -> RunSpec:
    return RunSpec(
        run_id=run_id, scenario_id="historical", as_of=as_of, stores=("MIL01", "MIL02"),
        source_manifest_hash="s", config_hash="c", code_version="0", mode="live", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


@pytest.fixture
def engine(tmp_path):
    return connect(f"sqlite:///{tmp_path / 't.db'}")


def make_repo(engine, as_of: datetime, master: bool = True, run_id: str = "run-1") -> Repo:
    if master:
        put_erp(engine, master_rows())
    s = spec(as_of, run_id)
    create_run(engine, s)
    return Repo(engine, s)


def systems(seen: list | None = None, no_extraction: frozenset[str] = frozenset(), down=False):
    """Mock warehouse: SAP stock for any `date`, ATP published 06:00 local on `asOf`."""

    def handler(request: httpx.Request) -> httpx.Response:
        if down:
            raise httpx.ConnectError("refused")
        q = request.url.params
        if seen is not None:
            seen.append((request.url.path, dict(q)))
        if request.url.path == "/warehouse/v1/stock":
            if q["date"] in no_extraction:
                return httpx.Response(200, json={"positions": [], "note": "no extraction"})
            d = date.fromisoformat(q["date"]).strftime("%d.%m.%Y")
            rows = [
                {"STICHTAG": d, "WERKS": "IT10", "LGORT": "0001", "MATNR": "J20931A00012999",
                 "J_3ASIZE": z, "LABST": f"{n},000", "EAN11": f"80000127610{z}"}
                for z, n in (("0", 3), ("1", 7))
            ]  # fmt: skip
            return httpx.Response(200, json={"positions": rows})
        if request.url.path == "/warehouse/v1/atp":
            positions = [
                {"plant": "IT10", "size": z, "unrestricted": n, "openDeliveries": 0,
                 "ecomReserve": 0, "blocked": 0, "atp": n}
                for z, n in (("0", 2), ("1", 0))
            ]  # fmt: skip
            body = {"snapshot": f"{q['asOf']}T06:00:00", "stale": False, "positions": positions}
            return httpx.Response(200, json=body)
        if request.url.path == "/logistics/v1/lanes":
            lane = json.loads((EXAMPLES / "logistics_get_lane_MIL02_MIL01.json").read_text())
            return httpx.Response(200, json=lane["response"])
        return httpx.Response(404, text="no route")

    return handler


def run_module(repo: Repo, handler, params: dict | None = None):
    rows, _ = sc.crosswalk_rows(REPO_ROOT / "generated" / "sources")
    client = SystemsClient(sc.crosswalk_at(repo, rows), transport=httpx.MockTransport(handler))
    ctx = SimpleNamespace(spec=repo.spec, repo=repo, params=params or {},
                          clients={"systems": client})  # fmt: skip
    return sc.run(ctx), client


def test_manifest_is_a_valid_source_module() -> None:
    assert sc.MANIFEST.id == "sys.client" and sc.MANIFEST.layer == "sources"
    assert sc.MANIFEST.requires == ("src.erp",) and sc.MANIFEST.boundary == "simulated"
    Draft202012Validator.check_schema(sc.MANIFEST.params_schema)
    Draft202012Validator(sc.MANIFEST.params_schema).validate({"skus": [SKU], "plants": ["IT10"]})


def test_run_stores_dc_stock_and_atp_for_assortment_and_supplying_dc(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    seen: list = []
    result, _ = run_module(repo, systems(seen))

    assert result.status == "succeeded", result
    # MIL01 and MIL02 are supplied by DC-IT-CSG = IT10; only MIL01 lists the SKU.
    assert {(p, q["plant"]) for p, q in seen} == {
        ("/warehouse/v1/stock", "IT10"),
        ("/warehouse/v1/atp", "IT10"),
    }
    facts = repo.list(StockFact)
    assert sorted((f.basis, f.size, f.qty) for f in facts) == [
        ("atp", "0", 2.0), ("atp", "1", 0.0), ("sellable", "0", 3.0), ("sellable", "1", 7.0),
    ]  # fmt: skip
    assert all(f.available_at <= FRIDAY_EVENING for f in facts)
    assert result.counts["stock_facts"] == 4 and result.counts["stock_facts_new"] == 4


def test_early_morning_replay_falls_back_to_the_last_published_day(engine) -> None:
    # 05:00 in Rome: Thursday's EOD stock (published 06:00) and today's ATP are not known yet.
    as_of = datetime(2026, 10, 16, 5, 0, tzinfo=ROME)
    repo = make_repo(engine, as_of)
    result, _ = run_module(repo, systems())
    facts = repo.list(StockFact)
    sellable = {f.snapshot_at.date() for f in facts if f.basis == "sellable"}
    atp = {f.snapshot_at for f in facts if f.basis == "atp"}
    assert sellable == {date(2026, 10, 14)}
    assert atp == {datetime(2026, 10, 15, 6, 0, tzinfo=ROME)}
    assert all(f.available_at <= as_of for f in facts)
    assert result.status == "succeeded"


def test_missing_extraction_uses_the_previous_day_not_zero(engine) -> None:
    monday = datetime(2026, 10, 19, 21, 0, tzinfo=ROME)
    repo = make_repo(engine, monday)
    run_module(repo, systems(no_extraction=frozenset({"2026-10-18"})))  # no Sunday extraction
    sellable = [f for f in repo.list(StockFact) if f.basis == "sellable"]
    assert {f.snapshot_at.date() for f in sellable} == {date(2026, 10, 17)}


def test_extraction_missing_for_the_whole_lookback_is_an_abstention(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    days = frozenset({"2026-10-15", "2026-10-14"})
    result, _ = run_module(repo, systems(no_extraction=days), {"lookback_days": 1})
    assert result.status == "succeeded"  # ATP still known
    assert result.abstentions == (f"dc_stock IT10 {SKU}: no_extraction",)
    assert {f.basis for f in repo.list(StockFact)} == {"atp"}


def test_systems_down_degrades_without_inventing_stock(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    result, _ = run_module(repo, systems(down=True))
    assert result.status == "degraded"
    assert result.errors == (f"dc_stock IT10 {SKU}: unavailable", f"atp IT10 {SKU}: unavailable")
    assert repo.list(StockFact) == []


def test_master_data_not_known_at_as_of_blocks(engine) -> None:
    repo = make_repo(engine, datetime(2026, 7, 1, tzinfo=UTC))  # before the master snapshot
    rows, _ = sc.crosswalk_rows(REPO_ROOT / "generated" / "sources")
    assert isinstance(sc.crosswalk_at(repo, rows), Unknown)
    result = sc.run(SimpleNamespace(spec=repo.spec, repo=repo, params={}, clients={}))
    assert result.status == "blocked"


def test_params_override_scope(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    seen: list = []
    result, _ = run_module(repo, systems(seen), {"skus": [SKU, "NOPE-000"], "plants": ["IT10"]})
    assert result.abstentions == (
        "dc_stock IT10 NOPE-000: unknown_sku",
        "atp IT10 NOPE-000: unknown_sku",
    )
    assert len(seen) == 2  # unknown SKU never reaches the network


def test_reader_stock_for_dc_and_store_at_as_of(engine) -> None:
    put_erp(engine, [
        stock_row("MIL02", "1", date(2026, 10, 15), 4),
        stock_row("MIL02", "1", date(2026, 10, 16), 1),  # published Saturday 06:00: future
    ])  # fmt: skip
    repo = make_repo(engine, FRIDAY_EVENING)
    _, client = run_module(repo, systems())
    reader = SystemsReader(repo, client)

    got = reader.stock(SKU, "1", ["IT10", "MIL02", "XX99"])
    assert [(f.basis, f.qty) for f in got["IT10"]] == [("atp", 0.0), ("sellable", 7.0)]
    (store,) = got["MIL02"]
    assert (store.basis, store.qty) == ("on_hand", 4.0)
    assert store.snapshot_at.date() == date(2026, 10, 15)
    assert store.reservations_included is None  # ERP on_hand says nothing about reservations
    assert got["XX99"] == Unknown("unknown_location", "XX99")
    assert reader.stock(SKU, "0", ["MIL02"])["MIL02"].reason == "not_loaded"


def test_reader_never_sees_facts_of_a_later_run(engine) -> None:
    later = make_repo(engine, FRIDAY_EVENING + timedelta(days=3), run_id="later")
    run_module(later, systems())
    earlier = make_repo(engine, FRIDAY_EVENING, master=False, run_id="earlier")
    rows, _ = sc.crosswalk_rows(REPO_ROOT / "generated" / "sources")
    reader = SystemsReader(earlier, SystemsClient(sc.crosswalk_at(earlier, rows)))
    assert reader.stock(SKU, "1", ["IT10"])["IT10"].reason == "not_loaded"


@pytest.mark.skipif(not EXAMPLES.exists(), reason="dataset not checked out")
def test_reader_lane_and_eta_against_required_by(engine) -> None:
    repo = make_repo(engine, FRIDAY_EVENING)
    _, client = run_module(repo, systems())
    reader = SystemsReader(repo, client)

    # Asked "now" or earlier: Friday 21:00 is after the 15:30 cut-off, next pickup Monday.
    got = reader.lane_and_eta("MIL02", "MIL01", FRIDAY_EVENING - timedelta(days=1),
                              required_by=datetime(2026, 10, 19, 12, 0, tzinfo=ROME))  # fmt: skip
    assert isinstance(got, LaneEta)
    assert got.eta.pickup_at == datetime(2026, 10, 19, 15, 30, tzinfo=ROME)
    assert (got.eta.eta_date, got.on_time, got.on_time_p90) == (date(2026, 10, 19), True, False)
    assert reader.lane_and_eta("MIL02", "MIL01", FRIDAY_EVENING).on_time is None
    assert reader.lane_and_eta("XX99", "MIL01", FRIDAY_EVENING).reason == "unknown_location"
