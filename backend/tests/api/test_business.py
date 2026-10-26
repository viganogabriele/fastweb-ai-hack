"""Dashboard routes read immutable run artifacts, including after input files disappear."""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from tesseract.api.main import create_app
from tesseract.core.config import Settings
from tesseract.core.contracts import RunSpec
from tesseract.core.db import connect
from tesseract.core.run_repo import repo_session
from tesseract.modules.sources import business


def test_business_api_publication_and_snapshot_isolation(tmp_path, monkeypatch):
    from tests.modules.sources.test_business import AS_OF, kpi, write_csv

    root = tmp_path / "sources"
    write_csv(
        root,
        "erp/master_data/stores.csv",
        [dict(store_id="MIL01", timezone="Europe/Rome", region="EMEA")],
    )
    write_csv(root, "erp/master_data/sku_colour.csv", [dict(sku="A-999", category="Outerwear")])
    raw = write_csv(root, "erp/kpi/store_daily_kpi.csv", [kpi("MIL01", "2026-10-21")])
    settings = Settings(_env_file=None, sources_dir=root, data_dir=tmp_path)
    monkeypatch.setattr(business, "get_settings", lambda: settings)
    engine = connect(settings.db_url)
    spec = RunSpec(
        run_id="business-run",
        scenario_id="historical",
        as_of=AS_OF,
        stores=("MIL01",),
        source_manifest_hash="test",
        config_hash="test",
        code_version="test",
        mode="recorded",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    client = TestClient(create_app(engine=engine, settings=settings))
    with repo_session(engine, spec) as repo:
        business.run(SimpleNamespace(spec=spec, repo=repo))
    assert client.get("/api/runs/business-run/kpi").status_code == 409
    with repo_session(engine, spec.run_id) as repo:
        repo.publish()
    first = client.get("/api/runs/business-run/kpi")
    assert first.status_code == 200
    assert first.json()[0]["sales_eur"] == 100
    raw.unlink()
    assert client.get("/api/runs/business-run/kpi").json() == first.json()
    assert client.get("/api/runs/business-run/market").json()["stores"] == ["MIL01"]
    assert client.get("/api/runs/missing/market").status_code == 404
    assert client.get("/api/runs/business-run/kpi?fixture=true").status_code == 403
    old = spec.model_copy(update={"run_id": "old"})
    with repo_session(engine, old) as repo:
        repo.publish()
    assert client.get("/api/runs/old/kpi").status_code == 404
    engine.dispose()
