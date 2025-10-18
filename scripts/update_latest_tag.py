#!/usr/bin/env python3
"""Validate release prerequisites and move the `latest` tag.

This utility should be executed after creating the release commit and the
corresponding `v<version>` tag. It enforces the internal release checklist:

1. Ensure there are no uncommitted changes.
2. Confirm the project name matches the template (`py-proj-template`).
3. Verify the version declared in `pyproject.toml` matches
   `config/settings.toml`.
4. Check that `CHANGELOG.md` already contains an entry for the version.
5. Confirm a semantic tag `v<version>` exists and represents the highest tag.

Only when all validations pass will the script fast-forward the `latest` tag
to the resolved release tag (unless `--dry-run` is provided).
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import Iterable, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PACKAGE_NAME = "py-proj-template"


def run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    """Execute ``command`` and return the completed process."""

    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def run_optional(command: Sequence[str], *, timeout: float | None = 5.0) -> subprocess.CompletedProcess[str]:
    """Execute ``command`` but suppress ``CalledProcessError``."""

    try:
        return subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, returncode=1, stdout="", stderr="timeout")


def ensure_clean_workspace() -> None:
    """Abort if there are pending changes."""

    status = run(["git", "status", "--porcelain"])
    if status.stdout.strip():
        raise SystemExit(
            "Workspace is not clean. Commit or stash changes before updating tags."
        )


def read_pyproject_fields() -> tuple[str, str]:
    """Return `(name, version)` from ``pyproject.toml``."""

    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    name_match = re.search(r'^name\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not name_match or not version_match:
        raise SystemExit("pyproject.toml must contain project name and version.")
    return name_match.group(1), version_match.group(1)


def read_template_version() -> str | None:
    """Return template version from settings if available."""

    settings_path = ROOT / "config" / "settings.toml"
    if not settings_path.exists():
        return None
    text = settings_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not match:
        return None
    return match.group(1)


def changelog_has_entry(version: str) -> bool:
    """Return True if ``CHANGELOG.md`` contains the version header."""

    entry = f"## [{version}]"
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    return entry in changelog


def parse_semver(tag: str) -> Tuple[int, ...]:
    """Parse a tag of the form ``v<semver>`` into a tuple of ints."""

    version_text = tag.lstrip("v")
    parts = version_text.split(".")
    try:
        return tuple(int(part) for part in parts)
    except ValueError as exc:
        raise SystemExit(f"Unsupported semantic version tag: {tag}") from exc


def resolve_highest_tag(tags: Iterable[str]) -> str:
    """Return the highest semantic version tag from ``tags``."""

    version_tags = [tag for tag in tags if tag.startswith("v")]
    if not version_tags:
        raise SystemExit("No version tags (v*) found. Create the release tag first.")
    return max(version_tags, key=parse_semver)


def ensure_release_tag_exists(version: str) -> None:
    """Confirm the semantic tag for ``version`` exists."""

    tag_name = f"v{version}"
    result = run(["git", "tag", "--list", tag_name])
    if not result.stdout.strip():
        raise SystemExit(f"Tag {tag_name} not found. Create it before updating latest.")


def resolve_tag_sha(tag: str) -> str | None:
    """Return the commit SHA for ``tag`` (or ``None`` if missing)."""

    result = run_optional(["git", "rev-parse", tag])
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def move_latest(tag: str, dry_run: bool) -> None:
    """Point ``latest`` to ``tag`` (unless ``dry_run``)."""

    if dry_run:
        print(f"[dry-run] Would move latest to {tag}")
        return
    run(["git", "tag", "-f", "latest", tag])
    print(f"latest now points to {tag}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show intended changes without updating tags.",
    )
    args = parser.parse_args(argv)

    ensure_clean_workspace()

    project_name, project_version = read_pyproject_fields()

    template_version = read_template_version()
    if project_name == TEMPLATE_PACKAGE_NAME:
        if template_version is None:
            raise SystemExit(
                "Template repositories must define config/settings.toml with template.version."
            )
        if project_version != template_version:
            raise SystemExit(
                "Version mismatch between pyproject.toml and config/settings.toml. "
                "Update both files before tagging."
            )
    else:
        # For downstream projects, optionally warn if metadata drifts.
        if template_version and template_version != project_version:
            print(
                "Warning: config/settings.toml template.version differs from pyproject version."
                " Proceeding because this is not the template repo."
            )

    if not changelog_has_entry(project_version):
        raise SystemExit(
            f"CHANGELOG.md does not list version {project_version}. "
            "Document the release before updating latest."
        )

    run_optional(["git", "fetch", "--tags"])
    ensure_release_tag_exists(project_version)

    tag_list = run(["git", "tag", "--list", "v*"]).stdout.splitlines()
    highest_tag = resolve_highest_tag(tag_list)
    expected_tag = f"v{project_version}"
    if highest_tag != expected_tag:
        raise SystemExit(
            f"Latest semantic tag is {highest_tag}, but pyproject declares {project_version}. "
            "Please tag the release with the matching version."
        )

    target_sha = resolve_tag_sha(highest_tag)
    if target_sha is None:
        raise SystemExit(f"Unable to resolve tag {highest_tag}.")

    latest_sha = resolve_tag_sha("latest")
    if latest_sha == target_sha:
        print("latest already points to the newest version tag. Nothing to update.")
        return 0

    move_latest(highest_tag, dry_run=args.dry_run)
    print("Reminder: run `uv run python scripts/run_checks.py` before pushing release tags.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
