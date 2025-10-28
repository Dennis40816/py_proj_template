"""Shared fixtures for py_proj_template tests."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture
def sample_name() -> str:
    """Provide a reusable name for greeting-related tests."""

    return "World"


# Ensure src/ is on sys.path so imports work when running from repo root
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "src"))


@pytest.fixture
def project_root() -> Path:
    """Return the absolute path to the project root."""

    return _PROJECT_ROOT


@pytest.fixture
def cli_runner(
    project_root: Path,
) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Run the CLI via python -m py_proj_template and capture its output."""

    def _run(*args: str) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-m", "py_proj_template", *args]
        env = os.environ.copy()
        existing = env.get("PYTHONPATH", "")
        add_path = str(project_root / "src")
        env["PYTHONPATH"] = (add_path if not existing else add_path + os.pathsep + existing)
        return subprocess.run(
            command,
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

    return _run

