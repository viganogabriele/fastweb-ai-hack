"""Read-only display metadata from `data/catalog/`: names and local reference photos.

The catalog never feeds extraction, linking or forecasts (data/catalog/README.md). The UI
links a case to a product only by its exact style or SKU scope.
"""

import json
import re
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from tesseract.api.models import CatalogProduct
from tesseract.core.config import get_settings

router = APIRouter(prefix="/api/catalog")

IMAGE_NAME = re.compile(r"[A-Za-z0-9_-]+\.jpg")


def catalog_dir(request: Request) -> Path:
    return (request.app.state.settings or get_settings()).catalog_dir


@lru_cache(maxsize=4)
def load_products(path: Path, mtime_ns: int) -> tuple[CatalogProduct, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    products = []
    for item in raw["products"]:
        reference = item["reference"]
        image = Path(reference["image"]).name
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
                    "image_url": f"/api/catalog/images/{image}"
                    if IMAGE_NAME.fullmatch(image)
                    else None,
                    "association": reference["association"],
                },
            )
        )
    return tuple(products)


@router.get("/products", response_model=list[CatalogProduct])
def products(request: Request) -> tuple[CatalogProduct, ...]:
    path = catalog_dir(request) / "products.json"
    if not path.is_file():
        raise HTTPException(404, "product catalog not available")
    return load_products(path, path.stat().st_mtime_ns)


@router.get("/images/{name}", response_class=FileResponse)
def image(request: Request, name: str) -> FileResponse:
    path = catalog_dir(request) / "images" / name
    if not IMAGE_NAME.fullmatch(name) or not path.is_file():
        raise HTTPException(404, "image not found")
    return FileResponse(
        path, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"}
    )
