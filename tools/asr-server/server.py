"""ASR-01: OpenAI-compatible transcription server on Apple Silicon (mlx-whisper).

Exposes `POST /v1/audio/transcriptions` so the backend can point `ASR_BASE_URL` here instead of
Fastweb with no client change. Auth: bearer API keys, stored as SHA-256 hashes in `keys.txt`.

    uv run python server.py add-key <name>     # prints the new key once
    uv run uvicorn server:app --host 127.0.0.1 --port 8100

Revoke a key by deleting its line from `keys.txt`: the file is re-read on every request.
The `model` form field is accepted for compatibility and ignored: the server runs `ASR_MODEL`.
"""

import argparse
import hashlib
import logging
import os
import re
import secrets
import tempfile
import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import mlx_whisper
import numpy as np
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mlx_whisper.audio import SAMPLE_RATE, load_audio

KEYS_FILE = Path(os.environ.get("ASR_KEYS_FILE", Path(__file__).parent / "keys.txt"))
MODEL = os.environ.get("ASR_MODEL", "mlx-community/whisper-large-v3-turbo")
MAX_UPLOAD_BYTES = int(os.environ.get("ASR_MAX_UPLOAD_MB", "25")) * 1024 * 1024
MAX_AUDIO_S = int(os.environ.get("ASR_MAX_AUDIO_S", "600"))
RATE_PER_MIN = int(os.environ.get("ASR_RATE_PER_MIN", "20"))
MAX_QUEUE = int(os.environ.get("ASR_MAX_QUEUE", "4"))
FORMATS = {"json", "text", "verbose_json"}

log = logging.getLogger("asr")

# MLX runs one transcription at a time; extra requests wait, beyond MAX_QUEUE they get a 429.
_infer_lock = threading.Lock()
_queue_lock = threading.Lock()
_queued = 0
_calls: dict[str, deque[float]] = defaultdict(deque)


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def load_keys() -> dict[str, str]:
    """`{sha256: name}` from lines `<name> <sha256>`; blank lines and `#` comments ignored."""
    if not KEYS_FILE.is_file():
        return {}
    keys = {}
    for line in KEYS_FILE.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, digest = line.split()
            keys[digest] = name
    return keys


_bearer = HTTPBearer(auto_error=False)


def require_key(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    name = load_keys().get(_hash(creds.credentials)) if creds else None
    if name is None:
        raise HTTPException(401, "invalid or missing API key")
    now = time.monotonic()
    calls = _calls[name]
    while calls and now - calls[0] > 60:
        calls.popleft()
    if len(calls) >= RATE_PER_MIN:
        raise HTTPException(429, f"rate limit: {RATE_PER_MIN} requests/minute per key")
    calls.append(now)
    return name


ApiKey = Annotated[str, Depends(require_key)]


def transcribe(path: str, language: str | None, prompt: str | None) -> dict:
    global _queued
    with _queue_lock:
        if _queued >= MAX_QUEUE:
            raise HTTPException(429, "server busy, retry shortly")
        _queued += 1
    try:
        try:
            audio = load_audio(path)
        except Exception as e:  # ffmpeg failed: not an audio file we can decode
            raise HTTPException(400, f"cannot decode audio: {e}") from None
        duration = audio.shape[0] / SAMPLE_RATE
        if duration > MAX_AUDIO_S:
            raise HTTPException(413, f"audio is {duration:.0f}s, limit {MAX_AUDIO_S}s")
        with _infer_lock:
            result = mlx_whisper.transcribe(
                audio, path_or_hf_repo=MODEL, language=language, initial_prompt=prompt
            )
        result["duration"] = duration
        return result
    finally:
        with _queue_lock:
            _queued -= 1


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Load the model and compile kernels now, so the first real call is not the slow one.
    mlx_whisper.transcribe(np.zeros(SAMPLE_RATE, dtype=np.float32), path_or_hf_repo=MODEL)
    log.warning("model %s ready, %d keys in %s", MODEL, len(load_keys()), KEYS_FILE)
    yield


app = FastAPI(title="asr-server", lifespan=lifespan, docs_url=None, redoc_url=None)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": MODEL}


@app.get("/v1/models")
def models(_: ApiKey) -> dict:
    return {"object": "list", "data": [{"id": MODEL, "object": "model", "owned_by": "local"}]}


@app.post("/v1/audio/transcriptions")
async def transcriptions(
    file: Annotated[UploadFile, File()],
    key_name: ApiKey,
    model: Annotated[str, Form()] = MODEL,
    language: Annotated[str | None, Form()] = None,
    prompt: Annotated[str | None, Form()] = None,
    response_format: Annotated[str, Form()] = "json",
):
    if response_format not in FORMATS:
        raise HTTPException(400, f"response_format must be one of {sorted(FORMATS)}")
    suffix = Path(file.filename or "").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        size = 0
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                raise HTTPException(413, f"file larger than {MAX_UPLOAD_BYTES // 2**20} MB")
            tmp.write(chunk)
        tmp.flush()
        t0 = time.perf_counter()
        r = await run_in_threadpool(transcribe, tmp.name, language, prompt)
    log.warning("key=%s audio=%.1fs took=%.1fs", key_name, r["duration"], time.perf_counter() - t0)

    text = r["text"].strip()
    if response_format == "text":
        return PlainTextResponse(text)
    if response_format == "json":
        return {"text": text}
    return {
        "task": "transcribe",
        "language": r["language"],
        "duration": r["duration"],
        "text": text,
        "segments": [
            {
                k: s[k]
                for k in (
                    "id",
                    "seek",
                    "start",
                    "end",
                    "text",
                    "tokens",
                    "temperature",
                    "avg_logprob",
                    "compression_ratio",
                    "no_speech_prob",
                )
            }
            for s in r["segments"]
        ],
    }


def add_key(name: str) -> None:
    if not re.fullmatch(r"[a-z0-9_-]+", name):
        raise SystemExit("name: lowercase letters, digits, - and _ only")
    if name in load_keys().values():
        raise SystemExit(f"key {name!r} exists: delete its line in {KEYS_FILE} first")
    key = "asr-" + secrets.token_urlsafe(32)
    with KEYS_FILE.open("a") as f:
        f.write(f"{name} {_hash(key)}\n")
    KEYS_FILE.chmod(0o600)
    print(key)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("add-key", help="create a key, print it once").add_argument("name")
    args = ap.parse_args()
    add_key(args.name)
