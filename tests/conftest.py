"""Shared fixtures for py_proj_template tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture
def sample_name() -> str:
    """Provide a reusable name for greeting-related tests."""

    return "World"


@pytest.fixture
def project_root() -> Path:
    """Return the absolute path to the project root."""

    return Path(__file__).resolve().parents[2]


@pytest.fixture
def cli_runner(
    project_root: Path,
) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Run the CLI via python -m py_proj_template and capture its output."""

    def _run(*args: str) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-m", "py_proj_template", *args]
        return subprocess.run(
            command,
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )

    return _run

