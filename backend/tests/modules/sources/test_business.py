"""Business projections respect store/day availability, provenance and source identities."""

import csv
import json
from datetime import UTC, datetime

import pytest

from tesseract.modules.sources.business import project, social_series

AS_OF = datetime(2026, 10, 22, 12, tzinfo=UTC)


def write_csv(root, name, rows):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def kpi(store, day, sales="100", visitors="10"):
    return dict(
        business_date=day,
        store_id=store,
        currency="EUR",
        net_sales_lc=sales,
        net_sales_eur_bud=sales,
        budget_lc="80",
        receipts="2",
        visitors_in=visitors,
        units="3",
        returns_units="1",
    )


@pytest.fixture
def sources(tmp_path):
    write_csv(
        tmp_path,
        "erp/master_data/stores.csv",
        [
            dict(store_id="MIL01", timezone="Europe/Rome", region="EMEA"),
            dict(store_id="NYC01", timezone="America/New_York", region="AMERICAS"),
            dict(store_id="ROM01", timezone="Europe/Rome", region="EMEA"),
        ],
    )
    write_csv(tmp_path, "erp/master_data/sku_colour.csv", [dict(sku="A-999", category="Outerwear")])
    write_csv(
        tmp_path,
        "erp/kpi/store_daily_kpi.csv",
        [
            kpi("MIL01", "2026-10-21", visitors=""),
            kpi("MIL01", "2026-10-21", visitors=""),
            kpi("MIL01", "2026-10-20"),
            kpi("NYC01", "2026-10-20"),
            kpi("NYC01", "2026-10-21"),
            kpi("ROM01", "2026-10-21", "9999"),
            kpi("MIL01", "2026-10-22", "9999"),
            kpi("MIL01", "2025-10-21", "40"),
            kpi("MIL01", "2025-10-22", "900"),
        ],
    )
    write_csv(
        tmp_path,
        "erp/sales/daily_store_sku/sales_daily_2026_10.csv",
        [
            dict(
                store_id="MIL01",
                business_date="2026-10-21",
                sku="A-999",
                currency="EUR",
                net_sales_lc="100",
                units_sold="3",
            ),
            dict(
                store_id="ROM01",
                business_date="2026-10-21",
                sku="A-999",
                currency="EUR",
                net_sales_lc="9999",
                units_sold="3",
            ),
            dict(
                store_id="MIL01",
                business_date="2026-10-22",
                sku="A-999",
                currency="EUR",
                net_sales_lc="9999",
                units_sold="3",
            ),
        ],
    )
    return tmp_path


def test_run_scope_duplicates_partial_month_and_missing_visitors(sources):
    days, market, refs = project(sources, ("MIL01", "NYC01"), AS_OF)
    assert len(days) == 4
    assert {d.store_id for d in days} == {"MIL01", "NYC01"}
    assert all(d.available_at <= AS_OF for d in days)
    assert next(d for d in days if d.store_id == "MIL01" and d.date.day == 21).visitors is None
    october = market.monthly[-1]
    assert october.partial_until == 21
    assert october.regions["EMEA"].sales == 200
    assert october.regions["EMEA"].ly == 40
    assert october.regions["AMERICAS"].sales == 200
    assert market.categories[0].sales == 100
    assert market.categories[0].units == 3
    assert len(refs) == 4
    assert all(
        r.uri.startswith("dataset://") and r.content_hash.startswith("sha256:") for r in refs
    )


def test_next_morning_uses_each_store_timezone_and_common_day(sources):
    cutoff = datetime(2026, 10, 22, 4, tzinfo=UTC)
    days, market, _ = project(sources, ("MIL01", "NYC01"), cutoff)
    assert market.last_day.isoformat() == "2026-10-20"
    assert all(d.date.day == 20 for d in days)


def test_conflicting_store_day_is_explicit_error(sources):
    path = sources / "erp/kpi/store_daily_kpi.csv"
    with path.open() as stream:
        rows = list(csv.DictReader(stream))
    rows.append(kpi("MIL01", "2026-10-21", "101"))
    write_csv(sources, "erp/kpi/store_daily_kpi.csv", rows)
    with pytest.raises(ValueError, match="conflicting source rows"):
        project(sources, ("MIL01", "NYC01"), AS_OF)


def test_social_latest_known_collection_schema_change_and_future_crawl(sources):
    folder = sources / "external/social/pulsewire"
    folder.mkdir(parents=True)

    def post(id, collected, sentiment, tags):
        return dict(
            doc_id=id,
            published_at="2026-10-20T10:00:00Z",
            collected_at=collected,
            sentiment=sentiment,
            hashtags=tags,
        )

    records = [
        post("one", "2026-10-20T11:00:00Z", "positive", ["Valentino", "valentino"]),
        post("one", "2026-10-21T11:00:00Z", {"label": "neg"}, ["Valentino"]),
        post("one", "2026-10-23T11:00:00Z", "positive", ["future"]),
        post("future", "2026-10-23T11:00:00Z", "positive", ["future"]),
    ]
    (folder / "export.jsonl").write_text(
        "\n".join(json.dumps(r) for r in records) + '\n{"doc_id": broken}\n'
    )
    series = social_series(sources, AS_OF, AS_OF.date(), {})
    assert series.posts == 1
    assert series.duplicates_removed == 1
    assert series.malformed_records == 1
    assert series.weeks[0].neg == 1
    assert series.weeks[0].pos == 0
    assert [(t.tag, t.now) for t in series.hashtags] == [("valentino", 1)]
