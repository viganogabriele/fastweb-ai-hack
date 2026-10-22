# asr-server (ASR-01)

OpenAI-compatible speech-to-text for the demo, running `whisper-large-v3-turbo` with
[mlx-whisper](https://pypi.org/project/mlx-whisper/) on Apple Silicon (our Mac mini M4). It stands
in for the Fastweb Whisper endpoint we have no key for (`docs/PLAN.md` §4 "ASR"). Any
OpenAI client works by changing only base URL and key.

Demo PoC, not production: one transcription at a time, in-memory rate limit, keys in a flat file.

## Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| `GET` | `/health` | none | `{"status": "ok", "model": ...}` |
| `GET` | `/v1/models` | key | the one served model |
| `POST` | `/v1/audio/transcriptions` | key | multipart: `file`, `model` (ignored), `language`, `prompt`, `response_format` = `json` / `text` / `verbose_json` (segments with `start`/`end`, used as audio evidence) |

Accepted audio: wav, mp3, ogg/opus, flac, m4a, webm, aac, caf (checked with `ffprobe`; playlists
such as HLS are refused). `language` takes a code (`it`) or a name (`italian`).

Errors: `401` bad or missing key (checked before the body is read), `411` no `Content-Length`,
`413` file or audio too long, `429` per-key rate limit or server busy, `400` undecodable audio,
unknown language or unsupported `response_format`.

## Setup on the Mac

```sh
brew install uv ffmpeg                     # ffmpeg + ffprobe decode the uploads
cd tools/asr-server
uv sync --frozen
uv run python server.py add-key backend    # prints the key ONCE: store it, it is not recoverable
uv run uvicorn server:app --host 127.0.0.1 --port 8100
```

The first start downloads the model (~1.6 GB) into the Hugging Face cache, then warms it up; the
log line `model ... ready` means it is serving.

**Keys.** One per consumer (`backend`, `lorenzo`, …). `keys.txt` holds only `name sha256`, mode
600, gitignored. Revoke by deleting the line: the file is re-read on every request, no restart.

**Settings** (env vars): `ASR_MODEL` (default `mlx-community/whisper-large-v3-turbo`),
`ASR_KEYS_FILE`, `ASR_MAX_UPLOAD_MB` (25), `ASR_MAX_AUDIO_S` (600), `ASR_RATE_PER_MIN` (20 per
key), `ASR_MAX_QUEUE` (4 requests in flight: 1 transcribing, the rest decoding or
waiting).

## Reverse proxy

TLS terminates at the proxy; the app listens on `127.0.0.1:8100` only. Raise the body limit to the
upload limit plus multipart overhead, and the read timeout above the longest transcription. nginx:

```nginx
location / {
    proxy_pass http://127.0.0.1:8100;
    client_max_body_size 26m;
    proxy_read_timeout 300s;
}
```

Caddy:

```caddy
asr.example.com {
    request_body {
        max_size 26MB
    }
    reverse_proxy 127.0.0.1:8100
}
```

## Check it

```sh
curl https://asr.example.com/health
curl https://asr.example.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $ASR_API_KEY" \
  -F file=@note.m4a -F language=it -F response_format=verbose_json
```

From Python, with the stock OpenAI SDK:

```python
from openai import OpenAI

client = OpenAI(base_url="https://asr.example.com/v1", api_key=ASR_API_KEY)
r = client.audio.transcriptions.create(
    model="whisper-large-v3-turbo", file=open("note.m4a", "rb"),
    language="it", response_format="verbose_json",
)
```
