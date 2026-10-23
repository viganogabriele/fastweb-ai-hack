import json
import subprocess
import sys

import pytest
from fastapi import FastAPI
from jsonschema import Draft202012Validator
from jsonschema import ValidationError as SchemaValidationError
from pydantic import ValidationError

from tesseract.core import contracts
from tesseract.core.contracts import ModuleManifest, ModuleSnapshot, RunSpec, SourceDocument
from tesseract.core.contracts.common import Contract
from tesseract.core.contracts.schema import export_schema


def test_schema_covers_all_public_dtos_and_has_resolvable_refs():
    schema = export_schema()
    Draft202012Validator.check_schema(schema)
    for name in contracts.__all__:
        model = getattr(contracts, name)
        if isinstance(model, type) and issubclass(model, Contract):
            assert name in schema["$defs"]

    def walk(value):
        if isinstance(value, dict):
            if "$ref" in value:
                assert value["$ref"].startswith("#/$defs/")
                assert value["$ref"].removeprefix("#/$defs/") in schema["$defs"]
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(schema)


def test_export_cli_is_deterministic_and_writes_a_portable_schema(tmp_path, document):
    target = tmp_path / "nested" / "contracts.json"
    subprocess.run(
        [sys.executable, "-m", "tesseract.core.contracts", "--output", str(target)],
        check=True,
    )
    schema = json.loads(target.read_text())
    assert schema == export_schema()
    document_schema = {**schema, "$ref": "#/$defs/SourceDocument"}
    Draft202012Validator(document_schema).validate(document.model_dump(mode="json"))
    with pytest.raises(SchemaValidationError) as error:
        Draft202012Validator(document_schema).validate({"text": "incomplete"})
    assert error.value.validator == "required"


def test_all_public_dtos_are_compatible_with_fastapi_openapi():
    app = FastAPI()
    for name in contracts.__all__:
        model = getattr(contracts, name)
        if isinstance(model, type) and issubclass(model, Contract):
            app.add_api_route(f"/{name}", lambda: None, response_model=model)
    schema = app.openapi()
    assert schema["openapi"].startswith("3.1")
    assert "SourceDocument" in schema["components"]["schemas"]
    assert "RunSpec" in schema["components"]["schemas"]


def test_run_snapshot_roundtrips_with_explicit_versions_and_modes():
    manifest = ModuleManifest(
        id="src.email",
        version="v1",
        layer="sources",
        description="Canonical email documents",
        requires=[],
        optional_inputs=[],
        produces=["SourceDocument"],
        enabled=True,
        mode="fixture",
        boundary="simulated",
        params_schema={"type": "object"},
    )
    run = RunSpec(
        run_id="run-1",
        scenario_id="fixture-session-1",
        as_of="2026-10-22T17:00:00Z",
        stores=["MIL01"],
        source_manifest_hash="sources-v1",
        config_hash="config-v1",
        code_version="commit-1",
        mode="fixture",
        modules=[ModuleSnapshot(manifest=manifest, params={})],
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=["fixture-1"],
    )
    assert RunSpec.model_validate_json(run.model_dump_json()) == run
    with pytest.raises(ValidationError):
        RunSpec(**{**run.model_dump(), "stores": ["MIL01", "MIL01"]})
    with pytest.raises(ValidationError):
        RunSpec(**{**run.model_dump(), "as_of": "2026-10-22T17:00:00"})


def test_schema_expresses_nullable_measurement_and_distinct_units():
    quantity = export_schema()["$defs"]["Quantity"]
    assert "null" in {branch["type"] for branch in quantity["properties"]["value"]["anyOf"]}
    units = quantity["properties"]["unit"]["anyOf"][0]["enum"]
    assert {"customers", "requests", "units", "money", "percent"} <= set(units)


def test_source_doc_can_be_validated_from_exported_json(document):
    assert SourceDocument.model_validate_json(document.model_dump_json()) == document
