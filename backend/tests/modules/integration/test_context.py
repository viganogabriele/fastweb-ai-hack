"""INT-06: int.context associates context events to cases by geo/time without uplift."""

from datetime import UTC, datetime, timedelta

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


@pytest.mark.parametrize(
    ("event_offset_hours", "expected_refs"),
    [(0, 1), (48, 1), (-48, 1), (49, 0), (-49, 0), (72, 0), (-72, 0)],
)
def test_associates_by_geo_time(tmp_path, event_offset_hours, expected_refs):
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
    offset = timedelta(hours=event_offset_hours)
    ev = ev.model_copy(update={"start": ev.start + offset, "end": ev.end + offset})
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
    assert len(out.context_refs) == expected_refs
    if expected_refs:
        assert out.context_refs[0].id == ev.id


@pytest.mark.parametrize(
    ("gap", "slack", "expected"),
    [
        (timedelta(hours=-12), timedelta(0), True),
        (timedelta(0), timedelta(0), True),
        (timedelta(microseconds=1), timedelta(0), False),
        (timedelta(hours=24), timedelta(hours=24), True),
        (timedelta(hours=24, microseconds=1), timedelta(hours=24), False),
        (timedelta(hours=48), timedelta(hours=24), False),
    ],
)
def test_time_tolerance_is_the_maximum_gap_in_either_order(gap, slack, expected):
    start = datetime(2026, 10, 8, tzinfo=UTC)
    end = start + timedelta(days=1)
    event_start = end + gap
    event_end = event_start + timedelta(days=1)

    assert context._overlap(start, end, event_start, event_end, slack) is expected
    assert context._overlap(event_start, event_end, start, end, slack) is expected
