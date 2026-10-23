"""Portable real recordings stay bound to their exact dev inputs and provider responses."""

import hashlib
import json

from tesseract.core.cache import ResponseCache, cache_key
from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import RunSpec
from tesseract.core.fixtures import read_fixtures

ASSETS = REPO_ROOT / "data/fixtures/runs/core-dev-20261023"


def test_source_backed_recordings_have_complete_versioned_inventory():
    inventory = json.loads((ASSETS / "asset-manifest.json").read_text())
    for relative, expected in inventory["files"]:
        path = ASSETS / relative
        assert path.is_relative_to(ASSETS)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, relative
    for name, count in (("llm_cache", 20), ("systems_cache", 12), ("investigate-job/llm_cache", 6)):
        cache = ResponseCache(ASSETS / name)
        paths = list(cache.directory.rglob("*.json"))
        assert len(paths) == count
        for path in paths:
            cache.get(path.stem)  # Envelope key/checksum/schema, without a provider client.
    evidence = json.loads((ASSETS / "recording-evidence.json").read_text())
    assert (
        evidence["complete"] and evidence["execution_sha"] == evidence["snapshot"]["code_version"]
    )
    assert all(not item["result"]["errors"] for item in evidence["modules"])
    assert all(t.get("status") == 200 or t.get("cache_hit") for t in evidence["llm_traces"])


def test_frozen_source_and_configuration_hashes_match_the_committed_inputs():
    spec = RunSpec.model_validate_json((ASSETS / "run-spec.json").read_text())
    assert spec.mode == "recorded" and spec.authorized_fixture_refs == ()
    inventory = json.loads((ASSETS / "input-manifest.json").read_text())
    for name, root, expected in (
        ("sources", REPO_ROOT / "generated/sources", spec.source_manifest_hash),
        ("config", REPO_ROOT / "config", spec.config_hash),
    ):
        entries = inventory[name]
        assert cache_key(entries) == expected
        for relative, sha in entries:
            assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == sha, relative
    # Recording assets are not DTO fixture input and must not be preloaded as projections.
    fixture_paths, _ = read_fixtures(REPO_ROOT / "data/fixtures")
    assert not any(p.is_relative_to(ASSETS) for p in fixture_paths)


def test_investigate_job_and_corrections_are_bound_to_this_candidate():
    spec = RunSpec.model_validate_json((ASSETS / "run-spec.json").read_text())
    snapshot = cache_key(spec.model_dump(mode="json"))
    api = json.loads((ASSETS / "api-verification.json").read_text())
    assert api["snapshot_sha256"] == snapshot and api["status"] == "passed"
    # Source-backed resend and correction emails yield certain, applied relations.
    assert api["evidence_relation_counts"]["duplicates"] >= 1
    assert api["evidence_relation_counts"]["supersedes"] >= 1
    job = json.loads((ASSETS / "investigate-job/manifest.json").read_text())
    assert job["parent"]["snapshot_sha256"] == snapshot
    assert job["parent"]["artifact_inventory_sha256"] == api["artifact_inventory_sha256"]
    assert job["parent"]["code_version"] == spec.code_version
    for name, entries in job["recordings"].items():
        directory = ASSETS / "investigate-job" / name
        found = sorted(
            [p.stem, hashlib.sha256(p.read_bytes()).hexdigest()] for p in directory.rglob("*.json")
        )
        assert found == entries, name
    verification = json.loads((ASSETS / "api-job-verification.json").read_text())
    assert verification["status"] == "passed" and verification["job_id"] == job["job"]["run_id"]
    for attempt in verification["positive_offline_replays"]:
        assert attempt["status"] == "passed" and attempt["network_attempts"] == 0
        assert all(attempt["checks"].values())
    negative = verification["negative_withheld_job_envelope"]
    assert negative["job_status"] == "failed" and not negative["job_published"]
