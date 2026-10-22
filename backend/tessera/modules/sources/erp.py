"""ING-01 pure: typed ERP rows with provenance and replay availability (RFC §4.3).

``parse_rows`` has no I/O. ``load_csv`` reads a single explicitly selected source
file and returns only rows known at an aware ``as_of``. No folder discovery, DB,
LLM, or inferred demand. Sales money stays net/local and returns stay separate.

Undated master data requires a caller-declared ``master_available_at`` snapshot;
otherwise its availability is unknown and it is excluded from strict replay.
Launch/valid-from dates describe products/prices, not when their files were known.
Daily facts use next-day 06:00 in the store timezone; later posting wins. Forecast
uses explicit issued_at when present, otherwise run-date 06:00 local. These 06:00
times are prototype conventions, recorded in availability_basis, not source facts.

Money stays ``Decimal``. Forecast units are fractional quantities fed to FC-01, so
they are ``float`` (FC-01 accepts any real number, which ``Decimal`` is not).
Source URIs are relative to ``generated/sources`` (``erp/...``), so row ids are the
same in every checkout, worktree and CI run.

ING-01 module: ``MANIFEST`` + ``run(ctx)`` (``src.erp``) select the source files of
the run's window by their file-name date, load them through ``load_csv`` at the
run's ``as_of`` and store the rows in ``erp_rows`` via ``repo.put_erp``. Only rows
already available at ``as_of`` are written. ``read`` returns a run's rows: ``Repo.erp``
(the ``as_of`` filter) limited to the run's stores, window and master snapshot.
"""

import csv
import hashlib
import json
import math
import re
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, Protocol
from zoneinfo import ZoneInfo

from sqlalchemy import Engine, select

from tessera.core import repo
from tessera.core.config import get_settings
from tessera.core.contracts import ModuleManifest, ModuleResult, RunSpec
from tessera.core.contracts.common import SourceRef
from tessera.core.db import erp_rows

Table = Literal[
    "stores",
    "styles",
    "sku_colour",
    "sku_size_ean",
    "assortment",
    "prices",
    "sales",
    "stock",
    "forecast",
]
Value = str | int | float | Decimal | date | datetime | None

# Identifier fields remain strings: leading zero sizes, colours and EANs survive.
_KEYS = {
    "stores": ("store_id", "timezone"),
    "styles": ("style_code", "style_name"),
    "sku_colour": ("sku", "style_code", "color_code"),
    "sku_size_ean": ("sku", "size", "sku_size", "ean"),
    "assortment": ("store_id", "sku"),
    "prices": ("store_id", "sku", "currency", "retail_price", "valid_from"),
    "sales": (
        "store_id",
        "sku",
        "business_date",
        "currency",
        "units_sold",
        "units_returned",
        "gross_sales_lc",
        "discount_lc",
        "returns_lc",
        "net_sales_lc",
    ),
    "stock": ("store_id", "sku", "size", "snapshot_date", "on_hand", "in_transit"),
    "forecast": ("store_id", "sku", "run_date", "target_week", "week_start", "fcst_units"),
}
_DATES = {
    "business_date",
    "snapshot_date",
    "run_date",
    "week_start",
    "opening_date",
    "launch_date",
    "end_date",
    "valid_from",
    "posting_date",
}
_INTEGERS = {"units_sold", "units_returned", "on_hand", "in_transit"}
_DECIMALS = {
    "price_eur",
    "retail_price",
    "gross_sales_lc",
    "discount_lc",
    "returns_lc",
    "net_sales_lc",
}
_FLOATS = {"fcst_units"}
_INSTANTS = {"posted_at", "issued_at", "available_at"}


@dataclass(frozen=True)
class ERPRow:
    table: Table
    id: str
    version: str
    available_at: datetime | None
    availability_basis: str
    source_refs: tuple[SourceRef, ...]
    data: Mapping[str, Value]


def _aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("An aware datetime is required")
    return value.astimezone(UTC)


def _local_six(day: date, timezone: ZoneInfo) -> datetime:
    return datetime.combine(day, time(6), tzinfo=timezone).astimezone(UTC)


def _parse(field: str, value: str) -> Value:
    if not value:
        return None
    if field in _DATES:
        return date.fromisoformat(value)
    if field in _INSTANTS:
        return _aware(datetime.fromisoformat(value))
    if field in _INTEGERS:
        result = int(value)
        if result < 0:
            raise ValueError(f"{field} must be nonnegative")
        return result
    if field in _FLOATS:
        try:
            result = float(value)
        except ValueError as exc:
            raise ValueError(f"Invalid number for {field}") from exc
        if not math.isfinite(result) or result < 0:
            raise ValueError(f"Invalid finite amount for {field}")
        return result
    if field in _DECIMALS:
        try:
            result = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(f"Invalid decimal for {field}") from exc
        if not result.is_finite() or (field != "net_sales_lc" and result < 0):
            raise ValueError(f"Invalid finite amount for {field}")
        return result
    return value


def _availability(
    table: Table,
    data: Mapping[str, Value],
    store_timezones: Mapping[str, str],
    master_available_at: datetime | None,
) -> tuple[datetime | None, str]:
    if table not in {"sales", "stock", "forecast"}:
        available = master_available_at
        basis = "declared_master_snapshot" if available else "availability_unknown:undated_master"
        # An explicit per-row publication time supersedes the snapshot assumption.
        if isinstance(data.get("available_at"), datetime):
            return data["available_at"], "source:available_at"
        return available, basis
    store = str(data["store_id"])
    if store not in store_timezones:
        raise ValueError(f"Missing timezone for store {store}")
    timezone = ZoneInfo(store_timezones[store])
    if table == "forecast":
        if isinstance(data.get("issued_at"), datetime):
            available, basis = data["issued_at"], "source:issued_at"
            if available.astimezone(timezone).date() < data["run_date"]:
                raise ValueError("Forecast issued_at precedes run_date")
        else:
            available = _local_six(data["run_date"], timezone)
            basis = "assumed:run_date_06_local"
    else:
        field = "business_date" if table == "sales" else "snapshot_date"
        available = _local_six(data[field] + timedelta(days=1), timezone)
        basis = f"assumed:{field}_next_day_06_local"
    for field in ("posting_date", "posted_at", "available_at"):
        value = data.get(field)
        if value is None:
            continue
        instant = _local_six(value, timezone) if field == "posting_date" else value
        if instant > available:
            available = instant
            basis += f";later_source:{field}"
    return available, basis


def parse_rows(
    table: Table,
    rows: Iterable[Mapping[str, str]],
    *,
    source: SourceRef,
    store_timezones: Mapping[str, str],
    master_available_at: datetime | None = None,
    store_ids: frozenset[str] | None = None,
) -> tuple[ERPRow, ...]:
    """Parse selected rows; preserve all vintages and mark unknown availability.

    ``store_ids`` is an explicit caller-selected scope, applied before row parsing.
    Source locators are physical CSV record numbers (header = record 1), including
    skipped stores. Unknown extra columns are retained; malformed facts fail closed.
    """
    if table not in _KEYS:
        raise ValueError(f"Unsupported ERP table: {table}")
    if master_available_at is not None:
        master_available_at = _aware(master_available_at)
    result = []
    for record_number, raw in enumerate(rows, start=2):
        if store_ids is not None and "store_id" in raw and raw["store_id"] not in store_ids:
            continue
        try:
            if any(not isinstance(k, str) or not isinstance(v, str) for k, v in raw.items()):
                raise ValueError("Malformed CSV record")
            if any(not raw.get(key, "").strip() for key in _KEYS[table]):
                raise ValueError(f"Missing required {table} fields")
            data = {key: _parse(key, value.strip()) for key, value in raw.items()}
            if table == "stores":
                ZoneInfo(str(data["timezone"]))
            if table == "forecast":
                week = data["week_start"]
                if week.weekday() != 0 or week.strftime("%G-W%V") != data["target_week"]:
                    raise ValueError("Forecast week_start/target_week mismatch")
            available, basis = _availability(table, data, store_timezones, master_available_at)
            # Row content + physical provenance: duplicates stay distinct, versions
            # change with source content. Neither depends on the replay clock.
            payload = json.dumps(dict(raw), sort_keys=True, ensure_ascii=False).encode()
            version = hashlib.sha256(payload).hexdigest()
            identity = f"{table}:{source.uri}:record={record_number}"
            result.append(
                ERPRow(
                    table=table,
                    id=hashlib.sha256(identity.encode()).hexdigest(),
                    version=version,
                    available_at=available,
                    availability_basis=basis,
                    source_refs=(source.model_copy(update={"locator": f"record={record_number}"}),),
                    data=MappingProxyType(data),
                )
            )
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"{source.uri} record {record_number}: {exc}") from exc
    return tuple(result)


def rows_at_as_of(rows: Iterable[ERPRow], as_of: datetime) -> tuple[ERPRow, ...]:
    """Exclude future/unknown facts without changing the input (T1 → T2 → T1)."""
    cutoff = _aware(as_of)
    return tuple(row for row in rows if row.available_at is not None and row.available_at <= cutoff)


def latest_forecast(rows: Iterable[ERPRow], as_of: datetime) -> tuple[ERPRow, ...]:
    """Latest eligible vintage per store, preserving its target coverage.

    The vintage is chosen per store (runs become available at 06:00 store-local time),
    not per store × SKU: a SKU or week absent from the latest run stays missing and is
    never filled from an older run (the dataset drops SKUs between runs).
    """
    eligible = rows_at_as_of(rows, as_of)
    newest = {}
    for row in eligible:
        if row.table != "forecast":
            raise ValueError("latest_forecast accepts forecast rows only")
        store = row.data["store_id"]
        newest[store] = max(newest.get(store, date.min), row.data["run_date"])
    selected = {}
    for row in eligible:
        if row.data["run_date"] != newest[row.data["store_id"]]:
            continue
        key = tuple(row.data[k] for k in ("store_id", "sku", "week_start"))
        previous = selected.get(key)
        rank = (row.data["run_date"], row.available_at)
        if previous is None or rank > (previous.data["run_date"], previous.available_at):
            selected[key] = row
        elif (
            rank == (previous.data["run_date"], previous.available_at) and row.data != previous.data
        ):
            raise ValueError(f"Conflicting forecast rows for {key}")
    return tuple(selected[key] for key in sorted(selected))


def load_csv(
    relative: str,
    table: Table,
    *,
    sources_dir: Path,
    as_of: datetime,
    store_timezones: Mapping[str, str],
    master_available_at: datetime | None = None,
    store_ids: frozenset[str] | None = None,
) -> tuple[ERPRow, ...]:
    """Read one UTF-8 ERP CSV under sources/erp; filter before returning facts.

    ``sources_dir`` is the dataset's generated/sources directory (a temporary
    equivalent in tests). No derived files are written, and symlink escapes fail.
    """
    _aware(as_of)
    if table not in _KEYS:
        raise ValueError(f"Unsupported ERP table: {table}")
    sources_dir = sources_dir.resolve(strict=True)
    root = (sources_dir / "erp").resolve(strict=True)
    if not root.is_relative_to(sources_dir):
        raise ValueError("ERP directory must stay inside sources")
    path = (root / relative).resolve(strict=True)
    if not path.is_relative_to(root) or path.suffix != ".csv":
        raise ValueError("ERP input must be a CSV inside sources/erp")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        # Hash the same opened file used by DictReader, without buffering the dataset.
        content_hash = hashlib.file_digest(stream.buffer, "sha256").hexdigest()
        stream.seek(0)
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not set(_KEYS[table]) <= set(reader.fieldnames):
            raise ValueError("Missing ERP CSV columns")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Duplicate ERP CSV columns")
        rows = parse_rows(
            table,
            reader,
            source=SourceRef(
                uri=path.relative_to(sources_dir).as_posix(), content_hash=content_hash
            ),
            store_timezones=store_timezones,
            master_available_at=master_available_at,
            store_ids=store_ids,
        )
    return rows_at_as_of(rows, as_of)


# ING-01 module (`src.erp`): the run selects the stores, the window selects the files.

DEFAULT_HISTORY_DAYS = 28
# Undated master data needs a declared snapshot (RFC §4.3). Assumption: the FW26
# master files are known from the start of the replay data (first stock snapshot,
# first forecast run). Overridable, but a database holds one declared snapshot:
# a run declaring another one fails. Recorded as declared_master_snapshot.
DEFAULT_MASTER_AVAILABLE_AT = "2026-08-01T00:00:00+00:00"

_MASTER: tuple[tuple[str, Table], ...] = (
    ("master_data/stores.csv", "stores"),
    ("master_data/styles.csv", "styles"),
    ("master_data/sku_colour.csv", "sku_colour"),
    ("master_data/sku_size_ean.csv", "sku_size_ean"),
    ("master_data/store_assortment.csv", "assortment"),
    ("master_data/price_list_FW26.csv", "prices"),
)
# Folder, file-name prefix, table, date field, extra lookback. Forecast runs are
# weekly: one more week keeps the vintage valid at as_of even for a short window.
_FACTS: tuple[tuple[str, str, Table, str, timedelta], ...] = (
    ("sales/daily_store_sku", "sales_daily_", "sales", "business_date", timedelta()),
    ("inventory/store_stock_daily", "stock_eod_", "stock", "snapshot_date", timedelta()),
    ("forecast/sku_store_weekly", "fcst_sku_store_run_", "forecast", "run_date", timedelta(7)),
)
_FACT_DATES = {table: field for _, _, table, field, _ in _FACTS}
_DECLARED = "declared_master_snapshot"
_END_OF_TIME = datetime.max.replace(tzinfo=UTC)

MANIFEST = ModuleManifest(
    id="src.erp",
    version="1",
    layer="sources",
    description=(
        "ERP catalog, assortment, prices, daily sales, stock and forecast vintages for the "
        "run's stores and history window, each row with available_at"
    ),
    requires=(),
    optional_inputs=(),
    produces=("erp_rows",),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {
            "history_days": {"type": "integer", "minimum": 1, "maximum": 800},
            "master_available_at": {"type": "string", "format": "date-time"},
        },
        "additionalProperties": False,
    },
)


class Context(Protocol):
    """The part of PLT-04's ``RunContext`` this module uses."""

    @property
    def spec(self) -> RunSpec: ...
    @property
    def repo(self) -> repo.Repo: ...
    @property
    def params(self) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class Window:
    """The ERP rows one run of ``src.erp`` loads, a function of its ``RunSpec`` alone.

    Daily facts cover ``history_days`` before ``D_store``, the ``as_of`` date in the
    store's timezone (RFC §4.3); forecast one week more. Rows declared available at
    the master snapshot belong to the window only if that is this run's snapshot.
    """

    as_of: datetime
    stores: frozenset[str]
    snapshot: datetime
    zones: Mapping[str, str]
    oldest: Mapping[tuple[str, str], date]

    def keeps(self, row: ERPRow | repo.ErpRecord) -> bool:
        if row.available_at is None or row.available_at > self.as_of:
            return False
        store = row.data.get("store_id")
        if store is not None and store not in self.stores:
            return False
        if row.table in _FACT_DATES:
            return row.data[_FACT_DATES[row.table]] >= self.oldest[row.table, store]
        return row.availability_basis != _DECLARED or row.available_at == self.snapshot


def run_params(spec: RunSpec) -> Mapping[str, Any]:
    """The ``src.erp`` params frozen in the run's module snapshot (empty if none)."""
    for module in spec.modules:
        if module.manifest.id == MANIFEST.id:
            return module.params
    return {}


def window(spec: RunSpec, params: Mapping[str, Any], *, sources_dir: Path) -> Window:
    as_of = _aware(spec.as_of)
    history = timedelta(days=params.get("history_days", DEFAULT_HISTORY_DAYS))
    snapshot = _aware(
        datetime.fromisoformat(params.get("master_available_at", DEFAULT_MASTER_AVAILABLE_AT))
    )
    stores = frozenset(spec.stores)
    # Timezones date the facts, so they are read whatever the snapshot.
    store_rows = load_csv(
        "master_data/stores.csv",
        "stores",
        sources_dir=sources_dir,
        as_of=_END_OF_TIME,
        store_timezones={},
        master_available_at=snapshot,
        store_ids=stores,
    )
    zones = {str(row.data["store_id"]): str(row.data["timezone"]) for row in store_rows}
    if missing := stores - zones.keys():
        raise ValueError(f"Stores not in stores.csv: {', '.join(sorted(missing))}")
    oldest = {
        (table, store): as_of.astimezone(ZoneInfo(zone)).date() - history - lookback
        for _, _, table, _, lookback in _FACTS
        for store, zone in zones.items()
    }
    return Window(as_of, stores, snapshot, MappingProxyType(zones), MappingProxyType(oldest))


def _check_master_snapshot(engine: Engine, snapshot: datetime) -> None:
    """One master snapshot per database: ``put_erp`` keeps the first availability seen.

    Row versions hash source content only, so a second declaration would be silently
    dropped (or would expose masters to a run that declared a later snapshot).
    """
    query = select(erp_rows.c.available_at).where(erp_rows.c.availability_basis == _DECLARED)
    with engine.connect() as conn:
        declared = set(conn.execute(query.distinct()).scalars())
    if conflicting := declared - {snapshot}:
        stored = ", ".join(sorted(instant.isoformat() for instant in conflicting))
        raise ValueError(
            f"erp_rows already holds master data declared available at {stored}; "
            f"this run declares {snapshot.isoformat()}"
        )


def _files(sources_dir: Path, folder: str, prefix: str) -> Iterator[tuple[str, date, date]]:
    """Files of a partitioned folder with the first and last day their name covers."""
    pattern = re.compile(re.escape(prefix) + r"(\d{4})[_-](\d{2})(?:-(\d{2}))?\.csv")
    for path in sorted((sources_dir / "erp" / folder).glob(f"{prefix}*.csv")):
        match = pattern.fullmatch(path.name)
        if match is None:
            raise ValueError(f"Unexpected ERP file name: {folder}/{path.name}")
        year, month, day = (int(part) if part else None for part in match.groups())
        if day is None:
            first = date(year, month, 1)
            last = (first + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        else:
            first = last = date(year, month, day)
        yield f"{folder}/{path.name}", first, last


def load_window(
    engine: Engine, spec: RunSpec, params: Mapping[str, Any], *, sources_dir: Path
) -> dict[str, int]:
    """Write the ERP rows of the run's ``window`` to ``erp_rows``.

    Files named after a day no row of which can be known yet are not opened;
    ``load_csv`` drops every row not available at ``as_of``. Returns, per table, the
    rows loaded and how many were new to ``erp_rows``.
    """
    scope = window(spec, params, sources_dir=sources_dir)
    _check_master_snapshot(engine, scope.snapshot)
    batches = {
        table: load_csv(
            relative,
            table,
            sources_dir=sources_dir,
            as_of=scope.as_of,
            store_timezones=scope.zones,
            master_available_at=scope.snapshot,
            store_ids=scope.stores,
        )
        for relative, table in _MASTER
    }
    # Facts of day D become known at the earliest on D (stock/sales, UTC+14) or D - 1
    # (forecast run D) in UTC, so later file names can't hold a visible row.
    newest = scope.as_of.date() + timedelta(days=1)
    for folder, prefix, table, _, _ in _FACTS:
        oldest = min(scope.oldest[table, store] for store in scope.stores)
        rows: list[ERPRow] = []
        for relative, first, last in _files(sources_dir, folder, prefix):
            if last < oldest or first > newest:
                continue
            loaded = load_csv(
                relative,
                table,
                sources_dir=sources_dir,
                as_of=scope.as_of,
                store_timezones=scope.zones,
                store_ids=scope.stores,
            )
            rows.extend(row for row in loaded if scope.keeps(row))
        batches[table] = tuple(rows)
    counts = {}
    for table, rows in batches.items():
        counts[f"{table}_rows"] = len(rows)
        counts[f"{table}_new"] = repo.put_erp(engine, rows)
    return counts


def read(
    run_repo: repo.Repo,
    table: Table,
    *,
    store_id: str | None = None,
    sku: str | None = None,
    sources_dir: Path | None = None,
) -> list[repo.ErpRecord]:
    """The run's ERP rows: ``Repo.erp`` limited to the ``window`` this run loaded.

    ``erp_rows`` is shared by all runs, so ``Repo.erp`` alone also returns rows that
    other runs loaded (other stores, older days). The window comes from the run's
    ``RunSpec``, so a read gives the same rows whatever is loaded later.
    """
    scope = window(
        run_repo.spec,
        run_params(run_repo.spec),
        sources_dir=sources_dir or get_settings().sources_dir,
    )
    return [row for row in run_repo.erp(table, store_id=store_id, sku=sku) if scope.keeps(row)]


def run(ctx: Context) -> ModuleResult:
    # read() rebuilds the window from the spec's snapshot, so the two must agree.
    frozen = any(m.manifest.id == MANIFEST.id for m in ctx.spec.modules)
    if frozen and dict(ctx.params) != run_params(ctx.spec):
        raise ValueError("src.erp params differ from the run's module snapshot")
    counts = load_window(
        ctx.repo.engine, ctx.spec, ctx.params, sources_dir=get_settings().sources_dir
    )
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="succeeded",
        counts=counts,
        errors=(),
        abstentions=(),
    )
