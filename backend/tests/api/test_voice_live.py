"""DEMO-04: live voice notes from /store/record, saved for src.voice and run on demand."""

import io
import json
import wave
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from tessera.api.main import create_app
from tessera.api.routers import voice as live
from tessera.core.config import Settings
from tessera.core.db import connect
from tessera.core.orchestrator import _plan
from tessera.core.registry import Registry
from tessera.modules.sources import voice
from tessera.modules.sources.emails import Store
from tessera.modules.sources.voice_inbox import list_notes, save_note

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
        settings=Settings(data_dir=tmp_path, asr_api_key=None),
    )
    with TestClient(app) as test_client:
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
    assert note.sidecar.sent_at.utcoffset() is not None
    audio = voice.load_audio(note)  # converted to 16 kHz mono wav, hash checked
    with wave.open(str(audio.path)) as reader:
        assert (reader.getframerate(), reader.getnchannels()) == (16000, 1)
    assert voice.manual_transcript(note) == "Due clienti hanno chiesto il gilet blu"
    assert [n["note_id"] for n in client.get("/api/voice/notes").json()] == [body["note_id"]]


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
    assert snapshots["src.voice"].params == {"notes": [first["note_id"]]}
    for snapshot in spec.modules:
        registry.resolve(snapshot)  # installed manifests and valid params
    plan = _plan(spec, None)
    assert plan.index("src.voice") < plan.index("ing.extract") < plan.index("int.cases")
    assert all(n.run_id for n in list_notes(tmp_path))
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

    monkeypatch.setattr(live.LLMClient, "transcribe", fake)
    response = client.post(
        "/api/voice/transcribe",
        data={"language": "it"},
        files={"audio": ("blob", b"x", "audio/webm;codecs=opus")},
    )
    assert response.json() == {"text": "Ciao dal negozio", "duration_s": 1.0}
    assert seen == {"mode": "live", "suffix": ".webm", "language": "it"}


def test_src_voice_reads_inbox_notes_next_to_fixtures(tmp_path, monkeypatch):
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
    assert result.counts["notes"] == 1
    assert stored[0].text == "Nota live"
    assert json.loads((note.directory / "note.json").read_text())["fixture_kind"] == "live"


class FakeLLM:
    """No ASR (the declared transcript is used) and one extracted unmet-demand fact."""

    def transcribe(self, *args, **kwargs):
        raise RuntimeError("no ASR in tests")

    def extract(self, schema, messages, **kwargs):
        from tessera.modules.ingestion.extract import Candidates

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

    from tessera.core.contracts import Case
    from tessera.core.orchestrator import run
    from tessera.core.run_repo import repo_session

    settings = Settings(data_dir=tmp_path)
    text = "Due clienti volevano il gilet VEL blu notte in taglia 3, ma non ce l'avevamo."
    save_note("MIL01", ROME, wav(), "wav", text, language="it", data_dir=tmp_path)
    monkeypatch.setattr(voice, "voice_path", lambda: tmp_path / "fixtures" / "voice")
    monkeypatch.setattr(voice, "inbox_path", lambda: tmp_path / "voice_inbox")
    registry = Registry.discover()
    spec = live.live_spec(
        registry, "MIL01", list_notes(tmp_path), datetime.now(UTC).replace(microsecond=0)
    )
    engine = connect(f"sqlite:///{tmp_path / 'test.db'}")
    with repo_session(engine, spec, fixture_mode=False, write=True):
        pass
    statuses = run(
        spec, engine=engine, registry=registry, clients={"llm": FakeLLM()}, settings=settings
    )
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
    from tessera.core.run_repo import repo_session

    post_note(client)
    (run,) = client.post("/api/voice/process", json={}).json()
    assert client.post("/api/voice/process", json={}).status_code == 409
    engine = client.app.state.engines["product"]
    with repo_session(engine, run["spec"]["run_id"], fixture_mode=False, write=True) as repo:
        repo.set_run_status("failed")
    assert [n["run_id"] for n in client.get("/api/voice/notes").json()] == [None]
    (again,) = client.post("/api/voice/process", json={}).json()
    assert again["spec"]["run_id"] != run["spec"]["run_id"]
