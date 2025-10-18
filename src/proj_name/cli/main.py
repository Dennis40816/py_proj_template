"""Command-line entry point demonstrating application and core imports."""

from __future__ import annotations

import argparse
from typing import Sequence

from proj_name.application import run_demo
from proj_name.core.lib_example import build_greeting


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the example CLI."""

    parser = argparse.ArgumentParser(
        prog="proj-name",
        description="Example CLI wiring for the project template.",
    )
    parser.add_argument(
        "--name",
        default="world",
        help="Name passed to the demo workflow.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI arguments and invoke application and core demos."""

    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    print(f"[core] {build_greeting(args.name)}")
    run_demo(args.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
