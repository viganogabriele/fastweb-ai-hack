"""ING-04 module: ``ing.extract`` turns document segments into verified ``Observation``s.

AI reads, code counts. The LLM proposes candidates (quote, kind, quantity words, period) through
the single-tool structured output of ``core.llm``; it never returns ids or offsets. Code then:

- locates the quote in the canonical document text, exactly or with runs of whitespace collapsed
  (offsets are mapped back to the canonical text, RFC §4.5); it must occur once, inside one
  segment, or the candidate is rejected and logged as an abstention;
- keeps a number only when the email's own words for it (``quantity_raw``) occur in the
  document and are not a vague quantifier from ``config/domain.yaml``: otherwise the quantity
  becomes ``vague`` or ``unknown`` without an imputed value;
- turns store-local period dates into instants, and drops a period that starts after the mail
  was sent, except for kinds that announce the future (events, operations).

A document whose extraction fails twice (``ExtractionFailed``) is an abstention, never a guess.
Provider errors and replay misses are module errors (status ``degraded``); an exhausted budget
stops the remaining documents.
"""

import hashlib
import re
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from functools import cache
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

import yaml
from pydantic import BaseModel, Field, ValidationError

from tessera.core.cache import ReplayMiss
from tessera.core.config import get_settings
from tessera.core.contracts import (
    ArtifactRef,
    Evidence,
    ModuleManifest,
    ModuleResult,
    Observation,
    Quantity,
    Segment,
    SourceDocument,
)
from tessera.core.llm import BudgetExceeded, ExtractionFailed, LLMCallFailed
from tessera.modules.sources.emails import load_stores

PROMPT_PATH = Path(__file__).resolve().parents[3] / "prompts" / "extract_observations.v1.md"
EXTRACTOR_VERSION = "llm-extract-v1"
OBSERVATION_VERSION = "v1"
# Kinds that legitimately refer to days after the mail was sent.
FUTURE_KINDS = {"local_event", "operational_issue"}

MANIFEST = ModuleManifest(
    id="ing.extract",
    version="1",
    layer="ingestion",
    description="LLM candidates from document segments, quotes and numbers verified by code",
    requires=("src.email",),
    optional_inputs=(),
    produces=("Observation",),
    enabled=True,
    mode="live",
    params_schema={"type": "object", "additionalProperties": False},
)

Kind = Literal[
    "unmet_demand",
    "demand_up",
    "demand_down",
    "stockout",
    "low_stock",
    "stock_discrepancy",
    "product_feedback",
    "traffic_change",
    "customer_profile",
    "operational_issue",
    "sales_figure",
    "local_event",
    "other",
]
Reason = Literal[
    "fit",
    "size_availability",
    "colour",
    "fabric_material",
    "quality_defect",
    "price",
    "style",
    "other",
]


class Candidate(BaseModel):
    """What the model may propose. Ids, offsets and evidence are assigned by code."""

    quote: str = Field(min_length=1)
    segment_idx: int | None = None
    kind: Kind
    product_mention: str | None = None
    quantity_kind: Literal["exact", "range", "vague", "unknown"] = "unknown"
    value: float | None = None
    low: float | None = None
    high: float | None = None
    unit: Literal["units", "customers", "requests", "visitors", "money", "percent"] | None = None
    currency: str | None = None
    quantity_raw: str | None = None
    direction: Literal["up", "down", "none"] = "none"
    reason: Reason | None = None
    reason_text: str | None = None
    time_text: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    attribution: Literal["store_staff", "customer", "hq", "third_party", "unknown"] = "unknown"
    negated: bool = False


class Candidates(BaseModel):
    observations: list[Candidate]


class Rejected(ValueError):
    """A candidate that code cannot verify; logged as an abstention."""


@cache
def prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


@cache
def vague_quantifiers(config_dir: Path) -> tuple[str, ...]:
    domain = yaml.safe_load((config_dir / "domain.yaml").read_text(encoding="utf-8"))
    words = {w.casefold() for ws in domain["vague_quantifiers"].values() for w in ws}
    return tuple(sorted(words, key=len, reverse=True))


def _collapse(text: str) -> tuple[str, list[int]]:
    """Text with whitespace runs as one space, and each kept character's canonical index."""
    out, index = [], []
    for i, char in enumerate(text):
        if char.isspace():
            if out and out[-1] == " ":
                continue
            char = " "
        out.append(char)
        index.append(i)
    return "".join(out), index


def locate(document: SourceDocument, segments: list[Segment], candidate: Candidate) -> Evidence:
    """Evidence for the quote: one occurrence, inside one segment, offsets in the canonical text."""
    quote = candidate.quote.strip()
    spans = [(m.start(), m.end()) for m in re.finditer(re.escape(quote), document.text)]
    if not spans:
        collapsed, index = _collapse(document.text)
        needle, _ = _collapse(quote)
        spans = [
            (index[m.start()], index[m.end() - 1] + 1)
            for m in re.finditer(re.escape(needle), collapsed)
        ]
    if not spans:
        raise Rejected("quote not found in the document")

    def segment_of(start: int, end: int) -> Segment | None:
        return next((s for s in segments if s.char_start <= start and end <= s.char_end), None)

    located = [(span, segment_of(*span)) for span in spans]
    located = [(span, segment) for span, segment in located if segment is not None]
    if len(located) > 1 and candidate.segment_idx is not None:
        located = [(s, seg) for s, seg in located if seg.idx == candidate.segment_idx]
    if not located:
        raise Rejected("quote crosses segment boundaries")
    if len(located) > 1:
        raise Rejected("quote occurs more than once")
    (start, end), segment = located[0]
    evidence = Evidence(
        document_id=document.id,
        document_version=document.version,
        segment_id=segment.id,
        quote=document.text[start:end],
        char_start=start,
        char_end=end,
    )
    evidence.validate_against(document, segment)
    return evidence


def _mentions(text: str, word: str) -> bool:
    # CJK text has no spaces between words: whole-word matching only for ASCII words.
    if word.isascii():
        return re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text) is not None
    return word in text


def quantity(candidate: Candidate, document: SourceDocument, vague: tuple[str, ...]) -> Quantity:
    """The model's quantity, kept only as far as the email's own words support it."""
    raw = (candidate.quantity_raw or "").strip() or None
    if (
        raw is not None
        and _collapse(raw)[0].casefold() not in _collapse(document.text)[0].casefold()
    ):
        raw = None
    kind = candidate.quantity_kind
    if raw is not None and any(_mentions(raw.casefold(), word) for word in vague):
        kind = "vague"
    if kind in ("exact", "range") and raw is None:
        kind = "unknown"  # a number the email does not state is never kept
    numeric = kind in ("exact", "range")
    try:
        return Quantity(
            kind=kind,
            value=candidate.value if kind == "exact" else None,
            low=candidate.low if kind == "range" else None,
            high=candidate.high if kind == "range" else None,
            unit=candidate.unit,
            currency=((candidate.currency or "").upper() or None) if numeric else None,
            raw=raw,
        )
    except ValidationError:
        # e.g. money without a currency: the words stay, the number does not.
        return Quantity(kind="unknown", unit=candidate.unit, raw=raw)


def period(
    candidate: Candidate, sent_at: datetime, timezone: str
) -> tuple[datetime | None, datetime | None]:
    zone = ZoneInfo(timezone)
    start = candidate.period_start
    end = candidate.period_end
    if start is None or (end is not None and end < start):
        return None, None
    if start > sent_at.astimezone(zone).date() and candidate.kind not in FUTURE_KINDS:
        return None, None
    begin = datetime.combine(start, time.min, zone)
    finish = (
        datetime.combine(end + timedelta(days=1), time.min, zone) - timedelta(seconds=1)
        if end is not None
        else None
    )
    return begin, finish


def messages(document: SourceDocument, segments: list[Segment], timezone: str) -> list[dict]:
    sent = document.available_at.astimezone(ZoneInfo(timezone))
    lines = [
        f"Store: {document.meta.get('store_id')}",
        f"Store language: {document.language}",
        f"Sent (store local time): {sent:%A %Y-%m-%d %H:%M}",
        f"Subject: {document.meta.get('subject', '')}",
        "",
    ]
    for segment in segments:
        flag = " [quoted]" if segment.is_quoted else ""
        lines.append(f"--- segment {segment.idx}{flag} ---")
        lines.append(segment.text)
    return [
        {"role": "system", "content": prompt()},
        {"role": "user", "content": "\n".join(lines)},
    ]


def observe(
    ctx_spec,
    document: SourceDocument,
    segments: list[Segment],
    candidate: Candidate,
    number: int,
    timezone: str,
    vague: tuple[str, ...],
) -> Observation:
    evidence = locate(document, segments, candidate)
    start, end = period(candidate, document.available_at, timezone)
    return Observation(
        id=f"obs-{document.id.removeprefix('doc-')}-{number}",
        version=OBSERVATION_VERSION,
        available_at=document.available_at,
        availability_basis="document_available_at",
        source_refs=document.source_refs,
        run_id=ctx_spec.run_id,
        scenario_id=ctx_spec.scenario_id,
        # The simulated evening, not the wall clock: replays stay byte-identical.
        computed_at=ctx_spec.as_of,
        input_refs=(
            ArtifactRef(kind="SourceDocument", id=document.id, version=document.version),
            ArtifactRef(
                kind="Segment",
                id=evidence.segment_id,
                version=next(s.version for s in segments if s.id == evidence.segment_id),
            ),
        ),
        producer=MANIFEST.id,
        producer_version=MANIFEST.version,
        document_id=document.id,
        kind=candidate.kind,
        store_id=document.meta.get("store_id"),
        period_start=start,
        period_end=end,
        time_text=candidate.time_text,
        product_mention=candidate.product_mention,
        quantity=quantity(candidate, document, vague),
        direction=candidate.direction,
        reason=candidate.reason,
        reason_text=candidate.reason_text,
        attribution=candidate.attribution,
        negated=candidate.negated,
        evidence=(evidence,),
        extractor_version=EXTRACTOR_VERSION,
    )


def run(ctx) -> ModuleResult:
    settings = get_settings()
    stores = load_stores(settings.sources_dir)
    vague = vague_quantifiers(settings.config_dir)
    llm = ctx.clients["llm"]
    prompt_hash = hashlib.sha256(prompt().encode()).hexdigest()
    by_document: dict[str, list[Segment]] = defaultdict(list)
    for segment in ctx.repo.list(Segment):
        by_document[segment.document_id].append(segment)
    counts = defaultdict(int)
    errors: list[str] = []
    abstentions: list[str] = []
    for document in ctx.repo.list(SourceDocument):
        segments = sorted(by_document.get(document.id, []), key=lambda s: s.idx)
        store = stores.get(document.meta.get("store_id"))
        if not segments or store is None:
            counts["documents_skipped"] += 1
            continue
        try:
            proposed = llm.extract(
                Candidates,
                messages(document, segments, store.timezone),
                cache_context={
                    "prompt": f"{PROMPT_PATH.name}:{prompt_hash}",
                    "extractor_version": EXTRACTOR_VERSION,
                    "document": [document.id, document.version, document.content_hash],
                    "text_version": document.text_version,
                },
                temperature=0,
            )
        except ExtractionFailed:
            abstentions.append(f"{document.id}: extraction failed validation twice")
            counts["documents_abstained"] += 1
            continue
        except (ReplayMiss, LLMCallFailed) as error:
            errors.append(f"{document.id}: {type(error).__name__}")
            continue
        except BudgetExceeded:
            errors.append(f"{document.id}: LLM budget exhausted, remaining documents not read")
            break
        counts["documents"] += 1
        observations = []
        for candidate in proposed.observations:
            try:
                observation = observe(
                    ctx.spec,
                    document,
                    segments,
                    candidate,
                    len(observations),
                    store.timezone,
                    vague,
                )
            except (Rejected, ValidationError) as error:
                reason = str(error) if isinstance(error, Rejected) else "invalid observation"
                abstentions.append(f"{document.id}: {candidate.kind} rejected ({reason})")
                counts["candidates_rejected"] += 1
                continue
            observations.append(observation)
            if candidate.quantity_kind in ("exact", "range") and observation.quantity.kind not in (
                "exact",
                "range",
            ):
                counts["numbers_dropped"] += 1
        if observations:
            ctx.repo.put(*observations)
        counts["observations"] += len(observations)
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if errors else "succeeded",
        counts=dict(counts),
        errors=tuple(errors),
        abstentions=tuple(abstentions),
    )
