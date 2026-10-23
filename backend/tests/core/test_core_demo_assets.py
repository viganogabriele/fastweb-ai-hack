"""Portable real recordings stay bound to their exact dev inputs and provider responses."""

import hashlib
import json

from tesseract.core.cache import ResponseCache, cache_key
from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import RunSpec
from tesseract.core.fixtures import read_fixtures
from tesseract.modules.actions.approval import DecisionRequest, LocalDraft

ASSETS = REPO_ROOT / "data/fixtures/runs/core-dev-20261023"


def test_source_backed_recordings_have_complete_versioned_inventory():
    inventory = json.loads((ASSETS / "asset-manifest.json").read_text())
    for relative, expected in inventory["files"]:
        path = ASSETS / relative
        assert path.is_relative_to(ASSETS)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, relative
    for name, count in (
        ("llm_cache", 21),
        ("systems_cache", 12),
        ("investigate-job/llm_cache", 6),
        ("investigate-job/systems_cache", 1),
    ):
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


def test_operator_decision_is_a_human_rejection_that_replays_on_this_candidate():
    spec = RunSpec.model_validate_json((ASSETS / "run-spec.json").read_text())
    snapshot = cache_key(spec.model_dump(mode="json"))
    raw = (ASSETS / "decisions-operator.json").read_bytes()
    [event] = json.loads(raw)
    assert (event["namespace"], event["snapshot_sha256"]) == ("product", snapshot)
    request = DecisionRequest.model_validate(event["request"])
    draft = LocalDraft.model_validate(event["draft"])
    # A genuine operator, not the scripted reviewer in decisions.json, which stays as is.
    assert request.by == draft.decision.by == "lorenzocorallo"
    assert (request.decision, request.option_id) == (
        "rejected",
        "opt-case-mil01-i10919b00011-20261008-transfer",
    )
    assert event["at"] == draft.decision.model_dump(mode="json")["at"]
    assert draft.decision.at.isoformat().startswith("2026-10-23")
    assert draft.decision.at < draft.option.valid_until
    assert draft.option.input_version_hash == request.input_version_hash
    assert draft.decision.dispatch_status == "draft" and draft.simulated
    assert draft.reservations == ()
    synthetic = json.loads((ASSETS / "decisions.json").read_text())
    assert [e["request"]["by"] for e in synthetic] == ["DEMO-02 scripted synthetic reviewer"]
    # Two cold replays with --decisions decisions-operator.json kept the exact draft.
    replays = json.loads((ASSETS / "operator-decision-replay.json").read_text())
    assert replays["decisions_sha256"] == hashlib.sha256(raw).hexdigest()
    assert replays["snapshot_sha256"] == snapshot and replays["exit_codes"] == [0, 0]
    assert replays["network_attempts"] == [0, 0]
    for key in ("decisions", "inputs", "output_sha256", "ledger_sha256", "exact_ids_and_versions"):
        assert replays[f"{key}_equal"] is True, key
    assert replays["raw_payload_differences"] == ["AgentTrace"]
    [saved] = replays["decisions"]
    assert saved["id"] == draft.decision.id
    assert saved["sha256"] == cache_key(draft.model_dump(mode="json"))
