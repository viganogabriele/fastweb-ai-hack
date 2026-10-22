"""Export one portable JSON Schema document with all public MVP DTOs in $defs."""

from pydantic.json_schema import models_json_schema

from tessera.core import contracts

from .common import SCHEMA_VERSION, Contract


def export_schema() -> dict:
    models = [
        model
        for name in contracts.__all__
        if isinstance(model := getattr(contracts, name), type) and issubclass(model, Contract)
    ]
    _, schema = models_json_schema(
        [(model, "validation") for model in sorted(models, key=lambda model: model.__name__)],
        title=f"Tessera MVP contracts {SCHEMA_VERSION}",
    )
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = f"urn:tessera:contracts:{SCHEMA_VERSION}"
    return schema
