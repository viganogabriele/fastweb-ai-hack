"""DATA-01b: link, relation, case, forecast and report fixtures validate against their contracts,
reference only existing DATA-01a/b records and respect availability (rebuild with
`data/fixtures/build_data01b.py`)."""

import csv
import hashlib
import json
import re
from datetime import UTC, date, datetime, time, timedelta
from functools import cache
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
import yaml

from tesseract.core.contracts import (
    ArtifactRef,
    Case,
    Citation,
    EntityLink,
    EvidenceRelation,
    ForecastAdjustment,
    Observation,
    Report,
    ScenarioValues,
    Segment,
    SourceDocument,
)
from tesseract.core.contracts.common import DerivedRecord, SourceRecord
from tesseract.core.fixtures import FIXTURE_RUN_ID, FIXTURE_SCENARIO_ID, read_fixtures

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "data" / "fixtures"
SOURCES = ROOT / "generated" / "sources"
MASTER = SOURCES / "erp" / "master_data"
FORECASTS = SOURCES / "erp" / "forecast" / "sku_store_weekly"
FOLDERS = {
    "documents": (SourceDocument, Segment),
    "observations": (Observation,),
    "links": (EntityLink, EvidenceRelation),
    "cases": (Case,),
    "forecast": (ForecastAdjustment,),
    "reports": (Report,),
}
KINDS = {cls.__name__: cls for classes in FOLDERS.values() for cls in classes}
EXTERNAL_KINDS = {"ForecastVintage"}  # source rows, not stored artifacts


def load(folder: str) -> list[SourceRecord]:
    records = []
    for path in sorted((FIXTURES / folder).glob("*.json")):
        for rec in json.loads(path.read_text(encoding="utf-8")):
            assert rec["kind"] in {c.__name__ for c in FOLDERS[folder]}, (path, rec["kind"])
            records.append(KINDS[rec["kind"]].model_validate(rec["payload"]))
    return records


@cache
def everything() -> dict[tuple[str, str], SourceRecord]:
    return {(type(r).__name__, r.id): r for folder in FOLDERS for r in load(folder)}


def of(kind: type) -> list:
    return [r for r in everything().values() if type(r) is kind]


def resolve(ref: ArtifactRef) -> SourceRecord:
    record = everything()[(ref.kind, ref.id)]
    assert record.version == ref.version, ref
    return record


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@cache
def domain() -> dict:
    return yaml.safe_load((ROOT / "config" / "domain.yaml").read_text(encoding="utf-8"))


@cache
def stores() -> dict[str, dict[str, str]]:
    return {r["store_id"]: r for r in read_csv(MASTER / "stores.csv")}


def test_folders_hold_their_contracts_with_unique_ids() -> None:
    for folder in ("links", "cases", "forecast", "reports"):
        records = load(folder)
        assert records, folder
        ids = [(type(r).__name__, r.id) for r in records]
        assert len(ids) == len(set(ids)), folder


def test_derived_records_reference_existing_inputs_and_are_not_early() -> None:
    for folder in ("links", "cases", "forecast", "reports"):
        for record in load(folder):
            assert isinstance(record, DerivedRecord)
            assert (record.run_id, record.scenario_id) == (FIXTURE_RUN_ID, FIXTURE_SCENARIO_ID)
            inputs = [resolve(r) for r in record.input_refs if r.kind not in EXTERNAL_KINDS]
            assert inputs, record.id
            known = [i.available_at for i in inputs if i.available_at is not None]
            for r in record.input_refs:  # a vintage is known from its publication instant
                if r.kind == "ForecastVintage":
                    assert isinstance(record, ForecastAdjustment)
                    known.append(vintage_published(date.fromisoformat(r.version), record.store_id))
            assert record.available_at == max(known), record.id
            for i in inputs:  # every input's provenance is carried along
                assert set(i.source_refs) <= set(record.source_refs), (record.id, i.id)


def test_every_observation_has_one_link() -> None:
    linked = [link.observation_id for link in of(EntityLink)]
    assert sorted(linked) == sorted(o.id for o in of(Observation))
    statuses = {link.status for link in of(EntityLink)}
    assert {"linked", "ambiguous"} <= statuses
    for link in of(EntityLink):
        obs = everything()[("Observation", link.observation_id)]
        assert link.input_refs[0] == ArtifactRef(kind="Observation", id=obs.id, version="v1")
        if obs.kind == "sales_figure":
            assert link.status == "not_product"


@cache
def catalog() -> tuple[set[str], set[str], dict[str, str], set[tuple[str, str]]]:
    styles = {r["style_code"] for r in read_csv(MASTER / "styles.csv")}
    skus = {r["sku"] for r in read_csv(MASTER / "sku_colour.csv")}
    sizes = {r["sku_size"]: r["sku"] for r in read_csv(MASTER / "sku_size_ean.csv")}
    assortment = {(r["store_id"], r["sku"]) for r in read_csv(MASTER / "store_assortment.csv")}
    return styles, skus, sizes, assortment


def carried(store: str, target: str, level: str) -> bool:
    styles, skus, sizes, assortment = catalog()
    if level == "style":
        return target in styles and any(
            s == store and sku.startswith(target + "-") for s, sku in assortment
        )
    if level == "sku":
        return target in skus and (store, target) in assortment
    return level == "sku_size" and target in sizes and (store, sizes[target]) in assortment


def test_link_targets_exist_in_catalog_and_store_assortment() -> None:
    for link in of(EntityLink):
        store = everything()[("Observation", link.observation_id)].store_id
        assert store is not None
        for cand in link.candidates:
            assert carried(store, cand.target_id, cand.level), (link.id, cand.target_id)
        if link.status == "linked":
            assert link.target_id is not None and link.level is not None
            assert carried(store, link.target_id, link.level), link.id
            assert link.target_id in {c.target_id for c in link.candidates}
        if link.status == "ambiguous":
            top = max(c.score for c in link.candidates)
            assert sum(c.score == top for c in link.candidates) > 1, link.id


def test_relations_match_duplicate_and_correction_documents() -> None:
    by_relation = {r.relation: r for r in of(EvidenceRelation)}
    assert set(by_relation) == {"duplicates", "supersedes"}
    for relation in by_relation.values():
        src, dst = resolve(relation.from_ref), resolve(relation.to_ref)
        assert isinstance(src, Observation) and isinstance(dst, Observation)
        assert src.available_at > dst.available_at  # the later fact points at the earlier one
        docs = {resolve(r).id for r in relation.evidence_refs}
        assert docs == {src.document_id, dst.document_id}
    dup = by_relation["duplicates"]
    a, b = resolve(dup.from_ref), resolve(dup.to_ref)
    assert isinstance(a, Observation) and isinstance(b, Observation)
    assert a.quantity == b.quantity and a.product_mention == b.product_mention
    fix = by_relation["supersedes"]
    new = everything()[("SourceDocument", resolve(fix.from_ref).document_id)]
    old = everything()[("SourceDocument", resolve(fix.to_ref).document_id)]
    assert isinstance(new, SourceDocument) and new.parent_document_id == old.id


def test_cases_are_consistent_with_their_evidence() -> None:
    owners = domain()["owners"]
    split = yaml.safe_load((ROOT / "config" / "eval_split.yaml").read_text(encoding="utf-8"))
    copies = {r.from_ref.id for r in of(EvidenceRelation) if r.relation == "duplicates"}
    for case in of(Case):
        assert case.store_id in split["dev"]
        assert case.owner == owners[case.case_type]
        obs = [resolve(r) for r in case.supporting]
        assert all(isinstance(o, Observation) and o.store_id == case.store_id for o in obs)
        docs = [everything()[("SourceDocument", o.document_id)] for o in obs]
        received = sorted(d.available_at for d in docs if d.available_at is not None)
        assert case.n_documents == len({d.id for d in docs})
        assert case.n_origin_groups == case.n_documents - len(
            {o.document_id for o in obs if o.id in copies}
        )
        assert (case.first_available_at, case.last_received_at) == (received[0], received[-1])
        assert case.last_independent_evidence_at == max(
            o.available_at for o in obs if o.id not in copies
        )
        assert case.window_start <= case.last_received_at
        for ref in case.context_refs:
            resolve(ref)
        links = [link for link in of(EntityLink) if link.observation_id in {o.id for o in obs}]
        if any(link.status != "linked" for link in links):  # RFC §4.5: never dropped
            assert (case.scope_level, case.status) == ("unknown", "verify")
        else:
            assert {link.target_id for link in links} == {case.scope_id}
            assert {link.level for link in links} == {case.scope_level}


def run_as_of() -> datetime:
    """The fixture run's as_of, as `tesseract fixtures load` sets it: the latest `available_at`."""
    return max(r.available_at for r in everything().values() if r.available_at is not None)


def vintage_published(run: date, store: str) -> datetime:
    """A vintage with only `run_date` is out at 06:00 local the next day (RFC §4.3 convention)."""
    tz = ZoneInfo(stores()[store]["timezone"])
    return datetime.combine(run + timedelta(days=1), time(6), tz).astimezone(UTC)


def local_day_bounds(first: date, last: date, store: str) -> tuple[datetime, datetime]:
    tz = ZoneInfo(stores()[store]["timezone"])
    start = datetime.combine(first, time(0), tz)
    end = datetime.combine(last + timedelta(days=1), time(0), tz) - timedelta(seconds=1)
    return start.astimezone(UTC), end.astimezone(UTC)


def expected_baseline(
    store: str, sku: str, as_of: datetime
) -> tuple[date, list[tuple[date, float]]]:
    """Run date of the latest vintage out by `as_of` and its D+1..D+7 daily baseline, D = `as_of`
    in the store's time zone (RFC §4.9). Plain arithmetic on the source CSV, not FC-01: every day
    of these stores is open, so each day is its ISO week's forecast / 7."""
    runs = [
        date.fromisoformat(p.stem.removeprefix("fcst_sku_store_run_"))
        for p in FORECASTS.glob("fcst_sku_store_run_*.csv")
    ]
    run = max(r for r in runs if vintage_published(r, store) <= as_of)
    assert not stores()[store]["closed_dow"], store
    weekly: dict[date, set[float]] = {}
    for r in read_csv(FORECASTS / f"fcst_sku_store_run_{run}.csv"):
        if r["store_id"] == store and r["sku"] == sku:
            weekly.setdefault(date.fromisoformat(r["week_start"]), set()).add(
                float(r["fcst_units"])
            )
    d = as_of.astimezone(ZoneInfo(stores()[store]["timezone"])).date()
    series = []
    for k in range(1, domain()["policy"]["horizon"]["days"]["value"] + 1):
        day = d + timedelta(days=k)
        (units,) = weekly[day - timedelta(days=day.weekday())]  # one value per week
        series.append((day, units / 7))
    return run, series


def check_forecast(fc: ForecastAdjustment, as_of: datetime) -> None:
    """`fc` is the run's D+1..D+7 baseline from the vintage admissible at `as_of`, unchanged."""
    assert fc.status == "unchanged" and fc.reason and not fc.components
    cases = [everything()[("Case", case_id)] for case_id in fc.case_ids]
    assert cases
    for case in cases:
        assert isinstance(case, Case) and case.store_id == fc.store_id
        assert case.scope_id is not None and fc.sku.startswith(case.scope_id.split("-")[0])
    run, series = expected_baseline(fc.store_id, fc.sku, as_of)
    assert fc.baseline_ref == ArtifactRef(
        kind="ForecastVintage",
        id=f"fcst_sku_store_run_{run}/{fc.store_id}/{fc.sku}",
        version=str(run),
    )
    assert fc.baseline_ref in fc.input_refs
    (src,) = [s for s in fc.source_refs if s.uri.startswith("dataset://erp/forecast/")]
    path = FORECASTS / f"fcst_sku_store_run_{run}.csv"
    assert src.uri == "dataset://" + path.relative_to(SOURCES).as_posix()
    assert src.content_hash == "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    assert (fc.horizon_start, fc.horizon_end) == (series[0][0], series[-1][0])
    assert [p.date for p in fc.series] == [day for day, _ in series]
    for p, (_, units) in zip(fc.series, series, strict=True):
        assert p.baseline == pytest.approx(units)
        for scenario in (p.latent, p.servable):  # no uplift: every scenario is the baseline
            assert scenario is not None
            assert (scenario.low, scenario.base, scenario.high) == pytest.approx((units,) * 3)
    # No look-ahead: known once both the case and the vintage are, and within the run.
    published = vintage_published(run, fc.store_id)
    assert fc.available_at == max(published, *(c.available_at for c in cases))
    assert fc.available_at <= as_of


def test_forecasts_are_the_run_horizon_from_the_admissible_vintage() -> None:
    assert of(ForecastAdjustment)
    for fc in of(ForecastAdjustment):
        check_forecast(fc, run_as_of())


def test_maire_baseline_is_hand_checked() -> None:
    """Anchor computed by hand from fcst_sku_store_run_2026-10-05.csv: run at 2026-10-09 08:35 UTC,
    D+1..D+7 = 10-10..10-16 = 2 days of W41 (13.66) + 5 days of W42 (14.42), /7 each."""
    (fc,) = [f for f in of(ForecastAdjustment) if f.sku == "J20931A00012-999"]
    assert fc.baseline_ref is not None and fc.baseline_ref.version == "2026-10-05"
    assert (fc.horizon_start, fc.horizon_end) == (date(2026, 10, 10), date(2026, 10, 16))
    total = sum(p.baseline or 0.0 for p in fc.series)
    assert total == pytest.approx((2 * 13.66 + 5 * 14.42) / 7) and round(total, 1) == 14.2


def stale_forecast(fc: ForecastAdjustment, as_of: datetime) -> ForecastAdjustment:
    """`fc` rebuilt as if the run were at `as_of`: other vintage, horizon and values."""
    run, series = expected_baseline(fc.store_id, fc.sku, as_of)
    path = FORECASTS / f"fcst_sku_store_run_{run}.csv"
    (src,) = [s for s in fc.source_refs if s.uri.startswith("dataset://erp/forecast/")]
    stale_src = src.model_copy(
        update={
            "uri": "dataset://" + path.relative_to(SOURCES).as_posix(),
            "content_hash": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )
    baseline = ArtifactRef(
        kind="ForecastVintage",
        id=f"fcst_sku_store_run_{run}/{fc.store_id}/{fc.sku}",
        version=str(run),
    )
    points = []
    for (day, units), p in zip(series, fc.series, strict=True):
        flat = ScenarioValues(low=units, base=units, high=units)
        points.append(
            p.model_copy(update={"date": day, "baseline": units, "latent": flat, "servable": flat})
        )
    return fc.model_copy(
        update={
            "baseline_ref": baseline,
            "input_refs": tuple(
                baseline if r.kind == "ForecastVintage" else r for r in fc.input_refs
            ),
            "source_refs": tuple(stale_src if s == src else s for s in fc.source_refs),
            "horizon_start": series[0][0],
            "horizon_end": series[-1][0],
            "series": tuple(points),
            "available_at": max(vintage_published(run, fc.store_id), as_of),
        }
    )


def test_forecast_check_rejects_a_case_dated_vintage_and_horizon() -> None:
    """The review's mutation: Aurea's baseline taken at the case date (2026-10-02), i.e. the
    2026-09-28 vintage for 10-03..10-09, is self-consistent but not the run's horizon."""
    (fc,) = [f for f in of(ForecastAdjustment) if f.sku == "J20931A00012-999"]
    case = everything()[("Case", fc.case_ids[0])]
    assert case.available_at is not None
    stale = stale_forecast(fc, case.available_at)
    assert stale.baseline_ref is not None and stale.baseline_ref.version == "2026-09-28"
    assert stale.horizon_start == date(2026, 10, 3)
    with pytest.raises(AssertionError, match="2026-09-28"):
        check_forecast(stale, run_as_of())
    # Right vintage reference and horizon, but the stale values: fails on the values.
    points = [
        p.model_copy(update={"date": q.date}) for p, q in zip(stale.series, fc.series, strict=True)
    ]
    with pytest.raises(AssertionError, match="comparison failed"):
        check_forecast(fc.model_copy(update={"series": tuple(points)}), run_as_of())


MARKER = re.compile(r"\[(\d+)\]")
NUMBER = re.compile(r"\d+(?:\.\d+)?")


def cited_segments(markdown: str) -> dict[int, str]:
    """Citation number → the text it closes: from the line start or the previous marker."""
    segments: dict[int, str] = {}
    for line in markdown.splitlines():
        line = re.sub(r"^\s*- ", "", line)
        prev = 0
        for m in MARKER.finditer(line):
            n = int(m.group(1))
            assert n not in segments, f"[{n}] cited twice"
            segments[n] = line[prev : m.start()]
            prev = m.end()
    return segments


def check_citation(c: Citation, text: str, as_of: datetime) -> None:
    """The rendered text says what the cited field holds, with the cited unit, scope and period
    (RFC §4.8.1). Expected values come from the cited record or the sources, not the report."""
    record = resolve(c.ref)
    numbers = [float(n) for n in NUMBER.findall(text)]
    if isinstance(record, Observation):
        q = record.quantity
        assert c.scope == {"store_id": record.store_id}
        assert (c.period_start, c.period_end) == (record.period_start, record.period_end)
        if c.field == "quantity.value":
            assert q.kind == "exact" and q.value is not None and c.unit == q.unit
            assert numbers == [q.value], text  # the value, and no other uncited number
            assert text.rstrip().endswith(f" {q.unit}"), text
        else:
            assert c.field == "quantity.kind" and c.unit is None
            assert numbers == [] and f"quantity {q.kind}" in text, text
    elif isinstance(record, ForecastAdjustment):
        run, series = expected_baseline(record.store_id, record.sku, as_of)
        first, last = series[0][0], series[-1][0]
        assert (c.field, c.unit) == ("series.baseline", "units")
        assert c.scope == {"store_id": record.store_id, "sku": record.sku}
        assert (c.period_start, c.period_end) == local_day_bounds(first, last, record.store_id)
        m = re.fullmatch(
            rf"baseline {re.escape(record.sku)} (\d\d)-(\d\d)\.\.(\d\d)-(\d\d) "
            rf"(\d+\.\d) units, {record.status} ",
            text,
        )
        assert m, text
        assert tuple(map(int, m.groups()[:4])) == (first.month, first.day, last.month, last.day)
        assert float(m.group(5)) == pytest.approx(sum(u for _, u in series), abs=0.05)
    elif isinstance(record, Case):
        if c.field is None:
            assert f"{record.status}, priority {record.priority} " in text, text
        else:
            assert c.field in ("n_documents", "n_origin_groups") and c.unit is None
            assert c.scope == {"store_id": record.store_id}
            assert numbers == [getattr(record, c.field)], text
    elif isinstance(record, EntityLink):
        assert c.field == "candidates" and record.status == "ambiguous"
        assert text.strip() == "product is " + " or ".join(x.target_id for x in record.candidates)
    else:
        raise AssertionError(f"unexpected citation {c}")


def check_report(report: Report) -> None:
    as_of = run_as_of()
    assert report.as_of == as_of == report.available_at
    assert report.as_of.utcoffset() == timedelta(0)
    cited = [resolve(c.ref) for c in report.citations]
    assert all(r.available_at is not None and r.available_at <= report.as_of for r in cited)
    assert {c.ref for c in report.citations} == set(report.input_refs)
    keys = sorted(f"{r.kind}:{r.id}@{r.version}" for r in report.input_refs)
    digest = hashlib.sha256("\n".join(keys).encode()).hexdigest()
    assert report.input_version_hash == f"sha256:{digest}"
    segments = cited_segments(report.markdown)
    assert sorted(segments) == list(range(1, len(report.citations) + 1))
    for n, c in enumerate(report.citations, start=1):
        check_citation(c, segments[n], as_of)
    # Every quantity is cited: a bullet holds numbers only inside cited segments, and the open
    # questions are the cases' own text, with no number.
    uncertainties = {u for case in of(Case) for u in case.blocking_uncertainties}
    for line in report.markdown.splitlines():
        if line.startswith("  - open: "):
            assert line.removeprefix("  - open: ") in uncertainties
            assert not NUMBER.search(line), line
        elif line.startswith("  - "):
            assert MARKER.search(line) and not NUMBER.search(MARKER.split(line)[-1]), line
    # Coverage: every case, every forecast and every counted (non-copy) observation is cited.
    copies = {r.from_ref.id for r in of(EvidenceRelation) if r.relation == "duplicates"}
    ids = {c.ref.id for c in report.citations}
    assert {c.id for c in of(Case)} <= ids
    assert {f.id for f in of(ForecastAdjustment)} <= ids
    counted = {r.id for case in of(Case) for r in case.supporting if r.id not in copies}
    assert {i for i in ids if i.startswith("obs-")} == counted


def test_report_renders_cited_values_at_the_fixture_as_of() -> None:
    (report,) = of(Report)
    check_report(report)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("unmet demand 7 requests [", "unmet demand 700 requests ["),  # the review's mutation
        ("10-10..10-16 14.2 units", "10-10..10-16 12.6 units"),  # stale vintage total
        ("J20931A00012-999 10-10..10-16", "J20931A00012-999 10-03..10-09"),  # stale horizon
        ("stockout 0 units [", "stockout 0 units, 3 asked ["),  # extra, uncited number
        ("2 documents [", "3 documents ["),
        ("priority high [", "priority low ["),
    ],
)
def test_report_check_rejects_wrong_rendered_values(old: str, new: str) -> None:
    (report,) = of(Report)
    assert report.markdown.count(old) == 1
    mutated = report.model_copy(update={"markdown": report.markdown.replace(old, new)})
    with pytest.raises(AssertionError):
        check_report(mutated)


@pytest.mark.parametrize(
    "update",
    [
        {"unit": "units"},  # requests are not units
        {"scope": {"store_id": "NYC01"}},  # the right number of the wrong store
        {"field": "quantity.kind"},
        {"period_end": None},
    ],
)
def test_report_check_rejects_wrong_citation_semantics(update: dict) -> None:
    (report,) = of(Report)
    citations = list(report.citations)
    (i,) = [i for i, c in enumerate(citations) if c.ref.id.endswith("mil01-maire-requests")]
    citations[i] = citations[i].model_copy(update=update)
    with pytest.raises(AssertionError):
        check_report(report.model_copy(update={"citations": tuple(citations)}))


def test_all_fixtures_load_as_one_run() -> None:
    # The loader reads every family under `data/fixtures/`; this file owns DATA-01a/b only, so
    # the encoder families must match exactly once DATA-01c's records are set aside.
    _, records = read_fixtures(FIXTURES)
    loaded = {(type(r).__name__, r.id) for r in records}
    ours = set(everything())
    assert ours <= loaded
    later = {"StockFact", "ActionOption", "AgentTrace", "ProductInsight"}  # DATA-01c, INS-01
    assert {key for key in loaded if key[0] not in later} == ours
