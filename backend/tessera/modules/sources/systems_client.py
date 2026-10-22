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
- Errors can come back as HTTP 200 with an `error` field (`NO_SNAPSHOT`, `NO_LANE`).
- ATP lists zero-stock sizes as explicit rows, so a missing row means "no record", not zero.
- SAP end-of-day stock is published at 06:00 local the next day (RFC §4.3 prototype convention).
  The 3PL snapshot taken on the morning of D+1 is the stock at the end of D; on missing days the
  feed repeats the previous snapshot, flagged `stale`.
- Lanes have no time filter: a lane reviewed after `as_of` is `unknown`. Observed P50/P90 cover
  the whole period, so they are not knowable in a replay and are dropped (contract days only).

Anything missing, late, rate-limited or unparseable is `Unknown(reason)`, never zero or a guess.

ACT-04 module (`sys.client`, bottom of this file): `run(ctx)` builds the crosswalk from the ERP
master rows known at `as_of` (so it requires `src.erp`), asks each supplying DC of the run's
stores for DC stock and ATP of the run's assortment, and stores the facts already available at
`as_of` as `StockFact`. `SystemsReader` is the read side for the investigator tools: stock per
location from the repo (DC facts, store stock from the ERP rows), lanes and ETA from the client,
both seen at the run's `as_of`. Clients are always built from the crosswalk of the run's `as_of`
(`ctx.clients["systems"]` is a factory, not a client), so no master data leaks across runs.
"""

import csv
import hashlib
import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from time import sleep as _sleep
from typing import Any, Literal, Protocol
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import httpx

from tessera.core import repo
from tessera.core.config import get_settings
from tessera.core.contracts import ModuleManifest, ModuleResult, RunSpec, SourceRef, StockFact

DC_TIMEZONES = {"IT10": "Europe/Rome", "US20": "America/New_York", "HK30": "Asia/Hong_Kong"}
DC_ALIASES = {"DC-IT-CSG": "IT10", "DC-US-NJ": "US20", "DC-HK-TKO": "HK30"}
SAP_SELLABLE_LGORT = "0001"
HK_SELLABLE_TYPES = frozenset({"PICK", "RESERVE"})
WEEKDAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
EOD_PUBLISHED_AT = time(6, 0)  # local time on the next day, RFC §4.3
BODY_ERRORS: dict[str, "UnknownReason"] = {
    "NO_SNAPSHOT": "no_snapshot",
    "NO_LANE": "no_lane",
    "NO_FILE": "no_extraction",  # 3PL feed of that day not (yet) delivered
}

UnknownReason = Literal[
    "bad_request",
    "not_loaded",
    "lane_reviewed_after_as_of",
    "no_extraction",
    "no_lane",
    "no_pickup_day",
    "no_position",
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
    stale: bool = False  # the feed repeated an older snapshot than the requested day

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
            if not positions or (size is not None and all(p.size != size for p in positions)):
                return Unknown("no_position", f"{plant} {sku} size={size}")
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
            reason = BODY_ERRORS.get(body["error"], "bad_request")
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
        available_at = datetime.combine(stock_date + timedelta(days=1), EOD_PUBLISHED_AT, tz)
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
                sellable[size] += _whole_units(row["Available Qty"])
        if len(times) != 1:
            return Unknown("unparseable", f"{len(times)} snapshot times in one feed")
        snapshot_at = datetime.strptime(times.pop(), "%Y-%m-%d %H:%M").replace(tzinfo=tz)
        if snapshot_at.date() > as_of:
            return Unknown("snapshot_after_as_of", snapshot_at.isoformat())
        covers = snapshot_at.date() - timedelta(days=1)  # morning of D+1 = end of day D
        return DcStockSnapshot(
            plant, sku, covers, snapshot_at, snapshot_at, sellable, eans, ref, covers < stock_date
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


def _whole_units(value: object) -> int:
    qty = float(str(value).replace(",", ""))
    if qty < 0 or qty != int(qty):
        raise ValueError(f"stock quantity must be a whole number >= 0, got {value!r}")
    return int(qty)


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


# ACT-04 module (`sys.client`): DC stock and ATP of the run's scope, stored as `StockFact`.

CROSSWALK_FILE = Path("systems") / "reference" / "store_code_crosswalk_MDM.csv"
DEFAULT_LOOKBACK_DAYS = 3
RATE_LIMIT_RETRIES = 2
MAX_RETRY_AFTER_S = 5.0
# Reasons worth asking an earlier day for: the day exists but is not (yet) usable.
_EARLIER_DAY = frozenset({"no_extraction", "snapshot_after_as_of"})
# The service failed or answered garbage: errors (run degraded), distinct from "no record".
_FAILURES = frozenset(
    {"unavailable", "rate_limited", "server_error", "bad_request", "not_found", "unparseable"}
)
_RESULT_LINE = re.compile(r"(dc_stock|atp) (\S+) (\S+): (\w+)")

ClientFactory = Callable[[Crosswalk], "SystemsClient"]

MANIFEST = ModuleManifest(
    id="sys.client",
    version="1",
    layer="sources",
    description=(
        "DC stock and ATP from the simulated warehouse systems for the run's assortment and "
        "supplying DCs, stored as StockFact when available at as_of"
    ),
    requires=("src.erp",),
    optional_inputs=(),
    produces=("StockFact",),
    enabled=True,
    mode="live",
    boundary="simulated",
    params_schema={
        "type": "object",
        "properties": {
            "skus": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
            "plants": {
                "type": "array",
                "items": {"enum": sorted(DC_TIMEZONES)},
                "uniqueItems": True,
            },
            "lookback_days": {"type": "integer", "minimum": 0, "maximum": 14},
        },
        "additionalProperties": False,
    },
)


class Context(Protocol):
    """The part of PLT-04's `RunContext` this module uses."""

    @property
    def spec(self) -> RunSpec: ...
    @property
    def repo(self) -> repo.Repo: ...
    @property
    def params(self) -> Mapping[str, Any]: ...
    @property
    def clients(self) -> Mapping[str, Any]: ...


def crosswalk_rows(sources_dir: Path) -> tuple[list[dict[str, str]], dict[str, str]]:
    """MDM crosswalk rows and each store's supplying DC plant (`DC-IT-CSG` → `IT10`)."""
    with open(sources_dir / CROSSWALK_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    supplying = {
        r["store_id"]: DC_ALIASES.get(r["supplying_dc"], r["supplying_dc"])
        for r in rows
        if r.get("supplying_dc")
    }
    return rows, supplying


def default_client(crosswalk: Crosswalk) -> "SystemsClient":
    return SystemsClient(crosswalk, base_url=get_settings().mocks_base_url)


def crosswalk_at(run_repo: repo.Repo, rows: Iterable[Mapping[str, str]]) -> Crosswalk | Unknown:
    """Crosswalk from the MDM rows plus the ERP stores and EANs known at the run's `as_of`."""
    stores = [{k: str(v) for k, v in r.data.items()} for r in run_repo.erp("stores")]
    sizes = [{k: str(v) for k, v in r.data.items()} for r in run_repo.erp("sku_size_ean")]
    if not stores or not sizes:
        return Unknown("not_loaded", "ERP stores / sku_size_ean not available at as_of")
    return Crosswalk.from_rows(rows, stores, sizes)


def latest_facts(
    fetch: Callable[[str, str, date], "AtpSnapshot | DcStockSnapshot | Unknown"],
    plant: str,
    sku: str,
    as_of: datetime,
    tz: ZoneInfo,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> tuple[tuple[StockFact, ...], bool] | Unknown:
    """Facts of the latest day already available at the instant `as_of`, and its stale flag.

    The client works on plant-local days; a day whose snapshot is published after `as_of`
    (early morning replays), or that has no extraction, falls back to an earlier day, at most
    `lookback_days` back. Facts keep their own `snapshot_at`: consumers see how old they are.
    """
    day = as_of.astimezone(tz).date()
    last: Unknown = Unknown("not_loaded", f"{plant} {sku}")
    for back in range(lookback_days + 1):
        got = fetch(plant, sku, day - timedelta(days=back))
        if isinstance(got, Unknown):
            if got.reason not in _EARLIER_DAY:
                return got
            last = got
            continue
        facts = tuple(f for f in got.stock_facts() if f.available_at <= as_of)
        if facts:
            return facts, got.stale
        last = Unknown("snapshot_after_as_of", f"{plant} {sku} {got.snapshot_at.isoformat()}")
    return last


def patient(
    fetch: Callable[[str, str, date], Any],
    sleep: Callable[[float], None] = _sleep,
    retries: int = RATE_LIMIT_RETRIES,
) -> Callable[[str, str, date], Any]:
    """Retry a rate-limited request a bounded number of times, honouring `Retry-After`."""

    def call(plant: str, sku: str, day: date) -> Any:
        for attempt in range(retries + 1):
            got = fetch(plant, sku, day)
            limited = isinstance(got, Unknown) and got.reason == "rate_limited"
            if not limited or attempt == retries:
                return got
            try:
                wait = float(got.detail or 1.0)
            except ValueError:
                wait = 1.0
            sleep(min(max(wait, 0.0), MAX_RETRY_AFTER_S))
        raise AssertionError("unreachable")

    return call


def load_stock(
    run_repo: repo.Repo,
    client: SystemsClient,
    skus: Iterable[str],
    plants: Iterable[str],
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    sleep: Callable[[float], None] = _sleep,
) -> ModuleResult:
    """DC stock and ATP for every plant × SKU, stored in the run when known at `as_of`.

    A plant still rate-limited after the retries is not asked again in this run: its remaining
    SKUs are recorded as `rate_limited` errors without a request.
    """
    as_of = run_repo.spec.as_of
    facts: list[StockFact] = []
    abstentions: list[str] = []
    errors: list[str] = []
    calls = stale = 0
    for plant in sorted(set(plants)):
        tz = client.crosswalk.timezone(plant)
        if tz is None:
            errors.append(f"{plant}: unknown_location")
            continue
        limited = False
        fetches = (
            ("dc_stock", patient(client.dc_stock, sleep)),
            ("atp", patient(client.atp, sleep)),
        )
        for sku in sorted(set(skus)):
            for name, fetch in fetches:
                if limited:
                    got: Any = Unknown("rate_limited", "not requested")
                else:
                    calls += 1
                    got = latest_facts(fetch, plant, sku, as_of, tz, lookback_days)
                if isinstance(got, Unknown):
                    line = f"{name} {plant} {sku}: {got.reason}"
                    (errors if got.reason in _FAILURES else abstentions).append(line)
                    limited = limited or got.reason == "rate_limited"
                    continue
                facts.extend(got[0])
                stale += got[1]
    new = run_repo.put(*facts) if facts else 0
    status = "degraded" if errors or not facts else "succeeded"
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status=status,
        counts={
            "requests": calls,
            "stock_facts": len(facts),
            "stock_facts_new": new,
            "stale_snapshots": stale,
            "unknown": len(abstentions) + len(errors),
        },
        errors=tuple(errors),
        abstentions=tuple(abstentions),
    )


def run(ctx: Context) -> ModuleResult:
    params = ctx.params
    rows, supplying = crosswalk_rows(get_settings().sources_dir)
    crosswalk = crosswalk_at(ctx.repo, rows)
    if isinstance(crosswalk, Unknown):
        return _blocked(crosswalk.detail)
    plants = params.get("plants") or sorted(
        {supplying[s] for s in ctx.spec.stores if s in supplying}
    )
    skus = params.get("skus") or sorted(
        {str(r.data["sku"]) for store in ctx.spec.stores for r in _assortment(ctx.repo, store)}
    )
    if not plants or not skus:
        return _blocked(f"no supplying DC ({len(plants)}) or assortment SKU ({len(skus)}) at as_of")
    factory: ClientFactory = ctx.clients.get("systems", default_client)
    client = factory(crosswalk)
    try:
        return load_stock(
            ctx.repo, client, skus, plants, params.get("lookback_days", DEFAULT_LOOKBACK_DAYS)
        )
    finally:
        client.close()


def _assortment(run_repo: repo.Repo, store: str) -> list[repo.ErpRecord]:
    return run_repo.erp("assortment", store_id=store)


def _blocked(reason: str) -> ModuleResult:
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="blocked",
        counts={},
        errors=(reason,),
        abstentions=(),
    )


# Read side for the investigator tools (`get_available_stock`, `get_lane_and_eta`).


@dataclass(frozen=True)
class LaneEta:
    lane: Lane
    eta: Eta
    on_time: bool | None  # contract ETA by `required_by` (dest-local day); None if not asked
    on_time_p90: bool | None


class SystemsReader:
    """Stock and lanes as seen at the run's `as_of`. Never writes, never reads past `as_of`.

    DC stock and ATP come from the `StockFact` stored by `sys.client`; store stock from the ERP
    `stock` rows (end-of-day `on_hand`), only for the run's stores. When a DC has no fact, the
    reason recorded by `sys.client` (e.g. `unavailable`, `rate_limited`, `no_position`) is
    returned, so a service failure never reads like "no stock". Lanes are read through the
    client, which drops a lane reviewed after `as_of` and the observed P50/P90.
    """

    def __init__(self, run_repo: repo.Repo, client: SystemsClient) -> None:
        self.repo = run_repo
        self.client = client
        self._reasons: dict[tuple[str, str], str] | None = None

    @classmethod
    def open(
        cls, run_repo: repo.Repo, factory: ClientFactory = default_client
    ) -> "SystemsReader | Unknown":
        """Reader with a client built from the crosswalk known at the run's `as_of`."""
        rows, _ = crosswalk_rows(get_settings().sources_dir)
        crosswalk = crosswalk_at(run_repo, rows)
        return crosswalk if isinstance(crosswalk, Unknown) else cls(run_repo, factory(crosswalk))

    @property
    def as_of(self) -> datetime:
        return self.repo.spec.as_of

    def stock(
        self, sku: str, size: str, locations: Iterable[str]
    ) -> dict[str, tuple[StockFact, ...] | Unknown]:
        """Latest fact per basis for each location; `Unknown` if this run holds none."""
        out: dict[str, tuple[StockFact, ...] | Unknown] = {}
        for location in locations:
            plant = DC_ALIASES.get(location, location)
            if plant in DC_TIMEZONES:
                # DCs are not run stores: filter on the payload, not on the store index.
                where = {"location_id": plant, "size": size}
                facts = self.repo.list(StockFact, sku=sku, where=where)
            elif location in self.repo.spec.stores:
                facts = self._store_facts(location, sku, size)
                if isinstance(facts, Unknown):
                    out[location] = facts
                    continue
            else:
                out[location] = Unknown("unknown_location", f"{location} is not a DC or run store")
                continue
            latest: dict[str, StockFact] = {}
            for f in facts:
                if f.basis not in latest or f.snapshot_at > latest[f.basis].snapshot_at:
                    latest[f.basis] = f
            out[location] = (
                tuple(latest[b] for b in sorted(latest)) if latest else self._missing(plant, sku)
            )
        return out

    def _missing(self, location: str, sku: str) -> Unknown:
        detail = f"{location} {sku} at {self.as_of.isoformat()}"
        reason = self._recorded_reasons().get((location, sku))
        return Unknown(reason or "not_loaded", detail)

    def _recorded_reasons(self) -> dict[tuple[str, str], str]:
        """Why `sys.client` stored no fact, per (plant, SKU): failures win over abstentions."""
        if self._reasons is None:
            self._reasons = {}
            for module_run in repo.list_module_runs(self.repo.engine, self.repo.run_id):
                if module_run.module_id != MANIFEST.id or module_run.result is None:
                    continue
                result = module_run.result
                for line in (*result.abstentions, *result.errors):
                    if match := _RESULT_LINE.fullmatch(line):
                        _, plant, sku, reason = match.groups()
                        self._reasons[(plant, sku)] = reason
        return self._reasons

    def lane_and_eta(
        self,
        origin: str,
        dest: str,
        requested_at: datetime,
        required_by: datetime | None = None,
    ) -> LaneEta | Unknown:
        """Lane valid at `as_of` and the first pickup at or after `requested_at`."""
        if requested_at.tzinfo is None or (required_by and required_by.tzinfo is None):
            raise ValueError("requested_at and required_by must be timezone-aware")
        if requested_at < self.as_of:
            requested_at = self.as_of  # nothing can leave before the decision is taken
        origin_tz = self.client.crosswalk.timezone(origin)
        if origin_tz is None:
            return Unknown("unknown_location", origin)
        lane = self.client.lane(origin, dest, self.as_of.astimezone(origin_tz).date())
        if isinstance(lane, Unknown):
            return lane
        got = eta(lane, requested_at)
        if isinstance(got, Unknown):
            return got
        if required_by is None:
            return LaneEta(lane, got, None, None)
        dest_tz = self.client.crosswalk.timezone(dest)
        if dest_tz is None:
            return Unknown("unknown_location", f"{dest}: no time zone at as_of")
        due = required_by.astimezone(dest_tz).date()
        p90 = None if got.eta_p90_date is None else got.eta_p90_date <= due
        return LaneEta(lane, got, got.eta_date <= due, p90)

    def _store_facts(self, store: str, sku: str, size: str) -> list[StockFact] | Unknown:
        tz = self.client.crosswalk.timezone(store)
        if tz is None:
            return Unknown("unknown_location", f"{store}: no time zone at as_of")
        facts = []
        for row in self.repo.erp("stock", store_id=store, sku=sku):
            if str(row.data["size"]) != size or row.data.get("on_hand") is None:
                continue
            day = row.data["snapshot_date"]
            ref = row.source_refs[0]
            facts.append(
                StockFact(
                    id=f"stock:{store}:{sku}-{size}:on_hand:{day.isoformat()}",
                    version=row.version,
                    available_at=row.available_at,
                    availability_basis=row.availability_basis,
                    source_refs=(ref,),
                    location_id=store,
                    sku=sku,
                    size=size,
                    snapshot_at=datetime.combine(day, time(23, 59, 59), tz),
                    qty=float(row.data["on_hand"]),
                    basis="on_hand",
                    reservations_included=None,
                    quality_holds_included=None,
                    source_ref=ref,
                )
            )
        return facts
