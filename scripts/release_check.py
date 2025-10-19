#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified release checklist.

Common checks:
- Clean working tree
- Tag name 'v<version>' (PEP440-like)
- pyproject.toml has [project].name and [project].version
- tag version == pyproject version
- src/<normalized_name>/__init__.py has __version__ == pyproject version
- CHANGELOG.md contains '## [<version>]'
- If template repo (name == 'py-proj-template'): config/settings.toml version == pyproject version

Extra when updating 'latest':
- Tag exists
- Tag is the current highest among 'v*'

CLI:
  python scripts/release_check.py --tag v1.2.3
  python scripts/release_check.py --tag v1.2.3 --require-highest
  python scripts/release_check.py --tag v1.2.3 --update-latest
Exit codes: 0 ok, 1 fail, 2 usage error
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except Exception as exc:
    print(f"[release] need Python 3.11+ for tomllib: {exc}", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"
SETTINGS = ROOT / "config" / "settings.toml"
TEMPLATE_REPO_NAME = "py-proj-template"
PEP440_TAG = re.compile(r"^v([0-9][0-9A-Za-z_.+-]*)$")


def sh(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check)


def clean_tree() -> bool:
    try:
        out = sh(["git", "status", "--porcelain"]).stdout.strip()
        return out == ""
    except Exception as exc:
        print(f"[release] git status failed: {exc}", file=sys.stderr)
        return False


def read_pyproject() -> tuple[str | None, str | None]:
    if not PYPROJECT.exists():
        print("[release] pyproject.toml not found", file=sys.stderr)
        return None, None
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    proj = data.get("project") or {}
    return proj.get("name"), proj.get("version")


def normalized_pkg_dir(name: str) -> Path:
    return ROOT / "src" / name.replace("-", "_")


def read_init_version(pkg_dir: Path) -> str | None:
    init_py = pkg_dir / "__init__.py"
    if not init_py.exists():
        print(f"[release] missing {init_py}", file=sys.stderr)
        return None
    text = init_py.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]+)[\'"]', text, flags=re.MULTILINE)
    if not match:
        print(f"[release] __version__ not found in {init_py}", file=sys.stderr)
        return None
    return match.group(1)


def changelog_has(version: str) -> bool:
    if not CHANGELOG.exists():
        print("[release] CHANGELOG.md not found", file=sys.stderr)
        return False
    return f"## [{version}]" in CHANGELOG.read_text(encoding="utf-8")


def tag_exists(tag: str) -> bool:
    out = sh(["git", "tag", "--list", tag], check=False).stdout.strip()
    return bool(out)


def highest_tag() -> str | None:
    out = sh(["git", "tag", "--sort=-v:refname", "v*"], check=False).stdout.splitlines()
    return out[0] if out else None


def move_latest(tag: str) -> None:
    sh(["git", "tag", "-f", "latest", tag])
    print(f"[release] latest -> {tag}")


def read_settings_version() -> str | None:
    if not SETTINGS.exists():
        return None
    text = SETTINGS.read_text(encoding="utf-8")
    match = re.search(r'(?m)^\s*version\s*=\s*"([^"]+)"\s*$', text)
    return match.group(1) if match else None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="tag name like v1.2.3")
    parser.add_argument("--require-highest", action="store_true", help="also require tag to exist and be highest v*")
    parser.add_argument("--update-latest", action="store_true", help="run checks + move 'latest' to tag (implies --require-highest)")
    args = parser.parse_args(argv[1:])

    if args.update_latest:
        args.require_highest = True

    if not clean_tree():
        print("[release] working tree not clean", file=sys.stderr)
        return 1

    match = PEP440_TAG.fullmatch(args.tag)
    if not match:
        print(f"[release] invalid tag format: {args.tag}", file=sys.stderr)
        return 1
    tag_version = match.group(1)

    name, version = read_pyproject()
    if not name or not version:
        print(
            f"[release] missing [project].name/version in {PYPROJECT}",
            file=sys.stderr,
        )
        return 1

    if f"v{version}" != args.tag:
        print(
            f"[release] tag mismatch: requested {args.tag} but {PYPROJECT} has version v{version}",
            file=sys.stderr,
        )
        return 1

    pkg_dir = normalized_pkg_dir(name)
    init_version = read_init_version(pkg_dir)
    if not init_version or init_version != version:
        init_path = pkg_dir / "__init__.py"
        print(
            f"[release] __init__ mismatch in {init_path}: __version__={init_version} vs pyproject={version}",
            file=sys.stderr,
        )
        return 1

    if not changelog_has(version):
        print(f"[release] CHANGELOG.md has no entry for {version}", file=sys.stderr)
        return 1

    if name == TEMPLATE_REPO_NAME:
        settings_version = read_settings_version()
        if not settings_version:
            print("[release] template repo requires config/settings.toml version", file=sys.stderr)
            return 1
        if settings_version != version:
            print(f"[release] settings version mismatch: settings={settings_version} vs pyproject={version}", file=sys.stderr)
            return 1

    if args.require_highest:
        sh(["git", "fetch", "--tags"], check=False)
        if not tag_exists(args.tag):
            print(f"[release] tag not found: {args.tag}", file=sys.stderr)
            return 1
        top_tag = highest_tag()
        if top_tag != args.tag:
            print(f"[release] highest tag is {top_tag}, not {args.tag}", file=sys.stderr)
            return 1

    print(f"[release] OK: {args.tag} matches pyproject={version}, __init__={init_version}, changelog present")
    if args.update_latest:
        move_latest(args.tag)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[release] unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)
