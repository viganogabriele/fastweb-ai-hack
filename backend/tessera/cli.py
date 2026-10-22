"""`tessera` command line. Subcommands (run, reset, export, smoke) are added by their tasks."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from tessera import __version__
from tessera.core.config import get_settings
from tessera.core.contracts import RunSpec
from tessera.core.db import RunRow, create_schema, make_engine
from tessera.core.fixtures import load_fixtures
from tessera.core.repo import repo_session


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="tessera")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command")
    fixtures = commands.add_parser("fixtures", help="Explicit fixture namespace operations")
    fixture_commands = fixtures.add_subparsers(dest="fixture_command", required=True)
    load = fixture_commands.add_parser("load")
    load.add_argument("--run-spec", type=Path, required=True)
    load.add_argument("--file", action="append", help="Authorized path relative to data/fixtures")
    reset = commands.add_parser("reset", help="Reset only projections of an existing run")
    reset.add_argument("--run", required=True)
    run = commands.add_parser("run", help="Execute an immutable module snapshot")
    run.add_argument("--run-spec", type=Path, required=True)
    run.add_argument(
        "--as-of",
        type=datetime.fromisoformat,
        help="Override the replay instant and assign a fresh run ID",
    )
    run.add_argument("--modules", nargs="+", help="Selected module IDs, including prerequisites")
    for command in (load, reset, run):
        command.add_argument("--db-url", help="SQLite URL; default comes from DATA_DIR")
        command.add_argument("--fixture-mode", action="store_true", default=None)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return
    settings = get_settings()
    fixture_mode = settings.fixture_mode if args.fixture_mode is None else args.fixture_mode
    url = args.db_url or settings.db_url
    database = make_url(url).database
    if database and database != ":memory:":
        Path(database).parent.mkdir(parents=True, exist_ok=True)
    engine = make_engine(url)
    try:
        create_schema(engine)
        if args.command == "fixtures":
            if not fixture_mode:
                parser.error("fixtures load requires --fixture-mode or FIXTURE_MODE=1")
            spec = RunSpec.model_validate_json(args.run_spec.read_text(encoding="utf-8"))
            files = args.file if args.file is not None else list(spec.authorized_fixture_refs)
            if not files:
                parser.error("RunSpec must explicitly authorize the selected fixture files")
            with repo_session(engine, spec, fixture_mode=True) as repo:
                result = load_fixtures(
                    repo, files, root=Path(__file__).resolve().parents[2] / "data/fixtures"
                )
            print(json.dumps({"run_id": spec.run_id, "namespace": "fixture", **result}))
        elif args.command == "run":
            from tessera.core.orchestrator import run as execute

            spec = RunSpec.model_validate_json(args.run_spec.read_text(encoding="utf-8"))
            if args.as_of is not None:
                spec = RunSpec.model_validate(
                    {**spec.model_dump(), "as_of": args.as_of, "run_id": str(uuid4())}
                )
            if (spec.mode == "fixture") != fixture_mode:
                parser.error("fixture run requires the explicit fixture namespace")
            if not any(
                m.manifest.enabled and m.manifest.mode != "unavailable" for m in spec.modules
            ):
                parser.error("run requires at least one enabled module")
            statuses = execute(spec, engine=engine, modules=args.modules)
            with repo_session(engine, spec, fixture_mode=fixture_mode) as repo:
                status = repo.run_state()["status"]
            print(
                json.dumps(
                    {
                        "run_id": spec.run_id,
                        "status": status,
                        "modules": [module.model_dump(mode="json") for module in statuses],
                    }
                )
            )
            if status not in {"succeeded", "degraded"}:
                raise SystemExit(1)
        else:
            namespace = "fixture" if fixture_mode else "product"
            with Session(engine) as session:
                row = session.get(RunRow, (namespace, args.run))
                if row is None:
                    parser.error("Run not found in the selected namespace")
                spec = RunSpec.model_validate(row.spec)
            with repo_session(engine, spec, fixture_mode=fixture_mode) as repo:
                count = repo.reset_projections()
            print(json.dumps({"run_id": spec.run_id, "namespace": namespace, "removed": count}))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
