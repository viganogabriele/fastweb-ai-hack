"""Read-only display metadata from `data/catalog/`: names and local reference photos.

The catalog never feeds extraction, linking or forecasts (data/catalog/README.md). The UI
links a case to a product only by its exact style or SKU scope. The run's product view joins
it with the ERP assortment and end-of-day stock that run loaded, as known at its `as_of`.
"""

import json
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from tesseract.api.models import (
    CatalogProduct,
    RunProduct,
    RunProductCatalog,
    RunProductColour,
    RunProductReference,
    StoreStock,
)
from tesseract.api.routers.runs import PublishedRepo
from tesseract.core.config import get_settings
from tesseract.modules.sources import erp

router = APIRouter(prefix="/api/catalog")
run_router = APIRouter(prefix="/api")

IMAGE_NAME = re.compile(r"[A-Za-z0-9_-]+\.jpg")


def catalog_dir(request: Request) -> Path:
    return (request.app.state.settings or get_settings()).catalog_dir


def image_url(reference: dict) -> str | None:
    image = Path(reference["image"]).name
    return f"/api/catalog/images/{image}" if IMAGE_NAME.fullmatch(image) else None


@lru_cache(maxsize=4)
def load_raw(path: Path, mtime_ns: int) -> tuple[dict, ...]:
    return tuple(json.loads(path.read_text(encoding="utf-8"))["products"])


def catalog_file(request: Request) -> Path:
    path = catalog_dir(request) / "products.json"
    if not path.is_file():
        raise HTTPException(404, "product catalog not available")
    return path


@lru_cache(maxsize=4)
def load_products(path: Path, mtime_ns: int) -> tuple[CatalogProduct, ...]:
    products = []
    for item in load_raw(path, mtime_ns):
        reference = item["reference"]
        products.append(
            CatalogProduct(
                style_code=item["style_code"],
                name=item["name"],
                category=item["category"],
                subcategory=item["subcategory"],
                variants=item["variants"],
                reference={
                    "id": reference["id"],
                    "name": reference["name"],
                    "url": reference["url"],
                    "image_url": image_url(reference),
                    "association": reference["association"],
                },
            )
        )
    return tuple(products)


@router.get("/products", response_model=list[CatalogProduct])
def products(request: Request) -> tuple[CatalogProduct, ...]:
    path = catalog_file(request)
    return load_products(path, path.stat().st_mtime_ns)


@router.get("/images/{name}", response_class=FileResponse)
def image(request: Request, name: str) -> FileResponse:
    path = catalog_dir(request) / "images" / name
    if not IMAGE_NAME.fullmatch(name) or not path.is_file():
        raise HTTPException(404, "image not found")
    return FileResponse(
        path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"}
    )


@run_router.get("/runs/{run_id}/products", response_model=RunProductCatalog)
def run_products(request: Request, repo: PublishedRepo) -> RunProductCatalog:
    """Catalog styles with the run's assortment and stock per store, size and colour.

    Stock is one end-of-day snapshot for every store: the latest day each store has
    published by ``as_of``, taken at the earliest of those days so stores stay comparable.
    Stores outside the run and rows not yet available never appear. A run without ERP
    stock has no snapshot to show and returns 404, like a missing catalog.
    """
    path = catalog_file(request)
    sources = (request.app.state.settings or get_settings()).sources_dir
    rows = erp.read(repo, "stock", sources_dir=sources)
    latest: dict[str, object] = {}
    for row in rows:
        store, day = row.data["store_id"], row.data["snapshot_date"]
        latest[store] = max(latest.get(store, day), day)
    if not latest:
        raise HTTPException(404, "no ERP stock snapshot in this run")
    day = min(latest.values())
    stock: dict[str, dict[str, dict]] = defaultdict(dict)
    known = []
    for row in rows:
        if row.data["snapshot_date"] != day:
            continue
        known.append(row.available_at)
        entry = stock[row.data["sku"]].setdefault(
            row.data["store_id"], {"sizes": {}, "in_transit": 0}
        )
        entry["sizes"][row.data["size"]] = row.data["on_hand"] or 0
        entry["in_transit"] += row.data["in_transit"] or 0
    carried: dict[str, list[str]] = defaultdict(list)
    for row in erp.read(repo, "assortment", sources_dir=sources):
        carried[row.data["sku"]].append(row.data["store_id"])
    names = {
        row.data["sku"]: row.data["color_name_it"]
        for row in erp.read(repo, "sku_colour", sources_dir=sources)
        if row.data.get("color_name_it")
    }
    return RunProductCatalog(
        available_at=max(known),
        snapshot_date=day,
        products=tuple(
            RunProduct(
                style_code=item["style_code"],
                name=item["name"],
                category=item["category"],
                subcategory=item["subcategory"],
                gender=item.get("gender") or "",
                price_eur=item["price_eur"],
                image=image_url(item["reference"]),
                reference=RunProductReference(
                    name=item["reference"]["name"], url=item["reference"]["url"]
                ),
                colours=tuple(
                    RunProductColour(
                        sku=variant["sku"],
                        colour=names.get(variant["sku"], variant["color"]),
                        stores=tuple(sorted(carried.get(variant["sku"], ()))),
                        stock={
                            store: StoreStock(**entry)
                            for store, entry in stock.get(variant["sku"], {}).items()
                        },
                    )
                    for variant in item["variants"]
                ),
            )
            for item in load_raw(path, path.stat().st_mtime_ns)
        ),
    )
