"""DATA-01b: link, relation, case, forecast and report fixtures validate against their contracts,
reference only existing DATA-01a/b records and respect availability (rebuild with
`data/fixtures/build_data01b.py`)."""

import csv
import hashlib
import json
from datetime import UTC, date, datetime, timedelta
from functools import cache
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
import yaml

from tessera.core.contracts import (
    ArtifactRef,
    Case,
    EntityLink,
    EvidenceRelation,
    ForecastAdjustment,
    Observation,
    Report,
    Segment,
    SourceDocument,
)
from tessera.core.contracts.common import DerivedRecord, SourceRecord
from tessera.core.fixtures import FIXTURE_RUN_ID, FIXTURE_SCENARIO_ID, read_fixtures
from tessera.modules.intelligence.disaggregation import disaggregate

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "data" / "fixtures"
SOURCES = ROOT / "generated" / "sources"
MASTER = SOURCES / "erp" / "master_data"
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
            latest = max(i.available_at for i in inputs if i.available_at is not None)
            assert record.available_at == latest, record.id
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


def vintage_rows(uri: str, store: str, sku: str) -> dict[date, float]:
    rows = read_csv(SOURCES / uri.removeprefix("dataset://"))
    return {
        date.fromisoformat(r["week_start"]): float(r["fcst_units"])
        for r in rows
        if r["store_id"] == store and r["sku"] == sku
    }


def test_forecasts_are_the_available_vintage_disaggregated_and_unchanged() -> None:
    assert of(ForecastAdjustment)
    for fc in of(ForecastAdjustment):
        assert fc.status == "unchanged" and fc.reason
        for case_id in fc.case_ids:
            case = everything()[("Case", case_id)]
            assert isinstance(case, Case) and case.store_id == fc.store_id
            assert case.scope_id is not None and fc.sku.startswith(case.scope_id.split("-")[0])
        assert fc.baseline_ref is not None and fc.baseline_ref in fc.input_refs
        (src,) = [s for s in fc.source_refs if s.uri.startswith("dataset://erp/forecast/")]
        path = SOURCES / src.uri.removeprefix("dataset://")
        assert src.content_hash == "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        run = date.fromisoformat(fc.baseline_ref.version)
        assert path.name == f"fcst_sku_store_run_{run}.csv"
        # No look-ahead: the vintage is out (06:00 local the next day, RFC §4.3) before D+1,
        # and D+1 is the day after the case's availability in the store's time zone.
        tz = ZoneInfo(stores()[fc.store_id]["timezone"])
        published = datetime.combine(run + timedelta(days=1), datetime.min.time(), tz)
        assert fc.available_at is not None
        assert published + timedelta(hours=6) <= fc.available_at
        assert fc.horizon_start == fc.available_at.astimezone(tz).date() + timedelta(days=1)
        assert (fc.horizon_end - fc.horizon_start).days + 1 == domain()["policy"]["horizon"][
            "days"
        ]["value"]
        expected = disaggregate(
            vintage_rows(src.uri, fc.store_id, fc.sku), fc.horizon_start, len(fc.series)
        )
        assert [p.baseline for p in fc.series] == pytest.approx(
            [p.baseline for p in expected.points]
        )


def test_report_cites_existing_records_at_the_fixture_as_of() -> None:
    (report,) = of(Report)
    as_of = max(r.available_at for r in everything().values() if r.available_at is not None)
    assert report.as_of == as_of == report.available_at
    assert report.as_of.tzinfo is UTC or report.as_of.utcoffset() == timedelta(0)
    cited = [resolve(c.ref) for c in report.citations]
    assert all(r.available_at is not None and r.available_at <= report.as_of for r in cited)
    assert {c.ref for c in report.citations} == set(report.input_refs)
    keys = sorted(f"{r.kind}:{r.id}@{r.version}" for r in report.input_refs)
    digest = hashlib.sha256("\n".join(keys).encode()).hexdigest()
    assert report.input_version_hash == f"sha256:{digest}"
    for i in range(1, len(report.citations) + 1):
        assert f"[{i}]" in report.markdown
    for case in of(Case):
        assert case.id in {c.ref.id for c in report.citations}


def test_all_fixtures_load_as_one_run() -> None:
    _, records = read_fixtures(FIXTURES)
    assert {(type(r).__name__, r.id) for r in records} == set(everything())
