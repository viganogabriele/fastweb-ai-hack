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


def test_repeated_record_reuses_frozen_response_before_network(tmp_path):
    first = completion()
    second = completion()
    second["choices"][0]["message"]["content"] = "different nondeterministic output"
    replies = [first, second]
    recorder, requests, _ = client(tmp_path, replies)
    original = recorder.chat(MESSAGES)
    assert recorder.chat(MESSAGES) == original
    assert len(requests) == recorder.budget.calls == 1
    assert replies == [second]
    assert recorder.traces[-1]["cache_hit"] is True
    replay, _, _ = client(tmp_path, [], mode="replay")
    assert replay.chat(MESSAGES) == original
    # Changing admissible context/version creates a different recording.
    changed = recorder.chat(MESSAGES, cache_context={"source_hash": "changed"})
    assert changed.choices[0].message.content == "different nondeterministic output"
    assert recorder.chat(MESSAGES) == original


def test_simultaneous_record_misses_return_one_immutable_winner(tmp_path):
    from threading import Barrier

    rendezvous = Barrier(2)
    lock = Lock()
    requests = []

    def respond(request):
        with lock:
            index = len(requests)
            requests.append(request)
        result = completion()
        result["choices"][0]["message"]["content"] = f"candidate-{index}"
        rendezvous.wait(timeout=5)
        return httpx.Response(200, json=result)

    def factory(**kwargs):
        return OpenAI(**kwargs, http_client=httpx.Client(transport=httpx.MockTransport(respond)))

    settings = TestSettings(_env_file=None, llm_mode="record", data_dir=tmp_path)
    recorder = LLMClient(settings, client_factory=factory)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: recorder.chat(MESSAGES), range(2)))
    assert len(requests) == 2
    assert results[0] == results[1]
    replay = LLMClient(settings.model_copy(update={"llm_mode": "replay"}))
    assert replay.chat(MESSAGES) == results[0]
    assert recorder.chat(MESSAGES) == results[0]
    assert len(requests) == 2


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("mode", ["record", "live"])
def test_nonfinite_embeddings_fail_before_cache_write(tmp_path, value, mode):
    response = {
        "object": "list",
        "model": "embed-model",
        "data": [{"index": 0, "object": "embedding", "embedding": [value]}],
        "usage": {"prompt_tokens": 1, "total_tokens": 1},
    }

    def factory(**kwargs):
        def respond(request):
            # Deliberately malformed numeric JSON from an untrusted provider.
            return httpx.Response(
                200, content=json.dumps(response), headers={"content-type": "application/json"}
            )

        return OpenAI(**kwargs, http_client=httpx.Client(transport=httpx.MockTransport(respond)))

    settings = TestSettings(_env_file=None, llm_mode=mode, data_dir=tmp_path)
    llm = LLMClient(settings, client_factory=factory)
    with pytest.raises(LLMCallFailed, match="nonfinite|finite values"):
        llm.embed(["text"], dimensions=1)
    assert not list(tmp_path.rglob("*.json"))


def test_cache_refuses_nonfinite_json_and_never_overwrites_existing_response(tmp_path):
    cache = ResponseCache(tmp_path)
    key = cache_key({"source": "stable"})
    assert cache.put(key, {"answer": "A"}) == {"answer": "A"}
    assert cache.put(key, {"answer": "B"}) == {"answer": "A"}
    assert cache.get(key) == {"answer": "A"}
    with pytest.raises(ValueError):
        cache_key({"number": float("nan")})
    with pytest.raises(ValueError):
        cache.put(cache_key({"source": "other"}), {"number": float("inf")})
    assert len(list(tmp_path.rglob("*.json"))) == 1


def run_spec(**changes):
    from tessera.core.contracts.runs import ModuleManifest, ModuleSnapshot, RunSpec

    module = ModuleSnapshot(
        manifest=ModuleManifest(
            id="ing.extract",
            version="1",
            layer="ingestion",
            description="Extract source",
            requires=(),
            optional_inputs=(),
            produces=("observations",),
            enabled=True,
            mode="live",
            params_schema={},
        ),
        params={"threshold": 0.5},
    )
    return RunSpec(
        **{
            "run_id": "run-original",
            "scenario_id": "dev",
            "as_of": "2026-10-21T20:00:00Z",
            "stores": ("MIL01",),
            "source_manifest_hash": "sources-1",
            "config_hash": "configuration-1",
            "code_version": "revision-1",
            "mode": "live",
            "modules": (module,),
            "prompt_versions": {"extract": "v1"},
            "model_versions": {"chat-model": "r1"},
            "authorized_fixture_refs": (),
            **changes,
        }
    )


def test_run_binding_isolates_as_of_and_reuses_same_snapshot_across_run_ids(tmp_path):
    llm, requests, _ = client(tmp_path, [completion(), completion()])
    spec = run_spec()
    original = llm.for_run(spec)
    original.chat(MESSAGES)
    assert original.cache is llm.cache
    assert original.budget is llm.budget
    assert original.traces is llm.traces
    original_calls = llm.budget.calls
    equivalent = llm.for_run(run_spec(run_id="another-execution", mode="recorded"))
    assert equivalent.chat(MESSAGES).choices[0].message.content == "ok"
    assert llm.budget.calls == original_calls
    future = llm.for_run(run_spec(as_of="2026-10-22T20:00:00Z"))
    future.chat(MESSAGES)
    assert llm.budget.calls == len(requests) == 2
    assert original.traces[0]["key"] != original.traces[-1]["key"]
    settings = Settings(
        _env_file=None,
        data_dir=tmp_path,
        chat_model="chat-model",
        llm_mode="replay",
        fastweb_keys_file=tmp_path / "absent.json",
    )
    replay = LLMClient(settings, client_factory=lambda **kw: pytest.fail("network client"))
    assert replay.for_run(spec).chat(MESSAGES).choices[0].message.content == "ok"
    assert replay.budget.calls == 0


def test_runs_without_erp_boundary_replay_recordings_from_the_previous_contract(tmp_path):
    from tessera.core.llm import RunLLMClient

    # Recreate the pre-boundary serialized run context used by existing recordings.
    spec = run_spec()
    legacy_scope = spec.model_dump(mode="json", exclude={"run_id", "mode", "erp_max_seq"})
    legacy_scope["namespace"] = "product"
    for module in legacy_scope["modules"]:
        module["manifest"].pop("mode")
    recorder, requests, _ = client(tmp_path, [completion()])
    RunLLMClient(recorder, json.dumps(legacy_scope)).chat(MESSAGES)
    assert len(requests) == 1
    replay, requests, _ = client(tmp_path, [], mode="replay")
    assert replay.for_run(spec).chat(MESSAGES).choices[0].message.content == "ok"
    assert requests == []


@pytest.mark.parametrize(
    "changes",
    [
        {"stores": ("PAR01",)},
        {"scenario_id": "other-scenario"},
        {"source_manifest_hash": "sources-2"},
        {"config_hash": "configuration-2"},
        {"code_version": "revision-2"},
        {"prompt_versions": {"extract": "v2"}},
        {"model_versions": {"chat-model": "r2"}},
        {"authorized_fixture_refs": ("new-fixture",)},
        {"erp_max_seq": 0},
    ],
)
def test_run_scope_versions_and_provenance_isolate_recordings(tmp_path, changes):
    llm, _, _ = client(tmp_path, [completion()])
    llm.for_run(run_spec()).chat(MESSAGES)
    replay, _, _ = client(tmp_path, [], mode="replay")
    with pytest.raises(ReplayMiss):
        replay.for_run(run_spec(**changes)).chat(MESSAGES)


def test_run_binding_freezes_nested_snapshot_and_namespaces_caller_context(tmp_path):
    llm, requests, _ = client(tmp_path, [completion(), completion(), completion()])
    spec = run_spec()
    bound = llm.for_run(spec)
    original = bound.chat(MESSAGES, cache_context={"catalog_version": "one"})
    spec.prompt_versions["extract"] = "mutated-after-binding"
    spec.modules[0].params["threshold"] = 0.75
    assert bound.chat(MESSAGES, cache_context={"catalog_version": "one"}) == original
    assert len(requests) == 1
    llm.for_run(spec).chat(MESSAGES, cache_context={"catalog_version": "one"})
    assert len(requests) == 2
    bound.chat(MESSAGES, cache_context={"run": {"as_of": "future"}})
    assert len(requests) == 3
    replay, _, _ = client(tmp_path, [], mode="replay")
    # A caller-provided run key cannot impersonate another bound run's scope.
    with pytest.raises(ReplayMiss):
        replay.for_run(run_spec(as_of="2026-10-22T20:00:00Z")).chat(
            MESSAGES, cache_context={"run": {"as_of": "future"}}
        )


def test_run_bound_extract_and_embed_share_scope_and_replay_mode_independence(tmp_path):
    embedding = {
        "object": "list",
        "model": "embed-model",
        "data": [{"index": 0, "object": "embedding", "embedding": [1.0]}],
        "usage": {"prompt_tokens": 1, "total_tokens": 1},
    }
    llm, requests, _ = client(tmp_path, [completion({"item": {"sku": "A-B"}}), embedding])
    spec = run_spec()
    llm.for_run(spec).extract(Envelope, MESSAGES)
    llm.for_run(spec).embed(["text"], dimensions=1)
    assert llm.budget.calls == len(requests) == 2
    replay, _, _ = client(tmp_path, [], mode="replay")
    snapshot = spec.model_dump()
    snapshot["modules"][0]["manifest"]["mode"] = "recorded"
    snapshot["run_id"] = "replay-execution"
    snapshot["mode"] = "recorded"
    from tessera.core.contracts.runs import RunSpec

    bound = replay.for_run(RunSpec.model_validate(snapshot))
    assert bound.extract(Envelope, MESSAGES).item.sku == "A-B"
    assert bound.embed(["text"], dimensions=1) == [[1.0]]
    assert replay.budget.calls == 0


def test_fixture_recordings_never_satisfy_product_replay(tmp_path):
    recorder, requests, _ = client(tmp_path, [completion()])
    fixture = run_spec(mode="fixture")
    recorder.for_run(fixture).chat(MESSAGES)
    assert len(requests) == 1
    replay = LLMClient(recorder.settings.model_copy(update={"llm_mode": "replay"}))
    assert replay.for_run(fixture).chat(MESSAGES).choices[0].message.content == "ok"
    with pytest.raises(ReplayMiss):
        replay.for_run(run_spec(mode="recorded")).chat(MESSAGES)
    with pytest.raises(ReplayMiss):
        replay.for_run(run_spec(mode="live")).chat(MESSAGES)
    assert len(requests) == 1


def test_sdk_assistant_message_can_continue_agent_conversation(tmp_path):
    llm, requests, _ = client(tmp_path, [completion(), completion()])
    first = llm.chat(MESSAGES)
    follow_up = [*MESSAGES, first.choices[0].message, {"role": "user", "content": "more"}]
    llm.chat(follow_up)
    sent = json.loads(requests[1].content)["messages"]
    assert sent[-2] == {"role": "assistant", "content": "ok"}


def test_usage_overrun_keeps_recording_and_blocks_next_call(tmp_path):
    reply = completion()
    reply["usage"]["total_tokens"] = 10**9
    llm, requests, _ = client(tmp_path, [reply], budget=CallBudget(max_tokens=100_000))
    assert llm.chat(MESSAGES).choices[0].message.content == "ok"
    replay = LLMClient(llm.settings.model_copy(update={"llm_mode": "replay"}))
    assert replay.chat(MESSAGES).choices[0].message.content == "ok"
    with pytest.raises(BudgetExceeded):
        llm.chat([{"role": "user", "content": "next"}])
    assert len(requests) == 1


def test_null_or_invalid_usage_settles_to_reservation(tmp_path):
    reply = completion()
    reply["usage"]["total_tokens"] = None
    llm, _, _ = client(tmp_path, [reply])
    llm.chat(MESSAGES)
    assert llm.budget.tokens > 0
    assert llm.traces[-1]["tokens"] == llm.budget.tokens


def test_budget_and_deadline_come_from_settings(tmp_path):
    llm, _, _ = client(tmp_path, [])
    settings = llm.settings.model_copy(
        update={"llm_max_calls": 7, "llm_max_tokens": 9, "llm_deadline_seconds": 5}
    )
    bounded = LLMClient(settings, clock=lambda: 0)
    assert (bounded.budget.max_calls, bounded.budget.max_tokens) == (7, 9)
    assert bounded._remaining() == 5
