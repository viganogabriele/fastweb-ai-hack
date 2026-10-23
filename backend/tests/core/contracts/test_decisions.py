import pytest
from pydantic import ValidationError

from tesseract.core.contracts import (
    ActionOption,
    Case,
    Clarification,
    Decision,
    EntityLink,
    EvidenceRelation,
    ForecastAdjustment,
    ForecastPoint,
    Leg,
    LinkCandidate,
    ScenarioValues,
)

REF = {"kind": "Observation", "id": "observation-1", "version": "v1"}


def leg_payload():
    return dict(
        origin="MIL02",
        dest="MIL01",
        sku="STYLE-COLOR",
        size="2",
        qty=1,
        pickup_at="2026-10-23T08:00:00Z",
        eta_at="2026-10-23T10:00:00Z",
        sellable_at="2026-10-24T08:00:00Z",
        lane_id="domestic-1",
        cost_eur=None,
    )


@pytest.mark.parametrize("quantity", [0, -1, 1.5, True, "2"])
def test_legs_require_positive_integer_quantities(quantity):
    with pytest.raises(ValidationError):
        Leg(**{**leg_payload(), "qty": quantity})


def test_leg_keeps_eta_distinct_from_sellable_time():
    leg = Leg(**leg_payload())
    assert leg.eta_at < leg.sellable_at
    with pytest.raises(ValidationError):
        Leg(**{**leg_payload(), "sellable_at": "2026-10-23T09:00:00Z"})


@pytest.mark.parametrize("status", ["fail", "unknown"])
def test_unknown_or_failed_mandatory_checks_block_recommendations(derived_fields, status):
    payload = dict(
        **derived_fields,
        case_id="case-1",
        kind="transfer",
        legs=[leg_payload()],
        checks=[
            dict(
                name="size_demand",
                status=status,
                mandatory=True,
                detail="size curve unverified",
                source_refs=[],
            )
        ],
        assumptions=[],
        valid_until="2026-10-23T08:00:00Z",
        recommended=False,
        rationale="needs verification",
        input_version_hash="inputs-v1",
    )
    blocked = ActionOption(**payload)
    assert blocked.outcomes is None
    with pytest.raises(ValidationError, match="mandatory"):
        ActionOption(**{**payload, "recommended": True})


def test_informational_option_does_not_impute_zero_outcomes(derived_fields):
    option = ActionOption(
        **derived_fields,
        case_id="case-1",
        kind="verify_stock",
        legs=[],
        checks=[],
        assumptions=[],
        valid_until="2026-10-23T08:00:00Z",
        recommended=True,
        rationale="confirm current sellable stock",
        input_version_hash="inputs-v1",
    )
    assert option.model_dump(mode="json")["outcomes"] is None


def test_candidate_scale_and_ambiguous_target(derived_fields):
    candidate = LinkCandidate(
        target_id="STYLE-COLOR", level="sku", method="fuzzy", score=90, score_min=0, score_max=100
    )
    payload = dict(
        **derived_fields,
        observation_id="observation-1",
        status="ambiguous",
        level=None,
        candidates=[candidate],
        decided_by="code",
        rationale="two aliases",
    )
    assert EntityLink(**payload).target_id is None
    with pytest.raises(ValidationError):
        EntityLink(**{**payload, "target_id": "STYLE-COLOR"})
    with pytest.raises(ValidationError):
        LinkCandidate(**{**candidate.model_dump(), "score": 101})


def test_corrections_are_versioned_fact_relations(derived_fields):
    payload = dict(
        **derived_fields,
        from_ref={**REF, "version": "v2"},
        to_ref=REF,
        relation="supersedes",
        basis="explicit correction",
        evidence_refs=[REF],
    )
    relation = EvidenceRelation(**payload)
    assert relation.available_at is not None
    with pytest.raises(ValidationError, match="fact"):
        EvidenceRelation(**{**payload, "to_ref": {**REF, "kind": "SourceDocument"}})


def test_unresolved_case_stays_visible_for_verification(derived_fields):
    case = Case(
        **derived_fields,
        case_type="unmet_demand",
        store_id="MIL01",
        scope_level="unknown",
        window_start="2026-10-22T08:00:00Z",
        window_end="2026-10-22T18:00:00Z",
        status="verify",
        owner="store_manager",
        priority="high",
        priority_reason="identity unclear",
        first_available_at="2026-10-22T17:00:00Z",
        last_received_at="2026-10-22T17:00:00Z",
        supporting=[REF],
        contradicting=[],
        n_documents=2,
        n_origin_groups=1,
        n_unknown_origins=0,
        blocking_uncertainties=["ambiguous_product"],
        context_refs=[],
    )
    assert case.scope_id is None
    with pytest.raises(ValidationError):
        Case(**{**case.model_dump(), "n_origin_groups": 3})


def forecast_payload(derived_fields):
    return dict(
        **derived_fields,
        case_ids=["case-1"],
        store_id="MIL01",
        sku="STYLE-COLOR",
        baseline_ref={"kind": "ForecastAdjustment", "id": "baseline-1", "version": "v1"},
        horizon_start="2026-10-23",
        horizon_end="2026-10-24",
        status="unchanged",
        reason="no quantified independent evidence",
        components=[],
        proposal_source="code",
        series=[
            dict(
                date=day,
                baseline=0,
                latent=dict(low=0, base=0, high=0),
                servable=dict(low=0, base=0, high=0),
            )
            for day in ("2026-10-23", "2026-10-24")
        ],
    )


def test_forecast_zero_is_preserved_and_missing_stays_not_estimable(derived_fields):
    payload = forecast_payload(derived_fields)
    assert ForecastAdjustment(**payload).series[0].baseline == 0
    missing = ForecastAdjustment(
        **{
            **payload,
            "status": "not_estimable",
            "baseline_ref": None,
            "reason": "missing vintage",
            "series": [dict(date="2026-10-23", baseline=None, latent=None, servable=None)],
        }
    )
    assert missing.series[0].baseline is None
    with pytest.raises(ValidationError):
        ForecastAdjustment(**{**payload, "series": payload["series"][:1]})
    with pytest.raises(ValidationError):
        ForecastAdjustment(**{**payload, "series": payload["series"][::-1]})


def test_scenario_order_and_exposure():
    with pytest.raises(ValidationError):
        ScenarioValues(low=3, base=2, high=4)
    with pytest.raises(ValidationError):
        ForecastPoint(
            date="2026-10-23",
            baseline=1,
            latent=dict(low=1, base=1, high=1),
            servable=dict(low=1, base=2, high=3),
        )
    with pytest.raises(ValidationError):
        ForecastPoint(
            date="2026-10-23", baseline=None, latent=dict(low=1, base=1, high=1), servable=None
        )


def test_not_estimable_preserves_known_baseline_but_cannot_assert_scenarios(derived_fields):
    payload = forecast_payload(derived_fields)
    payload.update(status="not_estimable", reason="incomplete vintage")
    with pytest.raises(ValidationError, match="quantified scenarios"):
        ForecastAdjustment(**payload)
    payload["series"] = [dict(date="2026-10-23", baseline=2, latent=None, servable=None)]
    assert ForecastAdjustment(**payload).series[0].baseline == 2


def test_computed_forecast_requires_explanatory_components(derived_fields):
    payload = forecast_payload(derived_fields)
    payload["status"] = "computed"
    with pytest.raises(ValidationError, match="explanatory components"):
        ForecastAdjustment(**payload)
    payload["components"] = [
        dict(
            type="daily_disaggregation",
            episode_refs=[],
            evidence_refs=[REF],
            params={"weight": 0.2},
            unit="units",
            effective_from="2026-10-23T00:00:00Z",
            effective_until="2026-10-25T00:00:00Z",
            reference_time="2026-10-22T17:00:00Z",
            formula_version="uniform-v1",
            explanation="Uniform weights over open days",
        )
    ]
    assert ForecastAdjustment(**payload).status == "computed"


@pytest.mark.parametrize(
    "changes",
    [
        {"dispatch_status": "accepted"},
        {"dispatch_status": "pending"},
        {"request_ref": REF},
        {"response_ref": REF},
    ],
)
def test_rejected_decision_cannot_have_dispatch_effects(derived_fields, changes):
    payload = dict(
        **derived_fields,
        option_id="option-1",
        input_version_hash="inputs-v1",
        decision="rejected",
        by="operator",
        at="2026-10-22T20:00:00Z",
        idempotency_key="decision-key-1",
        dispatch_status="draft",
    )
    assert Decision(**payload).decision == "rejected"
    with pytest.raises(ValidationError, match="cannot be dispatched"):
        Decision(**{**payload, **changes})


def test_outcome_comparisons_require_matching_unique_scenarios(derived_fields):
    outcome = dict(
        scenario_id="base",
        lost_units_dest=1,
        lost_units_donor=0,
        leftover_units_dest=0,
        leftover_units_donor=5,
        transport_cost_eur=10,
        demand_basis="servable scenario",
        size_allocation_basis="declared policy weights",
    )
    payload = dict(
        **derived_fields,
        case_id="case-1",
        kind="transfer",
        forecast_ref=REF,
        legs=[{**leg_payload(), "cost_eur": 10}],
        checks=[
            dict(
                name="size_demand",
                status="pass",
                mandatory=True,
                detail="verified size curve",
                source_refs=[REF],
            )
        ],
        outcomes=[outcome],
        baseline_outcomes=[outcome],
        assumptions=[],
        valid_until="2026-10-23T08:00:00Z",
        recommended=True,
        rationale="validated comparison",
        input_version_hash="inputs-v1",
    )
    assert ActionOption(**payload).recommended
    with pytest.raises(ValidationError, match="same scenarios"):
        ActionOption(**{**payload, "baseline_outcomes": [{**outcome, "scenario_id": "high"}]})
    with pytest.raises(ValidationError, match="unique scenario ids"):
        ActionOption(**{**payload, "outcomes": [outcome, outcome]})


def test_clarification_answer_has_its_own_later_availability(derived_fields):
    payload = dict(
        **derived_fields,
        case_id="case-1",
        observation_refs=[REF],
        question="Which size?",
        asked_at="2026-10-22T19:00:00Z",
        status="asked",
    )
    assert Clarification(**payload).simulated is True
    with pytest.raises(ValidationError):
        Clarification(
            **{
                **payload,
                "status": "answered",
                "answer_document_id": "answer-1",
                "answered_at": "2026-10-22T19:00:00Z",
            }
        )
    answer = Clarification(
        **{
            **payload,
            "status": "answered",
            "answer_document_id": "answer-1",
            "answered_at": "2026-10-22T20:00:00Z",
        }
    )
    assert answer.answered_at > answer.asked_at
