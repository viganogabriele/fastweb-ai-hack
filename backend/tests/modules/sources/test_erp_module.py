"""ING-01 module: `src.erp` writes `erp_rows`; reads at `as_of` never see future rows.

Synthetic sources tree in tmp_path, plus one smoke run on a dev store (MIL01).
"""

import csv
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from sqlalchemy import select

from tessera.core.contracts import ModuleManifest, RunSpec
from tessera.core.db import connect, erp_rows
from tessera.core.repo import Repo
from tessera.modules.sources import erp

T0 = datetime(2026, 10, 6, 18, tzinfo=UTC)
T1 = datetime(2026, 10, 8, 18, tzinfo=UTC)  # 20:00 in Milan
T2 = datetime(2026, 10, 14, 18, tzinfo=UTC)
TABLES = ("stores", "styles", "sku_colour", "sku_size_ean", "assortment", "prices")
TABLES += ("sales", "stock", "forecast")
SALE = ("business_date", "store_id", "sku", "units_sold", "units_returned")
SALE += ("gross_sales_lc", "discount_lc", "returns_lc", "net_sales_lc", "currency")


def write(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def sale(day, store="MIL01"):
    return (day, store, "J1-999", "1", "0", "100.00", "0.00", "0.00", "100.00", "EUR")


@pytest.fixture
def sources(tmp_path):
    erp_dir = tmp_path / "sources" / "erp"
    master = erp_dir / "master_data"
    write(
        master / "stores.csv",
        ("store_id", "timezone", "currency"),
        [("MIL01", "Europe/Rome", "EUR"), ("TYO01", "Asia/Tokyo", "JPY")],
    )
    write(master / "styles.csv", ("style_code", "style_name"), [("J1", "MAIRE")])
    write(master / "sku_colour.csv", ("sku", "style_code", "color_code"), [("J1-999", "J1", "999")])
    write(
        master / "sku_size_ean.csv",
        ("sku", "size", "sku_size", "ean"),
        [("J1-999", "00", "J1-999-00", "0800000000001")],
    )
    write(master / "store_assortment.csv", ("store_id", "sku"), [("MIL01", "J1-999")])
    write(
        master / "price_list_FW26.csv",
        ("store_id", "sku", "currency", "retail_price", "valid_from"),
        [("MIL01", "J1-999", "EUR", "1500.00", "2026-08-01")],
    )
    sales = erp_dir / "sales" / "daily_store_sku"
    write(sales / "sales_daily_2026_09.csv", SALE, [sale("2026-09-30")])
    october = [sale(f"2026-10-{day:02d}") for day in range(1, 22)] + [sale("2026-10-07", "TYO01")]
    write(sales / "sales_daily_2026_10.csv", SALE, october)
    stock = erp_dir / "inventory" / "store_stock_daily"
    for day in range(1, 22):
        write(
            stock / f"stock_eod_2026-10-{day:02d}.csv",
            ("snapshot_date", "store_id", "sku", "size", "on_hand", "in_transit"),
            [(f"2026-10-{day:02d}", "MIL01", "J1-999", "00", str(day), "0")],
        )
    # Far beyond any as_of used here: opening it would fail on the missing columns.
    write(stock / "stock_eod_2026-11-30.csv", ("broken",), [("x",)])
    forecast = erp_dir / "forecast" / "sku_store_weekly"
    for run_date, week, start in (
        ("2026-09-28", "2026-W41", "2026-10-05"),
        ("2026-10-05", "2026-W42", "2026-10-12"),
        ("2026-10-12", "2026-W43", "2026-10-19"),
    ):
        write(
            forecast / f"fcst_sku_store_run_{run_date}.csv",
            ("run_date", "target_week", "week_start", "store_id", "sku", "fcst_units"),
            [(run_date, week, start, "MIL01", "J1-999", "2.5")],
        )
    return tmp_path / "sources"


@pytest.fixture
def engine(tmp_path):
    return connect(f"sqlite:///{tmp_path / 'erp.db'}")


def spec(as_of, stores=("MIL01",)):
    return RunSpec(
        run_id=f"run-{as_of:%m%d}",
        scenario_id="historical",
        as_of=as_of,
        stores=stores,
        source_manifest_hash="sha256:test",
        config_hash="sha256:test",
        code_version="test",
        mode="live",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )


def load(engine, sources, as_of, **params):
    return erp.load_window(engine, spec(as_of), params, sources_dir=sources)


def stored(engine):
    with engine.connect() as conn:
        return conn.execute(select(erp_rows)).all()


def snapshot(engine, as_of):
    repo = Repo(engine, spec(as_of))
    return {table: sorted((r.id, r.version) for r in repo.erp(table)) for table in TABLES}


def test_manifest_matches_module_contract():
    assert isinstance(erp.MANIFEST, ModuleManifest)
    assert erp.MANIFEST.id == "src.erp"
    assert erp.MANIFEST.layer == "sources"
    assert erp.MANIFEST.requires == ()
    assert callable(erp.run)


def test_writes_only_rows_available_at_as_of(engine, sources):
    counts = load(engine, sources, T1)

    rows = stored(engine)
    assert rows and all(r.available_at is not None and r.available_at <= T1 for r in rows)
    assert {r.store_id for r in rows} <= {"MIL01", None}
    assert sum(counts[f"{t}_new"] for t in TABLES) == len(rows)
    sales = {r.data["business_date"]["$date"] for r in rows if r.tbl == "sales"}
    # 2026-10-08 becomes known at 06:00 Milan on 10-09; the window is 28 days.
    assert max(sales) == "2026-10-07" and "2026-09-30" in sales
    assert {r.availability_basis for r in rows if r.tbl == "stock"} == {
        "assumed:snapshot_date_next_day_06_local"
    }
    assert {r.availability_basis for r in rows if r.tbl == "styles"} == {"declared_master_snapshot"}


def test_repo_read_at_as_of_never_returns_future_rows(engine, sources):
    load(engine, sources, T1)
    before = snapshot(engine, T0)
    load(engine, sources, T2)  # a later run adds rows the earlier as_of must not see

    assert snapshot(engine, T0) == before
    repo = Repo(engine, spec(T0))
    for table in TABLES:
        assert all(r.available_at <= T0 for r in repo.erp(table))
    assert max(r.data["business_date"] for r in repo.erp("sales")).isoformat() == "2026-10-05"
    assert max(r.data["run_date"] for r in repo.erp("forecast")).isoformat() == "2026-10-05"
    assert max(r.data["run_date"] for r in Repo(engine, spec(T2)).erp("forecast")).isoformat() == (
        "2026-10-12"
    )


def test_window_keeps_the_valid_forecast_vintage(engine, sources):
    counts = load(engine, sources, T1, history_days=2)

    repo = Repo(engine, spec(T1))
    sales = sorted(r.data["business_date"].isoformat() for r in repo.erp("sales"))
    assert sales == ["2026-10-06", "2026-10-07"]
    assert [r.data["run_date"].isoformat() for r in repo.erp("forecast")] == ["2026-10-05"]
    assert counts["sales_rows"] == 2 and counts["forecast_rows"] == 1


def test_master_snapshot_after_as_of_writes_no_master_rows(engine, sources):
    counts = load(engine, sources, T1, master_available_at=(T1 + timedelta(hours=1)).isoformat())

    assert all(counts[f"{t}_rows"] == 0 for t in TABLES[:6])
    assert counts["sales_rows"] > 0  # timezones still date the facts
    assert {r.tbl for r in stored(engine)} == {"sales", "stock", "forecast"}


def test_reload_is_idempotent(engine, sources):
    load(engine, sources, T1)
    counts = load(engine, sources, T1)

    assert all(counts[f"{t}_new"] == 0 for t in TABLES)
    assert counts["sales_rows"] > 0


def test_unknown_store_fails(engine, sources):
    with pytest.raises(ValueError, match="ZZZ01"):
        erp.load_window(engine, spec(T1, ("MIL01", "ZZZ01")), {}, sources_dir=sources)


def test_run_on_dev_store(engine):
    run_spec = spec(T1)
    repo = Repo(engine, run_spec)
    ctx = SimpleNamespace(spec=run_spec, repo=repo, params={"history_days": 3})

    result = erp.run(ctx)

    assert (result.module_id, result.module_version, result.status) == (
        "src.erp",
        erp.MANIFEST.version,
        "succeeded",
    )
    assert result.counts["sales_rows"] > 0 and result.counts["forecast_rows"] > 0
    sales = repo.erp("sales", store_id="MIL01")
    assert max(r.data["business_date"] for r in sales).isoformat() == "2026-10-07"
    assert all(r.available_at <= T1 for t in TABLES for r in repo.erp(t))
