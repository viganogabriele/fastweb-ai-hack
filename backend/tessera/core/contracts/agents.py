from typing import Literal, Self

from pydantic import JsonValue, model_validator

from .common import (
    ArtifactRef,
    Contract,
    Count,
    DerivedRecord,
    Instant,
    Mode,
    NonNegative,
    Text,
    ordered,
    require_pair,
)


class AgentStep(Contract):
    tool: Text
    arguments: dict[str, JsonValue]
    input_refs: tuple[ArtifactRef, ...]
    output_refs: tuple[ArtifactRef, ...]
    duration_ms: NonNegative
    error: str | None = None


class AgentTrace(DerivedRecord):
    case_id: Text
    steps: tuple[AgentStep, ...]
    outcome: Text
    fallback_used: bool
    mode: Mode
    tokens_in: Count | None = None
    tokens_out: Count | None = None


class Decision(DerivedRecord):
    option_id: Text
    input_version_hash: Text
    decision: Literal["approved", "rejected"]
    by: Text
    at: Instant
    idempotency_key: Text
    note: str | None = None
    dispatch_status: Literal["draft", "pending", "accepted", "rejected", "unknown"]
    request_ref: ArtifactRef | None = None
    response_ref: ArtifactRef | None = None


class Clarification(DerivedRecord):
    case_id: Text
    observation_refs: tuple[ArtifactRef, ...]
    question: Text
    asked_at: Instant
    answer_document_id: str | None = None
    answered_at: Instant | None = None
    status: Literal["draft", "asked", "answered", "cancelled"]
    simulated: Literal[True] = True

    @model_validator(mode="after")
    def answer(self) -> Self:
        require_pair(self.answer_document_id, self.answered_at)
        ordered(self.asked_at, self.answered_at)
        if self.answered_at is not None and self.answered_at <= self.asked_at:
            raise ValueError("answer must become available strictly after the question")
        if (self.status == "answered") != (self.answered_at is not None):
            raise ValueError("answered status requires an answer document and timestamp")
        return self
