"""The run's product view joins display metadata with the ERP stock that run could know."""

import json
from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from tesseract.api.main import create_app
from tesseract.core.config import Settings
from tesseract.core.contracts import RunSpec
from tesseract.core.db import connect
from tesseract.core.repo import ErpRecord, put_erp
from tesseract.core.run_repo import repo_session
from tesseract.modules.sources.erp import DEFAULT_MASTER_AVAILABLE_AT

AS_OF = datetime(2026, 10, 22, 20, tzinfo=UTC)
MASTER = datetime.fromisoformat(DEFAULT_MASTER_AVAILABLE_AT)
SKU = "J20931A00012-999"


def product():
    return {
        "style_code": "J20931A00012",
        "name": "AUREA",
        "category": "Outerwear",
        "subcategory": "Short down jacket",
        "gender": "W",
        "price_eur": 1450.0,
        "variants": [
            {"sku": SKU, "color": "black", "color_code": "999"},
            {"sku": "J20931A00012-742", "color": "blu notte", "color_code": "742"},
        ],
        "reference": {
            "id": "REF_1",
            "name": "Nappa Leather Jacket",
            "url": "https://example.test/ref",
            "image": "images/REF_1.jpg",
            "association": "illustrative_category_match",
        },
    }


def stock(store, day, size, on_hand, in_transit=0, available=None):
    return ErpRecord(
        "stock",
        f"{store}-{day}-{size}",
        "v1",
        available or datetime.combine(day + timedelta(days=1), datetime.min.time(), UTC),
        "test",
        (),
        {
            "store_id": store,
            "sku": SKU,
            "size": size,
            "snapshot_date": day,
            "on_hand": on_hand,
            "in_transit": in_transit,
        },
    )


def master(table, id, data):
    return ErpRecord(table, id, "v1", MASTER, "declared_master_snapshot", (), data)


def seed(engine, *, published=True, rows=True):
    spec = RunSpec(
        run_id="run",
        scenario_id="historical",
        as_of=AS_OF,
        stores=("MIL01", "MIL02"),
        source_manifest_hash="test",
        config_hash="test",
        code_version="test",
        mode="recorded",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )
    with repo_session(engine, spec) as current:
        if published:
            current.publish()
    if not rows:
        return
    put_erp(
        engine,
        [
            stock("MIL01", date(2026, 10, 20), "00", 1),
            stock("MIL01", date(2026, 10, 20), "0", 2, in_transit=1),
            stock("MIL01", date(2026, 10, 21), "0", 9),
            stock("MIL02", date(2026, 10, 20), "0", 0, in_transit=2),
            # Another run's store, and a snapshot published after the cutoff.
            stock("NYC01", date(2026, 10, 20), "0", 5),
            stock("MIL02", date(2026, 10, 22), "0", 7, available=AS_OF + timedelta(hours=8)),
            master("assortment", "a1", {"store_id": "MIL01", "sku": SKU}),
            master("assortment", "a2", {"store_id": "MIL02", "sku": SKU}),
            master("assortment", "a3", {"store_id": "NYC01", "sku": SKU}),
            master(
                "sku_colour",
                SKU,
                {"sku": SKU, "style_code": "J20931A00012", "color_name_it": "nero"},
            ),
        ],
    )


@pytest.fixture
def service(tmp_path):
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    (catalog / "products.json").write_text(json.dumps({"products": [product()]}))
    sources = tmp_path / "sources"
    (sources / "erp/master_data").mkdir(parents=True)
    (sources / "erp/master_data/stores.csv").write_text(
        "store_id,timezone\nMIL01,Europe/Rome\nMIL02,Europe/Rome\nNYC01,America/New_York\n"
    )
    engine = connect(f"sqlite:///{tmp_path / 'products.db'}")
    settings = Settings(_env_file=None, catalog_dir=catalog, sources_dir=sources)
    with TestClient(create_app(engine=engine, settings=settings)) as client:
        yield client, engine
    engine.dispose()


def test_joins_catalog_with_one_common_stock_snapshot_inside_the_run(service):
    client, engine = service
    seed(engine)
    response = client.get("/api/runs/run/products")
    assert response.status_code == 200
    body = response.json()
    # MIL02's latest known snapshot is 10-20, so every store is shown at 10-20.
    assert body["snapshot_date"] == "2026-10-20"
    assert body["available_at"] == "2026-10-21T00:00:00Z"
    (item,) = body["products"]
    assert item["image"] == "/api/catalog/images/REF_1.jpg"
    assert item["reference"] == {"name": "Nappa Leather Jacket", "url": "https://example.test/ref"}
    black, navy = item["colours"]
    assert black["colour"] == "nero"
    assert black["stores"] == ["MIL01", "MIL02"]
    assert black["stock"] == {
        "MIL01": {"sizes": {"00": 1, "0": 2}, "in_transit": 1},
        "MIL02": {"sizes": {"0": 0}, "in_transit": 2},
    }
    assert navy == {
        "sku": "J20931A00012-742",
        "colour": "blu notte",
        "stores": [],
        "stock": {},
    }


def test_run_without_erp_stock_is_an_explicit_404(service):
    client, engine = service
    seed(engine, rows=False)
    response = client.get("/api/runs/run/products")
    assert response.status_code == 404
    assert response.json()["detail"] == "no ERP stock snapshot in this run"


def test_unpublished_run_is_a_409(service):
    client, engine = service
    seed(engine, published=False)
    assert client.get("/api/runs/run/products").status_code == 409
