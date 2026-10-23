"""src.voice: recorded ASR segments, the declared transcript and the fallback between them."""

import hashlib
import json

import pytest
from pydantic import ValidationError

from tessera.core.contracts import ModuleSnapshot, RunSpec, SourceDocument
from tessera.core.db import connect
from tessera.core.fixtures import read_fixtures
from tessera.core.llm import Transcript, TranscriptSegment
from tessera.core.orchestrator import run
from tessera.core.registry import RegisteredModule, Registry
from tessera.core.run_repo import repo_session
from tessera.modules.sources import voice
from tessera.modules.sources.voice import MANIFEST, Sidecar

AS_OF = "2026-10-22T20:00:00+00:00"
SENT = "2026-10-09T18:40:00+02:00"
TRANSCRIPT = "Ciao, il cardigan taglia M non c'e piu, ne ho venduti sette."
AUDIO = b"RIFF....WAVEfmt fake audio bytes for the test"
DIGEST = "sha256:" + hashlib.sha256(AUDIO).hexdigest()
ZERO = dict.fromkeys(
    ("notes", "documents", "segments", "recorded", "declared", "not_in_run", "not_available"), 0
)


def payload(**overrides):
    data = {
        "note_id": "mil01-cardigan",
        "store_id": "MIL01",
        "sent_at": SENT,
        "timezone": "Europe/Rome",
        "language": "it",
        "author_ref": "pseudonym:mil01-manager",
        "fixture_kind": "paraphrase",
        "audio": "cardigan.wav",
        "audio_sha256": DIGEST,
        "duration_s": 38.4,
        "related_source_refs": ["dataset://store_emails/MIL01/20261009_1035_MIL01.eml"],
    }
    data.update(overrides)
    return data


def note_dir(root, slug="mil01-cardigan", audio_bytes=AUDIO, **overrides):
    overrides.setdefault("note_id", slug)
    directory = root / slug
    directory.mkdir(parents=True)
    (directory / "cardigan.wav").write_bytes(audio_bytes)
    (directory / "transcript.txt").write_text(TRANSCRIPT, encoding="utf-8")
    (directory / "note.json").write_text(json.dumps(payload(**overrides)), encoding="utf-8")
    return directory


def asr(*pieces, text=None, language="it", duration=3.5):
    segments = tuple(
        TranscriptSegment(start=start, end=end, text=piece) for start, end, piece in pieces
    )
    return Transcript(
        text=text if text is not None else "".join(p for _, _, p in pieces),
        language=language,
        duration=duration,
        segments=segments,
    )


TRANSCRIPT_ASR = asr(
    (0.0, 1.8, "Ciao, il cardigan "),
    (1.8, 3.0, "taglia M non c'e piu, "),
    (3.0, 4.6, "ne ho venduti sette."),
)


class FakeASR:
    def __init__(self, transcript=None, error=None):
        self.transcript = TRANSCRIPT_ASR if transcript is None else transcript
        self.error = error
        self.calls = []

    def transcribe(self, path, language=None, prompt=None, *, model=None, cache_context=None):
        self.calls.append(
            {
                "path": path,
                "language": language,
                "prompt": prompt,
                "model": model,
                "cache_context": cache_context,
            }
        )
        if self.error is not None:
            raise self.error
        return self.transcript


def spec(params=None, as_of=AS_OF, stores=("MIL01",)):
    return RunSpec(
        run_id="voice-run",
        scenario_id="historical",
        as_of=as_of,
        stores=stores,
        source_manifest_hash="sources",
        config_hash="config",
        code_version="test",
        mode="live",
        modules=(ModuleSnapshot(manifest=MANIFEST, params=params or {}),),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )


def execute(tmp_path, request, voice_dir, client=None):
    engine = connect(f"sqlite:///{tmp_path / 'voice.db'}")
    module = RegisteredModule(
        MANIFEST, lambda ctx: voice.run(ctx, voice_dir=voice_dir, client=client)
    )
    statuses = run(request, engine=engine, registry=Registry((module,)), clients={"llm": client})
    return engine, statuses[0].result


def published(engine, request):
    with repo_session(engine, request) as repo:
        return repo.list(SourceDocument)


def test_registry_discovers_src_voice():
    assert MANIFEST in Registry.discover().manifests()


def test_recorded_note_is_one_segment_per_asr_segment(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir)
    client = FakeASR()
    request = spec()
    engine, status = execute(tmp_path, request, voice_dir, client)
    assert status.status == "succeeded"
    assert status.counts == {**ZERO, "notes": 1, "documents": 1, "segments": 3, "recorded": 1}
    (document,) = published(engine, request)
    assert document.id == "doc-voice-mil01-cardigan"
    assert document.source_type == "voice_note"
    assert document.connector == "src.voice"
    assert document.origin == "voice"
    assert document.language == "it"
    assert document.author_ref == "pseudonym:mil01-manager"
    assert document.available_at.isoformat() == "2026-10-09T16:40:00+00:00"
    assert document.business_date.isoformat() == "2026-10-09"
    assert document.text == TRANSCRIPT
    assert document.text_version == voice.ASR_TEXT_VERSION
    assert document.content_hash == DIGEST
    assert document.meta["transcript_mode"] == "recorded"
    assert document.meta["asr_model"] == voice.get_settings().asr_model
    assert document.meta["asr_text"] == TRANSCRIPT
    assert document.meta["fixture_kind"] == "paraphrase"
    with repo_session(engine, request) as repo:
        segments = sorted(repo.list(voice.Segment), key=lambda s: s.idx)
    assert [(s.char_start, s.char_end) for s in segments] == [
        (0, len("Ciao, il cardigan ")),
        (len("Ciao, il cardigan "), len("Ciao, il cardigan taglia M non c'e piu, ")),
        (len("Ciao, il cardigan taglia M non c'e piu, "), len(TRANSCRIPT)),
    ]
    assert [(s.t_start_s, s.t_end_s) for s in segments] == [
        (0.0, 1.8),
        (1.8, 3.0),
        (3.0, 4.6),
    ]
    assert [s.text for s in segments] == [
        "Ciao, il cardigan ",
        "taglia M non c'e piu, ",
        "ne ho venduti sette.",
    ]
    for segment in segments:
        segment.validate_against(document)


def test_recorded_note_calls_the_asr_with_the_declared_hints(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir, asr_prompt="cardigan")
    client = FakeASR()
    execute(tmp_path, spec(), voice_dir, client)
    (call,) = client.calls
    assert call["language"] == "it"
    assert call["prompt"] == "cardigan"
    assert call["path"].name == "cardigan.wav"
    assert call["cache_context"] == {
        "note_id": "mil01-cardigan",
        "store_id": "MIL01",
        "fixture_kind": "paraphrase",
    }


def test_language_hint_is_the_base_tag_and_none_when_unknown(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir, slug="a-one", language="pt-BR")
    note_dir(voice_dir, slug="b-two", language=None)
    client = FakeASR()
    execute(tmp_path, spec(), voice_dir, client)
    assert [c["language"] for c in client.calls] == ["pt", None]


def test_fixture_mode_never_calls_the_asr_and_keeps_no_intervals(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir)
    client = FakeASR()
    request = spec(params={"mode": "fixture"})
    engine, status = execute(tmp_path, request, voice_dir, client)
    assert client.calls == []
    assert status.counts == {**ZERO, "notes": 1, "documents": 1, "segments": 1, "declared": 1}
    assert status.abstentions == ()
    (document,) = published(engine, request)
    assert document.text == TRANSCRIPT
    assert document.text_version == voice.DECLARED_TEXT_VERSION
    assert document.meta["transcript_mode"] == "fixture"
    with repo_session(engine, request) as repo:
        (segment,) = repo.list(voice.Segment)
    assert (segment.char_start, segment.char_end) == (0, len(TRANSCRIPT))
    assert (segment.t_start_s, segment.t_end_s) == (None, None)


def test_asr_failure_falls_back_to_the_declared_transcript(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir)
    request = spec()
    engine, status = execute(tmp_path, request, voice_dir, FakeASR(error=OSError("no route")))
    assert status.status == "degraded"
    assert status.counts["declared"] == 1
    assert status.counts["recorded"] == 0
    (abstention,) = status.abstentions
    assert "ASR unavailable (OSError: no route)" in abstention
    (document,) = published(engine, request)
    assert document.text == TRANSCRIPT
    assert document.meta["transcript_mode"] == "fixture"
    with repo_session(engine, request) as repo:
        (segment,) = repo.list(voice.Segment)
    assert (segment.t_start_s, segment.t_end_s) == (None, None)


def test_asr_without_usable_segments_falls_back(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir)
    request = spec()
    empty = Transcript(text="", language=None, duration=None, segments=())
    engine, status = execute(tmp_path, request, voice_dir, FakeASR(transcript=empty))
    assert status.status == "degraded"
    assert status.counts["declared"] == 1
    assert "UnusableTranscript" in status.abstentions[0]
    (document,) = published(engine, request)
    assert document.text == TRANSCRIPT


def test_audio_must_match_the_declared_hash(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir, audio_sha256="sha256:" + "0" * 64)
    client = FakeASR()
    engine, status = execute(tmp_path, spec(), voice_dir, client)
    assert status.status == "degraded"
    assert status.counts == ZERO
    assert "audio_sha256" in status.errors[0]
    assert client.calls == []
    assert published(engine, spec()) == []


def test_a_note_sent_after_as_of_is_not_read(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir, sent_at="2026-10-23T09:00:00+02:00")
    client = FakeASR()
    engine, status = execute(tmp_path, spec(), voice_dir, client)
    assert status.status == "succeeded"
    assert status.counts == {**ZERO, "not_available": 1}
    assert client.calls == []
    assert published(engine, spec()) == []


def test_a_note_at_the_as_of_instant_is_available(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir, sent_at=AS_OF)
    engine, status = execute(tmp_path, spec(as_of=AS_OF), voice_dir, FakeASR())
    assert status.counts["documents"] == 1


def test_a_note_for_a_store_outside_the_run_is_skipped(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir, store_id="PAR01")
    client = FakeASR()
    engine, status = execute(tmp_path, spec(stores=("MIL01",)), voice_dir, client)
    assert status.counts == {**ZERO, "not_in_run": 1}
    assert client.calls == []


def test_notes_param_selects_a_subset_and_reports_unknown_slugs(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir, slug="a-one")
    note_dir(voice_dir, slug="b-two", audio="cardigan.wav")
    request = spec(params={"notes": ["b-two", "missing"]})
    engine, status = execute(tmp_path, request, voice_dir, FakeASR())
    assert [d.id for d in published(engine, request)] == ["doc-voice-b-two"]
    (error,) = status.errors
    assert "no such note: missing" in error or "no such note" in error


def test_business_date_uses_the_note_timezone(tmp_path):
    voice_dir = tmp_path / "voice"
    # 23:30 UTC on 9 October is already the 10th in Rome.
    note_dir(voice_dir, sent_at="2026-10-09T23:30:00+00:00")
    request = spec()
    engine, _ = execute(tmp_path, request, voice_dir, FakeASR())
    (document,) = published(engine, request)
    assert document.available_at.isoformat() == "2026-10-09T23:30:00+00:00"
    assert document.business_date.isoformat() == "2026-10-10"


def test_the_manual_transcript_hash_is_the_reference(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir)
    request = spec()
    engine, _ = execute(tmp_path, request, voice_dir, FakeASR())
    (document,) = published(engine, request)
    assert document.meta["manual_transcript"] == "transcript.txt"
    assert document.meta["manual_transcript_sha256"] == (
        "sha256:" + hashlib.sha256(TRANSCRIPT.encode()).hexdigest()
    )


def test_replay_without_a_recording_falls_back_explicitly(tmp_path):
    from tessera.core.config import Settings
    from tessera.core.llm import LLMClient

    voice_dir = tmp_path / "voice"
    note_dir(voice_dir)
    settings = Settings(llm_mode="replay", data_dir=tmp_path / "data")
    request = spec()
    client = LLMClient(settings).for_run(request)
    engine = connect(f"sqlite:///{tmp_path / 'voice.db'}")
    module = RegisteredModule(
        MANIFEST, lambda ctx: voice.run(ctx, voice_dir=voice_dir, client=client)
    )
    statuses = run(request, engine=engine, registry=Registry((module,)), clients={"llm": client})
    result = statuses[0].result
    assert result.status == "degraded"
    assert result.counts["declared"] == 1
    assert "ReplayMiss" in result.abstentions[0]
    (document,) = published(engine, request)
    assert document.meta["transcript_mode"] == "fixture"
    assert document.text == TRANSCRIPT


def test_missing_voice_dir_is_an_explicit_abstention(tmp_path):
    engine, status = execute(tmp_path, spec(), tmp_path / "voice", FakeASR())
    assert status.status == "succeeded"
    assert status.counts == ZERO
    assert "no voice notes" in status.abstentions[0]


def test_a_voice_dir_without_notes_is_an_explicit_abstention(tmp_path):
    voice_dir = tmp_path / "voice"
    voice_dir.mkdir()
    (voice_dir / "README.md").write_text("layout", encoding="utf-8")
    engine, status = execute(tmp_path, spec(), voice_dir, FakeASR())
    assert status.status == "succeeded"
    assert status.counts == ZERO
    assert "no voice notes" in status.abstentions[0]


def test_an_empty_manual_transcript_is_an_error(tmp_path):
    voice_dir = tmp_path / "voice"
    directory = note_dir(voice_dir)
    (directory / "transcript.txt").write_text("  \n", encoding="utf-8")
    engine, status = execute(tmp_path, spec(), voice_dir, FakeASR())
    assert status.status == "degraded"
    assert "manual transcript is empty" in status.errors[0]
    assert published(engine, spec()) == []


def test_a_folder_without_a_sidecar_is_reported(tmp_path):
    voice_dir = tmp_path / "voice"
    (voice_dir / "half-recorded").mkdir(parents=True)
    engine, status = execute(tmp_path, spec(), voice_dir, FakeASR())
    assert status.status == "degraded"
    assert "unreadable note.json" in status.errors[0]


@pytest.mark.parametrize(
    "overrides",
    [
        {"sent_at": "2026-10-09T18:40:00"},
        {"timezone": "Mars/Olympus"},
        {"fixture_kind": "guess"},
        {"audio": "../outside.wav"},
        {"manual_transcript": "/etc/passwd"},
        {"audio_sha256": DIGEST.removeprefix("sha256:")},
        {"language": "Italian"},
    ],
)
def test_the_sidecar_rejects_ambiguous_metadata(overrides):
    with pytest.raises(ValidationError):
        Sidecar.model_validate(payload(**overrides))


def test_the_sidecar_is_closed(tmp_path):
    with pytest.raises(ValidationError):
        Sidecar.model_validate(payload(unexpected="value"))


def test_fixture_loader_ignores_nested_voice_sidecars(tmp_path):
    note_dir(tmp_path / "fixtures" / "voice")
    assert read_fixtures(tmp_path / "fixtures") == ([], [])


def test_a_note_id_must_match_its_folder(tmp_path):
    voice_dir = tmp_path / "voice"
    note_dir(voice_dir, slug="folder-name", note_id="another-name")
    engine, status = execute(tmp_path, spec(), voice_dir, FakeASR())
    assert status.status == "degraded"
    assert "note_id must match the folder name" in status.errors[0]
