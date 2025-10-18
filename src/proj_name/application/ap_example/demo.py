"""Simple application workflow that calls into the API layer."""

from __future__ import annotations

from proj_name.api import get_greeting


def run_demo(name: str) -> None:
    """Run the sample application workflow using the public API."""

    message = get_greeting(name)
    print(f"[application] {message}")
