"""AG-03b: the two recorded real-model investigator traces replay offline, unchanged
(re-record with `LLM_MODE=record data/fixtures/build_ag03b.py`)."""

import importlib.util
import json
from pathlib import Path

import pytest

from tessera.core.config import Settings
from tessera.core.contracts import AgentTrace
from tessera.modules.agents import investigator

ROOT = Path(__file__).resolve().parents[3]
BUILDER = ROOT / "data" / "fixtures" / "build_ag03b.py"
D1 = "case-mil01-i10919b00011-20261008"
AMBIGUOUS = "case-nyc01-unknown-20260906"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_ag03b", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def no_network(**_):
    raise AssertionError("replay must not construct a provider client")


@pytest.fixture(scope="module")
def replayed(tmp_path_factory):
    builder = load_builder()
    settings = Settings(llm_mode="replay", _env_file=None)
    traces = builder.investigate_all(
        settings, tmp_path_factory.mktemp("ag03b"), client_factory=no_network
    )
    return builder, traces


def recorded(builder, case_id):
    return json.loads((builder.OUT / f"{case_id}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case_id", [D1, AMBIGUOUS])
def test_replay_reproduces_the_recorded_trace(replayed, case_id):
    builder, traces = replayed
    entry = recorded(builder, case_id)
    assert entry["model"] == investigator.MODEL
    AgentTrace.model_validate(entry["trace"])
    assert builder.comparable(traces[case_id]) == builder.comparable(entry)


def test_different_evidence_leads_to_different_checks(replayed):
    _, traces = replayed
    d1, ambiguous = (AgentTrace.model_validate(traces[c]["trace"]) for c in (D1, AMBIGUOUS))
    assert not d1.fallback_used and not ambiguous.fallback_used
    assert all(s.error is None for s in (*d1.steps, *ambiguous.steps))
    d1_tools = [s.tool for s in d1.steps]
    assert d1_tools[0] == "get_case_evidence" and d1_tools[-1] == "finish"
    assert {"get_available_stock", "get_lane_and_eta", "evaluate_options"} <= set(d1_tools)
    assert "request_clarification" not in d1_tools
    assert [s.tool for s in ambiguous.steps] == [
        "get_case_evidence",
        "request_clarification",
        "finish",
    ]
    assert ambiguous.outcome == "verify"
    # D1 proposes the engine's recommended non-movement option; nothing is approved or booked.
    assert d1.outcome == "action_proposed"
    assert d1.steps[-1].arguments["option_id"] == f"opt-{D1}-notify_owner"
