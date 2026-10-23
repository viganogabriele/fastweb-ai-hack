"""Record and replay simulated answers to the Core dev demo clarification (OUT-02e).

Run with backend/.venv/bin/python scripts/clarification_answers_demo.py --help.

``record`` is the trusted recording importer: it rebuilds the published Core parent
offline from its committed recordings, registers each allowed answer in that private
database, and executes the follow-up with real Fastweb models (``record``) and the
local mock systems server. Only new envelopes are written to the output caches.

``replay`` denies networking and subprocesses. It rebuilds the same parent, registers
the allowed answers whose recordings are complete, submits them through the actual
HTTP endpoint and executes every follow-up from committed recordings only. With
``--register-only`` it stops before submission, leaving a database for the UI.
Neither command sends a message or exposes answer registration over HTTP.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prepare_core_demo import prepare
from replay_demo import (
    ReplayCache,
    allowed,
    digest,
    environment,
    offline,
    rebuild,
    semantic_payload,
)
from sqlalchemy import select

from tesseract.core.cache import ResponseCache
from tesseract.core.config import REPO_ROOT, Settings
from tesseract.core.contracts import (
    Case,
    EntityLink,
    EvidenceRelation,
    Observation,
    RunSpec,
)
from tesseract.core.db import connect, runs
from tesseract.core.llm import LLMClient
from tesseract.core.registry import Registry
from tesseract.core.repo import KINDS
from tesseract.core.run_repo import repo_session
from tesseract.core.systems_cache import SystemsCache, systems_factory
from tesseract.modules.agents.answer_registry import (
    AnswerRequest,
    execute_follow_up,
    register_recorded_answer,
    submit_answer,
)

ASSETS = REPO_ROOT / "data/fixtures/runs/core-dev-20261022"
ANSWERS = ASSETS / "clarification-answers"
CASE_IDS = ("case-mil01-i10919b00011-20261008", "case-mil01-unknown-20261009")


def requests(manifest):
    """Exact allowed requests; the idempotency key is stable per answer."""
    return {
        answer["key"]: AnswerRequest(
            run_id=manifest["parent_run_id"],
            scenario_id=manifest["scenario_id"],
            case_id=manifest["case_id"],
            case_version=manifest["case_version"],
            clarification_id=manifest["clarification_id"],
            clarification_version=manifest["clarification_version"],
            text=answer["text"],
            received_at=answer["received_at"],
            language=answer["language"],
            follow_up_scenario_id=answer["follow_up_scenario_id"],
            as_of=answer["as_of"],
            idempotency_key=f"out02e-{answer['key']}",
        )
        for answer in manifest["answers"]
    }


def run_digest(engine, run_id):
    """Semantic hash of every artifact in one run (trace timings excluded)."""
    with repo_session(engine, run_id) as repo:
        payloads = [
            (kind, record.model_dump(mode="json"))
            for kind, model in sorted(KINDS.items())
            for record in repo.list(model)
        ]
    return digest(
        [
            (kind, semantic_payload(kind, item))
            for kind, item in sorted(payloads, key=lambda p: (p[0], p[1]["id"], p[1]["version"]))
        ]
    )


def outcome(engine, run_id):
    """What the contextual reading changed in the child, for evidence and tests."""
    with repo_session(engine, run_id) as repo:
        state = repo.run_state()
        current = [o for o in repo.list(Observation) if not o.version.startswith("parent:")]
        corrected = [o for o in current if o.producer == "ag.contextual_answer"]
        links = [lk for lk in repo.list(EntityLink) if not lk.version.startswith("parent:")]
        cases = [c for c in repo.list(Case) if not c.version.startswith("parent:")]
        relations = [r for r in repo.list(EvidenceRelation) if r.relation == "supersedes"]
        statuses = repo.module_runs()
        result = {
            "status": state["status"],
            "published": state["published"],
            "current_observations": len(current),
            "duplicate_current_observation_ids": sorted(
                {o.id for o in current if sum(c.id == o.id for c in current) > 1}
            ),
            "answer_document_observations": sum(
                o.document_id.startswith("clarification-answer:") for o in current
            ),
            "supersedes": len(relations),
            "corrected": [],
            "module_errors": {
                s.module_id: list(s.result.errors) for s in statuses if s.result and s.result.errors
            },
        }
        for observation in corrected:
            ref = (observation.id, observation.version)
            result["corrected"].append(
                {
                    "observation_id": observation.id,
                    "version": observation.version,
                    "product_mention": observation.product_mention,
                    "quantity_raw": observation.quantity.raw if observation.quantity else None,
                    "available_at": observation.available_at.isoformat(),
                    "links": [
                        {"status": lk.status, "level": lk.level, "target_id": lk.target_id}
                        for lk in links
                        if lk.observation_id == observation.id
                    ],
                    "cases": [
                        {
                            "id": c.id,
                            "status": c.status,
                            "scope_level": c.scope_level,
                            "scope_id": c.scope_id,
                        }
                        for c in cases
                        if any((r.id, r.version) == ref for r in c.supporting)
                    ],
                }
            )
    return result


def stage_parent(workspace):
    """Rebuild the published Core parent offline from its committed recordings."""
    workspace = allowed(workspace)
    candidate = workspace / "candidate"
    spec = prepare(
        candidate,
        sources=REPO_ROOT / "generated/sources",
        config=REPO_ROOT / "config",
        code_version=RunSpec.model_validate_json(
            (ASSETS / "run-spec.json").read_text()
        ).code_version,
        case_ids=CASE_IDS,
    )
    if spec != RunSpec.model_validate_json((ASSETS / "run-spec.json").read_text()):
        raise ValueError("prepared Core snapshot differs from the recorded RunSpec")
    manifest = rebuild(
        spec,
        sources=candidate / "sources",
        config=candidate / "config",
        cache=ASSETS / "llm_cache",
        systems_cache=ASSETS / "systems_cache",
        workspace=workspace / "parent",
    )
    if manifest["status"] not in {"succeeded", "degraded"}:
        raise RuntimeError(f"Core parent replay failed: {manifest['missing_prerequisites']}")
    attempt = workspace / "parent" / manifest["attempt_id"]
    return spec, attempt, manifest


def settings_for(attempt, **values):
    return Settings(
        _env_file=None,
        sources_dir=attempt / "inputs/sources",
        config_dir=attempt / "inputs/config",
        data_dir=attempt / "data",
        **values,
    )


def code_identity():
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    dirty = subprocess.check_output(
        [
            "git",
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            "backend/tesseract",
            "backend/prompts",
            "config",
            "scripts",
        ],
        cwd=REPO_ROOT,
        text=True,
    )
    return sha, bool(dirty)


def record(output, *, workspace, keys_file=None):
    """Trusted importer: real model/system recordings for each allowed answer."""
    output = allowed(output)
    if output.exists():
        raise ValueError("output exists; choose a new recording directory")
    sha, dirty = code_identity()
    if dirty:
        raise ValueError("commit executable code, prompts and config before recording")
    manifest = json.loads((ANSWERS / "answers.json").read_text())
    _, attempt, parent_manifest = stage_parent(workspace)
    output.mkdir(parents=True)
    shutil.copyfile(ANSWERS / "answers.json", output / "answers.json")
    settings = settings_for(
        attempt,
        llm_mode="record",
        llm_concurrency=1,
        llm_deadline_seconds=1800,
        **({"fastweb_keys_file": keys_file} if keys_file else {}),
    )
    engine = connect(settings.db_url)
    llm = LLMClient(settings, cache=ResponseCache(output / "llm_cache"))
    systems = SystemsCache(output / "systems_cache")
    evidence = {
        "format": 1,
        "execution_sha": sha,
        "parent": {
            "run_id": parent_manifest["run_id"],
            "snapshot_sha256": parent_manifest["snapshot_sha256"],
            "output_sha256": parent_manifest["output_sha256"],
            "artifact_sha256": run_digest(engine, parent_manifest["run_id"]),
        },
        "answers": {},
    }
    try:
        for key, request in requests(manifest).items():
            # Private recording database only; replay re-registers after checking recordings.
            fingerprint = register_recorded_answer(engine, request)
            job = submit_answer(engine, request)
            first = len(llm.traces)
            with environment(settings):
                try:
                    execute_follow_up(
                        engine,
                        job.run.run_id,
                        clients={
                            "llm": llm.for_run(job.run),
                            "systems": systems_factory(
                                settings, job.run, systems, allow_recording=True
                            ),
                        },
                        settings=settings,
                    )
                except Exception as error:  # Evidence must show the failure, not hide it.
                    evidence["answers"][key] = {"error": f"{type(error).__name__}: {error}"}
            result = outcome(engine, job.run.run_id)
            traces = llm.traces[first:]
            evidence["answers"][key] = {
                **evidence["answers"].get(key, {}),
                "fingerprint": fingerprint,
                "run_id": job.run.run_id,
                "scenario_id": job.run.scenario_id,
                "llm_calls": len(traces),
                "llm_keys": sorted({t["key"] for t in traces}),
                "llm_traces": traces,
                "artifact_sha256": run_digest(engine, job.run.run_id),
                **result,
            }
        evidence["parent"]["artifact_sha256_after"] = run_digest(engine, parent_manifest["run_id"])
        evidence["systems_cache_misses"] = sorted(systems.missing)
        evidence["systems_cache_corrupt"] = sorted(systems.corrupt)
        evidence["complete"] = (
            evidence["parent"]["artifact_sha256"] == evidence["parent"]["artifact_sha256_after"]
            and not systems.missing
            and not systems.corrupt
            and all(a.get("published") and not a.get("error") for a in evidence["answers"].values())
        )
    finally:
        engine.dispose()
        (output / "recording-evidence.json").write_text(
            json.dumps(evidence, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
        )
        write_asset_manifest(output)
    return evidence


def write_asset_manifest(directory):
    files = [
        (relative, sha)
        for relative, sha in inventory(directory)
        if relative != "asset-manifest.json"
    ]
    (directory / "asset-manifest.json").write_text(
        json.dumps({"format": 1, "files": files}, indent=2) + "\n"
    )


def inventory(directory):
    return sorted(
        (path.relative_to(directory).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
        for path in directory.rglob("*.json")
    )


def import_recordings(attempt, answers):
    """Merge answer envelopes into an offline attempt. Existing keys must be identical."""
    for name in ("llm_cache", "systems_cache"):
        source = allowed(answers / name)
        target = attempt / "data" / name
        for relative, _ in inventory(source) if source.is_dir() else ():
            destination = target / relative
            data = (source / relative).read_bytes()
            if destination.exists() and destination.read_bytes() != data:
                raise ValueError("conflicting recording for the same key")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)


def register(engine, answers):
    """Trusted import: only answers whose real recordings completed are registered."""
    manifest = json.loads((answers / "answers.json").read_text())
    evidence = json.loads((answers / "recording-evidence.json").read_text())
    registered = {}
    for key, request in requests(manifest).items():
        recorded = evidence["answers"].get(key, {})
        if not recorded.get("published") or recorded.get("error"):
            continue
        fingerprint = register_recorded_answer(engine, request)
        if fingerprint != recorded["fingerprint"]:
            raise ValueError("answer fingerprint differs from its recording")
        registered[key] = request
    return registered


def replay(workspace, *, answers=ANSWERS, register_only=False):
    """Offline parent rebuild, trusted registration and HTTP submission of each answer."""
    from fastapi.testclient import TestClient

    from tesseract.api.main import create_app

    workspace = allowed(workspace)
    answers = allowed(answers)
    evidence_in = json.loads((answers / "recording-evidence.json").read_text())
    spec, attempt, parent_manifest = stage_parent(workspace)
    import_recordings(attempt, answers)
    settings = settings_for(
        attempt, llm_mode="replay", fastweb_keys_file=attempt / "no-credentials.json"
    )
    cache = ReplayCache(settings.data_dir / "llm_cache")
    systems = SystemsCache(settings.data_dir / "systems_cache")
    engine = connect(settings.db_url)
    result = {
        "format": 1,
        "attempt": attempt.name,
        "parent": {
            "run_id": spec.run_id,
            "snapshot_sha256": parent_manifest["snapshot_sha256"],
            "output_sha256": parent_manifest["output_sha256"],
            "artifact_sha256": run_digest(engine, spec.run_id),
        },
        "answers": {},
    }
    try:
        registered = register(engine, answers)
        result["registered"] = sorted(registered)
        if register_only:
            return result | {"status": "registered", "data_dir": str(settings.data_dir)}

        from tesseract.api.routers import clarifications

        def worker(engine, run_id, **kwargs):
            # The real HTTP worker, with miss accounting on the same recordings.
            with engine.connect() as conn:
                frozen = conn.execute(select(runs.c.spec).where(runs.c.run_id == run_id)).scalar()
            job_spec = RunSpec.model_validate(frozen)
            return execute_follow_up(
                engine,
                run_id,
                clients={
                    "llm": LLMClient(settings, cache=cache).for_run(job_spec),
                    "systems": systems_factory(settings, job_spec, systems),
                },
                **kwargs,
            )

        original = clarifications.execute_follow_up
        clarifications.execute_follow_up = worker
        app = create_app(engine=engine, registry=Registry.discover(), settings=settings)
        try:
            with offline() as denied, environment(settings), TestClient(app) as client:
                first = next(iter(registered.values()))
                base = (
                    f"/api/runs/{first.run_id}/cases/{first.case_id}"
                    f"/clarifications/{first.clarification_id}"
                )
                # The UI path: discover trusted bodies, add only an idempotency key.
                presets = client.get(base + "/registered-answers").json()
                by_key = {r.follow_up_scenario_id: k for k, r in registered.items()}
                for preset in presets:
                    key = by_key[preset["follow_up_scenario_id"]]
                    body = {k: v for k, v in preset.items() if k != "fingerprint"}
                    body["idempotency_key"] = f"replay-{key}"
                    response = client.post(base + "/answer", json=body)
                    retry = client.post(base + "/answer", json=body)
                    job = response.json()
                    run = client.get(f"/api/runs/{job['run']['run_id']}").json()
                    artifact = run_digest(engine, job["run"]["run_id"])
                    result["answers"][key] = {
                        "http_status": response.status_code,
                        "retry_same_job": retry.status_code == 202 and retry.json() == job,
                        "fingerprint": job["fingerprint"],
                        "run_id": job["run"]["run_id"],
                        "run_status": run["status"],
                        "published": run["published"],
                        "artifact_sha256": artifact,
                        "matches_recording": artifact
                        == evidence_in["answers"][key]["artifact_sha256"],
                        **outcome(engine, job["run"]["run_id"]),
                    }
                positive_misses = (set(cache.missing), set(systems.missing))
                # Offline refusals: free text is rejected; a registered answer at an
                # unrecorded clock is accepted but its child cannot publish.
                free = first.model_dump(mode="json") | {
                    "text": "Forse il cardigan, non ricordo.",
                    "idempotency_key": "replay-free-text",
                }
                later = first.model_dump(mode="json") | {
                    "follow_up_scenario_id": first.follow_up_scenario_id + "-unrecorded",
                    "as_of": "2026-10-22T21:30:00Z",
                    "idempotency_key": "replay-unrecorded-clock",
                }
                refused = client.post(base + "/answer", json=free)
                accepted = client.post(base + "/answer", json=later)
                state = client.get(f"/api/runs/{accepted.json()['run']['run_id']}").json()
                result["negative"] = {
                    "free_text_status": refused.status_code,
                    "unrecorded_clock_status": accepted.status_code,
                    "unrecorded_clock_run_status": state["status"],
                    "unrecorded_clock_published": state["published"],
                    "unrecorded_clock_misses": len(cache.missing - positive_misses[0])
                    + len(systems.missing - positive_misses[1]),
                }
                result["network_attempts"] = len(denied)
        finally:
            clarifications.execute_follow_up = original
        # Misses of the deliberate unrecorded-clock probe are reported under "negative".
        result["cache_misses"] = sorted(positive_misses[0])
        result["cache_corrupt"] = sorted(cache.corrupt)
        result["systems_cache_misses"] = sorted(positive_misses[1])
        result["parent"]["artifact_sha256_after"] = run_digest(engine, spec.run_id)
        result["status"] = (
            "passed"
            if result["parent"]["artifact_sha256"] == result["parent"]["artifact_sha256_after"]
            and not result["network_attempts"]
            and not result["cache_misses"]
            and not cache.corrupt
            and not result["systems_cache_misses"]
            and registered
            and set(result["answers"]) == set(registered)
            and result["negative"]["free_text_status"] == 424
            and result["negative"]["unrecorded_clock_status"] == 202
            and not result["negative"]["unrecorded_clock_published"]
            and result["negative"]["unrecorded_clock_misses"] > 0
            and all(
                a["published"] and a["matches_recording"] and a["retry_same_job"]
                for a in result["answers"].values()
            )
            else "failed"
        )
        return result
    finally:
        engine.dispose()
        (attempt / "answers-replay.json").write_text(
            json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    rec = commands.add_parser("record", help="real-model recording (uses Fastweb credit)")
    rec.add_argument("--output", type=Path, required=True)
    rec.add_argument("--workspace", type=Path, required=True)
    rec.add_argument("--keys-file", type=Path)
    rep = commands.add_parser("replay", help="offline replay with networking denied")
    rep.add_argument("--workspace", type=Path, required=True)
    rep.add_argument("--answers", type=Path, default=ANSWERS)
    rep.add_argument("--register-only", action="store_true")
    args = parser.parse_args(argv)
    os.umask(0o077)
    if args.command == "record":
        evidence = record(args.output, workspace=args.workspace, keys_file=args.keys_file)
        summary = {
            "complete": evidence.get("complete"),
            "answers": {
                k: {
                    "llm_calls": a.get("llm_calls"),
                    "status": a.get("status"),
                    "error": a.get("error"),
                    "corrected": a.get("corrected"),
                }
                for k, a in evidence["answers"].items()
            },
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if evidence.get("complete") else 1
    result = replay(
        args.workspace / ("attempt-" + uuid4().hex),
        answers=args.answers,
        register_only=args.register_only,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in {"passed", "registered"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
