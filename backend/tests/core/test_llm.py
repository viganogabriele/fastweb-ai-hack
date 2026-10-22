"""Offline provider-contract tests: no credentials or external network required."""

import json
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import httpx
import pytest
from openai import OpenAI
from pydantic import BaseModel, SecretStr

from tessera.core.cache import CacheCorrupt, ReplayMiss, ResponseCache, cache_key
from tessera.core.config import Settings
from tessera.core.llm import (
    BudgetExceeded,
    CallBudget,
    ExtractionFailed,
    LLMCallFailed,
    LLMClient,
    inline_schema,
)

MESSAGES = [{"role": "user", "content": "Sanitized source"}]


class TestSettings(Settings):
    __test__ = False

    def api_key_for(self, model):
        return SecretStr(f"fake-{model}")


def completion(arguments=None, name="submit_Envelope", usage=True):
    message = {"role": "assistant", "content": "ok"}
    if arguments is not None:
        message["tool_calls"] = [
            {
                "id": "call-1",
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(arguments)},
            }
        ]
    response = {
        "id": "response-1",
        "object": "chat.completion",
        "created": 0,
        "model": "chat-model",
        "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
    }
    if usage:
        response["usage"] = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    return response


def client(tmp_path, replies, *, mode="record", **options):
    requests = []
    factories = []

    def respond(request):
        requests.append(request)
        reply = replies.pop(0)
        if isinstance(reply, int):
            return httpx.Response(reply, json={"error": {"message": "provider secret"}})
        return httpx.Response(200, json=reply)

    def factory(**kwargs):
        factories.append(kwargs)
        return OpenAI(**kwargs, http_client=httpx.Client(transport=httpx.MockTransport(respond)))

    settings = TestSettings(
        _env_file=None,
        llm_mode=mode,
        data_dir=tmp_path,
        chat_model="chat-model",
        embed_model="embed-model",
    )
    return LLMClient(settings, client_factory=factory, **options), requests, factories


class Item(BaseModel):
    sku: str


class Envelope(BaseModel):
    item: Item


def test_record_replay_key_and_no_key_access(tmp_path):
    live, requests, factories = client(tmp_path, [completion()])
    context = {"prompt_version": "extract.v1", "sources": {"source-1": "hash-v1"}}
    assert live.chat(MESSAGES, cache_context=context).choices[0].message.content == "ok"
    assert factories[0]["api_key"] == "fake-chat-model"
    assert factories[0]["max_retries"] == 0
    assert requests[0].url.path.endswith("/chat/completions")
    # Missing key file, and a factory that fails if called: replay must use neither.
    settings = Settings(
        _env_file=None,
        llm_mode="replay",
        data_dir=tmp_path,
        chat_model="chat-model",
        fastweb_keys_file=tmp_path / "absent.json",
    )
    replay = LLMClient(settings, client_factory=lambda **kw: pytest.fail("network client"))
    assert replay.chat(MESSAGES, cache_context=context).choices[0].message.content == "ok"
    assert replay.budget.calls == 0
    for changed in (
        {**context, "prompt_version": "extract.v2"},
        {**context, "sources": {"source-1": "hash-v2"}},
    ):
        with pytest.raises(ReplayMiss):
            replay.chat(MESSAGES, cache_context=changed)
    with pytest.raises(ReplayMiss):
        replay.chat(MESSAGES, temperature=0.7, cache_context=context)
    assert "fake-chat-model" not in repr(replay.traces)
    assert all("fake-chat-model" not in p.read_text() for p in tmp_path.rglob("*.json"))


def test_extract_inlines_nested_refs_and_retries_once(tmp_path):
    llm, requests, _ = client(
        tmp_path, [completion({"item": {}}), completion({"item": {"sku": "A-B"}})]
    )
    assert llm.extract(Envelope, MESSAGES).item.sku == "A-B"
    assert llm.budget.calls == 2
    bodies = [json.loads(r.content) for r in requests]
    assert bodies[0]["tool_choice"] == "required"
    assert "$ref" not in json.dumps(bodies[0]["tools"])
    assert "$defs" not in json.dumps(bodies[0]["tools"])
    assert "validation" in bodies[1]["messages"][-1]["content"]
    assert MESSAGES == [{"role": "user", "content": "Sanitized source"}]


@pytest.mark.parametrize(
    "response", [completion(), completion({}, name="wrong"), completion({"item": {}})]
)
def test_extract_abstains_after_two_invalid_submissions(tmp_path, response):
    llm, requests, _ = client(tmp_path, [response, response])
    with pytest.raises(ExtractionFailed):
        llm.extract(Envelope, MESSAGES)
    assert len(requests) == 2


def test_extract_retry_respects_global_call_budget(tmp_path):
    llm, requests, _ = client(tmp_path, [completion()], budget=CallBudget(max_calls=1))
    with pytest.raises(BudgetExceeded):
        llm.extract(Envelope, MESSAGES)
    assert len(requests) == 1


def test_backoff_charges_failed_attempts_and_sanitizes_trace(tmp_path):
    sleeps = []
    llm, requests, _ = client(tmp_path, [429, 503, completion()], sleep=sleeps.append)
    llm.chat(MESSAGES)
    assert len(requests) == llm.budget.calls == 3
    assert sleeps == [1, 2]
    assert llm.budget.tokens > 15
    assert [t["status"] for t in llm.traces] == [429, 503, 200]
    assert "provider secret" not in repr(llm.traces)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 500])
def test_nonretryable_provider_errors_do_not_leak_body(tmp_path, status):
    llm, requests, _ = client(tmp_path, [status])
    with pytest.raises(LLMCallFailed) as error:
        llm.chat(MESSAGES)
    assert "provider secret" not in str(error.value)
    assert len(requests) == 1


def test_transient_retry_limit_and_deadline(tmp_path):
    llm, requests, _ = client(tmp_path, [503, 503, 503], sleep=lambda _: None)
    with pytest.raises(LLMCallFailed):
        llm.chat(MESSAGES)
    assert len(requests) == 3
    llm, requests, _ = client(tmp_path, [429], deadline_seconds=0.5)
    with pytest.raises(BudgetExceeded, match="retry exceeds"):
        llm.chat(MESSAGES)
    assert len(requests) == 1


def test_token_budget_blocks_network_and_settles_usage(tmp_path):
    llm, requests, _ = client(tmp_path, [], budget=CallBudget(max_tokens=1))
    with pytest.raises(BudgetExceeded):
        llm.chat(MESSAGES)
    assert requests == []
    llm, _, _ = client(tmp_path, [completion()])
    llm.chat(MESSAGES)
    assert llm.budget.tokens == 15


def test_embeddings_per_model_key_order_dimensions_and_replay(tmp_path):
    response = {
        "object": "list",
        "model": "embed-model",
        "data": [
            {"index": 1, "object": "embedding", "embedding": [3.0, 4.0]},
            {"index": 0, "object": "embedding", "embedding": [1.0, 2.0]},
        ],
        "usage": {"prompt_tokens": 4, "total_tokens": 4},
    }
    llm, requests, factories = client(tmp_path, [response])
    assert llm.embed(["one", "two"], dimensions=2) == [[1, 2], [3, 4]]
    assert factories[0]["api_key"] == "fake-embed-model"
    assert requests[0].url.path.endswith("/embeddings")
    replay, _, _ = client(tmp_path, [], mode="replay")
    assert replay.embed(["one", "two"], dimensions=2) == [[1, 2], [3, 4]]
    with pytest.raises(ReplayMiss):
        replay.embed(["one", "two"], dimensions=3)


def test_invalid_embedding_response_fails(tmp_path):
    response = {
        "object": "list",
        "model": "embed-model",
        "data": [],
        "usage": {"prompt_tokens": 1, "total_tokens": 1},
    }
    llm, _, _ = client(tmp_path, [response])
    with pytest.raises(LLMCallFailed, match="embedding"):
        llm.embed(["one"], dimensions=2)


def test_cache_integrity_and_canonical_keys(tmp_path):
    assert cache_key({"a": 1, "b": 2}) == cache_key({"b": 2, "a": 1})
    cache = ResponseCache(tmp_path)
    key = cache_key({"input": "text"})
    cache.put(key, {"answer": 1})
    assert cache.get(key) == {"answer": 1}
    path = next(tmp_path.rglob("*.json"))
    path.write_text(path.read_text().replace('"answer": 1', '"answer": 2'))
    with pytest.raises(CacheCorrupt):
        cache.get(key)
    with pytest.raises(ValueError):
        cache.get("../escape")


def test_cache_writes_are_atomic_and_budget_is_thread_safe(tmp_path):
    cache = ResponseCache(tmp_path)
    key = cache_key({"input": "same"})
    budget = CallBudget(max_calls=3)
    admitted = []
    lock = Lock()

    def work(index):
        cache.put(key, {"answer": index})
        cache.get(key)
        try:
            budget.reserve(1)
            with lock:
                admitted.append(index)
        except BudgetExceeded:
            pass

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(work, range(12)))
    assert len(admitted) == budget.calls == 3
    assert cache.get(key)["answer"] in range(12)


def test_recursive_schema_and_unsafe_transport_parameters_rejected(tmp_path):
    class Recursive(BaseModel):
        child: "Recursive | None" = None

    with pytest.raises(ValueError, match="nonrecursive"):
        inline_schema(Recursive.model_json_schema())
    llm, _, _ = client(tmp_path, [])
    with pytest.raises(ValueError, match="unsupported"):
        llm.chat(MESSAGES, extra_headers={"Authorization": "secret"})


def test_live_does_not_record_and_null_usage_is_replayable(tmp_path):
    llm, _, _ = client(tmp_path, [completion(usage=False)], mode="live")
    llm.chat(MESSAGES)
    assert not list(tmp_path.rglob("*.json"))
    recorder, _, _ = client(tmp_path, [completion(usage=False)])
    recorder.chat(MESSAGES)
    replay, _, _ = client(tmp_path, [], mode="replay")
    assert replay.chat(MESSAGES).choices[0].message.content == "ok"


def test_extract_invalid_submission_replays_same_retry_path(tmp_path):
    recorder, _, _ = client(
        tmp_path, [completion({"item": {}}), completion({"item": {"sku": "A-B"}})]
    )
    recorder.extract(Envelope, MESSAGES)
    replay, requests, _ = client(tmp_path, [], mode="replay")
    assert replay.extract(Envelope, MESSAGES).item.sku == "A-B"
    assert requests == []
    assert len(replay.traces) == 2


def test_concurrency_is_bounded_across_provider_calls(tmp_path):
    import time

    active = 0
    peak = 0
    lock = Lock()

    def respond(request):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        time.sleep(0.025)
        with lock:
            active -= 1
        return httpx.Response(200, json=completion())

    def factory(**kwargs):
        return OpenAI(**kwargs, http_client=httpx.Client(transport=httpx.MockTransport(respond)))

    settings = TestSettings(_env_file=None, llm_mode="live", data_dir=tmp_path)
    llm = LLMClient(settings, client_factory=factory, concurrency=2)
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda _: llm.chat(MESSAGES), range(6)))
    assert peak == 2
    assert llm.budget.calls == 6
    assert llm.budget.tokens == 6 * 15


def test_expired_deadline_blocks_provider_construction(tmp_path):
    now = [0.0]
    llm, requests, factories = client(tmp_path, [], clock=lambda: now[0], deadline_seconds=1)
    now[0] = 2
    with pytest.raises(BudgetExceeded, match="deadline"):
        llm.chat(MESSAGES)
    assert requests == factories == []
