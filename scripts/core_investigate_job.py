"""Record, or verify offline, one positive POST-investigate job bound to a Core candidate.

record: copies the recorded candidate's published database into a new private directory,
marks only that copy's parent RunSpec live (the API never records on a recorded parent;
job identity and cache keys exclude execution mode), POSTs the job in record mode and
writes the job's own LLM and simulated-system envelopes plus a manifest pinning the parent
snapshot, artifact inventory, case version, job ID and trace. The candidate is unchanged.

verify: on a fresh offline replay attempt rebuilt from the package (replay_demo.py), POSTs
the same job against the unmodified recorded parent with networking denied, using only the
packaged job recordings. Job ID, trace, job artifacts and parent inventory must match.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from check_core_demo import artifact_inventory
from fastapi.testclient import TestClient
from replay_demo import allowed, digest, environment, offline, semantic_payload, stage
from sqlalchemy import select, update

from tesseract.api.main import create_app
from tesseract.core.config import REPO_ROOT, Settings
from tesseract.core.contracts import AgentTrace, Case, RunSpec
from tesseract.core.db import connect, runs
from tesseract.core.repo import latest
from tesseract.core.run_repo import repo_session


def recordings(directory):
    return sorted(
        (path.stem, hashlib.sha256(path.read_bytes()).hexdigest())
        for path in Path(directory).rglob("*.json")
    )


def private_copy(database, root, settings_args):
    """A new directory with a copy of the database; the source database is never opened."""
    root.mkdir(mode=0o700)
    settings = Settings(_env_file=None, data_dir=root / "data", **settings_args)
    settings.data_dir.mkdir()
    shutil.copyfile(allowed(database), settings.db_path)
    return settings


def parent_state(engine, spec, case_id):
    with repo_session(engine, spec.run_id) as repo:
        if repo.spec != spec:
            raise ValueError("published snapshot differs from the candidate RunSpec")
        case = next((c for c in latest(repo.list(Case)) if c.id == case_id), None)
        if case is None:
            raise ValueError("case not in the published candidate")
        traces = {(t.id, t.version) for t in repo.list(AgentTrace)}
        return artifact_inventory(repo), case, traces


def post_job(settings, engine, spec, case_id, parent_traces):
    fixture = connect("sqlite://")
    try:
        app = create_app(engine=engine, fixture_engine=fixture, settings=settings)
        with TestClient(app) as api:
            response = api.post(f"/api/runs/{spec.run_id}/cases/{case_id}/investigate")
            if response.status_code != 202:
                raise ValueError(f"investigate returned {response.status_code}")
            job_id = response.json()["spec"]["run_id"]
            # TestClient runs the background job before returning.
            state = api.get(f"/api/runs/{job_id}").json()
    finally:
        fixture.dispose()
    if not state["published"]:
        return job_id, state, None, None
    with repo_session(engine, job_id) as repo:
        new = [t for t in repo.list(AgentTrace) if (t.id, t.version) not in parent_traces]
        if len(new) != 1 or new[0].case_id != case_id:
            raise ValueError("the job must publish exactly one new trace for the case")
        return job_id, state, new[0], artifact_inventory(repo)


def trace_summary(trace):
    return {
        "id": trace.id,
        "version": trace.version,
        "outcome": trace.outcome,
        "fallback_used": trace.fallback_used,
        "mode": trace.mode,
        "tools": [s.tool for s in trace.steps],
        "semantic_sha256": digest(semantic_payload("AgentTrace", trace.model_dump(mode="json"))),
    }


def record(candidate, *, case_id, output):
    candidate, output = allowed(candidate), allowed(output)
    if output.exists():
        raise ValueError("output exists; job recordings are never overwritten")
    spec = RunSpec.model_validate_json((candidate / "run-spec.json").read_text())
    if spec.mode != "recorded" or spec.authorized_fixture_refs:
        raise ValueError("source-backed recorded candidate required")
    execution_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()
    source = Settings(_env_file=None, data_dir=candidate / "runtime")
    settings = private_copy(
        source.db_path,
        candidate / ("job-recording-" + uuid4().hex),
        {
            "llm_mode": "record",
            "sources_dir": candidate / "sources",
            "config_dir": candidate / "config",
            "llm_concurrency": 1,
            "llm_deadline_seconds": 900,
        },
    )
    engine = connect(settings.db_url)
    try:
        before, case, parent_traces = parent_state(engine, spec, case_id)
        live = spec.model_copy(update={"mode": "live"}).model_dump(mode="json")
        with engine.begin() as conn:
            conn.execute(update(runs).where(runs.c.run_id == spec.run_id).values(spec=live))
        with environment(settings):
            job_id, state, trace, job_inventory = post_job(
                settings, engine, spec, case_id, parent_traces
            )
        with engine.begin() as conn:
            conn.execute(
                update(runs)
                .where(runs.c.run_id == spec.run_id)
                .values(spec=spec.model_dump(mode="json"))
            )
        after, _, _ = parent_state(engine, spec, case_id)
        with engine.connect() as conn:
            job_spec = conn.execute(select(runs.c.spec).where(runs.c.run_id == job_id)).scalar()
    finally:
        engine.dispose()
    if trace is None or after != before:
        raise ValueError(f"job not published ({state['status']}) or parent changed")
    output.mkdir(mode=0o700)
    for name in ("llm_cache", "systems_cache"):
        if (settings.data_dir / name).is_dir():
            shutil.copytree(settings.data_dir / name, output / name)
        else:
            (output / name).mkdir()
    manifest = {
        "format": 1,
        "status": "recorded",
        "execution_sha": execution_sha,
        "parent": {
            "run_id": spec.run_id,
            "snapshot_sha256": digest(spec.model_dump(mode="json")),
            "code_version": spec.code_version,
            "artifact_inventory_sha256": before,
            "unchanged_after_job": True,
            "recording_copy_mode": "live (private database copy only)",
        },
        "case": {"id": case.id, "version": case.version},
        "job": {
            "run_id": job_id,
            "status": state["status"],
            "spec_sha256": digest(job_spec),
            "artifact_inventory_sha256": job_inventory,
        },
        "trace": trace_summary(trace),
        "recordings": {
            "llm_cache": recordings(output / "llm_cache"),
            "systems_cache": recordings(output / "systems_cache"),
        },
        "limitations": [
            "Synthetic dev candidate; no human decision, dispatch or hold-out claim.",
            "Recorded on a private copy whose parent was marked live; the copy is discarded.",
        ],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    shutil.rmtree(settings.data_dir.parent)
    return manifest


def verify(attempt, *, job, workspace):
    """Replay from a rebuilt attempt plus packaged job recordings only, networking denied."""
    attempt, job, workspace = allowed(attempt), allowed(job), allowed(workspace)
    manifest = json.loads((job / "manifest.json").read_text())
    rebuilt = json.loads((attempt / "manifest.json").read_text())
    if rebuilt["status"] not in {"succeeded", "degraded"}:
        raise ValueError("the offline rebuild did not complete")
    if rebuilt["snapshot_sha256"] != manifest["parent"]["snapshot_sha256"]:
        raise ValueError("job recordings belong to another candidate snapshot")
    for name in ("llm_cache", "systems_cache"):
        if recordings(job / name) != [list(r) for r in manifest["recordings"][name]]:
            raise ValueError(f"packaged {name} differs from the job manifest")
    workspace.mkdir(mode=0o700, parents=True, exist_ok=True)
    attempt_settings = Settings(_env_file=None, data_dir=attempt / "data")
    settings = private_copy(
        attempt_settings.db_path,
        workspace / ("job-replay-" + uuid4().hex),
        {
            "llm_mode": "replay",
            "sources_dir": attempt / "inputs/sources",
            "config_dir": attempt / "inputs/config",
            "fastweb_keys_file": workspace / "no-credentials.json",
        },
    )
    staged = {
        name: stage(job / name, settings.data_dir / name) for name in ("llm_cache", "systems_cache")
    }
    engine = connect(settings.db_url)
    try:
        with engine.connect() as conn:
            stored = conn.execute(
                select(runs.c.spec).where(runs.c.run_id == manifest["parent"]["run_id"])
            ).scalar_one()
        spec = RunSpec.model_validate(stored)
        if digest(spec.model_dump(mode="json")) != manifest["parent"]["snapshot_sha256"]:
            raise ValueError("rebuilt parent differs from the recorded parent")
        before, case, parent_traces = parent_state(engine, spec, manifest["case"]["id"])
        with offline() as denied, environment(settings):
            job_id, state, trace, job_inventory = post_job(
                settings, engine, spec, case.id, parent_traces
            )
        after, _, _ = parent_state(engine, spec, case.id)
    finally:
        engine.dispose()
    result = {
        "format": 1,
        "job_id": job_id,
        "job_status": state["status"],
        "job_published": state["published"],
        "network_attempts": len(denied),
        "inputs": staged,
        "checks": {
            "parent_inventory_matches_recording": before
            == manifest["parent"]["artifact_inventory_sha256"],
            "parent_unchanged": after == before,
            "case_version_matches": case.version == manifest["case"]["version"],
            "job_id_matches": job_id == manifest["job"]["run_id"],
            "trace_matches": trace is not None and trace_summary(trace) == manifest["trace"],
            "job_artifacts_match": job_inventory == manifest["job"]["artifact_inventory_sha256"],
        },
    }
    result["status"] = "passed" if all(result["checks"].values()) and not denied else "failed"
    shutil.rmtree(settings.data_dir.parent)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    rec = commands.add_parser("record")
    rec.add_argument("--candidate", type=Path, required=True)
    rec.add_argument("--case-id", required=True)
    rec.add_argument("--output", type=Path, required=True)
    ver = commands.add_parser("verify")
    ver.add_argument("--attempt", type=Path, required=True)
    ver.add_argument("--job", type=Path, required=True)
    ver.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "record":
        result = record(args.candidate, case_id=args.case_id, output=args.output)
    else:
        result = verify(args.attempt, job=args.job, workspace=args.workspace)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] in {"recorded", "passed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
