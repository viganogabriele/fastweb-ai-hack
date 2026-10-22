"""Client for the simulated warehouse and logistics systems (RFC §4.11, ACT-04 pure).

Reads DC stock, ATP and lanes from the mock agents server (`make mocks`, :8088) and turns them
into `StockFact` and `Lane`, with the ID crosswalk from `systems/reference/`. The base URL is
configurable: never the `.example` host in the OpenAPI files.

Each system has its own quirks, handled here and nowhere else:
- SAP stock (IT10, US20): raw fields (`LGORT`, `LABST`...), IT dates `DD.MM.YYYY` with decimal
  commas, US dates `MM/DD/YYYY` with decimal points. Only storage location `0001` is sellable.
- 3PL feed (HK30): one row per location type (`PICK`, `RESERVE`, `ECOM`, `RETURNS`), size from
  the barcode, snapshot time in HKT.
- ATP: `asOf` returns the last snapshot on or before that day; snapshot times are plant-local.
- Errors can come back as HTTP 200 with an `error` field (`NO_SNAPSHOT`).
- Lanes have no time filter: a lane reviewed after `as_of` is `unknown`. Observed P50/P90 cover
  the whole period, so they are not knowable in a replay and are dropped (contract days only).

Anything missing, late, rate-limited or unparseable is `Unknown(reason)`, never zero or a guess.
Pure adapter: no DB, no repo. Wiring it to the repo is the ACT-04 module step.
"""

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, Literal
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import httpx

from tessera.core.contracts import SourceRef, StockFact

DC_TIMEZONES = {"IT10": "Europe/Rome", "US20": "America/New_York", "HK30": "Asia/Hong_Kong"}
DC_ALIASES = {"DC-IT-CSG": "IT10", "DC-US-NJ": "US20", "DC-HK-TKO": "HK30"}
SAP_SELLABLE_LGORT = "0001"
HK_SELLABLE_TYPES = frozenset({"PICK", "RESERVE"})
WEEKDAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")

UnknownReason = Literal[
    "bad_request",
    "lane_reviewed_after_as_of",
    "no_extraction",
    "no_pickup_day",
    "no_snapshot",
    "not_found",
    "rate_limited",
    "server_error",
    "snapshot_after_as_of",
    "unavailable",
    "unknown_location",
    "unknown_sku",
    "unparseable",
]


@dataclass(frozen=True)
class Unknown:
    reason: UnknownReason
    detail: str = ""


@dataclass(frozen=True)
class Crosswalk:
    """Store ids (MIL01) ↔ SAP plants (1001), DC plants and time zones, SKU ↔ MATNR, EAN."""

    store_plant: Mapping[str, str]  # MIL01 → 1001
    timezones: Mapping[str, str]  # store id or DC plant → IANA zone
    sku_matnr: Mapping[str, str]  # J20931A00012-999 → J20931A00012999
    ean_sku_size: Mapping[str, tuple[str, str]]  # 800001276101 → (sku, size)

    @classmethod
    def from_rows(
        cls,
        crosswalk_rows: Iterable[Mapping[str, str]],
        store_rows: Iterable[Mapping[str, str]],
        sku_size_rows: Iterable[Mapping[str, str]],
    ) -> "Crosswalk":
        """From `store_code_crosswalk_MDM.csv`, `stores.csv` and `sku_size_ean.csv` rows."""
        store_plant = {r["store_id"]: r["sap_plant_werks"] for r in crosswalk_rows}
        timezones = {r["store_id"]: r["timezone"] for r in store_rows} | DC_TIMEZONES
        sku_matnr: dict[str, str] = {}
        ean: dict[str, tuple[str, str]] = {}
        for r in sku_size_rows:
            sku_matnr[r["sku"]] = r["sku"].replace("-", "")
            if r.get("ean"):
                ean[r["ean"]] = (r["sku"], r["size"])
        if len(set(sku_matnr.values())) != len(sku_matnr):
            raise ValueError("SKU → MATNR mapping is not one-to-one")
        return cls(store_plant, timezones, sku_matnr, ean)

    def plant(self, location: str) -> str | None:
        """SAP/TMS location code for a store id, DC plant or DC alias."""
        location = DC_ALIASES.get(location, location)
        if location in DC_TIMEZONES or location in self.store_plant.values():
            return location
        return self.store_plant.get(location)

    def timezone(self, location: str) -> ZoneInfo | None:
        location = DC_ALIASES.get(location, location)
        if location not in self.timezones:
            by_plant = {p: s for s, p in self.store_plant.items()}
            location = by_plant.get(location, location)
        tz = self.timezones.get(location)
        return ZoneInfo(tz) if tz else None


@dataclass(frozen=True)
class AtpPosition:
    plant: str
    sku: str
    size: str
    unrestricted: int
    open_deliveries: int
    ecom_reserve: int
    blocked: int
    atp: int
    next_receipt_date: date | None
    next_receipt_qty: int | None
    next_receipt_po: str | None


@dataclass(frozen=True)
class AtpSnapshot:
    snapshot_at: datetime
    stale: bool
    positions: tuple[AtpPosition, ...]
    source_ref: SourceRef

    def stock_facts(self) -> tuple[StockFact, ...]:
        return tuple(
            _stock_fact(
                p.plant,
                p.sku,
                p.size,
                None,
                self.snapshot_at,
                self.snapshot_at,
                "atp_snapshot_time",
                p.atp,
                "atp",
                False,
                False,
                self.source_ref,
            )
            for p in self.positions
        )


@dataclass(frozen=True)
class DcStockSnapshot:
    """Sellable DC stock per size: SAP `0001` unrestricted, or 3PL PICK + RESERVE available."""

    plant: str
    sku: str
    stock_date: date
    snapshot_at: datetime
    available_at: datetime
    sellable_by_size: Mapping[str, int]
    ean_by_size: Mapping[str, str]
    source_ref: SourceRef

    def stock_facts(self) -> tuple[StockFact, ...]:
        # SAP unrestricted still includes open deliveries; the 3PL "Available" is net of them.
        reservations = self.plant != "HK30"
        return tuple(
            _stock_fact(
                self.plant,
                self.sku,
                size,
                self.ean_by_size.get(size),
                self.snapshot_at,
                self.available_at,
                "dc_eod_stock_next_day" if reservations else "3pl_snapshot_time",
                qty,
                "sellable",
                reservations,
                False,
                self.source_ref,
            )
            for size, qty in sorted(self.sellable_by_size.items())
        )


@dataclass(frozen=True)
class Lane:
    lane_id: str
    origin: str
    dest: str
    origin_tz: ZoneInfo
    mode: str
    carrier: str | None
    transit_days: int  # contract, calendar days
    transit_days_p90: int | None  # contract
    pickup_cutoff: time
    pickup_days: frozenset[int]  # weekday numbers, Monday = 0
    customs_required: bool | None
    documents: str | None
    ibt_allowed: bool | None
    ibt_note: str | None
    cost_fixed_eur: float | None
    cost_per_unit_eur: float | None
    last_reviewed: date
    source_ref: SourceRef


@dataclass(frozen=True)
class Eta:
    pickup_at: datetime  # cut-off time on the pickup day, origin local time
    missed_cutoff: bool
    eta_date: date  # pickup day + contract transit days
    eta_p90_date: date | None
    basis: str = "contract_calendar_days"


def eta(lane: Lane, ready_at: datetime) -> Eta | Unknown:
    """First pickup at or after `ready_at` and the contract arrival dates.

    Ready after the cut-off, or on a non-pickup day, rolls to the next pickup day. Transit days
    are counted as calendar days (the lane matrix does not say otherwise): a declared assumption.
    """
    if ready_at.tzinfo is None:
        raise ValueError("ready_at must be timezone-aware")
    if not lane.pickup_days:
        return Unknown("no_pickup_day", lane.lane_id)
    local = ready_at.astimezone(lane.origin_tz)
    day, missed = local.date(), False
    if day.weekday() not in lane.pickup_days or local.time() > lane.pickup_cutoff:
        missed = local.time() > lane.pickup_cutoff and day.weekday() in lane.pickup_days
        day += timedelta(days=1)
        while day.weekday() not in lane.pickup_days:
            day += timedelta(days=1)
    pickup_at = datetime.combine(day, lane.pickup_cutoff, lane.origin_tz)
    p90 = day + timedelta(days=lane.transit_days_p90) if lane.transit_days_p90 is not None else None
    return Eta(pickup_at, missed, day + timedelta(days=lane.transit_days), p90)


class SystemsClient:
    def __init__(
        self,
        crosswalk: Crosswalk,
        base_url: str = "http://127.0.0.1:8088",
        transport: httpx.BaseTransport | None = None,
        timeout_s: float = 10.0,
    ) -> None:
        self.crosswalk = crosswalk
        self._http = httpx.Client(base_url=base_url, transport=transport, timeout=timeout_s)

    def close(self) -> None:
        self._http.close()

    def atp(
        self, plant: str, sku: str, as_of: date, size: str | None = None
    ) -> AtpSnapshot | Unknown:
        """Last ATP snapshot of one DC on or before `as_of`. One plant per call: the snapshot
        time is plant-local, so `plant=ALL` would have no single meaning."""
        plant = DC_ALIASES.get(plant, plant)
        tz = self.crosswalk.timezone(plant)
        matnr = self.crosswalk.sku_matnr.get(sku)
        if plant not in DC_TIMEZONES or tz is None:
            return Unknown("unknown_location", plant)
        if matnr is None:
            return Unknown("unknown_sku", sku)
        params = {"plant": plant, "material": matnr, "asOf": as_of.isoformat()}
        if size is not None:
            params["size"] = size
        got = self._get("/warehouse/v1/atp", params)
        if isinstance(got, Unknown):
            return got
        body, ref = got
        try:
            positions = tuple(self._atp_position(p, sku) for p in body["positions"])
            if any(p.plant != plant for p in positions):
                return Unknown("unparseable", f"ATP positions for another plant than {plant}")
            snapshot_at = datetime.fromisoformat(body["snapshot"]).replace(tzinfo=tz)
        except (KeyError, TypeError, ValueError) as e:
            return Unknown("unparseable", repr(e))
        if snapshot_at.date() > as_of:
            return Unknown("snapshot_after_as_of", snapshot_at.isoformat())
        return AtpSnapshot(snapshot_at, bool(body.get("stale")), positions, ref)

    def dc_stock(self, plant: str, sku: str, as_of: date) -> DcStockSnapshot | Unknown:
        """End-of-day DC stock of `as_of - 1`: the latest day certified on the evening of
        `as_of`. A missing extraction (e.g. Sundays at IT10) is `no_extraction`."""
        plant = DC_ALIASES.get(plant, plant)
        tz = self.crosswalk.timezone(plant)
        matnr = self.crosswalk.sku_matnr.get(sku)
        if plant not in DC_TIMEZONES or tz is None:
            return Unknown("unknown_location", plant)
        if matnr is None:
            return Unknown("unknown_sku", sku)
        stock_date = as_of - timedelta(days=1)
        got = self._get(
            "/warehouse/v1/stock",
            {"plant": plant, "material": matnr, "date": stock_date.isoformat()},
        )
        if isinstance(got, Unknown):
            return got
        body, ref = got
        rows = body.get("positions") or []
        if not rows:
            return Unknown("no_extraction", str(body.get("note", "")))
        try:
            if plant == "HK30":
                return self._hk_stock(rows, plant, sku, stock_date, as_of, tz, ref)
            return self._sap_stock(rows, plant, sku, stock_date, tz, ref)
        except (KeyError, TypeError, ValueError) as e:
            return Unknown("unparseable", repr(e))

    def lane(self, origin: str, dest: str, as_of: date) -> Lane | Unknown:
        o, d = self.crosswalk.plant(origin), self.crosswalk.plant(dest)
        if o is None or d is None:
            return Unknown("unknown_location", f"{origin}->{dest}")
        tz = self.crosswalk.timezone(o)
        if tz is None:
            return Unknown("unknown_location", origin)
        got = self._get("/logistics/v1/lanes", {"origin": o, "dest": d})
        if isinstance(got, Unknown):
            return got
        body, ref = got
        try:
            reviewed = date.fromisoformat(body["last_reviewed"])
            if reviewed > as_of:
                return Unknown("lane_reviewed_after_as_of", body["last_reviewed"])
            ibt = _yes_no(body.get("ibt_allowed"))
            note = str(body["ibt_allowed"]) if body.get("ibt_allowed") else None
            return Lane(
                lane_id=body["lane_id"],
                origin=body["origin"],
                dest=body["dest"],
                origin_tz=tz,
                mode=body["mode"],
                carrier=body.get("default_carrier"),
                transit_days=int(body["transit_days_contract"]),
                transit_days_p90=_opt_int(body.get("transit_days_p90_contract")),
                pickup_cutoff=time.fromisoformat(body["pickup_cutoff_local"]),
                pickup_days=_pickup_days(body.get("pickup_days")),
                customs_required=_yes_no(body.get("customs_required")),
                documents=body.get("documents"),
                ibt_allowed=ibt,
                ibt_note=note if note not in ("Y", "N") else None,
                cost_fixed_eur=_opt_float(body.get("cost_fixed_eur")),
                cost_per_unit_eur=_opt_float(body.get("cost_per_unit_eur")),
                last_reviewed=reviewed,
                source_ref=ref,
            )
        except (KeyError, TypeError, ValueError) as e:
            return Unknown("unparseable", repr(e))

    def _get(self, path: str, params: dict[str, str]) -> tuple[dict[str, Any], SourceRef] | Unknown:
        try:
            r = self._http.get(path, params=params)
        except httpx.HTTPError as e:
            return Unknown("unavailable", type(e).__name__)
        if r.status_code == 429:
            return Unknown("rate_limited", r.headers.get("retry-after", ""))
        if r.status_code == 404:
            return Unknown("not_found", r.text[:200])
        if 400 <= r.status_code < 500:
            return Unknown("bad_request", r.text[:200])
        if r.status_code >= 500:
            return Unknown("server_error", str(r.status_code))
        try:
            body = r.json()
        except json.JSONDecodeError:
            return Unknown("unparseable", "response is not JSON")
        if not isinstance(body, dict):
            return Unknown("unparseable", "response is not a JSON object")
        if "error" in body:
            reason: UnknownReason = (
                "no_snapshot" if body["error"] == "NO_SNAPSHOT" else "bad_request"
            )
            return Unknown(reason, str(body.get("message", body["error"])))
        uri = f"systems:{path}?{urlencode(sorted(params.items()))}"
        return body, SourceRef(uri=uri, content_hash=hashlib.sha256(r.content).hexdigest())

    def _atp_position(self, p: Mapping[str, Any], sku: str) -> AtpPosition:
        receipt = p.get("nextReceipt") or {}
        return AtpPosition(
            plant=p["plant"],
            sku=sku,
            size=str(p["size"]),
            unrestricted=int(p["unrestricted"]),
            open_deliveries=int(p["openDeliveries"]),
            ecom_reserve=int(p["ecomReserve"]),
            blocked=int(p["blocked"]),
            atp=int(p["atp"]),
            next_receipt_date=date.fromisoformat(receipt["date"]) if receipt.get("date") else None,
            next_receipt_qty=_opt_int(receipt.get("qty")),
            next_receipt_po=receipt.get("po"),
        )

    def _sap_stock(
        self,
        rows: list[dict[str, Any]],
        plant: str,
        sku: str,
        stock_date: date,
        tz: ZoneInfo,
        ref: SourceRef,
    ) -> DcStockSnapshot | Unknown:
        sellable: dict[str, int] = {}
        eans: dict[str, str] = {}
        for row in rows:
            if _sap_date(row["STICHTAG"], plant) != stock_date:
                return Unknown("unparseable", f"STICHTAG {row['STICHTAG']} != {stock_date}")
            size = str(row["J_3ASIZE"])
            sellable.setdefault(size, 0)
            if row.get("EAN11"):
                eans[size] = row["EAN11"]
            if row["LGORT"] == SAP_SELLABLE_LGORT:
                sellable[size] += _sap_qty(row["LABST"], plant)
        snapshot_at = datetime.combine(stock_date, time(23, 59, 59), tz)
        available_at = datetime.combine(stock_date + timedelta(days=1), time(0), tz)
        return DcStockSnapshot(
            plant, sku, stock_date, snapshot_at, available_at, sellable, eans, ref
        )

    def _hk_stock(
        self,
        rows: list[dict[str, Any]],
        plant: str,
        sku: str,
        stock_date: date,
        as_of: date,
        tz: ZoneInfo,
        ref: SourceRef,
    ) -> DcStockSnapshot | Unknown:
        sellable: dict[str, int] = {}
        eans: dict[str, str] = {}
        times = set()
        for row in rows:
            hit = self.crosswalk.ean_sku_size.get(str(row["Barcode"]))
            if hit is None or hit[0] != sku:
                return Unknown("unknown_sku", f"barcode {row['Barcode']}")
            size = hit[1]
            eans[size] = str(row["Barcode"])
            sellable.setdefault(size, 0)
            times.add(row["Snapshot Time (HKT)"])
            if row["Location Type"] in HK_SELLABLE_TYPES:
                sellable[size] += int(float(row["Available Qty"]))
        if len(times) != 1:
            return Unknown("unparseable", f"{len(times)} snapshot times in one feed")
        snapshot_at = datetime.strptime(times.pop(), "%Y-%m-%d %H:%M").replace(tzinfo=tz)
        if snapshot_at.date() > as_of:
            return Unknown("snapshot_after_as_of", snapshot_at.isoformat())
        return DcStockSnapshot(
            plant, sku, stock_date, snapshot_at, snapshot_at, sellable, eans, ref
        )


def _stock_fact(
    plant: str,
    sku: str,
    size: str,
    ean: str | None,
    snapshot_at: datetime,
    available_at: datetime,
    availability_basis: str,
    qty: int,
    basis: Literal["on_hand", "sellable", "atp"],
    reservations_included: bool | None,
    quality_holds_included: bool | None,
    ref: SourceRef,
) -> StockFact:
    ref = SourceRef(uri=ref.uri, content_hash=ref.content_hash, locator=f"size={size}")
    return StockFact(
        id=f"stock:{plant}:{sku}-{size}:{basis}:{snapshot_at.isoformat()}",
        version=ref.content_hash[:16],
        available_at=available_at,
        availability_basis=availability_basis,
        source_refs=(ref,),
        location_id=plant,
        sku=sku,
        size=size,
        ean=ean,
        snapshot_at=snapshot_at,
        qty=float(qty),
        basis=basis,
        reservations_included=reservations_included,
        quality_holds_included=quality_holds_included,
        source_ref=ref,
    )


def _sap_date(value: str, plant: str) -> date:
    fmt = "%m/%d/%Y" if plant == "US20" else "%d.%m.%Y"
    return datetime.strptime(value, fmt).date()


def _sap_qty(value: str, plant: str) -> int:
    """'14,000' (IT) / '14.000' (US) with three decimals → 14. Fractions are rejected."""
    whole, _, frac = value.rpartition("." if plant == "US20" else ",")
    whole = re.sub(r"[.,' ]", "", whole)
    if frac.strip("0"):
        raise ValueError(f"fractional stock quantity {value!r}")
    return int(whole or "0")


def _pickup_days(value: object) -> frozenset[int]:
    text = str(value or "").upper().replace(" ", "")
    if text in ("DAILY", "MON-SUN"):
        return frozenset(range(7))
    days: set[int] = set()
    for part in filter(None, text.split(",")):
        start, _, end = part.partition("-")
        if start not in WEEKDAYS or end and end not in WEEKDAYS:
            return frozenset()
        a, b = WEEKDAYS.index(start), WEEKDAYS.index(end or start)
        days.update(range(a, b + 1) if a <= b else [*range(a, 7), *range(0, b + 1)])
    return frozenset(days)


def _yes_no(value: object) -> bool | None:
    text = str(value or "").strip().upper()
    return True if text.startswith("Y") else False if text.startswith("N") else None


def _opt_int(value: object) -> int | None:
    return None if value is None else int(value)


def _opt_float(value: object) -> float | None:
    return None if value is None else float(value)
