"""RFC §7.3 gate test 3 (TST-03): dedup does not inflate quantities.

The RFC item has three clauses, each checked end to end through the pure chain
``int.dedup`` (relations, origin state) → ``int.cases`` (case, decay) → ``fc.overlay`` (units):

1. a copy or forward does not increase quantities and does not renew decay;
2. a distinct new request is not removed;
3. an uncertain origin is not added.

Store MIL01 (Europe/Rome, open every day). Run evening Fri 2026-10-09 20:00 in Milan, overlay
horizon Sat 10 → Fri 16 on a flat baseline of 2 units/day.
"""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import (
    ArtifactRef,
    EntityLink,
    Evidence,
    ForecastAdjustment,
    ForecastPoint,
    Observation,
    Quantity,
    RunSpec,
    ScenarioValues,
    Segment,
    SourceDocument,
)
from tessera.modules.integration import cases, dedup
from tessera.modules.intelligence import baseline, overlay

ROME = ZoneInfo("Europe/Rome")
AS_OF = datetime(2026, 10, 9, 18, tzinfo=UTC)
D = date(2026, 10, 8)
SKU = "J20931A00012-999"
OWNERS, VALIDITY_DAYS = cases.load_domain(REPO_ROOT / "config")
VALIDITY = timedelta(days=VALIDITY_DAYS)
POLICY = overlay.load_policy(REPO_ROOT / "config")
STORE = overlay.Store("MIL01", ROME, frozenset())


def at(day: date, hour: int) -> datetime:
    return datetime(day.year, day.month, day.day, hour, tzinfo=ROME)


def spec() -> RunSpec:
    return RunSpec(
        run_id="gate-3", scenario_id="historical", as_of=AS_OF, stores=("MIL01",),
        source_manifest_hash="s", config_hash="c", code_version="0", mode="fixture", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


def report(name, *, sent, value=6, day=D, text=None, parent=None, quoted=False,
           origin="mil01@store.example"):  # fmt: skip
    """One email, its one segment, its observation of lost units of Maire nera on ``day``."""
    text = text or f"Maire nera: {value} pezzi persi per mancanza taglie."
    common = dict(version="v1", available_at=sent, availability_basis="test", source_refs=())
    doc = SourceDocument(
        id=f"doc-{name}", **common, source_type="email", connector="test", uri=f"test://{name}",
        content_hash=f"raw-{name}", origin=origin, business_date=sent.astimezone(UTC).date(),
        parent_document_id=parent, text=text, text_version="t1", meta={"store_id": "MIL01"},
    )  # fmt: skip
    seg = Segment(
        id=f"seg-{name}", **common, document_id=doc.id, text_version="t1", idx=0, text=text,
        char_start=0, char_end=len(text), is_quoted=quoted,
    )  # fmt: skip
    obs = Observation(
        id=f"obs-{name}", **common, run_id="gate-3", scenario_id="historical", computed_at=AS_OF,
        input_refs=(dedup.ref(doc), dedup.ref(seg)), producer="test", producer_version="1",
        document_id=doc.id, kind="unmet_demand", store_id="MIL01",
        period_start=at(day, 0), period_end=at(day, 0) + timedelta(days=1, seconds=-1),
        product_mention="Maire nera", quantity=Quantity(kind="exact", value=value, unit="units"),
        direction="up", attribution="store_staff", negated=False, extractor_version="test",
        evidence=(Evidence(document_id=doc.id, document_version="v1", segment_id=seg.id,
                           quote=text, char_start=0, char_end=len(text)),),
    )  # fmt: skip
    link = EntityLink(
        id=f"link-{name}", version="v1", available_at=sent, availability_basis="test",
        source_refs=(), run_id="gate-3", scenario_id="historical", computed_at=AS_OF,
        input_refs=(dedup.ref(obs),), producer="test", producer_version="1",
        observation_id=obs.id, status="linked", level="sku", target_id=SKU, candidates=(),
        decided_by="test", rationale="test",
    )  # fmt: skip
    return doc, seg, obs, link


def forward(original, name, *, sent):
    """HQ forwards the store's email: the same fact, quoted, with an explicit parent."""
    doc, obs = original[0], original[2]
    return report(
        name, sent=sent, value=obs.quantity.value, day=obs.period_start.astimezone(ROME).date(),
        text=doc.text, parent=doc.id, quoted=True, origin="hq@brand.example",
    )  # fmt: skip


def flat_baseline() -> ForecastAdjustment:
    start = date(2026, 10, 10)
    flat = ScenarioValues(low=2.0, base=2.0, high=2.0)
    return ForecastAdjustment(
        id="baseline-mil01", version="v1", available_at=AS_OF - timedelta(days=3),
        availability_basis="test", source_refs=(), run_id="gate-3", scenario_id="historical",
        computed_at=AS_OF, input_refs=(), producer=baseline.MANIFEST.id, producer_version="1",
        case_ids=(), store_id="MIL01", sku=SKU,
        baseline_ref=ArtifactRef(kind="ForecastVintage", id="v", version="2026-10-05"),
        horizon_start=start, horizon_end=start + timedelta(days=6), status="unchanged",
        reason="test", proposal_source="code", components=(),
        series=tuple(ForecastPoint(date=start + timedelta(days=i), baseline=2.0, latent=flat,
                                   servable=flat) for i in range(7)),
    )  # fmt: skip


def chain(*reports):
    """Run the three modules' pure functions on the given reports at ``AS_OF``."""
    docs, segs, observations, links = zip(*reports, strict=True)
    relations, _ = dedup.build_relations(observations, docs, segs, links, spec())
    state = dedup.state_at(observations, relations, AS_OF)
    built = cases.build_cases(
        observations, docs, links, relations, spec(), owners=OWNERS, validity=VALIDITY,
        zones={"MIL01": "Europe/Rome"},
    )  # fmt: skip
    overlays = overlay.build_overlays(
        spec(), built.cases, observations, relations, {("MIL01", SKU): flat_baseline()},
        {"MIL01": STORE}, {}, {"MIL01": {SKU}}, POLICY,
    ).records  # fmt: skip
    return relations, state, built.cases, overlays


def latent(record: ForecastAdjustment, scenario: str = "base") -> list[float]:
    return [getattr(p.latent, scenario) for p in record.series]


def episode_params(record: ForecastAdjustment) -> dict:
    (component,) = [c for c in record.components if c.type == "incremental_episode"]
    return component.params


# 1. A copy or forward does not increase quantities and does not renew decay

ORIGINAL_SENT = at(D, 19)
COPIES = {
    # Same body, same sender, same business date, a second email two hours later.
    "resend": lambda original: report("copy", sent=at(D, 21)),
    # The next morning HQ forwards it: a later arrival that must not look like a new confirmation.
    "forward": lambda original: forward(original, "copy", sent=at(D + timedelta(days=1), 10)),
}


@pytest.mark.parametrize("kind", COPIES)
def test_copy_adds_no_units_and_does_not_renew_decay(kind):
    original = report("orig", sent=ORIGINAL_SENT)
    copy = COPIES[kind](original)
    _, _, (alone,), (alone_fc,) = chain(original)
    relations, state, (case,), (record,) = chain(original, copy)

    assert [r.relation for r in relations] == ["duplicates"]
    assert relations[0].from_ref == dedup.ref(copy[2])
    assert relations[0].to_ref == dedup.ref(original[2])
    assert state.active_refs == (dedup.ref(original[2]),) and state.non_additive_refs == ()
    assert state.groups[0].first_available_at == ORIGINAL_SENT

    # The copy is kept as evidence, but it is the same origin, with the original's age.
    assert dedup.ref(copy[2]) in case.supporting
    assert case.n_documents == 2 and case.n_origin_groups == 1
    assert case.last_independent_evidence_at == alone.last_independent_evidence_at
    assert case.last_independent_evidence_at == ORIGINAL_SENT
    assert case.valid_until == alone.valid_until == ORIGINAL_SENT + VALIDITY

    # Units: 6, not 12. The scenarios are exactly those of the original alone.
    assert record.status == alone_fc.status == "computed"
    assert episode_params(record)["n_units"] == 6
    assert episode_params(record)["decay_anchor"] == episode_params(alone_fc)["decay_anchor"]
    assert record.series == alone_fc.series
    assert dedup.ref(copy[2]) not in record.components[0].episode_refs


def test_late_forward_of_an_expired_report_does_not_revive_it():
    old_day = date(2026, 10, 1)
    original = report("old", sent=at(old_day, 19), day=old_day)
    late = forward(original, "fwd", sent=at(date(2026, 10, 9), 10))
    relations, _, (case,), (record,) = chain(original, late)

    assert [r.relation for r in relations] == ["duplicates"]
    assert case.last_independent_evidence_at == at(old_day, 19)
    assert case.valid_until == at(old_day, 19) + VALIDITY < datetime(2026, 10, 10, tzinfo=ROME)
    assert record.status == "unchanged" and record.reason.startswith("episode_expired")
    assert latent(record) == [2.0] * 7


# 2. A distinct new request is not removed


def test_distinct_new_request_is_kept_and_renews_the_case():
    original = report("orig", sent=ORIGINAL_SENT)
    next_day = D + timedelta(days=1)
    new = report(
        "new", sent=at(next_day, 19), value=3, day=next_day,
        text="Maire nera: oggi altri 3 pezzi persi, clienti diversi.",
    )  # fmt: skip
    relations, state, (case,), (record,) = chain(original, new)

    assert relations == ()  # disjoint days, different text: neither a copy nor a possible overlap
    assert set(state.active_refs) == {dedup.ref(original[2]), dedup.ref(new[2])}
    assert state.non_additive_refs == ()
    assert set(case.supporting) == {dedup.ref(original[2]), dedup.ref(new[2])}
    assert case.n_origin_groups == 2
    assert case.last_independent_evidence_at == at(next_day, 19)
    assert case.valid_until == at(next_day, 19) + VALIDITY
    # The overlay keeps both facts as inputs; it never drops the new one to quantify the old.
    assert {dedup.ref(original[2]), dedup.ref(new[2])} <= set(record.input_refs)
    assert new[2].id in (record.reason or "")


def test_distinct_new_request_alone_is_quantified_from_its_own_units():
    next_day = D + timedelta(days=1)
    new = report("new", sent=at(next_day, 19), value=3, day=next_day)
    _, _, (case,), (record,) = chain(new)
    assert record.status == "computed" and episode_params(record)["n_units"] == 3
    assert case.valid_until == at(next_day, 19) + VALIDITY


# 3. An uncertain origin is not added


UNCERTAIN = {
    # Same day and product, different wording and amount: maybe the same customers, maybe not.
    "different_wording": dict(value=4, text="Maire nera: oggi 4 pezzi persi.", sent=at(D, 20)),
    # Identical text but no sender: text alone does not prove a copy.
    "unknown_sender": dict(origin=None, sent=at(D, 20)),
}


@pytest.mark.parametrize("variant", UNCERTAIN)
def test_uncertain_origin_is_flagged_and_never_summed(variant):
    first = report("first", sent=ORIGINAL_SENT, origin=None if variant == "unknown_sender" else
                   "mil01@store.example")  # fmt: skip
    second = report("second", **UNCERTAIN[variant])
    relations, state, (case,), (record,) = chain(first, second)

    assert [r.relation for r in relations] == ["possibly_same_episode"]
    # Neither fact is deleted, and both are marked non-additive.
    both = {dedup.ref(first[2]), dedup.ref(second[2])}
    assert set(state.active_refs) == set(state.non_additive_refs) == both
    assert set(case.supporting) == both
    assert any("do not add" in u for u in case.blocking_uncertainties)
    # No 6 + 4 (or 6 + 6): the forecast stays at the baseline with a reason to verify.
    assert record.status == "unchanged" and record.reason.startswith("overlapping_episodes")
    assert record.components == ()
    for scenario in ("low", "base", "high"):
        assert latent(record, scenario) == [2.0] * 7
