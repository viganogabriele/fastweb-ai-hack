"""Systems recordings preserve provenance bytes and cannot fall through to HTTP."""

import base64
import json

import httpx
import pytest

from tessera.core.cache import CacheCorrupt, ReplayMiss
from tessera.core.config import Settings
from tessera.core.contracts import RunSpec
from tessera.core.systems_cache import SystemsCache, SystemsTransport, systems_factory
from tessera.modules.sources.systems_client import Crosswalk


@pytest.fixture
def spec():
    return RunSpec(
        run_id="first", scenario_id="historical", as_of="2026-10-22T20:00:00Z",
        stores=("MIL01",), source_manifest_hash="sources", config_hash="config",
        code_version="test", mode="live", modules=(), prompt_versions={},
        model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip


def settings(mode):
    return Settings(_env_file=None, llm_mode=mode)


def get(cache, spec, mode="replay", upstream=None, path="/warehouse/v1/atp?asOf=2026-10-22"):
    transport = SystemsTransport(settings(mode), spec, cache, upstream=upstream)
    with httpx.Client(base_url="http://127.0.0.1:8088", transport=transport) as client:
        return client.get(path)


def test_record_replay_preserves_bytes_and_does_not_construct_socket_transport(
    tmp_path, spec, monkeypatch
):
    cache = SystemsCache(tmp_path)
    raw = b'{ "positions": [], "note": "synthetic boundary response" }\n'
    calls = []

    def respond(request):
        calls.append(request.url)
        return httpx.Response(200, content=raw)

    first = get(cache, spec, "record", httpx.MockTransport(respond))
    assert first.content == raw and len(calls) == 1
    assert not cache.missing

    def forbidden(*args, **kwargs):
        raise AssertionError("replay constructed a network transport")

    monkeypatch.setattr(httpx, "HTTPTransport", forbidden)
    replay_spec = spec.model_copy(update={"run_id": "second", "mode": "recorded"})
    assert get(cache, replay_spec).content == raw
    assert get(cache, spec, "record").content == raw  # record also reuses immutable entries
    assert len(calls) == 1
    envelope = next(tmp_path.rglob("*.json")).read_text()
    assert "headers" not in envelope and "authorization" not in envelope


@pytest.mark.parametrize(
    "update",
    [
        {"as_of": "2026-10-21T20:00:00Z"},
        {"stores": ("MIL02",)},
        {"source_manifest_hash": "other"},
        {"config_hash": "other"},
        {"mode": "fixture"},
        {"code_version": "another-build"},
        {"scenario_id": "another-session"},
        {"erp_max_seq": 42},
        {"model_versions": {"ag.investigator": "different-model"}},
        {"prompt_versions": {"ag.investigator": "different-prompt"}},
    ],
)
def test_other_scope_is_an_explicit_miss(tmp_path, spec, update):
    cache = SystemsCache(tmp_path)
    get(cache, spec, "record", httpx.MockTransport(lambda _: httpx.Response(200, json={})))
    changed = RunSpec.model_validate({**spec.model_dump(), **update})
    with pytest.raises(ReplayMiss):
        get(cache, changed)
    assert len(cache.missing) == 1


def test_corruption_is_not_repaired_by_network(tmp_path, spec):
    cache = SystemsCache(tmp_path)
    get(cache, spec, "record", httpx.MockTransport(lambda _: httpx.Response(200, json={})))
    path = next(tmp_path.rglob("*.json"))
    envelope = json.loads(path.read_text())
    envelope["checksum"] = "invalid"
    path.write_text(json.dumps(envelope))
    with pytest.raises(CacheCorrupt):
        get(cache, spec)
    assert len(cache.corrupt) == 1


@pytest.mark.parametrize("path", ["/warehouse/v1/book", "https://elsewhere.test/warehouse/v1/atp"])
def test_unapproved_routes_and_origins_are_rejected(tmp_path, spec, path):
    with pytest.raises(ValueError, match="only simulated"):
        get(SystemsCache(tmp_path), spec, path=path)


def test_transient_errors_are_not_recorded(tmp_path, spec):
    cache = SystemsCache(tmp_path)
    result = get(cache, spec, "record", httpx.MockTransport(lambda _: httpx.Response(503)))
    assert result.status_code == 503
    assert not list(tmp_path.rglob("*.json"))


@pytest.mark.parametrize("raw", [b"not JSON", b"[]", b"\xff"])
def test_invalid_recorded_body_cannot_be_swallowed_as_an_unknown(tmp_path, spec, raw):
    cache = SystemsCache(tmp_path)
    get(cache, spec, "record", httpx.MockTransport(lambda _: httpx.Response(200, json={})))
    path = next(tmp_path.rglob("*.json"))
    key = path.stem
    path.unlink()
    cache.put(key, {"status": 200, "body": base64.b64encode(raw).decode()})
    with pytest.raises(CacheCorrupt):
        get(cache, spec)
    with pytest.raises(CacheCorrupt):
        cache.require_complete()


def test_factory_freezes_nested_snapshot_settings_and_forces_recorded_runs_offline(tmp_path, spec):
    cache = SystemsCache(tmp_path)
    original = spec.model_copy(deep=True)
    configured = settings("replay")
    factory = systems_factory(configured, spec, cache)
    get(cache, original, "record", httpx.MockTransport(lambda _: httpx.Response(200, json={})))
    configured.llm_mode = "live"
    configured.mocks_base_url = "https://elsewhere.test"
    spec.model_versions["chat"] = "changed"
    client = factory(Crosswalk({}, {}, {}, {}))
    try:
        assert client._http.get("/warehouse/v1/atp?asOf=2026-10-22").json() == {}
    finally:
        client.close()
    factory = systems_factory(
        settings("live"), original.model_copy(update={"mode": "recorded"}), cache
    )
    client = factory(Crosswalk({}, {}, {}, {}))
    try:
        with pytest.raises(ReplayMiss):
            client._http.get("/warehouse/v1/atp?asOf=2026-10-21")
    finally:
        client.close()


def test_get_bodies_are_rejected_before_network(tmp_path, spec):
    transport = SystemsTransport(settings("replay"), spec, SystemsCache(tmp_path))
    with httpx.Client(base_url="http://127.0.0.1:8088", transport=transport) as client:
        with pytest.raises(ValueError, match="request body"):
            client.request("GET", "/warehouse/v1/atp", content=b"different request")
