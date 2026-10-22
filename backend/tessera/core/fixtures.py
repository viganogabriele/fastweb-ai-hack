"""`tessera fixtures load`: hand-written fixtures as one published run in the fixture namespace.

Fixture files are `data/fixtures/<area>/*.json`, each a list of `{"kind", "payload"}` records
(`data/fixtures/README.md`). They load as run `fixture`, scenario `historical`, with `as_of` at
the latest `available_at` among them, into the fixture DB only (RFC §4.6): real runs never see
them. Loading again replaces the previous fixture run.
"""

import hashlib
import json
from pathlib import Path

from sqlalchemy import Engine

from tessera import __version__
from tessera.core.contracts import RunSpec
from tessera.core.contracts.common import SourceRecord
from tessera.core.repo import KINDS, Repo, RunNotFound, create_run, reset_run, set_run_status

FIXTURE_RUN_ID = "fixture"
FIXTURE_SCENARIO_ID = "historical"


def _digest(paths: list[Path], root: Path) -> str:
    h = hashlib.sha256()
    for path in paths:
        h.update(path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return "sha256:" + h.hexdigest()


def read_fixtures(fixtures_dir: Path) -> tuple[list[Path], list[SourceRecord]]:
    paths = sorted(fixtures_dir.glob("*/*.json"))
    records = []
    for path in paths:
        for i, rec in enumerate(json.loads(path.read_text(encoding="utf-8"))):
            if rec["kind"] not in KINDS:
                raise ValueError(f"{path}[{i}]: {rec['kind']!r} is not a storable contract")
            records.append(KINDS[rec["kind"]].model_validate(rec["payload"]))
    return paths, records


def load_fixtures(engine: Engine, fixtures_dir: Path, config_dir: Path) -> tuple[RunSpec, int]:
    """Replace the fixture run with the fixtures on disk; returns its spec and record count."""
    paths, records = read_fixtures(fixtures_dir)
    known = [r.available_at for r in records if r.available_at is not None]
    if not known:
        raise ValueError(f"no fixture with a known available_at under {fixtures_dir}")
    configs = sorted(config_dir.glob("*.yaml"))
    spec = RunSpec(
        run_id=FIXTURE_RUN_ID,
        scenario_id=FIXTURE_SCENARIO_ID,
        as_of=max(known),
        stores=tuple(sorted({s for r in records if (s := getattr(r, "store_id", None))})),
        source_manifest_hash=_digest(paths, fixtures_dir),
        config_hash=_digest(configs, config_dir),
        code_version=__version__,
        mode="fixture",
        modules=(),
        prompt_versions={},
        model_versions={},
        authorized_fixture_refs=tuple(p.relative_to(fixtures_dir).as_posix() for p in paths),
    )
    try:
        reset_run(engine, FIXTURE_RUN_ID)
    except RunNotFound:
        pass
    create_run(engine, spec)
    try:
        n = Repo(engine, spec).put(*records)
    except Exception:
        set_run_status(engine, FIXTURE_RUN_ID, "failed")
        raise
    set_run_status(engine, FIXTURE_RUN_ID, "published")
    return spec, n
