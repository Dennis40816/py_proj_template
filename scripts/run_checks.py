#!/usr/bin/env python3
"""Utility entry point for running common quality checks."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_TASKS: dict[str, list[list[str]]] = {
    "format": [["black", "src", "tests", "scripts"]],
    "lint": [["ruff", "check", "src", "tests", "scripts"]],
    "test": [["pytest"]],
}


def build_command(command: list[str]) -> list[str]:
    """Return a command, preferring uv if it is available."""
    tool, *args = command
    if shutil.which("uv"):
        return ["uv", "run", tool, *args]
    return [sys.executable, "-m", tool, *args]


def run_command(command: list[str]) -> int:
    """Execute a single command and stream output to the console."""
    completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    return completed.returncode


def run_task(task: str) -> int:
    """Run a named task composed of one or more commands."""
    print(f"==> {task}")
    for command in DEFAULT_TASKS[task]:
        exit_code = run_command(build_command(command))
        if exit_code != 0:
            return exit_code
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tasks",
        nargs="*",
        choices=sorted(DEFAULT_TASKS),
        help="Tasks to run (default: all)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tasks and exit.",
    )
    args = parser.parse_args(argv)

    if args.list:
        for task_name in sorted(DEFAULT_TASKS):
            print(task_name)
        return 0

    tasks = args.tasks or list(DEFAULT_TASKS)
    for task in tasks:
        exit_code = run_task(task)
        if exit_code != 0:
            return exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
