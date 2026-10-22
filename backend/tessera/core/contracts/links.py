from typing import Literal, Self

from pydantic import FiniteFloat, model_validator

from .common import ArtifactRef, Contract, DerivedRecord, EntityLevel, Text


class LinkCandidate(Contract):
    target_id: Text
    level: EntityLevel
    method: Text
    score: FiniteFloat
    score_min: FiniteFloat
    score_max: FiniteFloat

    @model_validator(mode="after")
    def declared_scale(self) -> Self:
        if (
            not self.score_min < self.score_max
            or not self.score_min <= self.score <= self.score_max
        ):
            raise ValueError(
                "candidate score must lie in its declared scale; it is not a probability"
            )
        return self


class EntityLink(DerivedRecord):
    observation_id: Text
    status: Literal["linked", "ambiguous", "unlinked", "not_product"]
    level: EntityLevel | None
    target_id: str | None = None
    candidates: tuple[LinkCandidate, ...]
    decided_by: Text
    rationale: Text

    @model_validator(mode="after")
    def resolution(self) -> Self:
        if self.status == "linked":
            if self.level is None or not self.target_id:
                raise ValueError("linked requires a target and level")
        elif self.target_id is not None or self.level is not None:
            raise ValueError("unresolved/non-product links must not assert a target or level")
        if self.status == "ambiguous" and not self.candidates:
            raise ValueError("ambiguous links must retain candidates")
        return self


class EvidenceRelation(DerivedRecord):
    from_ref: ArtifactRef
    to_ref: ArtifactRef
    relation: Literal[
        "duplicates",
        "possibly_same_episode",
        "supersedes",
        "retracts",
        "supports",
        "contradicts",
    ]
    basis: Text
    evidence_refs: tuple[ArtifactRef, ...]

    @model_validator(mode="after")
    def fact_correction(self) -> Self:
        if self.from_ref == self.to_ref:
            raise ValueError("relations must connect distinct facts/versions")
        if self.relation in ("supersedes", "retracts") and self.to_ref.kind == "SourceDocument":
            raise ValueError("corrections must target a fact, not an entire document")
        return self
