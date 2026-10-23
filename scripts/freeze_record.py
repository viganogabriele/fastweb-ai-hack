"""Bind a freeze candidate's mechanically computable identities (protocol §3).

    record   write a new experiment record (exclusive create, never overwritten)
    append   write a post-freeze addendum chained to the previous file by SHA-256
    verify   rehash every live file a record chain binds; exit 1 on any drift

Run from the repository root: backend/.venv/bin/python scripts/freeze_record.py --help.
Paths in, JSON out; every output is created exclusively under data/. Answers, labels,
.env and .secrets are refused as inputs: label hash receipts are accepted only as
values that eval/ computed after the freeze. See docs/freeze-runbook.md.
"""

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

from eval.harness import ARTIFACTS, FrozenRun  # noqa: E402

FORMAT = 1
FORBIDDEN = {".env", ".secrets", "ground_truth", "generator", "email_context"}
LOCKFILES = ("backend/uv.lock", "web/package-lock.json", "scripts/openapi/package-lock.json")
CACHE_KINDS = ("llm", "asr", "systems")
STATUSES = ("recorded", "fixture", "unavailable")
# Non-secret Settings fields that change what a product run calls or how it replays.
SETTINGS_FIELDS = (
    "fastweb_base_url",
    "chat_model",
    "embed_model",
    "asr_base_url",
    "asr_model",
    "llm_mode",
    "llm_max_calls",
    "llm_max_tokens",
    "llm_concurrency",
    "mocks_base_url",
)
# Live master data the reading and lead-time scorers read (eval/reading.py, eval/lead_time.py).
CATALOG = (
    "generated/sources/erp/master_data/stores.csv",
    "generated/sources/erp/master_data/sku_colour.csv",
    "generated/sources/erp/master_data/sku_size_ean.csv",
)
SPLIT = "config/eval_split.yaml"
# Baseline warm-up (eval/baselines.py): sales history 1 + window 3 + history 28 days,
# plus one day of margin for shifted windows; stock arming snapshot from start - 1.
SALES_WARMUP_DAYS = 33
STOCK_WARMUP_DAYS = 2


class RecordError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_digest(pairs) -> str:
    """Same canonical form as replay_demo.digest over (path, sha256) pairs (RunSpec hashes)."""
    return sha256(
        json.dumps(
            sorted([path, digest] for path, digest in pairs),
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode()
    )


def guarded(root: Path, path) -> Path:
    """Refuse hidden-answer and secret locations, before and after resolving links."""
    path = Path(path)
    path = (path if path.is_absolute() else root / path).absolute()
    resolved = path.resolve()
    for candidate in (path, resolved):
        parts = candidate.parts
        if any(p in FORBIDDEN or p.endswith("_notes.md") for p in parts):
            raise RecordError(f"forbidden input location: {path}")
        if any(a == "eval" and b == "labels" for a, b in zip(parts, parts[1:], strict=False)):
            raise RecordError(f"forbidden input location: {path}")
    if not resolved.is_relative_to(root):
        raise RecordError(f"input outside the repository: {path}")
    return resolved


def relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def file_entry(root: Path, path) -> dict:
    path = guarded(root, path)
    if not path.is_file():
        raise RecordError(f"missing file: {relative(root, path)}")
    data = path.read_bytes()
    return {"path": relative(root, path), "sha256": sha256(data), "bytes": len(data)}


def inventory(root: Path, paths) -> dict:
    unique = {entry["path"]: entry for entry in (file_entry(root, p) for p in paths)}
    files = [unique[path] for path in sorted(unique)]
    return {
        "count": len(files),
        "aggregate_sha256": tree_digest((e["path"], e["sha256"]) for e in files),
        "files": files,
    }


def tree_files(root: Path, directory) -> list[Path]:
    directory = guarded(root, directory)
    if not directory.is_dir():
        raise RecordError(f"missing directory: {directory}")
    return sorted(p for p in directory.rglob("*") if p.is_file())


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def dirty_paths(root: Path) -> list[str]:
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, text=True
    )
    return [line[3:] for line in status.splitlines()]


def version(*command: str) -> str | None:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def runtime() -> dict:
    return {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "uv": version("uv", "--version"),
        "node": version("node", "--version"),
        "npm": version("npm", "--version"),
    }


def settings_identity() -> dict:
    """Model ids/endpoints from the product Settings; keys are never read or recorded."""
    from tesseract.core.config import Settings

    settings = Settings()
    return {name: getattr(settings, name) for name in SETTINGS_FIELDS}


def candidate(root, *, expected_sha, evaluator_sha, allow_dirty, protocol, reviewer, approved_at):
    head = git(root, "rev-parse", "HEAD")
    if expected_sha and expected_sha != head:
        raise RecordError(f"candidate {expected_sha} is not the checked-out HEAD {head}")
    dirty = dirty_paths(root)
    if dirty and not allow_dirty:
        raise RecordError("working tree is dirty; commit, or pass --allow-dirty (recorded)")
    tag = subprocess.run(
        ["git", "rev-parse", "-q", "--verify", "refs/tags/freeze-g3^{commit}"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    return {
        "sha": head,
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
        "clean": not dirty,
        "allow_dirty": allow_dirty,
        "dirty_paths": dirty,
        "freeze_tag": {"name": "freeze-g3", "target": tag or None},
        "evaluator_sha": evaluator_sha or head,
        "evaluator_tree": git(root, "rev-parse", f"{evaluator_sha or head}:eval"),
        "protocol": file_entry(root, protocol),
        "reviewer": reviewer,
        "approved_at": approved_at,
    }


def run_spec_identity(root: Path, path) -> dict:
    entry = file_entry(root, path)
    spec = json.loads((root / entry["path"]).read_text(encoding="utf-8"))
    prompts = {}
    for module, name in sorted(spec.get("prompt_versions", {}).items()):
        prompt = root / "backend/prompts" / f"{name}.md"
        prompts[module] = file_entry(root, prompt) if prompt.is_file() else {"missing": name}
    return {
        **entry,
        **{
            key: spec.get(key)
            for key in (
                "run_id",
                "scenario_id",
                "as_of",
                "stores",
                "mode",
                "code_version",
                "schema_version",
                "source_manifest_hash",
                "config_hash",
                "model_versions",
                "prompt_versions",
                "authorized_fixture_refs",
            )
        },
        "prompt_files": prompts,
        "modules": [
            {
                "id": m["manifest"]["id"],
                "version": m["manifest"]["version"],
                "enabled": m["manifest"].get("enabled"),
                "mode": m["manifest"].get("mode"),
                "params_sha256": sha256(
                    json.dumps(
                        m.get("params") or {}, sort_keys=True, separators=(",", ":")
                    ).encode()
                ),
            }
            for m in spec.get("modules", [])
        ],
    }


def input_manifest(root: Path, path, sources_root: Path, config_root: Path):
    """DEMO-02 input-manifest.json: paths relative to the source/config roots, with hashes."""
    entry = file_entry(root, path)
    manifest = json.loads((root / entry["path"]).read_text(encoding="utf-8"))
    sources = [sources_root / name for name, _ in manifest["sources"]]
    config = [config_root / name for name, _ in manifest["config"]]
    expected = {
        relative(root, base / name): digest
        for base, key in ((sources_root, "sources"), (config_root, "config"))
        for name, digest in manifest[key]
    }
    return entry, sources, config, expected


def evaluator_inputs(root: Path, start: date, end: date) -> dict:
    """Live files the hold-out scorers read, including warm-up, absent ones recorded too."""
    erp = "generated/sources/erp"
    stock, sales = [], set()
    day = start - timedelta(days=STOCK_WARMUP_DAYS)
    while day <= end + timedelta(days=1):
        stock.append(f"{erp}/inventory/store_stock_daily/stock_eod_{day.isoformat()}.csv")
        day += timedelta(days=1)
    day = start - timedelta(days=SALES_WARMUP_DAYS)
    while day <= end + timedelta(days=1):
        sales.add(f"{erp}/sales/daily_store_sku/sales_daily_{day:%Y_%m}.csv")
        day += timedelta(days=1)
    wanted = [*CATALOG, *stock, *sorted(sales)]
    present = [p for p in wanted if (root / p).is_file()]
    return {
        "window": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "sales_warmup_days": SALES_WARMUP_DAYS,
            "stock_warmup_days": STOCK_WARMUP_DAYS,
        },
        "split": file_entry(root, SPLIT),
        "inventory": inventory(root, present),
        "absent": sorted(set(wanted) - set(present)),
    }


def cache_inventory(root: Path, kind: str, directory) -> dict:
    """Validate every content-addressed envelope (tesseract.core.cache) and hash its bytes."""
    directory = guarded(root, directory)
    files, models, invalid = [], Counter(), []
    for path in tree_files(root, directory):
        name = path.relative_to(directory).as_posix()
        data = path.read_bytes()
        try:
            envelope = json.loads(data)
            key = envelope["key"]
            response = envelope["response"]
            canonical = json.dumps(
                response, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
            if (
                envelope["version"] != 1
                or name != f"{key[:2]}/{key}.json"
                or envelope["checksum"] != sha256(canonical.encode())
            ):
                raise ValueError
        except (ValueError, KeyError, TypeError):
            invalid.append(name)
            continue
        models[response.get("model", "unspecified")] += 1
        files.append(
            {"path": relative(root, path), "key": key, "sha256": sha256(data), "bytes": len(data)}
        )
    if invalid:
        raise RecordError(f"{kind} cache {directory}: invalid entries {invalid[:5]}")
    return {
        "kind": kind,
        "directory": relative(root, directory),
        "entries": len(files),
        "aggregate_sha256": tree_digest((e["path"], e["sha256"]) for e in files),
        "models": dict(sorted(models.items())),
        "files": files,
    }


def components(caches: list[dict], declared: dict[str, tuple[str, str]], specs: list[dict]):
    """Recorded vs fixture vs unavailable, from the caches and RunSpec mode unless declared."""
    fixture = any(s["mode"] == "fixture" or s["authorized_fixture_refs"] for s in specs)
    result = {}
    for kind in CACHE_KINDS:
        entries = sum(c["entries"] for c in caches if c["kind"] == kind)
        if entries:
            result[kind] = {
                "status": "fixture" if fixture else "recorded",
                "reason": f"{entries} validated cache entries",
            }
        else:
            result[kind] = {"status": "unavailable", "reason": "no cache entries supplied"}
    for name, (status, reason) in declared.items():
        result[name] = {"status": status, "reason": reason, "declared": True}
    return dict(sorted(result.items()))


def export_group(root: Path, group: str, directory) -> list[dict]:
    directory = guarded(root, directory)
    result = []
    for kind in ARTIFACTS:
        entry = file_entry(root, directory / f"{kind}.json")
        rows = json.loads((root / entry["path"]).read_text(encoding="utf-8"))
        if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
            raise RecordError(f"{entry['path']} must be a JSON array of objects")
        by_kind, by_origin, by_store = Counter(), Counter(), Counter()
        for row in rows:
            payload = row.get("payload") if isinstance(row.get("payload"), dict) else row
            by_kind[row.get("kind") or kind] += 1
            by_origin[row.get("as_of") or payload.get("as_of") or "unspecified"] += 1
            by_store[payload.get("store_id") or "unspecified"] += 1
        result.append(
            {
                "group": group,
                "kind": kind,
                **entry,
                "rows": len(rows),
                "by_kind": dict(sorted(by_kind.items())),
                "by_origin": dict(sorted(by_origin.items())),
                "by_store": dict(sorted(by_store.items())),
            }
        )
    return result


def bundle_entry(root: Path, path, expected: str | None) -> dict:
    """Bind a harness bundle by its manifest digest after FrozenRun's full verification."""
    path = guarded(root, path)
    manifest = sha256((path / "manifest.json").read_bytes())
    if expected and expected != manifest:
        raise RecordError(f"bundle {path}: manifest digest {manifest} != {expected}")
    run = FrozenRun(path, manifest)
    protocol = run.manifest["protocol"]
    return {
        "path": relative(root, path),
        "manifest_sha256": manifest,
        "run_id": protocol["run_id"],
        "split": protocol["split"],
        "stores": protocol["stores"],
        "origins": len(protocol["origins"]),
        "counts": {kind: len(rows) for kind, rows in run.artifacts.items()},
        "files": [{k: e[k] for k in ("category", "path", "sha256")} for e in run.manifest["files"]],
    }


def cross_check(record: dict, bundles: list[dict]) -> list[str]:
    """Bundles must copy recorded exports and hash sources the record also binds."""
    problems = []
    exports = {e["sha256"] for e in record.get("exports", [])}
    sources = {e["path"]: e["sha256"] for e in record["inputs"]["sources"]["files"]}
    sources |= {e["path"]: e["sha256"] for e in record["inputs"]["evaluator"]["inventory"]["files"]}
    for bundle in bundles:
        for entry in bundle["files"]:
            if entry["category"] in ARTIFACTS and exports and entry["sha256"] not in exports:
                problems.append(f"{bundle['path']}: {entry['category']} is not a recorded export")
            if entry["category"] == "sources" and sources.get(entry["path"]) != entry["sha256"]:
                problems.append(f"{bundle['path']}: source {entry['path']} not in the record")
    return problems


def pairs(values: list[str], what: str) -> list[tuple[str, str]]:
    result = []
    for value in values:
        name, sep, rest = value.partition("=")
        if not sep or not name or not rest:
            raise RecordError(f"{what} must be NAME=VALUE: {value!r}")
        result.append((name, rest))
    return result


def label_receipts(values: list[str]) -> dict:
    receipts = {}
    for name, value in pairs(values, "--label-sha"):
        if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise RecordError(f"--label-sha {name}: expected a lowercase SHA-256 hex digest")
        receipts[name] = value
    return receipts


def evidence(root: Path, values: list[str]) -> dict:
    return {name: file_entry(root, path) for name, path in pairs(values, "--evidence")}


def bundles(root: Path, values: list[str]) -> list[dict]:
    result = []
    for value in values:
        path, _, expected = value.partition("=")
        result.append(bundle_entry(root, path, expected or None))
    return result


def build_record(root: Path, args) -> dict:
    sources_root = guarded(root, args.sources_root)
    config_root = guarded(root, args.config_root)
    lists = [file_entry(root, path) for path in args.source_list]
    sources = [Path(p) for e in lists for p in (root / e["path"]).read_text().splitlines() if p]
    sources += [Path(p) for p in args.source]
    config = [Path(p) for p in args.config]
    manifests, expected = [], {}
    for path in args.input_manifest:
        entry, more_sources, more_config, hashes = input_manifest(
            root, path, sources_root, config_root
        )
        manifests.append(entry)
        sources += more_sources
        config += more_config
        expected |= hashes
    if not sources:
        raise RecordError("provide the consumed sources (--source-list/--source/--input-manifest)")
    for path in sources:
        if not guarded(root, path).is_relative_to(guarded(root, "generated/sources")):
            raise RecordError(f"sources may come only from generated/sources: {path}")
    if not config:
        config = tree_files(root, config_root)
    source_inventory = inventory(root, sources)
    config_inventory = inventory(root, config)
    drift = [
        path
        for e in (*source_inventory["files"], *config_inventory["files"])
        if (path := e["path"]) in expected and expected[path] != e["sha256"]
    ]
    if drift:
        raise RecordError(f"live inputs differ from the input manifest: {drift[:5]}")
    for e in source_inventory["files"]:
        if e["path"].startswith(relative(root, sources_root) + "/"):
            e["source_relative"] = e["path"][len(relative(root, sources_root)) + 1 :]
    specs = [run_spec_identity(root, p) for p in args.run_spec]
    run_root_digests = {
        "sources": tree_digest(
            (e["source_relative"], e["sha256"])
            for e in source_inventory["files"]
            if "source_relative" in e
        ),
        "config": tree_digest(
            (Path(e["path"]).relative_to(relative(root, config_root)).as_posix(), e["sha256"])
            for e in config_inventory["files"]
            if Path(e["path"]).is_relative_to(relative(root, config_root))
        ),
    }
    for spec in specs:
        spec["matches_recorded_inputs"] = {
            "sources": spec["source_manifest_hash"] == run_root_digests["sources"],
            "config": spec["config_hash"] == run_root_digests["config"],
        }
    caches = [cache_inventory(root, kind, path) for kind, path in pairs(args.cache, "--cache")]
    for cache in caches:
        if cache["kind"] not in CACHE_KINDS:
            raise RecordError(f"cache kind must be one of {CACHE_KINDS}")
    declared = {}
    for name, value in pairs(args.component, "--component"):
        status, _, reason = value.partition(":")
        if status not in STATUSES or not reason:
            raise RecordError(f"--component {name}: expected STATUS:REASON, STATUS in {STATUSES}")
        declared[name] = (status, reason)
    record = {
        "format": FORMAT,
        "kind": "record",
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "candidate": candidate(
            root,
            expected_sha=args.candidate_sha,
            evaluator_sha=args.evaluator_sha,
            allow_dirty=args.allow_dirty,
            protocol=args.protocol,
            reviewer=args.reviewer,
            approved_at=args.approved_at,
        ),
        "integration": {
            "make_check_log": file_entry(root, args.make_check_log)
            if args.make_check_log
            else None,
            "gate_audit": file_entry(root, args.gate_audit) if args.gate_audit else None,
            "evidence": evidence(root, args.evidence),
        },
        "runtime": runtime(),
        "lockfiles": [file_entry(root, p) for p in LOCKFILES if (root / p).is_file()],
        "product_identity": {
            "settings": settings_identity(),
            "run_specs": specs,
            "prompts": inventory(root, tree_files(root, "backend/prompts")),
            "configuration": config_inventory,
            "run_root_digests": run_root_digests,
        },
        "inputs": {
            "source_lists": lists,
            "input_manifests": manifests,
            "sources": source_inventory,
            "evaluator": evaluator_inputs(root, args.window[0], args.window[1]),
        },
        "caches": {
            "replay_miss_policy": "replay: a cache miss is an error, never a provider call",
            "inventories": caches,
            "components": components(caches, declared, specs),
        },
        "exports": [
            e for g, d in pairs(args.exports, "--exports") for e in export_group(root, g, d)
        ],
        "bundles": bundles(root, args.bundle),
        "post_freeze": {"label_receipts": label_receipts(args.label_sha), "notes": args.note},
    }
    problems = cross_check(record, record["bundles"])
    if problems:
        raise RecordError("; ".join(problems))
    return record


def write_new(root: Path, path, data: dict) -> str:
    path = Path(path)
    path = (path if path.is_absolute() else root / path).absolute()
    if not path.is_relative_to(root / "data"):
        raise RecordError("experiment records must be written under data/")
    body = (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:  # Append-only: an existing record is never replaced.
        stream.write(body)
    return sha256(body)


def load_chain(root: Path, paths) -> list[dict]:
    """The record followed by its addenda; each addendum names its predecessor's digest."""
    chain, previous = [], None
    for path in paths:
        entry = file_entry(root, path)
        data = json.loads((root / entry["path"]).read_text(encoding="utf-8"))
        if data.get("format") != FORMAT:
            raise RecordError(f"{entry['path']}: unsupported record format")
        if previous is None and data.get("kind") != "record":
            raise RecordError("the chain must start with a record")
        if previous is not None and data.get("parent") != previous:
            raise RecordError(f"{entry['path']}: parent digest does not match {previous['path']}")
        chain.append(data)
        previous = {"path": entry["path"], "sha256": entry["sha256"]}
    return chain


def bound_files(value):
    """Every file entry (path + sha256 + bytes) anywhere in a record."""
    if isinstance(value, dict):
        if {"path", "sha256", "bytes"} <= value.keys():
            yield value
        for child in value.values():
            yield from bound_files(child)
    elif isinstance(value, list):
        for child in value:
            yield from bound_files(child)


def verify(root: Path, chain: list[dict]) -> dict:
    drift, warnings, checked = [], [], 0
    for document in chain:
        for entry in bound_files(document):
            checked += 1
            path = root / entry["path"]
            try:
                current = sha256(guarded(root, path).read_bytes())
            except (OSError, RecordError):
                drift.append(f"missing: {entry['path']}")
                continue
            if current != entry["sha256"]:
                drift.append(f"changed: {entry['path']}")
        for cache in document.get("caches", {}).get("inventories", []):
            live = (
                {relative(root, p) for p in tree_files(root, cache["directory"])}
                if (root / cache["directory"]).is_dir()
                else set()
            )
            extra = live - {e["path"] for e in cache["files"]}
            drift += [f"added cache entry: {p}" for p in sorted(extra)]
        evaluator = document.get("inputs", {}).get("evaluator")
        if evaluator:
            drift += [f"appeared: {p}" for p in evaluator["absent"] if (root / p).exists()]
        for bundle in document.get("bundles", []):
            try:
                FrozenRun(root / bundle["path"], bundle["manifest_sha256"])
            except (OSError, ValueError, KeyError) as error:
                drift.append(f"bundle {bundle['path']}: {error}")
    record = chain[0]
    head = git(root, "rev-parse", "HEAD")
    if head not in {record["candidate"]["sha"], record["candidate"]["evaluator_sha"]}:
        warnings.append(f"HEAD {head} is neither the candidate nor the evaluator SHA")
    if dirty_paths(root):
        warnings.append("working tree is dirty")
    if runtime()["python"] != record["runtime"]["python"]:
        warnings.append("Python version differs from the record")
    return {
        "format": FORMAT,
        "kind": "verification",
        "verified_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "head": head,
        "chain": [d.get("parent") for d in chain[1:]],
        "status": "drift" if drift else "ok",
        "files_checked": checked,
        "drift": drift,
        "warnings": warnings,
    }


def summary(record: dict, digest: str) -> dict:
    inputs = record.get("inputs", {})
    return {
        "sha256": digest,
        "candidate": record.get("candidate", {}).get("sha"),
        "sources": inputs.get("sources", {}).get("count"),
        "evaluator_inputs": inputs.get("evaluator", {}).get("inventory", {}).get("count"),
        "caches": {
            c["kind"]: c["entries"] for c in record.get("caches", {}).get("inventories", [])
        },
        "exports": len(record.get("exports", [])),
        "bundles": [b["manifest_sha256"] for b in record.get("bundles", [])],
    }


def parser() -> argparse.ArgumentParser:
    main = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = main.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record", help="write a new experiment record")
    rec.add_argument("--output", type=Path, required=True)
    rec.add_argument("--candidate-sha", help="refuse unless it equals the checked-out HEAD")
    rec.add_argument("--evaluator-sha", help="evaluator commit if different from the candidate")
    rec.add_argument("--allow-dirty", action="store_true", help="record a dirty tree (flagged)")
    rec.add_argument("--protocol", type=Path, default=Path("docs/holdout-evaluation-protocol.md"))
    rec.add_argument("--sources-root", type=Path, default=Path("generated/sources"))
    rec.add_argument("--config-root", type=Path, default=Path("config"))
    rec.add_argument(
        "--source-list",
        action="append",
        default=[],
        help="newline-separated repository-relative source paths (§5.1)",
    )
    rec.add_argument("--source", action="append", default=[])
    rec.add_argument(
        "--input-manifest",
        action="append",
        default=[],
        help="DEMO-02 input-manifest.json; its hashes must match live files",
    )
    rec.add_argument(
        "--config",
        action="append",
        default=[],
        help="configuration file; default every file under --config-root",
    )
    rec.add_argument("--run-spec", action="append", default=[])
    rec.add_argument(
        "--window",
        nargs=2,
        type=date.fromisoformat,
        metavar=("START", "END"),
        default=[date(2026, 8, 31), date(2026, 10, 21)],
        help="evaluation period for the scorers' live baseline inputs",
    )
    rec.add_argument("--cache", action="append", default=[], help="KIND=DIR, KIND llm|asr|systems")
    rec.add_argument(
        "--component",
        action="append",
        default=[],
        help="NAME=recorded|fixture|unavailable:REASON (explicit declaration)",
    )
    rec.add_argument(
        "--exports",
        action="append",
        default=[],
        help="GROUP=DIR with predictions.json, cases.json, options.json",
    )
    rec.add_argument("--make-check-log", type=Path)
    rec.add_argument("--gate-audit", type=Path, help="#226 gate audit disposition")
    for command in (rec, app := sub.add_parser("append", help="write a chained addendum")):
        command.add_argument("--reviewer", help="human reviewer of the candidate/freeze")
        command.add_argument("--approved-at", help="aware ISO timestamp of the human approval")
        command.add_argument("--bundle", action="append", default=[], help="DIR[=MANIFEST_SHA]")
        command.add_argument("--evidence", action="append", default=[], help="NAME=PATH")
        command.add_argument(
            "--label-sha",
            action="append",
            default=[],
            help="NAME=SHA256 computed by eval/ after the freeze",
        )
        command.add_argument("--note", action="append", default=[])
    app.add_argument(
        "--record",
        type=Path,
        nargs="+",
        required=True,
        help="the record and its earlier addenda, in order",
    )
    app.add_argument("--output", type=Path, required=True)
    ver = sub.add_parser("verify", help="rehash live files against a record chain")
    ver.add_argument("--record", type=Path, nargs="+", required=True)
    ver.add_argument("--output", type=Path, help="write the verification log (exclusive)")
    return main


def main(argv=None, root: Path = ROOT) -> int:
    args = parser().parse_args(argv)
    root = root.resolve()
    try:
        approved_at = getattr(args, "approved_at", None)
        if approved_at and datetime.fromisoformat(approved_at).utcoffset() is None:
            raise RecordError("--approved-at needs an explicit time zone")
        if args.command == "record":
            record = build_record(root, args)
            print(json.dumps(summary(record, write_new(root, args.output, record)), indent=2))
        elif args.command == "append":
            chain = load_chain(root, args.record)
            last = file_entry(root, args.record[-1])
            added = bundles(root, args.bundle)
            problems = cross_check(chain[0], added)
            if problems:
                raise RecordError("; ".join(problems))
            addendum = {
                "format": FORMAT,
                "kind": "addendum",
                "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "parent": {"path": last["path"], "sha256": last["sha256"]},
                "candidate_sha": chain[0]["candidate"]["sha"],
                "approval": {"reviewer": args.reviewer, "approved_at": args.approved_at},
                "bundles": added,
                "evidence": evidence(root, args.evidence),
                "post_freeze": {
                    "label_receipts": label_receipts(args.label_sha),
                    "notes": args.note,
                },
            }
            print(json.dumps(summary(addendum, write_new(root, args.output, addendum)), indent=2))
        else:
            report = verify(root, load_chain(root, args.record))
            if args.output:
                report["sha256"] = write_new(root, args.output, report)
            print(json.dumps(report, indent=2))
            return 0 if report["status"] == "ok" else 1
    except (RecordError, FileExistsError) as error:
        print(f"freeze_record: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
