from typing import Literal, Self

from pydantic import model_validator

from .common import ArtifactRef, Count, DerivedRecord, Instant, Text, ordered


class Case(DerivedRecord):
    case_type: Text
    store_id: str | None = None
    scope_level: Literal["sku_size", "sku", "style", "category", "store", "unknown"]
    scope_id: str | None = None
    window_start: Instant
    window_end: Instant
    status: Literal["open", "verify", "monitor", "action_proposed", "decided", "closed"]
    owner: Text
    priority: Literal["low", "medium", "high", "critical"]
    priority_reason: Text
    decision_due_at: Instant | None = None
    first_available_at: Instant
    last_received_at: Instant
    last_independent_evidence_at: Instant | None = None
    valid_until: Instant | None = None
    supporting: tuple[ArtifactRef, ...]
    contradicting: tuple[ArtifactRef, ...]
    n_documents: Count
    n_origin_groups: Count
    n_unknown_origins: Count
    blocking_uncertainties: tuple[Text, ...]
    context_refs: tuple[ArtifactRef, ...]

    @model_validator(mode="after")
    def scope_and_counts(self) -> Self:
        ordered(self.window_start, self.window_end)
        ordered(self.first_available_at, self.last_received_at)
        if self.scope_level == "unknown":
            if self.scope_id is not None:
                raise ValueError("unknown scope must not assert a scope id")
        elif not self.scope_id:
            raise ValueError("resolved scope requires scope_id")
        if self.n_origin_groups + self.n_unknown_origins > self.n_documents:
            raise ValueError("origin counts cannot exceed document count")
        return self
