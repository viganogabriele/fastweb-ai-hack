"""Offline replay boundaries, without real credentials or external network access."""

import hashlib
import importlib.util
import json
import logging
import socket
import subprocess
import sys
from datetime import timedelta

import httpx
import pytest
from sqlalchemy import inspect, select

from tessera.core.config import REPO_ROOT
from tessera.core.contracts import (
    ActionOption,
    ArtifactRef,
    ModuleManifest,
    ModuleResult,
    ModuleSnapshot,
    RunSpec,
    SourceDocument,
)
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.systems_cache import SystemsCache, SystemsTransport
from tessera.modules.actions import approval, ledger
from tessera.modules.sources import emails, voice
from tessera.modules.sources.systems_client import Crosswalk
from tests.modules.actions.test_options import fixture_case

module_spec = importlib.util.spec_from_file_location(
    "replay_demo", REPO_ROOT / "scripts/replay_demo.py"
)
replay = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(replay)

FIXTURE_FILES = {
    "erp/master_data/stores.csv": "store_id,language,timezone,currency\nMIL01,it,Europe/Rome,EUR\n",
    "store_emails/MIL01/message.eml": (
        "From: example@example.test\nTo: demo@example.test\nDate: Thu, 22 Oct 2026 18:00:00 +0200\n"
        "Message-ID: <demo@example.test>\nSubject: Closing\n"
        "Content-Type: text/plain; charset=utf-8\n\n"
        "PRIVATE SOURCE TEXT\n"
    ),
}


@pytest.fixture
def inputs(tmp_path):
    sources, config, cache = [tmp_path / name for name in ("sources", "config", "cache")]
    for path in (sources, config, cache):
        path.mkdir()
    for relative, content in FIXTURE_FILES.items():
        target = sources / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    return dict(sources=sources, config=config, cache=cache, workspace=tmp_path / "workspace")


def snapshot(manifest=emails.MANIFEST, mode="fixture"):
    return RunSpec(
        run_id="demo",
        scenario_id="historical",
        as_of="2026-10-22T20:00:00Z",
        stores=("MIL01",),
        source_manifest_hash=replay.digest(
            [
                (path, hashlib.sha256(content.encode()).hexdigest())
                for path, content in sorted(FIXTURE_FILES.items())
            ]
        ),
        config_hash=replay.digest([]),
        code_version="t",
        mode=mode,
        modules=(ModuleSnapshot(manifest=manifest, params={}),),
        prompt_versions={"extract": "v1"},
        model_versions={"chat": "model-v1"},
        authorized_fixture_refs=(),
    )


def custom(callback):
    manifest = ModuleManifest(
        id="test.replay",
        version="1",
        layer="sources",
        description="Synthetic boundary check",
        requires=(),
        optional_inputs=(),
        produces=(),
        enabled=True,
        mode="live",
        params_schema={},
    )
    return snapshot(manifest), Registry([RegisteredModule(manifest, callback)])


def success(ctx):
    return ModuleResult(
        module_id=ctx.manifest.id,
        module_version=ctx.manifest.version,
        status="succeeded",
        counts={},
        errors=(),
        abstentions=(),
    )


def test_repeatable_fixture_rebuild_starts_empty_and_retains_shared_inputs(inputs):
    first = replay.rebuild(snapshot(), **inputs)
    second = replay.rebuild(snapshot(), **inputs)
    assert first["status"] == second["status"] == "succeeded"
    assert first["fixture_demo_only"] is True and first["namespace"] == "fixture"
    assert first["output_sha256"] == second["output_sha256"]
    assert first["snapshot_sha256"] == second["snapshot_sha256"]
    assert first["artifacts"] == second["artifacts"]
    assert first["inputs"] == second["inputs"]
    assert first["modules"][0]["counts"]["documents"] == 1
    attempts = list(inputs["workspace"].glob("attempt-*"))
    assert len(attempts) == 2
    assert all((p / "data/tessera_fixture.db").is_file() for p in attempts)
    assert not (inputs["cache"] / "tessera_fixture.db").exists()
    assert "PRIVATE SOURCE TEXT" not in json.dumps(first)


@pytest.mark.parametrize("tree", ["sources", "config"])
def test_input_hash_mismatch_fails_before_any_module_or_client_runs(inputs, tree):
    seen = []

    def callback(ctx):
        seen.append(ctx)
        return success(ctx)

    spec, registry = custom(callback)
    (inputs[tree] / "changed-input.txt").write_text("Unapproved revision")
    result = replay.rebuild(spec, **inputs, registry=registry)
    assert result["status"] == "failed" and result["run_status"] == "not_started"
    assert tree + "_hash_mismatch" in result["missing_prerequisites"]
    assert not seen and not result["cache_misses"] and not result["network_attempts"]


def test_trace_semantic_comparison_ignores_only_execution_time():
    first = {"steps": [{"duration_ms": 12, "input_refs": [{"id": "source", "version": "v1"}]}]}
    second = {"steps": [{"duration_ms": 44, "input_refs": [{"id": "source", "version": "v1"}]}]}
    assert replay.digest(first) != replay.digest(second)  # raw provenance is retained
    assert replay.semantic_payload("AgentTrace", first) == replay.semantic_payload(
        "AgentTrace", second
    )
    second["steps"][0]["input_refs"][0]["version"] = "v2"
    assert replay.semantic_payload("AgentTrace", first) != replay.semantic_payload(
        "AgentTrace", second
    )


def test_systems_miss_does_not_fail_an_unrelated_source_module(inputs):
    def callback(ctx):
        cache = ctx.clients["systems"].recordings
        try:
            cache.get("0" * 64)
        except replay.ReplayMiss:
            pass
        return success(ctx)

    spec, registry = custom(callback)
    spec = spec.model_copy(
        update={"modules": spec.modules + (ModuleSnapshot(manifest=emails.MANIFEST, params={}),)}
    )
    registry = Registry(
        [registry.resolve(spec.modules[0]), RegisteredModule(emails.MANIFEST, emails.run)]
    )
    result = replay.rebuild(spec, **inputs, registry=registry)
    assert result["status"] == "failed"
    assert [(m["id"], m["status"]) for m in result["modules"]] == [
        ("test.replay", "failed"),
        ("src.email", "succeeded"),
    ]


def test_product_mode_identity_is_preserved_while_client_is_forced_to_replay(inputs, monkeypatch):
    monkeypatch.setenv("LLM_MODE", "live")
    seen = []

    def callback(ctx):
        seen.append((ctx.spec.mode, ctx.clients["llm"].settings.llm_mode))
        assert ctx.repo.list(SourceDocument) == []
        return success(ctx)

    spec, registry = custom(callback)
    spec = spec.model_copy(update={"mode": "live"})
    result = replay.rebuild(spec, **inputs, registry=registry)
    assert result["status"] == "succeeded" and result["namespace"] == "product"
    assert seen == [("live", "replay")]
    assert result["snapshot_sha256"] == replay.digest(spec.model_dump(mode="json"))


def test_swallowed_cache_miss_still_fails_and_shared_cache_is_unchanged(inputs):
    def callback(ctx):
        try:
            ctx.clients["llm"].chat([{"role": "user", "content": "PRIVATE PROMPT"}])
        except replay.ReplayMiss:
            pass
        return success(ctx)

    spec, registry = custom(callback)
    result = replay.rebuild(spec, **inputs, registry=registry)
    assert result["status"] == "failed" and result["run_status"] == "succeeded"
    assert len(result["cache_misses"]) == 1
    assert list(inputs["cache"].iterdir()) == []
    assert "PRIVATE PROMPT" not in json.dumps(result)


def test_network_denial_is_detected_even_when_module_falls_back(inputs, capsys):
    def callback(ctx):
        print("PRIVATE PRINT")
        logging.getLogger("example").error("PRIVATE LOG")
        with socket.socket() as sock:
            try:
                sock.connect(("127.0.0.1", 8088))
            except replay.OfflineNetworkDenied:
                pass
        return success(ctx)

    spec, registry = custom(callback)
    result = replay.rebuild(spec, **inputs, registry=registry)
    assert result["status"] == "failed" and result["network_attempts"] == 1
    captured = capsys.readouterr()
    assert "PRIVATE" not in captured.out + captured.err


def test_dns_lookup_is_denied_even_when_module_falls_back(inputs):
    def callback(ctx):
        try:
            socket.gethostbyname("localhost")
        except replay.OfflineNetworkDenied:
            pass
        return success(ctx)

    spec, registry = custom(callback)
    result = replay.rebuild(spec, **inputs, registry=registry)
    assert result["status"] == "failed" and result["network_attempts"] == 1
    assert result["run_status"] == "succeeded"


@pytest.mark.parametrize("location", ["sources", "config", "cache"])
def test_workspace_cannot_overlap_authorized_inputs(inputs, location):
    inputs["workspace"] = inputs[location] / "attempt-output"
    with pytest.raises(replay.IsolationError):
        replay.rebuild(snapshot(), **inputs)


def test_existing_unowned_workspace_and_durable_ledger_are_not_erased(inputs):
    workspace = inputs["workspace"]
    workspace.mkdir()
    ledger = workspace / "decisions.db"
    ledger.write_bytes(b"DO NOT TOUCH")
    with pytest.raises(replay.IsolationError):
        replay.rebuild(snapshot(), **inputs)
    assert ledger.read_bytes() == b"DO NOT TOUCH"


@pytest.mark.parametrize("kind", ["symlink", "secret", "answers"])
def test_inputs_reject_links_secrets_and_hidden_answers_without_reading_them(inputs, kind):
    root = inputs["sources"]
    if kind == "symlink":
        (root / "alias").symlink_to(inputs["config"], target_is_directory=True)
    elif kind == "secret":
        (root / ".env").write_text("fake-test-secret")
    else:
        (root / "ground_truth").mkdir()
    result = replay.rebuild(snapshot(), **inputs)
    assert result["status"] == "failed" and result["error_type"] == "IsolationError"
    assert "fake-test-secret" not in json.dumps(result)


def test_cli_reports_fixture_success_and_input_failure_with_nonzero_status(inputs, tmp_path):
    path = tmp_path / "spec.json"
    path.write_text(snapshot().model_dump_json())
    command = [sys.executable, str(REPO_ROOT / "scripts/replay_demo.py"), "--run-spec", str(path)]
    for key, value in inputs.items():
        command.extend(("--" + key, str(value)))
    first = subprocess.run(command, text=True, capture_output=True, check=False)
    assert first.returncode == 0, first.stderr
    assert json.loads(first.stdout)["fixture_demo_only"] is True
    assert "PRIVATE SOURCE TEXT" not in first.stdout + first.stderr
    missing = command.copy()
    missing[missing.index("--cache") + 1] = str(tmp_path / "missing-cache")
    second = subprocess.run(missing, text=True, capture_output=True, check=False)
    assert second.returncode == 1 and json.loads(second.stdout)["status"] == "failed"


@pytest.mark.parametrize("corrupt", [False, True])
def test_recorded_response_is_replayed_without_modifying_shared_cache(inputs, corrupt):
    response = {
        "id": "recorded",
        "object": "chat.completion",
        "created": 0,
        "model": "test",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": "PRIVATE RECORDED RESPONSE"},
            }
        ],
    }
    messages = [{"role": "user", "content": "private query"}]

    def callback(ctx):
        answer = ctx.clients["llm"].chat(messages)
        assert answer.choices[0].message.content == "PRIVATE RECORDED RESPONSE"
        return success(ctx)

    spec, registry = custom(callback)

    class SeedCache(replay.ResponseCache):
        def get(self, key):
            return replay.ResponseCache(self.directory).put(key, response)

    recorder = replay.LLMClient(
        replay.Settings(_env_file=None, llm_mode="replay"),
        cache=SeedCache(inputs["cache"]),
    ).for_run(spec)
    recorder.chat(messages)  # Fake recorded payload, no provider key or network.
    if corrupt:
        path = next(inputs["cache"].rglob("*.json"))
        envelope = json.loads(path.read_text())
        envelope["checksum"] = "bad"
        path.write_text(json.dumps(envelope))
    before = {
        p.relative_to(inputs["cache"]): p.read_bytes() for p in inputs["cache"].rglob("*.json")
    }
    result = replay.rebuild(spec, **inputs, registry=registry)
    assert result["status"] == ("failed" if corrupt else "succeeded")
    assert result["cache_misses"] == []
    assert len(result["cache_corrupt"]) == int(corrupt)
    assert before == {
        p.relative_to(inputs["cache"]): p.read_bytes() for p in inputs["cache"].rglob("*.json")
    }
    assert "PRIVATE RECORDED RESPONSE" not in json.dumps(result)


def test_subprocess_escape_is_denied(inputs):
    def callback(ctx):
        try:
            subprocess.run([sys.executable, "-c", "raise SystemExit(99)"], check=False)
        except replay.OfflineNetworkDenied:
            pass
        return success(ctx)

    spec, registry = custom(callback)
    result = replay.rebuild(spec, **inputs, registry=registry)
    assert result["status"] == "failed" and result["network_attempts"] == 1
    assert "offline_network_or_process_operation" in result["missing_prerequisites"]


@pytest.fixture
def decision_snapshot():
    def callback(ctx):
        ctx.repo.put(case, option)
        return success(ctx)

    spec, registry = custom(callback)
    case = fixture_case(run_id=spec.run_id, input_refs=())
    option = ActionOption(
        id="synthetic-option",
        version="1",
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        available_at=spec.as_of,
        availability_basis="synthetic test",
        source_refs=(),
        computed_at=spec.as_of,
        input_refs=(ArtifactRef(kind="Case", id=case.id, version=case.version),),
        producer="test.replay",
        producer_version="1",
        case_id=case.id,
        kind="hold",
        legs=(),
        checks=(),
        assumptions=(),
        valid_until=spec.as_of + timedelta(days=1),
        recommended=False,
        rationale="Synthetic boundary",
        input_version_hash="hash",
    )
    request = approval.DecisionRequest(
        run_id=spec.run_id,
        scenario_id=spec.scenario_id,
        option_id=option.id,
        input_version_hash=option.input_version_hash,
        decision="rejected",
        by="synthetic test reviewer",
        idempotency_key="decision-1",
    )
    at = spec.as_of + timedelta(minutes=1)
    # Explicitly synthetic, not an approved product scenario or Core evidence.
    frozen = replay.FrozenDecision(
        snapshot_sha256=replay.digest(spec.model_dump(mode="json")),
        namespace="fixture",
        at=at,
        request=request,
        draft=approval._draft(request, option, at),
    )
    return spec, registry, frozen


@pytest.mark.parametrize("change", ["run", "scenario", "clock", "snapshot", "namespace"])
def test_frozen_decision_must_match_the_rebuilt_snapshot(
    inputs, tmp_path, decision_snapshot, change
):
    spec, registry, frozen = decision_snapshot
    event = frozen.model_dump(mode="json")
    if change == "run":
        event["request"]["run_id"] = "other"
    elif change == "scenario":
        event["request"]["scenario_id"] = "other"
    elif change == "clock":
        event["at"] = "2026-10-21T20:01:00Z"
    elif change == "snapshot":
        event["snapshot_sha256"] = "other"
    elif change == "namespace":
        event["namespace"] = "product"
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps([event]))
    result = replay.rebuild(spec, **inputs, decisions=path, registry=registry)
    assert result["status"] == "failed" and result["error_type"] == "IsolationError"
    assert result["run_status"] == "not_started" and result["decisions"] == []


def test_frozen_drafts_are_exact_durable_and_part_of_replay_hashes(
    inputs, tmp_path, decision_snapshot
):
    spec, registry, frozen = decision_snapshot
    empty = replay.rebuild(spec, **inputs, registry=registry)
    path = tmp_path / "decisions.json"
    # Retry must return the same durable draft and must not count it twice in the ledger hash.
    path.write_text(json.dumps([frozen.model_dump(mode="json")] * 2))
    first = replay.rebuild(spec, **inputs, decisions=path, registry=registry)
    second = replay.rebuild(spec, **inputs, decisions=path, registry=registry)
    assert first["status"] == second["status"] == "succeeded", first
    assert first["network_attempts"] == second["network_attempts"] == 0
    assert first["decisions"] == second["decisions"]
    assert first["decisions"][0]["id"] == frozen.draft.decision.id
    assert first["decisions"][0]["sha256"] == replay.digest(frozen.draft.model_dump(mode="json"))
    assert (
        first["ledger_sha256"]
        == second["ledger_sha256"]
        == replay.digest([frozen.draft.model_dump(mode="json")])
    )
    assert first["output_sha256"] == second["output_sha256"] != empty["output_sha256"]
    assert first["raw_output_sha256"] == second["raw_output_sha256"] != empty["raw_output_sha256"]


def test_changed_frozen_draft_fails_without_saving_a_decision(inputs, tmp_path, decision_snapshot):
    spec, registry, frozen = decision_snapshot
    event = frozen.model_dump(mode="json")
    event["draft"]["decision"]["by"] = "invented approver"
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps([event]))
    result = replay.rebuild(spec, **inputs, decisions=path, registry=registry)
    assert result["status"] == "failed" and result["error_type"] == "Conflict"
    assert result["decisions"] == []
    engine = replay.connect(
        f"sqlite:///{inputs['workspace'] / result['attempt_id'] / 'data/tessera_fixture.db'}"
    )
    with engine.connect() as conn:
        assert not inspect(conn).has_table(ledger.drafts.name) or (
            conn.execute(select(ledger.drafts)).first() is None
        )
    engine.dispose()


@pytest.mark.parametrize("missing", [False, True])
def test_systems_recordings_rebuild_offline_and_swallowed_misses_still_fail(
    inputs, tmp_path, missing
):
    def callback(ctx):
        client = ctx.clients["systems"](Crosswalk({}, {}, {}, {}))
        try:
            try:
                response = client._http.get("/warehouse/v1/atp?asOf=2026-10-22")
                assert response.json() == {"positions": []}
            except replay.ReplayMiss:
                pass  # Tool fallback cannot hide a missing systems prerequisite.
        finally:
            client.close()
        return success(ctx)

    spec, registry = custom(callback)
    recorded = tmp_path / "systems"
    recorded.mkdir()
    if not missing:
        transport = SystemsTransport(
            replay.Settings(_env_file=None, llm_mode="record"),
            spec,
            SystemsCache(recorded),
            upstream=httpx.MockTransport(lambda _: httpx.Response(200, json={"positions": []})),
        )
        with httpx.Client(base_url="http://127.0.0.1:8088", transport=transport) as client:
            client.get("/warehouse/v1/atp?asOf=2026-10-22")
    result = replay.rebuild(spec, **inputs, systems_cache=recorded, registry=registry)
    assert result["status"] == ("failed" if missing else "succeeded")
    assert result["network_attempts"] == 0
    assert len(result["systems_cache_misses"]) == int(missing)
    assert result["inputs"]["systems_cache"]["files"] == int(not missing)


@pytest.mark.parametrize("location", ["sources", "config", "cache", "workspace"])
def test_symlinked_ancestor_is_rejected_before_staging(inputs, tmp_path, location):
    alias = tmp_path / "linked-parent"
    alias.symlink_to(tmp_path, target_is_directory=True)
    inputs[location] = alias / inputs[location].name
    with pytest.raises(replay.IsolationError):
        replay.rebuild(snapshot(), **inputs)
    assert not inputs["workspace"].exists()


@pytest.mark.parametrize("relative", ["eval/labels", "ground_truth/../authorized"])
def test_hidden_answer_paths_are_rejected_before_file_reads(inputs, tmp_path, relative):
    root = tmp_path / relative
    root.mkdir(parents=True)
    inputs["sources"] = root
    with pytest.raises(replay.IsolationError):
        replay.rebuild(snapshot(), **inputs)
    assert not inputs["workspace"].exists()


def test_module_settings_never_read_dotenv_and_restore_configuration(inputs, monkeypatch):
    from pydantic_settings.sources import DotEnvSettingsSource

    def guard(source):
        # Fail before opening any file, including the real repository dotenv.
        assert source.env_file is None, "replay must not read dotenv"
        return {}

    monkeypatch.setattr(DotEnvSettingsSource, "_read_env_files", guard)
    previous_env_file = replay.Settings.model_config["env_file"]
    seen = []

    def callback(ctx):
        settings = replay.get_settings()
        assert settings.sources_dir.is_relative_to(inputs["workspace"])
        assert settings.llm_mode == "replay"
        assert not settings.asr_api_key.get_secret_value()
        seen.append(settings)
        return success(ctx)

    spec, registry = custom(callback)
    result = replay.rebuild(spec, **inputs, registry=registry)
    assert result["status"] == "succeeded"
    assert len(seen) == 1
    assert replay.Settings.model_config["env_file"] == previous_env_file


def test_voice_snapshot_requires_and_rebuilds_explicit_voice_inputs(inputs, tmp_path):
    spec = snapshot(voice.MANIFEST)
    spec = spec.model_copy(
        update={"modules": (ModuleSnapshot(manifest=voice.MANIFEST, params={"mode": "fixture"}),)}
    )
    missing = replay.rebuild(spec, **inputs)
    assert missing["status"] == "failed"
    assert "voice_inputs" in missing["missing_prerequisites"]
    root = tmp_path / "voice"
    note = root / "demo-note"
    note.mkdir(parents=True)
    audio = b"synthetic test audio"
    (note / "audio.wav").write_bytes(audio)
    (note / "transcript.txt").write_text("PRIVATE VOICE TRANSCRIPT")
    (note / "note.json").write_text(
        json.dumps(
            {
                "note_id": "demo-note",
                "store_id": "MIL01",
                "sent_at": "2026-10-22T18:00:00Z",
                "timezone": "Europe/Rome",
                "author_ref": "synthetic-manager",
                "fixture_kind": "synthetic_extension",
                "audio": "audio.wav",
                "audio_sha256": "sha256:" + hashlib.sha256(audio).hexdigest(),
            }
        )
    )
    first = replay.rebuild(spec, **inputs, voice=root)
    second = replay.rebuild(spec, **inputs, voice=root)
    assert first["status"] == second["status"] == "succeeded"
    assert first["modules"][0]["counts"]["documents"] == 1
    assert first["inputs"]["voice"]["files"] == 3
    assert first["output_sha256"] == second["output_sha256"]
    assert "PRIVATE VOICE" not in json.dumps(first)
    with pytest.raises(replay.IsolationError):
        replay.rebuild(spec, **{**inputs, "workspace": root / "output"}, voice=root)
