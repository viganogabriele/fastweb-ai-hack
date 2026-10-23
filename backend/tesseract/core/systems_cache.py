"""Immutable GET recordings for the simulated stock/logistics boundary.

Keep response bytes intact: systems SourceRefs hash those bytes. No request headers,
credentials, writes or external dispatch are recorded. Replay never builds a socket
transport. The caller owns the cache so misses remain visible even if a tool catches one.
"""

import base64
import binascii
import json

import httpx

from tesseract.core.cache import CacheCorrupt, ReplayMiss, ResponseCache, cache_key
from tesseract.core.config import Settings
from tesseract.core.contracts import RunSpec

READ_PATHS = frozenset({"/warehouse/v1/stock", "/warehouse/v1/atp", "/logistics/v1/lanes"})


class SystemsCache(ResponseCache):
    def __init__(self, directory):
        super().__init__(directory)
        self.missing: set[str] = set()
        self.corrupt: set[str] = set()
        self.failures = 0

    def get(self, key):
        try:
            return super().get(key)
        except ReplayMiss:
            self.missing.add(key)
            self.failures += 1
            raise
        except CacheCorrupt:
            self.corrupt.add(key)
            self.failures += 1
            raise

    def require_complete(self):
        if self.missing:
            raise ReplayMiss("missing systems recording")
        if self.corrupt:
            raise CacheCorrupt("corrupt systems recording")


class SystemsTransport(httpx.BaseTransport):
    def __init__(self, settings, spec, cache, *, upstream=None):
        self.mode = settings.llm_mode
        self.origin = httpx.URL(settings.mocks_base_url)
        self.cache = cache
        scope = spec.model_dump(mode="json", exclude={"run_id", "mode"})
        scope["namespace"] = "fixture" if spec.mode == "fixture" else "product"
        scope["stores"] = sorted(scope["stores"])
        for module in scope["modules"]:
            module["manifest"].pop("mode", None)
        self.scope = scope
        self.upstream = upstream

    def handle_request(self, request):
        url = request.url
        if (
            request.method != "GET"
            or url.path not in READ_PATHS
            or (url.scheme, url.host, url.port)
            != (self.origin.scheme, self.origin.host, self.origin.port)
            or url.userinfo
        ):
            raise ValueError("only simulated stock/logistics GET reads may be recorded")
        if request.content:
            raise ValueError("simulated GET reads cannot have a request body")
        key = cache_key({"format": 2, "scope": self.scope, "url": str(url)})
        if self.mode == "live":
            return self._upstream().handle_request(request)
        try:
            saved = self.cache.get(key)
        except ReplayMiss:
            if self.mode == "replay":
                raise
            self.cache.missing.discard(key)
            response = self._upstream().handle_request(request)
            response.read()
            try:
                # Transient errors and invalid responses are not frozen as evidence.
                if response.status_code != 200:
                    return response
                try:
                    valid = isinstance(response.json(), dict)
                except ValueError:
                    valid = False
                if not valid:
                    return response
                saved = self.cache.put(
                    key,
                    {"status": 200, "body": base64.b64encode(response.content).decode("ascii")},
                )
            finally:
                response.close()
        try:
            if saved["status"] != 200:
                raise ValueError
            body = base64.b64decode(saved["body"], validate=True)
            if not isinstance(json.loads(body), dict):
                raise ValueError
        except (KeyError, TypeError, ValueError, binascii.Error):
            self.cache.corrupt.add(key)
            self.cache.failures += 1
            raise CacheCorrupt(f"invalid systems recording for {key}") from None
        return httpx.Response(200, content=body, headers={"content-type": "application/json"})

    def _upstream(self):
        if self.mode == "replay":
            raise RuntimeError("replay cannot construct a network transport")
        if self.upstream is None:
            self.upstream = httpx.HTTPTransport()
        return self.upstream

    def close(self):
        if self.upstream is not None:
            self.upstream.close()


def systems_factory(settings: Settings, spec: RunSpec, cache=None, *, allow_recording=False):
    """Wire the existing ACT-04 parser to recorded HTTP bytes, without changing its math."""
    from tesseract.modules.sources.systems_client import SystemsClient

    # Freeze before a queued job or module can mutate the caller's nested settings/spec.
    settings = settings.model_copy(deep=True)
    spec = spec.model_copy(deep=True)
    if spec.mode != "live" and not (allow_recording and settings.llm_mode == "record"):
        settings.llm_mode = "replay"
    cache = cache if cache is not None else SystemsCache(settings.data_dir / "systems_cache")

    def factory(crosswalk):
        return SystemsClient(
            crosswalk,
            base_url=settings.mocks_base_url,
            transport=SystemsTransport(settings, spec, cache),
        )

    factory.recordings = cache
    return factory
