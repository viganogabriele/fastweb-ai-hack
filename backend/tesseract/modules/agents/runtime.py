"""Bounded agent loop over Chat Completions-shaped models (RFC §4.8.1, AG-01 pure).

One run is a sequence of turns. Each turn calls the model once; every tool call it returns is
checked against the allowlist, its arguments are validated with the tool's Pydantic model, and
exactly one result is sent back per `tool_call_id`. The run ends when the model calls `finish`
with a choice that passes validation, or when a limit is hit.

Budget (defaults from the RFC) is total and includes retries: 6 tool calls, 8 turns, 90 seconds.
Every attempted tool call counts, rejected ones included, and so does `finish`. Every model call is
a turn, including a reply without tool calls or a failed request. Each request gets
`min(request_timeout_s, remaining)`. Once a limit is reached nothing else is called: pending tool
calls are recorded as not executed and the deterministic fallback decides.

Tool results and document text are untrusted data. They go back as `tool` messages wrapped in
`{"ok", "data"|"error"}` and never change the allowlist, the budget or the finish policy. The model
cannot approve or book anything: `finish` only selects an option (`action_proposed`) or ends in
`verify` / `monitor`, and it may cite only artifact ids visible in this run.

The fallback is a deterministic callable supplied by the agent (the investigator chains evidence →
ambiguity → availability → lane → options). Its choice passes the same validation; if it does not,
the run ends in `verify`. Either way the trace records `fallback_used=True`.

Pure code: no DB, no network. The real LLM adapter (AG-01 runtime) implements `ChatModel`:
`tesseract.modules.agents.chat_model.LLMChatModel` sends each turn through PLT-05's client and
replays the recorded provider replies from the run cache.
"""

import json
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationError, model_validator
from pydantic_core import PydanticSerializationError, to_jsonable_python

from tesseract.core.contracts import AgentStep, AgentTrace, ArtifactRef
from tesseract.core.contracts.common import Mode

PRODUCER = "modules.agents.runtime"
PRODUCER_VERSION = "1"
FINISH = "finish"
FALLBACK_STEP = "fallback"

StopReason = Literal["finished", "budget_tool_calls", "budget_turns", "budget_time", "model_error"]
Message = dict[str, Any]

NUDGE = (
    "Reply with tool calls only. Use the listed tools, then call `finish` exactly once "
    "with your choice."
)


# --- Model interface -------------------------------------------------------------------------


@dataclass(frozen=True)
class ToolCall:
    """One tool call as the model returned it. `arguments` is the raw JSON string."""

    id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class ModelReply:
    content: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()
    tokens_in: int | None = None
    tokens_out: int | None = None


class ModelError(Exception):
    """A failed model request. Non-retryable errors (401/403, budget_exceeded) end the run."""

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


class ChatModel(Protocol):
    def complete(
        self, messages: Sequence[Message], tools: Sequence[Message], timeout_s: float
    ) -> ModelReply: ...


# --- Tools -----------------------------------------------------------------------------------


class ToolError(Exception):
    """Expected tool failure (unknown id in the snapshot, service down), shown to the model."""


@dataclass(frozen=True)
class ToolResult:
    data: JsonValue
    input_refs: tuple[ArtifactRef, ...] = ()
    output_refs: tuple[ArtifactRef, ...] = ()


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    args: type[BaseModel]
    handler: Callable[[Any], ToolResult]

    def spec(self) -> Message:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args.model_json_schema(),
            },
        }


class Finish(BaseModel):
    """Arguments of the terminal `finish` tool. Selecting an option is not an approval."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["action_proposed", "verify", "monitor"]
    option_id: str | None = None
    evidence_refs: tuple[str, ...] = ()
    rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def option_iff_proposed(self) -> Self:
        if (self.status == "action_proposed") != (self.option_id is not None):
            raise ValueError("option_id is required for action_proposed and forbidden otherwise")
        return self


FINISH_DESCRIPTION = (
    "End the investigation. status=action_proposed requires an option_id evaluated in this run; "
    "otherwise use verify or monitor. evidence_refs are artifact ids returned by tools."
)

# Returns an error message, or None if the choice is acceptable.
FinishValidator = Callable[[Finish], str | None]


@dataclass(frozen=True)
class FallbackContext:
    reason: StopReason
    steps: tuple[AgentStep, ...]
    visible_ids: frozenset[str]


Fallback = Callable[[FallbackContext], Finish]


def verify_fallback(ctx: FallbackContext) -> Finish:
    """Default fallback: never guess, send the case to verification."""
    return Finish(status="verify", rationale=f"deterministic fallback after {ctx.reason}")


# --- Run configuration and result ------------------------------------------------------------


@dataclass(frozen=True)
class Budget:
    max_tool_calls: int = 6
    max_turns: int = 8
    max_seconds: float = 90.0
    request_timeout_s: float = 60.0


@dataclass(frozen=True)
class TraceMeta:
    """Identity of the run the trace belongs to. `as_of` is the replay clock of the run."""

    run_id: str
    scenario_id: str
    case_id: str
    as_of: datetime
    mode: Mode
    input_refs: tuple[ArtifactRef, ...] = ()
    trace_id: str | None = None
    producer: str = PRODUCER
    producer_version: str = PRODUCER_VERSION


@dataclass(frozen=True)
class AgentRun:
    trace: AgentTrace
    finish: Finish
    stop_reason: StopReason
    turns: int
    tool_calls: int


@dataclass
class _State:
    steps: list[AgentStep] = field(default_factory=list)
    visible: set[str] = field(default_factory=set)
    turns: int = 0
    tool_calls: int = 0
    tokens_in: int | None = None
    tokens_out: int | None = None


# --- Loop ------------------------------------------------------------------------------------


class AgentLoop:
    def __init__(
        self,
        model: ChatModel,
        tools: Iterable[Tool],
        *,
        budget: Budget | None = None,
        validate_finish: FinishValidator | None = None,
        fallback: Fallback = verify_fallback,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.model = model
        self.tools: dict[str, Tool] = {}
        for tool in tools:
            if tool.name == FINISH or tool.name in self.tools:
                raise ValueError(f"duplicate or reserved tool name: {tool.name}")
            self.tools[tool.name] = tool
        self.budget = budget or Budget()
        self.validate_finish = validate_finish
        self.fallback = fallback
        self.clock = clock
        finish_tool = Tool(FINISH, FINISH_DESCRIPTION, Finish, lambda args: ToolResult(None))
        # Fixed once per loop: nothing the model or a tool returns can extend it.
        self.specs: tuple[Message, ...] = tuple(
            t.spec() for t in (*self.tools.values(), finish_tool)
        )

    def run(self, messages: Sequence[Message], meta: TraceMeta) -> AgentRun:
        state = _State(visible={ref.id for ref in meta.input_refs})
        history: list[Message] = [dict(m) for m in messages]
        start = self.clock()

        def remaining() -> float:
            return self.budget.max_seconds - (self.clock() - start)

        while True:
            if state.turns >= self.budget.max_turns:
                return self._fall_back("budget_turns", state, meta)
            if state.tool_calls >= self.budget.max_tool_calls:
                return self._fall_back("budget_tool_calls", state, meta)
            left = remaining()
            if left <= 0:
                return self._fall_back("budget_time", state, meta)

            state.turns += 1
            try:
                reply = self.model.complete(
                    history, self.specs, min(self.budget.request_timeout_s, left)
                )
            except ModelError as exc:
                if not exc.retryable:
                    return self._fall_back("model_error", state, meta)
                continue
            _add_tokens(state, reply)

            calls = reply.tool_calls
            ids = [c.id for c in calls]
            if not calls or any(not i for i in ids) or len(set(ids)) != len(ids):
                history.append({"role": "assistant", "content": reply.content or ""})
                history.append({"role": "user", "content": NUDGE})
                continue

            history.append(_assistant_message(reply))
            finished: Finish | None = None
            stop: StopReason | None = None
            for call in calls:
                if finished is not None:
                    self._skip(call, state, "not executed: finish already accepted")
                    continue
                if stop is None and state.tool_calls >= self.budget.max_tool_calls:
                    stop = "budget_tool_calls"
                if stop is None and remaining() <= 0:
                    stop = "budget_time"
                if stop is not None:
                    self._skip(call, state, f"not executed: {stop}")
                    continue
                state.tool_calls += 1
                result, finished = self._execute(call, state)
                history.append({"role": "tool", "tool_call_id": call.id, "content": result})

            if finished is not None:
                return self._result(finished, "finished", False, state, meta)
            if stop is not None:
                return self._fall_back(stop, state, meta)

    # One tool call → (tool message content, accepted finish or None). Records one step.
    def _execute(self, call: ToolCall, state: _State) -> tuple[str, Finish | None]:
        began = self.clock()
        arguments, parse_error = _parse_arguments(call.arguments)
        tool = self.tools.get(call.name)
        accepted: Finish | None = None
        result = ToolResult(None)
        error: str | None = None

        if call.name != FINISH and tool is None:
            error = f"tool not allowed: {call.name}"
        elif parse_error is not None:
            error = parse_error
        else:
            args_model = Finish if tool is None else tool.args
            try:
                args = args_model.model_validate(arguments)
            except ValidationError as exc:
                error = f"invalid arguments: {_short_errors(exc)}"
            else:
                if tool is None:
                    error = self._check_finish(args, state.visible)
                    accepted = None if error else args
                else:
                    try:
                        result = tool.handler(args)
                    except ToolError as exc:
                        error = f"tool error: {exc}"
                    except Exception as exc:  # a broken tool must not crash the run
                        error = f"tool failed: {type(exc).__name__}: {exc}"

        payload: str | None = None
        if error is None and accepted is None and call.name != FINISH:
            try:  # Decimal, datetime, ... from a handler are rendered; anything else is an error
                payload = json.dumps(
                    {"ok": True, "data": to_jsonable_python(result.data)}, ensure_ascii=False
                )
            except (PydanticSerializationError, TypeError, ValueError) as exc:
                error = f"tool failed: result is not serializable: {exc}"

        state.steps.append(
            AgentStep(
                tool=call.name or "?",
                arguments=arguments,
                input_refs=result.input_refs,
                output_refs=result.output_refs,
                duration_ms=max(0.0, (self.clock() - began) * 1000),
                error=error,
            )
        )
        state.visible.update(ref.id for ref in result.output_refs)
        if error is not None:
            return json.dumps({"ok": False, "error": error}, ensure_ascii=False), None
        return payload or json.dumps({"ok": True, "data": None}), accepted

    def _check_finish(self, choice: Finish, visible: set[str]) -> str | None:
        unseen = [ref for ref in choice.evidence_refs if ref not in visible]
        if unseen:
            return f"evidence_refs not visible in this run: {', '.join(unseen)}"
        if self.validate_finish is not None:
            return self.validate_finish(choice)
        return None

    def _skip(self, call: ToolCall, state: _State, reason: str) -> None:
        arguments, _ = _parse_arguments(call.arguments)
        state.steps.append(
            AgentStep(
                tool=call.name or "?",
                arguments=arguments,
                input_refs=(),
                output_refs=(),
                duration_ms=0.0,
                error=reason,
            )
        )

    def _fall_back(self, reason: StopReason, state: _State, meta: TraceMeta) -> AgentRun:
        ctx = FallbackContext(
            reason=reason,
            steps=tuple(state.steps),
            visible_ids=frozenset(state.visible),
        )
        began = self.clock()
        error: str | None = None
        try:
            choice = self.fallback(ctx)
            error = self._check_finish(choice, state.visible)
        except Exception as exc:
            choice, error = None, f"fallback failed: {type(exc).__name__}: {exc}"
        if error is not None or choice is None:
            choice = Finish(status="verify", rationale=f"fallback choice rejected: {error}")
        state.steps.append(
            AgentStep(
                tool=FALLBACK_STEP,
                arguments={"reason": ctx.reason, **choice.model_dump(mode="json")},
                input_refs=(),
                output_refs=(),
                duration_ms=max(0.0, (self.clock() - began) * 1000),
                error=error,
            )
        )
        return self._result(choice, reason, True, state, meta)

    def _result(
        self, choice: Finish, reason: StopReason, fallback: bool, state: _State, meta: TraceMeta
    ) -> AgentRun:
        input_refs = _unique(
            [*meta.input_refs, *(ref for step in state.steps for ref in step.input_refs)]
        )
        trace = AgentTrace(
            id=meta.trace_id or f"trace:{meta.run_id}:{meta.case_id}",
            version=meta.producer_version,
            available_at=meta.as_of,
            availability_basis="run_as_of",
            source_refs=(),
            run_id=meta.run_id,
            scenario_id=meta.scenario_id,
            computed_at=meta.as_of,
            input_refs=input_refs,
            producer=meta.producer,
            producer_version=meta.producer_version,
            case_id=meta.case_id,
            steps=tuple(state.steps),
            outcome=choice.status,
            fallback_used=fallback,
            mode=meta.mode,
            tokens_in=state.tokens_in,
            tokens_out=state.tokens_out,
        )
        return AgentRun(trace, choice, reason, state.turns, state.tool_calls)


# --- Helpers ---------------------------------------------------------------------------------


def _parse_arguments(raw: str) -> tuple[dict[str, JsonValue], str | None]:
    try:
        parsed = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, AttributeError) as exc:
        return {"_raw": str(raw)}, f"arguments are not valid JSON: {exc}"
    if not isinstance(parsed, Mapping):
        return {"_raw": str(raw)}, "arguments must be a JSON object"
    return dict(parsed), None


def _short_errors(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(p) for p in err['loc']) or '<root>'}: {err['msg']}" for err in exc.errors()
    )


def _assistant_message(reply: ModelReply) -> Message:
    return {
        "role": "assistant",
        "content": reply.content,
        "tool_calls": [
            {"id": c.id, "type": "function", "function": {"name": c.name, "arguments": c.arguments}}
            for c in reply.tool_calls
        ],
    }


def _add_tokens(state: _State, reply: ModelReply) -> None:
    if reply.tokens_in is not None:
        state.tokens_in = (state.tokens_in or 0) + reply.tokens_in
    if reply.tokens_out is not None:
        state.tokens_out = (state.tokens_out or 0) + reply.tokens_out


def _unique(refs: Iterable[ArtifactRef]) -> tuple[ArtifactRef, ...]:
    return tuple(dict.fromkeys(refs))
