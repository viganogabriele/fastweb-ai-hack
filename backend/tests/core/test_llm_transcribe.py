"""ASR-01 transcription through the LLM client: offline, no credentials or network."""

import httpx
import pytest
from openai import OpenAI
from pydantic import SecretStr

from tessera.core.cache import ReplayMiss
from tessera.core.config import MissingApiKey, Settings
from tessera.core.llm import LLMCallFailed, LLMClient

from .test_llm import run_spec

ASR_URL = "https://asr.example.test/v1"


def verbose(text="Tre clienti hanno chiesto il piumino Maya.", segments=None):
    if segments is None:
        segments = [
            {"id": 0, "start": 0.0, "end": 2.5, "text": " Tre clienti hanno chiesto"},
            {"id": 1, "start": 2.5, "end": 4.0, "text": " il piumino Maya."},
        ]
    return {
        "task": "transcribe",
        "language": "italian",
        "duration": 4.0,
        "text": text,
        "segments": segments,
    }


def client(tmp_path, replies, *, mode="record", key="asr-secret"):
    requests = []
    factories = []

    def respond(request):
        requests.append(request)
        reply = replies.pop(0)
        if isinstance(reply, int):
            return httpx.Response(reply, json={"detail": "refused"})
        return httpx.Response(200, json=reply)

    def factory(**kwargs):
        factories.append(kwargs)
        return OpenAI(**kwargs, http_client=httpx.Client(transport=httpx.MockTransport(respond)))

    settings = Settings(
        _env_file=None,
        llm_mode=mode,
        data_dir=tmp_path,
        asr_base_url=ASR_URL,
        asr_api_key=SecretStr(key) if key is not None else None,
        fastweb_keys_file=tmp_path / "absent.json",
    )
    return LLMClient(settings, client_factory=factory, sleep=lambda _: None), requests, factories


@pytest.fixture
def note(tmp_path):
    path = tmp_path / "MIL01 2026-10-21 manager.M4A"
    path.write_bytes(b"fake m4a bytes")
    return path


def test_record_then_replay_without_key_or_network(tmp_path, note):
    live, requests, factories = client(tmp_path, [verbose()])
    transcript = live.transcribe(note, language="it", prompt="Maya, Grenoble")

    assert transcript.text == "Tre clienti hanno chiesto il piumino Maya."
    assert transcript.language == "italian"
    assert [(s.start, s.end) for s in transcript.segments] == [(0.0, 2.5), (2.5, 4.0)]
    assert factories[0]["base_url"] == ASR_URL
    assert factories[0]["api_key"] == "asr-secret"
    (request,) = requests
    assert request.url.path == "/v1/audio/transcriptions"
    body = request.read()
    assert b'name="language"\r\n\r\nit\r\n' in body
    assert b'name="prompt"\r\n\r\nMaya, Grenoble\r\n' in body
    assert b'name="response_format"\r\n\r\nverbose_json\r\n' in body
    assert b'name="model"\r\n\r\nwhisper-large-v3-turbo\r\n' in body
    # The original file name (store, author) never leaves the machine.
    assert b'filename="audio.m4a"' in body and b"MIL01" not in body
    assert live.traces[-1]["operation"] == "transcribe"

    replay, _, _ = client(tmp_path, [], mode="replay", key=None)
    replay._factory = lambda **kw: pytest.fail("network client in replay")
    assert replay.transcribe(note, language="it", prompt="Maya, Grenoble") == transcript
    assert replay.budget.calls == 0


def test_unset_optional_fields_are_not_sent(tmp_path, note):
    live, requests, _ = client(tmp_path, [verbose()])
    live.transcribe(note)
    body = requests[0].read()
    assert b'name="language"' not in body and b'name="prompt"' not in body


def test_key_follows_audio_bytes_language_and_prompt_not_file_name(tmp_path, note):
    live, requests, _ = client(tmp_path, [verbose()] * 4)
    live.transcribe(note, language="it")
    renamed = note.with_name("copy.m4a")
    renamed.write_bytes(note.read_bytes())
    live.transcribe(renamed, language="it")
    assert len(requests) == 1

    live.transcribe(note, language="en")
    live.transcribe(note, language="it", prompt="Maya")
    note.write_bytes(b"other audio")
    live.transcribe(note, language="it")
    assert len(requests) == 4


def test_replay_miss_is_explicit(tmp_path, note):
    replay, requests, _ = client(tmp_path, [], mode="replay")
    with pytest.raises(ReplayMiss):
        replay.transcribe(note)
    assert requests == []


def test_live_without_key_names_no_secret(tmp_path, note):
    live, requests, _ = client(tmp_path, [], key="")
    with pytest.raises(MissingApiKey, match="ASR_API_KEY"):
        live.transcribe(note)
    assert requests == []


def test_busy_server_is_retried(tmp_path, note):
    live, requests, _ = client(tmp_path, [429, verbose()])
    assert live.transcribe(note).segments
    assert len(requests) == 2


@pytest.mark.parametrize("status", [400, 401, 413])
def test_client_errors_are_not_retried_and_hide_the_detail(tmp_path, note, status):
    live, requests, _ = client(tmp_path, [status, verbose()])
    with pytest.raises(LLMCallFailed, match=f"status={status}") as error:
        live.transcribe(note)
    assert "refused" not in str(error.value)
    assert len(requests) == 1


@pytest.mark.parametrize(
    "segments",
    [
        [{"start": 3.0, "end": 1.0, "text": "backwards"}],
        [{"start": -1.0, "end": 1.0, "text": "negative"}],
        [{"start": 0.0, "text": "no end"}],
    ],
)
def test_invalid_segments_are_refused(tmp_path, note, segments):
    live, _, _ = client(tmp_path, [verbose(segments=segments)])
    with pytest.raises(LLMCallFailed, match="invalid transcription"):
        live.transcribe(note)


def test_empty_audio_is_refused_before_any_call(tmp_path):
    empty = tmp_path / "empty.wav"
    empty.write_bytes(b"")
    live, requests, _ = client(tmp_path, [])
    with pytest.raises(ValueError, match="empty"):
        live.transcribe(empty)
    assert requests == []


def test_run_binding_scopes_transcriptions(tmp_path, note):
    live, requests, _ = client(tmp_path, [verbose(), verbose()])
    live.for_run(run_spec()).transcribe(note)
    live.for_run(run_spec(run_id="another-execution")).transcribe(note)
    assert len(requests) == 1
    live.for_run(run_spec(as_of="2026-10-22T20:00:00Z")).transcribe(note)
    assert len(requests) == 2
