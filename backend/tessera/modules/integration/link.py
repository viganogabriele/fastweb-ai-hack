"""INT-01 module: ``int.link`` links each observation's product mention to the catalog.

For every ``Observation`` of the run it builds ranked catalog candidates with the INT-01 pure
linker (catalog names from the ERP master rows known at ``as_of``, aliases from
``config/aliases.yaml``, the store's assortment preferred) and writes one ``EntityLink``:

- no product mention → ``not_product``;
- the pure linker decides ``linked`` or ``unlinked`` → kept as is (``rule:link_mention``);
- ``ambiguous`` only because several colours of one style fit ("nero e blu") → linked at style
  level (``rule:same_style``): the style is certain, the colour is not;
- otherwise ``ambiguous`` → one constrained LLM choice among the candidates without blocking
  flags (prompt ``link_choice.v1``). An id outside that set, no id, or any LLM failure keeps the
  link ``ambiguous`` with its candidates: the module never guesses and never drops a mention.

Candidate scores keep the linker's 0–100 similarity scale; they are not probabilities.
"""

import hashlib
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import yaml
from pydantic import BaseModel, ConfigDict, Field

from tessera.core import repo
from tessera.core.config import REPO_ROOT, get_settings
from tessera.core.contracts import (
    ArtifactRef,
    EntityLink,
    LinkCandidate,
    ModuleManifest,
    ModuleResult,
    Observation,
    RunSpec,
    SourceRef,
)
from tessera.modules.integration.candidates import (
    BLOCKING_FLAGS,
    Candidate,
    Catalog,
    LinkParams,
    LinkResult,
    link_mention,
)

PROMPT_ID = "link_choice.v1"
PROMPT_PATH = REPO_ROOT / "backend" / "prompts" / f"{PROMPT_ID}.md"
SCORE_MIN, SCORE_MAX = 0.0, 100.0
# "taglia 4", "tg. 3", "size M", "taille 2": an explicit size word, never a bare letter.
SIZE_IN_MENTION = re.compile(
    r"(?<!\w)(?:taglia|tg\.?|size|taille|talla|gr(?:ö|oe)sse)\s*(\d{1,2}|xxs|xs|s|m|l|xl|xxl)(?!\w)",
    re.IGNORECASE,
)

MANIFEST = ModuleManifest(
    id="int.link",
    version="1",
    layer="integration",
    description=(
        "Product mentions of the run's observations linked to catalog style, SKU or SKU-size, "
        "ambiguous or unlinked with their candidates; one constrained LLM choice on ties"
    ),
    requires=("src.erp",),
    optional_inputs=("ing.extract",),
    produces=("EntityLink",),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {
            "llm": {"type": "boolean"},
            "candidate_min": {"type": "number", "minimum": 0, "maximum": 100},
            "link_min": {"type": "number", "minimum": 0, "maximum": 100},
            "min_margin": {"type": "number", "minimum": 0, "maximum": 100},
            "top_k": {"type": "integer", "minimum": 1, "maximum": 20},
        },
        "additionalProperties": False,
    },
)


class Context(Protocol):
    """The part of PLT-04's ``RunContext`` this module uses."""

    @property
    def spec(self) -> RunSpec: ...
    @property
    def repo(self) -> repo.Repo: ...
    @property
    def params(self) -> Mapping[str, Any]: ...
    @property
    def clients(self) -> Mapping[str, Any]: ...


class LinkChoice(BaseModel):
    """What the LLM may answer: one of the offered ids, or null."""

    model_config = ConfigDict(extra="forbid")

    target_id: str | None
    rationale: str = Field(min_length=1, max_length=500)


@dataclass(frozen=True)
class Decision:
    status: str
    level: str | None
    target_id: str | None
    candidates: tuple[Candidate, ...]
    decided_by: str
    rationale: str


@dataclass(frozen=True)
class CatalogSnapshot:
    catalog: Catalog
    source_refs: Mapping[str, tuple[SourceRef, ...]]  # SKU → refs of its sku_colour row
    assortment: Mapping[str, frozenset[str]]  # store id → SKUs
    style_names: Mapping[str, str]
    colour_names: Mapping[str, tuple[str, ...]]


def load_aliases(path: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Style and colour alias maps from ``config/aliases.yaml``. A shared alias is given to
    every style it names, so it can only produce a tie, never a silent pick."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    styles: dict[str, list[str]] = {}
    for code, entries in (data.get("styles") or {}).items():
        styles.setdefault(str(code), []).extend(e["alias"] for e in entries)
    for entry in data.get("shared") or []:
        for code in entry["styles"]:
            styles.setdefault(str(code), []).append(entry["alias"])
    colours = {
        str(code): [e["alias"] for e in entries]
        for code, entries in (data.get("colours") or {}).items()
    }
    return styles, colours


def catalog_at(run_repo: repo.Repo, aliases_path: Path) -> CatalogSnapshot | None:
    """Catalog from the ERP master rows known at the run's ``as_of``; None if not loaded."""
    colour_rows = run_repo.erp("sku_colour")
    size_rows = run_repo.erp("sku_size_ean")
    if not colour_rows or not size_rows:
        return None
    as_text = [{k: "" if v is None else str(v) for k, v in r.data.items()} for r in colour_rows]
    sizes = [{k: "" if v is None else str(v) for k, v in r.data.items()} for r in size_rows]
    style_aliases, colour_aliases = load_aliases(aliases_path)
    catalog = Catalog.from_rows(as_text, sizes, style_aliases, colour_aliases)
    assortment: dict[str, set[str]] = {}
    for store in run_repo.spec.stores:
        assortment[store] = {str(r.data["sku"]) for r in run_repo.erp("assortment", store_id=store)}
    return CatalogSnapshot(
        catalog=catalog,
        source_refs={str(r.data["sku"]): r.source_refs for r in colour_rows},
        assortment={s: frozenset(skus) for s, skus in assortment.items()},
        style_names={code: style.name for code, style in catalog.styles.items()},
        colour_names=catalog.colour_names,
    )


def size_in(mention: str) -> str | None:
    match = SIZE_IN_MENTION.search(mention)
    return match.group(1).upper() if match else None


def decide(
    obs: Observation,
    snapshot: CatalogSnapshot,
    params: LinkParams,
    llm: Any | None,
    errors: list[str],
) -> Decision:
    """Deterministic decision first; the LLM only breaks a tie among clean candidates."""
    mention = (obs.product_mention or "").strip()
    if not mention:
        return Decision("not_product", None, None, (), "rule:no_mention", "No product mention.")
    store_skus = snapshot.assortment.get(obs.store_id) if obs.store_id else None
    result = link_mention(mention, snapshot.catalog, size_in(mention), store_skus, params)
    reasons = ", ".join(result.reasons) or "unique candidate above threshold"
    if result.status != "ambiguous":
        return Decision(
            result.status,
            result.level,
            result.target_id,
            result.candidates,
            "rule:link_mention",
            f"{result.status}: {reasons}",
        )
    style = _same_style(result, params)
    if style is not None:
        return Decision(
            "linked",
            "style",
            style,
            result.candidates,
            "rule:same_style",
            f"Every close candidate is a colour of style {style}; the colour is not certain.",
        )
    ambiguous = Decision(
        "ambiguous", None, None, result.candidates, "rule:link_mention", f"ambiguous: {reasons}"
    )
    allowed = [c for c in result.candidates if not set(c.flags) & BLOCKING_FLAGS]
    if llm is None or len(allowed) < 2:
        return ambiguous
    try:
        choice = _ask(llm, obs, mention, allowed, snapshot)
    except Exception as exc:  # LLM down, budget, replay miss, invalid output: stay ambiguous
        errors.append(f"{obs.id}: llm {type(exc).__name__}")
        return ambiguous
    picked = next((c for c in allowed if c.target_id == choice.target_id), None)
    if picked is None:
        why = "no choice" if choice.target_id is None else "choice outside the candidates"
        return Decision(
            "ambiguous",
            None,
            None,
            result.candidates,
            f"llm:{PROMPT_ID}",
            f"ambiguous: {reasons}; LLM {why}: {choice.rationale}",
        )
    return Decision(
        "linked",
        picked.level,
        picked.target_id,
        result.candidates,
        f"llm:{PROMPT_ID}",
        f"LLM choice among {len(allowed)} candidates: {choice.rationale}",
    )


def to_link(obs: Observation, decision: Decision, spec: RunSpec, snapshot: CatalogSnapshot):
    sku = _sku_of(decision.target_id, decision.level)
    catalog_refs = tuple(snapshot.source_refs.get(sku, ())) if sku else ()
    return EntityLink(
        id="link-" + obs.id.removeprefix("obs-"),
        version=_version(obs, decision),
        available_at=obs.available_at,
        availability_basis="observation_available_at",
        source_refs=tuple(dict.fromkeys((*obs.source_refs, *catalog_refs))),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=spec.as_of,
        input_refs=(ArtifactRef(kind="Observation", id=obs.id, version=obs.version),),
        producer=MANIFEST.id,
        producer_version=MANIFEST.version,
        observation_id=obs.id,
        status=decision.status,
        level=decision.level,
        target_id=decision.target_id,
        candidates=tuple(_candidate(c) for c in decision.candidates),
        decided_by=decision.decided_by,
        rationale=decision.rationale,
    )


def link_observations(
    run_repo: repo.Repo,
    observations: Iterable[Observation],
    snapshot: CatalogSnapshot,
    params: LinkParams,
    llm: Any | None,
) -> ModuleResult:
    errors: list[str] = []
    abstentions: list[str] = []
    links: list[EntityLink] = []
    counts = dict.fromkeys(("linked", "ambiguous", "unlinked", "not_product"), 0)
    llm_links = 0
    for obs in observations:
        if obs.available_at is None:
            abstentions.append(f"{obs.id}: unknown availability")
            continue
        decision = decide(obs, snapshot, params, llm, errors)
        counts[decision.status] += 1
        llm_links += decision.decided_by.startswith("llm:") and decision.status == "linked"
        if decision.status in ("ambiguous", "unlinked"):
            abstentions.append(f"{obs.id}: {decision.rationale}")
        links.append(to_link(obs, decision, run_repo.spec, snapshot))
    new = run_repo.put(*links) if links else 0
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if errors else "succeeded",
        counts={"observations": len(links), "links_new": new, "llm_linked": llm_links, **counts},
        errors=tuple(errors),
        abstentions=tuple(abstentions),
    )


def run(ctx: Context) -> ModuleResult:
    snapshot = catalog_at(ctx.repo, get_settings().config_dir / "aliases.yaml")
    if snapshot is None:
        return ModuleResult(
            module_id=MANIFEST.id,
            module_version=MANIFEST.version,
            status="blocked",
            counts={},
            errors=("ERP sku_colour / sku_size_ean not available at as_of",),
            abstentions=(),
        )
    p = ctx.params
    defaults = LinkParams()
    params = LinkParams(
        candidate_min=p.get("candidate_min", defaults.candidate_min),
        link_min=p.get("link_min", defaults.link_min),
        min_margin=p.get("min_margin", defaults.min_margin),
        top_k=p.get("top_k", defaults.top_k),
    )
    llm = ctx.clients.get("llm") if p.get("llm", True) else None
    return link_observations(ctx.repo, ctx.repo.list(Observation), snapshot, params, llm)


# Helpers.


def _same_style(result: LinkResult, params: LinkParams) -> str | None:
    """Style code if the tie is only between colours of one style, with no blocking flag."""
    top = result.candidates[0]
    close = [c for c in result.candidates if top.score - c.score < params.min_margin]
    if top.score < params.link_min or len(close) < 2:
        return None
    if any(c.level == "style" or set(c.flags) & BLOCKING_FLAGS for c in close):
        return None
    styles = {c.target_id.split("-")[0] for c in close}
    if len(styles) != 1 or set(result.reasons) - {"close_runner_up", "global_fallback"}:
        return None
    return styles.pop()


def _ask(
    llm: Any,
    obs: Observation,
    mention: str,
    allowed: Sequence[Candidate],
    snapshot: CatalogSnapshot,
) -> LinkChoice:
    offered = []
    for c in allowed:
        style, _, rest = c.target_id.partition("-")
        colour = rest.split("-")[0] if rest else None
        offered.append(
            {
                "target_id": c.target_id,
                "level": c.level,
                "style_name": snapshot.style_names.get(style, ""),
                "colour_names": list(snapshot.colour_names.get(colour, ())) if colour else [],
            }
        )
    payload = {"mention": mention, "quotes": [e.quote for e in obs.evidence], "candidates": offered}
    messages = [
        {"role": "system", "content": PROMPT_PATH.read_text(encoding="utf-8")},
        {"role": "user", "content": _json(payload)},
    ]
    return llm.extract(
        LinkChoice,
        messages,
        cache_context={
            "prompt_version": PROMPT_ID,
            "observation": f"{obs.id}@{obs.version}",
            "producer": f"{MANIFEST.id}@{MANIFEST.version}",
        },
        temperature=0,
    )


def _candidate(c: Candidate) -> LinkCandidate:
    method = "+".join((c.method, *c.flags))
    return LinkCandidate(
        target_id=c.target_id,
        level=c.level,
        method=method,
        score=c.score,
        score_min=SCORE_MIN,
        score_max=SCORE_MAX,
    )


def _sku_of(target_id: str | None, level: str | None) -> str | None:
    if target_id is None or level in (None, "style"):
        return None
    return "-".join(target_id.split("-")[:2])


def _version(obs: Observation, decision: Decision) -> str:
    h = hashlib.sha256(
        _json(
            [obs.id, obs.version, decision.status, decision.target_id, decision.decided_by]
        ).encode()
    )
    return h.hexdigest()[:16]


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
