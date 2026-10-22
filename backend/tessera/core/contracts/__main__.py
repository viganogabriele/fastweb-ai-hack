import argparse
import json
from pathlib import Path

from .schema import export_schema


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the versioned MVP contract JSON Schema")
    parser.add_argument("--output", type=Path, help="Write to this file; default is stdout")
    args = parser.parse_args()
    payload = json.dumps(export_schema(), ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
