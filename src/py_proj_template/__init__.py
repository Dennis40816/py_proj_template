"""Top-level package exports for the project template.

By re-exporting selected API functions here, consumers can simply
import py_proj_template and access the public surface directly.
"""

from __future__ import annotations

from py_proj_template.api import get_greeting

__all__ = ["get_greeting"]

__version__ = "1.0.4"




