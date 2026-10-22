from typing import Literal, Self

from pydantic import JsonValue, model_validator

from .common import SCHEMA_VERSION, Contract, Count, Instant, Mode, Text, ordered


class ModuleManifest(Contract):
    id: Text
    version: Text
    layer: Literal[
        "sources", "ingestion", "integration", "intelligence", "actions", "agents", "outputs"
    ]
    description: Text
    requires: tuple[Text, ...]
    optional_inputs: tuple[Text, ...]
    produces: tuple[Text, ...]
    enabled: bool
    mode: Mode
    boundary: Literal["simulated"] | None = None
    params_schema: dict[str, JsonValue]


class ModuleSnapshot(Contract):
    manifest: ModuleManifest
    params: dict[str, JsonValue]


class RunSpec(Contract):
    run_id: Text
    scenario_id: Text
    as_of: Instant
    stores: tuple[Text, ...]
    source_manifest_hash: Text
    config_hash: Text
    code_version: Text
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    mode: Mode
    modules: tuple[ModuleSnapshot, ...]
    prompt_versions: dict[str, str]
    model_versions: dict[str, str]
    authorized_fixture_refs: tuple[Text, ...]

    @model_validator(mode="after")
    def scope(self) -> Self:
        if not self.stores or len(set(self.stores)) != len(self.stores):
            raise ValueError("run requires a nonempty set of unique stores")
        ids = [module.manifest.id for module in self.modules]
        if len(set(ids)) != len(ids):
            raise ValueError("module snapshot ids must be unique")
        return self


class ModuleResult(Contract):
    module_id: Text
    module_version: Text
    status: Literal["succeeded", "degraded", "blocked", "failed"]
    counts: dict[str, Count]
    errors: tuple[Text, ...]
    abstentions: tuple[Text, ...]


class ModuleRun(Contract):
    run_id: Text
    module_id: Text
    mode: Mode
    status: Literal["pending", "running", "succeeded", "degraded", "blocked", "failed"]
    started_at: Instant | None = None
    finished_at: Instant | None = None
    result: ModuleResult | None = None

    @model_validator(mode="after")
    def result_status(self) -> Self:
        ordered(self.started_at, self.finished_at)
        if self.result is not None and (
            self.result.module_id != self.module_id or self.result.status != self.status
        ):
            raise ValueError("module result must match this module and status")
        return self
