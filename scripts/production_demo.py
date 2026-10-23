"""Prepare, record and replay the redesign demo using the installed pipeline."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import timedelta
from email.message import EmailMessage
from email.policy import SMTP
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from prepare_core_demo import MODULES, copy_files
from replay_demo import allowed, digest, environment, rebuild

from tesseract.core.config import REPO_ROOT, Settings
from tesseract.core.contracts import ModuleSnapshot, RunSpec
from tesseract.core.db import connect
from tesseract.core.llm import LLMClient
from tesseract.core.orchestrator import run
from tesseract.core.registry import Registry
from tesseract.core.run_repo import repo_session
from tesseract.core.systems_cache import SystemsCache, systems_factory
from tesseract.modules.sources import business, docs, erp, external, systems_client


def prepare(output, profile, code_version=None):
    output = allowed(output)
    profile = allowed(profile)
    settings = Settings(_env_file=None)
    plan = yaml.safe_load(profile.read_text())
    split = yaml.safe_load((settings.config_dir / "eval_split.yaml").read_text())
    if not set(plan["stores"]) <= set(split["dev"]):
        raise ValueError("demo selection must contain dev stores only")
    registry = Registry.discover()
    manifests = {m.id: m for m in registry.manifests()}
    params = {
        "src.email": {
            "files": plan["emails"]
            + [f"{r['store']}/{r['filename']}" for r in plan["supplemental_emails"]]
        },
        "src.erp": {"history_days": 60},
        "src.external": {"window_days": 21},
        "sys.client": {
            "skus": ["I10919B00011-999", "I10919B00011-742", "J20931A00012-999"],
            "lookback_days": 0,
        },
        "ag.investigator": {"case_ids": plan["investigate"]},
    }
    calendar_path = "internal_comms/demo/decision_calendars.json"
    calendar_bytes = (
        json.dumps(
            {"synthetic": True, "calendars": plan["decision_calendars"]}, sort_keys=True, indent=2
        )
        + "\n"
    ).encode()
    calendar_hash = hashlib.sha256(calendar_bytes).hexdigest()
    params["int.cases"] = {
        "decision_calendars": [
            {
                **entry,
                "source_refs": [
                    {"uri": "dataset://" + calendar_path, "content_hash": "sha256:" + calendar_hash}
                ],
            }
            for entry in plan["decision_calendars"]
        ]
    }
    ids = tuple(i for i in MODULES if i != "out.reports") + (
        "src.business",
        "ins.product",
        "ag.investigator",
        "out.reports",
    )
    spec = RunSpec(
        run_id=plan["run_id"],
        scenario_id="synthetic-production-rehearsal",
        as_of=plan["as_of"],
        stores=plan["stores"],
        source_manifest_hash="pending",
        config_hash="pending",
        code_version=code_version
        or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
        mode="recorded",
        modules=tuple(ModuleSnapshot(manifest=manifests[i], params=params.get(i, {})) for i in ids),
        prompt_versions={
            "ing.extract": "extract_observations.v1",
            "int.link": "link_choice.v1",
            "ag.investigator": "investigator.v2",
        },
        model_versions={
            "chat": "google/gemma-4-26B-A4B-it",
            "ag.investigator": "glm-5.3-flash",
        },
        authorized_fixture_refs=(),
    )
    for snapshot in spec.modules:
        registry.resolve(snapshot)
    sources = allowed(settings.sources_dir)
    scope = erp.window(spec, params["src.erp"], sources_dir=sources)
    paths = ["erp/" + relative for relative, _ in erp._MASTER]
    for folder, prefix, table, _, _ in erp._FACTS:
        oldest = min(scope.oldest[table, store] for store in scope.stores)
        paths.extend(
            "erp/" + rel
            for rel, first, last in erp._files(sources, folder, prefix)
            if last >= oldest and first <= spec.as_of.date() + timedelta(days=1)
        )
    paths += ["store_emails/" + relative for relative in plan["emails"]]
    paths += [
        "reports/" + docs.DEFAULT_REPORT,
        systems_client.CROSSWALK_FILE,
        external.COVERAGE,
    ]
    coverage = external.coverage(sources)
    for store in spec.stores:
        city, provider = coverage.get(store, ("", ""))
        if provider == external.PROVIDER:
            paths.extend(
                p.relative_to(sources).as_posix()
                for p in (sources / external.FOLDER).glob(external.city_slug(city) + "_*.json")
            )
    _, _, refs = business.project(sources, spec.stores, spec.as_of)
    paths.extend(r.uri.removeprefix("dataset://") for r in refs)
    if output.is_relative_to(sources) or sources.is_relative_to(output) or output == REPO_ROOT:
        raise ValueError("output overlaps sources or repository")
    output.mkdir(parents=True, exist_ok=False)
    try:
        inventory = copy_files(sources, output / "sources", paths)
        calendar_output = output / "sources" / calendar_path
        calendar_output.parent.mkdir(parents=True, exist_ok=True)
        calendar_output.write_bytes(calendar_bytes)
        inventory.append((calendar_path, calendar_hash))
        for mail in plan["supplemental_emails"]:
            if mail["store"] not in spec.stores or Path(mail["filename"]).name != mail["filename"]:
                raise ValueError("invalid supplemental email location")
            message = EmailMessage(policy=SMTP)
            message["From"] = f"{mail['store'].lower()}.demo@synthetic.example"
            message["To"] = "hq@synthetic.example"
            message["Date"] = mail["date"]
            message["Message-ID"] = f"<{mail['filename']}@synthetic.example>"
            message["Subject"] = mail["subject"]
            message["X-Synthetic-Input"] = "DEMO-05 authored rehearsal input"
            message.set_content(mail["body"])
            raw = message.as_bytes()
            relative = f"store_emails/{mail['store']}/{mail['filename']}"
            path = output / "sources" / relative
            if path.exists():
                raise ValueError("supplemental mail would replace a source")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            inventory.append((relative, hashlib.sha256(raw).hexdigest()))
        inventory.sort()
        config_inventory = copy_files(
            settings.config_dir,
            output / "config",
            ("domain.yaml", "aliases.yaml", "eval_split.yaml", "report_metrics.yaml"),
        )
        spec = spec.model_copy(
            update={
                "source_manifest_hash": digest(inventory),
                "config_hash": digest(config_inventory),
            }
        )
        (output / "run-spec.json").write_text(spec.model_dump_json(indent=2) + "\n")
        (output / "input-manifest.json").write_text(
            json.dumps(
                {
                    "format": 1,
                    "status": "synthetic_dev_rehearsal",
                    "profile_sha256": hashlib.sha256(profile.read_bytes()).hexdigest(),
                    "sources": inventory,
                    "config": config_inventory,
                    "supplemental_emails": [
                        f"store_emails/{r['store']}/{r['filename']}"
                        for r in plan["supplemental_emails"]
                    ],
                    "limitations": [
                        "Synthetic dev demonstration, not hold-out evaluation.",
                        "Warehouse/logistics are the dataset's simulated systems, "
                        "read through the production adapter.",
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
    except Exception:
        shutil.rmtree(output)
        raise
    return spec


def record(candidate, keys_file):
    spec = RunSpec.model_validate_json((candidate / "run-spec.json").read_text())
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    dirty = subprocess.check_output(
        [
            "git",
            "status",
            "--porcelain",
            "--",
            "backend/tesseract",
            "backend/prompts",
            "scripts",
        ],
        cwd=REPO_ROOT,
        text=True,
    )
    if head != spec.code_version or dirty:
        raise ValueError("commit executable changes, then prepare a candidate at the executing SHA")
    for name, expected in (
        ("sources", spec.source_manifest_hash),
        ("config", spec.config_hash),
    ):
        actual = [
            (
                p.relative_to(candidate / name).as_posix(),
                hashlib.sha256(allowed(p).read_bytes()).hexdigest(),
            )
            for p in sorted((candidate / name).rglob("*"))
            if p.is_file()
        ]
        if digest(actual) != expected:
            raise ValueError("candidate input hash mismatch")
    settings = Settings(
        _env_file=None,
        sources_dir=candidate / "sources",
        config_dir=candidate / "config",
        data_dir=candidate / "runtime",
        fastweb_keys_file=keys_file,
        llm_mode="record",
        llm_max_calls=800,
        llm_max_tokens=1_500_000,
        llm_concurrency=8,
        llm_deadline_seconds=1800,
    )
    settings.data_dir.mkdir(exist_ok=False)
    engine = connect(settings.db_url)
    client = LLMClient(settings)
    systems = SystemsCache(settings.data_dir / "systems_cache")
    try:
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
        evidence = {
            "execution_sha": head,
            "run_id": spec.run_id,
            "status": state["status"],
            "published": state["published"],
            "modules": [s.model_dump(mode="json") for s in statuses],
            "llm_traces": client.traces,
            "systems_cache_misses": sorted(systems.missing),
            "systems_cache_corrupt": sorted(systems.corrupt),
        }
        (candidate / "recording-evidence.json").write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n"
        )
        print(
            json.dumps(
                {
                    "status": state["status"],
                    "published": state["published"],
                    "provider_calls": len(client.traces),
                }
            )
        )
        return (
            0
            if state["published"] and not any(s.result and s.result.errors for s in statuses)
            else 1
        )
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "record", "replay"))
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--profile", type=Path, default=REPO_ROOT / "config/production_demo.yaml")
    parser.add_argument("--keys-file", type=Path)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--code-version", help="frozen recording SHA when rebuilding inputs")
    args = parser.parse_args()
    candidate = allowed(args.candidate)
    if args.command == "prepare":
        spec = prepare(candidate, args.profile, args.code_version)
        print(json.dumps({"run_id": spec.run_id, "sources": spec.source_manifest_hash}))
        return 0
    if args.command == "record":
        return record(candidate, args.keys_file or Settings(_env_file=None).fastweb_keys_file)
    if args.workspace is None:
        parser.error("replay requires --workspace")
    spec = RunSpec.model_validate_json((candidate / "run-spec.json").read_text())
    result = rebuild(
        spec,
        sources=candidate / "sources",
        config=candidate / "config",
        cache=candidate / "runtime/llm_cache",
        systems_cache=candidate / "runtime/systems_cache",
        workspace=allowed(args.workspace),
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] in {"succeeded", "degraded"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
