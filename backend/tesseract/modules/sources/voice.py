"""ING-03 module: ``src.voice`` reads store voice notes as documents and segments.

A note lives in ``data/fixtures/voice/<slug>/`` (RFC §5.2) with three files: ``note.json``
(sidecar metadata), the audio it names, and ``transcript.txt`` (the manual transcript written
when the team recorded the note). Both modes publish the same document shape, so everything
downstream (evidence, extraction, cases) is unchanged:

- ``recorded`` (default): the audio goes to the team ASR server through ``transcribe()``; the
  canonical text is the ASR segments concatenated in order, and one ``Segment`` per ASR segment
  carries the real ``t_start_s``/``t_end_s``. Nothing is estimated: if the response has no
  usable segments, the note is not published as recorded.
- ``fixture``: the declared manual transcript is the canonical text, one segment, no intervals.
  A reader can still cite the words of the note, but audio evidence has no fake timestamps
  (RFC §5.2: the UI shows the transcript and the whole audio).

The declared transcript is also the *fallback* in ``recorded`` mode when the ASR server is
unreachable (or the response is unusable): the note is still published, with
``meta.transcript_mode = "fixture"`` and an abstention saying why. The manual transcript is the
reference used to check the ASR, so its hash travels in ``meta`` for both modes.

Availability is the note's ``sent_at`` (an instant with offset, plus the IANA zone used for the
store's business date), never the recording time of a file on disk: a note sent after ``as_of``
is not read, and its audio is not even opened. The sidecar declares the audio's SHA-256; a file
whose bytes differ from the declared hash is an error, because its transcript was checked
against different audio. Notes for stores outside the run are skipped, like other sources.

Live notes (DEMO-04) use immutable, explicitly queued ``data/voice_runs/<run_id>/`` snapshots.
Their accepted, possibly edited text is published as manual text without audio intervals.
Ordinary runs never read the live inbox or snapshots.
"""

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import model_validator

from tesseract.core.config import get_settings
from tesseract.core.contracts import ModuleManifest, ModuleResult, Segment, SourceDocument
from tesseract.core.contracts.common import Contract, Instant, NonNegative, Text

VOICE_DIR = "fixtures/voice"
INBOX_DIR = "voice_inbox"
NOTE_FILE = "note.json"
DEFAULT_TRANSCRIPT = "transcript.txt"
DOC_VERSION = "v1"
ASR_TEXT_VERSION = "voice-asr-v1"
DECLARED_TEXT_VERSION = "voice-transcript-v1"
ASR_BASIS = "ASR segments concatenated in order; intervals are the server's, never estimated"
DECLARED_BASIS = "declared manual transcript; no audio intervals"
LANGUAGE = re.compile(r"^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")

MANIFEST = ModuleManifest(
    id="src.voice",
    version="1",
    layer="sources",
    description="Store voice notes: ASR segments with real intervals, or the declared transcript",
    requires=(),
    optional_inputs=(),
    produces=("SourceDocument", "Segment"),
    enabled=True,
    mode="recorded",
    params_schema={
        "type": "object",
        "properties": {
            "mode": {"enum": ["recorded", "fixture"]},
            "notes": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "minItems": 1,
                "uniqueItems": True,
            },
        },
        "additionalProperties": False,
    },
)


class Sidecar(Contract):
    """``note.json``: what the note is, who sent it, and which bytes the transcript describes."""

    note_id: Text
    store_id: str
    sent_at: Instant
    timezone: Text
    language: str | None = None
    author_ref: Text
    fixture_kind: Literal["paraphrase", "synthetic_extension", "live"]
    audio: Text
    audio_sha256: str
    duration_s: NonNegative | None = None
    manual_transcript: Text = DEFAULT_TRANSCRIPT
    related_source_refs: tuple[Text, ...] = ()
    asr_prompt: str | None = None

    @model_validator(mode="after")
    def files_and_zone(self) -> "Sidecar":
        for name in (self.audio, self.manual_transcript):
            if Path(name).name != name or name in (".", ".."):
                raise ValueError("audio and transcript must be plain file names in the note folder")
        if not SHA256.fullmatch(self.audio_sha256):
            raise ValueError("audio_sha256 must be 'sha256:' plus 64 lowercase hex digits")
        if self.language is not None and not LANGUAGE.fullmatch(self.language):
            raise ValueError("language must be a language tag such as 'it' or 'pt-BR'")
        try:
            ZoneInfo(self.timezone)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError(f"unknown IANA timezone: {self.timezone}") from None
        return self


class UnusableTranscript(ValueError):
    """The ASR answered, but not with text that can become segments."""


@dataclass(frozen=True)
class Note:
    slug: str
    directory: Path
    sidecar: Sidecar

    @property
    def uri(self) -> str:
        if self.sidecar.fixture_kind == "live":
            return f"live-voice://{self.directory.parent.name}/{self.slug}"
        return f"dataset://voice/{self.slug}"

    @property
    def audio_path(self) -> Path:
        return note_file(self.directory, self.sidecar.audio)

    @property
    def transcript_path(self) -> Path:
        return note_file(self.directory, self.sidecar.manual_transcript)


@dataclass(frozen=True)
class Audio:
    path: Path
    sha256: str
    size: int


def voice_path(data_dir: Path | None = None) -> Path:
    return (data_dir or get_settings().data_dir) / VOICE_DIR


def inbox_path(data_dir: Path | None = None) -> Path:
    return (data_dir or get_settings().data_dir) / INBOX_DIR


def note_file(directory: Path, name: str) -> Path:
    """Every source file stays in its real note folder; never follow source symlinks."""
    path = directory / name
    if (
        directory.is_symlink()
        or path.is_symlink()
        or Path(name).name != name
        or path.resolve().parent != directory.resolve()
    ):
        raise ValueError("voice files must live in the note folder without symlinks")
    return path


def read_sidecar(directory: Path) -> Note:
    """Read ``note.json`` only: availability and store filtering need no audio bytes."""
    path = note_file(directory, NOTE_FILE)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"unreadable {NOTE_FILE}: {type(error).__name__}") from None
    if not isinstance(raw, dict):
        raise ValueError(f"{NOTE_FILE} must be a JSON object")
    sidecar = Sidecar.model_validate(raw)
    if sidecar.note_id != directory.name:
        raise ValueError("note_id must match the folder name")
    return Note(directory.name, directory, sidecar)


def load_audio(note: Note) -> Audio:
    """The declared notes are only read once the note is in the run and available."""
    path = note.audio_path
    if path.resolve().parent != note.directory.resolve():
        raise ValueError("audio must live in the note folder")
    try:
        data = path.read_bytes()
    except OSError as error:
        raise ValueError(f"cannot read audio: {type(error).__name__}") from None
    if not data:
        raise ValueError("empty audio file")
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    if digest != note.sidecar.audio_sha256:
        raise ValueError("audio does not match the declared audio_sha256")
    return Audio(path, digest, len(data))


def manual_transcript(note: Note) -> str:
    try:
        text = note.transcript_path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"cannot read the manual transcript: {type(error).__name__}") from None
    if not text.strip():
        raise ValueError("the manual transcript is empty")
    return text.strip()


def _common(note: Note, audio: Audio) -> dict:
    return {
        "version": DOC_VERSION,
        "available_at": note.sidecar.sent_at,
        "availability_basis": "voice_note_sent_at",
        "source_refs": ({"uri": note.uri, "content_hash": audio.sha256},),
    }


def _meta(note: Note, audio: Audio, *, transcript: str, mode: str, basis: str) -> dict:
    sidecar = note.sidecar
    return {
        "note_id": note.slug,
        "store_id": sidecar.store_id,
        "fixture_kind": sidecar.fixture_kind,
        "timezone": sidecar.timezone,
        "sent_at": sidecar.sent_at.isoformat(),
        "audio": sidecar.audio,
        "audio_bytes": audio.size,
        "audio_sha256": audio.sha256,
        "duration_s": sidecar.duration_s,
        "language": sidecar.language,
        "author_ref": sidecar.author_ref,
        "transcript_mode": mode,
        "manual_transcript": sidecar.manual_transcript,
        "manual_transcript_sha256": "sha256:" + hashlib.sha256(transcript.encode()).hexdigest(),
        "related_source_refs": list(sidecar.related_source_refs),
        "text": basis,
    }


def _document(
    note: Note,
    audio: Audio,
    *,
    text: str,
    text_version: str,
    transcript: str,
    mode: str,
    basis: str,
    meta: dict | None = None,
) -> SourceDocument:
    sidecar = note.sidecar
    return SourceDocument(
        id=f"doc-voice-{note.slug}",
        **_common(note, audio),
        source_type="voice_note",
        connector=MANIFEST.id,
        uri=note.uri,
        content_hash=audio.sha256,
        origin="voice",
        author_ref=sidecar.author_ref,
        language=sidecar.language,
        business_date=sidecar.sent_at.astimezone(ZoneInfo(sidecar.timezone)).date(),
        thread_key=None,
        parent_document_id=None,
        text=text,
        text_version=text_version,
        meta={
            **_meta(note, audio, transcript=transcript, mode=mode, basis=basis),
            **(meta or {}),
        },
    )


def declared_document(note: Note, audio: Audio) -> tuple[SourceDocument, list[Segment]]:
    """The manual transcript: citable words, and honestly no audio intervals."""
    text_version = DECLARED_TEXT_VERSION
    text = manual_transcript(note)
    document = _document(
        note,
        audio,
        text=text,
        text_version=text_version,
        transcript=text,
        mode="manual" if note.sidecar.fixture_kind == "live" else "fixture",
        basis="store-accepted text (possibly edited); no audio intervals"
        if note.sidecar.fixture_kind == "live"
        else DECLARED_BASIS,
    )
    segment = Segment(
        id=f"{document.id}-seg0",
        **_common(note, audio),
        document_id=document.id,
        text_version=text_version,
        idx=0,
        text=text,
        char_start=0,
        char_end=len(text),
        locator=None,
        t_start_s=None,
        t_end_s=None,
        is_quoted=False,
    )
    segment.validate_against(document)
    return document, [segment]


def recorded_document(
    note: Note, audio: Audio, transcript, *, model: str
) -> tuple[SourceDocument, list[Segment]]:
    """One segment per ASR segment; the document text is those segments, in order, verbatim."""
    segments = [s for s in transcript.segments if s.text]
    text = "".join(s.text for s in segments)
    if not segments or not text.strip():
        raise UnusableTranscript("the ASR returned no usable segments")
    for piece in segments:
        if piece.end <= piece.start:
            raise UnusableTranscript("the ASR returned an empty or reversed interval")
        if note.sidecar.duration_s is not None and piece.end > note.sidecar.duration_s:
            raise UnusableTranscript(
                f"ASR interval ends at {piece.end:g}s beyond audio duration "
                f"{note.sidecar.duration_s:g}s"
            )
    doc_id = f"doc-voice-{note.slug}"
    text_version = ASR_TEXT_VERSION
    segments_out: list[Segment] = []
    offset = 0
    for index, piece in enumerate(segments):
        segments_out.append(
            Segment(
                id=f"{doc_id}-seg{index}",
                **_common(note, audio),
                document_id=doc_id,
                text_version=text_version,
                idx=index,
                text=piece.text,
                char_start=offset,
                char_end=offset + len(piece.text),
                locator=None,
                t_start_s=piece.start,
                t_end_s=piece.end,
                is_quoted=False,
            )
        )
        offset += len(piece.text)
    document = _document(
        note,
        audio,
        text=text,
        text_version=text_version,
        transcript=manual_transcript(note),
        mode="recorded",
        basis=ASR_BASIS,
        meta={
            "asr_model": model,
            "asr_text": transcript.text,
            "asr_language": transcript.language,
            "asr_duration_s": transcript.duration,
        },
    )
    for segment in segments_out:
        segment.validate_against(document)
    return document, segments_out


def _language_hint(sidecar: Sidecar) -> str | None:
    """Pass a language only when the sidecar states it (RFC §4.7, OQ-3)."""
    return sidecar.language.split("-")[0] if sidecar.language else None


def run(ctx, *, voice_dir: Path | None = None, client=None) -> ModuleResult:
    live_run = getattr(ctx.spec, "scenario_id", None) == "live-voice"
    if live_run:
        from tesseract.modules.sources.voice_inbox import snapshot_path

        settings = getattr(ctx.clients.get("llm"), "settings", None) or get_settings()
        roots = [snapshot_path(settings.data_dir, ctx.spec.run_id)]
        if not roots[0].is_dir():
            raise ValueError("live voice snapshot is missing")
    else:
        roots = [voice_dir] if voice_dir else [voice_path()]
    mode = str(ctx.params.get("mode") or "recorded")
    if mode not in ("recorded", "fixture"):
        raise ValueError(f"unknown voice mode: {mode}")
    wanted = tuple(ctx.params.get("notes") or ())
    counts = dict.fromkeys(
        ("notes", "documents", "segments", "recorded", "declared", "not_in_run", "not_available"),
        0,
    )
    errors: list[str] = []
    abstentions: list[str] = []
    roots = [root for root in roots if root.is_dir()]
    if not roots:
        abstentions.append("no voice notes folder")
        return ModuleResult(
            module_id=MANIFEST.id,
            module_version=MANIFEST.version,
            status="succeeded",
            counts=counts,
            errors=(),
            abstentions=tuple(abstentions),
        )
    notes: list[Note] = []
    for directory in sorted(d for root in roots for d in root.iterdir()):
        if not directory.is_dir() or directory.name.startswith("."):
            continue
        if wanted and directory.name not in wanted:
            continue
        try:
            notes.append(read_sidecar(directory))
        except ValueError as error:
            errors.append(f"voice/{directory.name}: {error}")
    found = {note.slug for note in notes}
    if live_run:
        from tesseract.modules.sources.voice_inbox import LiveNote, batch_hash

        if batch_hash([LiveNote(n, "", None) for n in notes]) != ctx.spec.source_manifest_hash:
            raise ValueError("live voice snapshot does not match the source manifest hash")
    for slug in wanted:
        if slug not in found:
            errors.append(f"voice/{slug}: no such note")
    if not notes and not errors:
        abstentions.append(f"no voice notes under {', '.join(map(str, roots))}")
    for note in notes:
        sidecar = note.sidecar
        if sidecar.fixture_kind == "live" and not live_run:
            continue
        if sidecar.store_id not in ctx.spec.stores:
            counts["not_in_run"] += 1
            continue
        if sidecar.sent_at > ctx.spec.as_of:
            # A later note is future information: its audio is not opened either.
            counts["not_available"] += 1
            continue
        try:
            audio = load_audio(note)
            manual_transcript(note)
        except ValueError as error:
            errors.append(f"{note.uri}: {error}")
            continue
        document = None
        segments: list[Segment] = []
        if mode == "recorded" and sidecar.fixture_kind != "live":
            llm = client if client is not None else ctx.clients["llm"]
            try:
                transcript = llm.transcribe(
                    audio.path,
                    _language_hint(sidecar),
                    sidecar.asr_prompt,
                    cache_context={
                        "note_id": note.slug,
                        "store_id": sidecar.store_id,
                        "fixture_kind": sidecar.fixture_kind,
                    },
                )
                document, segments = recorded_document(
                    note, audio, transcript, model=get_settings().asr_model
                )
            except Exception as error:
                # A source must never fail the run; the declared transcript is the fallback.
                abstentions.append(
                    f"{note.uri}: ASR unavailable ({type(error).__name__}: {error}); "
                    "declared transcript used"
                )
        if document is None:
            document, segments = declared_document(note, audio)
            counts["declared"] += 1
        else:
            counts["recorded"] += 1
        ctx.repo.put(document, *segments)
        counts["notes"] += 1
        counts["documents"] += 1
        counts["segments"] += len(segments)
    return ModuleResult(
        module_id=MANIFEST.id,
        module_version=MANIFEST.version,
        status="degraded" if errors or (mode == "recorded" and counts["declared"]) else "succeeded",
        counts=counts,
        errors=tuple(errors),
        abstentions=tuple(abstentions),
    )
