"""Run from the repository root: python -m eval --help."""

import argparse
import json
from pathlib import Path

from .harness import ARTIFACTS, FrozenRun, freeze
from .isolation import run_product


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
    product = sub.add_parser(
        "product", help="Start the product with kernel-enforced input isolation"
    )
    product.add_argument("arguments", nargs=argparse.REMAINDER, help="-- -m tessera.cli ...")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    if args.command == "product":
        arguments = args.arguments
        if arguments[:1] == ["--"]:
            arguments = arguments[1:]
        if not arguments:
            parser.error("product requires Python arguments after --")
        raise SystemExit(run_product(root, arguments))
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
        if not args.output.resolve().is_relative_to(root / "data"):
            parser.error("evaluation receipts must be written under data/")
        run = FrozenRun(args.bundle, args.sha256)
        receipt = run.receipt(root / "generated/ground_truth", args.key)
        # Never overwrite a previous evaluation record.
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
            stream.write("\n")


if __name__ == "__main__":
    main()
