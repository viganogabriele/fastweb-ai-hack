"""INT-01 module: ``int.link`` links each observation's product mention to the catalog.

For every ``Observation`` of the run it builds ranked catalog candidates with the INT-01 pure
linker (catalog names from the ERP master rows known at ``as_of``, without SKUs launched after
the observation's day, aliases from ``config/aliases.yaml``, the store's assortment preferred) and
writes one ``EntityLink``:

- no product mention → ``not_product``;
- the pure linker decides ``linked`` or ``unlinked`` → kept as is (``rule:link_mention``);
- ``ambiguous`` only because several colours of one style fit ("nero e blu") → linked at style
  level (``rule:same_style``): the style is certain, the colour is not;
- otherwise ``ambiguous`` → one constrained LLM choice (prompt ``link_choice.v1``) among the
  candidates within ``min_margin`` of the top one, only if none of them carries a blocking flag.
  The tool schema enumerates the offered ids. No id, an invalid answer or any LLM failure keeps
  the link ``ambiguous`` with its candidates: the module never guesses and never drops a mention.

A size is used only when the mention names exactly one, after an explicit size word. Ended SKUs
stay in the catalog (a customer may still name them): they can only add ambiguity. A link is
available once both its observation and the catalog rows it was decided on are.

Candidate scores use 0–100: fuzzy similarity by default, normalized RRF rank scores
when embeddings are enabled. Neither scale represents a probability.
"""

import hashlib
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal, Protocol

import yaml
from pydantic import BaseModel, ConfigDict, Field, create_model

from tessera.core import repo
from tessera.core.cache import CacheCorrupt, ReplayMiss
from tessera.core.config import REPO_ROOT, get_settings
from tessera.core.contracts import (
    ArtifactRef,
    EntityLink,
    LinkCandidate,
    ModuleManifest,
    ModuleResult,
    Observation,
    RunSpec,
)
from tessera.core.llm import BudgetExceeded, ExtractionFailed, LLMCallFailed
from tessera.modules.integration.candidates import (
    BLOCKING_FLAGS,
    Candidate,
    Catalog,
    LinkParams,
    LinkResult,
    link_mention,
)
from tessera.modules.integration.embeddings import EmbeddingRetriever, InvalidEmbedding

PROMPT_ID = "link_choice.v1"
PROMPT_PATH = REPO_ROOT / "backend" / "prompts" / f"{PROMPT_ID}.md"
SCORE_MIN, SCORE_MAX = 0.0, 100.0
# "taglia 4", "tg. 3", "size M", "Größe 2", "サイズ1": an explicit size word, never a bare letter.
SIZE_WORDS = r"taglia|tg\.?|size|taille|talla|gr(?:ö|oe)(?:ss|ß)e|サイズ|尺码|사이즈"
SIZE_TOKEN = r"\d{1,2}|xxs|xs|s|m|l|xl|xxl"
SIZE_IN_MENTION = re.compile(
    rf"(?<!\w)(?:{SIZE_WORDS})\s*({SIZE_TOKEN})(?![a-z0-9'’])"
    # "tg 3 o 4", "size S/M": a second size after a connector is a second size.
    rf"(?:\s*(?:,|/|-|&|e|o|y|ou|or|and|oder|und)\s*(?:(?:{SIZE_WORDS})\s*)?({SIZE_TOKEN})(?![a-z0-9'’]))?",
    re.IGNORECASE,
)
# Failures of the LLM call or of its output. Anything else is a bug and fails the module.
LLM_ERRORS = (ExtractionFailed, BudgetExceeded, LLMCallFailed, ReplayMiss, CacheCorrupt)

MANIFEST = ModuleManifest(
    id="int.link",
    version="2",
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
            "use_embeddings": {"type": "boolean"},
            "embedding_dimensions": {"enum": [512, 2048]},
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


def choice_schema(ids: Sequence[str]) -> type[LinkChoice]:
    """`LinkChoice` whose `target_id` is an enum of the offered ids (or null)."""
    return create_model(
        "LinkChoice",
        __base__=LinkChoice,
        target_id=(Literal[tuple(ids)] | None, ...),  # type: ignore[valid-type]
    )


@dataclass(frozen=True)
class Decision:
    status: str
    level: str | None
    target_id: str | None
    candidates: tuple[Candidate, ...]
    decided_by: str
    rationale: str


@dataclass
class CatalogSnapshot:
    """Catalog rows known at the run's `as_of`; `catalog_on(day)` drops SKUs not launched yet."""

    colour_rows: Sequence[repo.ErpRecord]
    size_rows: Sequence[Mapping[str, str]]
    style_aliases: Mapping[str, list[str]]
    colour_aliases: Mapping[str, list[str]]
    assortment: Mapping[str, frozenset[str]]  # store id → SKUs
    available_at: datetime  # latest catalog/assortment row: no link is known before it
    _by_day: dict[date, Catalog] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.rows_by_sku = {str(r.data["sku"]): r for r in self.colour_rows}

    def catalog_on(self, day: date) -> Catalog:
        if day not in self._by_day:
            launched = [
                {k: "" if v is None else str(v) for k, v in r.data.items()}
                for r in self.colour_rows
                if not isinstance(r.data.get("launch_date"), date) or r.data["launch_date"] <= day
            ]
            self._by_day[day] = Catalog.from_rows(
                launched, self.size_rows, self.style_aliases, self.colour_aliases
            )
        return self._by_day[day]


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
    sizes = [{k: "" if v is None else str(v) for k, v in r.data.items()} for r in size_rows]
    style_aliases, colour_aliases = load_aliases(aliases_path)
    assortment: dict[str, frozenset[str]] = {}
    rows = [*colour_rows, *size_rows]
    for store in run_repo.spec.stores:
        store_rows = run_repo.erp("assortment", store_id=store)
        rows += store_rows
        assortment[store] = frozenset(str(r.data["sku"]) for r in store_rows)
    return CatalogSnapshot(
        colour_rows=colour_rows,
        size_rows=sizes,
        style_aliases=style_aliases,
        colour_aliases=colour_aliases,
        assortment=assortment,
        available_at=max(r.available_at for r in rows),
    )


def size_in(mention: str) -> str | None:
    """The one size named after a size word; None if there is none or more than one."""
    sizes = {s.upper() for pair in SIZE_IN_MENTION.findall(mention) for s in pair if s}
    return sizes.pop() if len(sizes) == 1 else None


def decide(
    obs: Observation,
    snapshot: CatalogSnapshot,
    params: LinkParams,
    llm: Any | None,
    errors: list[str],
    retriever: EmbeddingRetriever | None = None,
) -> Decision:
    """Deterministic decision first; the LLM only breaks a tie among clean candidates."""
    mention = (obs.product_mention or "").strip()
    if not mention:
        return Decision("not_product", None, None, (), "rule:no_mention", "No product mention.")
    store_skus = snapshot.assortment.get(obs.store_id) if obs.store_id else None
    catalog = snapshot.catalog_on(obs.available_at.date())
    result = link_mention(mention, catalog, size_in(mention), store_skus, params)
    if retriever is not None:
        descriptions = {
            sku: " ".join(
                str(row.data.get(field) or "")
                for field in (
                    "style_name",
                    "color_name_it",
                    "color_name_en",
                    "category",
                    "subcategory",
                    "gender",
                )
            )
            for sku, row in snapshot.rows_by_sku.items()
        }
        try:
            result = retriever.retrieve(
                mention,
                catalog,
                params=params,
                size=size_in(mention),
                store_skus=store_skus,
                descriptions=descriptions,
            )
        except (*LLM_ERRORS, InvalidEmbedding) as exc:
            errors.append(f"{obs.id}: embeddings {type(exc).__name__}; fuzzy candidates retained")
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
    allowed = offered(result, params)
    if llm is None or len(allowed) < 2:
        return ambiguous
    try:
        choice = _ask(llm, obs, mention, allowed, catalog)
    except LLM_ERRORS as exc:  # LLM down, budget, replay miss, invalid output: stay ambiguous
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


def offered(result: LinkResult, params: LinkParams) -> list[Candidate]:
    """Candidates the LLM may choose from: within `min_margin` of the top one, and only if none
    of those carries a blocking flag (a flagged top candidate is never bypassed)."""
    if not result.candidates:
        return []
    top = result.candidates[0]
    close = [c for c in result.candidates if top.score - c.score < params.min_margin]
    if any(set(c.flags) & BLOCKING_FLAGS for c in close):
        return []
    return close


def to_link(obs: Observation, decision: Decision, spec: RunSpec, snapshot: CatalogSnapshot):
    sku = _sku_of(decision.target_id, decision.level)
    row = snapshot.rows_by_sku.get(sku) if sku else None
    inputs = [ArtifactRef(kind="Observation", id=obs.id, version=obs.version)]
    if row is not None:
        inputs.append(ArtifactRef(kind="erp.sku_colour", id=row.id, version=row.version))
    return EntityLink(
        id="link-" + obs.id.removeprefix("obs-"),
        version=_version(obs, decision),
        available_at=max(obs.available_at, snapshot.available_at),
        availability_basis="max(observation, catalog)",
        source_refs=tuple(dict.fromkeys((*obs.source_refs, *(row.source_refs if row else ())))),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=spec.as_of,
        input_refs=tuple(inputs),
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
    retriever: EmbeddingRetriever | None = None,
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
        decision = decide(obs, snapshot, params, llm, errors, retriever)
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
    retriever = None
    if p.get("use_embeddings", False):
        client = ctx.clients.get("llm")
        if client is None:
            return ModuleResult(
                module_id=MANIFEST.id,
                module_version=MANIFEST.version,
                status="blocked",
                counts={},
                errors=("Embedding client unavailable",),
                abstentions=(),
            )
        retriever = EmbeddingRetriever(client, p.get("embedding_dimensions", 512))
    return link_observations(
        ctx.repo,
        ctx.repo.list(Observation),
        snapshot,
        params,
        llm,
        retriever,
    )


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
    catalog: Catalog,
) -> LinkChoice:
    choices = []
    for c in allowed:
        style, _, rest = c.target_id.partition("-")
        colour = rest.split("-")[0] if rest else None
        choices.append(
            {
                "target_id": c.target_id,
                "level": c.level,
                "style_name": catalog.styles[style].name if style in catalog.styles else "",
                "colour_names": list(catalog.colour_names.get(colour, ())) if colour else [],
            }
        )
    payload = {"mention": mention, "quotes": [e.quote for e in obs.evidence], "candidates": choices}
    messages = [
        {"role": "system", "content": PROMPT_PATH.read_text(encoding="utf-8")},
        {"role": "user", "content": _json(payload)},
    ]
    return llm.extract(
        choice_schema([c.target_id for c in allowed]),
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
    candidates = [(c.target_id, c.level, c.score, c.flags) for c in decision.candidates]
    fields = [obs.id, obs.version, decision.status, decision.level, decision.target_id]
    fields += [decision.decided_by, decision.rationale, candidates]
    h = hashlib.sha256(_json(fields).encode())
    return h.hexdigest()[:16]


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)
