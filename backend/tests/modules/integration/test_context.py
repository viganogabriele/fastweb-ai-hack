"""INT-06: int.context associates context events to cases by geo/time without uplift."""

from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from tessera.core.contracts import (
    Case,
    ContextEvent,
    ModuleSnapshot,
    Quantity,
    RunSpec,
)
from tessera.core.db import connect
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.run_repo import repo_session
from tessera.modules.integration import context


def make_case(as_of, store="MIL01"):
    return Case(
        id="case-mil01-x-20261008",
        version="v1",
        available_at=as_of,
        availability_basis="test",
        source_refs=(),
        run_id="r1",
        scenario_id="s1",
        computed_at=as_of,
        input_refs=(),
        producer="int.cases",
        producer_version="1",
        case_type="unmet_demand",
        store_id=store,
        scope_level="sku",
        scope_id="SKU1",
        window_start=datetime(2026, 10, 8, tzinfo=UTC),
        window_end=datetime(2026, 10, 9, tzinfo=UTC),
        status="open",
        owner="merch",
        priority="high",
        priority_reason="x",
        decision_due_at=None,
        first_available_at=datetime(2026, 10, 8, tzinfo=UTC),
        last_received_at=datetime(2026, 10, 9, tzinfo=UTC),
        last_independent_evidence_at=datetime(2026, 10, 9, tzinfo=UTC),
        valid_until=None,
        supporting=(),
        contradicting=(),
        n_documents=1,
        n_origin_groups=1,
        n_unknown_origins=0,
        blocking_uncertainties=(),
        context_refs=(),
    )


def make_event(as_of, store="MIL01", role="context_only"):
    return ContextEvent(
        id="ctx-milano-cold-20261008",
        version="v1",
        available_at=as_of,
        availability_basis="weather_observation_day_end",
        source_refs=(),
        run_id="r1",
        scenario_id="s1",
        computed_at=as_of,
        input_refs=(),
        producer="src.external",
        producer_version="1",
        kind="weather_cold",
        store_ids=(store,),
        start=datetime(2026, 10, 8, tzinfo=UTC),
        end=datetime(2026, 10, 9, tzinfo=UTC),
        issued_at=None,
        magnitude=Quantity(kind="vague", raw="-5 °C"),
        description="cold",
        role=role,
    )


def test_associates_by_geo_time(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 't.db'}")
    as_of = datetime(2026, 10, 22, tzinfo=UTC)
    spec = RunSpec(
        run_id="r1",
        scenario_id="s1",
        as_of=as_of,
        stores=("MIL01",),
        source_manifest_hash="s",
        config_hash="c",
        code_version="0",
        mode="fixture",
        modules=(ModuleSnapshot(manifest=context.MANIFEST, params={}),),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    case = make_case(as_of)
    ev = make_event(as_of)
    with repo_session(engine, spec, fixture_mode=True, write=True) as repo:
        repo.put(case, ev)
    registry = Registry((RegisteredModule(context.MANIFEST, context.run),))
    from tessera.core.orchestrator import run as orchestrate

    statuses = orchestrate(spec, engine=engine, registry=registry, clients={})
    assert statuses[0].status in ("succeeded", "degraded")
    with repo_session(engine, spec, fixture_mode=True, write=False) as repo:
        outs = repo.list(Case)
    # pick updated version
    out = max(outs, key=lambda c: c.version)
    assert len(out.context_refs) == 1
    assert out.context_refs[0].id == ev.id


@pytest.fixture
def context_repo(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'context.db'}")
    spec = RunSpec(
        run_id="r1",
        scenario_id="s1",
        as_of=datetime(2026, 10, 22, tzinfo=UTC),
        stores=("MIL01",),
        source_manifest_hash="s",
        config_hash="c",
        code_version="0",
        mode="fixture",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    try:
        with repo_session(engine, spec, fixture_mode=True, write=True) as repo:
            yield repo
    finally:
        engine.dispose()


def test_incremental_context_preserves_history_and_retries_are_idempotent(context_repo):
    repo = context_repo
    case = make_case(repo.spec.as_of)
    first = make_event(repo.spec.as_of)
    repo.put(case, first)
    ctx = SimpleNamespace(spec=repo.spec, repo=repo, params={})

    assert context.run(ctx).counts["updated_cases"] == 1
    enriched = repo.get(Case, case.id)
    second = first.model_copy(update={"id": "second-event"})
    repo.put(second)

    result = context.run(ctx)

    assert result.counts == {"cases": 1, "events": 2, "updated_cases": 1}
    latest = repo.get(Case, case.id)
    assert {r.id for r in latest.context_refs} == {first.id, second.id}
    assert repo.get(Case, case.id, case.version) == case
    assert repo.get(Case, case.id, enriched.version) == enriched
    assert context.run(ctx).counts["updated_cases"] == 0
    assert repo.get(Case, case.id) == latest
    assert len(repo.list(Case)) == 3


@pytest.mark.parametrize(("old_version", "new_version"), [("v9", "v10"), ("v10", "v2")])
def test_only_latest_stored_version_of_each_case_is_enriched(
    context_repo, old_version, new_version
):
    repo = context_repo
    old = make_case(repo.spec.as_of).model_copy(update={"version": old_version})
    latest = old.model_copy(update={"version": new_version, "status": "verify"})
    other = latest.model_copy(update={"id": "other-case", "priority": "low"})
    event = make_event(repo.spec.as_of)
    repo.put(old, latest, other, event)

    result = context.run(SimpleNamespace(spec=repo.spec, repo=repo, params={}))

    assert result.counts == {"cases": 2, "events": 1, "updated_cases": 2}
    for original in (latest, other):
        enriched = repo.get(Case, original.id)
        assert enriched.version == original.version + ".ctx"
        assert enriched.status == original.status
        assert enriched.priority == original.priority
        assert enriched.context_refs == (context.ref(event),)
    assert repo.get(Case, old.id, old.version) == old
    assert repo.get(Case, old.id, old.version + ".ctx") is None
