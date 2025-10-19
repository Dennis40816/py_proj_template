"""Public API surface for the project template.

This module shows how library-layer functionality is re-exported for
external consumers. Downstream projects can import from py_proj_template
without touching the internal core package directly.
"""

from __future__ import annotations

from py_proj_template.core.lib_example import build_greeting

__all__ = ["get_greeting"]


def get_greeting(name: str) -> str:
    """Return a greeting string produced by the library layer."""

    return f"[api] {build_greeting(name)}"

