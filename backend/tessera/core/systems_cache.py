"""Immutable GET recordings for the simulated stock/logistics boundary.

Keep response bytes intact: systems SourceRefs hash those bytes. No request headers,
credentials, writes or external dispatch are recorded. Replay never builds a socket
transport. The caller owns the cache so misses remain visible even if a tool catches one.
"""

import base64
import binascii

import httpx

from tessera.core.cache import CacheCorrupt, ReplayMiss, ResponseCache, cache_key
from tessera.core.config import Settings
from tessera.core.contracts import RunSpec

READ_PATHS = frozenset({"/warehouse/v1/stock", "/warehouse/v1/atp", "/logistics/v1/lanes"})


class SystemsCache(ResponseCache):
    def __init__(self, directory):
        super().__init__(directory)
        self.missing: set[str] = set()
        self.corrupt: set[str] = set()

    def get(self, key):
        try:
            return super().get(key)
        except ReplayMiss:
            self.missing.add(key)
            raise
        except CacheCorrupt:
            self.corrupt.add(key)
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
        self.scope = {
            "source_manifest_hash": spec.source_manifest_hash,
            "config_hash": spec.config_hash,
            "as_of": spec.as_of.isoformat(),
            "stores": sorted(spec.stores),
            "namespace": "fixture" if spec.mode == "fixture" else "product",
        }
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
        key = cache_key({"format": 1, "scope": self.scope, "url": str(url)})
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
        except (KeyError, TypeError, ValueError, binascii.Error):
            self.cache.corrupt.add(key)
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


def systems_factory(settings: Settings, spec: RunSpec, cache=None):
    """Wire the existing ACT-04 parser to recorded HTTP bytes, without changing its math."""
    from tessera.modules.sources.systems_client import SystemsClient

    cache = cache if cache is not None else SystemsCache(settings.data_dir / "systems_cache")

    def factory(crosswalk):
        return SystemsClient(
            crosswalk,
            base_url=settings.mocks_base_url,
            transport=SystemsTransport(settings, spec, cache),
        )

    factory.recordings = cache
    return factory
