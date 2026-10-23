"""ING-04 module: ``ing.extract`` turns document segments into verified ``Observation``s.

AI reads, code counts. The LLM proposes candidates (quote, kind, quantity words, period) through
the single-tool structured output of ``core.llm``; it never returns ids or offsets. Code then:

- locates the quote in the canonical document text, exactly or with runs of whitespace collapsed
  (offsets are mapped back to the canonical text, RFC §4.5); it must occur once, inside one
  segment, or the candidate is rejected and logged as an abstention;
- keeps a number only when the email's own words for it (``quantity_raw``) lie in the
  evidence segment, are not a vague quantifier from ``config/domain.yaml`` and actually read as
  that number (decimal comma or point, thousands separators, k/mila/万 suffixes, a few number
  words); money keeps its currency only when the segment shows it or it is the store's own.
  Otherwise the quantity becomes ``vague`` or ``unknown`` without an imputed value. Full
  multilingual quantity parsing is ING-09; until then unparsed numbers are dropped, not trusted;
- turns store-local period dates into instants, drops a period that starts after the mail was
  sent and treats a future end as still ongoing, except for kinds that announce the future.

Candidates are validated independently: unsupported optional unit/reason strings become null,
and invalid required fields reject only their item. Both are reported as abstentions. Unknown
units never become piece counts; the quantity verifier drops their unsupported numeric values.
The tool schema and prompt remain strict so recorded raw responses can be replayed unchanged.

A document whose envelope fails twice (``ExtractionFailed``) is an abstention, never a guess.
Provider errors and replay misses are module errors (status ``degraded``); an exhausted budget
stops the remaining documents.
"""

import hashlib
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta
from functools import cache
from pathlib import Path
from typing import Literal, get_args
from zoneinfo import ZoneInfo

import yaml
from pydantic import BaseModel, Field, PrivateAttr, ValidationError, model_validator

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
from tessera.modules.sources.emails import Store, load_stores

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
Unit = Literal["units", "customers", "requests", "visitors", "money", "percent"]


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
    unit: Unit | None = None
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
    _rejected: tuple[tuple[int, str], ...] = PrivateAttr(default=())
    _optional_dropped: tuple[tuple[int, str], ...] = PrivateAttr(default=())

    @model_validator(mode="wrap")
    @classmethod
    def validate_items(cls, value, handler):
        # Preserve envelope validation/retry and the strict tool schema. Only item
        # failures are isolated; required semantic fields are never guessed.
        if not isinstance(value, dict) or not isinstance(value.get("observations"), list):
            return handler(value)
        accepted, rejected, dropped = [], [], []
        for index, item in enumerate(value["observations"]):
            normalized = dict(item) if isinstance(item, dict) else item
            cleared = []
            if isinstance(normalized, dict):
                for field, allowed in (("unit", get_args(Unit)), ("reason", get_args(Reason))):
                    raw = normalized.get(field)
                    if isinstance(raw, str) and raw not in allowed:
                        normalized[field] = None
                        cleared.append((index, field))
            try:
                candidate = Candidate.model_validate(normalized)
            except ValidationError as error:
                fields = sorted(
                    {
                        ".".join(map(str, detail["loc"])) or "candidate"
                        for detail in error.errors(include_input=False, include_url=False)
                    }
                )
                rejected.append((index, ", ".join(fields)))
                continue
            accepted.append(candidate)
            dropped.extend(cleared)
        parsed = handler({**value, "observations": accepted})
        parsed._rejected = tuple(rejected)
        parsed._optional_dropped = tuple(dropped)
        return parsed


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


def _occurrences(needle: str, text: str) -> list[int]:
    """Every start index, overlapping ones included ("aa" occurs twice in "aaa")."""
    return [m.start() for m in re.finditer(f"(?={re.escape(needle)})", text)] if needle else []


def locate(document: SourceDocument, segments: list[Segment], candidate: Candidate) -> Evidence:
    """Evidence for the quote: one occurrence, inside one segment, offsets in the canonical text."""
    quote = candidate.quote.strip()
    spans = [(start, start + len(quote)) for start in _occurrences(quote, document.text)]
    if not spans:
        collapsed, index = _collapse(document.text)
        needle, _ = _collapse(quote)
        spans = [
            (index[start], index[start + len(needle) - 1] + 1)
            for start in _occurrences(needle, collapsed)
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


_MULTIPLIERS = {
    "k": 1e3,
    "mila": 1e3,
    "mln": 1e6,
    "千": 1e3,
    "万": 1e4,
    "萬": 1e4,
    "천": 1e3,
    "만": 1e4,
    "억": 1e8,
}
_NUMBER = re.compile(r"(\d[\d.,'’]*)\s*(k|mila|mln|千|万|萬|천|만|억)?(?![a-z])", re.IGNORECASE)
_WORDS = {
    "zero": 0,
    "nessun": 0,
    "nessuno": 0,
    "none": 0,
    "no": 0,
    "aucun": 0,
    "ningún": 0,
    "un": 1,
    "uno": 1,
    "una": 1,
    "one": 1,
    "a": 1,
    "an": 1,
    "une": 1,
    "ein": 1,
    "eine": 1,
    "due": 2,
    "two": 2,
    "deux": 2,
    "dos": 2,
    "zwei": 2,
    "tre": 3,
    "three": 3,
    "trois": 3,
    "tres": 3,
    "drei": 3,
}
_CURRENCY_MARKS = {
    "EUR": ("€", "eur", "euro"),
    "USD": ("$", "usd", "dollar"),
    "GBP": ("£", "gbp"),
    "JPY": ("¥", "円", "jpy", "yen"),
    "CNY": ("¥", "元", "rmb", "cny"),
    "KRW": ("₩", "원", "krw"),
    "CHF": ("chf",),
    "HKD": ("hk$", "hkd"),
    "AUD": ("a$", "aud"),
    "SGD": ("s$", "sgd"),
    "AED": ("aed",),
    "DKK": ("dkk", "kr"),
    "TWD": ("nt$", "twd"),
}


def _token_values(token: str) -> set[float]:
    """Readings of one digit run: thousands groups need exactly three digits, a decimal
    separator may appear once. "58,0" is 58.0, never 580; "1.234" is 1234 or 1.234."""
    groups = re.split(r"[.,'’]", token)
    if len(groups) == 1:
        return {float(token)}
    values: set[float] = set()
    if (
        1 <= len(groups[0]) <= 3
        and not groups[0].startswith("0")
        and all(len(g) == 3 for g in groups[1:])
    ):
        values.add(float("".join(groups)))
    last = max(token.rfind("."), token.rfind(","))
    if last != -1 and token.count(token[last]) == 1 and token[last + 1 :].isdigit():
        values.add(float(f"{re.sub(r"[.,'’]", '', token[:last]) or 0}.{token[last + 1 :]}"))
    return values


def readings(raw: str) -> set[float]:
    """Every value the email's words can mean; ambiguous separators give both readings."""
    values: set[float] = set()
    for match in _NUMBER.finditer(raw):
        multiplier = _MULTIPLIERS.get((match.group(2) or "").casefold(), 1)
        values |= {c * multiplier for c in _token_values(match.group(1).rstrip(".,'’"))}
    if not values:
        values = {float(_WORDS[w]) for w in re.findall(r"\w+", raw.casefold()) if w in _WORDS}
    return values


def _reads_as(value: float | None, raw: str, values: set[float]) -> bool:
    if value is None:
        return False
    signed = value < 0
    if signed and not re.search(r"[-−]", raw):
        return False
    return any(abs(abs(value) - v) <= 1e-9 * max(1.0, v) for v in values)


def _stated_in(raw: str, text: str) -> bool:
    """`raw` occurs in `text` as its own words: "2" is not found in "12" or "2,5"."""
    before = r"(?<!\d)(?<!\d[.,'’])" if raw[:1].isdigit() else ""
    after = r"(?!\d)(?![.,'’]\d)" if raw[-1:].isdigit() else ""
    return re.search(f"{before}{re.escape(raw)}{after}", text) is not None


def quantity(
    candidate: Candidate,
    segment: Segment,
    store_currency: str,
    vague: tuple[str, ...],
) -> Quantity:
    """The model's quantity, kept only as far as the evidence segment's own words support it."""
    raw = (candidate.quantity_raw or "").strip() or None
    text = _collapse(segment.text)[0].casefold()
    if raw is not None and not _stated_in(_collapse(raw)[0].casefold(), text):
        raw = None
    kind = candidate.quantity_kind
    if raw is not None and any(_mentions(raw.casefold(), word) for word in vague):
        kind = "vague"
    if kind in ("exact", "range"):
        values = readings(raw) if raw is not None else set()
        stated = (
            _reads_as(candidate.value, raw, values)
            if kind == "exact"
            else _reads_as(candidate.low, raw, values) and _reads_as(candidate.high, raw, values)
        )
        if not stated:
            kind = "unknown"  # a number the email does not state is never kept
    currency = (candidate.currency or "").upper() or None
    if currency is not None and currency != store_currency.upper():
        marks = _CURRENCY_MARKS.get(currency, (currency.casefold(),))
        if not any(mark in text for mark in marks):
            currency = None
    numeric = kind in ("exact", "range")
    try:
        return Quantity(
            kind=kind,
            value=candidate.value if kind == "exact" else None,
            low=candidate.low if kind == "range" else None,
            high=candidate.high if kind == "range" else None,
            unit=candidate.unit,
            currency=currency if numeric else None,
            raw=raw,
        )
    except ValidationError:
        # e.g. money without a supported currency: the words stay, the number does not.
        return Quantity(kind="unknown", unit=candidate.unit, raw=raw)


def period(
    candidate: Candidate, sent_at: datetime, timezone: str
) -> tuple[datetime | None, datetime | None]:
    zone = ZoneInfo(timezone)
    start = candidate.period_start
    end = candidate.period_end
    if start is None or (end is not None and end < start):
        return None, None
    sent = sent_at.astimezone(zone).date()
    if candidate.kind not in FUTURE_KINDS:
        if start > sent:
            return None, None
        if end is not None and end > sent:
            end = None  # a claim about later days is not observed: still ongoing at send time
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
    store: Store,
    vague: tuple[str, ...],
) -> Observation:
    evidence = locate(document, segments, candidate)
    segment = next(s for s in segments if s.id == evidence.segment_id)
    start, end = period(candidate, document.available_at, store.timezone)
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
            ArtifactRef(kind="Segment", id=segment.id, version=segment.version),
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
        quantity=quantity(candidate, segment, store.currency, vague),
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
    jobs = []
    for document in ctx.repo.list(SourceDocument):
        segments = sorted(
            (
                s
                for s in by_document.get(document.id, [])
                if s.text_version == document.text_version
            ),
            key=lambda s: s.idx,
        )
        store = stores.get(document.meta.get("store_id"))
        jobs.append((document, segments, store))

    def read(job) -> Candidates:
        document, segments, store = job
        return llm.extract(
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

    # Only the LLM calls run in parallel (the client bounds them); results are consumed in
    # document order on this thread, so observations, counts and errors match a serial run.
    pool = ThreadPoolExecutor(max_workers=settings.llm_concurrency)
    try:
        futures = [
            pool.submit(read, job) if job[1] and job[2] is not None else None for job in jobs
        ]
        for (document, segments, store), future in zip(jobs, futures, strict=True):
            if future is None:
                reason = "no segments for its text version" if not segments else "unknown store"
                abstentions.append(f"{document.id}: not read ({reason})")
                counts["documents_skipped"] += 1
                continue
            try:
                proposed = future.result()
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
            for index, fields in proposed._rejected:
                abstentions.append(f"{document.id}: candidate {index} rejected (invalid {fields})")
                counts["candidates_rejected"] += 1
            for index, field in proposed._optional_dropped:
                abstentions.append(f"{document.id}: candidate {index} unsupported {field} cleared")
                counts["optional_fields_dropped"] += 1
            observations = []
            for candidate in proposed.observations:
                try:
                    observation = observe(
                        ctx.spec,
                        document,
                        segments,
                        candidate,
                        len(observations),
                        store,
                        vague,
                    )
                except ValueError as error:  # Rejected, ValidationError, validate_against
                    reason = str(error) if isinstance(error, Rejected) else "invalid observation"
                    abstentions.append(f"{document.id}: {candidate.kind} rejected ({reason})")
                    counts["candidates_rejected"] += 1
                    continue
                observations.append(observation)
                numeric = ("exact", "range")
                if candidate.quantity_kind in numeric and observation.quantity.kind not in numeric:
                    counts["numbers_dropped"] += 1
            if observations:
                ctx.repo.put(*observations)
            counts["observations"] += len(observations)
    finally:
        pool.shutdown(cancel_futures=True)
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if errors else "succeeded",
        counts=dict(counts),
        errors=tuple(errors),
        abstentions=tuple(abstentions),
    )
