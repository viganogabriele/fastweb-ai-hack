"""INT-02: conservative, fact-level provenance and temporal corrections.

Exact body resends need the same sender and business date. Forwarded evidence needs
an explicit parent and an identical quote inside a quoted segment. Matching product,
store, author or text similarity alone never proves a copy. Possible overlaps stay
separate and their quantities must not be added by consumers.

Automatic corrections deliberately cover only explicit Italian/English phrases in
the fact's own unquoted evidence and an unambiguous fact in its parent document.
Other languages/ambiguous targets abstain; subjects and fixture metadata are never
used as correction labels. No LLM, contract changes or source mutations are needed.
"""

import hashlib
import json
import re
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations

from tesseract.core.contracts import (
    ArtifactRef,
    EntityLink,
    EvidenceRelation,
    ModuleManifest,
    ModuleResult,
    Observation,
    RunSpec,
    Segment,
    SourceDocument,
)
from tesseract.core.contracts.common import SourceRecord
from tesseract.core.orchestrator import RunContext

MANIFEST = ModuleManifest(
    id="int.dedup",
    version="1",
    layer="integration",
    description="Certain copies, possible overlaps and fact-level temporal corrections",
    requires=("int.link",),
    optional_inputs=(),
    produces=("EvidenceRelation",),
    enabled=True,
    mode="live",
    params_schema={"type": "object", "additionalProperties": False},
)

# Require a replacement/withdrawal statement, never just 'Re:' or 'correction'
# in the subject. Restrict to the evidence of the individual fact.
REPLACE = re.compile(
    r"\b(?:e non|anzich[eé]|invece di|rather than|instead of)\s+\d"
    r"|\b(?:rettifico|correggo|correzione|correction|corrected|replace)\b",
    re.IGNORECASE,
)
RETRACT = re.compile(
    r"\b(?:ritiro|ritiriamo|annullo|annulliamo|smentisco|retract|withdraw)\b",
    re.IGNORECASE,
)
AFFIRMATIVE_RETRACT = re.compile(
    r"^\s*(?:(?:io\s+)?(?:ritiro|ritiriamo|annullo|annulliamo|smentisco)"
    r"|(?:i|we)\s+(?:hereby\s+)?(?:retract|withdraw))\b",
    re.IGNORECASE,
)
AFFIRMATIVE_REPLACE = re.compile(
    r"^\s*(?:(?:io\s+)?(?:rettifico|correggo)|correzione\s*:|correction\s*:"
    r"|corrected\s*:|(?:i|we)\s+(?:hereby\s+)?(?:correct|replace))",
    re.IGNORECASE,
)
UNCERTAIN_INTENT = re.compile(
    r"[?]|\b(?:if|unless|whether|perhaps|maybe|might|may|would|could|should|can|will"
    r"|not|never|no|nothing|none|don['’]t|doesn['’]t|didn['’]t|non|nessun\w*"
    r"|suppos\w*|assum\w*|hypothe\w*|imagin\w*|when|once|after|tomorrow|later"
    r"|se|forse|potre\w*|dovre\w*|eventual\w*|ipot\w*|qualora|quando|appena|dopo|domani)\b"
    r"|\bin (?:case|caso)\b",
    re.IGNORECASE,
)
REPLACEMENT_CONTRAST = re.compile(
    r"\b(?:e non|anzich[eé]|invece di|rather than|instead of)\s+(?=\d)",
    re.IGNORECASE,
)
ASSERTED_VALUE = re.compile(
    r"^\s*(?:il (?:fatturato(?: netto)?|totale)(?: di oggi)?"
    r"|(?:the )?(?:net sales|revenue|total)(?: today)?)\s+(?:e['’]|è|is|are)\s+\d",
    re.IGNORECASE,
)
RefKey = tuple[str, str, str]
LinkMap = dict[RefKey, EntityLink]


def _correction_intent(text: str) -> tuple[str | None, bool]:
    """Accept affirmative statements only; uncertain language must never erase a fact.

    This intentionally abstains on wording outside the small supported grammar.
    The factual contrast '85 e non 58' is allowed; other negation/modal language,
    questions and conditionals require a human even after an affirmative prefix.
    """
    retract, replace = RETRACT.search(text), REPLACE.search(text)
    if not (retract or replace):
        return None, False
    contrast = REPLACEMENT_CONTRAST.search(text)
    unsafe = UNCERTAIN_INTENT.search(REPLACEMENT_CONTRAST.sub("", text))
    if not unsafe:
        if retract and AFFIRMATIVE_RETRACT.search(text):
            return "retracts", False
        if not retract and (
            AFFIRMATIVE_REPLACE.search(text) or (contrast and ASSERTED_VALUE.search(text))
        ):
            return "supersedes", False
    return None, True


def ref(record: SourceRecord) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


def _key(reference: ArtifactRef) -> RefKey:
    return reference.kind, reference.id, reference.version


def _visible(record: SourceRecord, as_of: datetime) -> bool:
    return record.available_at is not None and record.available_at <= as_of


def _norm(text: str | None) -> str:
    return " ".join((text or "").casefold().split())


def _product(obs: Observation, links: LinkMap) -> tuple:
    # Keep the literal mention as well: style-level links must not erase size/colour.
    link = links.get(_key(ref(obs)))
    return (
        _norm(obs.product_mention),
        (link.level, link.target_id) if link and link.status == "linked" else None,
    )


def _same_scope(a: Observation, b: Observation, links: LinkMap) -> bool:
    return (
        a.store_id is not None
        and a.store_id == b.store_id
        and a.kind == b.kind
        and _product(a, links) == _product(b, links)
        and a.quantity.unit == b.quantity.unit
        and a.quantity.currency == b.quantity.currency
    )


def _same_fact(a: Observation, b: Observation) -> bool:
    fields = (
        "kind",
        "store_id",
        "period_start",
        "period_end",
        "product_mention",
        "direction",
        "negated",
        "attribution",
        "reason",
        "reason_text",
        "funnel_stage",
    )
    quantity_fields = ("kind", "value", "low", "high", "unit", "currency")
    return all(getattr(a, f) == getattr(b, f) for f in fields) and all(
        getattr(a.quantity, f) == getattr(b.quantity, f) for f in quantity_fields
    )


def _possible_scope(a: Observation, b: Observation, links: LinkMap) -> bool:
    if a.store_id is None or a.store_id != b.store_id or a.kind != b.kind:
        return False
    left, right = links.get(_key(ref(a))), links.get(_key(ref(b)))
    if left and right and left.status == right.status == "linked":
        return (left.level, left.target_id) == (right.level, right.target_id)
    return (
        not a.product_mention
        or not b.product_mention
        or _norm(a.product_mention) == _norm(b.product_mention)
    )


def _relation(
    a: Observation,
    b: Observation,
    relation: str,
    basis: str,
    inputs: Iterable[SourceRecord],
    spec: RunSpec,
) -> EvidenceRelation:
    records = tuple({_key(ref(r)): r for r in (a, b, *inputs)}.values())
    input_refs = tuple(sorted((ref(r) for r in records), key=_key))
    digest = hashlib.sha256(
        json.dumps(
            [
                relation,
                ref(a).model_dump(),
                ref(b).model_dump(),
                basis,
                [r.model_dump() for r in input_refs],
            ],
            sort_keys=True,
        ).encode()
    ).hexdigest()[:24]
    return EvidenceRelation(
        id=f"rel-{digest}",
        version="v1",
        available_at=max(r.available_at for r in records),
        availability_basis="max_input_available_at",
        source_refs=tuple(dict.fromkeys(s for r in records for s in r.source_refs)),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=spec.as_of,
        input_refs=input_refs,
        producer=MANIFEST.id,
        producer_version=MANIFEST.version,
        from_ref=ref(a),
        to_ref=ref(b),
        relation=relation,
        basis=basis,
        evidence_refs=tuple(ref(r) for r in records if isinstance(r, (SourceDocument, Segment))),
    )


def build_relations(
    observations: Iterable[Observation],
    documents: Iterable[SourceDocument],
    segments: Iterable[Segment],
    links: Iterable[EntityLink],
    spec: RunSpec,
) -> tuple[tuple[EvidenceRelation, ...], tuple[str, ...]]:
    """Pure inference over this snapshot only. Unknown/future availability is excluded.

    Evidence must resolve to the exact document version and canonical segment. A
    missing/invalid parent is an abstention, never permission to guess a relation.
    """
    docs = {(d.id, d.version): d for d in documents if _visible(d, spec.as_of)}
    segs = {_key(ref(s)): s for s in segments if _visible(s, spec.as_of)}
    link_candidates = defaultdict(list)
    invalid_link_ids = set()
    for link in links:
        if not _visible(link, spec.as_of) or (link.run_id, link.scenario_id) != (
            spec.run_id,
            spec.scenario_id,
        ):
            continue
        pins = {r for r in link.input_refs if r.kind == "Observation"}
        if len(pins) != 1 or next(iter(pins)).id != link.observation_id:
            invalid_link_ids.add(link.observation_id)
            continue
        link_candidates[_key(next(iter(pins)))].append(link)
    link_map = {key: values[0] for key, values in link_candidates.items() if len(values) == 1}
    facts, errors, fact_docs, fact_segs = [], [], {}, {}
    for obs in sorted(observations, key=lambda o: (o.available_at or spec.as_of, o.id, o.version)):
        if not _visible(obs, spec.as_of) or obs.store_id not in spec.stores:
            continue
        if obs.id in invalid_link_ids or len(link_candidates[_key(ref(obs))]) > 1:
            errors.append(f"{obs.id}@{obs.version}: ambiguous or unpinned entity links")
            continue
        try:
            evidence_docs = [docs[(e.document_id, e.document_version)] for e in obs.evidence]
            evidence_segs = []
            for evidence in obs.evidence:
                pins = {
                    r for r in obs.input_refs if r.kind == "Segment" and r.id == evidence.segment_id
                }
                if len(pins) != 1:
                    raise ValueError("evidence needs one exact segment version")
                evidence_segs.append(segs[_key(next(iter(pins)))])
                if (
                    ArtifactRef(
                        kind="SourceDocument",
                        id=evidence.document_id,
                        version=evidence.document_version,
                    )
                    not in obs.input_refs
                ):
                    raise ValueError("evidence document version must be pinned")
            for evidence, doc, seg in zip(obs.evidence, evidence_docs, evidence_segs, strict=True):
                evidence.validate_against(doc, seg)
                if doc.meta.get("store_id") not in (None, obs.store_id):
                    raise ValueError("evidence store differs from observation")
            if len({(d.id, d.version) for d in evidence_docs}) != 1:
                raise ValueError("mixed document versions")
        except (KeyError, ValueError):
            errors.append(f"{obs.id}: unavailable or invalid canonical evidence")
            continue
        facts.append(obs)
        fact_docs[_key(ref(obs))] = evidence_docs[0]
        fact_segs[_key(ref(obs))] = tuple(evidence_segs)

    relations = []
    corrected = set()
    for new in facts:
        new_key = _key(ref(new))
        doc = fact_docs[new_key]
        own_quotes = [
            e.quote
            for e, s in zip(new.evidence, fact_segs[new_key], strict=True)
            if not s.is_quoted
        ]
        text = "\n".join(own_quotes)
        intent, uncertain = _correction_intent(text)
        if uncertain:
            errors.append(f"{new.id}: uncertain correction intent; facts retained")
        if intent is None:
            continue
        candidates = [
            old
            for old in facts
            if old.document_id == doc.parent_document_id
            and old.available_at < new.available_at
            and _same_scope(new, old, link_map)
            and new.period_start is not None
            and new.period_end is not None
            and (new.period_start, new.period_end) == (old.period_start, old.period_end)
        ]
        if len(candidates) != 1:
            errors.append(
                f"{new.id}: {intent} needs one explicit parent fact; found {len(candidates)}"
            )
            continue
        old = candidates[0]
        inputs = [doc, fact_docs[_key(ref(old))], *fact_segs[new_key], *fact_segs[_key(ref(old))]]
        inputs += [lk for o in (new, old) if (lk := link_map.get(_key(ref(o)))) is not None]
        relations.append(
            _relation(
                new,
                old,
                intent,
                "Explicit correction in fact evidence; unique parent fact",
                inputs,
                spec,
            )
        )
        corrected.add(frozenset((new_key, _key(ref(old)))))

    # Bucket by store/kind instead of comparing unrelated stores or fact types.
    buckets = defaultdict(list)
    for fact in facts:
        buckets[(fact.store_id, fact.kind)].append(fact)
    for bucket in buckets.values():
        for old, new in combinations(bucket, 2):
            old_key, new_key = _key(ref(old)), _key(ref(new))
            if frozenset((old_key, new_key)) in corrected:
                continue
            a, b = fact_docs[old_key], fact_docs[new_key]
            inputs = [a, b, *fact_segs[old_key], *fact_segs[new_key]]
            inputs += [lk for o in (old, new) if (lk := link_map.get(_key(ref(o)))) is not None]
            quote_equal = tuple(e.quote for e in old.evidence) == tuple(
                e.quote for e in new.evidence
            )
            resend = (
                a.id != b.id
                and bool(a.text.strip())
                and a.text == b.text
                and (
                    a.content_hash == b.content_hash
                    or (
                        a.origin is not None
                        and a.origin == b.origin
                        and a.business_date is not None
                        and a.business_date == b.business_date
                    )
                )
            )
            forwarded = (
                b.parent_document_id == a.id
                and quote_equal
                and all(s.is_quoted for s in fact_segs[new_key])
            )
            if (
                _same_scope(old, new, link_map)
                and _same_fact(old, new)
                and quote_equal
                and (resend or forwarded)
            ):
                relations.append(
                    _relation(
                        new,
                        old,
                        "duplicates",
                        "Exact fact in copied body"
                        if resend
                        else "Exact quoted fact from explicit parent",
                        inputs,
                        spec,
                    )
                )
                continue
            if not _possible_scope(old, new, link_map):
                continue
            # Same store/product/day is only possible overlap, including differing
            # quantities or negation. Disjoint known periods are separate episodes.
            if all(
                t is not None
                for t in (old.period_start, old.period_end, new.period_start, new.period_end)
            ):
                overlap = max(old.period_start, new.period_start) <= min(
                    old.period_end, new.period_end
                )
            else:
                # Unknown event dates cannot prove episodes disjoint, even if the
                # documents arrived on different days.
                overlap = True
            if overlap:
                relations.append(
                    _relation(
                        new,
                        old,
                        "possibly_same_episode",
                        "Compatible scope and overlapping/unknown period; independence unproven",
                        inputs,
                        spec,
                    )
                )
    return tuple(sorted(relations, key=lambda r: r.id)), tuple(errors)


@dataclass(frozen=True)
class OriginGroup:
    """Certain copies count once. The earliest fact supplies age, never its resend."""

    members: tuple[ArtifactRef, ...]
    representative: ArtifactRef
    first_available_at: datetime
    period_start: datetime | None
    period_end: datetime | None


@dataclass(frozen=True)
class DedupState:
    groups: tuple[OriginGroup, ...]
    active_refs: tuple[ArtifactRef, ...]
    non_additive_refs: tuple[ArtifactRef, ...]
    document_count: int


def state_at(
    observations: Iterable[Observation],
    relations: Iterable[EvidenceRelation],
    as_of: datetime,
) -> DedupState:
    """Derive active origin groups without changing history or summing quantities.

    Only exact endpoint versions present at `as_of` can affect the view. Retraction
    statements are not new demand. A correction invalidates every certain copy of
    its target. Supersession chains never resurrect an earlier corrected fact.
    """
    facts = {_key(ref(o)): o for o in observations if _visible(o, as_of)}
    parents = {key: key for key in facts}

    def root(key):
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    visible = [
        r
        for r in relations
        if _visible(r, as_of) and _key(r.from_ref) in facts and _key(r.to_ref) in facts
    ]
    for relation in visible:
        if relation.relation == "duplicates":
            parents[root(_key(relation.from_ref))] = root(_key(relation.to_ref))
    inactive, non_additive = set(), set()
    for relation in visible:
        a, b = root(_key(relation.from_ref)), root(_key(relation.to_ref))
        if relation.relation in ("supersedes", "retracts"):
            inactive.add(b)
            if relation.relation == "retracts":
                inactive.add(a)
        elif relation.relation == "possibly_same_episode" and a != b:
            non_additive.update((a, b))
    grouped = defaultdict(list)
    for key, obs in facts.items():
        grouped[root(key)].append(obs)
    groups, active, uncertain = [], [], []
    for key, members in grouped.items():
        members.sort(key=lambda o: (o.available_at, o.id, o.version))
        first = members[0]
        groups.append(
            OriginGroup(
                tuple(ref(o) for o in members),
                ref(first),
                first.available_at,
                first.period_start,
                first.period_end,
            )
        )
        if key not in inactive:
            active.append(ref(first))
            if key in non_additive:
                uncertain.append(ref(first))
    return DedupState(
        tuple(sorted(groups, key=lambda g: _key(g.representative))),
        tuple(sorted(active, key=_key)),
        tuple(sorted(uncertain, key=_key)),
        len({o.document_id for o in facts.values()}),
    )


def run(ctx: RunContext) -> ModuleResult:
    observations = ctx.repo.list(Observation)
    relations, abstentions = build_relations(
        observations,
        ctx.repo.list(SourceDocument),
        ctx.repo.list(Segment),
        ctx.repo.list(EntityLink),
        ctx.spec,
    )
    # Reuse existing artifacts on a repeated module call (the Repo is immutable).
    existing = {(r.id, r.version) for r in ctx.repo.list(EvidenceRelation)}
    new = [r for r in relations if (r.id, r.version) not in existing]
    written = ctx.repo.put(*new) if new else 0
    state = state_at(observations, relations, ctx.spec.as_of)
    counts = {
        name: sum(r.relation == name for r in relations)
        for name in ("duplicates", "possibly_same_episode", "supersedes", "retracts")
    }
    counts.update(
        observations=len(observations),
        relations_new=written,
        documents=state.document_count,
        origin_groups=len(state.groups),
        active_origins=len(state.active_refs),
        non_additive_origins=len(state.non_additive_refs),
    )
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if abstentions else "succeeded",
        counts=counts,
        errors=(),
        abstentions=abstentions,
    )
