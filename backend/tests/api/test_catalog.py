"""Catalog display metadata is read-only and serves only its own local images."""

import json

import pytest
from fastapi.testclient import TestClient

from tesseract.api.main import create_app
from tesseract.core.config import Settings
from tesseract.core.registry import Registry


def product(image="images/REF_1.jpg"):
    return {
        "style_code": "J20931A00012",
        "name": "AUREA",
        "category": "Outerwear",
        "subcategory": "Short down jacket",
        "price_eur": 1450.0,
        "variants": [{"sku": "J20931A00012-999", "color": "nero", "color_code": "999"}],
        "reference": {
            "id": "REF_1",
            "name": "Nappa Leather Jacket",
            "url": "https://example.test/ref",
            "image": image,
            "image_url": "https://cdn.example.test/ref.jpg",
            "price": 6900.0,
            "currency": "EUR",
            "association": "illustrative_category_match",
        },
    }


def client_for(catalog_dir):
    settings = Settings(_env_file=None, catalog_dir=catalog_dir)
    return TestClient(create_app(registry=Registry(), settings=settings))


@pytest.fixture
def catalog(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "REF_1.jpg").write_bytes(b"\xff\xd8jpeg")
    (tmp_path / "secret.jpg").write_bytes(b"outside")
    (tmp_path / "products.json").write_text(
        json.dumps({"products": [product(), product(image="../secret.jpg")]})
    )
    return tmp_path


def test_lists_products_with_local_image_urls_only(catalog):
    with client_for(catalog) as client:
        response = client.get("/api/catalog/products")
    assert response.status_code == 200
    first, second = response.json()
    assert first["name"] == "AUREA"
    assert first["variants"][0]["sku"] == "J20931A00012-999"
    assert first["reference"]["image_url"] == "/api/catalog/images/REF_1.jpg"
    assert "price" not in first["reference"] and "price_eur" not in first
    assert second["reference"]["image_url"] == "/api/catalog/images/secret.jpg"


def test_serves_only_image_files_inside_the_images_directory(catalog):
    with client_for(catalog) as client:
        assert client.get("/api/catalog/images/REF_1.jpg").content == b"\xff\xd8jpeg"
        assert client.get("/api/catalog/images/secret.jpg").status_code == 404
        assert client.get("/api/catalog/images/..%2Fsecret.jpg").status_code == 404
        assert client.get("/api/catalog/images/products.json").status_code == 404


def test_missing_catalog_is_an_explicit_404(tmp_path):
    with client_for(tmp_path) as client:
        assert client.get("/api/catalog/products").status_code == 404
