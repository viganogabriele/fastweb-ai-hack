"""Offline replay boundaries, without real credentials or external network access."""

import hashlib
import importlib.util
import json
import logging
import socket
import subprocess
import sys

import pytest

from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import (
    ModuleManifest,
    ModuleResult,
    ModuleSnapshot,
    RunSpec,
    SourceDocument,
)
from tesseract.core.registry import RegisteredModule, Registry
from tesseract.modules.sources import emails, voice

module_spec = importlib.util.spec_from_file_location(
    "replay_demo", REPO_ROOT / "scripts/replay_demo.py"
)
replay = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(replay)


@pytest.fixture
def inputs(tmp_path):
    sources, config, cache = [tmp_path / name for name in ("sources", "config", "cache")]
    for path in (sources, config, cache):
        path.mkdir()
    master = sources / "erp/master_data"
    master.mkdir(parents=True)
    (master / "stores.csv").write_text(
        "store_id,language,timezone,currency\nMIL01,it,Europe/Rome,EUR\n",
    )
    mailbox = sources / "store_emails/MIL01"
    mailbox.mkdir(parents=True)
    (mailbox / "message.eml").write_text(
        "From: example@example.test\nTo: demo@example.test\nDate: Thu, 22 Oct 2026 18:00:00 +0200\n"
        "Message-ID: <demo@example.test>\nSubject: Closing\n"
        "Content-Type: text/plain; charset=utf-8\n\n"
        "PRIVATE SOURCE TEXT\n",
    )
    return dict(sources=sources, config=config, cache=cache, workspace=tmp_path / "workspace")


def snapshot(manifest=emails.MANIFEST, mode="fixture"):
    return RunSpec(
        run_id="demo",
        scenario_id="historical",
        as_of="2026-10-22T20:00:00Z",
        stores=("MIL01",),
        source_manifest_hash="declared-sources",
        config_hash="declared-config",
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
    assert first["inputs"] == second["inputs"]
    assert first["modules"][0]["counts"]["documents"] == 1
    attempts = list(inputs["workspace"].glob("attempt-*"))
    assert len(attempts) == 2
    assert all((p / "data/tesseract_fixture.db").is_file() for p in attempts)
    assert not (inputs["cache"] / "tesseract_fixture.db").exists()
    assert "PRIVATE SOURCE TEXT" not in json.dumps(first)


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
