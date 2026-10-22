"""`tessera` command line. Subcommands (run, reset, export, smoke) are added by their tasks."""

import argparse

from tessera import __version__


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="tessera")
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args(argv)
    parser.print_help()


if __name__ == "__main__":
    main()
