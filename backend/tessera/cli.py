"""`tessera` command line. Subcommands (run, export, smoke) are added by their tasks."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from tessera import __version__
from tessera.core.config import Settings, get_settings


def _engine(settings: Settings):
    from tessera.core.db import connect

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return connect(settings.db_url)


def _fixtures_load(args: argparse.Namespace) -> None:
    from tessera.core.fixtures import load_fixtures

    # Fixtures always go to the fixture namespace, whatever FIXTURE_MODE says.
    settings = get_settings().model_copy(update={"fixture_mode": True})
    fixtures_dir = args.dir or settings.data_dir / "fixtures"
    spec, n = load_fixtures(_engine(settings), fixtures_dir, settings.config_dir)
    print(
        f"loaded {n} records from {len(spec.authorized_fixture_refs)} files as run "
        f"{spec.run_id!r} (as_of {spec.as_of.isoformat()}) into {settings.db_path}"
    )


def _reset(args: argparse.Namespace) -> None:
    from tessera.core.repo import reset_run

    settings = get_settings()
    n = reset_run(_engine(settings), args.run)
    print(f"deleted run {args.run!r} ({n} artifacts) from {settings.db_path}")


def _run(args: argparse.Namespace) -> None:
    from tessera.core.contracts import RunSpec
    from tessera.core.orchestrator import run
    from tessera.core.run_repo import repo_session

    settings = get_settings()
    if args.fixture_mode:
        settings = settings.model_copy(update={"fixture_mode": True})
    spec = RunSpec.model_validate_json(args.run_spec.read_text(encoding="utf-8"))
    if args.as_of is not None:
        spec = RunSpec.model_validate(
            {**spec.model_dump(), "as_of": args.as_of, "run_id": str(uuid4())}
        )
    if (spec.mode == "fixture") != settings.fixture_mode:
        raise ValueError("Fixture runs require an explicitly selected fixture namespace")
    if not any(m.manifest.enabled and m.manifest.mode != "unavailable" for m in spec.modules):
        raise ValueError("Run requires at least one enabled module")
    engine = _engine(settings)
    try:
        statuses = run(spec, engine=engine, modules=args.modules)
        with repo_session(engine, spec, fixture_mode=settings.fixture_mode) as repo:
            status = repo.run_state()["status"]
        print(
            json.dumps(
                {
                    "run_id": spec.run_id,
                    "status": status,
                    "modules": [m.model_dump(mode="json") for m in statuses],
                }
            )
        )
        if status not in {"succeeded", "degraded"}:
            raise SystemExit(1)
    finally:
        engine.dispose()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="tessera")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command")

    fixtures = sub.add_parser("fixtures", help="hand-written fixtures (fixture namespace)")
    fixtures_sub = fixtures.add_subparsers(dest="action", required=True)
    load = fixtures_sub.add_parser("load", help="replace the fixture run with data/fixtures/")
    load.add_argument("--dir", type=Path, help="fixtures folder (default: data/fixtures)")
    load.set_defaults(func=_fixtures_load)

    reset = sub.add_parser("reset", help="delete one run's projections (ERP rows stay)")
    reset.add_argument("--run", required=True, help="run id")
    reset.set_defaults(func=_reset)

    run = sub.add_parser("run", help="execute an immutable module snapshot")
    run.add_argument("--run-spec", type=Path, required=True)
    run.add_argument(
        "--as-of", type=datetime.fromisoformat, help="override the clock and assign a new run ID"
    )
    run.add_argument("--modules", nargs="+", help="selected module IDs plus prerequisites")
    run.add_argument("--fixture-mode", action="store_true")
    run.set_defaults(func=_run)

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
