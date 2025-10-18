"""Demonstration of a reusable library function."""

from __future__ import annotations


def build_greeting(name: str) -> str:
    """Return a greeting string to show library-to-API flow."""

    return f"Hello, {name}!"
