"""AG-02: ``ag.analyst`` proposes one alternative with FC-03's gates and never feeds the forecast.

Inline cases and baselines for the rules (scripted model, no network), then one module run on the
DATA-01a/b fixtures with the real MIL01/NYC01 ERP rows and a fake Chat Completions client.
"""

import json
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest
from openai.types.chat import ChatCompletion

from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import (
    AgentTrace,
    ArtifactRef,
    Case,
    Evidence,
    EvidenceRelation,
    ForecastAdjustment,
    ForecastPoint,
    ModuleSnapshot,
    Observation,
    Quantity,
    RunSpec,
    ScenarioValues,
)
from tesseract.core.db import connect
from tesseract.core.fixtures import read_fixtures
from tesseract.core.registry import Registry
from tesseract.core.repo import Repo, create_run
from tesseract.modules.actions.options import case_forecast
from tesseract.modules.agents import analyst
from tesseract.modules.agents.runtime import ModelReply, ToolCall, ToolError
from tesseract.modules.intelligence import baseline, overlay
from tesseract.modules.sources import erp

ROME = ZoneInfo("Europe/Rome")
STORE = overlay.Store("MIL01", ROME, frozenset())
POLICY = overlay.load_policy(REPO_ROOT / "config")
AS_OF = datetime(2026, 10, 9, 18, tzinfo=UTC)
START = date(2026, 10, 10)
SKU = "J20931A00012-999"
FIXTURES = REPO_ROOT / "data" / "fixtures"


def local(day: date, hour: int = 0, minute: int = 0, second: int = 0) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, second, tzinfo=ROME)


def spec(as_of=AS_OF, run_id="test", stores=("MIL01",)):
    return RunSpec(
        run_id=run_id, scenario_id="historical", as_of=as_of, stores=stores,
        source_manifest_hash="s", config_hash="c", code_version="0", mode="fixture", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


def derived(id_, at):
    return dict(
        id=id_, version="v1", available_at=at, availability_basis="test", source_refs=(),
        run_id="test", scenario_id="historical", computed_at=at, input_refs=(),
        producer="test", producer_version="1",
    )  # fmt: skip


def obs(name, value=6.0, unit="units", first=date(2026, 10, 8), days=2):
    at = local(date(2026, 10, 9), 20)
    return Observation(
        **derived(f"obs-{name}", at), document_id=f"doc-{name}", kind="unmet_demand",
        store_id="MIL01", period_start=local(first),
        period_end=local(first + timedelta(days - 1), 23, 59, 59), product_mention="Maire nera",
        quantity=Quantity(kind="exact", value=value, unit=unit), direction="up",
        attribution="store_staff", negated=False,
        evidence=(Evidence(document_id=f"doc-{name}", document_version="v1",
                           segment_id=f"seg-{name}", quote="x", char_start=0, char_end=1),),
        extractor_version="test",
    )  # fmt: skip


def case(*facts, name="maire"):
    at = max(f.available_at for f in facts)
    return Case(
        **derived(f"case-{name}", at), case_type="unmet_demand", store_id="MIL01",
        scope_level="sku", scope_id=SKU, window_start=min(f.period_start for f in facts),
        window_end=at, status="open", owner="merch", priority="high", priority_reason="test",
        first_available_at=at, last_received_at=at, last_independent_evidence_at=at,
        valid_until=at + timedelta(days=7), supporting=tuple(overlay.ref(f) for f in facts),
        contradicting=(), n_documents=len(facts), n_origin_groups=len(facts),
        n_unknown_origins=0, blocking_uncertainties=(), context_refs=(),
    )  # fmt: skip


def base_fc():
    flat = ScenarioValues(low=2.0, base=2.0, high=2.0)
    return ForecastAdjustment(
        **{**derived(f"baseline-mil01-{SKU.lower()}-{START:%Y%m%d}", AS_OF - timedelta(days=3)),
           "producer": baseline.MANIFEST.id},
        case_ids=(), store_id="MIL01", sku=SKU,
        baseline_ref=ArtifactRef(kind="ForecastVintage", id=f"v/MIL01/{SKU}", version="2026-10-05"),
        horizon_start=START, horizon_end=START + timedelta(6), status="unchanged", reason="test",
        series=tuple(ForecastPoint(date=START + timedelta(i), baseline=2.0, latent=flat,
                                   servable=flat) for i in range(7)),
        components=(), proposal_source="code",
    )  # fmt: skip


def setup(*facts, relations=()):
    """Two possible episodes: FC-03 abstains, the analyst may pick one."""
    c = case(*facts)
    base = base_fc()
    det = overlay.build_overlays(
        spec(), [c], facts, relations, {("MIL01", SKU): base}, {"MIL01": STORE}, {}, {}, POLICY
    ).records[0]
    inputs = analyst.CaseInputs(
        case=c, store=STORE, observations={f.id: f for f in facts},
        duplicates=overlay.copies(relations), baselines={SKU: base}, overlays={SKU: det},
        policy=POLICY,
    )  # fmt: skip
    return inputs, base, det


def repo_for(tmp_path, inputs, base, det):
    s = spec()
    engine = connect(f"sqlite:///{tmp_path / 'a.db'}")
    create_run(engine, s)
    repo = Repo(engine, s)
    repo.put(*inputs.observations.values(), inputs.case, base, det)
    return repo


def call(name, args, id_):
    return ToolCall(id=id_, name=name, arguments=json.dumps(args))


class Scripted:
    def __init__(self, *turns):
        self.turns = list(turns)

    def complete(self, messages, tools, timeout_s):
        self.last = messages
        return ModelReply(tool_calls=tuple(self.turns.pop(0))) if self.turns else ModelReply()


A, B = obs("a", 6.0), obs("b", 10.0, first=date(2026, 10, 7), days=3)


def test_manifest_is_discovered_after_the_overlay():
    manifest = {m.id: m for m in Registry.discover().manifests()}["ag.analyst"]
    assert set(manifest.requires) == {"fc.baseline", "fc.overlay", "int.cases"}
    assert manifest.produces == ("AgentTrace", "ForecastAdjustment")


def test_single_episode_is_fc03_on_the_baseline_never_on_the_overlay():
    inputs, base, det = setup(A, B)
    assert det.status == "unchanged" and det.reason.startswith("overlapping_episodes")
    (alt,) = analyst.propose(inputs, "single_episode", B.id, spec())
    episode = overlay.gate(B, STORE)
    same = overlay.build_overlay(spec(), inputs.case, base, STORE, POLICY, [episode], [])
    assert alt.status == "computed" and alt.proposal_source == "agent"
    assert alt.producer == "ag.analyst" and alt.baseline_ref == base.baseline_ref
    assert [p.latent for p in alt.series] == [p.latent for p in same.series]
    assert alt.components == same.components
    assert ArtifactRef(kind="ForecastAdjustment", id=det.id, version=det.version) in alt.input_refs
    assert alt.id != det.id


def test_no_uplift_equals_the_baseline_with_its_reason():
    inputs, base, _ = setup(A, B)
    (alt,) = analyst.propose(inputs, "no_uplift", None, spec())
    assert alt.status == "unchanged" and alt.reason.startswith("analyst_no_uplift")
    assert all(p.latent.high == p.baseline for p in alt.series)


def test_choices_are_distinct_versions():
    inputs, _, _ = setup(A, B)
    versions = {
        analyst.propose(inputs, "single_episode", A.id, spec())[0].version,
        analyst.propose(inputs, "single_episode", B.id, spec())[0].version,
        analyst.propose(inputs, "no_uplift", None, spec())[0].version,
    }
    assert len(versions) == 3


def test_analyst_uses_incremental_policy_from_the_run_snapshot():
    run_spec = spec().model_copy(
        update={
            "modules": (ModuleSnapshot(manifest=overlay.MANIFEST, params={"incremental": False}),)
        }
    )
    assert analyst._policy_for_spec(run_spec).incremental is False


def test_finish_must_cite_the_episode_selected_for_the_proposal(tmp_path):
    inputs, base, det = setup(A, B)
    repo = repo_for(tmp_path, inputs, base, det)
    model = Scripted(
        [call("get_case_evidence", {"case_id": "case-maire"}, "c0")],
        [call("propose_scenario", {"case_id": "case-maire", "template": "single_episode",
                                   "observation_id": B.id}, "c1")],
        [call("finish", {"status": "action_proposed", "evidence_refs": [A.id],
                         "option_id": f"alt:case-maire:single_episode:{B.id}",
                         "rationale": "x"}, "c2")],
        [call("finish", {"status": "action_proposed", "evidence_refs": [B.id],
                         "option_id": f"alt:case-maire:single_episode:{B.id}",
                         "rationale": "x"}, "c3")],
    )  # fmt: skip
    result, chosen = analyst.analyse(repo, inputs, model=model)
    finishes = [s for s in result.trace.steps if s.tool == "finish"]
    assert f"cite the selected observation {B.id}" in finishes[0].error
    assert finishes[1].error is None
    assert chosen and chosen[0].proposal_source == "agent"


def test_the_model_cannot_pass_a_fact_the_gates_reject():
    requests = obs("req", unit="requests")
    inputs, _, _ = setup(A, requests)
    with pytest.raises(ToolError, match="unit_requests_not_units"):
        analyst.propose(inputs, "single_episode", requests.id, spec())


def test_the_model_cannot_pick_a_fact_outside_the_case():
    inputs, _, _ = setup(A, B)
    with pytest.raises(ToolError, match="not a supporting observation"):
        analyst.propose(inputs, "single_episode", "obs-stranger", spec())


def test_a_certain_copy_cannot_be_the_episode():
    copy = obs("copy")
    rel = EvidenceRelation(
        **derived("rel-dup", copy.available_at), from_ref=overlay.ref(copy),
        to_ref=overlay.ref(A), relation="duplicates", basis="test", evidence_refs=(),
    )  # fmt: skip
    inputs, _, _ = setup(A, copy, relations=[rel])
    with pytest.raises(ToolError, match="copy of obs-a"):
        analyst.propose(inputs, "single_episode", copy.id, spec())


def test_proposal_is_stored_beside_and_never_selected_over_the_overlay(tmp_path):
    inputs, base, det = setup(A, B)
    repo = repo_for(tmp_path, inputs, base, det)
    model = Scripted(
        [call("get_case_evidence", {"case_id": "case-maire"}, "c1")],
        [
            call(
                "propose_scenario",
                {"case_id": "case-maire", "template": "single_episode", "observation_id": B.id},
                "c2",
            )
        ],  # fmt: skip
        [
            call(
                "finish",
                {
                    "status": "action_proposed",
                    "evidence_refs": [B.id],
                    "option_id": f"alt:case-maire:single_episode:{B.id}",
                    "rationale": "the longer note describes the episode",
                },
                "c3",
            )
        ],  # fmt: skip
    )
    result, chosen = analyst.analyse(repo, inputs, model=model)
    assert result.finish.status == "action_proposed" and not result.trace.fallback_used
    assert result.finish.rationale == analyst.RATIONALE["action_proposed"]
    (alt,) = chosen
    stored = repo.list(ForecastAdjustment, store_id="MIL01", sku=SKU)
    assert {(f.producer, f.status) for f in stored} == {
        ("fc.baseline", "unchanged"), ("fc.overlay", "unchanged"), ("ag.analyst", "computed")
    }  # fmt: skip
    assert case_forecast(repo, "MIL01", SKU, "case-maire").id == det.id
    assert repo.list(AgentTrace)[0].outcome == "action_proposed"
    analyst.analyse(repo, inputs, model=Scripted(*model_turns_again(B.id)))
    assert len(repo.list(ForecastAdjustment, where={"producer": "ag.analyst"})) == 1


def model_turns_again(obs_id):
    return (
        [call("propose_scenario", {"case_id": "case-maire", "template": "single_episode",
                                   "observation_id": obs_id}, "c1")],
        [call("finish", {"status": "action_proposed", "evidence_refs": [obs_id],
                         "option_id": f"alt:case-maire:single_episode:{obs_id}",
                         "rationale": "same"}, "c2")],
    )  # fmt: skip


def test_finish_needs_a_computed_proposal_and_a_cited_fact(tmp_path):
    inputs, base, det = setup(A, B)
    repo = repo_for(tmp_path, inputs, base, det)
    unknown = {"status": "action_proposed", "evidence_refs": [], "rationale": "x",
               "option_id": "alt:case-maire:no_uplift:-"}  # fmt: skip
    model = Scripted(
        [call("finish", unknown, "c1")],
        [call("get_case_evidence", {"case_id": "case-maire"}, "c2"),
         call("propose_scenario", {"case_id": "case-maire", "template": "no_uplift"}, "c3")],
        [call("finish", unknown, "c4")],
        [call("finish", {**unknown, "evidence_refs": [A.id]}, "c5")],
    )  # fmt: skip
    result, chosen = analyst.analyse(repo, inputs, model=model)
    errors = [s.error for s in result.trace.steps if s.tool == "finish"]
    assert "proposal_id from propose_scenario" in errors[0]
    assert "cite at least one supporting observation" in errors[1]
    assert errors[2] is None and chosen[0].status == "unchanged"


def test_other_cases_are_out_of_scope_and_silence_falls_back_to_verify(tmp_path):
    inputs, base, det = setup(A, B)
    repo = repo_for(tmp_path, inputs, base, det)
    model = Scripted([call("get_case_evidence", {"case_id": "case-other"}, "c1")])
    result, chosen = analyst.analyse(repo, inputs, model=model)
    assert "only case case-maire" in result.trace.steps[0].error
    assert result.trace.fallback_used and result.finish.status == "verify" and chosen == ()
    assert repo.list(ForecastAdjustment, where={"producer": "ag.analyst"}) == []


class FakeClient:
    """Chat Completions client returning a scripted conversation."""

    def __init__(self, *turns):
        self.turns = list(turns)

    def chat(self, messages, tools=None, model=None, *, cache_context=None, **generation):
        calls = self.turns.pop(0)
        return ChatCompletion.model_validate({
            "id": "x", "object": "chat.completion", "created": 0, "model": "fake",
            "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {
                "role": "assistant", "content": None,
                "tool_calls": [{"id": c.id, "type": "function",
                                "function": {"name": c.name, "arguments": c.arguments}}
                               for c in calls]}}],
        })  # fmt: skip


def test_module_runs_on_the_data01b_fixtures(tmp_path):
    """The Maire fixture case has only request counts and copies: no episode can be chosen,
    the analyst may still propose ``no_uplift``; the overlay and options default stay put."""
    _, records = read_fixtures(FIXTURES)
    kinds = ("SourceDocument", "Segment", "Observation", "EntityLink", "EvidenceRelation", "Case")
    inputs = [r for r in records if type(r).__name__ in kinds]
    as_of = max(r.available_at for r in inputs if r.available_at is not None)
    run_spec = spec(as_of, run_id="fixture", stores=("MIL01", "NYC01")).model_copy(
        update={"modules": (ModuleSnapshot(manifest=erp.MANIFEST, params={"history_days": 3}),)}
    )
    engine = connect(f"sqlite:///{tmp_path / 'f.db'}")
    create_run(engine, run_spec)
    repo = Repo(engine, run_spec)
    erp.run(SimpleNamespace(spec=run_spec, repo=repo, params={"history_days": 3}))
    repo.put(*sorted(inputs, key=lambda r: kinds.index(type(r).__name__)))
    ctx = SimpleNamespace(spec=run_spec, repo=repo, params={})
    baseline.run(ctx)
    overlay.run(ctx)

    case_id = "case-mil01-j20931a00012-999-20261002"
    ids = [r.id for r in analyst.load_inputs(repo, case_id).case.supporting]
    client = FakeClient(
        [call("get_case_evidence", {"case_id": case_id}, "c1")],
        [call("propose_scenario", {"case_id": case_id, "template": "single_episode",
                                   "observation_id": ids[0]}, "c2")],
        [call("propose_scenario", {"case_id": case_id, "template": "no_uplift"}, "c3")],
        [call("finish", {"status": "action_proposed", "evidence_refs": [ids[0]],
                         "option_id": f"alt:{case_id}:no_uplift:-", "rationale": "x"}, "c4")],
    )  # fmt: skip
    blocked = analyst.run(SimpleNamespace(repo=repo, clients={}, params={"case_ids": [case_id]}))
    assert blocked.status == "blocked"
    result = analyst.run(
        SimpleNamespace(repo=repo, clients={"llm": client}, params={"case_ids": [case_id]})
    )
    assert result.status == "succeeded" and result.counts["proposals"] == 1
    trace = repo.list(AgentTrace)[0]
    assert "fails the FC-03 gate" in trace.steps[1].error
    (alt,) = repo.list(ForecastAdjustment, where={"producer": "ag.analyst"})
    assert alt.status == "unchanged" and alt.case_ids == (case_id,)
    assert case_forecast(repo, "MIL01", SKU, case_id).producer == "fc.overlay"
