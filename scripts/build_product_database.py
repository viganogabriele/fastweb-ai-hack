"""Build the offline SQLite/CSV product dataset; no web app or API changes.

Inputs: official public product snapshot, synthetic ERP catalog, existing dev fixtures.
The demo cases are explicitly fixture data, separate from official product metadata.
"""

import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
FIXTURES = ROOT / "data/fixtures"

SCHEMA = """
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE reference_products (
    reference_id TEXT PRIMARY KEY,
    name TEXT NOT NULL, source_url TEXT NOT NULL,
    price REAL NOT NULL, currency TEXT NOT NULL, image_urls_json TEXT NOT NULL
);
CREATE TABLE products (
    style_code TEXT PRIMARY KEY, name TEXT NOT NULL,
    category TEXT NOT NULL, subcategory TEXT NOT NULL, gender TEXT NOT NULL,
    season TEXT NOT NULL, launch_date TEXT, end_date TEXT, synthetic_price_eur REAL NOT NULL
);
CREATE TABLE variants (
    sku TEXT PRIMARY KEY, style_code TEXT NOT NULL REFERENCES products,
    color_code TEXT NOT NULL, color TEXT NOT NULL
);
CREATE TABLE visual_references (
    style_code TEXT PRIMARY KEY REFERENCES products,
    reference_id TEXT NOT NULL REFERENCES reference_products,
    local_image TEXT NOT NULL,
    association TEXT NOT NULL CHECK (association = 'illustrative_category_match')
);
CREATE TABLE demo_cases (
    case_id TEXT PRIMARY KEY, mode TEXT NOT NULL CHECK (mode = 'fixture'),
    store_id TEXT, scope_level TEXT NOT NULL, scope_id TEXT,
    priority TEXT NOT NULL, status TEXT NOT NULL, case_type TEXT NOT NULL,
    priority_reason TEXT NOT NULL, payload_json TEXT NOT NULL
);
CREATE TABLE demo_case_products (
    case_id TEXT NOT NULL REFERENCES demo_cases,
    style_code TEXT NOT NULL REFERENCES products,
    PRIMARY KEY (case_id, style_code)
);
CREATE TABLE demo_observations (
    observation_id TEXT PRIMARY KEY, payload_json TEXT NOT NULL
);
CREATE TABLE demo_documents (
    document_id TEXT PRIMARY KEY, payload_json TEXT NOT NULL
);
CREATE VIEW product_cards AS
SELECT p.*, r.reference_id, r.name AS reference_name, r.source_url,
       v.local_image, v.association,
       (SELECT COUNT(*) FROM variants s WHERE s.style_code = p.style_code) AS color_count,
       (SELECT COUNT(*) FROM demo_case_products c WHERE c.style_code = p.style_code)
           AS demo_case_count
FROM products p JOIN visual_references v USING (style_code)
JOIN reference_products r USING (reference_id);
"""


def fixture_records(folder: str, kind: str) -> list[dict]:
    return [
        row["payload"]
        for path in sorted((FIXTURES / folder).glob("*.json"))
        for row in json.loads(path.read_text())
        if row["kind"] == kind
    ]


def case_matches(case: dict, product: dict) -> bool:
    scope, key = case["scope_level"], case["scope_id"]
    if scope == "style":
        return key == product["style_code"]
    if scope == "sku":
        return any(v["sku"] == key for v in product["variants"])
    if scope == "sku_size" and key:
        return any(key.startswith(v["sku"] + "-") for v in product["variants"])
    return False


def build() -> None:
    snapshot = json.loads((ROOT / "generated/sources/external/catalog/valentino.json").read_text())
    catalog = json.loads((CATALOG / "products.json").read_text())
    cases = fixture_records("cases", "Case")
    documents = fixture_records("documents", "SourceDocument")
    observations = fixture_records("observations", "Observation")
    temporary = CATALOG / "products.sqlite.tmp"
    temporary.unlink(missing_ok=True)
    with sqlite3.connect(temporary) as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript(SCHEMA)
        db.executemany(
            "INSERT INTO metadata VALUES (?, ?)",
            [
                ("brand", "Valentino"),
                ("retrieved_at", snapshot["retrieved_at"]),
                ("signals_mode", "fixture"),
                (
                    "disclosure",
                    "Official images are illustrative; SKU, prices and cases are synthetic.",
                ),
            ],
        )
        db.executemany(
            "INSERT INTO reference_products VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    p["id"],
                    p["name"],
                    p["url"],
                    p["price"],
                    p["currency"],
                    json.dumps(p["image_urls"]),
                )
                for p in snapshot["products"]
            ],
        )
        for p in catalog["products"]:
            db.execute(
                "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    p["style_code"],
                    p["name"],
                    p["category"],
                    p["subcategory"],
                    p["gender"],
                    p["season"],
                    p["launch_date"],
                    p["end_date"],
                    p["price_eur"],
                ),
            )
            db.executemany(
                "INSERT INTO variants VALUES (?, ?, ?, ?)",
                [(v["sku"], p["style_code"], v["color_code"], v["color"]) for v in p["variants"]],
            )
            ref = p["reference"]
            db.execute(
                "INSERT INTO visual_references VALUES (?, ?, ?, ?)",
                (
                    p["style_code"],
                    ref["id"],
                    ref["image"],
                    ref["association"],
                ),
            )
        for case in cases:
            db.execute(
                "INSERT INTO demo_cases VALUES (?, 'fixture', ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    case["id"],
                    case["store_id"],
                    case["scope_level"],
                    case["scope_id"],
                    case["priority"],
                    case["status"],
                    case["case_type"],
                    case["priority_reason"],
                    json.dumps(case, ensure_ascii=False),
                ),
            )
            db.executemany(
                "INSERT INTO demo_case_products VALUES (?, ?)",
                [
                    (case["id"], p["style_code"])
                    for p in catalog["products"]
                    if case_matches(case, p)
                ],
            )
        db.executemany(
            "INSERT INTO demo_observations VALUES (?, ?)",
            [(o["id"], json.dumps(o, ensure_ascii=False)) for o in observations],
        )
        db.executemany(
            "INSERT INTO demo_documents VALUES (?, ?)",
            [(d["id"], json.dumps(d, ensure_ascii=False)) for d in documents],
        )
        assert not db.execute("PRAGMA foreign_key_check").fetchall()
    temporary.replace(CATALOG / "products.sqlite")
    with (CATALOG / "sku_references.csv").open("w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(
            [
                "sku",
                "style_code",
                "name",
                "reference_id",
                "reference_name",
                "local_image",
                "source_url",
                "association",
            ]
        )
        for p in catalog["products"]:
            ref = p["reference"]
            for v in p["variants"]:
                writer.writerow(
                    [
                        v["sku"],
                        p["style_code"],
                        p["name"],
                        ref["id"],
                        ref["name"],
                        ref["image"],
                        ref["url"],
                        ref["association"],
                    ]
                )
    signals = {
        "mode": "fixture",
        "scenario_id": "historical",
        "source": "Existing source-derived dev fixtures, not real Valentino customer reports",
        "cases": cases,
        "documents": documents,
        "observations": observations,
        "product_links": [
            {"case_id": c["id"], "style_code": p["style_code"]}
            for c in cases
            for p in catalog["products"]
            if case_matches(c, p)
        ],
    }
    (CATALOG / "demo_signals.json").write_text(
        json.dumps(signals, ensure_ascii=False, indent=2) + "\n"
    )
    print(f"Built SQLite, SKU crosswalk and {len(cases)} explicitly synthetic demo cases")


if __name__ == "__main__":
    build()
