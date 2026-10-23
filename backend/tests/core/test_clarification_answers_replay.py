"""OUT-02e: real-model recorded (not fixture) answer follow-ups replay offline over HTTP.

The envelopes are actual Fastweb/mock-system responses recorded on the dev Core
demo question. Synthetic responses elsewhere test guards; this tests comprehension
as recorded and exact offline reproducibility of answer -> document -> new run.
"""

import hashlib
import importlib.util
import json

from tesseract.core.cache import ResponseCache
from tesseract.core.config import REPO_ROOT

module_spec = importlib.util.spec_from_file_location(
    "clarification_answers_demo", REPO_ROOT / "scripts/clarification_answers_demo.py"
)
demo = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(demo)

ANSWERS = demo.ANSWERS
TARGET = "obs-20261009-1035-mil01-1"


def test_recorded_answer_envelopes_are_complete_and_bound_to_their_evidence():
    evidence = json.loads((ANSWERS / "recording-evidence.json").read_text())
    inventory = json.loads((ANSWERS / "asset-manifest.json").read_text())
    for relative, expected in inventory["files"]:
        assert hashlib.sha256((ANSWERS / relative).read_bytes()).hexdigest() == expected
    assert evidence["complete"] is True
    assert evidence["parent"]["artifact_sha256"] == evidence["parent"]["artifact_sha256_after"]
    recorded = {key for answer in evidence["answers"].values() for key in answer["llm_keys"]}
    cache = ResponseCache(ANSWERS / "llm_cache")
    stored = {path.stem for path in cache.directory.rglob("*.json")}
    assert stored == recorded  # every envelope is used, none is missing
    for key in stored:
        cache.get(key)  # key, checksum and schema, without a provider client
    # Every envelope was produced by a real provider call in a recording session.
    sessions = [evidence]
    if (ANSWERS / "recording-evidence-initial.json").exists():
        sessions.append(json.loads((ANSWERS / "recording-evidence-initial.json").read_text()))
    real = {
        t["key"]
        for session in sessions
        for answer in session["answers"].values()
        for t in answer["llm_traces"]
        if not t.get("cache_hit") and t["status"] == 200
    }
    assert stored <= real


def test_recorded_answers_replay_offline_through_the_answer_api(tmp_path):
    result = demo.replay(tmp_path / "replay")
    evidence = json.loads((ANSWERS / "recording-evidence.json").read_text())
    assert result["status"] == "passed", result
    assert result["network_attempts"] == 0
    assert result["cache_misses"] == result["systems_cache_misses"] == []
    # The published historical parent is byte-for-byte the recorded one, before and after.
    assert (
        result["parent"]["artifact_sha256"]
        == result["parent"]["artifact_sha256_after"]
        == evidence["parent"]["artifact_sha256"]
    )
    assert set(result["answers"]) == {"self-contained", "elliptical", "abstain"}
    for key, answer in result["answers"].items():
        assert answer["http_status"] == 202 and answer["retry_same_job"]
        assert answer["published"] and answer["matches_recording"], key
        assert answer["fingerprint"] == evidence["answers"][key]["fingerprint"]
        # One current demand for the clarified observation; the reply adds none.
        assert answer["duplicate_current_observation_ids"] == []
        assert answer["answer_document_observations"] == 0
        (corrected,) = [c for c in answer["corrected"] if c["observation_id"] == TARGET]
        assert corrected["quantity_raw"] == "1 o 2 pezzi per colore"
        assert corrected["available_at"] == "2026-10-22T20:20:00+00:00"
        assert answer["supersedes"] >= 1
    readings = {k: a["corrected"][0]["product_mention"] for k, a in result["answers"].items()}
    # Recorded real-model comprehension of the two clarifying answers and the abstention.
    for key in ("self-contained", "elliptical"):
        assert {"cardigan", "logo"} <= set(readings[key].casefold().split()), readings
    assert readings["abstain"] == "M"
    negative = result["negative"]
    assert negative["free_text_status"] == 424
    assert negative["unrecorded_clock_status"] == 202
    assert not negative["unrecorded_clock_published"]
    assert negative["unrecorded_clock_misses"] > 0
