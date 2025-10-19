"""Integration test demonstrating CLI invocation."""

from __future__ import annotations

from subprocess import CompletedProcess

from typing import Callable

from py_proj_template import get_greeting


def test_cli_demo(
    cli_runner: Callable[..., CompletedProcess[str]],
) -> None:
    """Run `python -m py_proj_template` and capture its output."""

    completed = cli_runner("--name", "Integration")

    stdout = completed.stdout.strip().splitlines()
    assert stdout[0] == "[core] Hello, Integration!"
    assert stdout[1] == "[application] [api] Hello, Integration!"
    assert get_greeting("Integration") in stdout[1]

