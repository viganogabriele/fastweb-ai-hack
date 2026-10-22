import re
from typing import Literal, Self

from pydantic import FiniteFloat, model_validator

from .common import (
    ArtifactRef,
    Contract,
    Count,
    DerivedRecord,
    Instant,
    NonNegative,
    Text,
    Unit,
    ordered,
    require_pair,
)
from .documents import Segment, SourceDocument


class Evidence(Contract):
    document_id: Text
    document_version: Text
    segment_id: Text
    quote: Text
    char_start: Count
    char_end: Count
    t_start_s: NonNegative | None = None
    t_end_s: NonNegative | None = None

    @model_validator(mode="after")
    def intervals(self) -> Self:
        if self.char_end - self.char_start != len(self.quote):
            raise ValueError("quote offsets must span the quote in Unicode code points")
        require_pair(self.t_start_s, self.t_end_s)
        ordered(self.t_start_s, self.t_end_s)
        return self

    def validate_against(self, document: SourceDocument, segment: Segment) -> None:
        segment.validate_against(document)
        if self.document_id != document.id or self.document_version != document.version:
            raise ValueError("evidence must refer to this document version")
        if self.segment_id != segment.id:
            raise ValueError("evidence must belong to the indicated segment")
        if not segment.char_start <= self.char_start < self.char_end <= segment.char_end:
            raise ValueError("evidence must lie within the segment")
        if document.text[self.char_start : self.char_end] != self.quote:
            raise ValueError("quote must match the canonical document slice exactly")
        if self.t_start_s is not None:
            if segment.t_start_s is None or segment.t_end_s is None:
                raise ValueError("audio evidence needs an actual timed segment")
            if not segment.t_start_s <= self.t_start_s <= self.t_end_s <= segment.t_end_s:
                raise ValueError("audio evidence must lie within the segment interval")


class Quantity(Contract):
    kind: Literal["exact", "range", "vague", "unknown"]
    value: FiniteFloat | None = None
    low: FiniteFloat | None = None
    high: FiniteFloat | None = None
    unit: Unit | None = None
    currency: str | None = None
    raw: str | None = None
    evidence_ref: ArtifactRef | None = None

    @model_validator(mode="after")
    def shape_and_units(self) -> Self:
        if self.kind == "exact":
            if self.value is None or self.low is not None or self.high is not None:
                raise ValueError("exact requires only value")
        elif self.kind == "range":
            if self.low is None or self.high is None or self.value is not None:
                raise ValueError("range requires only low and high")
            ordered(self.low, self.high)
        elif any(value is not None for value in (self.value, self.low, self.high)):
            raise ValueError("vague/unknown must not contain imputed numeric values")
        if self.kind in ("exact", "range") and self.unit is None:
            raise ValueError("numeric quantities require a unit")
        if self.currency is not None and (
            self.unit != "money" or re.fullmatch(r"[A-Z]{3}", self.currency) is None
        ):
            raise ValueError("currency requires money and a three-letter uppercase code")
        if self.unit == "money" and self.kind in ("exact", "range") and self.currency is None:
            raise ValueError("numeric money requires currency")
        if self.unit in ("units", "customers", "requests", "visitors"):
            if any(value is not None and value < 0 for value in (self.value, self.low, self.high)):
                raise ValueError("physical counts cannot be negative")
        return self


class Observation(DerivedRecord):
    document_id: Text
    kind: Literal[
        "unmet_demand",
        "demand_up",
        "demand_down",
        "stockout",
        "low_stock",
        "stock_discrepancy",
        "product_feedback",
        "traffic_change",
        "customer_profile",
        "operational_issue",
        "sales_figure",
        "local_event",
        "other",
    ]
    store_id: str | None = None
    period_start: Instant | None = None
    period_end: Instant | None = None
    time_text: str | None = None
    product_mention: str | None = None
    quantity: Quantity
    direction: Text
    reason: str | None = None
    reason_text: str | None = None
    funnel_stage: str | None = None
    attribution: Text
    negated: bool
    evidence: tuple[Evidence, ...]
    extractor_version: Text

    @model_validator(mode="after")
    def period_and_evidence(self) -> Self:
        ordered(self.period_start, self.period_end)
        if not self.evidence or any(e.document_id != self.document_id for e in self.evidence):
            raise ValueError("observation needs evidence from its document")
        return self


class MetricFact(DerivedRecord):
    document_id: Text
    metric: Text
    definition: str | None = None
    value: FiniteFloat | None
    unit: Unit
    currency: str | None = None
    vat_included: bool | None = None
    gross_or_net: Literal["gross", "net"] | None = None
    scope: dict[str, str]
    period_start: Instant
    period_end: Instant
    calendar: str | None = None
    fx_basis: str | None = None
    locator: Text
    mapping_version: Text
    comparability_status: Literal["comparable", "not_comparable", "unknown"]

    @model_validator(mode="after")
    def comparability(self) -> Self:
        ordered(self.period_start, self.period_end)
        if self.comparability_status == "comparable" and not self.definition:
            raise ValueError("comparable metrics require a definition")
        Quantity(
            kind="unknown" if self.value is None else "exact",
            value=self.value,
            unit=self.unit,
            currency=self.currency,
        )
        return self


class ContextEvent(DerivedRecord):
    kind: Text
    store_ids: tuple[Text, ...]
    start: Instant
    end: Instant
    issued_at: Instant | None = None
    magnitude: Quantity | None = None
    description: Text
    role: Literal["context_only", "corroborating"]

    @model_validator(mode="after")
    def interval(self) -> Self:
        ordered(self.start, self.end)
        return self
