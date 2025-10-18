"""Top-level package exports for the project template.

By re-exporting selected API functions here, consumers can simply
import proj_name and access the public surface directly.
"""

from __future__ import annotations

from proj_name.api import get_greeting

__all__ = ["get_greeting"]
