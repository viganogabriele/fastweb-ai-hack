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

import hashlib
import json
import logging
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel

from tessera import __version__
from tessera.api.models import RunView
from tessera.api.routers.runs import engine_for, execute, registry_for, view
from tessera.core.config import MissingApiKey, Settings, get_settings
from tessera.core.contracts import ModuleSnapshot, RunSpec
from tessera.core.llm import LLMCallFailed, LLMClient
from tessera.core.registry import Registry
from tessera.core.repo import list_runs as stored_runs
from tessera.core.run_repo import repo_session
from tessera.modules.sources.emails import load_stores
from tessera.modules.sources.voice_inbox import (
    InvalidRecording,
    LiveNote,
    list_notes,
    mark_processed,
    save_note,
)

router = APIRouter(prefix="/api/voice")
logger = logging.getLogger("tessera.api.voice")

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
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"partial.{_suffix(audio)}"
        path.write_bytes(data)
        try:
            result = LLMClient(settings, concurrency=1).transcribe(path, language or None)
        except MissingApiKey:
            raise HTTPException(503, "ASR_API_KEY missing in .env") from None
        except (LLMCallFailed, ValueError) as error:
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
        live = save_note(
            store_id,
            store,
            data,
            _suffix(audio),
            transcript,
            language=language or None,
            data_dir=settings.data_dir,
        )
    except InvalidRecording as error:
        raise HTTPException(422, str(error)) from None
    return _note_view(live)


@router.get("/notes", response_model=tuple[LiveNoteView, ...])
def notes(request: Request, store: str | None = None):
    retry = {
        spec.run_id
        for spec, status in stored_runs(engine_for(request, "product"))
        if status in RETRY
    }
    return tuple(
        _note_view(n, retry)
        for n in list_notes(_settings(request).data_dir)
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
        source_manifest_hash=_hash(sorted(n.note.sidecar.audio_sha256 for n in notes)),
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
    engine = engine_for(request, "product")
    # A note whose run failed or was blocked (e.g. no key yet) is offered again.
    retry = {spec.run_id for spec, status in stored_runs(engine) if status in RETRY}
    pending = [
        n
        for n in list_notes(settings.data_dir)
        if (n.run_id is None or n.run_id in retry)
        and body.store_id in (None, n.note.sidecar.store_id)
    ]
    if not pending:
        raise HTTPException(409, "no new voice notes to process")
    registry = registry_for(request)
    # Recording keeps the demo reproducible: the same run replays later without keys.
    run_settings = settings.model_copy(
        update={"llm_mode": "live" if settings.llm_mode == "live" else "record"}
    )
    as_of = datetime.now(UTC).replace(microsecond=0)
    views = []
    for store_id in sorted({n.note.sidecar.store_id for n in pending}):
        batch = [n for n in pending if n.note.sidecar.store_id == store_id]
        spec = live_spec(
            registry, store_id, batch, max(as_of, *(n.note.sidecar.sent_at for n in batch))
        )
        with repo_session(engine, spec, fixture_mode=False, write=True) as repo:
            views.append(view(repo))
        mark_processed(batch, spec.run_id)
        tasks.add_task(execute, spec, engine, registry, run_settings)
    return tuple(views)
