"""FC-01 module: `fc.baseline` writes D+1..D+7 baselines from the vintage valid at `as_of`.

Synthetic sources tree in tmp_path, plus one smoke run on a dev store (MIL01).
"""

import csv
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace

import pytest

from tessera.core.contracts import ForecastAdjustment, ModuleManifest, ModuleSnapshot, RunSpec
from tessera.core.db import connect
from tessera.core.repo import Repo, create_run
from tessera.modules.intelligence import baseline
from tessera.modules.sources import erp

T1 = datetime(2026, 10, 14, 18, tzinfo=UTC)  # Wed 20:00 in Milan: horizon Thu 15 → Wed 21
T2 = datetime(2026, 10, 21, 18, tzinfo=UTC)  # run 2026-10-19 missing: horizon reaches week 10-26
FORECAST = ("run_date", "target_week", "week_start", "store_id", "sku", "fcst_units")


def write(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def fcst(run_date, week_start, store, sku, units):
    week = date.fromisoformat(week_start).strftime("%G-W%V")
    return (run_date, week, week_start, store, sku, units)


@pytest.fixture
def sources(tmp_path, monkeypatch):
    erp_dir = tmp_path / "sources" / "erp"
    master = erp_dir / "master_data"
    write(
        master / "stores.csv",
        ("store_id", "timezone", "currency", "closed_dow"),
        [("MIL01", "Europe/Rome", "EUR", ""), ("PAR01", "Europe/Paris", "EUR", "Sun")],
    )
    write(master / "styles.csv", ("style_code", "style_name"), [("J1", "MAIRE")])
    write(master / "sku_colour.csv", ("sku", "style_code", "color_code"), [("J1-999", "J1", "999")])
    write(
        master / "sku_size_ean.csv",
        ("sku", "size", "sku_size", "ean"),
        [("J1-999", "00", "J1-999-00", "0800000000001")],
    )
    write(
        master / "store_assortment.csv",
        ("store_id", "sku"),
        [("MIL01", "J1-999"), ("MIL01", "J1-742"), ("PAR01", "J1-999")],
    )
    write(
        master / "price_list_FW26.csv",
        ("store_id", "sku", "currency", "retail_price", "valid_from"),
        [("MIL01", "J1-999", "EUR", "1500.00", "2026-08-01")],
    )
    (erp_dir / "sales" / "daily_store_sku").mkdir(parents=True)
    (erp_dir / "inventory" / "store_stock_daily").mkdir(parents=True)
    forecast = erp_dir / "forecast" / "sku_store_weekly"
    write(
        forecast / "fcst_sku_store_run_2026-10-05.csv",
        FORECAST,
        [
            fcst("2026-10-05", ws, "MIL01", "J1-999", units)
            for ws, units in (("2026-10-05", "7"), ("2026-10-12", "14"), ("2026-10-19", "21"))
        ]
        + [fcst("2026-10-05", "2026-10-26", "MIL01", "J1-999", "70")],
    )
    write(
        forecast / "fcst_sku_store_run_2026-10-12.csv",
        FORECAST,
        [
            fcst("2026-10-12", "2026-10-12", "MIL01", "J1-999", "28"),
            fcst("2026-10-12", "2026-10-19", "MIL01", "J1-999", "35"),
            fcst("2026-10-12", "2026-10-19", "MIL01", "J1-999", "35"),  # exact duplicate
            fcst("2026-10-12", "2026-10-12", "MIL01", "J2-999", "7"),
            fcst("2026-10-12", "2026-10-19", "MIL01", "J2-999", "7"),
            fcst("2026-10-12", "2026-10-19", "MIL01", "J2-999", "9"),  # conflicting
            fcst("2026-10-12", "2026-10-12", "PAR01", "J1-999", "12"),
            fcst("2026-10-12", "2026-10-19", "PAR01", "J1-999", "12"),
        ],
    )
    root = tmp_path / "sources"
    monkeypatch.setattr(erp, "get_settings", lambda: SimpleNamespace(sources_dir=root))
    return root


@pytest.fixture
def engine(tmp_path):
    return connect(f"sqlite:///{tmp_path / 'fc.db'}")


def run_repo(engine, sources, as_of, stores=("MIL01", "PAR01")):
    spec = RunSpec(
        run_id=f"run-{as_of:%m%d}",
        scenario_id="historical",
        as_of=as_of,
        stores=stores,
        source_manifest_hash="sha256:test",
        config_hash="sha256:test",
        code_version="test",
        mode="live",
        modules=(
            ModuleSnapshot(manifest=erp.MANIFEST, params={}),
            ModuleSnapshot(manifest=baseline.MANIFEST, params={}),
        ),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    create_run(engine, spec)
    erp.load_window(engine, spec, {}, sources_dir=sources)
    return Repo(engine, spec)


def values(record):
    return [(p.date.isoformat(), p.baseline) for p in record.series]


def test_manifest_matches_module_contract():
    assert isinstance(baseline.MANIFEST, ModuleManifest)
    assert baseline.MANIFEST.id == "fc.baseline"
    assert baseline.MANIFEST.layer == "intelligence"
    assert baseline.MANIFEST.requires == ("src.erp",)
    assert callable(baseline.run)


def test_latest_vintage_split_over_the_horizon(engine, sources):
    repo = run_repo(engine, sources, T1)

    result = baseline.write_baselines(repo, 7)

    assert result.status == "succeeded"
    fc = baseline.baseline(repo, "MIL01", "J1-999")
    assert fc is not None and fc.status == "unchanged"
    assert (fc.horizon_start, fc.horizon_end) == (date(2026, 10, 15), date(2026, 10, 21))
    # Run 2026-10-12 wins over 2026-10-05; the duplicate row does not double week 10-19.
    assert values(fc) == [(f"2026-10-{d}", 4.0) for d in (15, 16, 17, 18)] + [
        (f"2026-10-{d}", 5.0) for d in (19, 20, 21)
    ]
    assert all(p.latent == p.servable and p.latent.base == p.baseline for p in fc.series)
    assert fc.baseline_ref.version == "2026-10-12"
    assert fc.baseline_ref.id == "fcst_sku_store_run_2026-10-12/MIL01/J1-999"
    assert fc.case_ids == () and fc.forecast_target == "sales_baseline"
    assert fc.available_at <= T1
    assert {r.uri for r in fc.source_refs} == {
        "erp/master_data/stores.csv",
        "erp/forecast/sku_store_weekly/fcst_sku_store_run_2026-10-12.csv",
    }


def test_closed_weekday_is_zero_and_open_days_share_the_week(engine, sources):
    repo = run_repo(engine, sources, T1)
    baseline.write_baselines(repo, 7)

    fc = baseline.baseline(repo, "PAR01", "J1-999")

    assert fc.status == "unchanged"
    assert dict(values(fc)) == {
        "2026-10-15": 2.0,
        "2026-10-16": 2.0,
        "2026-10-17": 2.0,
        "2026-10-18": 0.0,  # Sunday
        "2026-10-19": 2.0,
        "2026-10-20": 2.0,
        "2026-10-21": 2.0,
    }


def test_missing_week_is_not_estimable_never_filled_from_an_older_run(engine, sources):
    repo = run_repo(engine, sources, T2, stores=("MIL01",))

    baseline.write_baselines(repo, 7)

    fc = baseline.baseline(repo, "MIL01", "J1-999")
    assert fc.status == "not_estimable"
    assert "missing_forecast:2026-10-26" in fc.reason
    late = [p for p in fc.series if p.date >= date(2026, 10, 26)]
    assert late and all(p.baseline is None and p.latent is None for p in late)
    assert all(p.latent is None for p in fc.series)


def test_conflicting_rows_and_absent_skus_are_not_estimable(engine, sources):
    repo = run_repo(engine, sources, T1)

    result = baseline.write_baselines(repo, 7)

    conflict = baseline.baseline(repo, "MIL01", "J2-999")
    assert conflict.status == "not_estimable"
    assert "conflicting_forecast:2026-10-19" in conflict.reason
    absent = baseline.baseline(repo, "MIL01", "J1-742")
    assert absent.status == "not_estimable" and absent.baseline_ref is None
    assert absent.reason.startswith("sku_not_in_vintage")
    assert result.counts == {"baselines": 4, "unchanged": 2, "not_estimable": 2, "new": 4}


def test_no_vintage_at_as_of_blocks(engine, sources):
    repo = run_repo(engine, sources, datetime(2026, 10, 4, 18, tzinfo=UTC), stores=("MIL01",))

    result = baseline.write_baselines(repo, 7)

    assert result.status == "blocked"
    assert result.abstentions == ("MIL01: no forecast vintage available at as_of",)
    fc = baseline.baseline(repo, "MIL01", "J1-999")
    assert fc.status == "not_estimable" and fc.reason.startswith("no_forecast_vintage")


def test_rerun_is_idempotent(engine, sources):
    repo = run_repo(engine, sources, T1)
    baseline.write_baselines(repo, 7)

    assert baseline.write_baselines(repo, 7).counts["new"] == 0


def test_horizon_param_and_closed_dow_parsing(engine, sources):
    repo = run_repo(engine, sources, T1, stores=("MIL01",))
    ctx = SimpleNamespace(spec=repo.spec, repo=repo, params={"horizon_days": 3})

    baseline.run(ctx)

    fc = baseline.baseline(repo, "MIL01", "J1-999")
    assert fc.horizon_end == fc.horizon_start + timedelta(days=2)
    assert baseline.closed_weekdays("Sat|Sun") == {5, 6}
    assert baseline.closed_weekdays("") == frozenset()
    with pytest.raises(ValueError):
        baseline.closed_weekdays("Funday")


def test_run_on_dev_store(engine):
    as_of = datetime(2026, 10, 8, 18, tzinfo=UTC)
    spec = RunSpec(
        run_id="dev",
        scenario_id="historical",
        as_of=as_of,
        stores=("MIL01",),
        source_manifest_hash="sha256:test",
        config_hash="sha256:test",
        code_version="test",
        mode="live",
        modules=(ModuleSnapshot(manifest=erp.MANIFEST, params={"history_days": 3}),),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    create_run(engine, spec)
    repo = Repo(engine, spec)
    erp.run(SimpleNamespace(spec=spec, repo=repo, params={"history_days": 3}))

    result = baseline.run(SimpleNamespace(spec=spec, repo=repo, params={}))

    assert result.status in ("succeeded", "degraded")
    assert result.counts["unchanged"] > 0
    records = repo.list(ForecastAdjustment, store_id="MIL01")
    assert all(r.horizon_start == date(2026, 10, 9) for r in records)
    assert all(len(r.series) == 7 for r in records)
