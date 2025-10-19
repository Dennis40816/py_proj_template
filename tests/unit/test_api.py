"""Minimal unit test demonstrating API usage."""

from __future__ import annotations

from py_proj_template.api import get_greeting


def test_get_greeting(sample_name: str) -> None:
    """The public API should wrap the core greeting."""

    assert get_greeting(sample_name) == f"[api] Hello, {sample_name}!"

