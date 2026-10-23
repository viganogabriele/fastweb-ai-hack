"""DEMO-04: live voice notes from the store page ``/store/record``.

- ``POST /api/voice/transcribe``: the recording so far, transcribed live on the team ASR server
  (no cache: a partial recording is never a source). The page calls it every few seconds while
  the store speaks, then once more on stop.
- ``POST /api/voice/notes``: the final recording and the transcript the store accepted become a
  note in ``data/voice_inbox/`` (``voice_inbox.save_note``).
- ``GET /api/voice/notes``: live notes and the run that read each one.
- ``POST /api/voice/process``: one small product run over the notes not yet read, per store. It
  is a separate run (scenario ``live-voice``, ``as_of`` now), never a change to a published one:
  ``src.voice`` reads the notes, ``ing.extract`` their facts, ``int.link``/``int.cases`` link them
  to SKUs and open cases. ``src.email`` must succeed for ``ing.extract`` to run, so it is given a
  file outside the run's stores and reads no mail (it reports that skip, so the run is
  ``degraded`` by design). LLM calls are recorded, so the run replays later without keys.
"""

import fcntl
import hashlib
import json
import logging
import secrets
import tempfile
import time
from asyncio import to_thread
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Annotated
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from pydantic import BaseModel

from tessera import __version__
from tessera.api.models import RunView
from tessera.api.routers.runs import engine_for, execute, registry_for, view
from tessera.core.config import MissingApiKey, Settings, get_settings
from tessera.core.contracts import ModuleSnapshot, RunSpec
from tessera.core.llm import BudgetExceeded, LLMCallFailed, LLMClient
from tessera.core.registry import Registry
from tessera.core.repo import list_runs as stored_runs
from tessera.core.run_repo import repo_session
from tessera.modules.sources.emails import load_stores
from tessera.modules.sources.voice import LANGUAGE, read_sidecar
from tessera.modules.sources.voice_inbox import (
    InvalidRecording,
    LiveNote,
    RecordingUnavailable,
    batch_hash,
    freeze_notes,
    list_notes,
    save_note,
    snapshot_path,
    to_wav,
)


def authorize(request: Request) -> None:
    token = _settings(request).voice_access_token
    if token is None or not token.get_secret_value():
        raise HTTPException(503, "live voice is disabled; configure VOICE_ACCESS_TOKEN")
    supplied = request.headers.get("authorization", "").removeprefix("Bearer ")
    if not secrets.compare_digest(supplied.encode(), token.get_secret_value().encode()):
        raise HTTPException(401, "live voice access required")


router = APIRouter(prefix="/api/voice", dependencies=[Depends(authorize)])
logger = logging.getLogger("tessera.api.voice")
_ASR_SLOT = Lock()
_ASR_STARTS = deque()

SCENARIO = "live-voice"
# Roots in reading order: the voice documents exist before ing.extract lists documents.
ROOTS = ("src.voice", "ing.extract", "int.cases")
NO_MAIL = "NONE/no-mail.eml"
RETRY = {"failed", "blocked"}
SUFFIXES = {"webm", "mp4", "m4a", "ogg", "wav", "mp3", "aac"}
MAX_UPLOAD = 20 * 2**20


class Transcription(BaseModel):
    text: str
    duration_s: float | None = None


class LiveNoteView(BaseModel):
    note_id: str
    store_id: str
    sent_at: datetime
    duration_s: float | None
    transcript: str
    run_id: str | None


class ProcessRequest(BaseModel):
    store_id: str | None = None


def _settings(request: Request) -> Settings:
    return request.app.state.settings or get_settings()


def _note_view(live: LiveNote, retry: set[str] = frozenset()) -> LiveNoteView:
    """``run_id`` is null while the note still needs a run, also after a failed one."""
    sidecar = live.note.sidecar
    return LiveNoteView(
        note_id=live.note.slug,
        store_id=sidecar.store_id,
        sent_at=sidecar.sent_at,
        duration_s=sidecar.duration_s,
        transcript=live.transcript,
        run_id=None if live.run_id in retry else live.run_id,
    )


def _suffix(upload: UploadFile) -> str:
    """Browsers send ``audio/webm;codecs=opus`` or ``audio/mp4``; ffmpeg probes the bytes anyway."""
    kind = (upload.content_type or "").split(";")[0].split("/")[-1].lower()
    name = Path(upload.filename or "").suffix.lstrip(".").lower()
    for candidate in (name, kind):
        if candidate in SUFFIXES:
            return candidate
    return "webm"


async def _read(upload: UploadFile) -> bytes:
    data = await upload.read(MAX_UPLOAD + 1)
    if not data:
        raise HTTPException(400, "empty recording")
    if len(data) > MAX_UPLOAD:
        raise HTTPException(413, "recording too large")
    return data


def _store(settings: Settings, store_id: str):
    store = load_stores(settings.sources_dir).get(store_id)
    if store is None:
        raise HTTPException(422, f"unknown store {store_id!r}")
    return store


@router.post("/transcribe", response_model=Transcription)
async def transcribe(
    request: Request,
    audio: Annotated[UploadFile, File()],
    language: Annotated[str | None, Form()] = None,
):
    data = await _read(audio)
    settings = _settings(request).model_copy(update={"llm_mode": "live"})
    if language and not LANGUAGE.fullmatch(language):
        raise HTTPException(422, "invalid language tag")

    def work():
        # The worker owns the slot until the provider returns, even if HTTP is cancelled.
        if not _ASR_SLOT.acquire(blocking=False):
            raise HTTPException(429, "another transcription is in progress")
        try:
            now = time.monotonic()
            while _ASR_STARTS and _ASR_STARTS[0] <= now - 60:
                _ASR_STARTS.popleft()
            if len(_ASR_STARTS) >= 20:
                raise HTTPException(429, "transcription limit reached; try again later")
            _ASR_STARTS.append(now)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "partial.wav"
                # Apply the same container, duration and resource limits before ASR upload.
                settings.asr_key()
                path.write_bytes(to_wav(data, _suffix(audio)))
                return LLMClient(
                    settings, concurrency=1, max_retries=0, deadline_seconds=30
                ).transcribe(path, language or None)
        finally:
            _ASR_SLOT.release()

    try:
        result = await to_thread(work)
    except MissingApiKey:
        raise HTTPException(503, "ASR access is not configured") from None
    except RecordingUnavailable as error:
        raise HTTPException(503, str(error)) from None
    except InvalidRecording as error:
        raise HTTPException(422, str(error)) from None
    except (BudgetExceeded, LLMCallFailed, ValueError) as error:
        raise HTTPException(502, f"ASR unavailable: {type(error).__name__}") from None
    return Transcription(text=result.text.strip(), duration_s=result.duration)


@router.post("/notes", response_model=LiveNoteView, status_code=201)
async def create_note(
    request: Request,
    audio: Annotated[UploadFile, File()],
    store_id: Annotated[str, Form()],
    transcript: Annotated[str, Form()],
    language: Annotated[str | None, Form()] = None,
):
    settings = _settings(request)
    store = _store(settings, store_id)
    data = await _read(audio)
    try:
        live = await to_thread(
            save_note,
            store_id,
            store,
            data,
            _suffix(audio),
            transcript,
            language=language or None,
            data_dir=settings.data_dir,
        )
    except InvalidRecording as error:
        # Keep the refused upload (gitignored data/) so a phone-specific format can be inspected.
        rejects = settings.data_dir / "voice_rejects"
        rejects.mkdir(parents=True, exist_ok=True)
        kept = rejects / f"{datetime.now(UTC):%Y%m%d-%H%M%S}-{store_id}.{_suffix(audio)}"
        kept.write_bytes(data)
        logger.warning(
            "voice note refused: %s (content_type=%r, filename=%r, bytes=%d, kept=%s)",
            error,
            audio.content_type,
            audio.filename,
            len(data),
            kept.name,
        )
        raise HTTPException(422, str(error)) from None
    except RecordingUnavailable as error:
        raise HTTPException(503, str(error)) from None
    return _note_view(live)


@router.get("/notes", response_model=tuple[LiveNoteView, ...])
def notes(request: Request, store: str | None = None):
    return tuple(
        _note_view(n)
        for n in _live_notes(_settings(request), engine_for(request, "product"))
        if store is None or n.note.sidecar.store_id == store
    )


def _hash(value) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def live_spec(registry: Registry, store_id: str, notes: list[LiveNote], as_of: datetime) -> RunSpec:
    """A product run over ``notes`` only: the closure of ``ROOTS``, nothing else enabled."""
    manifests = {m.id: m for m in registry.manifests()}
    ordered: list[str] = []

    def add(module_id: str) -> None:
        if module_id in ordered:
            return
        for dependency in manifests[module_id].requires:
            add(dependency)
        ordered.append(module_id)

    for root in ROOTS:
        add(root)
    params = {
        # The text the store checked (and maybe corrected) on the phone is the source, not a
        # second ASR pass over the audio: one segment, no audio timestamps.
        "src.voice": {"notes": [n.note.slug for n in notes], "mode": "fixture"},
        "src.email": {"files": [NO_MAIL]},
    }
    modules = tuple(
        ModuleSnapshot(manifest=manifests[module_id], params=params.get(module_id, {}))
        for module_id in ordered
    )
    return RunSpec(
        run_id=str(uuid4()),
        scenario_id=SCENARIO,
        as_of=as_of,
        stores=(store_id,),
        source_manifest_hash=batch_hash(notes),
        config_hash=_hash([m.model_dump(mode="json") for m in modules]),
        code_version=__version__,
        mode="live",
        modules=modules,
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=(),
    )


@router.post("/process", response_model=tuple[RunView, ...], status_code=202)
def process(request: Request, body: ProcessRequest, tasks: BackgroundTasks):
    settings = _settings(request)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    # File lock serializes claim decisions across HTTP threads and server processes.
    with (settings.data_dir / "voice-process.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _process(request, body, tasks)


def _live_notes(settings: Settings, engine) -> list[LiveNote]:
    # The immutable spec IS the claim: its commit is atomic with run creation.
    notes = {n.note.slug: n for n in list_notes(settings.data_dir)}
    seen = set()
    for spec, status in stored_runs(engine):
        if spec.scenario_id != SCENARIO:
            continue
        for snapshot in spec.modules:
            if snapshot.manifest.id != "src.voice":
                continue
            frozen = []
            for slug in snapshot.params.get("notes", []):
                path = snapshot_path(settings.data_dir, spec.run_id) / slug
                note = read_sidecar(path)
                text = note.transcript_path.read_text(encoding="utf-8").strip()
                frozen.append(LiveNote(note, text, None if status in RETRY else spec.run_id))
            if batch_hash(frozen) != spec.source_manifest_hash:
                raise HTTPException(409, "queued voice snapshot has changed")
            for note in frozen:
                if note.note.slug not in seen:
                    notes[note.note.slug] = note
                    seen.add(note.note.slug)
    return sorted(notes.values(), key=lambda n: (n.note.sidecar.sent_at, n.note.slug))


def _process(request: Request, body: ProcessRequest, tasks: BackgroundTasks):
    settings = _settings(request)
    engine = engine_for(request, "product")
    if any(
        spec.scenario_id == SCENARIO and status in {"pending", "running"}
        for spec, status in stored_runs(engine)
    ):
        raise HTTPException(409, "voice processing is already in progress")
    # A note whose run failed or was blocked (e.g. no key yet) is offered again.
    as_of = datetime.now(UTC)
    pending = [
        n
        for n in _live_notes(settings, engine)
        if n.run_id is None
        and n.note.sidecar.sent_at <= as_of
        and body.store_id in (None, n.note.sidecar.store_id)
    ]
    if not pending:
        raise HTTPException(409, "no new voice notes to process")
    registry = registry_for(request)
    # Recording keeps the demo reproducible: the same run replays later without keys.
    run_settings = settings.model_copy(
        update={"llm_mode": "live" if settings.llm_mode == "live" else "record"}
    )
    views = []
    for store_id in sorted({n.note.sidecar.store_id for n in pending}):
        batch = [n for n in pending if n.note.sidecar.store_id == store_id]
        spec = live_spec(registry, store_id, batch, as_of)
        freeze_notes(settings.data_dir, spec.run_id, batch, spec.source_manifest_hash)
        with repo_session(engine, spec, fixture_mode=False, write=True) as repo:
            views.append(view(repo))
        tasks.add_task(execute, spec, engine, registry, run_settings)
    return tuple(views)
