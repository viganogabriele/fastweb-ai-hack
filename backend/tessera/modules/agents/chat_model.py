"""AG-01 runtime: the agent loop on the real LLM client, recorded and replayed through the cache.

``LLMChatModel`` implements the pure loop's ``ChatModel`` (``modules/agents/runtime.py``) on top of
PLT-05's ``LLMClient``. One ``complete`` call is one Chat Completions request: the conversation,
the fixed tool allowlist and the generation settings go to the provider, and the reply comes back
as a ``ModelReply`` with its tool calls and token usage. Nothing about the allowlist, the budget or
the finish policy is delegated to the model here; that stays in the pure loop.

The request also carries the caller's ``cache_context`` (prompt version, source/context hashes,
model revision) plus the adapter version. ``LLM_MODE=record`` then writes the provider replies,
and ``LLM_MODE=replay`` rebuilds the same ``AgentTrace`` with no network and no keys. A recording
is reused only for the same prompt version, tools and inputs, because both the context and the
payload enter PLT-05's cache key.

Errors are mapped to what the loop can do with them:

- a provider failure or the run's call/token/deadline allowance becomes a non-retryable
  ``ModelError``. PLT-05 already retried 429/503 with backoff inside the turn; repeating the same
  call here would only burn the loop's turn budget without a new chance of success. The run ends
  in the deterministic fallback, which never guesses.
- a replay miss is deliberately *not* converted: it propagates out of the loop, because a missing
  recording must fail loudly instead of degrading into a plausible-looking fallback trace.

The loop passes its remaining time as ``timeout_s``. The adapter refuses to start a call when it
is spent; the HTTP call itself is bounded by the run client's own timeout and deadline, because
PLT-05 owns the provider transport and the adapter must not reach around it.
"""

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from openai.types.chat import ChatCompletion

from tessera.core.llm import BudgetExceeded as LLMBudgetExceeded
from tessera.core.llm import LLMCallFailed, LLMClient, RunLLMClient
from tessera.modules.agents.runtime import Message, ModelError, ModelReply, ToolCall

ADAPTER_VERSION = "1"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_OUTPUT_TOKENS = 2048


class ChatClient(Protocol):
    """The part of PLT-05's client this adapter uses (``LLMClient`` or its run-bound faÃ§ade)."""

    def chat(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: list[dict] | None = None,
        model: str | None = None,
        *,
        cache_context: Mapping[str, Any] | None = None,
        **generation: Any,
    ) -> ChatCompletion: ...


class LLMChatModel:
    """``ChatModel`` over PLT-05's client: one bounded Chat Completions request per turn."""

    def __init__(
        self,
        client: ChatClient,
        *,
        cache_context: Mapping[str, Any],
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> None:
        prompt_version = cache_context.get("prompt_version")
        if not isinstance(prompt_version, str) or not prompt_version.strip():
            raise ValueError("cache_context requires a non-empty prompt_version")
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.cache_context = {"agent_runtime": ADAPTER_VERSION, **cache_context}

    def complete(
        self, messages: Sequence[Message], tools: Sequence[Message], timeout_s: float
    ) -> ModelReply:
        if timeout_s <= 0:
            raise ModelError("no time left for another model call", retryable=False)
        try:
            response = self.client.chat(
                messages,
                list(tools),
                self.model,
                cache_context=self.cache_context,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except LLMBudgetExceeded as error:
            raise ModelError(str(error), retryable=False) from None
        except LLMCallFailed as error:
            raise ModelError(str(error), retryable=False) from None
        return _reply(response)


def model_for_run(
    client: LLMClient | RunLLMClient,
    *,
    prompt_version: str,
    model: str | None = None,
    max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    cache_context: Mapping[str, Any] | None = None,
) -> LLMChatModel:
    """Bind the adapter to a run client with the prompt/versioned context of this agent."""
    return LLMChatModel(
        client,
        cache_context={"prompt_version": prompt_version, **dict(cache_context or {})},
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )


def _reply(response: ChatCompletion) -> ModelReply:
    if len(response.choices) != 1:
        raise ModelError("expected exactly one completion", retryable=False)
    message = response.choices[0].message
    calls: list[ToolCall] = []
    for call in message.tool_calls or ():
        if call.type != "function":
            raise ModelError(f"unsupported tool call type: {call.type}", retryable=False)
        calls.append(
            ToolCall(
                id=call.id,
                name=call.function.name,
                arguments=call.function.arguments or "",
            )
        )
    usage = response.usage
    return ModelReply(
        content=message.content,
        tool_calls=tuple(calls),
        tokens_in=None if usage is None else usage.prompt_tokens,
        tokens_out=None if usage is None else usage.completion_tokens,
    )
