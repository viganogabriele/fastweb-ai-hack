"""The dashboard demo packages provider envelopes, never fabricated projections."""

import hashlib
import json

import yaml

from tesseract.core.cache import ResponseCache, cache_key
from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import RunSpec

ASSETS = REPO_ROOT / "data/fixtures/runs/production-demo-20261022"


def test_production_package_has_exact_inventory_and_real_envelopes():
    inventory = json.loads((ASSETS / "asset-manifest.json").read_text())
    for relative, sha in inventory["files"]:
        path = ASSETS / relative
        assert path.is_relative_to(ASSETS)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == sha
    for folder in ("llm_cache", "systems_cache"):
        cache = ResponseCache(ASSETS / folder)
        paths = list(cache.directory.rglob("*.json"))
        assert paths
        for path in paths:
            cache.get(path.stem)


def test_production_snapshot_and_checks_cover_the_dashboard_without_holdout_data():
    spec = RunSpec.model_validate_json((ASSETS / "run-spec.json").read_text())
    profile = yaml.safe_load((ASSETS / "profile.yaml").read_text())
    split = yaml.safe_load((REPO_ROOT / "config/eval_split.yaml").read_text())
    assert set(spec.stores) <= set(split["dev"])
    assert spec.mode == "recorded" and not spec.authorized_fixture_refs
    assert profile == yaml.safe_load((REPO_ROOT / "config/production_demo.yaml").read_text())
    manifest = json.loads((ASSETS / "input-manifest.json").read_text())
    assert cache_key(manifest["sources"]) == spec.source_manifest_hash
    assert cache_key(manifest["config"]) == spec.config_hash
    record = json.loads((ASSETS / "recording-evidence.json").read_text())
    assert record["published"] and record["execution_sha"] == spec.code_version
    assert all(not m["result"]["errors"] for m in record["modules"])
    api = json.loads((ASSETS / "api-verification.json").read_text())
    assert api["status"] == "passed" and api["verified_quotes"] == api["observations"]
    assert api["network_attempts"] == 0
    assert api["dashboard"]["forecast_computed"] >= 1
    assert api["dashboard"]["cases_with_deduplicated_origins"] >= 1
    assert api["dashboard"]["monthly_points"] == 12
    replay = json.loads((ASSETS / "replay-comparison.json").read_text())
    assert replay["record_output_sha256"] == replay["replays"][0]["output_sha256"]
    assert len({r["output_sha256"] for r in replay["replays"]}) == 1
    assert all(r["network_attempts"] == 0 and not r["cache_misses"] for r in replay["replays"])
