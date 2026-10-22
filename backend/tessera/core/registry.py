"""Discover module entry points without a central list or table-name inference."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from importlib import import_module
from pkgutil import walk_packages
from typing import TYPE_CHECKING

from jsonschema import Draft202012Validator

from tessera.core.contracts import ModuleManifest, ModuleResult, ModuleSnapshot

if TYPE_CHECKING:
    from tessera.core.orchestrator import RunContext


@dataclass(frozen=True)
class RegisteredModule:
    manifest: ModuleManifest
    run: Callable[["RunContext"], ModuleResult]


class Registry:
    def __init__(self, entries: Iterable[RegisteredModule] = ()) -> None:
        self._entries: dict[str, RegisteredModule] = {}
        for entry in entries:
            if entry.manifest.id in self._entries:
                raise ValueError(f"duplicate module id: {entry.manifest.id}")
            if not callable(entry.run):
                raise TypeError(f"module {entry.manifest.id} has no callable run")
            Draft202012Validator.check_schema(entry.manifest.params_schema)
            self._entries[entry.manifest.id] = entry

    @classmethod
    def discover(cls, package: str = "tessera.modules") -> "Registry":
        root = import_module(package)
        entries = []
        for info in sorted(walk_packages(root.__path__, root.__name__ + "."), key=lambda x: x.name):
            module = import_module(info.name)
            if not hasattr(module, "MANIFEST"):
                continue
            manifest = module.MANIFEST
            if not isinstance(manifest, ModuleManifest):
                raise TypeError(f"{info.name}.MANIFEST must be a ModuleManifest")
            entries.append(RegisteredModule(manifest, getattr(module, "run", None)))
        return cls(entries)

    def manifests(self) -> tuple[ModuleManifest, ...]:
        return tuple(self._entries[key].manifest for key in sorted(self._entries))

    def resolve(self, snapshot: ModuleSnapshot) -> RegisteredModule:
        try:
            entry = self._entries[snapshot.manifest.id]
        except KeyError:
            raise ValueError(f"module not installed: {snapshot.manifest.id}") from None
        # Enabled is a per-run switch; implementation identity and dependency
        # declarations must still match the installed code exactly.
        if entry.manifest.model_dump(exclude={"enabled"}) != snapshot.manifest.model_dump(
            exclude={"enabled"}
        ):
            raise ValueError(f"module manifest changed: {snapshot.manifest.id}")
        Draft202012Validator(snapshot.manifest.params_schema).validate(snapshot.params)
        return entry
