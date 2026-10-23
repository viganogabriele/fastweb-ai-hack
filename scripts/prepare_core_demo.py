"""Freeze a small, source-backed dev integration candidate; never preload projections.

Run from the repository root. Output must not exist. This is a dev rehearsal,
not a hold-out evaluation or a release freeze. Add explicit --case-id values after
inspecting the discovery candidate; a changed snapshot requires new recordings.
"""

import argparse
import csv
import hashlib
import json
import shutil
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from replay_demo import allowed, digest

from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import ModuleSnapshot, RunSpec
from tesseract.core.registry import Registry
from tesseract.modules.sources import docs, erp, systems_client

STORES = ("MIL01", "MIL02", "MUN01", "NYC01")
EMAILS = (
    "MIL01/20260918_2115_MIL01.eml",
    "MIL01/20260918_2207_MIL01_corr.eml",
    "MIL01/20261002_2112_MIL01.eml",
    "MIL01/20261002_2113_MIL01_dup.eml",
    "MIL01/20261009_1035_MIL01.eml",
    "MIL01/20261009_1847_MIL01_re1.eml",
    "MIL02/20261009_1811_MIL02.eml",
    "NYC01/20260906_1837_NYC01.eml",
    "NYC01/20261004_1829_NYC01.eml",
    "NYC01/20261004_1858_NYC01_corr.eml",
    "NYC01/20261014_2248_NYC01_ooo.eml",
    "MUN01/20261014_2016_MUN01.eml",
)
MODULES = (
    "src.email",
    "src.erp",
    "src.docs",
    "ing.metrics",
    "src.external",
    "ing.extract",
    "int.link",
    "int.dedup",
    "sys.client",
    "int.cases",
    "int.context",
    "fc.baseline",
    "fc.overlay",
    "act.options",
    "out.reports",
)


def copy_files(root, destination, relatives):
    inventory = []
    for relative in sorted({str(p) for p in relatives}):
        source = allowed(root / relative)
        if not source.is_relative_to(root.resolve()):
            raise ValueError("source escapes authorized root")
        data = source.read_bytes()
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        inventory.append((relative, hashlib.sha256(data).hexdigest()))
    return inventory


def prepare(output, *, sources, config, code_version, case_ids=()):
    output, sources, config = (allowed(p) for p in (output, sources, config))
    if any(output.is_relative_to(p) or p.is_relative_to(output) for p in (sources, config)):
        raise ValueError("output overlaps inputs")
    # Prevent a partially prepared candidate from being mistaken for an approved one.
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    try:
        registry = Registry.discover()
        manifests = {m.id: m for m in registry.manifests()}
        params = {
            "src.email": {"files": list(EMAILS)},
            "src.erp": {"history_days": 60},
            "sys.client": {"skus": ["I10919B00011-999", "I10919B00011-742"], "lookback_days": 0},
            "src.external": {"window_days": 21},
        }
        ids = MODULES
        if case_ids:
            ids = tuple(i for i in ids if i != "out.reports") + ("ag.investigator", "out.reports")
            params["ag.investigator"] = {"case_ids": list(case_ids)}
        spec = RunSpec(
            run_id="core-dev-candidate",
            scenario_id="historical",
            as_of="2026-10-22T20:00:00Z",
            stores=STORES,
            source_manifest_hash="pending",
            config_hash="pending",
            code_version=code_version,
            mode="recorded",
            modules=tuple(
                ModuleSnapshot(manifest=manifests[i], params=params.get(i, {})) for i in ids
            ),
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
        # These two files are read before copy_files() checks the selected inventory.
        # Validate their lexical ancestors first, before a link could expose hidden inputs.
        stores_path = allowed(sources / "erp/master_data/stores.csv")
        split_path = allowed(config / "eval_split.yaml")
        scope = erp.window(spec, params["src.erp"], sources_dir=sources)
        paths = ["erp/" + relative for relative, _ in erp._MASTER]
        for folder, prefix, table, _, _ in erp._FACTS:
            oldest = min(scope.oldest[table, store] for store in scope.stores)
            newest = spec.as_of.date() + timedelta(days=1)
            paths.extend(
                "erp/" + rel
                for rel, first, last in erp._files(sources, folder, prefix)
                if last >= oldest and first <= newest
            )
        paths += ["store_emails/" + f for f in EMAILS]
        paths += [
            "reports/" + docs.DEFAULT_REPORT,
            systems_client.CROSSWALK_FILE,
            "external/weather/coverage_by_city.csv",
        ]
        paths += [
            p.relative_to(sources).as_posix()
            for city in ("milano", "muenchen")
            for p in (sources / "external/weather/eu_meteoarchive").glob(city + "_*.json")
        ]
        # Dev sample is checked against the authoritative split before any model call.
        import yaml

        split = yaml.safe_load(split_path.read_text())
        if not set(STORES) <= set(split["dev"]):
            raise ValueError("candidate contains a non-dev store")
        with stores_path.open() as stream:
            known = {r["store_id"] for r in csv.DictReader(stream)}
        if not set(STORES) <= known:
            raise ValueError("unknown store")
        source_files = copy_files(sources, output / "sources", paths)
        config_files = copy_files(
            config,
            output / "config",
            (
                "domain.yaml",
                "aliases.yaml",
                "eval_split.yaml",
                "report_metrics.yaml",
            ),
        )
        spec = spec.model_copy(
            update={
                "source_manifest_hash": digest(source_files),
                "config_hash": digest(config_files),
            }
        )
        (output / "run-spec.json").write_text(spec.model_dump_json(indent=2) + "\n")
        (output / "input-manifest.json").write_text(
            json.dumps(
                {
                    "format": 1,
                    "status": "candidate_unapproved",
                    "stores": STORES,
                    "as_of": spec.as_of.isoformat(),
                    "code_version": code_version,
                    "sources": source_files,
                    "config": config_files,
                    "limitations": [
                        "Historical dev rehearsal only; no hold-out metrics.",
                        "Voice and prior fixture investigator traces are separate evidence.",
                    ],
                },
                sort_keys=True,
                indent=2,
            )
            + "\n"
        )
        return spec
    except Exception:
        shutil.rmtree(output)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sources", type=Path, default=REPO_ROOT / "generated/sources")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "config")
    parser.add_argument("--code-version", required=True)
    parser.add_argument("--case-id", action="append", default=[])
    args = parser.parse_args()
    spec = prepare(
        args.output,
        sources=args.sources,
        config=args.config,
        code_version=args.code_version,
        case_ids=args.case_id,
    )
    print(
        json.dumps(
            {
                "run_id": spec.run_id,
                "source_manifest_hash": spec.source_manifest_hash,
                "config_hash": spec.config_hash,
                "modules": len(spec.modules),
            }
        )
    )


if __name__ == "__main__":
    main()
