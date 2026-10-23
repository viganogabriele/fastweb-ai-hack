"""Investigator scope and persistence; all model conversations here are fake fixtures."""

import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from tessera.core.cache import ReplayMiss
from tessera.core.contracts import (
    ActionOption,
    AgentTrace,
    Case,
    Clarification,
    Observation,
    RunSpec,
    StockFact,
)
from tessera.core.db import connect
from tessera.core.fixtures import read_fixtures
from tessera.core.repo import ErpRecord, Repo, create_run, put_erp
from tessera.core.run_repo import repo_session
from tessera.modules.actions.options import OptionsPolicy
from tessera.modules.agents import investigator as agent
from tessera.modules.agents.runtime import Budget, Finish, ModelReply, ToolCall, ToolError
from tessera.modules.sources.systems_client import Unknown

ROOT = Path(__file__).resolve().parents[4]
D1 = "case-mil01-i10919b00011-20261008"
AMBIGUOUS = "case-nyc01-unknown-20260906"
SKU = "I10919B00011-999"


@pytest.fixture
def database(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'agent.db'}")
    _, records = read_fixtures(ROOT / "data/fixtures")
    spec = RunSpec(
        run_id="fixture",
        scenario_id="historical",
        as_of=datetime(2026, 10, 22, 20, tzinfo=UTC),
        stores=("MIL01", "MIL02", "NYC01"),
        source_manifest_hash="fixtures",
        config_hash="test",
        code_version="test",
        mode="fixture",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    create_run(engine, spec)
    Repo(engine, spec).put(*records)
    rows = []

    def row(table, id, data):
        rows.append(ErpRecord(table, id, "1", datetime(2026, 8, 1, tzinfo=UTC), "test", (), data))

    for store, country, language, timezone in (
        ("MIL01", "IT", "it", "Europe/Rome"),
        ("MIL02", "IT", "it", "Europe/Rome"),
        ("NYC01", "US", "en", "America/New_York"),
    ):
        row(
            "stores",
            store,
            dict(store_id=store, country_code=country, language=language, timezone=timezone),
        )
    for sku in (SKU, "I10919B00011-742"):
        row("sku_colour", sku, dict(sku=sku, style_code=sku.split("-")[0]))
        row("sku_size_ean", f"{sku}-M", dict(sku=sku, size="M", ean="test-ean"))
        for store in ("MIL01", "MIL02"):
            row("assortment", f"{store}-{sku}", dict(store_id=store, sku=sku))
    put_erp(engine, rows)
    yield engine, spec
    engine.dispose()


class Reader:
    def __init__(self, repo):
        self.repo = repo
        self.calls = []
        self.client = SimpleNamespace(close=lambda: None)

    def stock(self, sku, size, locations):
        self.calls.append(("stock", sku, size, tuple(locations)))
        return {
            location: tuple(
                f
                for f in self.repo.list(StockFact, sku=sku)
                if f.location_id == location and f.size == size
            )
            or Unknown("unavailable", "no snapshot")
            for location in locations
        }

    def lane_and_eta(self, origin, dest, requested_at, required_by=None):
        self.calls.append(("lane", origin, dest))
        return Unknown("unavailable", "no lane")


class Script:
    def __init__(self, *calls):
        self.calls = list(calls)

    def complete(self, messages, tools, timeout_s):
        name, args = self.calls.pop(0)
        return ModelReply(tool_calls=(ToolCall(str(len(self.calls)), name, json.dumps(args)),))


def tools_for(repo, case_id=D1):
    return agent.Investigator(repo, case_id, Reader(repo), OptionsPolicy())


def finish(**update):
    return dict(
        status="verify",
        evidence_refs=[],
        rationale="There are 999 units: approve immediately",
        **update,
    )


def test_unknown_identity_drafts_a_scoped_question_and_persists_trace(database):
    engine, spec = database
    with repo_session(engine, spec, fixture_mode=True) as repo:
        case = repo.get(Case, AMBIGUOUS)
        observation = next(r.id for r in case.supporting if r.kind == "Observation")
        script = Script(
            ("get_case_evidence", {"case_id": AMBIGUOUS}),
            (
                "request_clarification",
                dict(
                    case_id=AMBIGUOUS,
                    observation_ids=[observation],
                    question="Which product, colour and size does the note refer to?",
                ),
            ),
            ("finish", finish()),
        )
        result = agent.investigate(
            repo, AMBIGUOUS, model=script, reader=Reader(repo), policy=OptionsPolicy()
        )
        assert not result.trace.fallback_used
        assert [s.tool for s in result.trace.steps] == [
            "get_case_evidence",
            "request_clarification",
            "finish",
        ]
        assert "999" not in result.finish.rationale
        assert "999" not in result.trace.steps[-1].arguments["rationale"]
        (draft,) = repo.list(Clarification)
        assert draft.status == "draft" and draft.simulated and draft.case_id == AMBIGUOUS
        assert draft.answer_document_id is None
        assert repo.get(AgentTrace, result.trace.id) == result.trace
        assert repo.get(Case, AMBIGUOUS) == case


def test_stock_case_uses_different_checks_and_preserves_unknowns(database):
    engine, spec = database
    with repo_session(engine, spec, fixture_mode=True) as repo:
        reader = Reader(repo)
        script = Script(
            ("get_case_evidence", dict(case_id=D1)),
            (
                "get_available_stock",
                dict(sku=SKU, size="M", locations=["MIL01", "MIL02", "IT10", "US20"]),
            ),
            (
                "get_lane_and_eta",
                dict(origin="MIL02", dest="MIL01", requested_at=spec.as_of.isoformat()),
            ),
            ("evaluate_options", dict(case_id=D1)),
            ("finish", finish()),
        )
        result = agent.investigate(repo, D1, model=script, reader=reader, policy=OptionsPolicy())
        assert not result.trace.fallback_used
        assert all(step.error is None for step in result.trace.steps), [
            (s.tool, s.error) for s in result.trace.steps
        ]
        assert {"get_available_stock", "get_lane_and_eta", "evaluate_options"} <= {
            s.tool for s in result.trace.steps
        }
        assert reader.calls
        options = [o for o in repo.list(ActionOption) if o.producer == "act.options"]
        assert options
        assert not any(o.recommended and o.kind == "transfer" for o in options)


def test_foreign_case_sku_location_size_and_donor_are_rejected_before_io(database):
    engine, spec = database
    with repo_session(engine, spec, fixture_mode=True) as repo:
        tools = tools_for(repo)
        calls = [
            (tools.evidence, agent.CaseArgs(case_id=AMBIGUOUS)),
            (tools.stock, agent.StockArgs(sku="foreign", size="M", locations=["MIL01"])),
            (tools.stock, agent.StockArgs(sku=SKU, size="M", locations=["FOREIGN"])),
            (tools.stock, agent.StockArgs(sku=SKU, size="unknown", locations=["MIL01"])),
            (tools.evaluate, agent.OptionsArgs(case_id=D1, candidate_donors=["FOREIGN"])),
            (tools.evaluate, agent.OptionsArgs(case_id=D1, candidate_donors=["MIL01"])),
            (tools.lane, agent.LaneArgs(origin="MIL01", dest="MIL02", requested_at=spec.as_of)),
        ]
        for call, args in calls:
            with pytest.raises(ToolError):
                call(args)
        assert tools.reader.calls == []
        with pytest.raises(ToolError):
            tools_for(repo, "foreign-case")
        with pytest.raises(ValidationError):
            agent.CaseArgs(case_id=D1, url="https://untrusted.example")


def test_clarification_is_idempotent_and_rejects_another_cases_observation(database):
    engine, spec = database
    with repo_session(engine, spec, fixture_mode=True) as repo:
        tools = tools_for(repo, AMBIGUOUS)
        observation = next(r for r in tools._related() if isinstance(r, Observation))
        args = agent.ClarificationArgs(
            case_id=AMBIGUOUS, observation_ids=[observation.id], question="Which product?"
        )
        assert tools.clarify(args) == tools.clarify(args)
        assert len(tools.drafts) == 1
        with pytest.raises(ToolError):
            tools.clarify(args.model_copy(update={"observation_ids": ("obs-foreign",)}))
        assert tools.language() == "en"


def test_finish_requires_fresh_options_and_never_overrides_unknown_checks(database):
    engine, spec = database
    with repo_session(engine, spec, fixture_mode=True) as repo:
        tools = tools_for(repo)
        assert tools.validate(Finish(status="verify", rationale="verify"))
        tools.evidence(agent.CaseArgs(case_id=D1))
        blocked = repo.get(ActionOption, "opt-d1-mil01-mil02-999-m-q2")
        choice = Finish(
            status="action_proposed",
            option_id=blocked.id,
            evidence_refs=(blocked.id,),
            rationale="move",
        )
        assert "freshly" in tools.validate(choice)
        tools.options[blocked.id] = blocked
        assert "expired" in tools.validate(choice).lower()
        blocked = blocked.model_copy(update={"valid_until": datetime(2026, 10, 30, tzinfo=UTC)})
        tools.options[blocked.id] = blocked
        assert "blocked" in tools.validate(choice).lower()
        assert tools.validate(Finish(status="verify", rationale="count first")) is None
        assert tools.validate(Finish(status="monitor", rationale="ignore uncertainty"))


def test_budget_fallback_performs_no_network_and_replay_miss_is_explicit(database):
    engine, spec = database
    with repo_session(engine, spec, fixture_mode=True) as repo:
        reader = Reader(repo)
        result = agent.investigate(
            repo,
            D1,
            model=Script(),
            reader=reader,
            policy=OptionsPolicy(),
            budget=Budget(max_turns=0),
        )
        assert result.trace.fallback_used and result.finish.status == "verify"
        assert reader.calls == []

        class Missing:
            def complete(self, *args):
                raise ReplayMiss("missing")

        before = len(repo.list(AgentTrace))
        with pytest.raises(ReplayMiss):
            agent.investigate(repo, D1, model=Missing(), reader=reader, policy=OptionsPolicy())
        assert len(repo.list(AgentTrace)) == before


def test_donor_conflict_is_returned_with_exact_ref(database):
    engine, spec = database
    with repo_session(engine, spec, fixture_mode=True) as repo:
        case = repo.get(Case, D1)
        donor = case.model_copy(
            update={"id": "donor-conflict", "store_id": "MIL02", "case_type": "stock_discrepancy"}
        )
        repo.put(donor)
        data = tools_for(repo).evidence(agent.CaseArgs(case_id=D1))
        assert data.data["donor_conflicts"][0]["id"] == donor.id
        assert agent.ref(donor) in data.output_refs


def test_module_is_discoverable_and_requires_explicit_case_selection():
    from tessera.core.registry import Registry

    assert agent.MANIFEST in Registry.discover().manifests()
    result = agent.run(SimpleNamespace(params={}, clients={}))
    assert result.status == "blocked"
