"""Record, or verify offline, one positive POST-investigate job bound to a Core candidate.

record: copies the recorded candidate's published database into a new private directory,
marks only that copy's parent RunSpec live (the API never records on a recorded parent;
job identity and cache keys exclude execution mode), POSTs the job in record mode and
writes the job's own LLM and simulated-system envelopes plus a manifest pinning the parent
snapshot, artifact inventory, case version, job ID and trace. The scratch copy lives in a
temporary directory outside the candidate and is removed on every exit.

verify: on a fresh offline replay attempt rebuilt from the package (replay_demo.py), POSTs
the same job against the unmodified recorded parent with networking denied, using only the
packaged job recordings. Job ID, trace, job artifacts and parent inventory must match.

rebind: after a reviewed code fix that changes only parent-derived artifacts, replays the
job as verify does and re-pins the parent and job artifact inventories. Job ID, case version,
trace and every envelope must still match; the earlier pins stay in the manifest. No provider
is called and no recording is replaced.
"""

import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

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


@contextmanager
def private_copy(database, settings_args):
    """A scratch directory outside every input with a consistent copy of the database.

    SQLite's backup API includes committed WAL pages; the source is opened read-only.
    The scratch directory is removed on every exit, including failures.
    """
    root = Path(tempfile.mkdtemp(prefix="core-investigate-job-"))
    try:
        settings = Settings(_env_file=None, data_dir=root / "data", **settings_args)
        settings.data_dir.mkdir()
        source = sqlite3.connect(f"file:{allowed(database)}?mode=ro", uri=True)
        target = sqlite3.connect(settings.db_path)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
        yield settings
    finally:
        shutil.rmtree(root)


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
        "stop_reason": trace.steps[-1].arguments.get("reason") if trace.fallback_used else None,
        "semantic_sha256": digest(semantic_payload("AgentTrace", trace.model_dump(mode="json"))),
    }


def head():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def record(candidate, *, case_id, output):
    candidate, output = allowed(candidate), allowed(output)
    if output.exists():
        raise ValueError("output exists; job recordings are never overwritten")
    spec = RunSpec.model_validate_json((candidate / "run-spec.json").read_text())
    if spec.mode != "recorded" or spec.authorized_fixture_refs:
        raise ValueError("source-backed recorded candidate required")
    execution_sha = head()
    source = Settings(_env_file=None, data_dir=candidate / "runtime")
    with private_copy(
        source.db_path,
        {
            "llm_mode": "record",
            "sources_dir": candidate / "sources",
            "config_dir": candidate / "config",
            "llm_concurrency": 1,
            "llm_deadline_seconds": 900,
        },
    ) as settings:
        return _record(settings, spec, case_id, output, execution_sha)


def _record(settings, spec, case_id, output, execution_sha):
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
    if trace_summary(trace)["stop_reason"] == "budget_time":
        # Replay is faster than the provider: the wall-clock stop would not recur and the
        # replay would ask for a turn that was never recorded. Record again instead.
        raise ValueError("the job stopped on the wall-clock budget; it cannot be replayed")
    output.mkdir(mode=0o700)
    for name in ("llm_cache", "systems_cache"):
        # An unused cache stays absent: git cannot carry an empty directory.
        if any((settings.data_dir / name).rglob("*.json")):
            shutil.copytree(settings.data_dir / name, output / name)
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
    return manifest


def verify(attempt, *, job, workspace):
    """Replay from a rebuilt attempt plus packaged job recordings only, networking denied."""
    return _replay(attempt, job=job, workspace=workspace)[0]


def rebind(attempt, *, job, workspace, reason):
    """Re-pin the inventories only when every other recorded value replays unchanged."""
    result, observed = _replay(attempt, job=job, workspace=workspace)
    kept = ("parent_unchanged", "case_version_matches", "job_id_matches", "trace_matches")
    if result["network_attempts"] or not all(result["checks"][check] for check in kept):
        raise ValueError("the job itself changed; record it again instead of rebinding")
    path = allowed(job) / "manifest.json"
    manifest = json.loads(path.read_text())
    previous = {
        "parent": manifest["parent"]["artifact_inventory_sha256"],
        "job": manifest["job"]["artifact_inventory_sha256"],
    }
    manifest["parent"]["artifact_inventory_sha256"] = observed["parent"]
    manifest["job"]["artifact_inventory_sha256"] = observed["job"]
    manifest.setdefault("rebound", []).append(
        {"execution_sha": head(), "reason": reason, "previous_artifact_inventory_sha256": previous}
    )
    path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return {**result, "status": "rebound", "artifact_inventory_sha256": observed}


def _replay(attempt, *, job, workspace):
    attempt, job, workspace = allowed(attempt), allowed(job), allowed(workspace)
    manifest = json.loads((job / "manifest.json").read_text())
    rebuilt = json.loads((attempt / "manifest.json").read_text())
    if rebuilt["status"] not in {"succeeded", "degraded"}:
        raise ValueError("the offline rebuild did not complete")
    if rebuilt["snapshot_sha256"] != manifest["parent"]["snapshot_sha256"]:
        raise ValueError("job recordings belong to another candidate snapshot")
    for name in ("llm_cache", "systems_cache"):
        if [list(r) for r in recordings(job / name)] != manifest["recordings"][name]:
            raise ValueError(f"packaged {name} differs from the job manifest")
    workspace.mkdir(mode=0o700, parents=True, exist_ok=True)
    attempt_settings = Settings(_env_file=None, data_dir=attempt / "data")
    with private_copy(
        attempt_settings.db_path,
        {
            "llm_mode": "replay",
            "sources_dir": attempt / "inputs/sources",
            "config_dir": attempt / "inputs/config",
            "fastweb_keys_file": workspace / "no-credentials.json",
        },
    ) as settings:
        return _verify(settings, job, manifest)


def _verify(settings, job, manifest):
    staged = {
        name: stage(job / name, settings.data_dir / name)
        for name in ("llm_cache", "systems_cache")
        if manifest["recordings"][name]
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
    return result, {"parent": before, "job": job_inventory}


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
    reb = commands.add_parser("rebind")
    reb.add_argument("--attempt", type=Path, required=True)
    reb.add_argument("--job", type=Path, required=True)
    reb.add_argument("--workspace", type=Path, required=True)
    reb.add_argument("--reason", required=True)
    args = parser.parse_args()
    if args.command == "record":
        result = record(args.candidate, case_id=args.case_id, output=args.output)
    elif args.command == "rebind":
        result = rebind(args.attempt, job=args.job, workspace=args.workspace, reason=args.reason)
    else:
        result = verify(args.attempt, job=args.job, workspace=args.workspace)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] in {"recorded", "passed", "rebound"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
