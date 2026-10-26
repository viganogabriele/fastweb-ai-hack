"""DEMO-04: live voice notes from /store/record, saved for src.voice and run on demand."""

import io
import json
import wave
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from tesseract.api.main import create_app
from tesseract.api.routers import voice as live
from tesseract.core.config import Settings
from tesseract.core.db import connect
from tesseract.core.orchestrator import _plan
from tesseract.core.registry import Registry
from tesseract.modules.sources import voice
from tesseract.modules.sources.emails import Store
from tesseract.modules.sources.voice_inbox import (
    batch_hash,
    freeze_notes,
    list_notes,
    save_note,
    snapshot_path,
)

ROME = Store(language="it", timezone="Europe/Rome", currency="EUR")


def wav(seconds=1.0, rate=8000) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        writer.writeframes(b"\x00\x00" * int(seconds * rate))
    return buffer.getvalue()


@pytest.fixture
def client(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(live, "execute", lambda *args: calls.append(args))
    app = create_app(
        engine=connect(f"sqlite:///{tmp_path / 'test.db'}"),
        registry=Registry.discover(),
        settings=Settings(data_dir=tmp_path, asr_api_key=None, voice_access_token="test-voice"),
    )
    live._ASR_STARTS.clear()
    with TestClient(app, headers={"Authorization": "Bearer test-voice"}) as test_client:
        test_client.executed = calls
        yield test_client


def post_note(client, store="MIL01", transcript="Due clienti hanno chiesto il gilet blu"):
    return client.post(
        "/api/voice/notes",
        data={"store_id": store, "transcript": transcript, "language": "it"},
        files={"audio": ("note.wav", wav(), "audio/wav")},
    )


def test_a_recording_becomes_a_live_note_src_voice_can_read(client, tmp_path):
    response = post_note(client)
    assert response.status_code == 201
    body = response.json()
    assert body["note_id"].startswith("live-mil01-")
    assert body["run_id"] is None
    note = voice.read_sidecar(tmp_path / "voice_inbox" / body["note_id"])
    assert note.sidecar.fixture_kind == "live"
    assert note.sidecar.author_ref == "pseudonym:mil01-staff-live"
    assert body["staff_ref"] is None
    assert body["prompt_set"] is None
    assert note.sidecar.sent_at.utcoffset() is not None
    audio = voice.load_audio(note)  # converted to 16 kHz mono wav, hash checked
    with wave.open(str(audio.path)) as reader:
        assert (reader.getframerate(), reader.getnchannels()) == (16000, 1)
    assert voice.manual_transcript(note) == "Due clienti hanno chiesto il gilet blu"
    assert [n["note_id"] for n in client.get("/api/voice/notes").json()] == [body["note_id"]]


def test_guided_notes_preserve_distinct_employees_and_prompt_set(client, tmp_path):
    for staff in ("staff-09", "staff-10"):
        response = client.post(
            "/api/voice/notes",
            data={
                "store_id": "MIL01",
                "transcript": "Due clienti hanno chiesto il gilet blu",
                "staff_ref": staff,
                "prompt_set": "guided-v1",
            },
            files={"audio": ("note.wav", wav(), "audio/wav")},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["staff_ref"] == staff
        assert body["prompt_set"] == "guided-v1"
        note = voice.read_sidecar(tmp_path / "voice_inbox" / body["note_id"])
        assert note.sidecar.author_ref == f"pseudonym:mil01-{staff}"
        assert note.sidecar.staff_ref == staff
        assert note.sidecar.prompt_set == "guided-v1"
    listed = client.get("/api/voice/notes").json()
    assert {note["staff_ref"] for note in listed} == {"staff-09", "staff-10"}
    notes = list_notes(tmp_path)
    freeze_notes(tmp_path, "guided-test", notes, batch_hash(notes))
    assert {
        voice.read_sidecar(path).sidecar.staff_ref
        for path in snapshot_path(tmp_path, "guided-test").iterdir()
    } == {"staff-09", "staff-10"}


@pytest.mark.parametrize(
    "metadata",
    [
        {"staff_ref": "BAD"},
        {"staff_ref": "bad code"},
        {"staff_ref": "bad_code"},
        {"staff_ref": "x" * 33},
        {"staff_ref": "staff-09\n"},
        {"prompt_set": "unknown"},
        {"prompt_set": "guided-v1"},
        {"prompt_set": "guided-v1", "staff_ref": ""},
    ],
)
def test_invalid_guided_metadata_is_rejected_before_publication(client, tmp_path, metadata):
    response = client.post(
        "/api/voice/notes",
        data={"store_id": "MIL01", "transcript": "ciao", **metadata},
        files={"audio": ("note.wav", wav(), "audio/wav")},
    )
    assert response.status_code == 422
    assert not list_notes(tmp_path)


@pytest.mark.parametrize(
    ("store", "transcript", "status"), [("XXX99", "testo", 422), ("MIL01", "   ", 422)]
)
def test_unknown_store_or_empty_transcript_is_refused(client, store, transcript, status):
    assert post_note(client, store, transcript).status_code == status


def test_undecodable_audio_is_refused(client):
    response = client.post(
        "/api/voice/notes",
        data={"store_id": "MIL01", "transcript": "ciao"},
        files={"audio": ("note.webm", b"not audio", "audio/webm")},
    )
    assert response.status_code == 422


def test_process_runs_each_store_once_over_new_notes_only(client, tmp_path):
    first = post_note(client).json()
    post_note(client, "MIL02")
    response = client.post("/api/voice/process", json={})
    assert response.status_code == 202
    runs = response.json()
    assert sorted(r["spec"]["stores"][0] for r in runs) == ["MIL01", "MIL02"]
    assert len(client.executed) == 2
    spec, _, registry, settings = client.executed[0]
    assert settings.llm_mode == "record"
    assert spec.scenario_id == "live-voice" and spec.mode == "live"
    snapshots = {s.manifest.id: s for s in spec.modules}
    assert snapshots["src.voice"].params == {"notes": [first["note_id"]], "mode": "fixture"}
    for snapshot in spec.modules:
        registry.resolve(snapshot)  # installed manifests and valid params
    plan = _plan(spec, None)
    assert plan.index("src.voice") < plan.index("ing.extract") < plan.index("int.cases")
    assert all(n["run_id"] for n in client.get("/api/voice/notes").json())
    assert client.post("/api/voice/process", json={}).status_code == 409


def test_process_can_be_limited_to_one_store(client):
    post_note(client)
    post_note(client, "MIL02")
    runs = client.post("/api/voice/process", json={"store_id": "MIL02"}).json()
    assert [r["spec"]["stores"] for r in runs] == [["MIL02"]]
    pending = [n for n in client.get("/api/voice/notes").json() if n["run_id"] is None]
    assert [n["store_id"] for n in pending] == ["MIL01"]


def test_transcribe_without_an_asr_key_says_so(client):
    response = client.post(
        "/api/voice/transcribe", files={"audio": ("partial.webm", b"x", "audio/webm")}
    )
    assert response.status_code == 503


def test_transcribe_is_live_and_returns_the_text(client, monkeypatch):
    seen = {}

    def fake(self, path, language=None, *args, **kwargs):
        seen.update(mode=self.settings.llm_mode, suffix=path.suffix, language=language)
        return SimpleNamespace(text=" Ciao dal negozio ", duration=1.0)

    client.app.state.settings.asr_api_key = __import__("pydantic").SecretStr("fake-asr")
    monkeypatch.setattr(live.LLMClient, "transcribe", fake)
    response = client.post(
        "/api/voice/transcribe",
        data={"language": "it"},
        files={"audio": ("blob.wav", wav(), "audio/wav")},
    )
    assert response.json() == {"text": "Ciao dal negozio", "duration_s": 1.0}
    assert seen == {"mode": "live", "suffix": ".wav", "language": "it"}


def test_ordinary_src_voice_never_reads_live_inbox(tmp_path, monkeypatch):
    note = save_note("MIL01", ROME, wav(), "wav", "Nota live", data_dir=tmp_path).note
    (tmp_path / "fixtures" / "voice").mkdir(parents=True)
    monkeypatch.setattr(voice, "voice_path", lambda: tmp_path / "fixtures" / "voice")
    monkeypatch.setattr(voice, "inbox_path", lambda: tmp_path / "voice_inbox")
    stored = []
    ctx = SimpleNamespace(
        params={"mode": "fixture"},
        spec=SimpleNamespace(stores=("MIL01",), as_of=note.sidecar.sent_at),
        repo=SimpleNamespace(put=lambda *records: stored.extend(records)),
    )
    result = voice.run(ctx)
    assert result.counts["notes"] == 0
    assert stored == []
    assert json.loads((note.directory / "note.json").read_text())["fixture_kind"] == "live"


class FakeLLM:
    """No ASR (the declared transcript is used) and one extracted unmet-demand fact."""

    def transcribe(self, *args, **kwargs):
        raise RuntimeError("no ASR in tests")

    def extract(self, schema, messages, **kwargs):
        from tesseract.modules.ingestion.extract import Candidates

        assert schema is Candidates
        fact = {
            "quote": "Due clienti volevano il gilet VEL blu notte in taglia 3",
            "kind": "unmet_demand",
            "product_mention": "gilet VEL blu notte taglia 3",
            "quantity_kind": "exact",
            "value": 2,
            "unit": "customers",
            "quantity_raw": "Due",
            "direction": "up",
            "reason": "size_availability",
            "attribution": "store_staff",
        }
        return Candidates.model_validate({"observations": [fact]})


def test_a_live_run_turns_a_named_product_into_a_sku_size_case(tmp_path, monkeypatch):
    from datetime import UTC, datetime

    from tesseract.core.contracts import Case
    from tesseract.core.orchestrator import run
    from tesseract.core.run_repo import repo_session

    settings = Settings(data_dir=tmp_path)
    text = "Due clienti volevano il gilet VEL blu notte in taglia 3, ma non ce l'avevamo."
    save_note("MIL01", ROME, wav(), "wav", text, language="it", data_dir=tmp_path)
    monkeypatch.setattr(voice, "voice_path", lambda: tmp_path / "fixtures" / "voice")
    monkeypatch.setattr(voice, "inbox_path", lambda: tmp_path / "voice_inbox")
    registry = Registry.discover()
    spec = live.live_spec(
        registry, "MIL01", list_notes(tmp_path), datetime.now(UTC).replace(microsecond=0)
    )
    freeze_notes(tmp_path, spec.run_id, list_notes(tmp_path), spec.source_manifest_hash)
    fake = FakeLLM()
    fake.settings = settings
    engine = connect(f"sqlite:///{tmp_path / 'test.db'}")
    with repo_session(engine, spec, fixture_mode=False, write=True):
        pass
    statuses = run(spec, engine=engine, registry=registry, clients={"llm": fake}, settings=settings)
    assert {s.module_id: s.status for s in statuses}["ing.extract"] == "succeeded"
    with repo_session(engine, spec, fixture_mode=False) as repo:
        assert repo.run_state()["status"] == "degraded"  # src.email reads no mail on purpose
        (case,) = repo.list(Case)
    assert (case.case_type, case.scope_level, case.scope_id) == (
        "unmet_demand",
        "sku_size",
        "J10911A00305-742-3",
    )


def test_a_note_whose_run_failed_can_be_processed_again(client):
    from tesseract.core.run_repo import repo_session

    post_note(client)
    (run,) = client.post("/api/voice/process", json={}).json()
    assert client.post("/api/voice/process", json={}).status_code == 409
    engine = client.app.state.engines["product"]
    with repo_session(engine, run["spec"]["run_id"], fixture_mode=False, write=True) as repo:
        repo.set_run_status("failed")
    assert [n["run_id"] for n in client.get("/api/voice/notes").json()] == [None]
    (again,) = client.post("/api/voice/process", json={}).json()
    assert again["spec"]["run_id"] != run["spec"]["run_id"]


def test_live_routes_require_explicit_opt_in_and_capability(client):
    assert client.get("/api/voice/notes", headers={"Authorization": ""}).status_code == 401
    assert (
        client.post(
            "/api/voice/process", json={}, headers={"Authorization": "Bearer wrong"}
        ).status_code
        == 401
    )
    client.app.state.settings.voice_access_token = None
    assert post_note(client).status_code == 503
    assert client.executed == []


def test_missing_ffmpeg_is_a_service_failure_not_bad_user_audio(client, tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    result = post_note(client)
    assert result.status_code == 503
    assert result.json()["detail"] == "ffmpeg is required on the server"
    assert list_notes(tmp_path) == []


@pytest.mark.parametrize(
    ("suffix", "codec", "flags"),
    [
        ("webm", "libopus", []),
        ("mp4", "aac", ["-movflags", "+frag_keyframe+empty_moov+default_base_moof"]),
    ],
)
def test_real_browser_containers_are_converted_to_bounded_mono_pcm(tmp_path, suffix, codec, flags):
    import subprocess

    from tesseract.modules.sources.voice_inbox import to_wav

    source = tmp_path / "source.wav"
    source.write_bytes(wav(rate=48000))
    target = tmp_path / f"capture.{suffix}"
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(source),
            "-c:a",
            codec,
            *flags,
            str(target),
        ],
        check=True,
    )
    converted = to_wav(target.read_bytes(), suffix)
    with wave.open(io.BytesIO(converted)) as reader:
        assert (reader.getnchannels(), reader.getframerate(), reader.getsampwidth()) == (
            1,
            16000,
            2,
        )
        assert 0.9 <= reader.getnframes() / reader.getframerate() <= 1.1


def test_duration_empty_upload_size_and_language_limits(client, tmp_path, monkeypatch):
    from tesseract.modules.sources.voice_inbox import InvalidRecording, to_wav

    with pytest.raises(InvalidRecording, match="90 seconds"):
        to_wav(wav(seconds=91), "wav")
    response = client.post(
        "/api/voice/notes",
        data={"store_id": "MIL01", "transcript": "test", "language": "../invalid"},
        files={"audio": ("a.wav", wav(), "audio/wav")},
    )
    assert response.status_code == 422
    assert list_notes(tmp_path) == []
    monkeypatch.setattr(live, "MAX_UPLOAD", 8)
    assert post_note(client).status_code == 413
    assert (
        client.post(
            "/api/voice/transcribe", files={"audio": ("a.wav", b"", "audio/wav")}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/voice/notes", content=b"x", headers={"Content-Length": "999999999"}
        ).status_code
        == 413
    )


def test_decoder_timeout_is_explicit_and_does_not_publish(client, tmp_path, monkeypatch):
    import subprocess

    from tesseract.modules.sources import voice_inbox

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(voice_inbox.subprocess, "run", timeout)
    assert post_note(client).json()["detail"] == "recording conversion timed out"
    assert list_notes(tmp_path) == []


def test_playlists_cannot_fetch_network_or_read_an_external_local_audio(tmp_path):
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    from tesseract.modules.sources.voice_inbox import InvalidRecording, to_wav

    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(wav())

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    external = tmp_path / "external.wav"
    external.write_bytes(wav())
    try:
        for uri in (f"http://127.0.0.1:{server.server_port}/private.wav", external.as_uri()):
            for payload in (
                f"ffconcat version 1.0\nfile {uri}\n",
                f"#EXTM3U\n#EXT-X-TARGETDURATION:1\n#EXTINF:1,\n{uri}\n#EXT-X-ENDLIST\n",
            ):
                for suffix in live.SUFFIXES:
                    with pytest.raises(InvalidRecording):
                        to_wav(payload.encode(), suffix)
        assert requests == []
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_queued_sources_and_retries_preserve_accepted_text_not_mutable_inbox(client, tmp_path):
    from tesseract.modules.sources.voice_inbox import batch_hash, snapshot_path

    note = post_note(client, transcript="Accepted edited text").json()
    (queued,) = client.post("/api/voice/process", json={}).json()
    spec = client.executed[-1][0]
    inbox = tmp_path / "voice_inbox" / note["note_id"]
    (inbox / "transcript.txt").write_text("Later different text")
    frozen = voice.read_sidecar(snapshot_path(tmp_path, spec.run_id) / note["note_id"])
    assert voice.manual_transcript(frozen) == "Accepted edited text"
    assert batch_hash(list_notes(tmp_path)) != spec.source_manifest_hash
    with __import__("tesseract.core.run_repo", fromlist=["repo_session"]).repo_session(
        client.app.state.engines["product"], spec, write=True
    ) as repo:
        repo.set_run_status("failed")
    (retried,) = client.post("/api/voice/process", json={}).json()
    retry_spec = client.executed[-1][0]
    assert retry_spec.source_manifest_hash == spec.source_manifest_hash
    assert retried["spec"]["run_id"] != queued["spec"]["run_id"]


def test_simultaneous_process_submissions_claim_a_note_once(client):
    from concurrent.futures import ThreadPoolExecutor

    post_note(client)
    with ThreadPoolExecutor(2) as executor:
        results = list(
            executor.map(lambda _: client.post("/api/voice/process", json={}).status_code, range(2))
        )
    assert sorted(results) == [202, 409]
    assert len(client.executed) == 1


def test_future_notes_are_not_queued_and_foreign_store_stays_pending(client, tmp_path):
    from datetime import UTC, datetime, timedelta

    save_note(
        "MIL01",
        ROME,
        wav(),
        "wav",
        "Future",
        now=datetime.now(UTC) + timedelta(days=1),
        data_dir=tmp_path,
    )
    post_note(client, "MIL02")
    assert client.post("/api/voice/process", json={"store_id": "MIL01"}).status_code == 409
    (run,) = client.post("/api/voice/process", json={}).json()
    assert run["spec"]["stores"] == ["MIL02"]
    assert len(client.executed) == 1


def test_live_accepted_transcript_is_never_retranscribed_or_given_fake_intervals(client, tmp_path):
    from tesseract.core.contracts import Segment, SourceDocument

    post_note(client, transcript="User corrected the model name")
    client.post("/api/voice/process", json={})
    spec = client.executed[-1][0]
    stored = []
    ctx = SimpleNamespace(
        spec=spec,
        params={"notes": spec.modules[0].params["notes"]},
        clients={"llm": SimpleNamespace(settings=client.app.state.settings)},
        repo=SimpleNamespace(put=lambda *records: stored.extend(records)),
    )
    result = voice.run(ctx)
    assert result.counts["declared"] == 1 and result.counts["recorded"] == 0
    doc, segment = stored
    assert isinstance(doc, SourceDocument) and isinstance(segment, Segment)
    assert doc.text == "User corrected the model name"
    assert doc.meta["transcript_mode"] == "manual"
    assert segment.t_start_s is None and segment.t_end_s is None
    from tesseract.modules.sources.voice_inbox import snapshot_path

    path = snapshot_path(tmp_path, spec.run_id) / doc.meta["note_id"] / "transcript.txt"
    path.write_text("Tampered")
    with pytest.raises(ValueError, match="source manifest hash"):
        voice.run(ctx)


def test_transcription_throttle_is_shared_and_releases_after_failure(client, monkeypatch):
    import time

    from pydantic import SecretStr

    client.app.state.settings.asr_api_key = SecretStr("fake")
    live._ASR_STARTS.extend([time.monotonic()] * 20)
    args = {"files": {"audio": ("a.wav", wav(), "audio/wav")}}
    assert client.post("/api/voice/transcribe", **args).status_code == 429
    live._ASR_STARTS.clear()
    monkeypatch.setattr(
        live.LLMClient,
        "transcribe",
        lambda *a, **k: (_ for _ in ()).throw(live.LLMCallFailed("synthetic")),
    )
    assert client.post("/api/voice/transcribe", **args).status_code == 502
    assert not live._ASR_SLOT.locked()


@pytest.mark.parametrize("name", ["note.json", "note.wav", "transcript.txt", "directory"])
def test_inbox_never_reads_symlinked_source_files(client, tmp_path, name):
    note = post_note(client).json()
    directory = tmp_path / "voice_inbox" / note["note_id"]
    if name == "directory":
        external = tmp_path / note["note_id"]
        directory.rename(external)
        directory.symlink_to(external, target_is_directory=True)
    else:
        path = directory / name
        external = tmp_path / name
        path.rename(external)
        path.symlink_to(external)
    assert client.get("/api/voice/notes").json() == []
    assert client.post("/api/voice/process", json={}).status_code == 409
    assert client.executed == []


def test_chunked_upload_limit_is_enforced_before_multipart_spooling(client, monkeypatch):
    monkeypatch.setattr(live, "MAX_UPLOAD", 8)

    def chunks():
        yield (
            b'--boundary\r\nContent-Disposition: form-data; name="audio"; filename="a.wav"\r\n\r\n'
        )
        yield b"x" * (64 * 1024 + 9)
        yield b"\r\n--boundary--\r\n"

    response = client.post(
        "/api/voice/notes",
        content=chunks(),
        headers={"Content-Type": "multipart/form-data; boundary=boundary"},
    )
    assert response.status_code == 413
    assert client.executed == []


def test_live_source_references_are_distinct_from_dataset_sources(client, tmp_path):
    post_note(client)
    client.post("/api/voice/process", json={})
    spec = client.executed[-1][0]
    from tesseract.modules.sources.voice_inbox import snapshot_path

    (path,) = snapshot_path(tmp_path, spec.run_id).iterdir()
    note = voice.read_sidecar(path)
    assert note.uri == f"live-voice://{spec.run_id}/{note.slug}"


def test_precise_duration_rejects_audio_just_over_ninety_seconds():
    from tesseract.modules.sources.voice_inbox import InvalidRecording, to_wav

    with pytest.raises(InvalidRecording, match="90 seconds"):
        to_wav(wav(seconds=90.02), "wav")


def test_generic_run_creation_cannot_forge_live_voice_claims(client):
    from datetime import UTC, datetime

    spec = live.live_spec(Registry.discover(), "MIL01", [], datetime.now(UTC))
    payload = spec.model_dump(mode="json", exclude={"run_id", "erp_max_seq"})
    response = client.post("/api/runs", json=payload, headers={"Authorization": ""})
    assert response.status_code == 422
    assert "/api/voice/process" in response.json()["detail"]
    assert client.get("/api/voice/notes").json() == []


def test_a_second_batch_waits_for_the_active_live_run(client):
    post_note(client)
    assert client.post("/api/voice/process", json={}).status_code == 202
    post_note(client, transcript="A second fresh note")
    response = client.post("/api/voice/process", json={})
    assert response.status_code == 409
    assert "already in progress" in response.json()["detail"]
    assert len(client.executed) == 1
    assert len([n for n in client.get("/api/voice/notes").json() if n["run_id"] is None]) == 1


def test_asr_deadline_failure_is_a_service_error_and_releases_slot(client, monkeypatch):
    from pydantic import SecretStr

    client.app.state.settings.asr_api_key = SecretStr("fake")

    def timeout(*args, **kwargs):
        raise live.BudgetExceeded("synthetic deadline")

    monkeypatch.setattr(live.LLMClient, "transcribe", timeout)
    response = client.post("/api/voice/transcribe", files={"audio": ("a.wav", wav(), "audio/wav")})
    assert response.status_code == 502
    assert not live._ASR_SLOT.locked()


def test_a_run_from_before_snapshots_does_not_break_the_listing(client, tmp_path):
    import shutil

    from tesseract.api.routers.voice import snapshot_path

    old = post_note(client).json()
    (run,) = client.post("/api/voice/process", json={}).json()
    shutil.rmtree(snapshot_path(tmp_path, run["spec"]["run_id"]))  # created by older code
    new = post_note(client, transcript="Una cliente ha chiesto la sciarpa beige").json()
    response = client.get("/api/voice/notes")
    assert response.status_code == 200
    states = {n["note_id"]: n["run_id"] for n in response.json()}
    assert states == {old["note_id"]: run["spec"]["run_id"], new["note_id"]: None}
