"""Import official product metadata, then build the dashboard's offline visual catalog.

Run with --fetch to refresh the public snapshot and download reference images.
Without --fetch, rebuilding from the committed snapshot needs no network.
Commercial references are presentation metadata, never historical demand evidence.
"""

import argparse
import csv
import json
import re
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "generated/sources/external/catalog/valentino.json"
MASTER = ROOT / "generated/sources/erp/master_data"
OUTPUT = ROOT / "data/catalog/products.json"
IMAGES = ROOT / "data/catalog/images"
BASE = "https://www.valentino.com/en-it/"
COLLECTIONS = {
    "outerwear-w": "women/ready-to-wear/coats-and-outerwear",
    "outerwear-m": "men/ready-to-wear/outerwear",
    "knitwear-w": "women/ready-to-wear/knitwear",
    "knitwear-m": "men/ready-to-wear/knitwear",
    "jersey": "men/ready-to-wear/t-shirts-and-sweatshirts",
    "bottoms": "men/ready-to-wear/pants-and-shorts",
    "footwear-w": "women/shoes/sneakers",
    "footwear-m": "men/shoes/sneakers",
    "accessories": "men/accessories/hats-and-gloves",
    "scarves": "women/accessories/soft-accessories",
    "bags": "men/bags",
}


def download(url: str) -> tuple[bytes, str]:
    request = Request(quote(url, safe=":/?&=%"), headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=45) as response:
        return response.read(), response.headers.get_content_type()


def listing_products(html: str) -> list[dict]:
    products = {}
    for block in re.findall(
        r"<script[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>(.*?)</script>",
        html,
        re.DOTALL,
    ):
        document = json.loads(block)
        if document.get("@type") != "ItemList":
            continue
        for entry in document["itemListElement"]:
            product = entry["item"]
            if product.get("@type") == "Product":
                sku = product.get("sku") or product["url"].rsplit("-", 1)[-1]
                products[sku] = {**product, "sku": sku}
    if not products:
        raise ValueError("Official collection did not expose a JSON-LD product list")
    return list(products.values())


def fetch_snapshot() -> dict:
    products = {}
    for collection, path in COLLECTIONS.items():
        url = BASE + path
        content, _ = download(url)
        for product in listing_products(content.decode("utf-8")):
            sku = product["sku"]
            if sku not in products:
                offer = product["offers"]
                products[sku] = {
                    "id": sku,
                    "name": unescape(re.sub(r"\s*\([^()]+\)$", "", product["name"])).strip(),
                    "url": product["url"],
                    "image_urls": product["image"],
                    "price": float(offer["price"]),
                    "currency": offer["priceCurrency"],
                    "collections": [],
                }
            products[sku]["collections"].append(collection)
        print(f"Imported {collection}", flush=True)
    snapshot = {
        "brand": "Valentino",
        "retrieved_at": datetime.now(UTC).isoformat(),
        "source": "Official Valentino public collection JSON-LD",
        "usage": "Visual references only. Synthetic SKU associations are illustrative.",
        "collections": {key: BASE + path for key, path in COLLECTIONS.items()},
        "products": list(products.values()),
    }
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    return snapshot


def collection_for(style: dict) -> str:
    category = style["category"].lower()
    gender = "w" if style["gender"] == "W" else "m"
    if category in {"outerwear", "knitwear", "footwear"}:
        return f"{category}-{gender}"
    if "SCARF" in style["style_name"].upper():
        return "scarves"
    if any(term in style["subcategory"].lower() for term in ("bag", "backpack")):
        return "bags"
    return category


def build_catalog(snapshot: dict, fetch_images: bool) -> None:
    styles = list(csv.DictReader((MASTER / "styles.csv").open()))
    variants = list(csv.DictReader((MASTER / "sku_colour.csv").open()))
    # Preserve the explicit associations across later refreshes; never remap a SKU silently.
    previous = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {"products": []}
    references = {p["style_code"]: p["reference"]["id"] for p in previous["products"]}
    by_id = {p["id"]: p for p in snapshot["products"]}
    used_names = set()
    catalog = []
    for style in styles:
        collection = collection_for(style)
        if style["style_code"] in references:
            reference = by_id[references[style["style_code"]]]
        else:
            candidates = [p for p in by_id.values() if collection in p["collections"]]
            reference = next(p for p in candidates if p["name"] not in used_names)
        used_names.add(reference["name"])
        image = IMAGES / f"{reference['id']}.jpg"
        if fetch_images and not image.exists():
            url = reference["image_urls"][0].replace("format=auto", "format=jpg")
            data, mime = download(url)
            if mime != "image/jpeg":
                raise ValueError(f"Expected JPEG from official image CDN, got {mime}")
            image.parent.mkdir(parents=True, exist_ok=True)
            image.write_bytes(data)
        if not image.exists():
            raise FileNotFoundError(f"Missing reference image: {image.name}; run with --fetch")
        catalog.append(
            {
                "style_code": style["style_code"],
                "name": style["style_name"],
                "category": style["category"],
                "subcategory": style["subcategory"],
                "gender": style["gender"],
                "season": style["season"],
                "launch_date": style["launch_date"] or None,
                "end_date": style["end_date"] or None,
                "price_eur": float(style["price_eur"]),
                "variants": [
                    {
                        "sku": v["sku"],
                        "color": v["color_name_it"],
                        "color_code": v["color_code"],
                    }
                    for v in variants
                    if v["style_code"] == style["style_code"]
                ],
                "reference": {
                    "id": reference["id"],
                    "name": reference["name"],
                    "url": reference["url"],
                    "image": f"images/{image.name}",
                    "image_url": reference["image_urls"][0],
                    "price": reference["price"],
                    "currency": reference["currency"],
                    "association": "illustrative_category_match",
                },
            }
        )
    result = {
        "brand": "Valentino",
        "retrieved_at": snapshot["retrieved_at"],
        "source": snapshot["source"],
        "official_product_count": len(by_id),
        "products": catalog,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"Built {len(catalog)} styles / {len(variants)} synthetic SKUs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Refresh from the official website")
    parser.add_argument("--download-images", action="store_true", help="Download snapshot images")
    args = parser.parse_args()
    snapshot = fetch_snapshot() if args.fetch else json.loads(SNAPSHOT.read_text())
    build_catalog(snapshot, fetch_images=args.fetch or args.download_images)
