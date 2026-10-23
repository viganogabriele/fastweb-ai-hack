from .common import ArtifactRef, Contract, DerivedRecord, Instant, Text, Unit


class Citation(Contract):
    ref: ArtifactRef
    field: str | None = None
    unit: Unit | None = None
    scope: dict[str, str] | None = None
    period_start: Instant | None = None
    period_end: Instant | None = None


class Report(DerivedRecord):
    as_of: Instant
    view: Text
    markdown: str
    citations: tuple[Citation, ...]
    generated_by: Text
    input_version_hash: Text
