"""HTTP envelopes; domain artifacts remain the shared contracts."""

from typing import Literal

from pydantic import JsonValue

from tesseract.core.contracts import (
    Citation,
    EntityLink,
    ModuleRun,
    ModuleSnapshot,
    Observation,
    Report,
    RunSpec,
    Segment,
    SourceDocument,
)
from tesseract.core.contracts.common import Contract, Instant, Mode, Text


class CreateRun(Contract):
    scenario_id: Text
    as_of: Instant
    stores: tuple[Text, ...]
    source_manifest_hash: Text
    config_hash: Text
    code_version: Text
    schema_version: Literal["1.0"] = "1.0"
    mode: Mode
    modules: tuple[ModuleSnapshot, ...]
    prompt_versions: dict[str, str]
    model_versions: dict[str, str]
    authorized_fixture_refs: tuple[Text, ...]


class RunView(Contract):
    spec: RunSpec
    status: Literal["pending", "running", "succeeded", "degraded", "blocked", "failed"]
    published: bool
    namespace: Literal["product", "fixture"]
    module_runs: tuple[ModuleRun, ...] = ()


class DocumentDetail(Contract):
    document: SourceDocument
    segments: tuple[Segment, ...]
    observations: tuple[Observation, ...]
    links: tuple[EntityLink, ...]


class Health(Contract):
    status: Literal["ok"]
    version: str
    llm_mode: str
    fastweb_models_configured: list[str]
    sources_present: bool


class ResolvedReportCitation(Contract):
    citation: Citation
    artifact: dict[str, JsonValue]


class ReportDetail(Contract):
    report: Report
    citations: tuple[ResolvedReportCitation, ...]


class CatalogVariant(Contract):
    sku: str
    color: str
    color_code: str


class CatalogReference(Contract):
    id: str
    name: str
    url: str
    image_url: str | None
    association: str


class CatalogProduct(Contract):
    """Synthetic style with an illustrative official visual reference, for display only."""

    style_code: str
    name: str
    category: str
    subcategory: str
    variants: tuple[CatalogVariant, ...]
    reference: CatalogReference
