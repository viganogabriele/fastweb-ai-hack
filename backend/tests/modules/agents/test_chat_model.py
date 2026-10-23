"""AG-01 runtime: provider replies are recorded once and replay the same agent trace offline."""

import json
from datetime import UTC, datetime
from types import SimpleNamespace

import httpx
import pytest
from openai import OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, SecretStr

from tessera.core.cache import ReplayMiss
from tessera.core.config import Settings
from tessera.core.contracts import ArtifactRef
from tessera.core.llm import CallBudget, LLMClient
from tessera.modules.agents.chat_model import LLMChatModel, model_for_run
from tessera.modules.agents.runtime import (
    AgentLoop,
    ModelError,
    Tool,
    ToolCall,
    ToolResult,
    TraceMeta,
)

AS_OF = datetime(2026, 10, 22, 19, 0, tzinfo=UTC)
META = TraceMeta(
    run_id="run-1", scenario_id="historical", case_id="case-D1", as_of=AS_OF, mode="fixture"
)
MESSAGES = [
    {"role": "system", "content": "You investigate a case."},
    {"role": "user", "content": "Case case-D1."},
]


class TestSettings(Settings):
    __test__ = False

    def api_key_for(self, model):
        return SecretStr(f"fake-{model}")


class CaseArgs(BaseModel):
    case_id: str


class Recorder:
    """The read-only part of the RFC section 4.8.2 investigator allowlist, deterministic."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def evidence(self, args: CaseArgs) -> ToolResult:
        self.calls.append("get_case_evidence")
        return ToolResult(
            {"observations": ["obs-1"]},
            (),
            (ArtifactRef(kind="Observation", id="obs-1", version="v1"),),
        )

    def options(self, args: CaseArgs) -> ToolResult:
        self.calls.append("evaluate_options")
        return ToolResult(
            {"options": ["opt-1"]},
            (),
            (ArtifactRef(kind="ActionOption", id="opt-1", version="v1"),),
        )

    def tools(self) -> list[Tool]:
        return [
            Tool("get_case_evidence", "Evidence for a case", CaseArgs, self.evidence),
            Tool("evaluate_options", "Deterministic options", CaseArgs, self.options),
        ]


def completion(content=None, calls=(), usage=True):
    message = {"role": "assistant", "content": content}
    if calls:
        message["tool_calls"] = [
            {
                "id": call_id,
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(arguments)},
            }
            for call_id, name, arguments in calls
        ]
    response = {
        "id": "response-1",
        "object": "chat.completion",
        "created": 0,
        "model": "chat-model",
        "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
    }
    if usage:
        response["usage"] = {"prompt_tokens": 100, "completion_tokens": 10, "total_tokens": 110}
    return response


def finish_call() -> tuple[str, str, dict]:
    return (
        "call-3",
        "finish",
        {
            "status": "action_proposed",
            "option_id": "opt-1",
            "evidence_refs": ["obs-1", "opt-1"],
            "rationale": "the cardigan is out of stock and the donor is feasible",
        },
    )


def scripted():
    """The same three-turn conversation the pure loop tests use, provider-shaped."""
    return [
        completion(calls=[("call-1", "get_case_evidence", {"case_id": "case-D1"})]),
        completion(calls=[("call-2", "evaluate_options", {"case_id": "case-D1"})]),
        completion(calls=[finish_call()]),
    ]


class FakeClock:
    """A frozen monotonic clock: tool durations are part of the trace, so keep them at zero."""

    def __call__(self) -> float:
        return 0.0


class Provider:
    def __init__(self, replies):
        self.replies = list(replies)
        self.requests = []

    def __call__(self, **kwargs):
        def respond(request):
            self.requests.append(json.loads(request.content))
            reply = self.replies.pop(0)
            if isinstance(reply, int):
                return httpx.Response(reply, json={"error": {"message": "provider secret"}})
            return httpx.Response(200, json=reply)

        return OpenAI(**kwargs, http_client=httpx.Client(transport=httpx.MockTransport(respond)))


def settings(tmp_path, mode="record"):
    return TestSettings(
        _env_file=None,
        llm_mode=mode,
        data_dir=tmp_path,
        chat_model="chat-model",
    )


def run_agent(model, recorder=None, budget=None):
    recorder = recorder or Recorder()
    loop = AgentLoop(model, recorder.tools(), budget=budget, clock=FakeClock())
    return loop.run(MESSAGES, META), recorder


def test_complete_maps_tool_calls_and_usage() -> None:
    class FakeClient:
        def __init__(self, response):
            self.response = response
            self.calls = []

        def chat(self, messages, tools=None, model=None, **kwargs):
            self.calls.append({"messages": messages, "tools": tools, "model": model, **kwargs})
            return self.response

    client = FakeClient(ChatCompletion.model_validate(completion(calls=[finish_call()])))
    model = LLMChatModel(client, cache_context={"prompt_version": "investigator.v1"})
    reply = model.complete(MESSAGES, [{"type": "function"}], 30.0)

    assert reply.content is None
    assert reply.tool_calls == (
        ToolCall(
            id="call-3",
            name="finish",
            arguments=json.dumps(finish_call()[2]),
        ),
    )
    assert (reply.tokens_in, reply.tokens_out) == (100, 10)
    assert client.calls[0]["model"] is None
    assert client.calls[0]["cache_context"]["agent_runtime"] == "1"
    assert client.calls[0]["cache_context"]["prompt_version"] == "investigator.v1"
    assert client.calls[0]["temperature"] == 0.0
    assert client.calls[0]["max_tokens"] == 2048


def test_missing_usage_is_unknown_not_zero() -> None:
    class FakeClient:
        def chat(self, *args, **kwargs):
            return ChatCompletion.model_validate(completion(usage=False))

    model = LLMChatModel(FakeClient(), cache_context={"prompt_version": "investigator.v1"})
    reply = model.complete(MESSAGES, [], 30.0)
    assert (reply.tokens_in, reply.tokens_out) == (None, None)


def test_unusable_completions_and_tool_types_are_refused() -> None:
    two = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="a", tool_calls=None))] * 2,
        usage=None,
    )
    model = LLMChatModel(
        type("C", (), {"chat": lambda self, *a, **k: two})(),
        cache_context={"prompt_version": "investigator.v1"},
    )
    with pytest.raises(ModelError, match="exactly one completion"):
        model.complete(MESSAGES, [], 30.0)

    call = SimpleNamespace(id="c", type="web_search", function=None)
    message = SimpleNamespace(content=None, tool_calls=[call])
    wrong = SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)
    model = LLMChatModel(
        type("C", (), {"chat": lambda self, *a, **k: wrong})(),
        cache_context={"prompt_version": "investigator.v1"},
    )
    with pytest.raises(ModelError, match="unsupported tool call type"):
        model.complete(MESSAGES, [], 30.0)


def test_cache_context_requires_a_prompt_version() -> None:
    client = type("C", (), {})()
    with pytest.raises(ValueError, match="prompt_version"):
        LLMChatModel(client, cache_context={})
    with pytest.raises(ValueError, match="prompt_version"):
        LLMChatModel(client, cache_context={"prompt_version": "  "})


def test_no_time_left_does_not_call_the_provider() -> None:
    class FakeClient:
        def __init__(self):
            self.calls = 0

        def chat(self, *args, **kwargs):
            self.calls += 1

    client = FakeClient()
    model = LLMChatModel(client, cache_context={"prompt_version": "investigator.v1"})
    with pytest.raises(ModelError) as error:
        model.complete(MESSAGES, [], 0)
    assert error.value.retryable is False
    assert client.calls == 0


def test_record_then_replay_produces_the_same_trace(tmp_path) -> None:
    provider = Provider(scripted())
    recorded_client = LLMClient(settings(tmp_path, "record"), client_factory=provider)
    recorder = Recorder()
    recorded, _ = run_agent(
        LLMChatModel(recorded_client, cache_context={"prompt_version": "investigator.v1"}),
        recorder,
    )

    assert recorded.stop_reason == "finished"
    assert recorded.finish.option_id == "opt-1"
    assert [step.tool for step in recorded.trace.steps] == [
        "get_case_evidence",
        "evaluate_options",
        "finish",
    ]
    assert recorder.calls == ["get_case_evidence", "evaluate_options"]
    assert (recorded.trace.tokens_in, recorded.trace.tokens_out) == (300, 30)
    assert len(provider.requests) == 3
    # The allowlist and the conversation are sent as the loop built them.
    assert [t["function"]["name"] for t in provider.requests[0]["tools"]] == [
        "get_case_evidence",
        "evaluate_options",
        "finish",
    ]
    assert provider.requests[1]["messages"][-1]["role"] == "tool"

    replay_client = LLMClient(
        settings(tmp_path, "replay"),
        client_factory=lambda **kwargs: pytest.fail("replay must not build a network client"),
    )
    replayed, _ = run_agent(
        LLMChatModel(replay_client, cache_context={"prompt_version": "investigator.v1"}),
        Recorder(),
    )

    assert replayed.trace.model_dump(mode="json") == recorded.trace.model_dump(mode="json")
    assert (replayed.turns, replayed.tool_calls) == (recorded.turns, recorded.tool_calls)
    assert replayed.finish == recorded.finish
    assert replay_client.budget.calls == 0
    assert all(trace["cache_hit"] for trace in replay_client.traces)


def test_replay_miss_propagates_instead_of_falling_back(tmp_path) -> None:
    provider = Provider(scripted())
    recorded_client = LLMClient(settings(tmp_path, "record"), client_factory=provider)
    run_agent(LLMChatModel(recorded_client, cache_context={"prompt_version": "investigator.v1"}))

    replay_client = LLMClient(
        settings(tmp_path, "replay"),
        client_factory=lambda **kwargs: pytest.fail("replay must not build a network client"),
    )
    with pytest.raises(ReplayMiss):
        run_agent(LLMChatModel(replay_client, cache_context={"prompt_version": "investigator.v2"}))


def test_provider_failure_ends_in_the_deterministic_fallback(tmp_path) -> None:
    provider = Provider([401])
    recorded_client = LLMClient(settings(tmp_path, "live"), client_factory=provider)
    run, _ = run_agent(
        LLMChatModel(recorded_client, cache_context={"prompt_version": "investigator.v1"})
    )

    assert len(provider.requests) == 1  # 401 is not retried
    assert run.stop_reason == "model_error"
    assert run.trace.fallback_used is True
    assert run.trace.outcome == "verify"
    assert run.trace.steps[-1].tool == "fallback"
    assert run.trace.steps[-1].error is None


def test_exhausted_llm_budget_ends_in_the_deterministic_fallback(tmp_path) -> None:
    provider = Provider(scripted())
    client = LLMClient(
        settings(tmp_path, "record"),
        client_factory=provider,
        budget=CallBudget(max_calls=0),
    )
    run, _ = run_agent(LLMChatModel(client, cache_context={"prompt_version": "investigator.v1"}))
    assert provider.requests == []
    assert run.stop_reason == "model_error"
    assert run.trace.outcome == "verify"


def test_model_for_run_versions_the_prompt() -> None:
    client = type("C", (), {"chat": lambda self, *a, **k: None})()
    model = model_for_run(
        client, prompt_version="investigator.v1", cache_context={"sources": {"doc-1": "hash-1"}}
    )
    assert model.cache_context == {
        "agent_runtime": "1",
        "prompt_version": "investigator.v1",
        "sources": {"doc-1": "hash-1"},
    }
