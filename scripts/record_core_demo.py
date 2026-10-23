"""Record an explicit prepared dev candidate, preserving its recorded provenance.

No source discovery, projection preloading or fake-model responses. Credentials
are resolved only by Settings. Use --reset-projections only in this dedicated
candidate; existing decisions are refused, and earlier execution evidence is kept.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from replay_demo import allowed, digest, environment

from tessera.core.config import REPO_ROOT, Settings
from tessera.core.contracts import RunSpec
from tessera.core.db import connect
from tessera.core.llm import LLMClient
from tessera.core.orchestrator import run
from tessera.core.repo import reset_run
from tessera.core.run_repo import repo_session
from tessera.core.systems_cache import SystemsCache, systems_factory


def record(candidate, *, execution_sha, reset=False):
    candidate = allowed(candidate)
    if not allowed(candidate / "input-manifest.json").is_file():
        raise ValueError("prepare the explicit dev candidate first")
    spec = RunSpec.model_validate_json(allowed(candidate / "run-spec.json").read_text())
    if spec.mode != "recorded" or spec.authorized_fixture_refs:
        raise ValueError("source-backed recorded snapshot required")
    if spec.code_version != execution_sha:
        raise ValueError("candidate code_version must match the executing candidate SHA")
    actual_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()
    if execution_sha != actual_sha:
        raise ValueError("execution SHA does not match the current checkout")
    dirty_code = subprocess.check_output(
        [
            "git",
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            "backend/tessera",
            "backend/prompts",
            "scripts",
        ],
        cwd=REPO_ROOT,
        text=True,
    )
    if dirty_code:
        raise ValueError("commit executable code and prompts before recording")
    for name, expected in (("sources", spec.source_manifest_hash), ("config", spec.config_hash)):
        root = allowed(candidate / name)
        inventory = []
        for item in sorted(root.rglob("*")):
            item = allowed(item)
            if item.is_dir():
                continue
            if not item.is_file():
                raise ValueError("non-regular candidate input")
            inventory.append(
                (item.relative_to(root).as_posix(), hashlib.sha256(item.read_bytes()).hexdigest())
            )
        if digest(inventory) != expected:
            raise ValueError("candidate inputs changed; prepare and review a new snapshot")
    allowed(candidate / "runtime")
    settings = Settings(
        _env_file=None,
        llm_mode="record",
        sources_dir=candidate / "sources",
        config_dir=candidate / "config",
        data_dir=candidate / "runtime",
        llm_concurrency=1,
        llm_deadline_seconds=900,
    )
    settings.data_dir.mkdir(exist_ok=True)
    exists = settings.db_path.exists()
    if exists and not reset:
        raise ValueError("candidate projections exist; choose another candidate or explicit reset")
    engine = connect(settings.db_url)
    client = LLMClient(settings)
    systems = SystemsCache(settings.data_dir / "systems_cache")
    try:
        if exists:
            from sqlalchemy import inspect, select

            from tessera.modules.actions.ledger import drafts

            with engine.connect() as conn:
                if inspect(conn).has_table(drafts.name) and conn.execute(select(drafts)).first():
                    raise ValueError("candidate has durable decisions; use a fresh candidate")
            reset_run(engine, spec.run_id)
        with environment(settings):
            statuses = run(
                spec,
                engine=engine,
                settings=settings,
                clients={
                    "llm": client.for_run(spec),
                    "systems": systems_factory(settings, spec, systems, allow_recording=True),
                },
            )
        with repo_session(engine, spec.run_id) as repo:
            state = repo.run_state()
        complete = (
            state["published"]
            and all(
                s.status in {"succeeded", "degraded"}
                and s.result is not None
                and not s.result.errors
                for s in statuses
            )
            and not systems.missing
            and not systems.corrupt
        )
        evidence = {
            "format": 1,
            "execution_sha": execution_sha,
            "run_id": spec.run_id,
            "status": state["status"],
            "complete": complete,
            "snapshot": spec.model_dump(mode="json"),
            "llm_traces": client.traces,
            "modules": [s.model_dump(mode="json") for s in statuses],
            "systems_cache_misses": sorted(systems.missing),
            "systems_cache_corrupt": sorted(systems.corrupt),
        }
        output = candidate / "executions"
        output.mkdir(exist_ok=True)
        path = output / ("record-" + uuid4().hex + ".json")
        path.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n")
        print(
            json.dumps(
                {
                    "complete": bool(complete),
                    "evidence": str(path),
                    "provider_calls": len(client.traces),
                }
            )
        )
        return 0 if complete else 1
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--execution-sha", required=True)
    parser.add_argument("--reset-projections", action="store_true")
    args = parser.parse_args()
    return record(args.candidate, execution_sha=args.execution_sha, reset=args.reset_projections)


if __name__ == "__main__":
    raise SystemExit(main())
