"""Versioned MVP DTOs; public imports for producers, consumers and fixture validation."""

from .agents import AgentStep, AgentTrace, Clarification, Decision
from .cases import Case
from .common import SCHEMA_VERSION, ArtifactRef, SourceRef, StockFact
from .documents import Segment, SourceDocument
from .forecast import AdjustmentComponent, ForecastAdjustment, ForecastPoint, ScenarioValues
from .insights import ProductInsight, Share
from .links import EntityLink, EvidenceRelation, LinkCandidate
from .observations import ContextEvent, Evidence, MetricFact, Observation, Quantity
from .options import ActionOption, Check, Leg, Reservation, ScenarioOutcome
from .reports import Citation, Report
from .runs import ModuleManifest, ModuleResult, ModuleRun, ModuleSnapshot, RunSpec

__all__ = [
    "SCHEMA_VERSION",
    "ActionOption",
    "AdjustmentComponent",
    "AgentStep",
    "AgentTrace",
    "ArtifactRef",
    "Case",
    "Check",
    "Citation",
    "Clarification",
    "ContextEvent",
    "Decision",
    "EntityLink",
    "Evidence",
    "EvidenceRelation",
    "ForecastAdjustment",
    "ForecastPoint",
    "Leg",
    "LinkCandidate",
    "MetricFact",
    "ModuleManifest",
    "ModuleResult",
    "ModuleRun",
    "ModuleSnapshot",
    "Observation",
    "ProductInsight",
    "Quantity",
    "Report",
    "Reservation",
    "RunSpec",
    "ScenarioOutcome",
    "ScenarioValues",
    "Segment",
    "SourceDocument",
    "Share",
    "SourceRef",
    "StockFact",
]
