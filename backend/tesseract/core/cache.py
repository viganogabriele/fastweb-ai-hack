"""Content-addressed LLM recordings, outside artifact/view projections.

Only sanitized inputs may be sent to the LLM. Recordings contain responses, never
credentials or request headers. Source/context versions belong in ``cache_context``.
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


class ReplayMiss(LookupError):
    """No recording exists; replay must never fall through to a provider."""


class CacheCorrupt(ValueError):
    """An existing recording failed its integrity/schema check."""


def cache_key(request: dict[str, Any]) -> str:
    canonical = json.dumps(
        request, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


class ResponseCache:
    def __init__(self, directory: Path):
        self.directory = Path(directory)

    def _path(self, key: str) -> Path:
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise ValueError("cache key must be a SHA-256 digest")
        return self.directory / key[:2] / f"{key}.json"

    def get(self, key: str) -> dict[str, Any]:
        path = self._path(key)
        try:
            envelope = json.loads(path.read_text())
            response = envelope["response"]
            if envelope["version"] != 1 or envelope["key"] != key:
                raise ValueError
            if not isinstance(response, dict) or envelope["checksum"] != cache_key(response):
                raise ValueError
            return response
        except FileNotFoundError:
            raise ReplayMiss(f"no LLM recording for {key}") from None
        except (ValueError, KeyError, TypeError):
            raise CacheCorrupt(f"invalid LLM recording for {key}") from None

    def put(self, key: str, response: dict[str, Any]) -> dict[str, Any]:
        """Publish once and return the winning recording, including across processes.

        A hard link exposes the fully-written temporary file atomically and fails
        if the destination exists. Never replace an earlier recording: frozen
        replay must keep the same response for a given request/context hash.
        """
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        envelope = {"version": 1, "key": key, "response": response, "checksum": cache_key(response)}
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
                temporary = stream.name
                json.dump(envelope, stream, ensure_ascii=False, sort_keys=True, allow_nan=False)
            try:
                os.link(temporary, path)
            except FileExistsError:
                pass
            return self.get(key)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
