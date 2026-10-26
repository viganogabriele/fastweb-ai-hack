"""DEMO-03: the public-bundle manifest export selects current DTOs and keeps the builder's input."""

import importlib.util
import json
import sqlite3
import sys

import pytest

from tesseract.core.config import REPO_ROOT


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = load("export_public_demo_manifest", "scripts/export_public_demo_manifest.py")
builder = load("build_public_demo", "web/scripts/build_public_demo.py")


@pytest.mark.parametrize("destination", ["outside", "symlink", "fixtures", "catalog"])
def test_private_manifest_rejects_unsafe_output_before_reading_inputs(
    tmp_path, monkeypatch, destination
):
    root = tmp_path / "repo"
    data = root / "data"
    data.mkdir(parents=True)
    (root / ".gitignore").write_text("data/*\n!data/fixtures/\n!data/catalog/\n")
    if destination == "symlink":
        outside = tmp_path / "external"
        outside.mkdir()
        (data / "escape").symlink_to(outside, target_is_directory=True)
        output = data / "escape" / "private.json"
    elif destination == "outside":
        output = root / "private.json"
    else:
        output = data / destination / "private.json"
        output.parent.mkdir()
    monkeypatch.setattr(exporter, "ROOT", root)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "export",
            "--db",
            "missing.db",
            "--run-id",
            "run",
            "--key-file",
            "missing-key",
            "--output",
            str(output),
        ],
    )
    with pytest.raises(SystemExit, match="ignored data/"):
        exporter.main()
    assert not output.exists()


def test_private_manifest_is_exclusive_and_owner_only(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    private = root / "data" / "private-demo"
    private.mkdir(parents=True)
    (root / ".gitignore").write_text("data/*\n!data/fixtures/\n!data/catalog/\n")
    key = private / "key"
    key.write_text("k" * 32)
    output = private / "manifest.json"
    monkeypatch.setattr(exporter, "ROOT", root)
    monkeypatch.setattr(
        exporter, "export", lambda *args: {"artifacts": [], "reference_key": "synthetic"}
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "export",
            "--db",
            "unused",
            "--run-id",
            "run",
            "--key-file",
            str(key),
            "--output",
            str(output),
        ],
    )
    exporter.main()
    original = output.read_bytes()
    assert output.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):
        exporter.main()
    assert output.read_bytes() == original


TEXT = "Giulia: zero cardigan in M."
DOC = {
    "id": "doc-1",
    "version": "v1",
    "text": TEXT,
    "text_version": "email-v1",
    "source_type": "email",
    "uri": "dataset://store_emails/MIL01/x.eml",
    "meta": {"store_id": "MIL01"},
}
SEG = {
    "id": "seg-1",
    "version": "v1",
    "document_id": "doc-1",
    "text_version": "email-v1",
    "text": TEXT,
    "char_start": 0,
    "char_end": len(TEXT),
}
OBS = {
    "id": "obs-1",
    "version": "v1",
    "document_id": "doc-1",
    "store_id": "MIL01",
    "kind": "stockout",
    "product_mention": "cardigan in M",
    "quantity": {"kind": "exact", "value": 0.0, "unit": "units"},
    "evidence": [
        {
            "document_id": "doc-1",
            "document_version": "v1",
            "segment_id": "seg-1",
            "quote": "zero cardigan in M",
            "char_start": 8,
            "char_end": 26,
        }
    ],
}


def case(version, status):
    return {
        "id": "case-1",
        "version": version,
        "store_id": "MIL01",
        "case_type": "unmet_demand",
        "status": status,
        "priority": "high",
        "priority_reason": "Store reports stockout.",
        "owner": "allocation",
        "supporting": [{"kind": "Observation", "id": "obs-1", "version": "v1"}],
        "contradicting": [],
        "context_refs": [
            {"kind": "EntityLink", "id": "link-1", "version": "abc"},
            {"kind": "Observation", "id": "obs-1", "version": "v1"},
        ],
    }


def test_export_feeds_the_existing_builder(tmp_path, monkeypatch):
    db = tmp_path / "t.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE artifacts (seq INTEGER, run_id TEXT, kind TEXT, id TEXT, payload)")
    rows = [
        ("Case", case("v1", "verify")),
        ("SourceDocument", DOC),
        ("Segment", SEG),
        ("Observation", OBS),
        ("EntityLink", {"id": "link-1", "version": "abc"}),
        ("Case", case("v2", "open")),
    ]
    for seq, (kind, payload) in enumerate(rows):
        con.execute(
            "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?)",
            (seq, "run", kind, payload["id"], json.dumps(payload)),
        )
    con.execute(
        "INSERT INTO artifacts VALUES (9, 'other', 'Case', 'case-x', ?)",
        (json.dumps(case("v1", "open") | {"id": "case-x"}),),
    )
    con.commit()
    replacements = tmp_path / "replacements.json"
    replacements.write_text(json.dumps({"Giulia": "Elena"}))
    monkeypatch.setattr(exporter, "REPLACEMENTS", replacements)

    manifest = exporter.export(db, "run", "k" * 32, approved=True)

    assert [(a["kind"], a["payload"]["id"]) for a in manifest["artifacts"]] == [
        ("SourceDocument", "doc-1"),
        ("Segment", "seg-1"),
        ("Observation", "obs-1"),
        ("Case", "case-1"),
    ]
    exported_case = manifest["artifacts"][-1]["payload"]
    assert exported_case["version"] == "v2"
    assert exported_case["context_refs"] == [
        {"kind": "Observation", "id": "obs-1", "version": "v1"}
    ]
    assert manifest["artifacts"][0]["payload"]["text"] == TEXT

    files, _ = builder.Builder(manifest, list(exporter.STORES)).build()
    public = json.loads(files["artifacts.json"])
    assert {item["kind"] for item in public} == {"SourceDocument", "Segment", "Observation", "Case"}
    document = next(item["payload"] for item in public if item["kind"] == "SourceDocument")
    observation = next(item["payload"] for item in public if item["kind"] == "Observation")
    evidence = observation["evidence"][0]
    assert document["text"] == "Elena: zero cardigan in M."
    assert document["text"][evidence["char_start"] : evidence["char_end"]] == evidence["quote"]
    assert json.loads(files["manifest.json"])["excluded"] == []


def test_export_rejects_a_run_without_artifacts(tmp_path):
    db = tmp_path / "empty.db"
    with sqlite3.connect(db) as con:
        con.execute(
            "CREATE TABLE artifacts (seq INTEGER, run_id TEXT, kind TEXT, id TEXT, payload)"
        )
    with pytest.raises(ValueError, match="no public artifacts"):
        exporter.export(db, "wrong-run", "k" * 32, approved=True)
