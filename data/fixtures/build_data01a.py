"""Build the DATA-01a fixtures: documents, segments and hand-labelled observations.

Run from the repo root (rewrites `data/fixtures/{documents,observations}/*.json`):

    backend/.venv/bin/python data/fixtures/build_data01a.py

Documents and segments come from real dev `.eml` files through the ING-02 parser, so text and
offsets are exactly what the product will see. Observations are written by hand here: they are
what a correct extractor should return, not the output of a model. Only dev stores, only
`generated/sources/`. Dedup, linking and correction relations are DATA-01b (lane B): both copies
of a duplicate and both sides of a correction keep their own observation here.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tesseract.core.contracts import Evidence, Observation, Quantity, Segment, SourceDocument
from tesseract.modules.ingestion.email_parser import ParsedEmail, parse_eml

ROOT = Path(__file__).resolve().parents[2]
EMAILS = ROOT / "generated" / "sources" / "store_emails"
OUT = ROOT / "data" / "fixtures"

RUN_ID = "fixture"
SCENARIO_ID = "historical"
COMPUTED_AT = datetime(2026, 10, 22, 12, 0, tzinfo=UTC)
PRODUCER = "fixture.data01a"
PRODUCER_VERSION = "1"
EXTRACTOR_VERSION = "manual-data01a-v1"
DOC_VERSION = "v1"

STORES = {"MIL01": ("it", "Europe/Rome"), "NYC01": ("en", "America/New_York")}

# file → (fixture case, store)
EMAILS_USED = {
    "MIL01/20261009_1035_MIL01.eml": ("d1_positive", "MIL01"),
    "MIL01/20261002_2112_MIL01.eml": ("duplicate", "MIL01"),
    "MIL01/20261002_2113_MIL01_dup.eml": ("duplicate", "MIL01"),
    "MIL01/20260918_2115_MIL01.eml": ("correction", "MIL01"),
    "MIL01/20260918_2207_MIL01_corr.eml": ("correction", "MIL01"),
    "MIL01/20261001_1124_MIL01_fwd.eml": ("forward", "MIL01"),
    "NYC01/20260906_1837_NYC01.eml": ("ambiguous_mention", "NYC01"),
}


def local_day(day: str, tz: str) -> tuple[datetime, datetime]:
    start = datetime.fromisoformat(day).replace(tzinfo=ZoneInfo(tz))
    return start, start.replace(hour=23, minute=59, second=59)


# Hand labels. `quote` (and each of `also_quotes`, the same fact restated in the same document)
# must occur exactly once in the document text. `period` is the fact's own period in store-local
# days; None as end means ongoing at send time (never a guessed end after `available_at`).
OBSERVATIONS = {
    "MIL01/20261009_1035_MIL01.eml": [
        {
            "slug": "stockout",
            "kind": "stockout",
            "quote": "da ieri siamo a zero cardigan logo in M, sia nero che blu",
            "product_mention": "cardigan logo in M, sia nero che blu",
            "quantity": {"kind": "exact", "value": 0, "unit": "units", "raw": "a zero"},
            "direction": "down",
            "time_text": "da ieri",
            "period": ("2026-10-08", None),
            "attribution": "store_staff",
        },
        {
            "slug": "unmet-demand",
            "kind": "unmet_demand",
            "quote": "ce lo chiedono in continuazione",
            "product_mention": "cardigan logo in M",
            "quantity": {"kind": "vague", "unit": "requests", "raw": "in continuazione"},
            "direction": "up",
            "time_text": None,
            "period": ("2026-10-08", None),
            "attribution": "store_staff",
        },
    ],
    "MIL01/20261002_2112_MIL01.eml": [
        {
            "slug": "maire-requests",
            "kind": "unmet_demand",
            "quote": "Aurea nera: 7 richieste (2 2 2, 1 1, 0, 4)",
            "also_quotes": ["Aurea nera 7 richieste."],  # same fact in the Note row
            "product_mention": "Aurea nera",
            "quantity": {"kind": "exact", "value": 7, "unit": "requests", "raw": "7 richieste"},
            "direction": "up",
            "time_text": None,
            "period": ("2026-10-02", "2026-10-02"),
            "attribution": "store_staff",
        },
    ],
    "MIL01/20261002_2113_MIL01_dup.eml": [
        {
            "slug": "maire-requests",
            "kind": "unmet_demand",
            "quote": "Aurea nera: 7 richieste (2 2 2, 1 1, 0, 4)",
            "also_quotes": ["Aurea nera 7 richieste."],  # same fact in the Note row
            "product_mention": "Aurea nera",
            "quantity": {"kind": "exact", "value": 7, "unit": "requests", "raw": "7 richieste"},
            "direction": "up",
            "time_text": None,
            "period": ("2026-10-02", "2026-10-02"),
            "attribution": "store_staff",
        },
    ],
    "MIL01/20260918_2115_MIL01.eml": [
        {
            "slug": "net-sales",
            "kind": "sales_figure",
            "quote": "Fatturato: 58,0k",
            "product_mention": None,
            "quantity": {
                "kind": "exact",
                "value": 58000,
                "unit": "money",
                "currency": "EUR",
                "raw": "58,0k",
            },
            "direction": "none",
            "time_text": None,
            "period": ("2026-09-18", "2026-09-18"),
            "attribution": "store_staff",
        },
    ],
    "MIL01/20260918_2207_MIL01_corr.eml": [
        {
            "slug": "net-sales",
            "kind": "sales_figure",
            "quote": "il fatturato di oggi e' 85,0k e non 58",
            "product_mention": None,
            "quantity": {
                "kind": "exact",
                "value": 85000,
                "unit": "money",
                "currency": "EUR",
                "raw": "85,0k",
            },
            "direction": "none",
            "time_text": "oggi",
            "period": ("2026-09-18", "2026-09-18"),
            "attribution": "store_staff",
        },
    ],
    "MIL01/20261001_1124_MIL01_fwd.eml": [
        {
            "slug": "tib-zip",
            "kind": "product_feedback",
            "quote": "il cursore della zip si e' staccato da una parte",
            "product_mention": "gilet Vel blu taglia 4",
            "quantity": {"kind": "exact", "value": 1, "unit": "units", "raw": "un gilet"},
            "direction": "down",
            "reason": "quality_defect",
            "reason_text": "il cursore della zip si e' staccato",
            "time_text": "Dopo nemmeno tre settimane",
            "period": None,
            "attribution": "customer",
        },
    ],
    "NYC01/20260906_1837_NYC01.eml": [
        {
            "slug": "sweatshirt-return",
            "kind": "product_feedback",
            "quote": "a sweatshirt",
            "product_mention": "a sweatshirt",
            "quantity": {"kind": "exact", "value": 1, "unit": "units", "raw": "a sweatshirt"},
            "direction": "down",
            "time_text": "sun",
            "period": ("2026-09-06", "2026-09-06"),
            "attribution": "store_staff",
        },
    ],
}


def doc_id(rel: str) -> str:
    return "doc-" + Path(rel).stem.lower().replace("_", "-")


def thread_root(p: ParsedEmail) -> str | None:
    return (p.references[0] if p.references else p.in_reply_to) or p.message_id


def build_document(rel: str, store: str, by_message_id: dict[str, str]) -> tuple[dict, list]:
    raw = (EMAILS / rel).read_bytes()
    p = parse_eml(raw)
    language, tz = STORES[store]
    assert p.sent_at is not None, rel
    source_ref = {
        "uri": f"dataset://store_emails/{rel}",
        "content_hash": f"sha256:{p.content_hash}",
    }
    common = {
        "version": DOC_VERSION,
        "available_at": p.sent_at,
        "availability_basis": "email_date_header",
        "source_refs": [source_ref],
    }
    did = doc_id(rel)
    document = SourceDocument(
        id=did,
        **common,
        source_type="email",
        connector="src.email",
        uri=source_ref["uri"],
        content_hash=source_ref["content_hash"],
        origin=p.sender_address,
        author_ref=p.sender_name,
        language=language,
        business_date=p.sent_at.astimezone(ZoneInfo(tz)).date(),
        thread_key=thread_root(p),
        parent_document_id=by_message_id.get(p.in_reply_to or ""),
        text=p.text,
        text_version=p.parser_version,
        meta={
            "store_id": store,
            "message_id": p.message_id,
            "in_reply_to": p.in_reply_to,
            "subject": p.subject,
            "thread_subject": p.thread_subject,
            "is_reply": p.is_reply,
            "is_forward": p.is_forward,
            "body_source": p.body_source,
            "fixture_case": EMAILS_USED[rel][0],
        },
    )
    segments = [
        Segment(
            id=f"{did}-seg{s.idx}",
            **common,
            document_id=did,
            text_version=p.parser_version,
            idx=s.idx,
            text=s.text,
            char_start=s.char_start,
            char_end=s.char_end,
            is_quoted=s.is_quoted,
        )
        for s in p.segments
    ]
    for seg in segments:
        seg.validate_against(document)
    return document, segments


def build_evidence(document: SourceDocument, segments: list, quote: str) -> Evidence:
    assert document.text.count(quote) == 1, (document.id, quote)
    start = document.text.index(quote)
    end = start + len(quote)
    segment = next(s for s in segments if s.char_start <= start and end <= s.char_end)
    evidence = Evidence(
        document_id=document.id,
        document_version=document.version,
        segment_id=segment.id,
        quote=quote,
        char_start=start,
        char_end=end,
    )
    evidence.validate_against(document, segment)
    return evidence


def build_observation(document: SourceDocument, segments: list, label: dict, store: str) -> dict:
    quotes = [label["quote"], *label.get("also_quotes", ())]
    evidence = [build_evidence(document, segments, q) for q in quotes]
    segment = next(s for s in segments if s.id == evidence[0].segment_id)
    tz = STORES[store][1]
    period_start = period_end = None
    if label["period"]:
        first, last = label["period"]
        period_start = local_day(first, tz)[0]
        period_end = local_day(last, tz)[1] if last else None
    ref = {"kind": "SourceDocument", "id": document.id, "version": document.version}
    used = dict.fromkeys(e.segment_id for e in evidence)
    seg_refs = [
        {"kind": "Segment", "id": sid, "version": next(x for x in segments if x.id == sid).version}
        for sid in used
    ]
    return Observation(
        id=f"obs-{document.id.removeprefix('doc-')}-{label['slug']}",
        version="v1",
        available_at=document.available_at,
        availability_basis="document_available_at",
        source_refs=document.source_refs,
        run_id=RUN_ID,
        scenario_id=SCENARIO_ID,
        computed_at=COMPUTED_AT,
        input_refs=[ref, *seg_refs],
        producer=PRODUCER,
        producer_version=PRODUCER_VERSION,
        document_id=document.id,
        kind=label["kind"],
        store_id=store,
        period_start=period_start,
        period_end=period_end,
        time_text=label["time_text"],
        product_mention=label["product_mention"],
        quantity=Quantity(**label["quantity"]),
        direction=label["direction"],
        reason=label.get("reason"),
        reason_text=label.get("reason_text"),
        attribution=label["attribution"],
        negated=False,
        evidence=evidence,
        extractor_version=EXTRACTOR_VERSION,
    )


def record(dto) -> dict:
    return {"kind": type(dto).__name__, "payload": dto.model_dump(mode="json")}


def write(path: Path, records: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    by_message_id: dict[str, str] = {}
    for rel in sorted(EMAILS_USED, key=lambda r: Path(r).name):  # parents before replies
        store = EMAILS_USED[rel][1]
        document, segments = build_document(rel, store, by_message_id)
        if document.meta["message_id"]:
            by_message_id[str(document.meta["message_id"])] = document.id
        write(
            OUT / "documents" / f"{document.id}.json",
            [record(document)] + [record(s) for s in segments],
        )
        observations = [
            build_observation(document, segments, label, store) for label in OBSERVATIONS[rel]
        ]
        write(OUT / "observations" / f"{document.id}.json", [record(o) for o in observations])
        print(document.id, len(segments), "segments,", len(observations), "observations")


if __name__ == "__main__":
    main()
