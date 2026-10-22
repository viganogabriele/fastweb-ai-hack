"""Export one portable JSON Schema document with all public MVP DTOs in $defs."""

from pydantic.json_schema import models_json_schema

from . import __all__ as public_names
from . import (
    agents,
    cases,
    common,
    documents,
    forecast,
    links,
    observations,
    options,
    reports,
    runs,
)
from .common import SCHEMA_VERSION, Contract


def export_schema() -> dict:
    models = {
        model
        for area in (
            agents,
            cases,
            common,
            documents,
            forecast,
            links,
            observations,
            options,
            reports,
            runs,
        )
        for name in public_names
        if isinstance(model := getattr(area, name, None), type) and issubclass(model, Contract)
    }
    _, schema = models_json_schema(
        [(model, "validation") for model in sorted(models, key=lambda model: model.__name__)],
        title=f"Tessera MVP contracts {SCHEMA_VERSION}",
    )
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = f"urn:tessera:contracts:{SCHEMA_VERSION}"
    return schema
