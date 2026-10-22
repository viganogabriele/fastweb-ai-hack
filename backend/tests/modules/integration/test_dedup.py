"""INT-02 regressions: immutable evidence, conservative copies and T1 → T2 → T1."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import (
    ArtifactRef,
    EntityLink,
    Evidence,
    EvidenceRelation,
    Observation,
    Quantity,
    RunSpec,
    Segment,
    SourceDocument,
)
from tessera.core.db import connect
from tessera.core.fixtures import read_fixtures
from tessera.core.registry import Registry
from tessera.core.run_repo import repo_session
from tessera.modules.integration import dedup

T1 = datetime(2026, 10, 2, 18, tzinfo=UTC)
T2 = T1 + timedelta(hours=1)
T3 = T2 + timedelta(hours=1)
START, END = T1.replace(hour=0), T1.replace(hour=23)


def spec(as_of=T3, run_id="test"):
    return RunSpec(
        run_id=run_id,
        scenario_id="historical",
        as_of=as_of,
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


def fact(
    name,
    *,
    at=T1,
    text="Maire nera: 7 richieste.",
    parent=None,
    quoted=False,
    value=7,
    period=(START, END),
    mention="Maire nera",
    negated=False,
    origin="store@example.test",
    doc_id=None,
):
    doc_id = doc_id or f"doc-{name}"
    common = dict(version="v1", available_at=at, availability_basis="test", source_refs=())
    doc = SourceDocument(
        id=doc_id,
        **common,
        source_type="email",
        connector="test",
        uri=f"test://{doc_id}",
        content_hash=f"raw-{doc_id}",
        origin=origin,
        business_date=at.date(),
        parent_document_id=parent,
        text=text,
        text_version="text-v1",
        meta={"store_id": "MIL01"},
    )
    seg = Segment(
        id=f"seg-{name}",
        **common,
        document_id=doc.id,
        text_version=doc.text_version,
        idx=0,
        text=text,
        char_start=0,
        char_end=len(text),
        is_quoted=quoted,
    )
    obs = Observation(
        id=f"obs-{name}",
        **common,
        run_id="test",
        scenario_id="historical",
        computed_at=T3,
        input_refs=(dedup.ref(doc), dedup.ref(seg)),
        producer="test",
        producer_version="1",
        document_id=doc.id,
        kind="unmet_demand",
        store_id="MIL01",
        period_start=period[0],
        period_end=period[1],
        product_mention=mention,
        quantity=Quantity(kind="exact", value=value, unit="requests"),
        direction="up",
        attribution="store_staff",
        negated=negated,
        extractor_version="test",
        evidence=(
            Evidence(
                document_id=doc.id,
                document_version=doc.version,
                segment_id=seg.id,
                quote=text,
                char_start=0,
                char_end=len(text),
            ),
        ),
    )
    return doc, seg, obs


def infer(*triples, as_of=T3):
    docs, segs, observations = zip(*triples, strict=True)
    return dedup.build_relations(observations, docs, segs, (), spec(as_of))


def entity_link(obs, target, *, name=None):
    common = {
        key: getattr(obs, key)
        for key in (
            "available_at",
            "availability_basis",
            "source_refs",
            "run_id",
            "scenario_id",
            "computed_at",
            "producer",
            "producer_version",
        )
    }
    return EntityLink(
        id=name or f"link-{obs.id}-{obs.version}",
        version="v1",
        **common,
        input_refs=(dedup.ref(obs),),
        observation_id=obs.id,
        status="linked",
        level="sku",
        target_id=target,
        candidates=(),
        decided_by="test",
        rationale="test",
    )


def test_exact_resend_counts_once_and_keeps_the_original_age():
    original, copy = fact("a"), fact("b", at=T2)
    relations, abstentions = infer(original, copy)
    assert not abstentions
    assert [r.relation for r in relations] == ["duplicates"]
    relation = relations[0]
    assert relation.available_at == T2
    assert relation.from_ref == dedup.ref(copy[2])
    assert relation.to_ref == dedup.ref(original[2])
    assert {r.kind for r in relation.input_refs} == {"Observation", "SourceDocument", "Segment"}
    state = dedup.state_at([original[2], copy[2]], relations, T3)
    assert state.document_count == 2
    assert len(state.groups) == len(state.active_refs) == 1
    assert state.groups[0].first_available_at == T1
    assert state.groups[0].period_start == START
    assert state.active_refs == (dedup.ref(original[2]),)
    assert original[2].quantity.value == copy[2].quantity.value == 7


def test_parent_and_exact_quoted_fact_prove_a_forward():
    original = fact("a")
    forward = fact("b", at=T2, parent=original[0].id, quoted=True, origin="hq@example.test")
    relations, _ = infer(original, forward)
    assert [r.relation for r in relations] == ["duplicates"]
    assert dedup.ref(forward[1]) in relations[0].evidence_refs


@pytest.mark.parametrize(
    "change",
    [
        {"value": 9},
        {"negated": True},
        {"mention": "Maire nera taglia 2"},
        {"period": (START - timedelta(days=1), END - timedelta(days=1))},
    ],
)
def test_size_period_negation_or_quantity_difference_is_not_a_copy(change):
    a, b = fact("a"), fact("b", at=T2, **change)
    relations, _ = infer(a, b)
    assert all(r.relation != "duplicates" for r in relations)


def test_similar_daily_requests_stay_separate_and_uncertain_quantities_are_not_added():
    a, b = fact("a"), fact("b", at=T2, text="Maire nera: altre 7 richieste.")
    relations, _ = infer(a, b)
    assert [r.relation for r in relations] == ["possibly_same_episode"]
    state = dedup.state_at([a[2], b[2]], relations, T3)
    assert len(state.active_refs) == len(state.non_additive_refs) == 2
    assert len(state.groups) == 2


def test_new_daily_request_is_a_distinct_episode():
    a = fact("a")
    b = fact(
        "b", at=T1 + timedelta(days=1), period=(START + timedelta(days=1), END + timedelta(days=1))
    )
    relations, _ = infer(a, b, as_of=T3 + timedelta(days=1))
    assert relations == ()


def test_text_alone_with_unknown_sender_does_not_prove_copy():
    relations, _ = infer(fact("a", origin=None), fact("b", at=T2, origin=None))
    assert [r.relation for r in relations] == ["possibly_same_episode"]


def test_reply_and_forward_flags_alone_do_not_prove_copies_or_corrections():
    a = fact("a")
    b = fact("b", at=T2, text="Maire nera: oggi 9 richieste.", value=9, parent=a[0].id)
    b = (b[0].model_copy(update={"meta": {"is_forward": True, "subject": "CORREZIONE"}}), *b[1:])
    relations, _ = infer(a, b)
    assert [r.relation for r in relations] == ["possibly_same_episode"]


@pytest.mark.parametrize(
    "text,kind",
    [
        ("Correggo Maire nera: 9 richieste e non 7.", "supersedes"),
        ("Correction: Maire nera, 9 requests instead of 7.", "supersedes"),
        ("Ritiro la segnalazione Maire nera: 7 richieste.", "retracts"),
        ("I withdraw the Maire nera report of 7 requests.", "retracts"),
    ],
)
def test_explicit_corrections_only_disable_the_target_fact(text, kind):
    a = fact("a")
    b = fact("b", at=T2, text=text, value=9, parent=a[0].id)
    unrelated = fact("other", text=a[0].text, mention="Tib", doc_id=a[0].id)
    relations, abstentions = infer(a, b, unrelated)
    assert not abstentions
    assert [r.relation for r in relations] == [kind]
    assert relations[0].to_ref == dedup.ref(a[2])
    state = dedup.state_at([a[2], b[2], unrelated[2]], relations, T3)
    expected = {unrelated[2].id} | ({b[2].id} if kind == "supersedes" else set())
    assert {r.id for r in state.active_refs} == expected


def test_correction_requires_unique_parent_target():
    a = fact("a")
    another = fact("another", doc_id=a[0].id)
    b = fact("b", at=T2, text="Correggo: 9 e non 7.", value=9, parent=a[0].id)
    relations, abstentions = infer(a, another, b)
    assert len(abstentions) == 1 and "found 2" in abstentions[0]
    assert all(r.relation not in ("supersedes", "retracts") for r in relations)


def test_quoted_correction_does_not_create_a_new_correction():
    a = fact("a")
    b = fact("b", at=T2, text="Correggo: 9 e non 7.", value=9, parent=a[0].id, quoted=True)
    relations, _ = infer(a, b)
    assert all(r.relation not in ("supersedes", "retracts") for r in relations)


@pytest.mark.parametrize(
    "text",
    [
        "Do not withdraw the Maire nera report: 7 requests remain confirmed.",
        "I do not withdraw the Maire nera report: 7 requests remain confirmed.",
        "Non ritiro la segnalazione Maire nera: 7 richieste confermate.",
        "If confirmed, I withdraw the Maire nera report: 7 requests.",
        "I withdraw the Maire nera report if the 7 requests are a mistake.",
        "I might withdraw the Maire nera report: 7 requests.",
        "Se confermato, ritiro la segnalazione Maire nera: 7 richieste.",
        "Ritiro la segnalazione Maire nera se le 7 richieste sono errate.",
        "I withdraw the Maire nera report of 7 requests?",
        "Do not replace the Maire nera report: 7 requests remain confirmed.",
        "Non correggo la segnalazione Maire nera: 7 richieste confermate.",
        "If confirmed, correction: 9 requests instead of 7.",
        "Forse 9 richieste e non 7.",
        "Suppose there were 9 requests instead of 7.",
        "We discussed 9 requests instead of 7.",
        "I withdraw the Maire nera report once the 7 requests are confirmed as a mistake.",
        "Ritiro la segnalazione Maire nera domani: 7 richieste.",
    ],
)
def test_negated_hypothetical_or_questioned_corrections_retain_both_facts(text):
    a = fact("a")
    b = fact("b", at=T2, text=text, parent=a[0].id)
    relations, abstentions = infer(a, b)
    assert [r.relation for r in relations] == ["possibly_same_episode"]
    assert abstentions == ("obs-b: uncertain correction intent; facts retained",)
    assert len(dedup.state_at([a[2], b[2]], relations, T3).active_refs) == 2


@pytest.mark.parametrize("reverse", [False, True])
def test_segment_version_is_pinned_even_if_newer_version_changes_quoted_status(tmp_path, reverse):
    a = fact("a")
    b = fact(
        "b",
        at=T2,
        text="I withdraw the Maire nera report of 7 requests.",
        parent=a[0].id,
        quoted=True,
    )
    newer_segment = b[1].model_copy(update={"version": "v2", "is_quoted": False})
    segments = [b[1], newer_segment]
    if reverse:
        segments.reverse()
    engine = connect(f"sqlite:///{tmp_path / 'versions.db'}")
    with repo_session(engine, spec(), fixture_mode=True, write=True) as repo:
        repo.put(a[0], b[0], a[1], *segments, a[2], b[2])
        result = dedup.run(SimpleNamespace(spec=repo.spec, repo=repo))
        relations = repo.list(EvidenceRelation)
    assert result.status == "succeeded", result
    assert result.counts["active_origins"] == 2
    assert [r.relation for r in relations] == ["possibly_same_episode"]
    assert dedup.ref(b[1]) in relations[0].input_refs
    assert dedup.ref(newer_segment) not in relations[0].input_refs


@pytest.mark.parametrize("pins", [(), ("v2",), ("v1", "v2")])
def test_missing_or_ambiguous_segment_version_abstains_instead_of_falling_back(pins):
    a, b = fact("a"), fact("b", at=T2)
    obs = b[2].model_copy(
        update={
            "input_refs": (
                dedup.ref(b[0]),
                *(ArtifactRef(kind="Segment", id=b[1].id, version=v) for v in pins),
            )
        }
    )
    relations, abstentions = dedup.build_relations(
        [a[2], obs], [a[0], b[0]], [a[1], b[1]], (), spec()
    )
    assert not relations
    assert abstentions == ("obs-b: unavailable or invalid canonical evidence",)


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("include_v2", [False, True])
def test_links_bind_to_exact_observation_version_independently_of_input_order(reverse, include_v2):
    a, b = fact("a"), fact("b", at=T2)
    a_v2 = a[2].model_copy(update={"version": "v2", "available_at": T1 + timedelta(minutes=1)})
    links = [entity_link(a[2], "sku-A"), entity_link(a_v2, "sku-B"), entity_link(b[2], "sku-B")]
    observations = [a[2], b[2], *([a_v2] if include_v2 else [])]
    if reverse:
        links.reverse()
        observations.reverse()
    relations, abstentions = dedup.build_relations(
        observations, [a[0], b[0]], [a[1], b[1]], links, spec()
    )
    assert not abstentions
    assert all(r.to_ref != dedup.ref(a[2]) and r.from_ref != dedup.ref(a[2]) for r in relations)
    if include_v2:
        assert [r.relation for r in relations] == ["duplicates"]
        assert relations[0].to_ref == dedup.ref(a_v2)
        assert dedup.ref(entity_link(a_v2, "sku-B")) in relations[0].input_refs
        assert dedup.ref(entity_link(a[2], "sku-A")) not in relations[0].input_refs
    else:
        assert not relations


@pytest.mark.parametrize("reverse", [False, True])
def test_conflicting_links_for_one_observation_version_abstain(reverse):
    a, b = fact("a"), fact("b", at=T2)
    links = [entity_link(a[2], "sku-A"), entity_link(a[2], "sku-B", name="conflicting")]
    if reverse:
        links.reverse()
    relations, abstentions = dedup.build_relations(
        [a[2], b[2]], [a[0], b[0]], [a[1], b[1]], links, spec()
    )
    assert not relations
    assert abstentions == ("obs-a@v1: ambiguous or unpinned entity links",)


def test_t1_t2_t1_is_immutable_and_future_correction_is_invisible():
    a = fact("a")
    b = fact("b", at=T2, text="Correggo: 9 e non 7.", value=9, parent=a[0].id)
    relations, _ = infer(a, b)
    observations = [a[2], b[2]]
    before = dedup.state_at(observations, relations, T1)
    after = dedup.state_at(observations, relations, T2)
    assert before.active_refs == (dedup.ref(a[2]),)
    assert after.active_refs == (dedup.ref(b[2]),)
    assert dedup.state_at(observations, relations, T1) == before
    assert infer(a, b, as_of=T1) == ((), ())


def test_correction_suppresses_every_certain_copy_and_chain_does_not_resurrect():
    a, copy = fact("a"), fact("copy", at=T1 + timedelta(minutes=1))
    b = fact("b", at=T2, text="Correggo: 9 e non 7.", value=9, parent=a[0].id)
    c = fact("c", at=T3, text="Ritiro la segnalazione.", value=9, parent=b[0].id)
    relations, errors = infer(a, copy, b, c)
    assert not errors
    assert dedup.state_at([x[2] for x in (a, copy, b, c)], relations, T3).active_refs == ()


@pytest.mark.parametrize(
    "text",
    [
        "I withdraw my objection: the Maire nera report of 7 requests is confirmed.",
        "I withdraw my objection about the Maire nera report of 7 requests.",
        "Ritiro la mia obiezione: la segnalazione Maire nera di 7 richieste è confermata.",
        "Ritiro la segnalazione Tib: Maire nera, 7 richieste.",
        "I withdraw the report about Tib: Maire nera, 7 requests.",
        "I withdraw the Maire nera report of 3 requests.",
        "I withdraw the Maire nera report of 7 customers.",
    ],
)
def test_withdrawal_of_another_object_or_count_does_not_retract_confirmed_fact(tmp_path, text):
    a = fact("a")
    b = fact("b", at=T2, text=text, parent=a[0].id)
    engine = connect(f"sqlite:///{tmp_path / 'target.db'}")
    with repo_session(engine, spec(), fixture_mode=True, write=True) as repo:
        repo.put(*a[:2], *b[:2], a[2], b[2])
        result = dedup.run(SimpleNamespace(spec=repo.spec, repo=repo))
        relations = repo.list(EvidenceRelation)
    assert result.status == "degraded"
    assert result.abstentions == ("obs-b: uncertain withdrawal target; facts retained",)
    assert result.counts["active_origins"] == 2
    assert [r.relation for r in relations] == ["possibly_same_episode"]


@pytest.mark.parametrize("parent", ["doc-a", "doc-b"])
@pytest.mark.parametrize("quoted", [False, True])
@pytest.mark.parametrize(
    "intent,text,value",
    [
        ("supersedes", "Correction: Maire nera, 9 requests instead of 7.", 9),
        ("retracts", "I withdraw the Maire nera report of 7 requests.", 7),
    ],
)
def test_copied_correction_is_deduplicated_before_intent_and_keeps_age(
    tmp_path, parent, quoted, intent, text, value
):
    a = fact("a")
    b = fact("b", at=T2, text=text, value=value, parent=a[0].id)
    c = fact("c", at=T3, text=text, value=value, parent=parent, quoted=quoted)
    engine = connect(f"sqlite:///{tmp_path / 'correction-copy.db'}")
    with repo_session(engine, spec(), fixture_mode=True, write=True) as repo:
        repo.put(*a[:2], *b[:2], *c[:2], a[2], b[2], c[2])
        result = dedup.run(SimpleNamespace(spec=repo.spec, repo=repo))
        relations = repo.list(EvidenceRelation)
    assert result.status == "succeeded", result
    assert {
        (r.from_ref.id, r.to_ref.id, r.relation)
        for r in relations
        if r.relation != "possibly_same_episode"
    } == {
        (b[2].id, a[2].id, intent),
        (c[2].id, b[2].id, "duplicates"),
    }
    before = dedup.state_at([a[2], b[2], c[2]], relations, T2)
    after = dedup.state_at([a[2], b[2], c[2]], relations, T3)
    assert (
        before.active_refs
        == after.active_refs
        == ((dedup.ref(b[2]),) if intent == "supersedes" else ())
    )
    group = next(g for g in after.groups if dedup.ref(b[2]) in g.members)
    assert group.representative == dedup.ref(b[2])
    assert group.first_available_at == T2
    assert after.non_additive_refs == ()
    assert dedup.state_at([a[2], b[2], c[2]], relations, T2) == before


@pytest.mark.parametrize(
    "change", [{"available_at": None}, {"available_at": T3 + timedelta(seconds=1)}]
)
def test_unknown_or_future_relation_availability_cannot_change_state(change):
    a, b = fact("a"), fact("b", at=T2)
    relations, _ = infer(a, b)
    relations = [relations[0].model_copy(update=change)]
    assert len(dedup.state_at([a[2], b[2]], relations, T3).active_refs) == 2


def test_wrong_endpoint_version_cannot_suppress_an_observation():
    a, b = fact("a"), fact("b", at=T2)
    relations, _ = infer(a, b)
    relations = [
        relations[0].model_copy(
            update={"to_ref": dedup.ref(a[2]).model_copy(update={"version": "other"})}
        )
    ]
    assert len(dedup.state_at([a[2], b[2]], relations, T3).active_refs) == 2


def test_invalid_evidence_is_an_abstention_and_never_a_relation():
    a, b = fact("a"), fact("b", at=T2)
    b = (b[0].model_copy(update={"text": "changed source"}), *b[1:])
    relations, abstentions = infer(a, b)
    assert not relations
    assert abstentions == ("obs-b: unavailable or invalid canonical evidence",)


def test_unknown_periods_do_not_establish_independence_across_days():
    a = fact("a", period=(None, None))
    b = fact("b", at=T1 + timedelta(days=1), period=(None, None), text="Another report.")
    relations, _ = infer(a, b, as_of=T3 + timedelta(days=1))
    assert [r.relation for r in relations] == ["possibly_same_episode"]


def test_plain_negative_number_does_not_retract_or_replace_a_fact():
    a = fact("a")
    b = fact("b", at=T2, text="Not 7 requests were met.", parent=a[0].id, negated=True)
    relations, errors = infer(a, b)
    assert not errors
    assert [r.relation for r in relations] == ["possibly_same_episode"]


def test_aliases_with_the_same_link_remain_possible_overlap_with_link_provenance():
    a, b = fact("a"), fact("b", at=T2, mention="black Maire", text="Black Maire: 7 requests.")
    links = [
        EntityLink(
            **{
                k: v
                for k, v in obs.model_dump().items()
                if k
                in (
                    "version",
                    "available_at",
                    "availability_basis",
                    "source_refs",
                    "run_id",
                    "scenario_id",
                    "computed_at",
                    "producer",
                    "producer_version",
                )
            },
            id=f"link-{obs.id}",
            input_refs=(dedup.ref(obs),),
            observation_id=obs.id,
            status="linked",
            level="sku",
            target_id="sku-black",
            candidates=(),
            decided_by="test",
            rationale="test",
        )
        for obs in (a[2], b[2])
    ]
    relations, _ = dedup.build_relations([a[2], b[2]], [a[0], b[0]], [a[1], b[1]], links, spec())
    assert [r.relation for r in relations] == ["possibly_same_episode"]
    assert all(dedup.ref(lk) in relations[0].input_refs for lk in links)


@pytest.mark.parametrize("which", [0, 1])
@pytest.mark.parametrize("available", [None, T3 + timedelta(seconds=1)])
def test_unknown_or_future_documents_and_segments_cannot_create_relations(which, available):
    a, b = fact("a"), list(fact("b", at=T2))
    b[which] = b[which].model_copy(update={"available_at": available})
    relations, errors = infer(a, b)
    assert not relations
    assert len(errors) == 1


def test_relation_availability_includes_delayed_canonical_segment():
    a, b = fact("a"), list(fact("b", at=T2))
    b[1] = b[1].model_copy(update={"available_at": T3})
    relations, _ = infer(a, b)
    assert relations[0].available_at == T3


def test_manifest_is_discovered():
    assert dedup.MANIFEST in Registry.discover().manifests()


def test_data01_fixtures_match_relations_and_module_is_idempotent(tmp_path):
    _, fixtures = read_fixtures(REPO_ROOT / "data" / "fixtures")
    inputs = [
        r
        for r in fixtures
        if isinstance(r, (SourceDocument, Segment, Observation))
        and (not isinstance(r, Observation) or r.store_id == "MIL01")
        and (not isinstance(r, SourceDocument) or r.meta.get("store_id") == "MIL01")
    ]
    # Include only segments belonging to the selected documents.
    ids = {r.id for r in inputs if isinstance(r, SourceDocument)}
    inputs = [r for r in inputs if not isinstance(r, Segment) or r.document_id in ids]
    expected = {
        (r.from_ref.id, r.to_ref.id, r.relation)
        for r in fixtures
        if isinstance(r, EvidenceRelation)
    }
    engine = connect(f"sqlite:///{tmp_path / 'dedup.db'}")
    fixture_spec = spec(datetime(2026, 10, 22, 20, tzinfo=UTC), run_id="fixture")
    with repo_session(engine, fixture_spec, fixture_mode=True, write=True) as repo:
        repo.put(*inputs)
        ctx = SimpleNamespace(spec=repo.spec, repo=repo)
        result = dedup.run(ctx)
        assert result.status == "succeeded", result
        relations = repo.list(EvidenceRelation)
        assert {(r.from_ref.id, r.to_ref.id, r.relation) for r in relations} == expected
        assert result.counts["duplicates"] == result.counts["supersedes"] == 1
        assert dedup.run(ctx).counts["relations_new"] == 0
        assert len(repo.list(EvidenceRelation)) == 2
