"""DEMO-04: live store voice notes recorded from ``/store/record``, saved for ``src.voice``.

A recording from the phone becomes ``data/voice_inbox/<note_id>/`` with the same three files as
a DATA-03 fixture: ``note.json`` (``fixture_kind: "live"``), ``note.wav`` (16 kHz mono PCM,
converted with ffmpeg because ``src.voice`` reads wav/mp3 only) and ``transcript.txt``, the live
ASR transcript the store accepted. ``sent_at`` is the moment the note is saved, in the store's
zone: the note is available from then, and only runs with a later ``as_of`` read it.

``processed.json`` in a note folder records the run that read it, so the demo button and a
periodic job process each note once. ``src.voice`` ignores that file.
"""

import hashlib
import json
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tessera.modules.sources.emails import Store
from tessera.modules.sources.voice import NOTE_FILE, Note, inbox_path, read_sidecar

AUDIO_FILE = "note.wav"
TRANSCRIPT_FILE = "transcript.txt"
PROCESSED_FILE = "processed.json"
MAX_TRANSCRIPT_CHARS = 5000


class InvalidRecording(ValueError):
    """The upload cannot become a note: no audio ffmpeg can decode, or an empty transcript."""


@dataclass(frozen=True)
class LiveNote:
    note: Note
    transcript: str
    run_id: str | None


def to_wav(audio: bytes, suffix: str) -> bytes:
    """Any browser recording (webm/opus, mp4/aac, ogg, wav) as 16 kHz mono PCM, no metadata."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / f"in{suffix if suffix.startswith('.') else '.' + suffix}"
        target = Path(tmp) / AUDIO_FILE
        source.write_bytes(audio)
        # fmt: off
        cmd = [
            "ffmpeg", "-nostdin", "-v", "error", "-i", str(source),
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", "-map_metadata", "-1", str(target),
        ]
        # fmt: on
        try:
            done = subprocess.run(cmd, capture_output=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise InvalidRecording(f"ffmpeg unavailable: {type(error).__name__}") from None
        if done.returncode or not target.is_file():
            raise InvalidRecording("cannot decode the recording")
        return target.read_bytes()


def _duration(path: Path) -> float:
    with wave.open(str(path), "rb") as reader:
        return round(reader.getnframes() / reader.getframerate(), 1)


def _note_id(root: Path, store_id: str, sent_at: datetime) -> str:
    base = f"live-{store_id.lower()}-{sent_at:%Y%m%d-%H%M%S}"
    note_id, n = base, 1
    while (root / note_id).exists():
        n += 1
        note_id = f"{base}-{n}"
    return note_id


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
    wav = to_wav(audio, suffix)
    sent_at = (now or datetime.now(UTC)).astimezone(ZoneInfo(store.timezone)).replace(microsecond=0)
    root = inbox_path(data_dir)
    root.mkdir(parents=True, exist_ok=True)
    note_id = _note_id(root, store_id, sent_at)
    # Write into a hidden folder and rename: src.voice never sees a half-written note.
    staging = root / f".{note_id}"
    staging.mkdir()
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
            text = (directory / note.sidecar.manual_transcript).read_text(encoding="utf-8")
        except (ValueError, OSError):
            continue
        processed = directory / PROCESSED_FILE
        run_id = (
            json.loads(processed.read_text(encoding="utf-8")).get("run_id")
            if processed.is_file()
            else None
        )
        notes.append(LiveNote(note, text.strip(), run_id))
    return sorted(notes, key=lambda n: (n.note.sidecar.sent_at, n.note.slug))


def mark_processed(notes: list[LiveNote], run_id: str) -> None:
    for live in notes:
        (live.note.directory / PROCESSED_FILE).write_text(
            json.dumps({"run_id": run_id}) + "\n", encoding="utf-8"
        )
