"""Run from the repository root: python -m eval --help."""

import argparse
import json
from datetime import date
from pathlib import Path

from .forecast import KEY, score_forecasts
from .harness import ARTIFACTS, FrozenRun, freeze
from .isolation import run_product
from .lead_time import lead_time_report
from .reading import catalog_ids, load_labels, reading_protocol, score


def _write_new(path: Path, data: object) -> None:
    """Exclusive creation: previous records are never overwritten."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    freeze_parser = sub.add_parser("freeze", help="Snapshot product exports before oracle access")
    freeze_parser.add_argument("destination", type=Path)
    freeze_parser.add_argument("--protocol", type=Path, required=True)
    for kind in ARTIFACTS:
        freeze_parser.add_argument(f"--{kind}", type=Path, required=True)
    freeze_parser.add_argument("--source", action="append", type=Path, required=True)
    freeze_parser.add_argument("--configuration", action="append", type=Path, required=True)
    verify = sub.add_parser(
        "verify", help="Verify snapshot, then record selected oracle key hashes"
    )
    verify.add_argument("bundle", type=Path)
    verify.add_argument("--sha256", required=True)
    verify.add_argument("--key", action="append", required=True)
    verify.add_argument("--output", type=Path, required=True)
    forecast = sub.add_parser("forecast", help="Score frozen forecast errors on a fixed universe")
    forecast.add_argument("bundle", type=Path)
    forecast.add_argument("--sha256", required=True)
    forecast.add_argument("--key", default=KEY)
    forecast.add_argument("--output", type=Path, required=True)
    sample = sub.add_parser(
        "reading-sample", help="EVL-02: write the sample file list and protocol, no answers"
    )
    sample.add_argument("--files-out", type=Path)
    sample.add_argument("--run-spec", type=Path, help="frozen RunSpec, for the protocol")
    sample.add_argument("--protocol-out", type=Path)
    reading = sub.add_parser("reading", help="EVL-02: score a verified bundle on the labels")
    reading.add_argument("bundle", type=Path)
    reading.add_argument("--sha256", required=True)
    reading.add_argument("--output", type=Path, required=True)
    product = sub.add_parser(
        "product", help="Start the product with kernel-enforced input isolation"
    )
    product.add_argument("arguments", nargs=argparse.REMAINDER, help="-- -m tesseract.cli ...")
    lead = sub.add_parser(
        "lead-time", help="EVL-04: pipeline lead time vs stock and sales baselines"
    )
    lead.add_argument("--bundle", type=Path, help="Frozen run; omit to score baselines only")
    lead.add_argument("--sha256", help="Manifest SHA-256 recorded before oracle access")
    lead.add_argument("--split", default="dev", help="Stores when no bundle is given")
    lead.add_argument("--start", type=date.fromisoformat, default=date(2026, 8, 31))
    lead.add_argument("--end", type=date.fromisoformat, default=date(2026, 10, 21))
    lead.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    if args.command in (
        "verify",
        "forecast",
        "lead-time",
    ) and not args.output.resolve().is_relative_to(root / "data"):
        parser.error("evaluation outputs must be written under data/")
    if args.command == "lead-time":
        if bool(args.bundle) != bool(args.sha256):
            parser.error("--bundle and --sha256 go together")
        run = FrozenRun(args.bundle, args.sha256) if args.bundle else None
        report = lead_time_report(root, run, args.split, args.start, args.end)
        _write_new(args.output, report)
        return
    if args.command == "product":
        arguments = args.arguments
        if arguments[:1] == ["--"]:
            arguments = arguments[1:]
        if not arguments:
            parser.error("product requires Python arguments after --")
        raise SystemExit(run_product(root, arguments))
    if args.command in {"reading-sample", "reading"}:
        outputs = (
            [args.files_out, args.protocol_out]
            if args.command == "reading-sample"
            else [args.output]
        )
        if any(o is not None and not o.resolve().is_relative_to(root / "data") for o in outputs):
            parser.error("outputs must be written under data/")
        labels, labels_sha256 = load_labels()
    if args.command == "reading-sample":
        if args.files_out is not None:
            # File names only: the product run must not see labels or anchors.
            args.files_out.parent.mkdir(parents=True, exist_ok=True)
            with args.files_out.open("x", encoding="utf-8") as stream:
                stream.write("".join(f"{name}\n" for name in sorted(labels["files"])))
        if args.protocol_out is not None:
            if args.run_spec is None:
                parser.error("--protocol-out requires --run-spec")
            spec = json.loads(args.run_spec.read_text(encoding="utf-8"))
            _write_new(args.protocol_out, reading_protocol(labels, spec))
        return
    if args.command == "reading":
        run = FrozenRun(args.bundle, args.sha256)
        result = score(
            labels,
            run.artifacts["predictions"],
            catalog_ids(root / "generated/sources/erp/master_data"),
        )
        result["manifest_sha256"] = run.manifest_sha256
        result["labels_sha256"] = labels_sha256
        result["protocol"] = run.manifest["protocol"]
        _write_new(args.output, result)
        print(json.dumps({"overall": result["overall"], "links": result["links"]}, indent=2))
        return
    if args.command == "freeze":
        protocol = args.protocol.resolve(strict=True)
        if not protocol.is_relative_to(root / "data"):
            parser.error("protocol must come from data/")
        sha256 = freeze(
            args.destination,
            json.loads(protocol.read_bytes()),
            {kind: getattr(args, kind) for kind in ARTIFACTS},
            args.source,
            args.configuration,
            root=root,
        )
        print(sha256)
    else:
        run = FrozenRun(args.bundle, args.sha256)
        receipt = (
            score_forecasts(run, root / "generated/ground_truth", args.key)
            if args.command == "forecast"
            else run.receipt(root / "generated/ground_truth", args.key)
        )
        _write_new(args.output, receipt)


if __name__ == "__main__":
    main()
