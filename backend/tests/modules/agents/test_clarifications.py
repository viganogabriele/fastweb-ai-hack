"""Pure clarification answers: scope, event time, replay and immutable branching."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from tesseract.core.contracts import (
    Case,
    Clarification,
    Evidence,
    ModuleManifest,
    ModuleSnapshot,
    Observation,
    Quantity,
    RunSpec,
    SourceDocument,
)
from tesseract.modules.agents.clarifications import (
    InvalidAnswer,
    SimulatedAnswer,
    UnrecordedAnswer,
    answer_fingerprint,
    prepare_answer,
)

NOW = datetime(2026, 10, 22, 20, tzinfo=UTC)


def ref(kind, id, version="1"):
    return {"kind": kind, "id": id, "version": version}


@pytest.fixture
def inputs():
    manifest = ModuleManifest(
        id="src.email",
        version="1",
        layer="sources",
        description="test",
        requires=(),
        optional_inputs=(),
        produces=("SourceDocument",),
        enabled=True,
        mode="recorded",
        params_schema={},
    )
    parent = RunSpec(
        run_id="original",
        scenario_id="historical",
        as_of=NOW,
        stores=("MIL01",),
        source_manifest_hash="sources-1",
        config_hash="config-1",
        code_version="code-1",
        mode="recorded",
        modules=(ModuleSnapshot(manifest=manifest, params={"scope": {"ids": ["MIL01"]}}),),
        prompt_versions={"extract": "1"},
        model_versions={"extract": "test-model"},
        authorized_fixture_refs=(),
    )
    source = SourceDocument(
        id="mail",
        version="1",
        available_at=NOW - timedelta(days=1),
        availability_basis="test",
        source_refs=(),
        source_type="email",
        connector="src.email",
        uri="dataset://test/mail.eml",
        content_hash="test",
        origin="episode-1",
        language="it",
        text="Una felpa 🧥 rossa",
        text_version="1",
        meta={"store_id": "MIL01"},
    )
    quote = "felpa 🧥"
    start = source.text.index(quote)
    observation = Observation(
        id="observation",
        version="1",
        available_at=source.available_at,
        availability_basis="test",
        source_refs=(),
        run_id=parent.run_id,
        scenario_id=parent.scenario_id,
        computed_at=NOW,
        input_refs=(ref("SourceDocument", source.id),),
        producer="test",
        producer_version="1",
        document_id=source.id,
        store_id="MIL01",
        kind="unmet_demand",
        product_mention="felpa",
        quantity=Quantity(kind="unknown"),
        direction="unknown",
        attribution="store",
        negated=False,
        evidence=(
            Evidence(
                document_id=source.id,
                document_version="1",
                segment_id="segment",
                quote=quote,
                char_start=start,
                char_end=start + len(quote),
            ),
        ),
        extractor_version="1",
    )
    common = dict(
        version="1",
        available_at=source.available_at,
        availability_basis="test",
        source_refs=(),
        run_id=parent.run_id,
        scenario_id=parent.scenario_id,
        computed_at=NOW,
        producer="test",
        producer_version="1",
    )
    case = Case(
        id="case",
        input_refs=(ref("Observation", observation.id),),
        case_type="unmet_demand",
        store_id="MIL01",
        scope_level="unknown",
        window_start=source.available_at,
        window_end=NOW,
        status="verify",
        owner="allocation",
        priority="high",
        priority_reason="Ambiguous product",
        first_available_at=source.available_at,
        last_received_at=source.available_at,
        supporting=(ref("Observation", observation.id),),
        contradicting=(),
        n_documents=1,
        n_origin_groups=1,
        n_unknown_origins=0,
        blocking_uncertainties=("Product identity",),
        context_refs=(),
        **common,
    )
    clarification = Clarification(
        id="clarification",
        input_refs=(ref("Case", case.id), ref("Observation", observation.id)),
        case_id=case.id,
        observation_refs=(ref("Observation", observation.id),),
        question="Quale prodotto e taglia?",
        asked_at=NOW - timedelta(hours=1),
        status="draft",
        **common,
    )
    answer = SimulatedAnswer("È la felpa 🧥 rossa, taglia M.\r\n店", NOW + timedelta(hours=1), "it")
    return dict(
        parent=parent,
        case=case,
        clarification=clarification,
        observations=(observation,),
        documents=(source,),
        answer=answer,
        scenario_id="simulated-reply",
        as_of=NOW + timedelta(hours=2),
    )


def test_answer_is_a_linked_source_event_and_never_changes_historical_inputs(inputs):
    original = {
        k: v.model_dump(mode="json")
        for k, v in inputs.items()
        if k in ("parent", "case", "clarification")
    }
    prepared = prepare_answer(**inputs, replay=False)
    assert prepared.document.source_type == "clarification_reply"
    assert prepared.document.available_at == inputs["answer"].received_at
    assert prepared.document.text == "È la felpa 🧥 rossa, taglia M.\n店"
    assert prepared.document.parent_document_id == "mail"
    assert prepared.document.origin == "episode-1"
    assert prepared.document.meta["simulated"] is True
    assert prepared.document.meta["observation_refs"] == [ref("Observation", "observation")]
    prepared.segment.validate_against(prepared.document)
    assert prepared.segment.char_end == len(prepared.document.text)
    assert prepared.clarification.status == "answered"
    assert prepared.clarification.answer_document_id == prepared.document.id
    assert prepared.clarification.answered_at == prepared.document.available_at
    assert prepared.clarification.run_id == prepared.run.run_id
    assert prepared.clarification.scenario_id == prepared.run.scenario_id
    for key, value in original.items():
        assert inputs[key].model_dump(mode="json") == value
    assert inputs["case"].scope_level == "unknown"
    assert inputs["observations"][0].quantity.kind == "unknown"


def test_follow_up_preserves_configuration_and_fixture_isolation(inputs):
    for mode in ("live", "recorded", "fixture"):
        parent = inputs["parent"].model_copy(
            update={
                "mode": mode,
                "authorized_fixture_refs": ("documents/test.json",) if mode == "fixture" else (),
            }
        )
        result = prepare_answer(**dict(inputs, parent=parent), replay=False)
        assert result.run.run_id != parent.run_id
        assert result.run.scenario_id != parent.scenario_id
        assert result.run.source_manifest_hash != parent.source_manifest_hash
        assert result.run.model_dump(
            exclude={"run_id", "scenario_id", "as_of", "source_manifest_hash"}
        ) == (parent.model_dump(exclude={"run_id", "scenario_id", "as_of", "source_manifest_hash"}))
        result.run.modules[0].params["scope"]["ids"].append("NYC01")
        assert parent.modules[0].params["scope"]["ids"] == ["MIL01"]


def test_replay_requires_registered_context_and_never_silently_accepts_new_text(inputs):
    with pytest.raises(UnrecordedAnswer):
        prepare_answer(**inputs)
    key = answer_fingerprint(inputs["parent"], inputs["clarification"], inputs["answer"])
    accepted = prepare_answer(**inputs, registered_answers={key})
    assert accepted == prepare_answer(**inputs, replay=False)
    changed = dict(inputs, answer=replace(inputs["answer"], text="Unregistered text"))
    with pytest.raises(UnrecordedAnswer):
        prepare_answer(**changed, registered_answers={key})
    changed = dict(
        inputs,
        clarification=inputs["clarification"].model_copy(update={"question": "New question"}),
    )
    with pytest.raises(UnrecordedAnswer):
        prepare_answer(**changed, registered_answers={key})


def test_ids_are_idempotent_but_different_events_and_schedules_have_distinct_identity(inputs):
    first = prepare_answer(**inputs, replay=False)
    assert first == prepare_answer(**inputs, replay=False)
    equiv = dict(
        inputs,
        answer=replace(
            inputs["answer"],
            text=inputs["answer"].text.replace("\r\n", "\n"),
            received_at=inputs["answer"].received_at.astimezone(timezone(timedelta(hours=2))),
        ),
    )
    assert prepare_answer(**equiv, replay=False) == first
    later = prepare_answer(**dict(inputs, as_of=inputs["as_of"] + timedelta(hours=1)), replay=False)
    assert later.document == first.document
    assert later.run.run_id != first.run.run_id
    for answer in (
        replace(inputs["answer"], text="Different"),
        replace(inputs["answer"], received_at=inputs["answer"].received_at + timedelta(seconds=1)),
        replace(inputs["answer"], language="en"),
    ):
        other = prepare_answer(**dict(inputs, answer=answer), replay=False)
        assert other.document.id != first.document.id
        assert other.run.source_manifest_hash != first.run.source_manifest_hash


@pytest.mark.parametrize(
    "change",
    [
        {"scenario_id": "historical"},
        {"scenario_id": " "},
        {"as_of": NOW},
        {"as_of": NOW.replace(tzinfo=None)},
    ],
)
def test_rejects_invalid_branch_or_clock(inputs, change):
    with pytest.raises(InvalidAnswer):
        prepare_answer(**dict(inputs, **change), replay=False)


@pytest.mark.parametrize("received", [NOW - timedelta(minutes=1), NOW, NOW.replace(tzinfo=None)])
def test_rejects_backdated_or_naive_answers(inputs, received):
    with pytest.raises(InvalidAnswer):
        prepare_answer(
            **dict(inputs, answer=replace(inputs["answer"], received_at=received)), replay=False
        )


@pytest.mark.parametrize(
    "field,update",
    [
        ("parent", {"mode": "unavailable"}),
        ("case", {"run_id": "foreign"}),
        ("case", {"scenario_id": "foreign"}),
        ("case", {"store_id": "NYC01"}),
        ("case", {"status": "closed"}),
        ("clarification", {"case_id": "foreign"}),
        ("clarification", {"run_id": "foreign"}),
        ("clarification", {"status": "cancelled"}),
        ("clarification", {"asked_at": NOW + timedelta(minutes=1)}),
        ("clarification", {"available_at": None}),
    ],
)
def test_rejects_foreign_unavailable_or_closed_targets(inputs, field, update):
    with pytest.raises(InvalidAnswer):
        prepare_answer(
            **dict(inputs, **{field: inputs[field].model_copy(update=update)}), replay=False
        )


@pytest.mark.parametrize(
    "update",
    [
        {"run_id": "foreign"},
        {"store_id": "NYC01"},
        {"version": "wrong"},
        {"available_at": NOW + timedelta(hours=1)},
    ],
)
def test_rejects_foreign_observation_versions_and_future_evidence(inputs, update):
    observation = inputs["observations"][0].model_copy(update=update)
    with pytest.raises(InvalidAnswer):
        prepare_answer(**dict(inputs, observations=(observation,)), replay=False)


def test_missing_unrelated_and_forged_sources_are_rejected(inputs):
    for change in (
        {"observations": ()},
        {"observations": inputs["observations"] * 2},
        {"documents": ()},
        {"documents": (inputs["documents"][0].model_copy(update={"version": "wrong"}),)},
        {"documents": (inputs["documents"][0].model_copy(update={"text": "forged"}),)},
        {"case": inputs["case"].model_copy(update={"input_refs": (), "supporting": ()})},
    ):
        with pytest.raises(InvalidAnswer):
            prepare_answer(**dict(inputs, **change), replay=False)


@pytest.mark.parametrize("case_refs", [(), (ref("Case", "case", "other-version"),)])
def test_question_requires_the_exact_selected_case_version(inputs, case_refs):
    clarification = Clarification.model_validate(
        {
            **inputs["clarification"].model_dump(),
            "input_refs": (*case_refs, ref("Observation", "observation")),
        }
    )
    with pytest.raises(InvalidAnswer, match="case version"):
        prepare_answer(**dict(inputs, clarification=clarification), replay=False)


def test_a_different_case_version_cannot_reuse_a_registered_answer(inputs):
    key = answer_fingerprint(inputs["parent"], inputs["clarification"], inputs["answer"])
    case = inputs["case"].model_copy(update={"version": "2", "priority_reason": "Updated case"})
    with pytest.raises(InvalidAnswer, match="case version"):
        prepare_answer(**dict(inputs, case=case), registered_answers={key})


@pytest.mark.parametrize("same_document_id", [False, True])
def test_multiple_source_documents_never_get_an_arbitrary_parent(inputs, same_document_id):
    source = inputs["documents"][0].model_copy(
        update={
            "id": "mail" if same_document_id else "second",
            "version": "2",
            "origin": "other-origin",
        }
    )
    observation = inputs["observations"][0].model_copy(
        update={
            "id": "second-observation",
            "document_id": source.id,
            "evidence": (
                inputs["observations"][0]
                .evidence[0]
                .model_copy(update={"document_id": source.id, "document_version": source.version}),
            ),
        }
    )
    reference = ref("Observation", observation.id)
    clarification = Clarification.model_validate(
        {
            **inputs["clarification"].model_dump(),
            "observation_refs": (*inputs["clarification"].observation_refs, reference),
        }
    )
    case = Case.model_validate(
        {**inputs["case"].model_dump(), "supporting": (*inputs["case"].supporting, reference)}
    )
    result = prepare_answer(
        **dict(
            inputs,
            case=case,
            clarification=clarification,
            observations=(*inputs["observations"], observation),
            documents=(*inputs["documents"], source),
        ),
        replay=False,
    )
    assert result.document.parent_document_id is None
    assert result.document.origin is None
    assert result.document.meta["parent_document_ids"] == (
        ["mail"] if same_document_id else ["mail", "second"]
    )
    assert len(result.document.meta["parent_document_refs"]) == 2
    assert any(r["version"] == "2" for r in result.document.meta["parent_document_refs"])
