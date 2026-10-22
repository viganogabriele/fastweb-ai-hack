import csv
import json
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import httpx
import pytest

from tessera.core.config import REPO_ROOT
from tessera.modules.sources.systems_client import (
    Crosswalk,
    Lane,
    SystemsClient,
    Unknown,
    eta,
)

SYSTEMS = REPO_ROOT / "generated" / "sources" / "systems"
EXAMPLES = SYSTEMS / "agents" / "examples"
SKU = "J20931A00012-999"
ROME, HKT, BERLIN = ZoneInfo("Europe/Rome"), ZoneInfo("Asia/Hong_Kong"), ZoneInfo("Europe/Berlin")

CROSSWALK = Crosswalk.from_rows(
    [
        {"store_id": "MIL01", "sap_plant_werks": "1001"},
        {"store_id": "MIL02", "sap_plant_werks": "1002"},
        {"store_id": "BER01", "sap_plant_werks": "1402"},
        {"store_id": "PAR01", "sap_plant_werks": "1101"},
    ],
    [
        {"store_id": "MIL01", "timezone": "Europe/Rome"},
        {"store_id": "MIL02", "timezone": "Europe/Rome"},
        {"store_id": "BER01", "timezone": "Europe/Berlin"},
        {"store_id": "PAR01", "timezone": "Europe/Paris"},
    ],
    [
        {"sku": SKU, "size": "0", "ean": "800001276101"},
        {"sku": SKU, "size": "1", "ean": "800001276102"},
        {"sku": "J20931A00618-510", "size": "1", "ean": "800009999999"},
    ],
)


def example(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text())["response"]


def client(routes: dict[str, tuple[int, object]], seen: list | None = None) -> SystemsClient:
    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request.url)
        status, body = routes[request.url.path]
        return httpx.Response(status, json=body)

    return SystemsClient(CROSSWALK, transport=httpx.MockTransport(handler))


def sap_row(lgort: str, size: str, labst: str, day: str = "15.10.2026") -> dict:
    return {
        "STICHTAG": day,
        "WERKS": "IT10",
        "LGORT": lgort,
        "MATNR": "J20931A00012999",
        "J_3ASIZE": size,
        "LABST": labst,
        "EAN11": "800001276101" if size == "0" else "800001276102",
    }


def test_crosswalk_maps_stores_dcs_and_aliases() -> None:
    assert CROSSWALK.plant("MIL01") == "1001"
    assert CROSSWALK.plant("1001") == "1001"
    assert CROSSWALK.plant("DC-IT-CSG") == "IT10"
    assert CROSSWALK.plant("NOPE") is None
    assert CROSSWALK.timezone("1402") == BERLIN
    assert CROSSWALK.timezone("HK30") == HKT
    assert CROSSWALK.sku_matnr[SKU] == "J20931A00012999"


def test_sap_stock_keeps_only_main_location_and_parses_decimal_commas() -> None:
    seen: list = []
    rows = [
        sap_row("0001", "0", "3,000"),
        sap_row("W100", "0", "14,000"),
        sap_row("RT01", "0", "2,000"),
        sap_row("0001", "1", "1.204,000"),
    ]
    c = client({"/warehouse/v1/stock": (200, {"positions": rows})}, seen)
    s = c.dc_stock("IT10", SKU, as_of=date(2026, 10, 16))
    assert seen[0].params["date"] == "2026-10-15"  # end of day D-1, certified on D
    assert dict(s.sellable_by_size) == {"0": 3, "1": 1204}
    assert s.snapshot_at == datetime(2026, 10, 15, 23, 59, 59, tzinfo=ROME)
    assert s.available_at == datetime(2026, 10, 16, 6, 0, tzinfo=ROME)  # RFC §4.3
    facts = s.stock_facts()
    assert [(f.size, f.qty, f.basis, f.ean) for f in facts] == [
        ("0", 3.0, "sellable", "800001276101"),
        ("1", 1204.0, "sellable", "800001276102"),
    ]
    assert facts[0].reservations_included is True and facts[0].quality_holds_included is False
    assert facts[0].source_ref.locator == "size=0"


def test_sap_us_dates_and_decimal_points() -> None:
    row = sap_row("0001", "0", "1,204.000", day="10/15/2026") | {"WERKS": "US20"}
    c = client({"/warehouse/v1/stock": (200, {"positions": [row]})})
    s = c.dc_stock("US20", SKU, as_of=date(2026, 10, 16))
    assert dict(s.sellable_by_size) == {"0": 1204}
    assert s.snapshot_at.tzinfo == ZoneInfo("America/New_York")


def test_sap_fractional_or_wrong_day_is_unparseable() -> None:
    c = client({"/warehouse/v1/stock": (200, {"positions": [sap_row("0001", "0", "1,500")]})})
    assert c.dc_stock("IT10", SKU, date(2026, 10, 16)).reason == "unparseable"
    c = client({"/warehouse/v1/stock": (200, {"positions": [sap_row("0001", "0", "1,000")]})})
    assert c.dc_stock("IT10", SKU, date(2026, 10, 20)).reason == "unparseable"


def test_missing_extraction_is_unknown_not_zero() -> None:
    body = {"positions": [], "note": "no rows (no extraction on Sundays at IT10)"}
    r = client({"/warehouse/v1/stock": (200, body)}).dc_stock("IT10", SKU, date(2026, 10, 19))
    assert r == Unknown("no_extraction", body["note"])


def hk_row(kind: str, available: str, when: str = "2026-10-16 06:17") -> dict:
    return {
        "Snapshot Time (HKT)": when,
        "Barcode": "800001276101",
        "Location Type": kind,
        "Available Qty": available,
    }


def test_hk_3pl_feed_sums_pick_and_reserve_by_barcode() -> None:
    rows = [hk_row("PICK", "57"), hk_row("RESERVE", "130"), hk_row("ECOM", "17")]
    c = client({"/warehouse/v1/stock": (200, {"positions": rows})})
    s = c.dc_stock("HK30", SKU, date(2026, 10, 16))
    assert dict(s.sellable_by_size) == {"0": 187}
    assert s.snapshot_at == s.available_at == datetime(2026, 10, 16, 6, 17, tzinfo=HKT)
    assert s.stock_facts()[0].reservations_included is False


def test_hk_morning_snapshot_covers_previous_day_and_repeats_are_stale() -> None:
    # Live mock: date 2026-10-20 -> snapshot 2026-10-21 06:24 HKT; on a missing day (date
    # 2026-10-18) the feed repeats 2026-10-18 06:18, which is the end of 2026-10-17.
    fresh = [hk_row("PICK", "5", when="2026-10-21 06:24")]
    s = client({"/warehouse/v1/stock": (200, {"positions": fresh})}).dc_stock(
        "HK30", SKU, date(2026, 10, 21)
    )
    assert (s.stock_date, s.stale) == (date(2026, 10, 20), False)
    repeated = [hk_row("PICK", "5", when="2026-10-18 06:18")]
    s = client({"/warehouse/v1/stock": (200, {"positions": repeated})}).dc_stock(
        "HK30", SKU, date(2026, 10, 19)
    )
    assert (s.stock_date, s.stale) == (date(2026, 10, 17), True)


def test_hk_fractional_quantity_is_unparseable() -> None:
    rows = [hk_row("PICK", "5.5", when="2026-10-16 06:17")]
    c = client({"/warehouse/v1/stock": (200, {"positions": rows})})
    assert c.dc_stock("HK30", SKU, date(2026, 10, 16)).reason == "unparseable"


def test_atp_without_a_row_for_the_size_is_unknown_not_zero() -> None:
    # Live mock: zero stock comes back as an explicit row with atp 0; no row = no record.
    snapshot = {"snapshot": "2026-10-19T06:00:00", "stale": False, "totalAtp": 0}
    c = client({"/warehouse/v1/atp": (200, snapshot | {"positions": []})})
    assert c.atp("IT10", SKU, date(2026, 10, 20), size="9").reason == "no_position"
    row = {
        "plant": "IT10",
        "size": "1",
        "unrestricted": 0,
        "openDeliveries": 0,
        "ecomReserve": 0,
        "blocked": 0,
        "atp": 0,
    }
    c = client({"/warehouse/v1/atp": (200, snapshot | {"positions": [row]})})
    assert c.atp("IT10", SKU, date(2026, 10, 20), size="0").reason == "no_position"
    zero = c.atp("IT10", SKU, date(2026, 10, 20), size="1")
    assert [f.qty for f in zero.stock_facts()] == [0.0]  # explicit zero stays zero


def test_no_lane_is_its_own_reason() -> None:
    # Live mock: GET /logistics/v1/lanes?origin=IT10&dest=IT10 -> 200 {"error": "NO_LANE"}
    c = client({"/logistics/v1/lanes": (200, {"error": "NO_LANE"})})
    assert c.lane("IT10", "MIL01", date(2026, 10, 20)).reason == "no_lane"


def test_hk_snapshot_after_as_of_is_rejected() -> None:
    rows = [hk_row("PICK", "5", when="2026-10-17 06:17")]
    c = client({"/warehouse/v1/stock": (200, {"positions": rows})})
    assert c.dc_stock("HK30", SKU, date(2026, 10, 16)).reason == "snapshot_after_as_of"


@pytest.mark.skipif(not EXAMPLES.exists(), reason="dataset not checked out")
def test_atp_from_official_example() -> None:
    seen: list = []
    c = client(
        {"/warehouse/v1/atp": (200, example("warehouse_get_atp_HK30_ILVARO510_20261022.json"))},
        seen,
    )
    a = c.atp("HK30", "J20931A00618-510", date(2026, 10, 22))
    assert seen[0].params["asOf"] == "2026-10-22"
    assert a.snapshot_at == datetime(2026, 10, 22, 6, 0, tzinfo=HKT)
    p = next(p for p in a.positions if p.size == "0")
    assert (p.atp, p.next_receipt_date, p.next_receipt_po) == (19, date(2026, 11, 20), "4500222417")
    fact = next(f for f in a.stock_facts() if f.size == "0")
    assert (fact.basis, fact.qty, fact.reservations_included) == ("atp", 19.0, False)


def test_atp_error_in_200_body_and_http_errors() -> None:
    body = {"error": "NO_SNAPSHOT", "message": "no ATP snapshot"}
    c = client({"/warehouse/v1/atp": (200, body)})
    assert c.atp("IT10", SKU, date(2026, 8, 1)) == Unknown("no_snapshot", "no ATP snapshot")
    for status, reason in [(429, "rate_limited"), (404, "not_found"), (503, "server_error")]:
        c = client({"/warehouse/v1/atp": (status, {"error": "x"})})
        assert c.atp("IT10", SKU, date(2026, 10, 1)).reason == reason


def test_unknown_inputs_and_unreachable_server() -> None:
    c = client({})
    assert c.atp("XX99", SKU, date(2026, 10, 1)).reason == "unknown_location"
    assert c.atp("IT10", "NOPE-000", date(2026, 10, 1)).reason == "unknown_sku"

    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    down = SystemsClient(CROSSWALK, transport=httpx.MockTransport(boom))
    assert down.dc_stock("IT10", SKU, date(2026, 10, 1)).reason == "unavailable"


@pytest.mark.skipif(not EXAMPLES.exists(), reason="dataset not checked out")
def test_lane_from_official_example_uses_crosswalk() -> None:
    seen: list = []
    c = client({"/logistics/v1/lanes": (200, example("logistics_get_lane_MIL02_MIL01.json"))}, seen)
    lane = c.lane("MIL02", "MIL01", date(2026, 10, 1))
    assert (seen[0].params["origin"], seen[0].params["dest"]) == ("1002", "1001")
    assert isinstance(lane, Lane)
    assert (lane.lane_id, lane.transit_days, lane.transit_days_p90) == ("LN-1002-1001", 0, 1)
    assert lane.pickup_days == frozenset(range(5)) and lane.pickup_cutoff == time(15, 30)
    assert lane.ibt_allowed is True and lane.customs_required is False
    assert lane.origin_tz == ROME
    assert not hasattr(lane, "observed_p50_days")  # not knowable in a replay


def test_lane_reviewed_after_as_of_is_unknown() -> None:
    body = example("logistics_get_lane_MIL02_MIL01.json") if EXAMPLES.exists() else {}
    c = client({"/logistics/v1/lanes": (200, body | {"last_reviewed": "2026-07-15"})})
    assert c.lane("MIL02", "MIL01", date(2026, 7, 1)).reason == "lane_reviewed_after_as_of"


def test_lane_ibt_note_kept() -> None:
    body = {
        "lane_id": "LN-IT10-3101",
        "origin": "IT10",
        "dest": "3101",
        "mode": "AIR_EXPRESS",
        "transit_days_contract": 5,
        "transit_days_p90_contract": 7,
        "pickup_cutoff_local": "14:00",
        "pickup_days": "MON-SAT",
        "customs_required": "Y",
        "ibt_allowed": "N (route via regional DC)",
        "last_reviewed": "2026-07-15",
    }
    lane = client({"/logistics/v1/lanes": (200, body)}).lane("IT10", "MIL01", date(2026, 10, 1))
    assert lane.ibt_allowed is False and lane.ibt_note == "N (route via regional DC)"
    assert lane.customs_required is True and lane.pickup_days == frozenset(range(6))


def lane(**kw) -> Lane:
    base = dict(
        lane_id="LN-1402-1101",
        origin="1402",
        dest="1101",
        origin_tz=BERLIN,
        mode="ROAD_EXPRESS",
        carrier=None,
        transit_days=2,
        transit_days_p90=4,
        pickup_cutoff=time(12, 0),
        pickup_days=frozenset(range(5)),
        customs_required=False,
        documents=None,
        ibt_allowed=True,
        ibt_note=None,
        cost_fixed_eur=None,
        cost_per_unit_eur=None,
        last_reviewed=date(2026, 7, 15),
        source_ref=None,
    )
    return Lane(**(base | kw))


def test_eta_before_cutoff_ships_same_day() -> None:
    e = eta(lane(), datetime(2026, 10, 8, 11, 0, tzinfo=BERLIN))  # Thursday
    assert e.pickup_at == datetime(2026, 10, 8, 12, 0, tzinfo=BERLIN) and not e.missed_cutoff
    assert (e.eta_date, e.eta_p90_date) == (date(2026, 10, 10), date(2026, 10, 12))


def test_eta_after_cutoff_on_friday_rolls_to_monday() -> None:
    e = eta(lane(), datetime(2026, 10, 9, 13, 0, tzinfo=BERLIN))
    assert e.missed_cutoff
    assert e.pickup_at.date() == date(2026, 10, 12)
    assert e.eta_date == date(2026, 10, 14)


def test_eta_uses_origin_local_time() -> None:
    # Berlin is UTC+2 in October: 09:30 UTC = 11:30 local, 10:30 UTC = 12:30 local
    assert not eta(lane(), datetime(2026, 10, 8, 9, 30, tzinfo=ZoneInfo("UTC"))).missed_cutoff
    e = eta(lane(), datetime(2026, 10, 8, 10, 30, tzinfo=ZoneInfo("UTC")))
    assert e.missed_cutoff and e.pickup_at.date() == date(2026, 10, 9)


def test_eta_weekend_and_bad_inputs() -> None:
    e = eta(lane(), datetime(2026, 10, 10, 9, 0, tzinfo=BERLIN))  # Saturday, not missed
    assert not e.missed_cutoff and e.pickup_at.date() == date(2026, 10, 12)
    assert eta(lane(pickup_days=frozenset()), datetime(2026, 10, 8, tzinfo=BERLIN)).reason == (
        "no_pickup_day"
    )
    with pytest.raises(ValueError):
        eta(lane(), datetime(2026, 10, 8, 9, 0))


def mocks_running() -> bool:
    try:
        return httpx.get("http://127.0.0.1:8088/logistics/v1/lanes", timeout=0.5).status_code > 0
    except httpx.HTTPError:
        return False


@pytest.mark.skipif(not mocks_running(), reason="`make mocks` not running")
def test_live_mock_server() -> None:
    master = REPO_ROOT / "generated" / "sources" / "erp" / "master_data"
    with (
        open(SYSTEMS / "reference" / "store_code_crosswalk_MDM.csv") as cw,
        open(master / "stores.csv") as st,
        open(master / "sku_size_ean.csv") as se,
    ):
        crosswalk = Crosswalk.from_rows(csv.DictReader(cw), csv.DictReader(st), csv.DictReader(se))
    c = SystemsClient(crosswalk)
    assert c.dc_stock("IT10", SKU, date(2026, 10, 19)).reason == "no_extraction"  # Sunday
    for plant in ("IT10", "US20", "HK30"):
        s = c.dc_stock(plant, SKU, date(2026, 10, 16))
        assert not isinstance(s, Unknown), (plant, s)
        assert s.stock_facts()
    assert c.atp("IT10", SKU, date(2026, 8, 1)).reason == "no_snapshot"
    assert c.atp("IT10", SKU, date(2026, 10, 15), size="1").stale is True
    assert isinstance(c.lane("BER01", "PAR01", date(2026, 10, 10)), Lane)
