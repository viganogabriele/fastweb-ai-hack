"""Scoped RFC 4.8.2 tools and the ag.investigator module. No approval or dispatch."""

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from uuid import uuid4

import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import to_jsonable_python

from tessera.core.cache import ReplayMiss
from tessera.core.config import get_settings
from tessera.core.contracts import (
    ActionOption,
    ArtifactRef,
    Case,
    Check,
    Clarification,
    ModuleManifest,
    ModuleResult,
    Observation,
    Reservation,
    StockFact,
)
from tessera.core.contracts.common import DerivedRecord, Instant
from tessera.core.repo import KINDS, Repo, latest
from tessera.modules.actions.options import (
    CLOSED_CASES,
    Context,
    OptionsPolicy,
    Reader,
    case_products,
    evaluate_case,
    gather,
    load_policy,
)
from tessera.modules.agents.chat_model import model_for_run
from tessera.modules.agents.runtime import (
    AgentLoop,
    AgentRun,
    Budget,
    ChatModel,
    FallbackContext,
    Finish,
    Tool,
    ToolError,
    ToolResult,
    TraceMeta,
)
from tessera.modules.sources.systems_client import (
    DC_TIMEZONES,
    SystemsReader,
    Unknown,
    default_client,
)

PROMPT_VERSION = "investigator.v2"
PROMPT_PATH = Path(__file__).resolve().parents[3] / "prompts" / f"{PROMPT_VERSION}.md"
# The chat default (Gemma) spends the tool budget on one-location stock reads; GLM completes
# both recorded dev paths. Hosted outside the EU (docs/smoke-fastweb.md): inputs are synthetic.
MODEL = "glm-5.3-flash"
MOVEMENTS = frozenset({"transfer", "replenish_dc", "combo"})
EVIDENCE_KINDS = frozenset(
    {"Observation", "EntityLink", "EvidenceRelation", "MetricFact", "ContextEvent"}
)

MANIFEST = ModuleManifest(
    id="ag.investigator",
    version="1",
    layer="agents",
    description="Investigate selected cases with scoped tools; propose or verify, never approve",
    requires=("int.cases", "act.options"),
    optional_inputs=("sys.client",),
    produces=("AgentTrace", "Clarification", "ActionOption"),
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


class Arguments(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CaseArgs(Arguments):
    case_id: str = Field(min_length=1)


class StockArgs(Arguments):
    sku: str = Field(min_length=1)
    size: str = Field(min_length=1)
    locations: tuple[str, ...] = Field(min_length=1, max_length=20)


class LaneArgs(Arguments):
    origin: str = Field(min_length=1)
    dest: str = Field(min_length=1)
    requested_at: Instant
    required_by: Instant | None = None


class OptionsArgs(CaseArgs):
    candidate_donors: tuple[str, ...] | None = Field(default=None, max_length=20)


class ClarificationArgs(CaseArgs):
    observation_ids: tuple[str, ...] = Field(min_length=1, max_length=20)
    question: str = Field(min_length=1, max_length=1000)


def ref(record) -> ArtifactRef:
    return ArtifactRef(kind=type(record).__name__, id=record.id, version=record.version)


def _json(value):
    return to_jsonable_python(value, fallback=lambda item: str(item))


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(_json(value), sort_keys=True).encode()).hexdigest()


def visible_case(repo: Repo, case_id: str) -> Case:
    case = repo.get(Case, case_id)
    if (
        case is None
        or case.run_id != repo.spec.run_id
        or case.scenario_id != repo.spec.scenario_id
        or case.store_id not in repo.spec.stores
        or case.status in CLOSED_CASES
    ):
        raise ToolError("Case is unavailable or not actionable in this run")
    return case


class Investigator:
    def __init__(
        self,
        repo: Repo,
        case_id: str,
        reader: Reader,
        policy: OptionsPolicy,
        horizon=7,
        *,
        reservations: tuple[Reservation, ...] | None = None,
    ):
        self.repo, self.reader, self.policy, self.horizon = repo, reader, policy, horizon
        self.reservations = reservations
        self.case = visible_case(repo, case_id)
        self.options: dict[str, ActionOption] = {}
        self.proposals: dict[tuple[str, str], ActionOption] = {}
        self.facts: dict[tuple[str, str], StockFact] = {}
        self.drafts: dict[str, Clarification] = {}
        self.evidence_read = False

    def _case(self, case_id: str):
        if case_id != self.case.id:
            raise ToolError("Tool case_id must match the selected case")

    def _related(self):
        refs = dict.fromkeys(
            (
                *self.case.input_refs,
                *self.case.supporting,
                *self.case.contradicting,
                *self.case.context_refs,
            )
        )
        records = []
        for item in refs:
            if item.kind not in EVIDENCE_KINDS:
                continue
            record = self.repo.get(KINDS[item.kind], item.id, item.version)
            if record is not None and (
                not isinstance(record, DerivedRecord)
                or (record.run_id, record.scenario_id)
                == (self.repo.spec.run_id, self.repo.spec.scenario_id)
            ):
                records.append(record)
        return records

    def _products(self):
        return {sku for sku, _ in case_products(self.repo, self.case) if sku is not None}

    def _locations(self, locations):
        if not set(locations) <= (set(self.repo.spec.stores) | set(DC_TIMEZONES)):
            raise ToolError("Location is outside this run and supported distribution centres")

    def _donor_conflicts(self):
        return [
            c
            for c in latest(self.repo.list(Case))
            if (
                c.store_id in self.repo.spec.stores
                and c.store_id != self.case.store_id
                and c.status not in CLOSED_CASES
                and c.case_type == "stock_discrepancy"
                and (
                    c.scope_level in {"unknown", "store"}
                    or (
                        c.scope_id
                        and self.case.scope_id
                        and c.scope_id.split("-")[0] == self.case.scope_id.split("-")[0]
                    )
                )
            )
        ]

    def evidence(self, args: CaseArgs) -> ToolResult:
        self._case(args.case_id)
        records = self._related()
        # A donor's discrepancy matters even when its case has a different episode window.
        donors = self._donor_conflicts()
        self.evidence_read = True
        refs = tuple(dict.fromkeys(ref(r) for r in (self.case, *records, *donors)))
        return ToolResult(
            {
                "case": self.case.model_dump(mode="json"),
                "records": [r.model_dump(mode="json") for r in records],
                "donor_conflicts": [c.model_dump(mode="json") for c in donors],
                "products": sorted(self._products()),
                "locations": list(self.repo.spec.stores),
                "language": self.language(),
            },
            input_refs=refs,
            output_refs=refs,
        )

    def stock(self, args: StockArgs) -> ToolResult:
        if args.sku not in self._products():
            raise ToolError("SKU is unresolved or outside the selected case")
        scoped_sizes = {
            size
            for sku, size in case_products(self.repo, self.case)
            if sku == args.sku and size is not None
        }
        if scoped_sizes and args.size not in scoped_sizes:
            raise ToolError("Size is outside the selected case")
        self._locations(args.locations)
        sizes = {str(r.data["size"]) for r in self.repo.erp("sku_size_ean", sku=args.sku)}
        sizes.update(f.size for f in self.repo.list(StockFact, sku=args.sku))
        if args.size not in sizes:
            raise ToolError("Size is not identified for this SKU in the run")
        data = self.reader.stock(args.sku, args.size, args.locations)
        # Physical ERP snapshots are not stored artifacts: cite their actual source rows.
        refs = [ref(self.case)]
        for location, facts in data.items():
            if isinstance(facts, Unknown):
                continue
            self.facts.update({(f.id, f.version): f for f in facts})
            refs.extend(ref(f) for f in facts)
            if location in self.repo.spec.stores:
                refs.extend(
                    ArtifactRef(kind="erp.stock", id=r.id, version=r.version)
                    for r in self.repo.erp("stock", store_id=location, sku=args.sku)
                    if str(r.data["size"]) == args.size
                )
        refs = tuple(dict.fromkeys(refs))
        return ToolResult(_json(data), input_refs=refs, output_refs=refs)

    def lane(self, args: LaneArgs) -> ToolResult:
        self._locations((args.origin, args.dest))
        if args.dest != self.case.store_id or args.origin == args.dest:
            raise ToolError("Lane must lead from a donor to this case's store")
        if args.requested_at < self.repo.spec.as_of:
            raise ToolError("Pickup cannot precede the replay clock")
        result = self.reader.lane_and_eta(
            args.origin, args.dest, args.requested_at, args.required_by
        )
        return ToolResult(_json(asdict(result)), input_refs=(ref(self.case),))

    def evaluate(self, args: OptionsArgs) -> ToolResult:
        self._case(args.case_id)
        if args.candidate_donors is not None:
            donors = set(args.candidate_donors)
            if not donors <= (set(self.repo.spec.stores) - {self.case.store_id}):
                raise ToolError("Candidate donors must be other stores in this run")
        colours = []
        for product in case_products(self.repo, self.case):
            inputs = gather(
                self.repo,
                self.reader,
                self.case,
                self.policy,
                self.horizon,
                product=product,
                reservations=self.reservations,
            )
            if args.candidate_donors is not None:
                inputs = replace(
                    inputs,
                    routes=tuple(
                        route
                        for route in inputs.routes
                        if route.donor.store_id in args.candidate_donors
                    ),
                )
            colours.append(inputs)
            for position in (inputs.dest, *(route.donor for route in inputs.routes)):
                for fact in position.stock.values():
                    if isinstance(fact, StockFact):
                        self.facts[(fact.id, fact.version)] = fact
        options = []
        for option in evaluate_case(colours):
            conflicts = [
                c
                for c in self._donor_conflicts()
                if any(leg.origin == c.store_id for leg in option.legs)
            ]
            if conflicts:
                checks = tuple(
                    Check(
                        name="donor_conflict",
                        status="unknown",
                        mandatory=True,
                        detail="Unresolved donor stock discrepancy requires verification",
                        source_refs=(ref(c),),
                    )
                    for c in conflicts
                )
                digest = _digest(
                    [option.input_version_hash, [c.model_dump(mode="json") for c in conflicts]]
                )
                option = ActionOption.model_validate(
                    {
                        **option.model_dump(),
                        "checks": (*option.checks, *checks),
                        "recommended": False,
                        "version": digest,
                        "input_version_hash": f"sha256:{digest}",
                        "input_refs": (*option.input_refs, *(ref(c) for c in conflicts)),
                        "available_at": max(
                            option.available_at, *(c.available_at for c in conflicts)
                        ),
                        "rationale": "Verify donor stock before proposing a movement.",
                    }
                )
            options.append(option)
        self.options = {o.id: o for o in options}
        self.proposals.update({(o.id, o.version): o for o in options})
        refs = tuple(dict.fromkeys((ref(self.case), *(r for o in options for r in o.input_refs))))
        return ToolResult(
            [o.model_dump(mode="json") for o in options],
            input_refs=refs,
            output_refs=tuple(ref(o) for o in options),
        )

    def language(self) -> str:
        store = next(
            (r for r in self.repo.erp("stores") if r.data.get("store_id") == self.case.store_id),
            None,
        )
        return str(store.data.get("language", "en")) if store else "en"

    def clarify(self, args: ClarificationArgs) -> ToolResult:
        self._case(args.case_id)
        observations = {r.id: r for r in self._related() if isinstance(r, Observation)}
        if not set(args.observation_ids) <= observations.keys():
            raise ToolError("Clarification observations must belong to this case")
        refs = tuple(
            sorted((ref(observations[i]) for i in set(args.observation_ids)), key=lambda r: r.id)
        )
        question = " ".join(args.question.split())
        identity = _digest([self.repo.spec.run_id, _json(ref(self.case)), _json(refs), question])
        draft = Clarification(
            id=f"clarification:{identity}",
            version="1",
            available_at=self.repo.spec.as_of,
            availability_basis="run_as_of",
            source_refs=(),
            run_id=self.repo.spec.run_id,
            scenario_id=self.repo.spec.scenario_id,
            computed_at=self.repo.spec.as_of,
            input_refs=(ref(self.case), *refs),
            producer=MANIFEST.id,
            producer_version=MANIFEST.version,
            case_id=self.case.id,
            observation_refs=refs,
            question=question,
            asked_at=self.repo.spec.as_of,
            status="draft",
        )
        self.drafts[draft.id] = draft
        return ToolResult(
            draft.model_dump(mode="json"), input_refs=draft.input_refs, output_refs=(ref(draft),)
        )

    def validate(self, choice: Finish) -> str | None:
        if not self.evidence_read:
            return "Inspect this case's evidence before finishing"
        if choice.status == "monitor" and (
            self.case.scope_level == "unknown" or self.case.blocking_uncertainties
        ):
            return "Unresolved identity or blocking uncertainty requires verification"
        if choice.option_id is None:
            return None
        option = self.options.get(choice.option_id)
        if option is None or option.case_id != self.case.id:
            return "Select an option freshly evaluated for this case"
        if option.id not in choice.evidence_refs:
            return "Cite the evaluated option in evidence_refs"
        if option.valid_until <= self.repo.spec.as_of:
            return "Option is expired"
        if option.kind in MOVEMENTS and (
            self.case.scope_level not in {"sku_size", "sku", "style"}
            or not option.recommended
            or not option.checks
            or any(
                c.mandatory and c.status not in {"pass", "not_applicable"} for c in option.checks
            )
        ):
            return "Movement is ambiguous, blocked or not recommended by the deterministic engine"
        if option.kind in {"verify_stock", "ask_store"}:
            return "Missing information requires status=verify without an option_id"
        return None

    def fallback(self, ctx: FallbackContext) -> Finish:
        # No network/tool calls after the budget. Inspect only already available inputs.
        self.evidence_read = True
        self._related()
        if self.case.scope_level == "unknown" or self.case.blocking_uncertainties:
            return Finish(status="verify", rationale="Evidence requires verification")
        available = list(self.options.values()) or [
            o for o in self.repo.list(ActionOption) if o.case_id == self.case.id
        ]
        for option in available:
            if option.kind in MOVEMENTS and option.recommended:
                # Fallback never proposes a movement the model did not freshly evaluate.
                if (
                    option.id in self.options
                    and self.validate(
                        Finish(
                            status="action_proposed",
                            option_id=option.id,
                            evidence_refs=(option.id,),
                            rationale="Validated proposal",
                        )
                    )
                    is None
                ):
                    return Finish(
                        status="action_proposed",
                        option_id=option.id,
                        evidence_refs=(option.id,),
                        rationale="Validated proposal",
                    )
        return Finish(
            status="verify", rationale="Availability and lane checks require verification"
        )

    def tools(self):
        return (
            Tool(
                "get_case_evidence",
                "Read evidence, candidates and donor conflicts",
                CaseArgs,
                self.evidence,
            ),
            Tool(
                "get_available_stock",
                "Read one SKU-size at several locations: basis, time and unknown states",
                StockArgs,
                self.stock,
            ),
            Tool(
                "get_lane_and_eta",
                "Read the scoped lane, cutoff and contract ETA",
                LaneArgs,
                self.lane,
            ),
            Tool(
                "evaluate_options",
                "Recompute deterministic options; validate donor candidates",
                OptionsArgs,
                self.evaluate,
            ),
            Tool(
                "request_clarification",
                "Draft a question in the returned store language; never send",
                ClarificationArgs,
                self.clarify,
            ),
        )


def investigate(
    repo: Repo,
    case_id: str,
    *,
    model: ChatModel,
    reader: Reader,
    policy: OptionsPolicy,
    horizon_days: int = 7,
    budget: Budget | None = None,
    prompt: str | None = None,
    reservations: tuple[Reservation, ...] | None = None,
) -> AgentRun:
    session = Investigator(repo, case_id, reader, policy, horizon_days, reservations=reservations)
    if prompt is None:
        prompt = PROMPT_PATH.read_text(encoding="utf-8")
    result = AgentLoop(
        model,
        session.tools(),
        budget=budget,
        validate_finish=session.validate,
        fallback=session.fallback,
    ).run(
        [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "case_id": case_id,
                        "as_of": repo.spec.as_of.isoformat(),
                        "store_id": session.case.store_id,
                    }
                ),
            },
        ],
        TraceMeta(
            run_id=repo.spec.run_id,
            scenario_id=repo.spec.scenario_id,
            case_id=case_id,
            as_of=repo.spec.as_of,
            mode=repo.spec.mode,
            input_refs=(ref(session.case),),
            trace_id=f"trace:{case_id}:{uuid4().hex}",
            producer=MANIFEST.id,
            producer_version=MANIFEST.version,
        ),
    )
    # Model prose is not a numerical renderer. Publish a template tied to validated scope.
    rationale = {
        "verify": "Verify the selected case before any stock movement.",
        "monitor": "Monitor the selected case; no stock movement is proposed.",
        "action_proposed": (
            "The deterministic engine validated the selected option; human approval is required."
        ),
    }[result.finish.status]
    choice = result.finish.model_copy(update={"rationale": rationale})
    steps = tuple(
        step.model_copy(update={"arguments": {**step.arguments, "rationale": rationale}})
        if step.tool in {"finish", "fallback"}
        else step
        for step in result.trace.steps
    )
    trace = result.trace.model_copy(update={"steps": steps})
    # Retain earlier tool outputs after narrowing donor candidates.
    records = [*session.facts.values(), *session.proposals.values(), *session.drafts.values()]
    if records:
        repo.put(*records)
    repo.put(trace)
    return replace(result, trace=trace, finish=choice)


class UnavailableReader:
    def __init__(self, reason: Unknown):
        self.reason = reason

    def stock(self, sku, size, locations):
        return {location: self.reason for location in locations}

    def lane_and_eta(self, origin, dest, requested_at, required_by=None):
        return self.reason


def run(ctx: Context) -> ModuleResult:
    ids = ctx.params.get("case_ids", ())
    if not ids or "llm" not in ctx.clients:
        return ModuleResult(
            module_id=MANIFEST.id,
            module_version=MANIFEST.version,
            status="blocked",
            counts={},
            errors=("Select case_ids and configure the LLM client",),
            abstentions=(),
        )
    settings = get_settings()
    domain = yaml.safe_load((settings.config_dir / "domain.yaml").read_text(encoding="utf-8"))
    policy = load_policy(settings.config_dir)
    horizon = int(domain["policy"]["horizon"]["days"]["value"])
    reader = SystemsReader.open(ctx.repo, ctx.clients.get("systems", default_client))
    unavailable = isinstance(reader, Unknown)
    if unavailable:
        reader = UnavailableReader(reader)
    traces = []
    errors = []
    try:
        for case_id in ids:
            try:
                case = visible_case(ctx.repo, case_id)
                model = model_for_run(
                    ctx.clients["llm"],
                    prompt_version=PROMPT_VERSION,
                    model=MODEL,
                    cache_context={"case": case.model_dump(mode="json")},
                )
                result = investigate(
                    ctx.repo,
                    case_id,
                    model=model,
                    reader=reader,
                    policy=policy,
                    horizon_days=horizon,
                )
                traces.append(result.trace)
            except ToolError as error:
                errors.append(f"{case_id}: {error}")
            except ReplayMiss:
                return ModuleResult(
                    module_id=MANIFEST.id,
                    module_version=MANIFEST.version,
                    status="failed",
                    counts={},
                    errors=(f"{case_id}: missing LLM recording",),
                    abstentions=(),
                )
    finally:
        if not unavailable:
            reader.client.close()
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded"
        if errors or unavailable or any(t.fallback_used for t in traces)
        else "succeeded",
        counts={
            "cases": len(ids),
            "traces": len(traces),
            "fallbacks": sum(t.fallback_used for t in traces),
        },
        errors=tuple(errors),
        abstentions=(),
    )
