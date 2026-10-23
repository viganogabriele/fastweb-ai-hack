"""DEMO-04: live store voice notes recorded from ``/store/record``, saved for ``src.voice``.

A recording from the phone becomes ``data/voice_inbox/<note_id>/`` with the same three files as
a DATA-03 fixture: ``note.json`` (``fixture_kind: "live"``), ``note.wav`` (16 kHz mono PCM,
converted with ffmpeg because ``src.voice`` reads wav/mp3 only) and ``transcript.txt``, the live
ASR transcript the store accepted or edited. ``sent_at`` is the moment the note is saved,
in the store's zone: only runs with a later ``as_of`` read it.

Each queued run freezes these files into ``data/voice_runs/<run_id>/``. The committed run
spec is the processing claim; retries reuse the original snapshot rather than mutable inbox text.
"""

import hashlib
import json
import shutil
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

from tesseract.modules.sources.emails import Store
from tesseract.modules.sources.voice import NOTE_FILE, Note, inbox_path, note_file, read_sidecar

AUDIO_FILE = "note.wav"
TRANSCRIPT_FILE = "transcript.txt"
MAX_TRANSCRIPT_CHARS = 5000
MAX_SECONDS = 90


class RecordingUnavailable(RuntimeError):
    """The server cannot convert audio; this is not an invalid user recording."""


class InvalidRecording(ValueError):
    """The upload cannot become a note: no audio ffmpeg can decode, or an empty transcript."""


@dataclass(frozen=True)
class LiveNote:
    note: Note
    transcript: str
    run_id: str | None


def to_wav(audio: bytes, suffix: str) -> bytes:
    """Any browser recording (webm/opus, mp4/aac, ogg, wav) as 16 kHz mono PCM, no metadata."""
    formats = {
        "webm": "matroska",
        "mp4": "mov",
        "m4a": "mov",
        "ogg": "ogg",
        "wav": "wav",
        "mp3": "mp3",
        "aac": "aac",
    }
    if suffix.lstrip(".") not in formats:
        raise InvalidRecording("unsupported recording container")
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / f"in{suffix if suffix.startswith('.') else '.' + suffix}"
        target = Path(tmp) / AUDIO_FILE
        source.write_bytes(audio)
        # fmt: off
        cmd = [
            "ffmpeg", "-nostdin", "-v", "error", "-threads", "1",
            "-protocol_whitelist", "file,pipe", "-f", formats[suffix.lstrip(".")],
            "-i", str(source), "-map", "0:a:0", "-vn", "-sn", "-dn", "-t", "91",
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", "-map_metadata", "-1", str(target),
        ]
        # fmt: on
        try:
            done = subprocess.run(cmd, capture_output=True, timeout=60)
        except OSError:
            raise RecordingUnavailable("ffmpeg is required on the server") from None
        except subprocess.TimeoutExpired:
            raise InvalidRecording("recording conversion timed out") from None
        if done.returncode or not target.is_file():
            raise InvalidRecording("cannot decode the recording")
        duration = _duration(target)
        if not 0 < duration <= MAX_SECONDS:
            raise InvalidRecording("recording must be between 0 and 90 seconds")
        return target.read_bytes()


def _duration(path: Path) -> float:
    with wave.open(str(path), "rb") as reader:
        return reader.getnframes() / reader.getframerate()


def _note_id(root: Path, store_id: str, sent_at: datetime) -> str:
    return f"live-{store_id.lower()}-{sent_at:%Y%m%d-%H%M%S}-{uuid4().hex}"


def save_note(
    store_id: str,
    store: Store,
    audio: bytes,
    suffix: str,
    transcript: str,
    *,
    language: str | None = None,
    now: datetime | None = None,
    data_dir: Path | None = None,
) -> LiveNote:
    text = transcript.strip()
    if not text:
        raise InvalidRecording("the transcript is empty")
    if len(text) > MAX_TRANSCRIPT_CHARS:
        raise InvalidRecording("the transcript is too long")
    if not audio:
        raise InvalidRecording("empty recording")
    # Validate metadata before conversion or publication, including user-supplied language.
    if language is not None:
        from tesseract.modules.sources.voice import LANGUAGE

        if not LANGUAGE.fullmatch(language):
            raise InvalidRecording("invalid language tag")
    wav = to_wav(audio, suffix)
    sent_at = (now or datetime.now(UTC)).astimezone(ZoneInfo(store.timezone)).replace(microsecond=0)
    root = inbox_path(data_dir)
    root.mkdir(parents=True, exist_ok=True)
    note_id = _note_id(root, store_id, sent_at)
    # Write into a hidden folder and rename: src.voice never sees a half-written note.
    staging = Path(tempfile.mkdtemp(prefix=".note-", dir=root))
    (staging / AUDIO_FILE).write_bytes(wav)
    (staging / TRANSCRIPT_FILE).write_text(text + "\n", encoding="utf-8")
    sidecar = {
        "note_id": note_id,
        "store_id": store_id,
        "sent_at": sent_at.isoformat(),
        "timezone": store.timezone,
        "language": language,
        "author_ref": f"pseudonym:{store_id.lower()}-staff-live",
        "fixture_kind": "live",
        "audio": AUDIO_FILE,
        "audio_sha256": "sha256:" + hashlib.sha256(wav).hexdigest(),
        "duration_s": _duration(staging / AUDIO_FILE),
        "manual_transcript": TRANSCRIPT_FILE,
    }
    (staging / NOTE_FILE).write_text(
        json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    staging.rename(root / note_id)
    return LiveNote(read_sidecar(root / note_id), text, None)


def list_notes(data_dir: Path | None = None) -> list[LiveNote]:
    """Live notes, oldest first; unreadable folders are skipped (src.voice reports them)."""
    root = inbox_path(data_dir)
    if not root.is_dir():
        return []
    notes = []
    for directory in sorted(root.iterdir()):
        if not directory.is_dir() or directory.name.startswith("."):
            continue
        try:
            note = read_sidecar(directory)
            if note.sidecar.fixture_kind != "live":
                continue
            # Validate all three paths before any file is copied or hashed.
            note_file(directory, note.sidecar.audio)
            text = note.transcript_path.read_text(encoding="utf-8")
        except (ValueError, OSError):
            continue
        notes.append(LiveNote(note, text.strip(), None))
    return sorted(notes, key=lambda n: (n.note.sidecar.sent_at, n.note.slug))


def batch_hash(notes: list[LiveNote]) -> str:
    """Bind the exact source bytes, including accepted text and availability/store metadata."""
    payload = []
    for live in sorted(notes, key=lambda n: n.note.slug):
        note = live.note
        payload.append(
            [
                note.slug,
                *[
                    hashlib.sha256(note_file(note.directory, name).read_bytes()).hexdigest()
                    for name in (NOTE_FILE, note.sidecar.audio, note.sidecar.manual_transcript)
                ],
            ]
        )
    return "sha256:" + hashlib.sha256(json.dumps(payload).encode()).hexdigest()


def snapshot_path(data_dir: Path, run_id: str) -> Path:
    if not run_id or Path(run_id).name != run_id or run_id in (".", ".."):
        raise ValueError("invalid live run id")
    return data_dir / "voice_runs" / run_id


def freeze_notes(data_dir: Path, run_id: str, notes: list[LiveNote], expected_hash: str) -> None:
    root = data_dir / "voice_runs"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".batch-", dir=root) as tmp:
        staging = Path(tmp) / "notes"
        staging.mkdir()
        for live in notes:
            note = live.note
            target = staging / note.slug
            target.mkdir()
            for name in (NOTE_FILE, note.sidecar.audio, note.sidecar.manual_transcript):
                shutil.copyfile(note_file(note.directory, name), target / name)
        frozen = [LiveNote(read_sidecar(p), "", None) for p in staging.iterdir()]
        if batch_hash(frozen) != expected_hash:
            raise ValueError("voice notes changed while queuing")
        staging.rename(snapshot_path(data_dir, run_id))
