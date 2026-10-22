"""ING-01: inline ERP facts only; never open answer keys or holdout sources."""

import csv
import hashlib
from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from tessera.core.contracts.common import SourceRef
from tessera.modules.sources.erp import (
    latest_forecast,
    load_csv,
    parse_rows,
    rows_at_as_of,
)

ZONES = {"MIL01": "Europe/Rome", "TYO01": "Asia/Tokyo", "NYC01": "America/New_York"}
SOURCE = SourceRef(uri="synthetic:///erp.csv", content_hash="synthetic-file-hash")
T1 = datetime(2026, 10, 8, 18, tzinfo=UTC)


def parse(table, rows, **kwargs):
    return parse_rows(table, rows, source=SOURCE, store_timezones=ZONES, **kwargs)


def sale(**changes):
    return {
        "business_date": "2026-10-08",
        "store_id": "MIL01",
        "sku": "STYLE-001",
        "units_sold": "2",
        "units_returned": "3",
        "gross_sales_lc": "200.00",
        "discount_lc": "10.00",
        "returns_lc": "300.00",
        "net_sales_lc": "-110.00",
        "currency": "EUR",
        **changes,
    }


def stock(**changes):
    return {
        "snapshot_date": "2026-10-08",
        "store_id": "MIL01",
        "sku": "STYLE-001",
        "size": "00",
        "on_hand": "0",
        "in_transit": "4",
        **changes,
    }


def forecast(**changes):
    return {
        "run_date": "2026-10-05",
        "target_week": "2026-W42",
        "week_start": "2026-10-12",
        "store_id": "MIL01",
        "sku": "STYLE-001",
        "fcst_units": "13.66",
        **changes,
    }


def test_daily_sales_next_day_boundary_and_money():
    (row,) = parse("sales", [sale()])
    assert row.available_at == datetime(2026, 10, 9, 4, tzinfo=UTC)
    assert "assumed:business_date_next_day_06_local" == row.availability_basis
    assert rows_at_as_of([row], T1) == ()
    assert rows_at_as_of([row], datetime(2026, 10, 9, 3, 59, tzinfo=UTC)) == ()
    assert rows_at_as_of([row], row.available_at) == (row,)
    assert row.data["net_sales_lc"] == Decimal("-110.00")
    assert row.data["units_returned"] == 3
    assert row.data["currency"] == "EUR"
    assert row.data["business_date"] == date(2026, 10, 8)


@pytest.mark.parametrize(
    ("store", "expected"),
    [
        ("MIL01", "2026-10-09T04:00:00+00:00"),
        ("TYO01", "2026-10-08T21:00:00+00:00"),
        ("NYC01", "2026-10-09T10:00:00+00:00"),
    ],
)
def test_store_local_timezone_not_utc_day(store, expected):
    (row,) = parse("stock", [stock(store_id=store)])
    assert row.available_at == datetime.fromisoformat(expected)
    assert row.data["size"] == "00"
    assert row.data["on_hand"] == 0
    assert row.data["in_transit"] == 4


def test_six_oclock_convention_tracks_dst():
    rows = parse("stock", [stock(snapshot_date="2026-10-24"), stock(snapshot_date="2026-10-25")])
    assert [row.available_at.hour for row in rows] == [5, 5]  # Rome switches on Oct 25.


@pytest.mark.parametrize(
    "posting",
    [
        {"posted_at": "2026-10-10T13:00:00+02:00"},
        {"available_at": "2026-10-10T11:00:00Z"},
        {"posting_date": "2026-10-10"},
    ],
)
def test_late_posting_overrides_daily_assumption(posting):
    (row,) = parse("sales", [sale(**posting)])
    assert row.available_at.date() == date(2026, 10, 10)
    assert "later_source" in row.availability_basis
    assert rows_at_as_of([row], datetime(2026, 10, 9, 23, tzinfo=UTC)) == ()


def test_early_posting_does_not_expose_same_day_sales():
    (row,) = parse("sales", [sale(posted_at="2026-10-08T12:00:00Z")])
    assert row.available_at == datetime(2026, 10, 9, 4, tzinfo=UTC)


def test_forecast_issue_convention_explicit_issue_and_later_posting():
    (assumed,) = parse("forecast", [forecast()])
    assert assumed.available_at == datetime(2026, 10, 5, 4, tzinfo=UTC)
    assert assumed.availability_basis == "assumed:run_date_06_local"
    (actual,) = parse("forecast", [forecast(issued_at="2026-10-05T03:00:00+02:00")])
    assert actual.available_at == datetime(2026, 10, 5, 1, tzinfo=UTC)
    assert actual.availability_basis == "source:issued_at"
    (late,) = parse("forecast", [forecast(posted_at="2026-10-06T10:00:00Z")])
    assert late.available_at == datetime(2026, 10, 6, 10, tzinfo=UTC)


def test_forecast_vintages_and_replay_rollback():
    rows = parse(
        "forecast",
        [
            forecast(),
            forecast(run_date="2026-10-12", fcst_units="0"),
            forecast(sku="OTHER-001", week_start="2026-10-19", target_week="2026-W43"),
        ],
    )
    t2 = datetime(2026, 10, 12, 4, tzinfo=UTC)
    first = latest_forecast(rows, T1)
    assert len(first) == 2
    second = latest_forecast(reversed(rows), t2)
    selected = next(row for row in second if row.data["sku"] == "STYLE-001")
    assert selected.data["run_date"] == date(2026, 10, 12)
    assert selected.data["fcst_units"] == Decimal("0")
    assert latest_forecast(rows, T1) == first
    assert len(rows) == 3  # No overwrite of older vintage.
    assert latest_forecast(rows, datetime(2026, 10, 5, 3, 59, tzinfo=UTC)) == ()


def test_conflicting_forecast_values_are_not_silently_chosen():
    rows = parse("forecast", [forecast(), forecast(fcst_units="99")])
    with pytest.raises(ValueError, match="Conflicting forecast"):
        latest_forecast(rows, T1)


def test_missing_target_in_latest_vintage_stays_missing():
    rows = parse(
        "forecast",
        [
            forecast(),
            forecast(week_start="2026-10-19", target_week="2026-W43"),
            forecast(run_date="2026-10-12", fcst_units="0"),
        ],
    )
    selected = latest_forecast(rows, datetime(2026, 10, 12, 4, tzinfo=UTC))
    assert len(selected) == 1
    assert selected[0].data["week_start"] == date(2026, 10, 12)


@pytest.mark.parametrize(
    ("table", "raw"),
    [
        ("stores", {"store_id": "MIL01", "timezone": "Europe/Rome"}),
        ("styles", {"style_code": "STYLE", "style_name": "Example", "launch_date": "2026-10-12"}),
        ("sku_colour", {"sku": "STYLE-001", "style_code": "STYLE", "color_code": "001"}),
        (
            "sku_size_ean",
            {"sku": "STYLE-001", "size": "00", "sku_size": "STYLE-001-00", "ean": "001234567890"},
        ),
        ("assortment", {"store_id": "MIL01", "sku": "STYLE-001"}),
        (
            "prices",
            {
                "store_id": "MIL01",
                "sku": "STYLE-001",
                "currency": "EUR",
                "retail_price": "1450.00",
                "valid_from": "2026-02-01",
            },
        ),
    ],
)
def test_master_data_unknown_unless_snapshot_declared(table, raw):
    (unknown,) = parse(table, [raw])
    assert unknown.available_at is None
    assert rows_at_as_of([unknown], T1) == ()
    (known,) = parse(table, [raw], master_available_at=T1)
    assert known.available_at == T1
    assert known.availability_basis == "declared_master_snapshot"
    assert rows_at_as_of([known], T1) == (known,)
    for field in ("ean", "size", "color_code"):
        if field in raw:
            assert known.data[field] == raw[field]


def test_master_publication_time_is_not_inferred_from_launch_or_validity():
    (row,) = parse(
        "styles",
        [
            {
                "style_code": "STYLE",
                "style_name": "Example",
                "launch_date": "2026-10-12",
                "available_at": "2026-10-01T10:00:00Z",
            }
        ],
    )
    assert row.available_at == datetime(2026, 10, 1, 10, tzinfo=UTC)


def test_scope_before_parsing_retains_physical_record_locator():
    rows = parse(
        "sales",
        [sale(store_id="SKIPPED", units_sold="bad"), sale()],
        store_ids=frozenset({"MIL01"}),
    )
    assert len(rows) == 1
    assert rows[0].source_refs[0].locator == "record=3"
    assert parse("sales", [sale()], store_ids=frozenset()) == ()


def test_provenance_versions_and_immutability():
    a, b = parse("stock", [stock(), stock()])
    assert a.id != b.id
    assert a.version == b.version
    (same,) = parse("stock", [stock()])
    (changed,) = parse("stock", [stock(on_hand="2")])
    assert same == a
    assert changed.id == a.id and changed.version != a.version
    assert a.source_refs[0].content_hash == SOURCE.content_hash
    with pytest.raises(TypeError):
        a.data["on_hand"] = 5
    with pytest.raises(FrozenInstanceError):
        a.available_at = T1


@pytest.mark.parametrize(
    ("table", "raw"),
    [
        ("sales", sale(units_sold="1.5")),
        ("sales", sale(units_returned="-1")),
        ("sales", sale(net_sales_lc="NaN")),
        ("sales", sale(net_sales_lc="Infinity")),
        ("sales", sale(currency="")),
        ("sales", sale(business_date="2026-02-30")),
        ("stock", stock(on_hand="-1")),
        ("stock", stock(store_id="UNKNOWN")),
        ("forecast", forecast(fcst_units="")),
        ("forecast", forecast(fcst_units="-1")),
        ("forecast", forecast(week_start="2026-10-13")),
        ("forecast", forecast(target_week="2026-W43")),
        ("forecast", forecast(issued_at="2026-10-04T12:00:00Z")),
        ("sales", sale(posted_at="2026-10-09T12:00:00")),
    ],
)
def test_invalid_facts_fail_with_source_locator(table, raw):
    with pytest.raises(ValueError, match="synthetic:///erp.csv record 2"):
        parse(table, [raw])


def test_naive_replay_or_master_clock_rejected():
    with pytest.raises(ValueError, match="aware"):
        rows_at_as_of([], datetime(2026, 10, 8))
    with pytest.raises(ValueError, match="aware"):
        parse("assortment", [], master_available_at=datetime(2026, 10, 8))


def write_csv(tmp_path, rows):
    root = tmp_path / "sources"
    path = root / "erp/sales/sample.csv"
    path.parent.mkdir(parents=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    return root, path


def test_csv_loader_hash_and_strict_cutoff_without_source_changes(tmp_path):
    root, path = write_csv(tmp_path, [sale(business_date="2026-10-07"), sale()])
    before = path.read_bytes()
    loaded = load_csv(
        "sales/sample.csv",
        "sales",
        sources_dir=root,
        as_of=T1,
        store_timezones=ZONES,
        store_ids=frozenset({"MIL01"}),
    )
    assert len(loaded) == 1
    assert loaded[0].data["business_date"] == date(2026, 10, 7)
    assert loaded[0].source_refs[0] == SourceRef(
        uri=path.as_uri(), content_hash=hashlib.sha256(before).hexdigest(), locator="record=2"
    )
    assert path.read_bytes() == before


def test_csv_loader_rejects_traversal_and_symlink(tmp_path):
    root, path = write_csv(tmp_path, [sale()])
    outside = tmp_path / "hidden.csv"
    outside.write_text("DO NOT READ")
    link = path.parent / "link.csv"
    link.symlink_to(outside)
    for relative in ("../../hidden.csv", "sales/link.csv", str(outside)):
        with pytest.raises(ValueError, match="inside sources/erp"):
            load_csv(relative, "sales", sources_dir=root, as_of=T1, store_timezones=ZONES)


@pytest.mark.parametrize("header", ["store_id,sku\n", "store_id,store_id,timezone\n"])
def test_csv_loader_rejects_missing_or_duplicate_columns(tmp_path, header):
    root, path = write_csv(tmp_path, [sale()])
    path.write_text(header)
    with pytest.raises(ValueError, match="CSV columns"):
        load_csv("sales/sample.csv", "stores", sources_dir=root, as_of=T1, store_timezones=ZONES)
