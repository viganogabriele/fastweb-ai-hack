"""INS-01: `ins.product` counts sales, POS returns and reported reasons over one perimeter/period.

Pure tests on synthetic rows, plus one run on the DATA-01b fixtures (MIL01, NYC01) with the real
ERP sales and POS returns of their window, checked against the CSVs counted independently.
"""

import csv
from collections import Counter
from datetime import UTC, date, datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import (
    ArtifactRef,
    ProductInsight,
    RunSpec,
    Share,
)
from tesseract.core.db import connect
from tesseract.core.fixtures import read_fixtures
from tesseract.core.registry import Registry
from tesseract.core.repo import ErpRecord, Repo, create_run
from tesseract.modules.intelligence import insights
from tesseract.modules.sources import erp

FIXTURES = REPO_ROOT / "data" / "fixtures"
SOURCES = REPO_ROOT / "generated" / "sources"
AS_OF = datetime(2026, 10, 9, 8, 35, 52, tzinfo=UTC)  # fixture run: 10:35 Milan, 04:35 NYC
ZONES = {"MIL01": "Europe/Rome", "NYC01": "America/New_York"}


def spec(as_of=AS_OF, stores=("MIL01", "NYC01")) -> RunSpec:
    return RunSpec(
        run_id="fixture", scenario_id="historical", as_of=as_of, stores=stores,
        source_manifest_hash="s", config_hash="c", code_version="0", mode="fixture", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


def row(table, n, **data) -> ErpRecord:
    return ErpRecord(
        table=table, id=f"{table}-{n}", version="v1",
        available_at=datetime(2026, 10, 1, tzinfo=UTC), availability_basis="test",
        source_refs=(), data=data,
    )  # fmt: skip


def sale(n, sku, day, sold, returned, store="MIL01"):
    return row("sales", n, store_id=store, sku=sku, business_date=day,
               units_sold=sold, units_returned=returned)  # fmt: skip


def ret(n, sku, day, reason, store="MIL01"):
    return row("returns", n, store_id=store, sku=sku, business_date=day, return_reason=reason)


def by_id(records):
    return {r.id: r for r in records}


@pytest.fixture(scope="module")
def fixture_records():
    _, records = read_fixtures(FIXTURES)
    return records


def kind(records, name, as_of=AS_OF):
    return [r for r in records if type(r).__name__ == name and r.available_at <= as_of]


LATE = datetime(2026, 10, 10, 12, tzinfo=UTC)  # after every fixture


# Pure parts.


def test_manifest_is_discovered_after_erp_and_dedup():
    (manifest,) = [m for m in Registry.discover().manifests() if m.id == "ins.product"]
    assert manifest.requires == ("src.erp", "int.dedup")
    assert manifest.produces == ("ProductInsight",)


def test_period_ends_on_the_last_day_every_store_has_published():
    # New York is at 04:35: its Oct 8 sales come at 06:00, so Oct 7 is the last common day.
    period = insights.period(AS_OF, ZONES, 7, 28)
    assert period == insights.Period(date(2026, 10, 1), date(2026, 10, 7))
    later = datetime(2026, 10, 9, 10, 1, tzinfo=UTC)  # 06:01 New York
    assert insights.period(later, ZONES, 1, 28) == insights.Period(
        date(2026, 10, 8), date(2026, 10, 8)
    )


def test_period_never_starts_before_any_stores_erp_window():
    # Milan is already on Oct 9: its 28-day window starts on Sep 11, a day after New York's.
    period = insights.period(AS_OF, ZONES, 28, 28)
    assert period == insights.Period(date(2026, 9, 11), date(2026, 10, 7))


def test_counted_drops_copies_corrections_and_negations(fixture_records):
    observations = kind(fixture_records, "Observation")
    relations = kind(fixture_records, "EvidenceRelation")
    ids = {o.id for o in insights.counted(observations, relations)}
    assert "obs-20261002-2113-mil01-dup-maire-requests" not in ids  # certain copy
    assert "obs-20261002-2112-mil01-maire-requests" in ids  # its original
    assert "obs-20260918-2115-mil01-net-sales" not in ids  # superseded
    negated = observations[0].model_copy(update={"negated": True})
    assert insights.counted([negated], []) == []
    retract = relations[0].model_copy(update={"relation": "retracts"})
    assert insights.counted(observations, [retract]) == [
        o for o in observations if o.id not in (retract.from_ref.id, retract.to_ref.id)
    ]


def test_product_of_maps_sizes_to_their_colour_and_skips_unresolved(fixture_records):
    links = {link.observation_id: link for link in kind(fixture_records, "EntityLink", LATE)}
    assert insights.product_of(links["obs-20261001-1124-mil01-fwd-tib-zip"]) == (
        "sku",
        "J10911A00305-742",
    )
    assert insights.product_of(links["obs-20261009-1035-mil01-stockout"]) == (
        "style",
        "I10919B00011",
    )
    assert insights.product_of(links["obs-20260906-1837-nyc01-sweatshirt-return"]) is None
    assert insights.product_of(links["obs-20260918-2115-mil01-net-sales"]) is None


def build(sales=(), returns=(), observations=(), links=None, as_of=AS_OF, **kw):
    inputs = insights.Inputs(
        sales=sales, returns=returns, observations=observations, links=links or {}, zones=ZONES
    )
    kw.setdefault("days", 7)
    kw.setdefault("min_return_lines", 2)
    return {i.product_id: i for i in insights.build(inputs, spec(as_of), **kw)}


def test_returns_and_sales_share_stores_and_days():
    out = build(
        sales=[
            sale(1, "S1-999", date(2026, 10, 7), 8, 1),
            sale(2, "S1-999", date(2026, 10, 1), 2, 1, store="NYC01"),
            sale(3, "S1-999", date(2026, 10, 8), 50, 0),  # after the period (NYC not published)
            sale(4, "S1-999", date(2026, 9, 30), 50, 0),  # before it
            sale(5, "S1-999", date(2026, 10, 7), 50, 0, store="PAR01"),  # outside the perimeter
        ],
        returns=[
            ret(1, "S1-999", date(2026, 10, 7), "DEF"),
            ret(2, "S1-999", date(2026, 10, 1), "SIZE", store="NYC01"),
            ret(3, "S1-999", date(2026, 10, 8), "DEF"),
        ],
    )
    s1 = out["S1-999"]
    assert (s1.period_first, s1.period_last) == (date(2026, 10, 1), date(2026, 10, 7))
    assert (s1.units_sold, s1.units_returned, s1.return_rate) == (10, 2, 0.2)
    assert s1.return_lines == 2
    assert s1.return_reasons == (Share(key="DEF", count=1, of=2), Share(key="SIZE", count=1, of=2))
    assert s1.n_observations == 0 and s1.reported_reasons == ()
    assert s1.stores == ("MIL01", "NYC01")
    assert set(s1.input_refs) == {
        ArtifactRef(kind="ERP:sales", id="sales-1", version="v1"),
        ArtifactRef(kind="ERP:sales", id="sales-2", version="v1"),
        ArtifactRef(kind="ERP:returns", id="returns-1", version="v1"),
        ArtifactRef(kind="ERP:returns", id="returns-2", version="v1"),
    }
    assert s1.notes == ("returns of the period may refer to sales made before it",)


def test_returns_without_sales_have_no_rate_and_few_returns_no_insight():
    out = build(
        sales=[sale(1, "S2-999", date(2026, 10, 2), 0, 3)],
        returns=[ret(n, "S2-999", date(2026, 10, 2), "DEF") for n in (1, 2)]
        + [ret(3, "S3-999", date(2026, 10, 2), "DEF")],
    )
    assert set(out) == {"S2-999"}  # S3 has one return line, under min_return_lines
    s2 = out["S2-999"]
    assert s2.return_rate is None and s2.units_returned == 3 and s2.return_lines == 2
    assert any("POS return lines (2) and ERP units returned (3) differ" in n for n in s2.notes)
    assert any("not defined" in n for n in s2.notes)


def test_style_link_sums_its_colours_and_reasons_are_shares_of_observations(fixture_records):
    observations = kind(fixture_records, "Observation", LATE)
    links = {link.observation_id: link for link in kind(fixture_records, "EntityLink", LATE)}
    cardigan = [o for o in observations if o.id.startswith("obs-20261009-1035")]
    # Reported on Oct 9: inside a period that ends on Oct 9.
    out = build(
        sales=[
            sale(1, "I10919B00011-999", date(2026, 10, 8), 3, 0),
            sale(2, "I10919B00011-742", date(2026, 10, 9), 1, 0),
            sale(3, "I10919B000119-999", date(2026, 10, 9), 9, 0),  # another style code
        ],
        observations=cardigan,
        links=links,
        as_of=LATE,
    )
    style = out["I10919B00011"]
    assert style.level == "style" and style.units_sold == 4
    assert (style.n_observations, style.n_documents) == (2, 1)
    assert style.reported_kinds == (
        Share(key="stockout", count=1, of=2),
        Share(key="unmet_demand", count=1, of=2),
    )
    assert style.reported_reasons == (Share(key="unspecified", count=2, of=2),)
    assert set(style.input_refs) == {
        *(ArtifactRef(kind="Observation", id=o.id, version=o.version) for o in cardigan),
        ArtifactRef(kind="ERP:sales", id="sales-1", version="v1"),
        ArtifactRef(kind="ERP:sales", id="sales-2", version="v1"),
    }
    # The same notes reported before the period starts are not counted against its sales.
    assert "I10919B00011" not in build(observations=cardigan, links=links, as_of=AS_OF)


def test_contract_rejects_inconsistent_denominators():
    good = dict(
        id="i", version="v1", available_at=AS_OF, availability_basis="test", source_refs=(),
        run_id="r", scenario_id="s", computed_at=AS_OF, input_refs=(), producer="ins.product",
        producer_version="1", as_of=AS_OF, level="sku", product_id="S1-999", stores=("MIL01",),
        period_first=date(2026, 10, 1), period_last=date(2026, 10, 7), units_sold=10,
        units_returned=2, return_rate=0.2, return_lines=2,
        return_reasons=(Share(key="DEF", count=2, of=2),), n_observations=0, n_documents=0,
        reported_kinds=(), reported_reasons=(), observation_refs=(),
    )  # fmt: skip
    ProductInsight(**good)
    for change in (
        {"return_rate": 0.5},  # not returned / sold
        {"units_sold": 0},  # rate without a sale
        {"return_reasons": (Share(key="DEF", count=1, of=2),)},  # doesn't add up
        {"return_reasons": (Share(key="DEF", count=2, of=3),)},  # other denominator
        {"n_observations": 1},  # no ref behind it
        {"stores": ()},
    ):
        with pytest.raises(ValidationError):
            ProductInsight(**{**good, **change})
    with pytest.raises(ValidationError):
        Share(key="DEF", count=3, of=2)


# Fixture run on the real ERP window.


def pos_returns(first, last, stores):
    counts = Counter()
    for path in sorted((SOURCES / "erp" / "sales" / "pos_lines").glob("pos_lines_*.csv")):
        with path.open(encoding="utf-8") as stream:
            for r in csv.DictReader(stream):
                day = date.fromisoformat(r["business_date"])
                if r["line_type"] == "RETURN" and r["store_id"] in stores and first <= day <= last:
                    counts[r["sku"], r["return_reason"]] += 1
    return counts


def daily_sales(first, last, stores, sku):
    sold = returned = 0
    for month in ("09", "10"):
        path = SOURCES / "erp" / "sales" / "daily_store_sku" / f"sales_daily_2026_{month}.csv"
        with path.open(encoding="utf-8") as stream:
            for r in csv.DictReader(stream):
                day = date.fromisoformat(r["business_date"])
                if r["store_id"] in stores and r["sku"] == sku and first <= day <= last:
                    sold += int(r["units_sold"])
                    returned += int(r["units_returned"])
    return sold, returned


@pytest.fixture(scope="module")
def fixture_run(tmp_path_factory, fixture_records):
    engine = connect(f"sqlite:///{tmp_path_factory.mktemp('ins') / 'r.db'}")
    run_spec = spec()
    erp.load_window(engine, run_spec, {}, sources_dir=SOURCES)
    create_run(engine, run_spec)
    repo = Repo(engine, run_spec)
    repo.put(*(
        r for r in fixture_records
        if type(r).__name__ in ("Observation", "EntityLink", "EvidenceRelation")
        and r.available_at is not None and r.available_at <= AS_OF
    ))  # fmt: skip
    ctx = SimpleNamespace(spec=run_spec, repo=repo, params={})
    result = insights.run(ctx)
    again = insights.run(ctx)
    return result, again, by_id(i for i in repo.list(ProductInsight))


def test_fixture_run_matches_the_source_csvs(fixture_run):
    result, again, built = fixture_run
    assert result.status == "succeeded" and result.counts["products_new"] == len(built)
    assert again.counts["products_new"] == 0
    first, last = date(2026, 9, 11), date(2026, 10, 7)
    stores = {"MIL01", "NYC01"}
    returns = pos_returns(first, last, stores)
    for insight in built.values():
        assert (insight.period_first, insight.period_last) == (first, last)
        if insight.level == "sku":
            expected = {r: n for (s, r), n in returns.items() if s == insight.product_id}
            got = {s.key: s.count for s in insight.return_reasons}
            assert got == expected
            sold, returned = daily_sales(first, last, stores, insight.product_id)
            assert (insight.units_sold, insight.units_returned) == (sold, returned)
    # Every SKU with at least 5 return lines in the perimeter has its insight.
    lines = Counter()
    for (sku, _), n in returns.items():
        lines[sku] += n
    busy = {f"insight-sku-{s.lower()}-20261009T0835" for s, n in lines.items() if n >= 5}
    assert busy <= set(built)


def test_fixture_run_sets_reported_reasons_beside_returns(fixture_run):
    _, _, built = fixture_run
    tib = built["insight-sku-j10911a00305-742-20261009T0835"]
    assert tib.n_observations == 1
    assert tib.reported_reasons == (Share(key="quality_defect", count=1, of=1),)
    assert tib.reported_kinds == (Share(key="product_feedback", count=1, of=1),)
    maire = built["insight-sku-j20931a00012-999-20261009T0835"]
    # The duplicate mail is counted once.
    assert maire.n_observations == 1 and maire.n_documents == 1
    assert all(i.available_at <= AS_OF for i in built.values())
    assert not any(
        i.product_id.startswith("I10919B00011") and i.n_observations for i in built.values()
    )


def test_ins01_fixture_is_what_the_module_returns(fixture_run, fixture_records):
    _, _, built = fixture_run
    stored = by_id(r for r in fixture_records if isinstance(r, ProductInsight))
    assert stored == built  # rebuild with data/fixtures/build_ins01.py
