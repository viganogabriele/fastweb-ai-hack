"""OUT-01 module: ``out.reports`` writes the brief of the run, one ``Report`` per view.

The brief is rendered from the same facts the queue shows: the run's ``Case`` records with their
supporting ``Observation``s, ``EntityLink``s, ``EvidenceRelation``s, ``ForecastAdjustment``s and
``ActionOption``s, all read at ``as_of``. No LLM: every sentence comes from a fixed template, and
every number is rendered from a structured citation ``(ref, field, unit, scope, period)`` of the
record that holds it (RFC §4.8.1). Optional LLM prose is not part of this module.

- ``by_office`` (default): one section per owner (``config/domain.yaml`` ``owners``, already on
  the case), so each office reads its own brief. ``by_priority``: one section per priority.
- Inside a section, cases go high priority first, then by id. Each case lists its counted
  observations (a certain copy is counted once, via its original), the product candidates of an
  ambiguous link, the document/origin counts when copies exist, the D+1..D+7 baseline of each
  SKU-colour in scope, the recommended option and the case's own open questions.
- A forecast is the case's own adjustment when one names the case, else the store × SKU baseline
  of every colour in scope (the colours the store carries, for a style case).
- A thin "Product feedback" section closes every view when ``ins.product`` ran: up to
  ``PRODUCTS_SHOWN`` products, those with reported observations first. Each shows the kinds and
  reasons reported, as shares of counted observations; units sold and returned over the same
  stores and days; and POS return reasons, as shares of return lines. A rate is shown only where
  its denominator exists.
- Labels come from the ERP master data (``styles``, ``sku_colour``); a code missing from it is
  shown as is.

The report is available at the latest cited record, ``as_of`` is the run's, ``input_refs`` are
the cited records and ``input_version_hash`` is the SHA-256 of their sorted ``kind:id@version``.
A run with no case writes a brief that says so. Rerunning over the same inputs writes nothing;
over changed inputs (e.g. options added later) it writes the next version of the same report id.
"""

import hashlib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from tessera.core import repo
from tessera.core.contracts import (
    ActionOption,
    ArtifactRef,
    Case,
    Citation,
    EntityLink,
    EvidenceRelation,
    ForecastAdjustment,
    ModuleManifest,
    ModuleResult,
    Observation,
    ProductInsight,
    Report,
    RunSpec,
    Share,
)
from tessera.core.contracts.common import SourceRecord
from tessera.modules.actions.options import case_forecast, case_products
from tessera.modules.sources import erp

VIEWS = ("by_office", "by_priority")
PRIORITIES = ("critical", "high", "medium", "low")
TEMPLATE = "template:out.reports.v1"
PRODUCTS_SHOWN = 5

MANIFEST = ModuleManifest(
    id="out.reports",
    version="2",
    layer="outputs",
    description=(
        "Brief per owner (and per priority) from the run's cases, evidence, baselines and "
        "options; every number rendered from a structured citation by a template"
    ),
    requires=("int.cases",),
    optional_inputs=("fc.baseline", "fc.overlay", "act.options", "ins.product"),
    produces=("Report",),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {
            "views": {
                "type": "array",
                "items": {"enum": list(VIEWS)},
                "minItems": 1,
                "uniqueItems": True,
            }
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


@dataclass(frozen=True)
class Facts:
    """What the brief may say, already read at the run's ``as_of``."""

    cases: Sequence[Case]
    observations: Mapping[str, Observation]
    links: Mapping[str, EntityLink]  # by observation id
    copies: frozenset[str]  # observation ids that certainly duplicate another one
    forecasts: Mapping[str, Sequence[ForecastAdjustment]]  # by case id
    options: Mapping[str, Sequence[ActionOption]]  # by case id
    styles: Mapping[str, str] = field(default_factory=dict)  # style code → name
    colours: Mapping[str, str] = field(default_factory=dict)  # SKU → colour name
    zones: Mapping[str, str] = field(default_factory=dict)  # store → time zone
    insights: Sequence[ProductInsight] = ()


def ref(record: SourceRecord) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


def input_version_hash(refs: Iterable[ArtifactRef]) -> str:
    keys = sorted(f"{r.kind}:{r.id}@{r.version}" for r in refs)
    return "sha256:" + hashlib.sha256("\n".join(keys).encode()).hexdigest()


def _local_midnight(day: date, zone: str) -> datetime:
    return datetime.combine(day, time(), ZoneInfo(zone))


def _product_name(code: str, facts: "Facts") -> str:
    parts = code.split("-")
    name = facts.styles.get(parts[0], parts[0])
    if len(parts) >= 2:
        name += " " + facts.colours.get("-".join(parts[:2]), parts[1])
    if len(parts) >= 3:
        name += f" size {'-'.join(parts[2:])}"
    return name


def _shares(shares: Sequence[Share]) -> str:
    total = shares[0].of
    parts = ", ".join(f"{s.key.replace('_', ' ')} {s.count}" for s in shares)
    return f"{parts} of {total}"


def _label(case: Case, facts: Facts) -> str:
    if case.scope_level == "unknown" or case.scope_id is None:
        return f"{case.store_id or 'store unknown'} · product not identified"
    code = case.scope_id
    if case.scope_level in ("category", "store"):
        return f"{case.store_id} · {code}"
    return f"{case.store_id} · {_product_name(code, facts)} ({code})"


class _Brief:
    def __init__(self, facts: Facts) -> None:
        self.facts = facts
        self.citations: list[Citation] = []
        self.cited: dict[tuple[str, str, str], SourceRecord] = {}

    def cite(self, record: SourceRecord, field: str | None = None, unit=None, **kw) -> str:
        self.citations.append(Citation(ref=ref(record), field=field, unit=unit, **kw))
        self.cited.setdefault((type(record).__name__, record.id, record.version), record)
        return f"[{len(self.citations)}]"

    def case(self, case: Case) -> list[str]:
        facts = self.facts
        head = (
            f"- **{_label(case, facts)}**: {case.status}, priority {case.priority} "
            f"{self.cite(case)}."
        )
        body: list[str] = []
        for obs_ref in case.supporting:
            obs = facts.observations.get(obs_ref.id)
            if obs is None or obs.id in facts.copies:
                continue
            body += self.observation(obs)
        if case.n_documents > case.n_origin_groups + case.n_unknown_origins:
            scope = {"store_id": str(case.store_id)}
            body.append(
                f"{case.n_documents} documents {self.cite(case, 'n_documents', scope=scope)} "
                f"from {case.n_origin_groups} origin "
                + self.cite(case, "n_origin_groups", scope=scope)
            )
        for fc in facts.forecasts.get(case.id, ()):
            if line := self.forecast(fc):
                body.append(line)
        for option in facts.options.get(case.id, ()):
            if option.recommended:
                body.append(
                    f"recommended option: {option.kind.replace('_', ' ')} "
                    + self.cite(option, "recommended")
                )
        body += [f"open: {u}" for u in case.blocking_uncertainties]
        return [head, *(f"  - {b}" for b in body)]

    def observation(self, obs: Observation) -> list[str]:
        q = obs.quantity
        what = obs.kind.replace("_", " ")
        kw = {
            "scope": {"store_id": str(obs.store_id)},
            "period_start": obs.period_start,
            "period_end": obs.period_end,
        }
        if q.kind == "exact" and q.value is not None:
            cite = self.cite(obs, "quantity.value", q.unit, **kw)
            lines = [f"{what} {q.value:g} {q.unit} {cite}"]
        else:
            lines = [f"{what}, quantity {q.kind} " + self.cite(obs, "quantity.kind", **kw)]
        link = self.facts.links.get(obs.id)
        if link is not None and link.status == "ambiguous" and link.candidates:
            names = " or ".join(c.target_id for c in link.candidates)
            lines.append(f"product is {names} {self.cite(link, 'candidates')}")
        return lines

    def product(self, insight: ProductInsight) -> list[str]:
        scope = {"product_id": insight.product_id, "stores": ",".join(insight.stores)}

        def cite(field: str | None = None, unit=None) -> str:
            return self.cite(insight, field, unit, scope=scope)

        name = _product_name(insight.product_id, self.facts)
        days = f"{insight.period_first:%m-%d}..{insight.period_last:%m-%d}"
        head = f"- **{name} ({insight.product_id})**, {', '.join(insight.stores)}, {days} {cite()}"
        body = []
        if insight.n_observations:
            kinds = _shares(insight.reported_kinds)
            line = f"reported: {kinds} observations {cite('reported_kinds')}"
            if any(r.key != "unspecified" for r in insight.reported_reasons):
                reasons = _shares(insight.reported_reasons)
                line += f", reasons: {reasons} {cite('reported_reasons')}"
            body.append(line)
        sales = (
            f"sold {insight.units_sold} units {cite('units_sold', 'units')}, "
            f"returned {insight.units_returned} units {cite('units_returned', 'units')}"
        )
        if insight.return_rate is not None:
            rate = insight.return_rate * 100
            sales += f", return rate {rate:.1f}% {cite('return_rate', 'percent')}"
        body.append(sales)
        if insight.return_lines:
            reasons = _shares(insight.return_reasons)
            body.append(f"POS return reasons: {reasons} lines {cite('return_reasons')}")
        return [head, *(f"  - {b}" for b in body)]

    def forecast(self, fc: ForecastAdjustment) -> str | None:
        points = [p.baseline for p in fc.series]
        if fc.status == "not_estimable" or not points or any(p is None for p in points):
            return f"baseline {fc.sku} not estimable {self.cite(fc, 'status')}"
        zone = self.facts.zones.get(fc.store_id, "UTC")
        end = _local_midnight(fc.horizon_end + timedelta(days=1), zone) - timedelta(seconds=1)
        total = sum(p for p in points if p is not None)
        return (
            f"baseline {fc.sku} {fc.horizon_start:%m-%d}..{fc.horizon_end:%m-%d} "
            f"{total:.1f} units, {fc.status} "
            + self.cite(
                fc,
                "series.baseline",
                "units",
                scope={"store_id": fc.store_id, "sku": fc.sku},
                period_start=_local_midnight(fc.horizon_start, zone),
                period_end=end,
            )
        )


def _sections(view: str, cases: Sequence[Case]) -> list[tuple[str, list[Case]]]:
    key = (lambda c: c.owner) if view == "by_office" else (lambda c: c.priority)
    names = sorted({key(c) for c in cases})
    if view == "by_priority":
        names = [p for p in PRIORITIES if p in names]
    order = sorted(cases, key=lambda c: (PRIORITIES.index(c.priority), c.id))
    return [(name, [c for c in order if key(c) == name]) for name in names]


def _products(insights: Sequence[ProductInsight]) -> list[ProductInsight]:
    """Reported reasons first (most observations), then the most POS return lines."""
    ranked = sorted(insights, key=lambda i: (-i.n_observations, -i.return_lines, i.id))
    return ranked[:PRODUCTS_SHOWN]


def build_report(view: str, facts: Facts, spec: RunSpec) -> Report:
    """One view of the brief at ``spec.as_of``; numbers only from cited fields."""
    if view not in VIEWS:
        raise ValueError(f"unknown report view: {view}")
    as_of = spec.as_of
    title = view.removeprefix("by_")
    brief = _Brief(facts)
    lines = [f"# Brief by {title}, as of {as_of:%Y-%m-%d %H:%M} UTC", ""]
    sections = _sections(view, facts.cases)
    if not sections:
        lines += ["No open case at this time.", ""]
    for name, cases in sections:
        lines += [f"## {name}", ""]
        for case in cases:
            lines += brief.case(case)
        lines.append("")
    if products := _products(facts.insights):
        lines += ["## Product feedback", ""]
        for insight in products:
            lines += brief.product(insight)
        lines.append("")
    cited = list(brief.cited.values())
    available = [r.available_at for r in cited if r.available_at is not None]
    input_refs = tuple(ref(r) for r in cited)
    return Report(
        id=f"report-{view.replace('_', '-')}-{as_of:%Y%m%dT%H%M}",
        version="v1",
        available_at=max(available) if available else as_of,
        availability_basis="max_input_available_at" if available else "run_as_of",
        source_refs=tuple(dict.fromkeys(s for r in cited for s in r.source_refs)),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=as_of,
        input_refs=input_refs,
        producer=MANIFEST.id,
        producer_version=MANIFEST.version,
        as_of=as_of,
        view=view,
        markdown="\n".join(lines).rstrip() + "\n",
        citations=tuple(brief.citations),
        generated_by=TEMPLATE,
        input_version_hash=input_version_hash(input_refs),
    )


def _forecasts(run_repo: repo.Repo, case: Case) -> list[ForecastAdjustment]:
    found = run_repo.list(ForecastAdjustment, store_id=case.store_id)
    own = [f for f in found if case.id in f.case_ids]
    if own or case.store_id is None or case.scope_level not in ("sku_size", "sku", "style"):
        return own
    found = []
    for sku, _size in case_products(run_repo, case):
        if sku is not None and (fc := case_forecast(run_repo, case.store_id, sku, case.id)):
            found.append(fc)
    return found


def read_facts(run_repo: repo.Repo) -> Facts:
    cases = run_repo.list(Case)
    observations = {o.id: o for o in run_repo.list(Observation)}
    links = {link.observation_id: link for link in run_repo.list(EntityLink)}
    relations = run_repo.list(EvidenceRelation)
    master = {}
    names = (("styles", "style_code", "style_name"), ("sku_colour", "sku", "color_name_en"))
    for table, key, value in names:
        master[table] = {
            str(r.data[key]): str(r.data[value])
            for r in erp.read(run_repo, table)  # type: ignore[arg-type]
            if r.data.get(value)
        }
    return Facts(
        cases=cases,
        observations=observations,
        links=links,
        copies=frozenset(r.from_ref.id for r in relations if r.relation == "duplicates"),
        forecasts={c.id: _forecasts(run_repo, c) for c in cases},
        options={c.id: run_repo.list(ActionOption, case_id=c.id) for c in cases},
        styles=master["styles"],
        colours=master["sku_colour"],
        zones={str(r.data["store_id"]): str(r.data["timezone"]) for r in run_repo.erp("stores")},
        insights=run_repo.list(ProductInsight),
    )


def run(ctx: Context) -> ModuleResult:
    facts = read_facts(ctx.repo)
    views = tuple(ctx.params.get("views") or VIEWS)
    reports = [build_report(view, facts, ctx.spec) for view in views]
    stored = ctx.repo.list(Report)
    new = []
    for report in reports:
        same_id = [r for r in stored if r.id == report.id]
        if same_id and same_id[-1].input_version_hash == report.input_version_hash:
            continue
        # A regeneration over changed inputs is a new version, never an overwrite.
        new.append(report.model_copy(update={"version": f"v{len(same_id) + 1}"}))
    written = ctx.repo.put(*new) if new else 0
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="succeeded",
        counts={
            "reports": len(reports),
            "reports_new": written,
            "cases": len(facts.cases),
            "citations": sum(len(r.citations) for r in reports),
        },
        errors=(),
        abstentions=(),
    )
