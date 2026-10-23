"""AG-02 module: ``ag.analyst`` proposes one alternative scenario for a demand case (RFC §4.8.3).

The model reads the case through two tools and picks an enumerated template; code computes the
numbers with FC-03's own gates and parameters (``fc.overlay``: ``gate``, ``episodes``,
``build_overlay``, ``config/domain.yaml`` policy). It never sets a quantity, a coefficient or a
validity window itself.

Templates:

- ``no_uplift``: scenarios equal the baseline (the evidence is one-off or already in it).
- ``single_episode``: one supporting observation, chosen by the model, is the episode. It must be
  a supporting fact of the case, not a certain copy of another, and pass FC-03's ``gate``. This is
  the alternative to FC-03 abstaining on several possible episodes or concurrent cases: one is
  picked, they are never summed. Style scope, a ``not_estimable`` baseline, cold start, expiry and
  the cap behave exactly as in FC-03.

An alternative is built on the ``fc.baseline`` record, never on the deterministic overlay, so it
can't be added on top of it. It is a separate ``ForecastAdjustment`` with
``proposal_source="agent"``, ``producer="ag.analyst"`` and a version derived from the choice, so a
different choice is a new version. ``act.options`` and the reports skip agent proposals: without
an explicit selection the deterministic rule stands.

``finish(action_proposed, option_id=<proposal id>)`` publishes the proposal; ``verify`` /
``monitor`` publish nothing but the trace. The budget, allowlist and fallback (``verify``) are
AG-01's. Published rationales are templates; model prose never reaches a record.
"""

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal, Self
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tessera.core.cache import ReplayMiss
from tessera.core.config import get_settings
from tessera.core.contracts import (
    ArtifactRef,
    Case,
    EvidenceRelation,
    ForecastAdjustment,
    ModuleManifest,
    ModuleResult,
    Observation,
)
from tessera.core.repo import Repo
from tessera.modules.agents.chat_model import model_for_run
from tessera.modules.agents.runtime import (
    AgentLoop,
    AgentRun,
    Budget,
    ChatModel,
    Finish,
    Tool,
    ToolError,
    ToolResult,
    TraceMeta,
)
from tessera.modules.intelligence import baseline as fc_baseline
from tessera.modules.intelligence import overlay as fc_overlay
from tessera.modules.sources import erp

PROMPT_VERSION = "analyst.v1"
PROMPT_PATH = Path(__file__).resolve().parents[3] / "prompts" / f"{PROMPT_VERSION}.md"
TEMPLATES = ("no_uplift", "single_episode")
Template = Literal["no_uplift", "single_episode"]

MANIFEST = ModuleManifest(
    id="ag.analyst",
    version="1",
    layer="agents",
    description=(
        "Propose one alternative scenario per demand case from an enumerated template; "
        "FC-03 gates compute it, never added to the forecast"
    ),
    requires=("fc.baseline", "fc.overlay", "int.cases"),
    optional_inputs=(),
    produces=("AgentTrace", "ForecastAdjustment"),
    enabled=True,
    mode="live",
    params_schema={
        "type": "object",
        "properties": {
            "case_ids": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "minItems": 1,
                "maxItems": 20,
                "uniqueItems": True,
            },
        },
        "required": ["case_ids"],
        "additionalProperties": False,
    },
)

RATIONALE = {
    "action_proposed": (
        "Alternative scenario computed by code with the FC-03 gates and policy; it does not "
        "replace or add to the deterministic overlay until a human selects it."
    ),
    "verify": "No alternative proposed; the deterministic overlay stands, the case needs checks.",
    "monitor": "No alternative proposed; the deterministic overlay stands.",
}


class CaseArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str = Field(min_length=1)


class ProposeArgs(CaseArgs):
    template: Template
    observation_id: str | None = None

    @model_validator(mode="after")
    def episode_iff_single(self) -> Self:
        if (self.template == "single_episode") != (self.observation_id is not None):
            raise ValueError("observation_id is required for single_episode, forbidden otherwise")
        return self


@dataclass(frozen=True)
class CaseInputs:
    """Everything the analyst reads for one case, already filtered to the run's ``as_of``."""

    case: Case
    store: fc_overlay.Store
    observations: Mapping[str, Observation]
    duplicates: Mapping[str, str]
    baselines: Mapping[str, ForecastAdjustment]  # by SKU
    overlays: Mapping[str, ForecastAdjustment]  # deterministic, by SKU
    policy: fc_overlay.Policy


def _ref(record) -> ArtifactRef:
    return fc_overlay.ref(record)


def _totals(fc: ForecastAdjustment) -> dict[str, float | None]:
    if fc.status == "not_estimable":
        return {"baseline": None, "low": None, "base": None, "high": None}
    return {
        "baseline": round(sum(p.baseline or 0.0 for p in fc.series), 3),
        **{
            s: round(sum(getattr(p.latent, s) for p in fc.series if p.latent), 3)
            for s in fc_overlay.SCENARIOS
        },
    }


def propose(
    inputs: CaseInputs, template: Template, observation_id: str | None, spec
) -> tuple[ForecastAdjustment, ...]:
    """The alternative for every SKU of the case. Pure: the gates are FC-03's, not the model's."""
    case, store = inputs.case, inputs.store
    found: list[fc_overlay.Episode] = []
    reasons: list[str] = []
    if template == "single_episode":
        supporting = {r.id for r in case.supporting if r.kind == "Observation"}
        obs = inputs.observations.get(observation_id or "")
        if obs is None or observation_id not in supporting:
            raise ToolError(f"{observation_id} is not a supporting observation of {case.id}")
        if inputs.duplicates.get(obs.id) in supporting:
            raise ToolError(f"{obs.id} is a copy of {inputs.duplicates[obs.id]}; cite the original")
        verdict = fc_overlay.gate(obs, store)
        if isinstance(verdict, str):
            raise ToolError(f"{obs.id} fails the FC-03 gate: {verdict}")
        found = [verdict]
    else:
        reasons = ["analyst template no_uplift"]

    choice = {"template": template, "observation_id": observation_id}
    version = "a" + hashlib.sha256(json.dumps(choice, sort_keys=True).encode()).hexdigest()[:10]
    records = []
    for sku, base in sorted(inputs.baselines.items()):
        built = fc_overlay.build_overlay(spec, case, base, store, inputs.policy, found, reasons)
        update: dict = {
            "id": f"analyst-{case.id}-{sku.lower()}-{base.horizon_start:%Y%m%d}",
            "version": version,
            "available_at": spec.as_of,
            "availability_basis": "agent proposal at the run's as_of",
            "producer": MANIFEST.id,
            "producer_version": MANIFEST.version,
            "proposal_source": "agent",
        }
        if template == "no_uplift" and built.status == "unchanged":
            update["reason"] = (
                "analyst_no_uplift: the evidence is treated as one-off or already in the baseline"
            )
        if (det := inputs.overlays.get(sku)) is not None:
            update["input_refs"] = (*built.input_refs, _ref(det))
        records.append(built.model_copy(update=update))
    if not records:
        raise ToolError(f"{case.id} has no fc.baseline to build on")
    return tuple(ForecastAdjustment.model_validate(r.model_dump()) for r in records)


class Analyst:
    """Tools, finish validation and buffered proposals for one case."""

    def __init__(self, inputs: CaseInputs, spec) -> None:
        self.inputs = inputs
        self.spec = spec
        self.proposals: dict[str, tuple[ForecastAdjustment, ...]] = {}

    @property
    def case(self) -> Case:
        return self.inputs.case

    def _check(self, case_id: str) -> None:
        if case_id != self.case.id:
            raise ToolError(f"only case {self.case.id} is in scope")

    def evidence(self, args: CaseArgs) -> ToolResult:
        self._check(args.case_id)
        i = self.inputs
        supporting = {r.id for r in self.case.supporting}
        facts, refs = [], []
        for r in self.case.supporting:
            obs = i.observations.get(r.id)
            if obs is None:
                facts.append({"id": r.id, "kind": r.kind, "admissible": False,
                              "reason": "not_an_observation"})  # fmt: skip
                continue
            refs.append(_ref(obs))
            fact = {
                "id": obs.id,
                "kind": obs.kind,
                "direction": obs.direction,
                "negated": obs.negated,
                "quantity": obs.quantity.model_dump(mode="json"),
                "period_start": obs.period_start,
                "period_end": obs.period_end,
                "quotes": [e.quote for e in obs.evidence],
            }
            if i.duplicates.get(obs.id) in supporting:
                fact |= {"admissible": False, "reason": f"copy_of:{i.duplicates[obs.id]}"}
            else:
                verdict = fc_overlay.gate(obs, i.store)
                fact |= (
                    {"admissible": False, "reason": verdict}
                    if isinstance(verdict, str)
                    else {"admissible": True, "units": verdict.n, "open_days": verdict.g}
                )
            facts.append(fact)
        overlays = []
        for sku, base in sorted(i.baselines.items()):
            det = i.overlays.get(sku)
            refs.append(_ref(base))
            if det is not None:
                refs.append(_ref(det))
            overlays.append({
                "sku": sku,
                "baseline_id": base.id,
                "baseline_total": _totals(base)["baseline"],
                "overlay_id": None if det is None else det.id,
                "overlay_status": None if det is None else det.status,
                "overlay_reason": None if det is None else det.reason,
                "overlay_totals": None if det is None else _totals(det),
            })  # fmt: skip
        data = {
            "case": {
                "id": self.case.id,
                "type": self.case.case_type,
                "store_id": self.case.store_id,
                "scope": f"{self.case.scope_level}:{self.case.scope_id}",
                "valid_until": self.case.valid_until,
                "blocking_uncertainties": list(self.case.blocking_uncertainties),
            },
            "supporting": facts,
            "forecast": overlays,
            "templates": list(TEMPLATES),
        }
        return ToolResult(data, input_refs=(_ref(self.case),), output_refs=tuple(refs))

    def propose(self, args: ProposeArgs) -> ToolResult:
        self._check(args.case_id)
        records = propose(self.inputs, args.template, args.observation_id, self.spec)
        pid = f"alt:{self.case.id}:{args.template}:{args.observation_id or '-'}"
        self.proposals[pid] = records
        data = {
            "proposal_id": pid,
            "per_sku": [
                {"sku": r.sku, "status": r.status, "reason": r.reason, "totals": _totals(r),
                 "deterministic_overlay": (det := self.inputs.overlays.get(r.sku))
                 and _totals(det)}
                for r in records
            ],
        }  # fmt: skip
        return ToolResult(
            data,
            input_refs=(_ref(self.case),),
            output_refs=tuple(_ref(r) for r in records),
        )

    def validate(self, choice: Finish) -> str | None:
        if choice.status != "action_proposed":
            return None
        if choice.option_id not in self.proposals:
            return f"option_id must be a proposal_id from propose_scenario: {choice.option_id}"
        supporting = {r.id for r in self.case.supporting}
        if not supporting.intersection(choice.evidence_refs):
            return "cite at least one supporting observation id in evidence_refs"
        return None

    def tools(self) -> list[Tool]:
        return [
            Tool(
                "get_case_evidence",
                "The case, its supporting facts with the FC-03 gate verdict of each, the baseline "
                "and the deterministic overlay per SKU. Call this first.",
                CaseArgs,
                self.evidence,
            ),
            Tool(
                "propose_scenario",
                "Compute an alternative with code: template no_uplift, or single_episode with one "
                "admissible supporting observation_id. Returns a proposal_id and its totals.",
                ProposeArgs,
                self.propose,
            ),
        ]


def analyse(
    repo: Repo, inputs: CaseInputs, *, model: ChatModel, budget: Budget | None = None
) -> tuple[AgentRun, tuple[ForecastAdjustment, ...]]:
    """Run the analyst on one case; persist the trace and, if proposed, the chosen alternative."""
    session = Analyst(inputs, repo.spec)
    case = inputs.case
    result = AgentLoop(model, session.tools(), budget=budget, validate_finish=session.validate).run(
        [
            {"role": "system", "content": PROMPT_PATH.read_text(encoding="utf-8")},
            {"role": "user", "content": json.dumps({
                "case_id": case.id, "as_of": repo.spec.as_of.isoformat(),
                "store_id": case.store_id,
            })},
        ],  # fmt: skip
        TraceMeta(
            run_id=repo.spec.run_id,
            scenario_id=repo.spec.scenario_id,
            case_id=case.id,
            as_of=repo.spec.as_of,
            mode=repo.spec.mode,
            input_refs=(_ref(case),),
            trace_id=f"trace:{case.id}:{uuid4().hex}",
            producer=MANIFEST.id,
            producer_version=MANIFEST.version,
        ),
    )
    rationale = RATIONALE[result.finish.status]
    choice = result.finish.model_copy(update={"rationale": rationale})
    steps = tuple(
        s.model_copy(update={"arguments": {**s.arguments, "rationale": rationale}})
        if s.tool in {"finish", "fallback"}
        else s
        for s in result.trace.steps
    )
    trace = result.trace.model_copy(update={"steps": steps})
    chosen: tuple[ForecastAdjustment, ...] = ()
    if choice.status == "action_proposed" and choice.option_id is not None:
        chosen = session.proposals[choice.option_id]
        stored = repo.list(ForecastAdjustment, store_id=case.store_id)
        existing = {(f.id, f.version) for f in stored}
        new = [r for r in chosen if (r.id, r.version) not in existing]
        if new:
            repo.put(*new)
    repo.put(trace)
    return replace(result, trace=trace, finish=choice), chosen


def load_inputs(repo: Repo, case_id: str) -> CaseInputs:
    """One visible demand case of this run with what FC-03 used to quantify it."""
    case = repo.get(Case, case_id)
    if (
        case is None
        or case.run_id != repo.spec.run_id
        or case.store_id not in repo.spec.stores
        or case.case_type not in fc_overlay.DEMAND_CASE_TYPES
    ):
        raise ToolError(f"{case_id} is not a visible demand case of this run")
    (row,) = [r for r in erp.read(repo, "stores") if r.data["store_id"] == case.store_id]
    store = fc_overlay.Store(
        case.store_id,
        ZoneInfo(str(row.data["timezone"])),
        fc_baseline.closed_weekdays(row.data.get("closed_dow")),
    )
    carried = {
        str(r.data["sku"])
        for r in erp.read(repo, "assortment")
        if r.data["store_id"] == store.store_id
    }
    sku_of_size = {
        str(r.data["sku_size"]): str(r.data["sku"]) for r in erp.read(repo, "sku_size_ean")
    }
    skus = fc_overlay.case_skus(case, sku_of_size, carried)
    forecasts = repo.list(ForecastAdjustment, store_id=case.store_id)
    baselines = {
        f.sku: f for f in forecasts if f.producer == fc_baseline.MANIFEST.id and f.sku in skus
    }
    overlays = {
        f.sku: f
        for f in forecasts
        if f.producer == fc_overlay.MANIFEST.id and case.id in f.case_ids and f.sku in skus
    }
    return CaseInputs(
        case=case,
        store=store,
        observations={o.id: o for o in repo.list(Observation)},
        duplicates=fc_overlay.copies(repo.list(EvidenceRelation)),
        baselines=baselines,
        overlays=overlays,
        policy=fc_overlay.load_policy(get_settings().config_dir),
    )


def run(ctx) -> ModuleResult:
    ids: Sequence[str] = ctx.params.get("case_ids", ())
    if not ids or "llm" not in ctx.clients:
        return ModuleResult(
            module_id=MANIFEST.id,
            module_version=MANIFEST.version,
            status="blocked",
            counts={},
            errors=("Select case_ids and configure the LLM client",),
            abstentions=(),
        )
    traces, proposed, errors = [], 0, []
    for case_id in ids:
        try:
            inputs = load_inputs(ctx.repo, case_id)
            model = model_for_run(
                ctx.clients["llm"],
                prompt_version=PROMPT_VERSION,
                cache_context={"case": inputs.case.model_dump(mode="json")},
            )
            result, chosen = analyse(ctx.repo, inputs, model=model)
        except ToolError as error:
            errors.append(f"{case_id}: {error}")
            continue
        except ReplayMiss:
            return ModuleResult(
                module_id=MANIFEST.id,
                module_version=MANIFEST.version,
                status="failed",
                counts={},
                errors=(f"{case_id}: missing LLM recording",),
                abstentions=(),
            )
        traces.append(result.trace)
        proposed += bool(chosen)
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if errors or any(t.fallback_used for t in traces) else "succeeded",
        counts={
            "cases": len(ids),
            "traces": len(traces),
            "proposals": proposed,
            "fallbacks": sum(t.fallback_used for t in traces),
        },
        errors=tuple(errors),
        abstentions=(),
    )
