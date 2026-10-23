"""Shared boundary types. All instants are aware and serialized in UTC."""

from datetime import UTC, datetime
from typing import Annotated, Literal, Self

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    FiniteFloat,
    model_validator,
)

SCHEMA_VERSION = "1.0"

Text = Annotated[str, Field(min_length=1)]
Instant = Annotated[AwareDatetime, AfterValidator(lambda value: value.astimezone(UTC))]
NonNegative = Annotated[FiniteFloat, Field(ge=0)]
Count = Annotated[int, Field(strict=True, ge=0)]
PositiveInt = Annotated[int, Field(strict=True, gt=0)]
Mode = Literal["live", "recorded", "fixture", "unavailable"]
Unit = Literal["units", "customers", "requests", "visitors", "money", "percent"]
EntityLevel = Literal["sku_size", "sku", "style", "category"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class ArtifactRef(Contract):
    kind: Text
    id: Text
    version: Text


class SourceRef(Contract):
    uri: Text
    content_hash: Text
    locator: str | None = None


class SourceRecord(Contract):
    id: Text
    version: Text
    available_at: Instant | None
    availability_basis: Text
    source_refs: tuple[SourceRef, ...]


class DerivedRecord(SourceRecord):
    run_id: Text
    scenario_id: Text
    computed_at: Instant
    input_refs: tuple[ArtifactRef, ...]
    producer: Text
    producer_version: Text


class StockFact(SourceRecord):
    location_id: Text
    sku: Text
    size: Text
    ean: str | None = None
    snapshot_at: Instant
    qty: NonNegative | None
    basis: Literal["on_hand", "sellable", "atp"]
    reservations_included: bool | None
    quality_holds_included: bool | None
    source_ref: SourceRef

    @model_validator(mode="after")
    def consistent_source(self) -> Self:
        if self.source_refs != (self.source_ref,):
            raise ValueError("stock source_refs must contain exactly its source_ref")
        return self


def ordered(start: datetime | float | None, end: datetime | float | None) -> None:
    if start is not None and end is not None and end < start:
        raise ValueError("end must be greater than or equal to start")


def require_pair(start: object | None, end: object | None) -> None:
    if (start is None) != (end is None):
        raise ValueError("both interval endpoints must be provided together")


def require_reason(status: str, reason: str | None, statuses: tuple[str, ...]) -> None:
    if status in statuses and (reason is None or not reason.strip()):
        raise ValueError(f"{status} requires a reason")
