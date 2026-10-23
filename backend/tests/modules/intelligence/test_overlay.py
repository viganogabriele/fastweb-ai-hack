"""FC-03: `fc.overlay` gates, abstains with a reason, decays from the episode, reconciles the cap.

Inline cases, observations and baselines for the rules, then one smoke run on the DATA-01a/b
fixtures with the real MIL01/NYC01 ERP rows, checked against the DATA-01b forecast fixtures.
"""

import json
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import (
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
from tessera.core.db import connect
from tessera.core.fixtures import read_fixtures
from tessera.core.registry import Registry
from tessera.core.repo import Repo, create_run
from tessera.modules.intelligence import baseline, overlay
from tessera.modules.sources import erp

ROME = ZoneInfo("Europe/Rome")
STORE = overlay.Store("MIL01", ROME, frozenset())
POLICY = overlay.load_policy(REPO_ROOT / "config")
AS_OF = datetime(2026, 10, 9, 18, tzinfo=UTC)  # Fri 20:00 in Milan: horizon Sat 10 → Fri 16
START = date(2026, 10, 10)
SKU = "J20931A00012-999"
FIXTURES = REPO_ROOT / "data" / "fixtures"


def local(day: date, hour: int = 0, minute: int = 0, second: int = 0) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, second, tzinfo=ROME)


def spec(as_of=AS_OF, run_id="test"):
    return RunSpec(
        run_id=run_id, scenario_id="historical", as_of=as_of, stores=("MIL01",),
        source_manifest_hash="s", config_hash="c", code_version="0", mode="fixture", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


def derived(id_, at):
    return dict(
        id=id_, version="v1", available_at=at, availability_basis="test", source_refs=(),
        run_id="test", scenario_id="historical", computed_at=at, input_refs=(),
        producer="test", producer_version="1",
    )  # fmt: skip


def obs(name, value=6.0, unit="units", kind="unmet_demand", days=(date(2026, 10, 8), 2),
        quantity="exact", negated=False, direction="up", at=None):  # fmt: skip
    at = at or local(date(2026, 10, 9), 20)
    first, n = days if days else (None, 0)
    return Observation(
        **derived(f"obs-{name}", at), document_id=f"doc-{name}", kind=kind, store_id="MIL01",
        period_start=local(first) if first else None,
        period_end=local(first + timedelta(n - 1), 23, 59, 59) if first else None,
        product_mention="Aurea nera",
        quantity=Quantity(kind="exact", value=value, unit=unit) if quantity == "exact"
        else Quantity(kind=quantity, unit=unit),
        direction=direction, attribution="store_staff", negated=negated,
        evidence=(Evidence(document_id=f"doc-{name}", document_version="v1",
                           segment_id=f"seg-{name}", quote="x", char_start=0, char_end=1),),
        extractor_version="test",
    )  # fmt: skip


def case(*facts, scope=("sku", SKU), last=None, valid_until="auto", name="aurea",
         case_type="unmet_demand"):  # fmt: skip
    last = last or max(f.available_at for f in facts)
    at = max(f.available_at for f in facts)
    return Case(
        **derived(f"case-{name}", at), case_type=case_type, store_id="MIL01",
        scope_level=scope[0], scope_id=scope[1],
        window_start=min(f.period_start or at for f in facts),
        window_end=at, status="open", owner="merch", priority="high", priority_reason="test",
        first_available_at=at, last_received_at=at, last_independent_evidence_at=last,
        valid_until=last + timedelta(days=7) if valid_until == "auto" else valid_until,
        supporting=tuple(overlay.ref(f) for f in facts), contradicting=(), n_documents=len(facts),
        n_origin_groups=len(facts), n_unknown_origins=0, blocking_uncertainties=(), context_refs=(),
    )  # fmt: skip


def base_fc(values=(2.0,) * 7, start=START, sku=SKU, status="unchanged"):
    points = []
    for i, v in enumerate(values):
        flat = ScenarioValues(low=v, base=v, high=v) if status == "unchanged" else None
        points.append(
            ForecastPoint(date=start + timedelta(i), baseline=v, latent=flat, servable=flat)
        )
    return ForecastAdjustment(
        **{**derived(f"baseline-mil01-{sku.lower()}-{start:%Y%m%d}", AS_OF - timedelta(days=3)),
           "producer": baseline.MANIFEST.id},
        case_ids=(), store_id="MIL01", sku=sku,
        baseline_ref=ArtifactRef(kind="ForecastVintage", id=f"v/MIL01/{sku}", version="2026-10-05"),
        horizon_start=start, horizon_end=start + timedelta(len(values) - 1), status=status,
        reason="test", series=tuple(points), components=(), proposal_source="code",
    )  # fmt: skip


def duplicate(new, old):
    return EvidenceRelation(
        **derived("rel-dup", new.available_at), from_ref=overlay.ref(new), to_ref=overlay.ref(old),
        relation="duplicates", basis="test", evidence_refs=(),
    )  # fmt: skip


def build(cases, facts, baselines=None, relations=(), store=STORE, policy=POLICY, as_of=AS_OF):
    baselines = baselines or [base_fc()]
    built = overlay.build_overlays(
        spec(as_of), cases, facts, relations, {(b.store_id, b.sku): b for b in baselines},
        {"MIL01": store}, {f"{SKU}-M": SKU}, {"MIL01": {SKU, "J20931A00012-742"}}, policy,
    )  # fmt: skip
    return built.records


def one(*args, **kwargs) -> ForecastAdjustment:
    (record,) = build(*args, **kwargs)
    return record


def scenario(record, name):
    return [getattr(p.latent, name) for p in record.series]


def assert_baseline(record):
    assert record.status == "unchanged" and not record.components
    for p in record.series:
        assert p.latent == p.servable == ScenarioValues(low=p.baseline, base=p.baseline,
                                                        high=p.baseline)  # fmt: skip


def test_manifest_is_discovered_after_baseline_and_cases():
    manifest = {m.id: m for m in Registry.discover().manifests()}["fc.overlay"]
    assert manifest == overlay.MANIFEST
    assert manifest.requires == ("fc.baseline", "int.cases")


@pytest.mark.parametrize(
    ("fact", "code"),
    [
        (obs("req", value=7, unit="requests"), "unit_requests_not_units"),
        (obs("cust", value=3, unit="customers"), "unit_customers_not_units"),
        (obs("vague", quantity="vague"), "quantity_vague"),
        (obs("stock", kind="stockout", value=0), "kind_stockout_gives_no_uplift"),
        (obs("neg", negated=True), "negated"),
        (obs("down", kind="demand_down", direction="down"), "kind_demand_down_gives_no_uplift"),
        (obs("open", days=None), "period_unknown"),
        (obs("zero", value=0), "count_not_positive"),
    ],
)
def test_inadmissible_fact_keeps_the_baseline_with_its_reason(fact, code):
    record = one([case(fact)], [fact])
    assert_baseline(record)
    assert record.reason == f"no_admissible_episode: {fact.id}: {code}"
    assert record.case_ids == ("case-aurea",) and record.baseline_ref == base_fc().baseline_ref


def test_admissible_episode_gives_ordered_decaying_scenarios():
    fact = obs("units")  # 6 units over Thu 8 and Fri 9: u = 3 units/day
    record = one([case(fact)], [fact])
    assert record.status == "computed" and record.reason is None
    anchor = date(2026, 10, 9)  # the episode ends on Fri 9, confirmed that evening
    w = [2 ** (-(START + timedelta(i) - anchor).days / 7) for i in range(7)]
    assert scenario(record, "low") == [2.0] * 7  # delta_low = 0
    assert scenario(record, "base") == pytest.approx([2.0 + 1.5 * x for x in w])
    assert scenario(record, "high") == pytest.approx([2.0 + 3.0 * x for x in w])
    assert all(p.servable == p.latent for p in record.series)
    (component,) = record.components
    assert component.type == "incremental_episode" and component.unit == "units"
    assert component.episode_refs == (overlay.ref(fact),)
    assert component.params["u_units_per_day"] == 3.0 and component.params["r"] == 1.0
    assert ArtifactRef(kind="Observation", id=fact.id, version="v1") in record.input_refs
    assert record.available_at == max(fact.available_at, base_fc().available_at)


def test_decay_runs_from_the_episode_not_from_the_run():
    """Same facts, a run three days later: smaller weights, no new document needed."""
    fact = obs("units")
    early = one([case(fact)], [fact])
    late = one([case(fact)], [fact], baselines=[base_fc(start=START + timedelta(3))],
               as_of=AS_OF + timedelta(days=3))  # fmt: skip
    assert scenario(late, "high")[0] == pytest.approx(2.0 + 3.0 * 2 ** (-4 / 7))
    assert scenario(late, "high")[0] < scenario(early, "high")[0]
    # Past validity (Fri 16 evening) the contribution is zero, the case can stay open.
    assert scenario(late, "high")[-3:] == [2.0] * 3


def test_expired_episode_keeps_the_baseline():
    fact = obs("units")
    record = one([case(fact, valid_until=local(date(2026, 10, 9), 23))], [fact])
    assert_baseline(record)
    assert record.reason.startswith("episode_expired:")


def test_certain_copy_counts_once_and_does_not_refresh_decay():
    a = obs("a")
    b = obs("b", at=a.available_at + timedelta(days=2))  # a forward two days later
    record = one([case(a, b, last=a.available_at)], [a, b], relations=[duplicate(b, a)])
    assert record.status == "computed"
    (component,) = record.components
    assert component.params["n_units"] == 6.0  # not 12
    assert component.reference_time == a.period_end  # the copy's arrival is not a confirmation


def test_two_possible_episodes_are_never_summed():
    a, b = obs("a"), obs("b", value=4, at=local(date(2026, 10, 9), 21))
    record = one([case(a, b)], [a, b])
    assert_baseline(record)
    assert record.reason.startswith("overlapping_episodes: obs-a, obs-b")


def test_two_cases_quantifying_one_sku_both_abstain():
    a, b = obs("a"), obs("b", value=2)
    records = build([case(a, name="one"), case(b, scope=("sku_size", f"{SKU}-M"), name="two")],
                    [a, b])  # fmt: skip
    assert {r.case_ids for r in records} == {("case-one",), ("case-two",)}
    for record in records:
        assert_baseline(record)
        assert record.reason.startswith("concurrent_cases:")


def test_size_case_lands_on_its_colour():
    fact = obs("m")
    record = one([case(fact, scope=("sku_size", f"{SKU}-M"))], [fact])
    assert record.sku == SKU and record.status == "computed"
    assert record.components[0].params["case_scope"] == f"sku_size:{SKU}-M"


def test_style_case_is_not_split_over_colours():
    fact = obs("style")
    baselines = [base_fc(), base_fc(sku="J20931A00012-742")]
    records = build([case(fact, scope=("style", "J20931A00012"))], [fact], baselines)
    assert sorted(r.sku for r in records) == ["J20931A00012-742", SKU]
    for record in records:
        assert_baseline(record)
        assert record.reason.startswith("scope_style:")


def test_cap_clips_and_the_series_reconciles():
    fact = obs("big", value=60)  # u = 30 units/day on a 0.5 baseline: capped at 1.5
    record = one([case(fact)], [fact], baselines=[base_fc(values=(0.5,) * 7)])
    assert record.status == "computed"
    assert all(v == pytest.approx(1.5) for v in scenario(record, "high"))
    episode, clip = record.components
    assert clip.type == "cap_clip" and clip.params["cap_multiple_of_baseline"] == 3.0
    for s in ("low", "base", "high"):
        total = sum(scenario(record, s))
        uplift = episode.params["total_uplift"][s]
        assert total == pytest.approx(0.5 * 7 + uplift - clip.params["total_clipped"][s])


def test_zero_baseline_with_uplift_is_cold_start_not_estimable():
    fact = obs("units")
    record = one([case(fact)], [fact], baselines=[base_fc(values=(0.0,) + (2.0,) * 6)])
    assert record.status == "not_estimable" and record.reason.startswith("cold_start:")
    assert all(p.latent is None and p.servable is None for p in record.series)


def test_closed_days_get_no_uplift_and_do_not_count():
    sunday_closed = overlay.Store("MIL01", ROME, frozenset({6}))
    fact = obs("weekend", days=(date(2026, 10, 3), 2))  # Sat 3 + Sun 4: one open day
    record = one([case(fact, last=local(date(2026, 10, 9), 20))], [fact], store=sunday_closed,
                 baselines=[base_fc(values=(2.0, 0.0, 2.0, 2.0, 2.0, 2.0, 2.0))])  # fmt: skip
    assert record.components[0].params["open_days_counted"] == 1
    assert scenario(record, "high")[1] == 0.0  # Sun 11


def test_baseline_not_estimable_stays_not_estimable():
    fact = obs("units")
    record = one([case(fact)], [fact], baselines=[base_fc(status="not_estimable")])
    assert record.status == "not_estimable" and record.reason.startswith("baseline_not_estimable")


def test_hypothesis_off_keeps_the_baseline():
    fact = obs("units")
    off = overlay.Policy(**{**POLICY.__dict__, "incremental": False})
    record = one([case(fact)], [fact], policy=off)
    assert_baseline(record)
    assert record.reason.startswith("incremental_hypothesis_off")


def test_non_demand_and_unscoped_cases_get_no_overlay():
    fact = obs("units")
    records = build(
        [case(fact, case_type="product_feedback", name="fb"),
         case(fact, scope=("unknown", None), name="unk")], [fact],
    )  # fmt: skip
    assert records == ()


def test_run_on_the_data01b_fixtures_matches_their_forecasts(tmp_path):
    """Real MIL01/NYC01 ERP rows and the DATA-01a/b records: every fixture case is vague, a
    stock-out or a request count, so each overlay keeps the baseline, as the fixtures do."""
    _, records = read_fixtures(FIXTURES)
    kinds = ("SourceDocument", "Segment", "Observation", "EntityLink", "EvidenceRelation", "Case")
    inputs = [r for r in records if type(r).__name__ in kinds]
    as_of = max(r.available_at for r in inputs if r.available_at is not None)
    run_spec = spec(as_of, run_id="fixture").model_copy(
        update={
            "stores": ("MIL01", "NYC01"),
            "modules": (ModuleSnapshot(manifest=erp.MANIFEST, params={"history_days": 3}),),
        }
    )
    engine = connect(f"sqlite:///{tmp_path / 'o.db'}")
    create_run(engine, run_spec)
    repo = Repo(engine, run_spec)
    erp.run(SimpleNamespace(spec=run_spec, repo=repo, params={"history_days": 3}))
    repo.put(*sorted(inputs, key=lambda r: kinds.index(type(r).__name__)))
    ctx = SimpleNamespace(spec=run_spec, repo=repo, params={})
    baseline.run(ctx)
    result = overlay.run(ctx)
    again = overlay.run(ctx)

    got = {
        (r.case_ids, r.sku): r
        for r in repo.list(ForecastAdjustment, where={"producer": "fc.overlay"})
    }
    want = {}
    for path in sorted((FIXTURES / "forecast").glob("*.json")):
        (rec,) = json.loads(path.read_text(encoding="utf-8"))
        fc = ForecastAdjustment.model_validate(rec["payload"])
        want[(fc.case_ids, fc.sku)] = fc
    assert set(got) == set(want)
    for key, fc in want.items():
        assert got[key].status == fc.status == "unchanged"
        assert got[key].baseline_ref == fc.baseline_ref
        assert [p.latent for p in got[key].series] == pytest.approx([p.latent for p in fc.series])
    valentino_v01 = got[(("case-mil01-j20931a00012-999-20261002",), SKU)]
    assert "unit_requests_not_units" in valentino_v01.reason and "copy_of:" in valentino_v01.reason
    assert result.counts["computed"] == 0 and result.counts["overlays"] == len(want)
    assert again.counts["new"] == 0
