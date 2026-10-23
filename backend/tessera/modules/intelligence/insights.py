"""INS-01 module: ``ins.product`` sets each product's sales and POS returns beside the reasons
stores report for it ("same sales, different reasons", RFC §3.3, demo case D4).

One ``ProductInsight`` per product, over one perimeter and one period shared by every count:

- **Perimeter:** the run's stores. **Period:** up to ``days`` local business days ending on the
  last day whose sales every store has published at ``as_of`` (daily facts are known at 06:00
  local the next day), never older than the ``src.erp`` history window of any store.
- **Sales and returns** (ERP daily sales): units sold and returned in the period; the return rate
  is returned / sold over the same stores and days, and is undefined (``None``) with no sale.
  Returns of the period may refer to sales made before it; the note says so.
- **Return reasons** (POS ``RETURN`` lines): reason codes of the period's return lines, as shares
  of those lines. When the line count differs from the units returned, a note says so instead
  of mixing the two.
- **Reported reasons** (``Observation``s linked to the product): counted once per origin
  (certain copies, superseded and retracted facts are dropped, as in ``int.cases``), not
  negated, reported in the period. Kinds and reasons are shares of those observations, never of
  sales: there is no conversion rate without a denominator of shoppers.

A product is a SKU-colour (a size-level link counts for its colour) or a style when the link is
style-level, whose sales are summed over its colours. Products with a counted observation are
always kept; products with only POS returns need ``min_return_lines`` of them. No LLM.
"""

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from tessera.core import repo
from tessera.core.contracts import (
    ArtifactRef,
    EntityLink,
    EvidenceRelation,
    ModuleManifest,
    ModuleResult,
    Observation,
    ProductInsight,
    RunSpec,
    Share,
    SourceRef,
)
from tessera.modules.sources import erp

DEFAULT_DAYS = 28
DEFAULT_MIN_RETURN_LINES = 5
UNSPECIFIED = "unspecified"

MANIFEST = ModuleManifest(
    id="ins.product",
    version="1",
    layer="intelligence",
    description=(
        "Per product: units sold and returned, POS return reasons and the reasons stores "
        "report, over the same stores and business days"
    ),
    requires=("src.erp", "int.dedup"),
    optional_inputs=(),
    produces=("ProductInsight",),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {
            "days": {"type": "integer", "minimum": 1, "maximum": 800},
            "min_return_lines": {"type": "integer", "minimum": 1},
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


Product = tuple[str, str]  # (level, product id)


@dataclass(frozen=True)
class Period:
    first: date
    last: date

    def __contains__(self, day: date) -> bool:
        return self.first <= day <= self.last


def period(as_of: datetime, zones: Mapping[str, str], days: int, history: int) -> Period:
    """The ``days`` local days ending on the last day all stores have published at ``as_of``.

    The first day is never older than the ``src.erp`` window of any store (``history`` days
    before its local ``as_of`` date), so no store's rows are missing from the start.
    """
    local = [as_of.astimezone(ZoneInfo(zone)) for zone in zones.values()]
    last = min(t.date() - timedelta(1 if t.hour >= 6 else 2) for t in local)
    oldest = max(t.date() for t in local) - timedelta(days=history)
    return Period(max(last - timedelta(days=days - 1), oldest), last)


def product_of(link: EntityLink) -> Product | None:
    if link.status != "linked" or link.target_id is None:
        return None
    if link.level == "style":
        return ("style", link.target_id)
    if link.level in ("sku", "sku_size"):
        return ("sku", "-".join(link.target_id.split("-")[:2]))
    return None


def _matches(product: Product, sku: str) -> bool:
    level, code = product
    return sku == code if level == "sku" else sku.split("-")[0] == code


def counted(
    observations: Iterable[Observation], relations: Iterable[EvidenceRelation]
) -> list[Observation]:
    """One observation per origin: no certain copy, nothing superseded or retracted, no negation."""
    dropped = set()
    for r in relations:
        if r.relation == "duplicates":
            dropped.add(r.from_ref.id)
        elif r.relation in ("supersedes", "retracts"):
            dropped.add(r.to_ref.id)
            if r.relation == "retracts":
                dropped.add(r.from_ref.id)
    return [o for o in observations if o.id not in dropped and not o.negated]


def _shares(counts: Counter[str], total: int) -> tuple[Share, ...]:
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return tuple(Share(key=k, count=n, of=total) for k, n in ranked)


def _ref(o: Observation) -> ArtifactRef:
    return ArtifactRef(kind="Observation", id=o.id, version=o.version)


@dataclass(frozen=True)
class Inputs:
    """What the module reads, already limited to the run's stores and ``as_of``."""

    sales: Sequence[repo.ErpRecord]
    returns: Sequence[repo.ErpRecord]
    observations: Sequence[Observation]  # already counted (see ``counted``)
    links: Mapping[str, EntityLink]  # by observation id
    zones: Mapping[str, str]  # store → time zone


def build(
    inputs: Inputs,
    spec: RunSpec,
    *,
    days: int,
    min_return_lines: int,
    history: int = erp.DEFAULT_HISTORY_DAYS,
) -> list[ProductInsight]:
    zones = {s: inputs.zones[s] for s in sorted(spec.stores)}
    window = period(spec.as_of, zones, days, history)

    def local_day(instant: datetime, store: str) -> date:
        return instant.astimezone(ZoneInfo(zones[store])).date()

    sales = [r for r in inputs.sales if r.data["store_id"] in zones]
    sales = [r for r in sales if r.data["business_date"] in window]
    returns = [r for r in inputs.returns if r.data["store_id"] in zones]
    returns = [r for r in returns if r.data["business_date"] in window]
    reported: dict[Product, list[Observation]] = defaultdict(list)
    for o in inputs.observations:
        if o.store_id not in zones or o.available_at is None:
            continue
        if local_day(o.period_start or o.available_at, o.store_id) not in window:
            continue
        link = inputs.links.get(o.id)
        if link is not None and (product := product_of(link)) is not None:
            reported[product].append(o)
    lines_by_sku = Counter(str(r.data["sku"]) for r in returns)
    busy = {("sku", sku) for sku, n in lines_by_sku.items() if n >= min_return_lines}
    products = set(reported) | busy

    insights = []
    for product in sorted(products):
        own_sales = [r for r in sales if _matches(product, str(r.data["sku"]))]
        own_returns = [r for r in returns if _matches(product, str(r.data["sku"]))]
        observations = sorted(reported.get(product, ()), key=lambda o: (o.available_at, o.id))
        insights.append(_insight(product, own_sales, own_returns, observations, window, spec))
    return insights


def _insight(
    product: Product,
    sales: Sequence[repo.ErpRecord],
    returns: Sequence[repo.ErpRecord],
    observations: Sequence[Observation],
    window: Period,
    spec: RunSpec,
) -> ProductInsight:
    sold = sum(int(r.data["units_sold"]) for r in sales)  # type: ignore[arg-type]
    returned = sum(int(r.data["units_returned"]) for r in sales)  # type: ignore[arg-type]
    reasons = Counter(str(r.data.get("return_reason") or UNSPECIFIED) for r in returns)
    notes = []
    if returned:
        notes.append("returns of the period may refer to sales made before it")
    if len(returns) != returned:
        notes.append(
            f"POS return lines ({len(returns)}) and ERP units returned ({returned}) differ; "
            "reason shares are of POS lines only"
        )
    if not sold:
        notes.append("no unit sold in the period: return rate not defined")
    n = len(observations)
    refs = tuple(_ref(o) for o in observations)
    erp_rows = [*sales, *returns]
    available = [r.available_at for r in erp_rows] + [o.available_at for o in observations]
    known = [a for a in available if a is not None]
    level, code = product
    body = {
        "units_sold": sold,
        "units_returned": returned,
        "return_reasons": sorted(reasons.items()),
        "observations": [f"{r.id}@{r.version}" for r in refs],
        "erp": sorted(f"{r.id}@{r.version}" for r in erp_rows),
    }
    digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    return ProductInsight(
        id=f"insight-{level}-{code.lower()}-{spec.as_of:%Y%m%dT%H%M}",
        version=f"sha256:{digest[:16]}",
        available_at=max(known) if known else spec.as_of,
        availability_basis="max_input_available_at" if known else "run_as_of",
        source_refs=_sources(erp_rows, observations),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=spec.as_of,
        input_refs=refs,
        producer=MANIFEST.id,
        producer_version=MANIFEST.version,
        as_of=spec.as_of,
        level=level,  # type: ignore[arg-type]
        product_id=code,
        stores=tuple(sorted(spec.stores)),
        period_first=window.first,
        period_last=window.last,
        units_sold=sold,
        units_returned=returned,
        return_rate=returned / sold if sold else None,
        return_lines=len(returns),
        return_reasons=_shares(reasons, len(returns)),
        n_observations=n,
        n_documents=len({o.document_id for o in observations}),
        reported_kinds=_shares(Counter(o.kind for o in observations), n),
        reported_reasons=_shares(Counter(o.reason or UNSPECIFIED for o in observations), n),
        observation_refs=refs,
        notes=tuple(notes),
    )


def _sources(
    erp_rows: Iterable[repo.ErpRecord], observations: Iterable[Observation]
) -> tuple[SourceRef, ...]:
    """ERP files (not one locator per row) and the observations' own sources."""
    files = {(s.uri, s.content_hash) for r in erp_rows for s in r.source_refs}
    refs = [SourceRef(uri=u, content_hash=h) for u, h in sorted(files)]
    refs += [s for o in observations for s in o.source_refs]
    return tuple(dict.fromkeys(refs))


def read_inputs(run_repo: repo.Repo) -> Inputs:
    links = {link.observation_id: link for link in run_repo.list(EntityLink)}
    observations = counted(run_repo.list(Observation), run_repo.list(EvidenceRelation))
    return Inputs(
        sales=erp.read(run_repo, "sales"),
        returns=erp.read(run_repo, "returns"),
        observations=observations,
        links=links,
        zones={str(r.data["store_id"]): str(r.data["timezone"]) for r in run_repo.erp("stores")},
    )


def run(ctx: Context) -> ModuleResult:
    insights = build(
        read_inputs(ctx.repo),
        ctx.spec,
        days=ctx.params.get("days", DEFAULT_DAYS),
        min_return_lines=ctx.params.get("min_return_lines", DEFAULT_MIN_RETURN_LINES),
        history=erp.run_params(ctx.spec).get("history_days", erp.DEFAULT_HISTORY_DAYS),
    )
    written = ctx.repo.put(*insights) if insights else 0
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="succeeded",
        counts={
            "products": len(insights),
            "products_new": written,
            "with_reported_reasons": sum(1 for i in insights if i.n_observations),
            "return_lines": sum(i.return_lines for i in insights),
        },
        errors=(),
        abstentions=tuple(
            f"{i.product_id}: return rate not defined (no unit sold)"
            for i in insights
            if i.return_rate is None and i.units_returned
        ),
    )
