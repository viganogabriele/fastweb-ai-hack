"""Frozen bundle protocol, integrity checks and lazy answer-key access."""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

DEV = frozenset("MIL01 MIL02 PAR01 LON01 MUN01 MAD01 NYC01 TYO01 SEL01 SHA01 HKG01 SYD01".split())
HOLDOUT = frozenset("ROM01 PAR02 LON02 ZRH01 NYC02 TYO02 SEL02 BJS01 TPE01 DXB01".split())
ARTIFACTS = ("predictions", "cases", "options")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(data: Any) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def _timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("Temporal origins require an explicit time zone")
    return result


def validate_protocol(protocol: dict) -> None:
    """Validate the preselected sample; no oracle-derived defaults."""
    for field in ("run_id", "sampling_criterion", "models", "parameters"):
        if not protocol.get(field):
            raise ValueError(f"Missing protocol field: {field}")
    stores = protocol.get("stores", [])
    split = protocol.get("split")
    permitted = {"dev": DEV, "holdout": HOLDOUT}.get(split)
    if not permitted or not stores or not set(stores) <= permitted:
        raise ValueError("Stores must belong to the explicitly selected dev/holdout split")
    origins = protocol.get("origins", [])
    if not origins:
        raise ValueError("Preselect at least one temporal origin")
    for origin in origins:
        _timestamp(origin)
    universe = protocol.get("universe", [])
    if not universe or any(
        item.get("store_id") not in stores or not item.get("sku") for item in universe
    ):
        raise ValueError("Preselect the store/SKU universe, including no-alert cases")
    if set(stores) != {item["store_id"] for item in universe}:
        raise ValueError("Every selected store must be represented in the universe")


def freeze(
    destination: Path,
    protocol: dict,
    artifacts: dict[str, Path],
    sources: list[Path],
    configuration: list[Path],
    *,
    root: Path,
) -> str:
    """Copy exports/config and record source hashes, without touching the oracle.

    Return the manifest SHA-256, to be recorded outside the bundle before scoring.
    The producer must freeze these inputs before a holdout run; this function
    records their identity, it cannot prove when the producer chose them.
    """
    validate_protocol(protocol)
    if set(artifacts) != set(ARTIFACTS) or not sources or not configuration:
        raise ValueError("Provide predictions, cases, options, source and configuration manifests")
    root = root.resolve(strict=True)
    destination = destination.resolve()
    if not destination.is_relative_to(root / "data"):
        raise ValueError("Frozen bundles must be written under data/")
    source_root = (root / "generated/sources").resolve(strict=True)
    entries = []
    copies = {}
    for category, paths in [("sources", sources), ("configuration", configuration)]:
        for index, path in enumerate(paths):
            path = path.resolve(strict=True)
            if not path.is_relative_to(root):
                raise ValueError("Manifest inputs must be inside the repository")
            relative = path.relative_to(root)
            if category == "sources":
                if not path.is_relative_to(source_root):
                    raise ValueError("Source manifest may read only generated/sources")
            elif relative.parts[0] not in {"config", "backend"}:
                raise ValueError("Configuration must come from config/ or backend/ (prompts)")
            if "email_context" in relative.parts or path.name.endswith("_notes.md"):
                raise ValueError("Hidden answer material cannot be a manifest input")
            data = path.read_bytes()
            entry = {"category": category, "path": relative.as_posix(), "sha256": digest(data)}
            if category == "configuration":
                name = f"configuration/{index}-{path.name}"
                copies[name] = data
                entry["snapshot"] = name
            entries.append(entry)
    for kind in ARTIFACTS:
        artifact = artifacts[kind].resolve(strict=True)
        if not artifact.is_relative_to(root / "data"):
            raise ValueError("Product exports must come from data/")
        data = artifact.read_bytes()
        records = json.loads(data)
        if not isinstance(records, list) or any(not isinstance(row, dict) for row in records):
            raise ValueError(f"{kind} must be a JSON array of artifact objects")
        name = f"{kind}.json"
        copies[name] = data
        entries.append({"category": kind, "path": name, "sha256": digest(data)})
    manifest = _json({"version": 1, "protocol": protocol, "files": entries})
    destination.mkdir(parents=True, exist_ok=False)
    try:
        for name, data in copies.items():
            path = destination / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(data)
        (destination / "manifest.json").write_bytes(manifest)
    except BaseException:
        shutil.rmtree(destination)
        raise
    return digest(manifest)


class FrozenRun:
    """Verified snapshot; oracle files are opened only after full verification."""

    def __init__(self, bundle: Path, expected_sha256: str):
        self.bundle = bundle.resolve(strict=True)
        manifest_bytes = (self.bundle / "manifest.json").read_bytes()
        if digest(manifest_bytes) != expected_sha256:
            raise ValueError("Frozen manifest hash mismatch")
        self.manifest_sha256 = expected_sha256
        self.manifest = json.loads(manifest_bytes)
        if self.manifest["version"] != 1:
            raise ValueError("Unsupported frozen export version")
        validate_protocol(self.manifest["protocol"])
        self.artifacts = {}
        for entry in self.manifest["files"]:
            category = entry["category"]
            if category == "sources":
                continue  # Provenance only: scoring never rereads mutable product inputs.
            name = entry.get("snapshot", entry["path"])
            path = (self.bundle / name).resolve(strict=True)
            if not path.is_relative_to(self.bundle):
                raise ValueError("Snapshot path escapes frozen bundle")
            data = path.read_bytes()
            if digest(data) != entry["sha256"]:
                raise ValueError(f"Frozen file hash mismatch: {name}")
            if category in ARTIFACTS:
                self.artifacts[category] = json.loads(data)
        if set(self.artifacts) != set(ARTIFACTS):
            raise ValueError("Incomplete frozen artifacts")

    def read_answer_key(self, oracle_root: Path, relative: str) -> bytes:
        """Load a specific scorer's key; never enumerate the oracle or import product code."""
        root = oracle_root.resolve(strict=True)
        path = (root / relative).resolve(strict=True)
        if not path.is_relative_to(root):
            raise ValueError("Answer key path escapes oracle root")
        return path.read_bytes()

    def receipt(self, oracle_root: Path, keys: list[str]) -> dict:
        """Record verified inputs for downstream EVL-02/04 scorers, without invented metrics."""
        return {
            "status": "inputs_verified",
            "manifest_sha256": self.manifest_sha256,
            "protocol": self.manifest["protocol"],
            "counts": {kind: len(rows) for kind, rows in self.artifacts.items()},
            "answer_keys": [
                {"path": key, "sha256": digest(self.read_answer_key(oracle_root, key))}
                for key in keys
            ],
            "metrics": {},
        }
