"""Rebuild an explicit snapshot offline in a fresh, owned attempt directory.

Run with backend/.venv/bin/python scripts/replay_demo.py --help. No projections,
ledger, secrets or provider clients are imported from a previous workspace.

--decisions accepts an ordered JSON array of FrozenDecision objects. Each event
contains namespace, snapshot_sha256 (digest of RunSpec.model_dump(mode="json")),
at, the original DecisionRequest, and draft (the exact exported LocalDraft).
The approval service revalidates these events before saving their original IDs.
"""

import argparse
import hashlib
import json
import logging
import os
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import TypeAdapter
from sqlalchemy import inspect, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from tessera.core.cache import CacheCorrupt, ReplayMiss, ResponseCache
from tessera.core.config import Settings, get_settings
from tessera.core.contracts import RunSpec
from tessera.core.contracts.common import Contract, Instant, Text
from tessera.core.db import connect
from tessera.core.llm import LLMClient
from tessera.core.orchestrator import run
from tessera.core.registry import Registry
from tessera.core.repo import KINDS
from tessera.core.run_repo import repo_session
from tessera.core.systems_cache import SystemsCache, systems_factory
from tessera.modules.actions import ledger
from tessera.modules.actions.approval import DecisionRequest, LocalDraft, decide

MARKER = ".tessera-replay-workspace.json"
OWNER = {"format": 1, "owner": "tessera-offline-replay"}
FORBIDDEN = {".env", ".secrets", "ground_truth", "generator", "email_context"}


class IsolationError(ValueError):
    pass


class OfflineNetworkDenied(RuntimeError):
    pass


class FrozenDecision(Contract):
    snapshot_sha256: Text
    namespace: Literal["fixture", "product"]
    at: Instant
    request: DecisionRequest
    draft: LocalDraft


class ReplayCache(ResponseCache):
    def __init__(self, directory):
        super().__init__(directory)
        self.missing: set[str] = set()
        self.corrupt: set[str] = set()

    def get(self, key):
        try:
            return super().get(key)
        except ReplayMiss:
            self.missing.add(key)
            raise
        except CacheCorrupt:
            self.corrupt.add(key)
            raise

    def put(self, key, response):
        raise IsolationError("replay cache is read-only")


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


def semantic_payload(kind, payload):
    # Retain measured timings in the DB/raw artifact hash. They describe this
    # execution, rather than evidence, policy or the recorded model's choices.
    if kind == "AgentTrace":
        return {
            **payload,
            "steps": [
                {k: v for k, v in step.items() if k != "duration_ms"} for step in payload["steps"]
            ],
        }
    return payload


def allowed(path):
    # Check every lexical ancestor before resolve() can hide a link or a
    # forbidden component (including one followed by '..').
    path = Path(path).absolute()
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink():
            raise IsolationError("symlink input")
        if ancestor.name in FORBIDDEN or ancestor.name.endswith("_notes.md"):
            raise IsolationError("forbidden input location")
        if ancestor.name == "labels" and ancestor.parent.name == "eval":
            raise IsolationError("forbidden input location")
    path = path.resolve()
    if any(p in FORBIDDEN or p.endswith("_notes.md") for p in path.parts):
        raise IsolationError("forbidden input location")
    return path


def stage(root, destination):
    """Copy regular inputs only; the source trees and shared cache stay untouched."""
    root = allowed(root)
    if not root.is_dir():
        raise FileNotFoundError("required input directory")
    destination.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(root.rglob("*")):
        checked = allowed(path)
        if not checked.is_relative_to(root):
            raise IsolationError("input escapes root")
        if path.is_dir():
            continue
        if not path.is_file():
            raise IsolationError("non-regular input")
        relative = path.relative_to(root)
        content = path.read_bytes()
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        files.append((relative.as_posix(), hashlib.sha256(content).hexdigest()))
    return {"sha256": digest(files), "files": len(files)}


@contextmanager
def offline():
    # Audit hooks cannot be removed. Disable this hook on exit so focused tests
    # may reuse their process; the command itself always runs in its own process.
    active = [True]
    denied = []

    def audit(event, args):
        if active[0] and (
            event
            in {
                "socket.connect",
                "socket.getaddrinfo",
                "socket.gethostbyname",
                "socket.gethostbyaddr",
                "socket.getnameinfo",
                "socket.bind",
                "socket.sendto",
                "socket.sendmsg",
                "subprocess.Popen",
                "os.system",
                "os.exec",
                "os.posix_spawn",
            }
        ):
            denied.append(event)
            raise OfflineNetworkDenied("offline replay denied network/process operation")

    sys.addaudithook(audit)
    try:
        yield denied
    finally:
        active[0] = False


@contextmanager
def environment(settings):
    values = settings.model_dump(exclude={"asr_api_key"})
    values["asr_api_key"] = ""
    updates = {key.upper(): str(value) for key, value in values.items()}
    previous = {key: os.environ.get(key) for key in updates}
    # Modules import the cached get_settings function directly. Its Settings()
    # would still open the repository dotenv even when every field is overridden
    # through the environment; prevent that read for this dedicated command.
    previous_env_file = Settings.model_config.get("env_file")
    try:
        Settings.model_config["env_file"] = None
        os.environ.update(updates)
        get_settings.cache_clear()
        yield
    finally:
        Settings.model_config["env_file"] = previous_env_file
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        get_settings.cache_clear()


def attempt_directory(workspace, inputs):
    workspace = allowed(workspace)
    for path in inputs:
        path = allowed(path)
        if workspace.is_relative_to(path) or path.is_relative_to(workspace):
            raise IsolationError("workspace overlaps an input")
    workspace.mkdir(parents=True, exist_ok=True, mode=0o700)
    marker = workspace / MARKER
    if marker.exists():
        if marker.is_symlink() or json.loads(marker.read_text()) != OWNER:
            raise IsolationError("workspace ownership mismatch")
    else:
        if any(workspace.iterdir()):
            raise IsolationError("workspace is not empty or owned")
        with marker.open("x") as stream:
            json.dump(OWNER, stream, sort_keys=True)
    attempt = workspace / ("attempt-" + uuid4().hex)
    attempt.mkdir(mode=0o700)
    return attempt


def rebuild(
    spec,
    *,
    sources,
    config,
    cache,
    workspace,
    voice=None,
    systems_cache=None,
    decisions=None,
    registry=None,
):
    """Trusted installed modules only. Each invocation starts with a fresh SQLite DB."""
    attempt = attempt_directory(
        workspace,
        (
            sources,
            config,
            cache,
            *((voice,) if voice else ()),
            *((systems_cache,) if systems_cache else ()),
            *((decisions,) if decisions else ()),
        ),
    )
    manifest = {
        "format": 2,
        "attempt_id": attempt.name,
        "run_id": spec.run_id,
        "scenario_id": spec.scenario_id,
        "as_of": spec.as_of.isoformat(),
        "namespace": "fixture" if spec.mode == "fixture" else "product",
        "fixture_demo_only": spec.mode == "fixture",
        "execution_mode": "replay",
        "snapshot_sha256": digest(spec.model_dump(mode="json")),
        "status": "failed",
        "run_status": "not_started",
        "modules": [],
        "missing_prerequisites": [],
        "network_attempts": 0,
        "cache_misses": [],
        "cache_corrupt": [],
        "systems_cache_misses": [],
        "systems_cache_corrupt": [],
        "decisions": [],
        "ledger_sha256": None,
        "inputs": {},
        "output_sha256": None,
        "output_hash_excludes": ["AgentTrace.steps[*].duration_ms"],
    }
    engine = None
    replay_cache = None
    recorded_systems = None
    denied = []
    try:
        if spec.mode == "unavailable" or not any(
            s.manifest.enabled and s.manifest.mode != "unavailable" for s in spec.modules
        ):
            raise ValueError("no runnable snapshot")
        if spec.authorized_fixture_refs:
            # Generic preloading of derived fixtures would masquerade as a rebuild.
            raise IsolationError("fixture artifact preloading is unsupported; use source inputs")
        needs_voice = any(
            s.manifest.id == "src.voice" and s.manifest.enabled and s.manifest.mode != "unavailable"
            for s in spec.modules
        )
        if needs_voice and voice is None:
            manifest["missing_prerequisites"].append("voice_inputs")
            raise FileNotFoundError("voice source directory required")
        trees = [
            ("sources", sources, attempt / "inputs/sources"),
            ("config", config, attempt / "inputs/config"),
            ("cache", cache, attempt / "data/llm_cache"),
        ]
        if voice is not None:
            trees.append(("voice", voice, attempt / "data/fixtures/voice"))
        if systems_cache is not None:
            trees.append(("systems_cache", systems_cache, attempt / "data/systems_cache"))
        for name, root, dest in trees:
            manifest["missing_prerequisites"].append(name)
            manifest["inputs"][name] = stage(root, dest)
            manifest["missing_prerequisites"].pop()
        frozen_decisions = []
        if decisions is not None:
            raw = allowed(decisions).read_bytes()
            frozen_decisions = TypeAdapter(list[FrozenDecision]).validate_json(raw)
            if any(
                d.request.run_id != spec.run_id
                or d.request.scenario_id != spec.scenario_id
                or d.snapshot_sha256 != manifest["snapshot_sha256"]
                or d.namespace != manifest["namespace"]
                or d.at < spec.as_of
                for d in frozen_decisions
            ):
                raise IsolationError("decision does not belong to this snapshot/clock")
            if any(
                a.at > b.at for a, b in zip(frozen_decisions, frozen_decisions[1:], strict=False)
            ):
                raise IsolationError("decision clocks must be chronological")
            identities = {}
            for frozen in frozen_decisions:
                key = frozen.draft.decision.id
                if key in identities and identities[key] != frozen:
                    raise IsolationError("conflicting frozen decision identity")
                identities[key] = frozen
            (attempt / "inputs/decisions.json").write_bytes(raw)
            manifest["inputs"]["decisions"] = {
                "sha256": hashlib.sha256(raw).hexdigest(),
                "files": 1,
            }

        for name, expected in (
            ("sources", spec.source_manifest_hash),
            ("config", spec.config_hash),
        ):
            if manifest["inputs"][name]["sha256"] != expected:
                manifest["missing_prerequisites"].append(name + "_hash_mismatch")
                raise IsolationError("staged inputs differ from the declared snapshot")

        settings = Settings(
            _env_file=None,
            sources_dir=attempt / "inputs/sources",
            config_dir=attempt / "inputs/config",
            data_dir=attempt / "data",
            fixture_mode=spec.mode == "fixture",
            llm_mode="replay",
            fastweb_keys_file=attempt / "no-credentials.json",
            asr_api_key=None,
        )
        manifest["provider_identity_sha256"] = digest(
            {
                key: getattr(settings, key)
                for key in (
                    "fastweb_base_url",
                    "asr_base_url",
                    "chat_model",
                    "embed_model",
                    "asr_model",
                )
            }
        )
        replay_cache = ReplayCache(settings.data_dir / "llm_cache")
        recorded_systems = SystemsCache(settings.data_dir / "systems_cache")
        engine = connect(settings.db_url)
        old_logging = logging.root.manager.disable
        try:
            logging.disable(logging.CRITICAL)
            with (
                offline() as denied,
                environment(settings),
                open(os.devnull, "w") as sink,
            ):
                with redirect_stdout(sink), redirect_stderr(sink):
                    client = LLMClient(settings, cache=replay_cache).for_run(spec)
                    statuses = run(
                        spec,
                        engine=engine,
                        registry=registry or Registry.discover(),
                        clients={
                            "llm": client,
                            "systems": systems_factory(settings, spec, recorded_systems),
                        },
                        settings=settings,
                    )
                    # Record the actual pipeline state even when a later decision fails.
                    with repo_session(
                        engine, spec.run_id, fixture_mode=settings.fixture_mode
                    ) as repo:
                        manifest["run_status"] = repo.run_state()["status"]
                    can_decide = (
                        not replay_cache.missing
                        and not replay_cache.corrupt
                        and not recorded_systems.missing
                        and not recorded_systems.corrupt
                        and all(
                            s.status in {"succeeded", "degraded"}
                            and s.result is not None
                            and not s.result.errors
                            for s in statuses
                        )
                    )
                    if frozen_decisions and not can_decide:
                        manifest["decision_replay_skipped"] = True
                    for frozen in frozen_decisions if can_decide else ():
                        draft = decide(
                            engine, frozen.request, now=frozen.at, expected_draft=frozen.draft
                        )

                        manifest["decisions"].append(
                            {
                                "id": draft.decision.id,
                                "version": draft.decision.version,
                                "sha256": digest(draft.model_dump(mode="json")),
                                "option_id": draft.option.id,
                                "option_version": draft.option.version,
                                "input_version_hash": draft.decision.input_version_hash,
                                "decision": draft.decision.decision,
                                "dispatch_status": draft.decision.dispatch_status,
                                "simulated": draft.simulated,
                                "reservations": len(draft.reservations),
                            }
                        )
        finally:
            logging.disable(old_logging)
        manifest["network_attempts"] = len(denied)
        manifest["cache_misses"] = sorted(replay_cache.missing)
        manifest["cache_corrupt"] = sorted(replay_cache.corrupt)
        with repo_session(engine, spec.run_id, fixture_mode=settings.fixture_mode) as repo:
            manifest["run_status"] = repo.run_state()["status"]
            payloads = [
                (kind, record.model_dump(mode="json"))
                for kind, model in sorted(KINDS.items())
                for record in repo.list(model)
            ]
        with engine.connect() as conn:
            durable = (
                list(conn.execute(select(ledger.drafts.c.payload)).scalars())
                if inspect(conn).has_table(ledger.drafts.name)
                else []
            )
        durable.sort(key=lambda d: d["decision"]["id"])
        manifest["output_sha256"] = digest(
            [
                (kind, semantic_payload(kind, item))
                for kind, item in sorted(
                    payloads, key=lambda p: (p[0], p[1]["id"], p[1]["version"])
                )
            ]
            + [("LocalDraft", draft) for draft in durable]
        )
        manifest["ledger_sha256"] = digest(durable)

        manifest["artifacts"] = [
            {"kind": kind, "id": item["id"], "version": item["version"], "sha256": digest(item)}
            for kind, item in sorted(payloads, key=lambda p: (p[0], p[1]["id"], p[1]["version"]))
        ]
        manifest["raw_output_sha256"] = digest(
            sorted(payloads, key=lambda p: (p[0], p[1]["id"], p[1]["version"]))
            + [("LocalDraft", draft) for draft in durable]
        )
        manifest["artifact_counts"] = {
            kind: sum(k == kind for k, _ in payloads) for kind in sorted({k for k, _ in payloads})
        }

        manifest["modules"] = [
            {
                "id": item.module_id,
                "mode": item.mode,
                "status": item.status,
                "counts": item.result.counts if item.result else {},
                "has_errors": bool(item.result and item.result.errors),
            }
            for item in statuses
        ]
        manifest["missing_prerequisites"] = [
            m["id"]
            for m in manifest["modules"]
            if m["status"] in {"failed", "blocked"} or m["has_errors"]
        ]
        if (
            manifest["run_status"] in {"succeeded", "degraded"}
            and not denied
            and not replay_cache.missing
            and not replay_cache.corrupt
            and not recorded_systems.missing
            and not recorded_systems.corrupt
            and not manifest["missing_prerequisites"]
        ):
            manifest["status"] = manifest["run_status"]
    except Exception as error:
        manifest["error_type"] = type(error).__name__
        manifest["missing_prerequisites"].append(type(error).__name__)
    finally:
        manifest["network_attempts"] = len(denied)
        if replay_cache is not None:
            manifest["cache_misses"] = sorted(replay_cache.missing)
            manifest["cache_corrupt"] = sorted(replay_cache.corrupt)
        if recorded_systems is not None:
            manifest["systems_cache_misses"] = sorted(recorded_systems.missing)
            manifest["systems_cache_corrupt"] = sorted(recorded_systems.corrupt)
            if recorded_systems.missing or recorded_systems.corrupt:
                manifest["status"] = "failed"
                manifest["missing_prerequisites"].append("valid_systems_recordings")
        if denied:
            manifest["missing_prerequisites"].append("offline_network_or_process_operation")
        if replay_cache is not None and (replay_cache.missing or replay_cache.corrupt):
            manifest["missing_prerequisites"].append("valid_llm_recordings")
        if engine is not None:
            engine.dispose()
        (attempt / "manifest.json").write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n"
        )
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run-spec", "sources", "config", "cache", "workspace"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument(
        "--voice",
        type=Path,
        help="authorized voice source tree (required for src.voice)",
    )
    parser.add_argument(
        "--systems-cache",
        type=Path,
        help="recorded simulated stock/logistics GET responses",
    )
    parser.add_argument(
        "--decisions",
        type=Path,
        help="frozen requests and exact exported local drafts, pinned to snapshot hash/namespace",
    )
    args = parser.parse_args(argv)
    try:
        spec_path = allowed(args.run_spec)
        if spec_path.is_relative_to(args.workspace.resolve()):
            raise IsolationError("workspace contains snapshot")
        spec = RunSpec.model_validate_json(spec_path.read_text())
        result = rebuild(
            spec,
            sources=args.sources,
            config=args.config,
            cache=args.cache,
            workspace=args.workspace,
            voice=args.voice,
            systems_cache=args.systems_cache,
            decisions=args.decisions,
        )
    except Exception as error:
        result = {"format": 1, "status": "failed", "error_type": type(error).__name__}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] in {"succeeded", "degraded"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
