"""ing.extract: a fake LLM proposes candidates; code must verify quotes, numbers and periods."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from tessera.core.cache import ReplayMiss
from tessera.core.contracts import (
    ModuleManifest,
    ModuleResult,
    ModuleSnapshot,
    Observation,
    RunSpec,
    Segment,
    SourceDocument,
)
from tessera.core.db import connect
from tessera.core.llm import BudgetExceeded, ExtractionFailed
from tessera.core.orchestrator import run
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.run_repo import repo_session
from tessera.modules.ingestion import extract
from tessera.modules.ingestion.extract import Candidate, Candidates

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "data" / "fixtures"
D1 = "doc-20261009-1035-mil01"

SOURCE = ModuleManifest(
    id="src.email",
    version="1",
    layer="sources",
    description="fixture documents",
    requires=(),
    optional_inputs=(),
    produces=("SourceDocument", "Segment"),
    enabled=True,
    mode="live",
    params_schema={},
)


def fixture_records(name):
    items = json.loads((FIXTURES / "documents" / f"{name}.json").read_text())
    kinds = {"SourceDocument": SourceDocument, "Segment": Segment}
    return [kinds[i["kind"]].model_validate(i["payload"]) for i in items]


def synthetic(text, doc="doc-synthetic", sent="2026-10-02T19:00:00Z"):
    document = SourceDocument(
        id=doc,
        version="v1",
        available_at=sent,
        availability_basis="email_date_header",
        source_refs=({"uri": f"dataset://{doc}", "content_hash": "sha256:x"},),
        source_type="email",
        connector="src.email",
        uri=f"dataset://{doc}",
        content_hash="sha256:x",
        origin=None,
        language="it",
        text=text,
        text_version="email-v1",
        meta={"store_id": "MIL01", "subject": "chiusura"},
    )
    segment = Segment(
        id=f"{doc}-seg0",
        version="v1",
        available_at=sent,
        availability_basis="email_date_header",
        source_refs=document.source_refs,
        document_id=doc,
        text_version="email-v1",
        idx=0,
        text=text,
        char_start=0,
        char_end=len(text),
        is_quoted=False,
    )
    return [document, segment]


class FakeLLM:
    def __init__(self, replies):
        self.replies = replies  # document id -> Candidates | exception
        self.calls = []

    def extract(self, schema, messages, *, cache_context, **generation):
        assert schema is Candidates and generation == {"temperature": 0}
        document_id = cache_context["document"][0]
        self.calls.append(document_id)
        reply = self.replies[document_id]
        if isinstance(reply, Exception):
            raise reply
        return Candidates(observations=reply)


def execute(tmp_path, records, replies, as_of="2026-10-22T20:00:00Z"):
    request = RunSpec(
        run_id="extract-run",
        scenario_id="historical",
        as_of=as_of,
        stores=("MIL01",),
        source_manifest_hash="sources",
        config_hash="config",
        code_version="test",
        mode="live",
        modules=(
            ModuleSnapshot(manifest=SOURCE, params={}),
            ModuleSnapshot(manifest=extract.MANIFEST, params={}),
        ),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )

    def source(ctx):
        for record in records:
            ctx.repo.put(record)
        return ModuleResult(
            module_id="src.email",
            module_version="1",
            status="succeeded",
            counts={},
            errors=(),
            abstentions=(),
        )

    llm = FakeLLM(replies)
    engine = connect(f"sqlite:///{tmp_path / 'extract.db'}")
    registry = Registry(
        (RegisteredModule(SOURCE, source), RegisteredModule(extract.MANIFEST, extract.run))
    )
    statuses = run(request, engine=engine, registry=registry, clients={"llm": llm})
    with repo_session(engine, request) as repo:
        observations = repo.list(Observation)
        published = repo.run_state()["published"]
    engine.dispose()
    return statuses[-1], observations, published, llm


def test_registry_discovers_ing_extract():
    assert extract.MANIFEST in Registry.discover().manifests()


def test_d1_quote_matches_hand_labelled_evidence(tmp_path):
    labelled = json.loads((FIXTURES / "observations" / f"{D1}.json").read_text())[0]["payload"]
    candidate = Candidate(
        quote="da ieri siamo a zero cardigan logo in M, sia nero che blu",
        segment_idx=0,
        kind="stockout",
        product_mention="cardigan logo in M, sia nero che blu",
        quantity_kind="exact",
        value=0,
        unit="units",
        quantity_raw="a zero",
        direction="down",
        time_text="da ieri",
        period_start="2026-10-08",
        attribution="store_staff",
    )
    status, observations, published, _ = execute(tmp_path, fixture_records(D1), {D1: [candidate]})
    assert status.status == "succeeded" and published
    assert status.result.counts == {"documents": 1, "observations": 1}
    (observation,) = observations
    assert observation.evidence[0].model_dump(mode="json") == labelled["evidence"][0]
    assert observation.quantity == Observation.model_validate(labelled).quantity
    for field in ("period_start", "period_end", "kind", "store_id", "available_at", "direction"):
        assert getattr(observation, field) == getattr(
            Observation.model_validate(labelled), field
        ), field
    refs = {(r.kind, r.id) for r in observation.input_refs}
    assert refs == {("SourceDocument", D1), ("Segment", f"{D1}-seg0")}


def test_whitespace_variant_quote_maps_to_canonical_slice(tmp_path):
    text = "Oggi tanti clienti\nhanno chiesto la Maire nera.\nNessun problema."
    candidate = Candidate(quote="hanno   chiesto la\nMaire  nera", kind="unmet_demand")
    _, observations, _, _ = execute(tmp_path, synthetic(text), {"doc-synthetic": [candidate]})
    evidence = observations[0].evidence[0]
    assert evidence.quote == "hanno chiesto la Maire nera"
    assert text[evidence.char_start : evidence.char_end] == evidence.quote


def test_unverifiable_quotes_are_abstentions(tmp_path):
    text = "Maire nera finita.\n\nMaire nera richiesta da due clienti."
    replies = {
        "doc-synthetic": [
            Candidate(quote="Maire blu finita", kind="stockout"),
            Candidate(quote="Maire nera", kind="unmet_demand"),
            Candidate(quote="Maire nera finita.", kind="stockout"),
        ]
    }
    status, observations, published, _ = execute(tmp_path, synthetic(text), replies)
    assert [o.kind for o in observations] == ["stockout"]
    assert status.result.counts["candidates_rejected"] == 2
    assert status.result.abstentions == (
        "doc-synthetic: stockout rejected (quote not found in the document)",
        "doc-synthetic: unmet_demand rejected (quote occurs more than once)",
    )
    assert published


def test_numbers_are_kept_only_when_the_email_states_them(tmp_path):
    text = "Un paio di clienti chiedevano il Tib.\nVenduto 58,0k.\nTib finito."
    replies = {
        "doc-synthetic": [
            # A vague quantifier never becomes a number, whatever the model says.
            Candidate(
                quote="Un paio di clienti chiedevano il Tib",
                kind="unmet_demand",
                quantity_kind="exact",
                value=2,
                unit="customers",
                quantity_raw="Un paio",
            ),
            # Money with its words but no currency: the number is dropped.
            Candidate(
                quote="Venduto 58,0k",
                kind="sales_figure",
                quantity_kind="exact",
                value=58000,
                unit="money",
                quantity_raw="58,0k",
            ),
            # A number whose words are not in the email.
            Candidate(
                quote="Tib finito",
                kind="stockout",
                quantity_kind="exact",
                value=12,
                unit="units",
                quantity_raw="12 pezzi",
            ),
        ]
    }
    status, observations, _, _ = execute(tmp_path, synthetic(text), replies)
    quantities = [o.quantity for o in observations]
    assert [(q.kind, q.value, q.raw) for q in quantities] == [
        ("vague", None, "Un paio"),
        ("unknown", None, "58,0k"),
        ("unknown", None, None),
    ]
    assert status.result.counts["numbers_dropped"] == 3


def test_period_after_send_date_is_dropped_except_for_future_kinds(tmp_path):
    text = "Cardigan finito.\nSabato sfilata in Galleria."
    replies = {
        "doc-synthetic": [
            Candidate(quote="Cardigan finito", kind="stockout", period_start="2026-10-05"),
            Candidate(
                quote="Sabato sfilata in Galleria",
                kind="local_event",
                period_start="2026-10-03",
                period_end="2026-10-03",
            ),
        ]
    }
    _, observations, _, _ = execute(tmp_path, synthetic(text), replies)
    stockout, event = observations
    assert stockout.period_start is None and stockout.period_end is None
    assert event.period_start == datetime(2026, 10, 2, 22, 0, tzinfo=UTC)
    assert event.period_end == datetime(2026, 10, 3, 21, 59, 59, tzinfo=UTC)


def test_extraction_failure_abstains_and_provider_errors_degrade(tmp_path):
    records = (
        synthetic("Uno.", doc="doc-a", sent="2026-10-01T19:00:00Z")
        + synthetic("Due.", doc="doc-b", sent="2026-10-02T19:00:00Z")
        + synthetic("Tre.", doc="doc-c", sent="2026-10-03T19:00:00Z")
    )
    replies = {
        "doc-a": ExtractionFailed("invalid twice"),
        "doc-b": ReplayMiss("no recording"),
        "doc-c": [],
    }
    status, observations, published, _ = execute(tmp_path, records, replies)
    assert observations == []
    assert status.status == "degraded" and published
    assert status.result.abstentions == ("doc-a: extraction failed validation twice",)
    assert status.result.errors == ("doc-b: ReplayMiss",)
    assert status.result.counts == {"documents_abstained": 1, "documents": 1, "observations": 0}


def test_budget_exhaustion_stops_remaining_documents(tmp_path):
    records = synthetic("Uno.", doc="doc-a") + synthetic("Due.", doc="doc-b")
    status, _, _, llm = execute(tmp_path, records, {"doc-a": BudgetExceeded("over"), "doc-b": []})
    assert llm.calls == ["doc-a"]
    assert status.result.errors == ("doc-a: LLM budget exhausted, remaining documents not read",)


@pytest.mark.parametrize("raw", ["몇명", "好几件", "a couple"])
def test_vague_words_without_spaces_are_recognised(raw):
    vague = extract.vague_quantifiers(ROOT / "config")
    assert any(extract._mentions(raw.casefold(), word) for word in vague)
