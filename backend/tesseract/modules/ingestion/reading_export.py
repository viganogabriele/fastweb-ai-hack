"""EVL-02 product side: run the reading pipeline on a preselected mail sample and export it.

Not a registered module (no ``MANIFEST``): a driver over the orchestrator. ``spec`` freezes a
``RunSpec`` with ``src.email`` restricted to the sample files, ``src.erp`` (catalog for the
links), ``ing.extract`` and ``int.link``. ``run`` executes that spec under a new run id and
writes the run's documents, segments, observations, links and module results as one JSON array
of ``{"kind", "payload"}`` records, the format the ``eval`` harness freezes.

The cache identity of LLM calls excludes the run id: record once (``LLM_MODE=record``, needs
the Fastweb keys), then produce the evaluated export in replay under the isolated launcher,
which cannot read ``.secrets/``, ``generated/ground_truth/`` or ``eval/``::

    backend/.venv/bin/python -m eval product -- -m tesseract.modules.ingestion.reading_export \\
        run --run-spec data/eval/evl02/run_spec.json --run-id evl02-replay \\
        --out data/exports/evl02-dev
"""

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

from tesseract.core.config import get_settings
from tesseract.core.contracts import (
    EntityLink,
    ModuleSnapshot,
    Observation,
    RunSpec,
    Segment,
    SourceDocument,
)
from tesseract.core.db import connect
from tesseract.core.orchestrator import run as run_spec
from tesseract.core.registry import Registry
from tesseract.core.run_repo import repo_session
from tesseract.modules.ingestion import extract
from tesseract.modules.integration import link

MODULES = ("src.email", "src.erp", "ing.extract", "int.link")
# The links need the master rows only; one day of daily facts keeps the load small.
ERP_PARAMS = {"history_days": 1}
CONFIG_FILES = ("aliases.yaml", "domain.yaml")
MASTER_FILES = ("stores.csv", "sku_colour.csv", "sku_size_ean.csv", "store_assortment.csv")
EXPORTED = (SourceDocument, Segment, Observation, EntityLink)


def _digest(root: Path, paths: list[Path]) -> str:
    """Hash of names relative to ``root`` and contents: the same in every checkout."""
    entries = [
        f"{p.relative_to(root).as_posix()}:{hashlib.sha256(p.read_bytes()).hexdigest()}"
        for p in paths
    ]
    return "sha256:" + hashlib.sha256("\n".join(sorted(entries)).encode()).hexdigest()


def _prompt_version(path: Path) -> str:
    return f"{path.stem}:{hashlib.sha256(path.read_bytes()).hexdigest()[:12]}"


def build_spec(files: list[str], as_of: datetime, run_id: str, code_version: str) -> RunSpec:
    settings = get_settings()
    manifests = {m.id: m for m in Registry.discover().manifests()}
    params = {"src.email": {"files": files}, "src.erp": ERP_PARAMS}
    emails = settings.sources_dir / "store_emails"
    master = settings.sources_dir / "erp" / "master_data"
    return RunSpec(
        run_id=run_id,
        scenario_id="historical",
        as_of=as_of,
        stores=tuple(sorted({f.split("/")[0] for f in files})),
        source_manifest_hash=_digest(
            settings.sources_dir,
            [emails / f for f in files] + [master / name for name in MASTER_FILES],
        ),
        config_hash=_digest(
            settings.config_dir, [settings.config_dir / name for name in CONFIG_FILES]
        ),
        code_version=code_version,
        mode="live",
        modules=tuple(
            ModuleSnapshot(manifest=manifests[m], params=params.get(m, {})) for m in MODULES
        ),
        prompt_versions={
            "extract": _prompt_version(extract.PROMPT_PATH),
            "link": _prompt_version(link.PROMPT_PATH),
        },
        model_versions={"chat": settings.chat_model},
        authorized_fixture_refs=(),
    )


def execute(spec: RunSpec, run_id: str) -> list[dict]:
    """Run ``spec`` as ``run_id`` and return its published artifacts and module results."""
    spec = spec.model_copy(update={"run_id": run_id})
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    engine = connect(settings.db_url)
    try:
        statuses = run_spec(spec, engine=engine, settings=settings)
        records = [{"kind": "RunSpec", "payload": spec.model_dump(mode="json")}]
        records += [{"kind": "ModuleRun", "payload": s.model_dump(mode="json")} for s in statuses]
        with repo_session(engine, spec.run_id) as repo:
            for kind in EXPORTED:
                records += [
                    {"kind": kind.__name__, "payload": r.model_dump(mode="json")}
                    for r in repo.list(kind)
                ]
    finally:
        engine.dispose()
    return records


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    spec = sub.add_parser("spec", help="freeze the RunSpec for a sample file list")
    spec.add_argument("--files", type=Path, required=True, help="one <STORE>/<file>.eml per line")
    spec.add_argument("--as-of", type=datetime.fromisoformat, required=True)
    spec.add_argument("--run-id", required=True)
    spec.add_argument("--code-version", required=True)
    spec.add_argument("--out", type=Path, required=True)
    run = sub.add_parser("run", help="execute a frozen RunSpec under a new run id and export it")
    run.add_argument("--run-spec", type=Path, required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--out", type=Path, required=True, help="directory, created; never reused")
    args = parser.parse_args(argv)
    if args.command == "spec":
        files = [line.strip() for line in args.files.read_text().splitlines() if line.strip()]
        built = build_spec(files, args.as_of, args.run_id, args.code_version)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(built.model_dump_json(indent=2) + "\n")
        return
    frozen = RunSpec.model_validate_json(args.run_spec.read_text(encoding="utf-8"))
    records = execute(frozen, args.run_id)
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "predictions.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    for name in ("cases", "options"):  # not produced by the reading slice
        (args.out / f"{name}.json").write_text("[]\n", encoding="utf-8")
    runs = [r["payload"] for r in records if r["kind"] == "ModuleRun"]
    print(json.dumps({m["module_id"]: m["status"] for m in runs}))


if __name__ == "__main__":
    main()
