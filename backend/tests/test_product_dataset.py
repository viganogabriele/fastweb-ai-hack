"""Integrity of the offline visual dataset and its explicitly synthetic case joins."""

import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data/catalog"


def test_catalog_covers_exactly_the_erp_skus_with_local_images():
    catalog = json.loads((CATALOG / "products.json").read_text())
    snapshot = json.loads((ROOT / "generated/sources/external/catalog/valentino.json").read_text())
    references = {p["id"]: p for p in snapshot["products"]}
    master = ROOT / "generated/sources/erp/master_data"
    with (master / "sku_colour.csv").open() as source:
        expected = {row["sku"]: row for row in csv.DictReader(source)}
    actual = {}
    for product in catalog["products"]:
        reference = product["reference"]
        assert reference["association"] == "illustrative_category_match"
        assert reference["url"] == references[reference["id"]]["url"]
        assert reference["url"].startswith("https://www.valentino.com/")
        image = (CATALOG / reference["image"]).resolve()
        assert image.is_relative_to(CATALOG)
        assert image.read_bytes().startswith(b"\xff\xd8\xff")
        for variant in product["variants"]:
            sku = variant["sku"]
            assert sku not in actual
            actual[sku] = variant
            assert product["style_code"] == expected[sku]["style_code"]
            assert product["name"] == expected[sku]["style_name"]
            assert variant["color_code"] == expected[sku]["color_code"]
            assert product["price_eur"] == float(expected[sku]["price_eur"])
    assert actual.keys() == expected.keys()
    assert catalog["official_product_count"] == len(references)


def test_sqlite_json_and_csv_agree_without_assigning_unknown_cases():
    signals = json.loads((CATALOG / "demo_signals.json").read_text())
    catalog = json.loads((CATALOG / "products.json").read_text())
    with (CATALOG / "sku_references.csv").open() as source:
        crosswalk = list(csv.DictReader(source))
    with sqlite3.connect(f"file:{CATALOG / 'products.sqlite'}?mode=ro", uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        assert db.execute("SELECT COUNT(*) FROM product_cards").fetchone()[0] == len(
            catalog["products"]
        )
        assert db.execute("SELECT COUNT(*) FROM variants").fetchone()[0] == len(crosswalk)
        assert db.execute("SELECT COUNT(*) FROM demo_cases").fetchone()[0] == len(signals["cases"])
        assert db.execute("SELECT DISTINCT mode FROM demo_cases").fetchall() == [("fixture",)]
        assert not db.execute("""
            SELECT p.case_id FROM demo_case_products p JOIN demo_cases c USING (case_id)
            WHERE c.scope_level IN ('unknown', 'category', 'store')
        """).fetchall()
        known = {p["style_code"]: p for p in catalog["products"]}
        for case_id, code in db.execute("SELECT case_id, style_code FROM demo_case_products"):
            case = next(c for c in signals["cases"] if c["id"] == case_id)
            if case["scope_level"] == "style":
                assert code == case["scope_id"]
            else:
                assert any(
                    case["scope_id"] == v["sku"] or case["scope_id"].startswith(v["sku"] + "-")
                    for v in known[code]["variants"]
                )


def test_demo_quotes_match_the_rebranded_documents():
    signals = json.loads((CATALOG / "demo_signals.json").read_text())
    documents = {d["id"]: d for d in signals["documents"]}
    for observation in signals["observations"]:
        for evidence in observation["evidence"]:
            document = documents[evidence["document_id"]]
            assert (
                document["text"][evidence["char_start"] : evidence["char_end"]] == evidence["quote"]
            )
