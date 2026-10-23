"""Export an explicit public-bundle input manifest from a replayed demo database (DEMO-03).

Selection only: no text is changed here. Sanitising stays in
`web/scripts/build_public_demo.py`. The output holds original synthetic text, so it is a
private file under ignored `data/` and is never distributed. The reviewed replacement
dictionary is `docs/demo_bundle/replacements.json`; the reference key is read from a
private file and never printed.

Run from the repository root:

    backend/.venv/bin/python scripts/export_public_demo_manifest.py \
      --db data/demo/current/data/tesseract.db --run-id core-dev-candidate \
      --key-file data/private-demo/reference_key --output data/private-demo/approved-demo.json
"""

import argparse
import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLACEMENTS = ROOT / "docs/demo_bundle/replacements.json"
STORES = ("MIL01", "MIL02", "MUN01", "NYC01")
# Kinds the builder projects, in its processing order.
KINDS = ("SourceDocument", "Segment", "Observation", "Case", "Report")


def export(db, run_id, key, approved):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT kind, id, payload FROM artifacts WHERE run_id = ? AND kind IN (?, ?, ?, ?, ?) "
        "ORDER BY seq",
        (run_id, *KINDS),
    ).fetchall()
    # Current version only: a later row of the same kind/id supersedes an earlier one.
    current = {}
    for kind, artifact_id, payload in rows:
        current[(kind, artifact_id)] = json.loads(payload)
    artifacts = []
    for (kind, _), payload in sorted(current.items(), key=lambda i: (KINDS.index(i[0][0]), i[0])):
        if kind == "Case":
            # EntityLink/EvidenceRelation/ContextEvent are not part of the public projection;
            # keeping them would exclude every case as a dangling reference.
            payload["context_refs"] = [
                ref for ref in payload.get("context_refs", []) if ref["kind"] in KINDS
            ]
        artifacts.append({"kind": kind, "payload": payload})
    return {
        "version": 1,
        "approved": approved,
        "split": "dev",
        "stores": list(STORES),
        "reference_key": key,
        "replacements": json.loads(REPLACEMENTS.read_text(encoding="utf-8")),
        "artifacts": artifacts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--key-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--approved",
        action="store_true",
        help="record that the selection and replacements were reviewed",
    )
    args = parser.parse_args()
    key = args.key_file.read_text(encoding="utf-8").strip()
    if len(key) < 32:
        raise SystemExit("reference key must have at least 32 characters")
    manifest = export(args.db, args.run_id, key, args.approved)
    with open(
        args.output, "x", encoding="utf-8", opener=lambda p, f: os.open(p, f, 0o600)
    ) as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=1)
    counts = {}
    for item in manifest["artifacts"]:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1
    print(json.dumps({"output": str(args.output), "artifacts": counts}))


if __name__ == "__main__":
    main()
