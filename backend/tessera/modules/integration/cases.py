"""INT-03 module: ``int.cases`` groups the run's observations into cases for a human.

Inputs are the run's ``Observation``, ``EntityLink`` (INT-01), ``EvidenceRelation`` (INT-02) and
``SourceDocument`` records visible at ``as_of``. Rules:

- Each observation kind maps to one case type (``KIND_CASE_TYPE``); the owner is
  ``owners[case_type]`` in ``config/domain.yaml``. A case type without an owner is a config
  error. ``sales_figure`` and ``local_event`` open no case: they are metrics and context.
- Certain copies (``duplicates``) form one origin group and always land in the same case.
  ``supersedes`` disables the target group and ``retracts`` both groups, as in INT-02; disabled
  facts are never supporting evidence, the relation stays in ``context_refs``.
- The scope comes from the exact observation version's link: ``linked`` gives its level and
  target, ``not_product`` the store. Ambiguous, unlinked, missing or conflicting links give
  ``scope=unknown`` and status ``verify``: the case is kept, never dropped, and the link with its
  candidates is cited. Unknown-scope groups are never merged with each other.
- Groups with the same store, case type and resolved scope join one case, in arrival order, while
  a group arrives within ``policy.decay.max_validity`` of the case's last independent evidence;
  otherwise they open a new case. Earlier membership never depends on later arrivals.
- A negated fact opens no case; it is ``contradicting`` evidence of the open case with the same
  key at its arrival.
- ``n_documents`` counts documents of the supporting facts; documents joined by certain copies are
  one origin. An origin whose documents all lack ``origin`` counts as unknown. A copy never
  refreshes ``last_independent_evidence_at``. Possible overlaps are flagged, never summed.
- Priority, reason and blocking uncertainties come from fixed templates over these facts.
  ``valid_until`` is set for decaying demand signals only; ``decision_due_at`` is left to INT-04.

Each case is available at its latest input, ``computed_at`` is the run's ``as_of`` and its id is
fixed by the group that opened it: ``case-<store>-<scope id|unknown>-<local date>``.
"""

import re
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol
from zoneinfo import ZoneInfo

import yaml

from tessera.core import repo
from tessera.core.config import get_settings
from tessera.core.contracts import (
    ArtifactRef,
    Case,
    EntityLink,
    EvidenceRelation,
    ModuleManifest,
    ModuleResult,
    Observation,
    RunSpec,
    SourceDocument,
)
from tessera.core.contracts.common import SourceRecord

MANIFEST = ModuleManifest(
    id="int.cases",
    version="1",
    layer="integration",
    description=(
        "Cases per store, case type, product scope and window, unlinked ones included as "
        "verify; owner from domain.yaml, document and origin counts"
    ),
    requires=("int.dedup",),
    optional_inputs=(),
    produces=("Case",),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {"max_validity_days": {"type": "integer", "minimum": 1, "maximum": 60}},
        "additionalProperties": False,
    },
)

KIND_CASE_TYPE = {
    "unmet_demand": "unmet_demand",
    "stockout": "unmet_demand",
    "low_stock": "unmet_demand",
    "demand_up": "demand_shift",
    "demand_down": "demand_shift",
    "stock_discrepancy": "stock_discrepancy",
    "product_feedback": "product_feedback",
    "traffic_change": "traffic_change",
    "customer_profile": "customer_profile",
    "operational_issue": "operational_issue",
    "other": "unknown",
}
NO_CASE_KINDS = frozenset({"sales_figure", "local_event"})
DECAYING = frozenset({"unmet_demand", "demand_shift", "traffic_change"})
STOCK_KINDS = frozenset({"stockout", "low_stock"})
COUNT_UNITS = frozenset({"requests", "customers"})

RefKey = tuple[str, str, str]


class Context(Protocol):
    """The part of PLT-04's ``RunContext`` this module uses."""

    @property
    def spec(self) -> RunSpec: ...
    @property
    def repo(self) -> repo.Repo: ...
    @property
    def params(self) -> Mapping[str, Any]: ...


def ref(record: SourceRecord) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


def _key(reference: ArtifactRef) -> RefKey:
    return reference.kind, reference.id, reference.version


def _visible(record: SourceRecord, as_of: datetime) -> bool:
    return record.available_at is not None and record.available_at <= as_of


def load_domain(config_dir: Path) -> tuple[dict[str, str], int]:
    """Owners per case type and the validity in days; every case type must have an owner."""
    domain = yaml.safe_load((config_dir / "domain.yaml").read_text(encoding="utf-8"))
    owners = {str(k): str(v) for k, v in domain["owners"].items()}
    missing = sorted(set(KIND_CASE_TYPE.values()) - set(owners))
    if missing:
        raise ValueError(f"domain.yaml owners missing for case types: {missing}")
    return owners, int(domain["policy"]["decay"]["max_validity"]["value"])


@dataclass
class Group:
    """One origin group: an observation and its certain copies, earliest first."""

    members: list[Observation]
    link: EntityLink | None
    link_problem: str | None
    scope_level: str
    scope_id: str | None

    @property
    def first(self) -> Observation:
        return self.members[0]

    @property
    def available_at(self) -> datetime:
        return self.first.available_at  # type: ignore[return-value]


@dataclass
class Draft:
    case_type: str
    store_id: str | None
    scope_level: str
    scope_id: str | None
    groups: list[Group]
    negated: list[Group] = field(default_factory=list)

    def last_independent(self) -> datetime:
        return max(g.available_at for g in self.groups)


def _links(links: Iterable[EntityLink], spec: RunSpec) -> dict[RefKey, list[EntityLink]]:
    """Links per exact observation version; a link must pin exactly one observation."""
    found: dict[RefKey, list[EntityLink]] = defaultdict(list)
    for link in links:
        if not _visible(link, spec.as_of):
            continue
        pins = [r for r in link.input_refs if r.kind == "Observation"]
        if len(pins) == 1 and pins[0].id == link.observation_id:
            found[_key(pins[0])].append(link)
    return found


def _scope(
    obs: Observation, links: list[EntityLink]
) -> tuple[EntityLink | None, str | None, str, str | None]:
    if not links:
        return None, "missing", "unknown", None
    if len({(lk.status, lk.level, lk.target_id) for lk in links}) > 1:
        return links[0], "conflicting", "unknown", None
    link = links[0]
    if link.status == "linked":
        return link, None, str(link.level), link.target_id
    if link.status == "not_product" and obs.store_id is not None:
        return link, None, "store", obs.store_id
    return link, link.status, "unknown", None


def _groups(
    facts: dict[RefKey, Observation],
    relations: list[EvidenceRelation],
    links: dict[RefKey, list[EntityLink]],
) -> tuple[list[Group], set[RefKey]]:
    """Origin groups by certain copies, and the facts disabled by corrections."""
    parents = {key: key for key in facts}

    def root(key: RefKey) -> RefKey:
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    for relation in relations:
        if relation.relation == "duplicates":
            parents[root(_key(relation.from_ref))] = root(_key(relation.to_ref))
    inactive_roots = set()
    for relation in relations:
        if relation.relation in ("supersedes", "retracts"):
            inactive_roots.add(root(_key(relation.to_ref)))
            if relation.relation == "retracts":
                inactive_roots.add(root(_key(relation.from_ref)))
    members: dict[RefKey, list[Observation]] = defaultdict(list)
    for key, obs in facts.items():
        members[root(key)].append(obs)
    groups, inactive = [], set()
    for group_root, observations in members.items():
        observations.sort(key=lambda o: (o.available_at, o.id, o.version))
        if group_root in inactive_roots:
            inactive.update(_key(ref(o)) for o in observations)
            continue
        first = observations[0]
        link, problem, level, target = _scope(first, links.get(_key(ref(first)), []))
        groups.append(Group(observations, link, problem, level, target))
    groups.sort(key=lambda g: (g.available_at, g.first.id, g.first.version))
    return groups, inactive


def _cluster(groups: list[Group], validity: timedelta) -> tuple[list[Draft], int]:
    drafts: list[Draft] = []
    open_by_key: dict[tuple, Draft] = {}
    unattached = 0
    for group in groups:
        case_type = KIND_CASE_TYPE[group.first.kind]
        store = group.first.store_id
        resolved = group.scope_level != "unknown" and store is not None
        key = (store, case_type, group.scope_level, group.scope_id)
        current = open_by_key.get(key) if resolved else None
        alive = current is not None and group.available_at <= current.last_independent() + validity
        if group.first.negated:
            if alive:
                current.negated.append(group)  # type: ignore[union-attr]
            else:
                unattached += 1
            continue
        if alive:
            current.groups.append(group)  # type: ignore[union-attr]
            continue
        draft = Draft(case_type, store, group.scope_level, group.scope_id, [group])
        drafts.append(draft)
        if resolved:
            open_by_key[key] = draft
    return drafts, unattached


def _priority(draft: Draft, kinds: set[str], reasons: set[str | None]) -> tuple[str, str]:
    stock = sorted(k.replace("_", "-") for k in kinds & STOCK_KINDS)
    if draft.case_type == "unmet_demand" and stock and "unmet_demand" in kinds:
        level, text = "high", f"Store reports {' and '.join(stock)} while customers ask for it."
    elif draft.case_type == "unmet_demand" and "unmet_demand" in kinds:
        level, text = "medium", "Customers asked for a product the store could not sell."
    elif draft.case_type == "unmet_demand":
        level, text = "medium", f"Store reports {' and '.join(stock)}."
    elif draft.case_type == "product_feedback" and "quality_defect" in reasons:
        level, text = "medium", "Quality defect reported."
    elif draft.case_type in ("stock_discrepancy", "operational_issue"):
        level, text = "medium", f"{draft.case_type.replace('_', ' ').capitalize()} reported."
    else:
        level, text = "low", f"{draft.case_type.replace('_', ' ').capitalize()} signal."
    if draft.scope_level == "unknown":
        text += " Product not identified."
    if draft.store_id is None:
        text += " Store not identified."
    return level, text


def _uncertainties(
    draft: Draft,
    supporting: list[Observation],
    relations: list[EvidenceRelation],
    members: set[RefKey],
) -> list[str]:
    out = []
    first = draft.groups[0]
    if draft.store_id is None:
        out.append("Store not identified.")
    if first.link_problem == "missing":
        out.append("No entity link: the product mention was not checked against the catalog.")
    elif first.link_problem == "conflicting":
        out.append("Conflicting entity links for one observation: product not identified.")
    elif first.link_problem in ("ambiguous", "unlinked") and first.link is not None:
        ids = ", ".join(c.target_id for c in first.link.candidates)
        mention = first.first.product_mention or "the product"
        if first.link_problem == "ambiguous":
            out.append(f"Product ambiguous: '{mention}' fits {ids}.")
        else:
            out.append(f"Product '{mention}' not found in the catalog" + (
                f"; closest candidates {ids}." if ids else "."
            ))
    if draft.case_type == "unknown":
        out.append("Signal type 'other': needs human review.")
    if draft.scope_level == "style" and draft.case_type in DECAYING:
        out.append("Linked at style level: the colour is not identified.")
    vague = [o for o in supporting if o.quantity.kind in ("vague", "unknown")]
    if vague:
        out.append(f"Quantity vague or missing in {len(vague)} report(s): no count, no uplift.")
    if any(
        o.kind == "unmet_demand"
        and o.quantity.kind in ("exact", "range")
        and o.quantity.unit in COUNT_UNITS
        for o in supporting
    ):
        out.append("Requests are not units: no conversion to demand without evidence.")
    if any(o.kind in STOCK_KINDS for o in supporting):
        out.append("Stock level is the store's statement; ERP stock not checked yet.")
    inside = [
        r
        for r in relations
        if r.relation == "possibly_same_episode"
        and _key(r.from_ref) in members
        and _key(r.to_ref) in members
    ]
    across = [
        r
        for r in relations
        if r.relation == "possibly_same_episode"
        and (_key(r.from_ref) in members) != (_key(r.to_ref) in members)
    ]
    if inside:
        out.append(
            f"{len(inside)} pair(s) of reports may describe the same episode: "
            "do not add their quantities."
        )
    if across:
        out.append("A report may describe the same episode as another case: do not add across.")
    if draft.negated:
        out.append(f"{len(draft.negated)} negated report(s) contradict this case.")
    return out


def _case_id(draft: Draft, zones: Mapping[str, str], taken: set[str]) -> str:
    first = draft.groups[0].first
    start = first.period_start or draft.groups[0].available_at
    zone = ZoneInfo(zones[draft.store_id]) if draft.store_id in zones else UTC
    day = start.astimezone(zone).strftime("%Y%m%d")
    store = (draft.store_id or "nostore").lower()
    scope = re.sub(r"[^a-z0-9-]+", "-", (draft.scope_id or "unknown").lower())
    base = f"case-{store}-{scope}-{day}"
    candidates = [base, f"{base}-{draft.case_type.replace('_', '-')}"]
    candidates += [f"{candidates[1]}-{n}" for n in range(2, len(taken) + 3)]
    found = next(c for c in candidates if c not in taken)
    taken.add(found)
    return found


@dataclass(frozen=True)
class CaseBuild:
    cases: tuple[Case, ...]
    abstentions: tuple[str, ...]
    counts: dict[str, int]


def build_cases(
    observations: Iterable[Observation],
    documents: Iterable[SourceDocument],
    links: Iterable[EntityLink],
    relations: Iterable[EvidenceRelation],
    spec: RunSpec,
    *,
    owners: Mapping[str, str],
    validity: timedelta,
    zones: Mapping[str, str],
) -> CaseBuild:
    """Pure: the cases of this snapshot. Records not visible at ``as_of`` are ignored."""
    as_of = spec.as_of
    all_facts = {
        _key(ref(o)): o
        for o in observations
        if _visible(o, as_of) and (o.store_id is None or o.store_id in spec.stores)
    }
    docs = {d.id: d for d in documents if _visible(d, as_of)}
    visible_rel = sorted(
        (
            r
            for r in relations
            if _visible(r, as_of) and _key(r.from_ref) in all_facts and _key(r.to_ref) in all_facts
        ),
        key=lambda r: r.id,
    )
    link_map = _links(links, spec)
    groups, inactive = _groups(all_facts, visible_rel, link_map)
    case_groups = [g for g in groups if g.first.kind not in NO_CASE_KINDS]
    drafts, unattached = _cluster(case_groups, validity)

    cases, abstentions, taken = [], [], set()
    totals = defaultdict(int)
    for draft in drafts:
        supporting = [o for g in draft.groups for o in g.members]
        contradicting = [o for g in draft.negated for o in g.members]
        members = {_key(ref(o)) for o in (*supporting, *contradicting)}
        touching = [
            r for r in visible_rel if _key(r.from_ref) in members or _key(r.to_ref) in members
        ]
        if (problem := draft.groups[0].link_problem) in ("missing", "conflicting"):
            abstentions.append(f"{draft.groups[0].first.id}: {problem} entity link")
        own_links = list(
            dict.fromkeys(
                lk for o in (*supporting, *contradicting) for lk in link_map.get(_key(ref(o)), [])
            )
        )

        origins: list[list[SourceDocument]] = []
        seen_docs: set[str] = set()
        for group in draft.groups:
            group_docs = [
                docs[i]
                for i in dict.fromkeys(o.document_id for o in group.members)
                if i in docs and i not in seen_docs
            ]
            seen_docs.update(d.id for d in group_docs)
            if group_docs:
                origins.append(group_docs)
        if len(seen_docs) < len({o.document_id for o in supporting}):
            abstentions.append(f"{draft.groups[0].first.id}: supporting document not visible")
        received = [d.available_at for ds in origins for d in ds] or [
            o.available_at for o in supporting
        ]
        independent = [min(d.available_at for d in ds) for ds in origins] or [
            g.available_at for g in draft.groups
        ]
        unknown_origins = sum(not any(d.origin for d in ds) for ds in origins)

        starts = [o.period_start for o in supporting if o.period_start is not None]
        ends = [o.period_end for o in supporting if o.period_end is not None]
        first_available, last_received = min(received), max(received)
        window_start = min(starts) if starts else first_available
        window_end = max(ends) if len(ends) == len(supporting) else last_received
        last_independent = max(independent)
        valid_until = last_independent + validity if draft.case_type in DECAYING else None

        kinds = {o.kind for o in supporting}
        priority, reason = _priority(draft, kinds, {o.reason for o in supporting})
        unresolved = draft.scope_level == "unknown" or draft.store_id is None
        status = "verify" if unresolved or draft.case_type == "unknown" else "open"
        inputs: list[SourceRecord] = [
            *supporting,
            *contradicting,
            *own_links,
            *touching,
            *(d for ds in origins for d in ds),
        ]
        cases.append(
            Case(
                id=_case_id(draft, zones, taken),
                version="v1",
                available_at=max(r.available_at for r in inputs),  # type: ignore[type-var]
                availability_basis="max_input_available_at",
                source_refs=tuple(dict.fromkeys(s for r in inputs for s in r.source_refs)),
                run_id=spec.run_id,
                scenario_id=spec.scenario_id,
                computed_at=as_of,
                input_refs=tuple(dict.fromkeys(ref(r) for r in inputs)),
                producer=MANIFEST.id,
                producer_version=MANIFEST.version,
                case_type=draft.case_type,
                store_id=draft.store_id,
                scope_level=draft.scope_level,
                scope_id=draft.scope_id if draft.scope_level != "unknown" else None,
                window_start=window_start,
                window_end=max(window_end, window_start),
                status=status,
                owner=owners[draft.case_type],
                priority=priority,
                priority_reason=reason,
                decision_due_at=None,
                first_available_at=first_available,
                last_received_at=last_received,
                last_independent_evidence_at=last_independent,
                valid_until=valid_until,
                supporting=tuple(ref(o) for o in supporting),
                contradicting=tuple(ref(o) for o in contradicting),
                n_documents=len(seen_docs),
                n_origin_groups=len(origins) - unknown_origins,
                n_unknown_origins=unknown_origins,
                blocking_uncertainties=tuple(
                    _uncertainties(draft, supporting, visible_rel, members)
                ),
                context_refs=tuple(ref(r) for r in (*own_links, *touching)),
            )
        )
        totals["documents"] += len(seen_docs)
        totals["origin_groups"] += len(origins) - unknown_origins
        totals["unknown_origins"] += unknown_origins

    counts = {
        "observations": len(all_facts),
        "cases": len(cases),
        "cases_verify": sum(c.status == "verify" for c in cases),
        "scope_unknown": sum(c.scope_level == "unknown" for c in cases),
        "no_case_kind": sum(len(g.members) for g in groups if g.first.kind in NO_CASE_KINDS),
        "inactive_facts": len(inactive),
        "negated_unattached": unattached,
        **totals,
    }
    for name in ("documents", "origin_groups", "unknown_origins"):
        counts.setdefault(name, 0)
    return CaseBuild(tuple(cases), tuple(abstentions), counts)


def _zones(run_repo: repo.Repo) -> dict[str, str]:
    return {str(r.data["store_id"]): str(r.data["timezone"]) for r in run_repo.erp("stores")}


def run(ctx: Context) -> ModuleResult:
    owners, days = load_domain(get_settings().config_dir)
    days = ctx.params.get("max_validity_days") or days
    built = build_cases(
        ctx.repo.list(Observation),
        ctx.repo.list(SourceDocument),
        ctx.repo.list(EntityLink),
        ctx.repo.list(EvidenceRelation),
        ctx.spec,
        owners=owners,
        validity=timedelta(days=days),
        zones=_zones(ctx.repo),
    )
    existing = {(c.id, c.version) for c in ctx.repo.list(Case)}
    new = [c for c in built.cases if (c.id, c.version) not in existing]
    written = ctx.repo.put(*new) if new else 0
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if built.abstentions else "succeeded",
        counts={**built.counts, "cases_new": written},
        errors=(),
        abstentions=built.abstentions,
    )
