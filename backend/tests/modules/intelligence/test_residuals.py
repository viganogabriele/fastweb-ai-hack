"""Synthetic, pure FC-02 temporal/censorship regressions; no hidden answers."""

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace

import pytest

from tesseract.core.contracts import ForecastAdjustment
from tesseract.core.contracts.common import SourceRef
from tesseract.core.registry import Registry
from tesseract.core.repo import ErpRecord
from tesseract.modules.intelligence import residuals
from tesseract.modules.intelligence.residuals import DayAssessment, estimate

AS_OF = datetime(2026, 10, 20, 18, tzinfo=UTC)
SOURCE = SourceRef(uri="erp/test.csv", locator="record=2", content_hash="a" * 64)


def row(table, available_at, **data):
    return ErpRecord(
        table,
        str(data),
        "v1",
        available_at,
        "test",
        (SOURCE,),
        {"store_id": "MIL01", "sku": "J1-999", **data},
    )


@pytest.fixture
def inputs():
    forecasts = [
        row(
            "forecast",
            datetime(2026, 10, 4, 4, tzinfo=UTC),
            run_date=date(2026, 10, 4),
            week_start=date(2026, 10, d),
            fcst_units=14.0,
        )
        for d in (5, 12, 19)
    ]
    sales = [
        row(
            "sales",
            datetime(2026, 10, d + 1, 4, tzinfo=UTC),
            business_date=date(2026, 10, d),
            units_sold=4,
            units_returned=3,
        )
        for d in range(6, 20)
    ]
    assessments = [
        DayAssessment(
            "MIL01",
            "J1-999",
            r.data["business_date"],
            r.available_at,
            (SOURCE,),
            True,
            True,
            True,
            False,
        )
        for r in sales
    ]
    return dict(
        store_id="MIL01",
        sku="J1-999",
        as_of=AS_OF,
        timezone="Europe/Rome",
        forecasts=forecasts,
        sales=sales,
        assessments=assessments,
        enabled=True,
    )


def test_default_disabled(inputs):
    inputs.pop("enabled")
    assert estimate(**inputs).reason == "disabled"
    assert estimate(**inputs).multiplier == 1
    assert residuals.MANIFEST.enabled is False
    assert "fc.residuals" in {m.id for m in Registry.discover().manifests()}


def test_gross_sales_shrinkage_and_exact_window(inputs):
    result = estimate(**inputs)
    assert result.reason == "estimated"
    assert result.multiplier == pytest.approx((56 + 5) / (28 + 5))
    assert len(result.eligible) == 14
    assert (result.days[0].day, result.days[-1].day) == (date(2026, 10, 6), date(2026, 10, 19))
    assert all(d.source_refs == (SOURCE,) for d in result.days)


@pytest.mark.parametrize(("units", "expected"), [(0, 0.5), (100, 2)])
def test_clipping(inputs, units, expected):
    inputs["sales"] = [replace(r, data={**r.data, "units_sold": units}) for r in inputs["sales"]]
    assert estimate(**inputs).multiplier == expected


def test_five_complete_days_required(inputs):
    inputs["assessments"] = inputs["assessments"][:4]
    assert estimate(**inputs).multiplier == 1
    assert "insufficient_complete_observations" in estimate(**inputs).reason
    inputs["assessments"].append(
        DayAssessment(
            "MIL01", "J1-999", date(2026, 10, 10), AS_OF, (SOURCE,), True, True, True, False
        )
    )
    assert estimate(**inputs).multiplier == pytest.approx(25 / 15)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("available_all_day", False, "stockout_or_size_availability_unknown"),
        ("available_all_day", None, "stockout_or_size_availability_unknown"),
        ("movements_reconciled", False, "movements_not_reconciled"),
        ("complete", False, "incomplete_data"),
        ("disrupted", True, "disruption_or_unknown"),
        ("disrupted", None, "disruption_or_unknown"),
        ("source_refs", (), "availability_not_assessable"),
        ("available_at", AS_OF + timedelta(seconds=1), "availability_not_assessable"),
    ],
)
def test_censorship_and_unknowns_abstain(inputs, field, value, reason):
    inputs["assessments"] = [replace(a, **{field: value}) for a in inputs["assessments"]]
    result = estimate(**inputs)
    assert result.multiplier == 1
    assert len(result.eligible) == 0
    assert all(reason in d.reasons for d in result.days)


def test_no_assessment_never_treats_sales_as_proof_of_availability(inputs):
    inputs["assessments"] = []
    result = estimate(**inputs)
    assert result.multiplier == 1
    assert "availability_not_assessable" in result.reason


def test_historical_vintage_strict_local_cutoff(inputs):
    # Oct 12 midnight Rome = Oct 11 22:00 UTC. The vintage exactly at
    # midnight cannot predict Oct 12, but is available for Oct 13 onward.
    inputs["forecasts"].append(
        row(
            "forecast",
            datetime(2026, 10, 11, 22, tzinfo=UTC),
            run_date=date(2026, 10, 11),
            week_start=date(2026, 10, 12),
            fcst_units=70.0,
        )
    )
    result = estimate(**inputs)
    by_day = {d.day.day: d for d in result.days}
    assert by_day[12].baseline == 2
    assert by_day[13].baseline == 10
    assert by_day[19].baseline is None  # latest vintage lacks that week
    assert "missing_historical_forecast" in by_day[19].reasons


def test_newest_store_vintage_missing_sku_does_not_backfill(inputs):
    inputs["forecasts"].append(
        row(
            "forecast",
            datetime(2026, 10, 5, 4, tzinfo=UTC),
            run_date=date(2026, 10, 5),
            week_start=date(2026, 10, 5),
            sku="OTHER",
            fcst_units=70.0,
        )
    )
    assert all("missing_historical_forecast" in d.reasons for d in estimate(**inputs).days)


def test_future_rows_and_other_stores_are_invisible(inputs):
    expected = estimate(**inputs)
    inputs["forecasts"].extend(
        [
            row(
                "forecast",
                AS_OF + timedelta(seconds=1),
                run_date=date(2026, 10, 5),
                week_start=date(2026, 10, 5),
                fcst_units=700.0,
            ),
            row(
                "forecast",
                datetime(2026, 10, 5, tzinfo=UTC),
                run_date=date(2026, 10, 5),
                week_start=date(2026, 10, 5),
                store_id="OTHER",
                fcst_units=700.0,
            ),
        ]
    )
    inputs["sales"].append(
        replace(
            inputs["sales"][0],
            available_at=AS_OF + timedelta(seconds=1),
            data={**inputs["sales"][0].data, "units_sold": 900},
        )
    )
    assert estimate(**inputs) == expected


def test_late_sales_missing_not_zero(inputs):
    inputs["sales"] = [
        replace(r, available_at=AS_OF + timedelta(seconds=1)) for r in inputs["sales"]
    ]
    result = estimate(**inputs)
    assert all(d.sales is None and "missing_sales" in d.reasons for d in result.days)
    assert result.multiplier == 1


def test_duplicates_not_double_counted_conflicts_excluded(inputs):
    expected = estimate(**inputs)
    inputs["sales"] *= 2
    inputs["forecasts"] *= 2
    assert estimate(**inputs) == expected
    inputs["sales"].append(
        replace(inputs["sales"][0], data={**inputs["sales"][0].data, "units_sold": 999})
    )
    result = estimate(**inputs)
    assert "invalid_or_conflicting_sales" in result.days[0].reasons
    assert len(result.eligible) == 13


def test_zero_forecast_positive_sales_is_not_fixed_by_multiplier(inputs):
    inputs["forecasts"] = [
        replace(r, data={**r.data, "fcst_units": 0.0}) for r in inputs["forecasts"]
    ]
    assert estimate(**inputs).reason == "cold_start_or_forecast_bias"
    assert estimate(**inputs).multiplier == 1
    inputs["sales"] = [replace(r, data={**r.data, "units_sold": 0}) for r in inputs["sales"]]
    assert estimate(**inputs).reason == "estimated"
    assert estimate(**inputs).multiplier == 1


def test_closed_days_excluded_and_full_week_denominator(inputs):
    inputs["closed_weekdays"] = frozenset({6})
    result = estimate(**inputs)
    assert len(result.eligible) == 12
    assert all(d.baseline == pytest.approx(14 / 6) for d in result.eligible)
    assert all(
        d.baseline == 0 and "closed_day" in d.reasons for d in result.days if d.day.weekday() == 6
    )


def test_naive_clock_rejected(inputs):
    inputs["as_of"] = AS_OF.replace(tzinfo=None)
    with pytest.raises(ValueError, match="timezone-aware"):
        estimate(**inputs)


def test_module_persists_separate_auditable_abstention(monkeypatch, inputs):
    # A real Repo round trip; module consumes only baseline producer artifacts.
    from tesseract.core.contracts import ArtifactRef, ForecastPoint, RunSpec, ScenarioValues
    from tesseract.core.db import connect
    from tesseract.core.repo import Repo, create_run

    engine = connect("sqlite://")
    spec = RunSpec(
        run_id="residual-test",
        scenario_id="historical",
        as_of=AS_OF,
        stores=("MIL01",),
        source_manifest_hash="test",
        config_hash="test",
        code_version="test",
        mode="live",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    create_run(engine, spec)
    repository = Repo(engine, spec)
    flat = ScenarioValues(low=2, base=2, high=2)
    base = ForecastAdjustment(
        id="baseline-test",
        version="v1",
        available_at=AS_OF,
        availability_basis="test",
        source_refs=(SOURCE,),
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        computed_at=AS_OF,
        input_refs=(),
        producer="fc.baseline",
        producer_version="1",
        case_ids=(),
        store_id="MIL01",
        sku="J1-999",
        baseline_ref=ArtifactRef(kind="ForecastVintage", id="test", version="v1"),
        horizon_start=date(2026, 10, 21),
        horizon_end=date(2026, 10, 21),
        status="unchanged",
        reason="baseline",
        series=(ForecastPoint(date=date(2026, 10, 21), baseline=2, latent=flat, servable=flat),),
        components=(),
        proposal_source="code",
    )
    repository.put(base)
    store = row("stores", AS_OF, timezone="Europe/Rome")
    tables = {"stores": [store], "forecast": inputs["forecasts"], "sales": inputs["sales"]}
    monkeypatch.setattr(residuals.erp, "read", lambda _, table, **kwargs: tables[table])
    ctx = SimpleNamespace(repo=repository)
    result = residuals.run(ctx)
    assert result.status == "degraded"
    assert result.counts == {"proposals": 1, "new": 1, "corrected": 0}
    output = repository.list(ForecastAdjustment, where={"producer": "fc.residuals"})[0]
    assert output.series == base.series
    assert output.components[0].params["multiplier"] == 1
    assert "availability_not_assessable" in output.reason
    assert len(output.components[0].params["days"]) == 14
    assert repository.list(ForecastAdjustment, where={"producer": "fc.baseline"}) == [base]
    assert residuals.run(ctx).counts["new"] == 0
