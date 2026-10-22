"""Explicit, authorized fixture loading into a separate namespace only."""

import json
from pathlib import Path

from tessera.core.contracts import Segment, SourceDocument
from tessera.core.contracts.common import DerivedRecord
from tessera.core.repo import ARTIFACT_TYPES, Repo


def load_fixtures(repo: Repo, files: list[str], *, root: Path) -> dict[str, int]:
    """Load authorized paths relative to data/fixtures; never discover files.

    Derived fixtures are rebound to the target fixture run/scenario. Unknown or
    future artifacts are counted as excluded, not moved back in time. The caller
    owns the outer transaction; a savepoint also prevents partial imports if an
    error is caught by that caller.
    """
    if repo.namespace != "fixture" or repo.spec.mode != "fixture":
        raise ValueError("Fixtures may be loaded only in the fixture namespace")
    root = root.resolve(strict=True)
    allowed = set(repo.spec.authorized_fixture_refs)
    records = []
    for name in files:
        if name not in allowed:
            raise ValueError(f"Fixture is not authorized by RunSpec: {name}")
        path = (root / name).resolve(strict=True)
        if not path.is_relative_to(root) or path.suffix != ".json":
            raise ValueError("Fixture path escapes the fixture directory")
        content = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(content, list):
            raise ValueError("Fixture files must contain arrays of kind/payload records")
        for item in content:
            if not isinstance(item, dict) or set(item) != {"kind", "payload"}:
                raise ValueError("Invalid fixture envelope")
            kind = ARTIFACT_TYPES.get(item["kind"])
            if kind is None:
                raise ValueError("Unknown fixture artifact kind")
            payload = dict(item["payload"])
            if issubclass(kind, DerivedRecord):
                payload.update(run_id=repo.spec.run_id, scenario_id=repo.spec.scenario_id)
            records.append(kind.model_validate(payload))
    eligible = [
        record
        for record in records
        if record.available_at is not None and record.available_at <= repo.spec.as_of
    ]
    pending = sorted(
        eligible,
        key=lambda row: (
            0 if isinstance(row, SourceDocument) else 1 if isinstance(row, Segment) else 2,
            type(row).__name__,
            row.id,
            row.version,
        ),
    )
    count = 0
    with repo.session.begin_nested():
        while pending:
            deferred = []
            for row in pending:
                if isinstance(row, DerivedRecord) and any(
                    repo.get(ARTIFACT_TYPES[ref.kind], ref.id, ref.version) is None
                    for ref in row.input_refs
                    if ref.kind in ARTIFACT_TYPES
                ):
                    deferred.append(row)
                    continue
                repo.put(row)
                count += 1
            if len(deferred) == len(pending):
                raise ValueError("Fixture dependencies are missing, future, or cyclic")
            pending = deferred
    return {"loaded": count, "excluded": len(records) - len(eligible)}
