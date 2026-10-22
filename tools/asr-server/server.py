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
import subprocess
import tempfile
import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import mlx_whisper
import numpy as np
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, PlainTextResponse
from mlx_whisper.audio import SAMPLE_RATE
from mlx_whisper.tokenizer import LANGUAGES, TO_LANGUAGE_CODE

KEYS_FILE = Path(os.environ.get("ASR_KEYS_FILE", Path(__file__).parent / "keys.txt"))
MODEL = os.environ.get("ASR_MODEL", "mlx-community/whisper-large-v3-turbo")
MAX_UPLOAD_BYTES = int(os.environ.get("ASR_MAX_UPLOAD_MB", "25")) * 1024 * 1024
MAX_AUDIO_S = int(os.environ.get("ASR_MAX_AUDIO_S", "600"))
RATE_PER_MIN = int(os.environ.get("ASR_RATE_PER_MIN", "20"))
MAX_QUEUE = int(os.environ.get("ASR_MAX_QUEUE", "4"))
FORMATS = {"json", "text", "verbose_json"}
# ffprobe demuxer names. Playlist-like formats (hls, concat) are refused: they make ffmpeg open
# other files on the Mac.
AUDIO_DEMUXERS = {"wav", "mp3", "ogg", "flac", "mov", "matroska", "aac", "caf"}
# Multipart framing around the file: headers and the small form fields.
BODY_OVERHEAD = 64 * 1024

log = logging.getLogger("asr")

# MLX runs one transcription at a time; extra requests wait, beyond MAX_QUEUE they get a 429.
_infer_lock = threading.Lock()
_queue_lock = threading.Lock()
_queued = 0
_rate_lock = threading.Lock()
_calls: dict[str, deque[float]] = defaultdict(deque)


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def load_keys() -> dict[str, str]:
    """`{sha256: name}` from lines `<name> <sha256>`; malformed lines are skipped and logged."""
    if not KEYS_FILE.is_file():
        return {}
    keys = {}
    for n, line in enumerate(KEYS_FILE.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[1]):
            log.warning("%s:%d malformed, skipped", KEYS_FILE, n)
            continue
        keys[parts[1]] = parts[0]
    return keys


def key_name(request: Request) -> str | None:
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    return load_keys().get(_hash(token)) if scheme.lower() == "bearer" and token else None


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse({"detail": message}, status_code=status)


async def guard_api(request: Request, call_next):
    """Check key and declared size before FastAPI reads the body: no unauthenticated uploads."""
    if request.url.path.startswith("/v1/"):
        if key_name(request) is None:
            return _error(401, "invalid or missing API key")
        if request.method == "POST":
            length = request.headers.get("content-length")
            if length is None or not length.isdigit():
                return _error(411, "Content-Length required")
            if int(length) > MAX_UPLOAD_BYTES + BODY_OVERHEAD:
                return _error(413, f"file larger than {MAX_UPLOAD_BYTES // 2**20} MB")
    return await call_next(request)


def rate_limited_key(request: Request) -> str:
    name = key_name(request)
    if name is None:  # revoked between the middleware and here
        raise HTTPException(401, "invalid or missing API key")
    now = time.monotonic()
    with _rate_lock:
        calls = _calls[name]
        while calls and now - calls[0] > 60:
            calls.popleft()
        if len(calls) >= RATE_PER_MIN:
            raise HTTPException(429, f"rate limit: {RATE_PER_MIN} requests/minute per key")
        calls.append(now)
    return name


ApiKey = Annotated[str, Depends(rate_limited_key)]


def language_code(language: str | None) -> str | None:
    if language is None:
        return None
    lang = language.lower()
    code = lang if lang in LANGUAGES else TO_LANGUAGE_CODE.get(lang)
    if code is None:
        raise HTTPException(400, f"unsupported language {language!r}")
    return code


def decode(path: str) -> np.ndarray:
    """Mono 16 kHz float32, decoding at most MAX_AUDIO_S + 1 s so a tiny file can't fill RAM."""
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=format_name",
            "-of",
            "default=nw=1:nk=1",
            path,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    demuxer = probe.stdout.strip().split(",")[0]
    if probe.returncode or demuxer not in AUDIO_DEMUXERS:
        log.warning("refused upload: ffprobe=%r %s", demuxer, probe.stderr.strip()[-200:])
        raise HTTPException(400, "cannot decode audio (wav, mp3, ogg/opus, flac, m4a, webm)")
    # fmt: off
    cmd = [
        "ffmpeg", "-nostdin", "-v", "error", "-f", demuxer, "-i", path,
        "-t", str(MAX_AUDIO_S + 1), "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "s16le", "-",
    ]
    # fmt: on
    out = subprocess.run(cmd, capture_output=True, timeout=120)
    if out.returncode:
        log.warning("ffmpeg failed: %s", out.stderr.decode(errors="replace")[-200:])
        raise HTTPException(400, "cannot decode audio")
    return np.frombuffer(out.stdout, np.int16).astype(np.float32) / 32768.0


def transcribe(path: str, language: str | None, prompt: str | None) -> dict:
    global _queued
    with _queue_lock:
        if _queued >= MAX_QUEUE:
            raise HTTPException(429, "server busy, retry shortly")
        _queued += 1
    try:
        audio = decode(path)
        duration = len(audio) / SAMPLE_RATE
        if duration > MAX_AUDIO_S:
            raise HTTPException(413, f"audio longer than {MAX_AUDIO_S}s")
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
app.middleware("http")(guard_api)


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
    code = language_code(language)
    with tempfile.NamedTemporaryFile(suffix=".upload") as tmp:
        size = 0
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                raise HTTPException(413, f"file larger than {MAX_UPLOAD_BYTES // 2**20} MB")
            tmp.write(chunk)
        tmp.flush()
        t0 = time.perf_counter()
        r = await run_in_threadpool(transcribe, tmp.name, code, prompt)
    log.warning("key=%s audio=%.1fs took=%.1fs", key_name, r["duration"], time.perf_counter() - t0)

    text = r["text"].strip()
    if response_format == "text":
        return PlainTextResponse(text)
    if response_format == "json":
        return {"text": text}
    seg_keys = ("id", "seek", "start", "end", "text", "tokens", "temperature", "avg_logprob",
                "compression_ratio", "no_speech_prob")  # fmt: skip
    return {
        "task": "transcribe",
        "language": LANGUAGES.get(r["language"], r["language"]),
        "duration": r["duration"],
        "text": text,
        "segments": [{k: s[k] for k in seg_keys} for s in r["segments"]],
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
