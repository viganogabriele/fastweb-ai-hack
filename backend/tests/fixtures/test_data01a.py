"""DATA-01a: document and observation fixtures validate against their contracts and their
dev source emails (rebuild with `data/fixtures/build_data01a.py`)."""

import json
from functools import cache
from pathlib import Path

import pytest
import yaml

from tessera.core.contracts import Observation, Segment, SourceDocument
from tessera.modules.ingestion.email_parser import parse_eml

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "data" / "fixtures"
EMAILS = ROOT / "generated" / "sources" / "store_emails"
KINDS = {cls.__name__: cls for cls in (SourceDocument, Segment, Observation)}


def load(folder: str) -> list:
    records = []
    for path in sorted((FIXTURES / folder).glob("*.json")):
        for rec in json.loads(path.read_text(encoding="utf-8")):
            records.append(KINDS[rec["kind"]].model_validate(rec["payload"]))
    return records


@cache
def documents() -> dict[str, SourceDocument]:
    return {d.id: d for d in load("documents") if isinstance(d, SourceDocument)}


@cache
def segments() -> dict[str, Segment]:
    return {s.id: s for s in load("documents") if isinstance(s, Segment)}


@cache
def observations() -> tuple[Observation, ...]:
    return tuple(load("observations"))


def test_ids_are_unique() -> None:
    for folder in ("documents", "observations"):
        ids = [(type(r).__name__, r.id) for r in load(folder)]
        assert len(ids) == len(set(ids)), folder


def test_documents_match_their_source_email() -> None:
    assert documents()
    for doc in documents().values():
        rel = doc.uri.removeprefix("dataset://store_emails/")
        parsed = parse_eml((EMAILS / rel).read_bytes())
        assert doc.content_hash == f"sha256:{parsed.content_hash}"
        assert doc.text == parsed.text and doc.text_version == parsed.parser_version
        assert doc.available_at == parsed.sent_at
        assert doc.parent_document_id is None or doc.parent_document_id in documents()


def test_segments_tile_their_document() -> None:
    for seg in segments().values():
        seg.validate_against(documents()[seg.document_id])
    for doc in documents().values():
        own = sorted(
            (s for s in segments().values() if s.document_id == doc.id), key=lambda s: s.idx
        )
        assert [s.idx for s in own] == list(range(len(own)))


def test_observation_evidence_is_exact() -> None:
    assert observations()
    for obs in observations():
        doc = documents()[obs.document_id]
        assert obs.available_at == doc.available_at
        for ev in obs.evidence:
            ev.validate_against(doc, segments()[ev.segment_id])
        for ref in obs.input_refs:
            target = documents() if ref.kind == "SourceDocument" else segments()
            assert target[ref.id].version == ref.version


def test_only_dev_stores() -> None:
    split = yaml.safe_load((ROOT / "config" / "eval_split.yaml").read_text(encoding="utf-8"))
    for doc in documents().values():
        assert doc.meta["store_id"] in split["dev"]
    for obs in observations():
        assert obs.store_id in split["dev"]


@pytest.mark.parametrize(
    "case", ["d1_positive", "ambiguous_mention", "forward", "duplicate", "correction"]
)
def test_required_cases_are_covered(case: str) -> None:
    docs = [d for d in documents().values() if d.meta["fixture_case"] == case]
    assert docs and all(any(o.document_id == d.id for o in observations()) for d in docs)


def test_duplicate_and_correction_shapes() -> None:
    by_case: dict[str, list[SourceDocument]] = {}
    for doc in documents().values():
        by_case.setdefault(str(doc.meta["fixture_case"]), []).append(doc)
    first, copy = sorted(by_case["duplicate"], key=lambda d: d.available_at)
    assert first.text == copy.text and first.content_hash != copy.content_hash
    original, correction = sorted(by_case["correction"], key=lambda d: d.available_at)
    assert correction.parent_document_id == original.id
    values = {o.document_id: o.quantity.value for o in observations() if o.kind == "sales_figure"}
    assert values[original.id] != values[correction.id]
    (fwd,) = by_case["forward"]
    (obs,) = [o for o in observations() if o.document_id == fwd.id]
    assert all(segments()[e.segment_id].is_quoted for e in obs.evidence)
