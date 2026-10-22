"""Bounded Fastweb OpenAI-compatible calls and deterministic offline replay.

Pass prompt/schema/tool versions, model revision, source/context hashes and catalog
version in ``cache_context``. Full payload, model, provider and generation parameters
always enter the key. Do not include credentials or unsanitized personal data.
"""

import json
import re
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, TypeVar
from urllib.parse import urlsplit

from openai import APIError, OpenAI
from openai.types.chat import ChatCompletion
from openai.types.create_embedding_response import CreateEmbeddingResponse
from pydantic import BaseModel, ValidationError

from tessera.core.cache import ResponseCache, cache_key
from tessera.core.config import Settings, get_settings

T = TypeVar("T", bound=BaseModel)


class ExtractionFailed(ValueError):
    """Two attempts failed validation; the caller must record an abstention."""


class BudgetExceeded(RuntimeError):
    """The global call/token/deadline allowance cannot cover this attempt."""


class LLMCallFailed(RuntimeError):
    """Provider failure; intentionally excludes provider bodies and credentials."""


@dataclass
class CallBudget:
    max_calls: int = 100
    max_tokens: int = 200_000
    calls: int = 0
    tokens: int = 0
    _lock: Any = field(default_factory=threading.Lock, repr=False)

    def reserve(self, tokens: int) -> None:
        with self._lock:
            if self.calls >= self.max_calls or self.tokens + tokens > self.max_tokens:
                raise BudgetExceeded("LLM call/token budget exhausted")
            self.calls += 1
            self.tokens += tokens

    def settle(self, reserved: int, actual: int) -> None:
        with self._lock:
            self.tokens += actual - reserved
            if self.tokens > self.max_tokens:
                raise BudgetExceeded("provider usage exceeded LLM token budget")


def inline_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Expand local Pydantic refs; reject recursive schemas unsupported by Gemma."""
    definitions = schema.get("$defs", {})

    def visit(value: Any, parents: tuple[str, ...] = ()) -> Any:
        if isinstance(value, list):
            return [visit(item, parents) for item in value]
        if not isinstance(value, dict):
            return value
        if "$ref" in value:
            ref = value["$ref"]
            name = ref.removeprefix("#/$defs/")
            if not ref.startswith("#/$defs/") or name not in definitions or name in parents:
                raise ValueError("extract requires nonrecursive local JSON schema references")
            expanded = visit(definitions[name], (*parents, name))
            return {**expanded, **visit({k: v for k, v in value.items() if k != "$ref"}, parents)}
        return {k: visit(v, parents) for k, v in value.items() if k != "$defs"}

    return visit(schema)


class LLMClient:
    """Synchronous, thread-safe call allowance shared by chat/extract/embed.

    Use one client per bounded run (its deadline starts at construction), or pass
    the same CallBudget to multiple clients to share a larger allowance. Provider
    failures retain their conservative token reservation because billed usage is
    unknown; successful calls settle to reported usage. Replay costs no budget.

    Example::

        llm = LLMClient(settings)
        result = llm.extract(Candidates, messages, cache_context={
            "prompt_version": "extract_observations.v1",
            "sources": {document_id: source_hash},
            "context_hash": allowed_context_hash,
            "model_revision": "known-provider-revision",
        })

    Responses retain the OpenAI chat/tool-call shape for agent round trips.
    ``extract`` returns the schema instance; ``embed`` returns ordered vectors.
    ``traces`` contains hashes, counts and timings, with no payload or credentials.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        cache: ResponseCache | None = None,
        budget: CallBudget | None = None,
        client_factory: Callable[..., Any] = OpenAI,
        concurrency: int = 4,
        timeout: float = 60,
        max_retries: int = 2,
        deadline_seconds: float = 180,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ):
        if concurrency < 1 or timeout <= 0 or not 0 <= max_retries <= 2 or deadline_seconds <= 0:
            raise ValueError("invalid LLM limits")
        self.settings = settings or get_settings()
        url = urlsplit(self.settings.fastweb_base_url)
        if url.username or url.password or url.query or url.fragment:
            raise ValueError("provider URL must not contain credentials, query or fragment")
        self.cache = cache or ResponseCache(self.settings.data_dir / "llm_cache")
        self.budget = budget or CallBudget()
        self._factory = client_factory
        self._semaphore = threading.BoundedSemaphore(concurrency)
        self._timeout = timeout
        self._max_retries = max_retries
        self._clock = clock
        self._sleep = sleep
        self._deadline = clock() + deadline_seconds
        self.traces: list[dict[str, Any]] = []

    def _remaining(self) -> float:
        remaining = self._deadline - self._clock()
        if remaining <= 0:
            raise BudgetExceeded("LLM deadline exhausted")
        return remaining

    def _request(self, operation: str, payload: dict, context: Mapping[str, Any] | None) -> dict:
        key = cache_key(
            {
                "version": 1,
                "provider": self.settings.fastweb_base_url.rstrip("/"),
                "operation": operation,
                "request": payload,
                "context": dict(context or {}),
            }
        )
        if self.settings.llm_mode == "replay":
            response = self.cache.get(key)
            self.traces.append(
                {
                    "key": key,
                    "operation": operation,
                    "model": payload["model"],
                    "mode": "replay",
                    "latency_seconds": 0,
                    "attempt": 0,
                    "tokens": (response.get("usage") or {}).get("total_tokens", 0),
                }
            )
            return response
        # Byte count is a conservative upper bound for ordinary text tokenization.
        reserved = len(json.dumps(payload, ensure_ascii=False).encode()) + payload.get(
            "max_tokens", 0
        )
        if not self._semaphore.acquire(timeout=self._remaining()):
            raise BudgetExceeded("LLM concurrency wait exhausted deadline")
        try:
            # Lazy construction: replay does not read keys or construct any network client.
            with self._factory(
                api_key=self.settings.api_key_for(payload["model"]).get_secret_value(),
                base_url=self.settings.fastweb_base_url,
                timeout=self._timeout,
                max_retries=0,
            ) as client:
                for attempt in range(self._max_retries + 1):
                    remaining = self._remaining()
                    self.budget.reserve(reserved)
                    start = self._clock()
                    trace = {
                        "key": key,
                        "operation": operation,
                        "model": payload["model"],
                        "mode": self.settings.llm_mode,
                        "attempt": attempt + 1,
                    }
                    try:
                        endpoint = (
                            client.chat.completions if operation == "chat" else client.embeddings
                        )
                        result = endpoint.create(**payload, timeout=min(self._timeout, remaining))
                    except APIError as error:
                        status = getattr(error, "status_code", None)
                        trace.update(
                            status=status, tokens=reserved, latency_seconds=self._clock() - start
                        )
                        self.traces.append(trace)
                        if status not in (429, 503) or attempt == self._max_retries:
                            raise LLMCallFailed(f"LLM provider failure (status={status})") from None
                        delay = 2**attempt
                        if delay >= self._remaining():
                            raise BudgetExceeded("LLM retry exceeds deadline") from None
                        self._sleep(delay)
                        continue
                    response = result.model_dump(mode="json")
                    tokens = (response.get("usage") or {}).get("total_tokens", reserved)
                    trace.update(tokens=tokens, latency_seconds=self._clock() - start, status=200)
                    self.traces.append(trace)
                    self.budget.settle(reserved, tokens)
                    if self.settings.llm_mode == "record":
                        self.cache.put(key, response)
                    return response
        finally:
            self._semaphore.release()
        raise AssertionError("unreachable")

    def chat(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: list[dict] | None = None,
        model: str | None = None,
        *,
        cache_context: Mapping[str, Any] | None = None,
        **generation: Any,
    ) -> ChatCompletion:
        allowed = {
            "temperature",
            "top_p",
            "max_tokens",
            "seed",
            "stop",
            "tool_choice",
            "parallel_tool_calls",
            "frequency_penalty",
            "presence_penalty",
        }
        if set(generation) - allowed:
            raise ValueError("unsupported generation parameter")
        payload = {
            "model": model or self.settings.chat_model,
            "messages": list(messages),
            "max_tokens": 2048,
            **generation,
        }
        if not isinstance(payload["max_tokens"], int) or payload["max_tokens"] <= 0:
            raise ValueError("max_tokens must be positive")
        if tools is not None:
            payload["tools"] = tools
        return ChatCompletion.model_validate(self._request("chat", payload, cache_context))

    def extract(
        self,
        schema: type[T],
        messages: Sequence[Mapping[str, Any]],
        *,
        model: str | None = None,
        cache_context: Mapping[str, Any] | None = None,
        **generation: Any,
    ) -> T:
        name = "submit_" + re.sub(r"[^a-zA-Z0-9_-]", "_", schema.__name__)[:57]
        tool = {
            "type": "function",
            "function": {"name": name, "parameters": inline_schema(schema.model_json_schema())},
        }
        conversation = list(messages)
        generation["tool_choice"] = "required"
        for attempt in range(2):
            response = self.chat(
                conversation, [tool], model, cache_context=cache_context, **generation
            )
            try:
                if len(response.choices) != 1:
                    raise ValueError("expected one completion")
                calls = response.choices[0].message.tool_calls or []
                if len(calls) != 1 or calls[0].type != "function" or calls[0].function.name != name:
                    raise ValueError("expected exactly the requested submission tool")
                return schema.model_validate_json(calls[0].function.arguments)
            except (ValueError, ValidationError) as error:
                if attempt == 1:
                    raise ExtractionFailed(
                        "structured extraction failed after two attempts"
                    ) from None
                # Validation details omit input values; retry stays within the same global budget.
                details = (
                    json.dumps(
                        [
                            {"location": item["loc"], "type": item["type"]}
                            for item in error.errors(include_input=False, include_url=False)
                        ]
                    )
                    if isinstance(error, ValidationError)
                    else str(error)
                )
                conversation.append(
                    {
                        "role": "user",
                        "content": (
                            f"Previous submission failed validation: {details}. "
                            f"Submit corrected arguments using only {name}."
                        ),
                    }
                )
        raise AssertionError("unreachable")

    def embed(
        self,
        texts: Sequence[str],
        dimensions: int = 512,
        *,
        model: str | None = None,
        cache_context: Mapping[str, Any] | None = None,
    ) -> list[list[float]]:
        if dimensions <= 0 or isinstance(texts, str) or not texts:
            raise ValueError("embed requires nonempty texts and positive dimensions")
        response = CreateEmbeddingResponse.model_validate(
            self._request(
                "embed",
                {
                    "model": model or self.settings.embed_model,
                    "input": list(texts),
                    "dimensions": dimensions,
                    "encoding_format": "float",
                },
                cache_context,
            )
        )
        data = sorted(response.data, key=lambda item: item.index)
        if [item.index for item in data] != list(range(len(texts))) or any(
            len(item.embedding) != dimensions for item in data
        ):
            raise LLMCallFailed("invalid embedding count, indices or dimensions")
        return [item.embedding for item in data]
