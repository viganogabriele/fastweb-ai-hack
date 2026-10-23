"""PLT-09: published forecast reads preserve scenarios, abstentions and snapshot isolation."""

from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert

from tesseract.api.main import create_app
from tesseract.core.config import Settings
from tesseract.core.contracts import (
    AdjustmentComponent,
    ArtifactRef,
    ForecastAdjustment,
    ForecastPoint,
    RunSpec,
    ScenarioValues,
)
from tesseract.core.db import artifacts, connect
from tesseract.core.run_repo import repo_session

AS_OF = datetime(2026, 10, 22, 20, tzinfo=UTC)
DAY = date(2026, 10, 23)


def adjustment(run_id, id="baseline", *, store="MIL01", sku="STYLE-999", status="unchanged"):
    values = ScenarioValues(low=2, base=2, high=2)
    computed = status == "computed"
    return ForecastAdjustment(
        id=id,
        version="1",
        available_at=AS_OF,
        availability_basis="test input time",
        source_refs=(),
        run_id=run_id,
        scenario_id="historical",
        computed_at=AS_OF,
        input_refs=(),
        producer="fc.overlay" if id != "baseline" else "fc.baseline",
        producer_version="1",
        case_ids=("case-1",) if id != "baseline" else (),
        store_id=store,
        sku=sku,
        baseline_ref=ArtifactRef(kind="ForecastVintage", id="vintage-1", version="1"),
        horizon_start=DAY,
        horizon_end=DAY,
        status=status,
        reason=None if computed else "No admissible quantitative evidence",
        series=(
            ForecastPoint(
                date=DAY,
                baseline=2,
                latent=None
                if status == "not_estimable"
                else (ScenarioValues(low=2, base=3, high=4) if computed else values),
                servable=None
                if status == "not_estimable"
                else (ScenarioValues(low=2, base=3, high=4) if computed else values),
            ),
        ),
        components=(
            AdjustmentComponent(
                type="incremental",
                episode_refs=(),
                evidence_refs=(),
                params={"units": 1},
                unit="units",
                effective_from=AS_OF,
                effective_until="2026-10-24T00:00:00Z",
                reference_time=AS_OF,
                formula_version="test",
                explanation="Declared test scenario",
            ),
        )
        if computed
        else (),
        proposal_source="code",
    )


def seed(engine, run_id="run", *, mode="recorded", published=True, forecasts=True, hidden=False):
    spec = RunSpec(
        run_id=run_id,
        scenario_id="historical",
        as_of=AS_OF,
        stores=("MIL01", "MIL02"),
        source_manifest_hash="test",
        config_hash="test",
        code_version="test",
        mode=mode,
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    with repo_session(engine, spec, fixture_mode=mode == "fixture") as current:
        if forecasts:
            current.put(
                adjustment(run_id),
                adjustment(run_id, "overlay", status="computed"),
                adjustment(run_id, "abstention", sku="STYLE-111", status="not_estimable"),
                adjustment(run_id, "unchanged-overlay", store="MIL02"),
            )
        if hidden:
            # Independently exercise read guards by bypassing canonical write validation.
            foreign = adjustment(run_id, "foreign", store="NYC01")
            future = adjustment(run_id, "future").model_copy(
                update={
                    "available_at": datetime(2026, 10, 23, 20, tzinfo=UTC),
                }
            )
            for value in (foreign, future):
                current.session.execute(
                    insert(artifacts).values(
                        run_id=run_id,
                        kind="ForecastAdjustment",
                        id=value.id,
                        version=value.version,
                        store_id=value.store_id,
                        sku=value.sku,
                        available_at=value.available_at,
                        payload=value.model_dump(mode="json"),
                        input_refs=[],
                    )
                )
        if published:
            current.publish()


@pytest.fixture
def service(tmp_path):
    engine = connect(f"sqlite:///{tmp_path / 'forecast.db'}")
    app = create_app(
        engine=engine, fixture_engine=engine, settings=Settings(_env_file=None, fixture_mode=True)
    )
    with TestClient(app) as client:
        yield client, engine, app
    engine.dispose()


def test_forecast_preserves_baseline_scenarios_and_abstention(service):
    client, engine, _ = service
    seed(engine)
    response = client.get("/api/runs/run/forecast")
    assert response.status_code == 200
    values = {value["id"]: value for value in response.json()}
    assert set(values) == {"baseline", "overlay", "abstention", "unchanged-overlay"}
    assert values["baseline"] == adjustment("run").model_dump(mode="json")
    assert values["overlay"]["producer"] == "fc.overlay"
    assert values["overlay"]["series"][0]["servable"] == {"low": 2, "base": 3, "high": 4}
    assert values["overlay"]["components"][0]["params"] == {"units": 1}
    assert values["abstention"]["status"] == "not_estimable"
    assert values["abstention"]["reason"] == "No admissible quantitative evidence"
    assert values["abstention"]["series"][0]["servable"] is None
    assert values["unchanged-overlay"]["reason"]


@pytest.mark.parametrize(
    "query,expected",
    [
        ("store=MIL01", {"baseline", "overlay", "abstention"}),
        ("store=MIL02", {"unchanged-overlay"}),
        ("sku=STYLE-111", {"abstention"}),
        ("store=MIL01&sku=STYLE-999", {"baseline", "overlay"}),
        ("sku=missing", set()),
    ],
)
def test_filters_do_not_mix_stores_or_skus(service, query, expected):
    client, engine, _ = service
    seed(engine)
    response = client.get(f"/api/runs/run/forecast?{query}")
    assert response.status_code == 200
    assert {value["id"] for value in response.json()} == expected


def test_publication_clock_run_and_namespace_guards(service):
    client, engine, app = service
    seed(engine, hidden=True)
    seed(engine, "pending", published=False)
    seed(engine, "empty", forecasts=False)
    seed(engine, "fixtures", mode="fixture")
    assert client.get("/api/runs/no-run/forecast").status_code == 404
    assert client.get("/api/runs/pending/forecast").status_code == 409
    assert client.get("/api/runs/empty/forecast").json() == []
    assert client.get("/api/runs/run/forecast?store=NYC01").status_code == 422
    assert client.get("/api/runs/fixtures/forecast").status_code == 404
    assert client.get("/api/runs/run/forecast?fixture=true").status_code == 404
    fixture = client.get("/api/runs/fixtures/forecast?fixture=true")
    assert fixture.status_code == 200
    assert all(value["run_id"] == "fixtures" for value in fixture.json())
    visible = client.get("/api/runs/run/forecast").json()
    assert len(visible) == 4
    assert all(value["run_id"] == "run" for value in visible)
    assert not {"future", "foreign"} & {value["id"] for value in visible}
    app.state.settings = Settings(_env_file=None, fixture_mode=False)
    assert client.get("/api/runs/fixtures/forecast?fixture=true").status_code == 403


def test_openapi_exposes_forecast_contract_and_filters(service):
    client, _, _ = service
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/runs/{run_id}/forecast"]["get"]
    assert {parameter["name"] for parameter in operation["parameters"]} == {
        "run_id",
        "store",
        "sku",
        "fixture",
    }
    response = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert response["items"]["$ref"] == "#/components/schemas/ForecastAdjustment"
