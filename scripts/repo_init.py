#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize a repo cloned from py_proj_template.

Actions:
  - Rename src/proj_name -> src/<new_name>
  - Replace 'proj_name' in text files (skip protected files)
  - Update pyproject.toml: project.name and occurrences
  - Initialize versions to 1.0.0:
      * pyproject.toml [project].version = "1.0.0"
      * src/<new_name>/__init__.py __version__ = "1.0.0"
  - Git: rename 'origin' -> 'upstream', add new 'origin' if given
  - Create/update 'template' branch and merge baseline into 'main'
  - Optionally create .venv with uv and editable install
  - Install .git/hooks/pre-push that calls scripts/release_check.py

Notes:
  - Does NOT change config/settings.toml
  - Requires clean git working tree
  - Dry-run by default, use --apply to execute
"""
from __future__ import annotations

import argparse, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PKG_OLD = SRC / "proj_name"
PYPROJECT = ROOT / "pyproject.toml"
TEXT_EXT = {".py", ".toml", ".md", ".yml", ".yaml", ".txt", ".cfg", ".ini", ".json", ".lock"}
PROTECTED = {str((ROOT / "config" / "settings.toml").resolve())}


def sh(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, check=check, text=True)


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def git_clean() -> bool:
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], text=True, cwd=ROOT)
        return out.strip() == ""
    except Exception:
        return False


def iter_text_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXT:
            yield p


def rename_package(old_dir: Path, new_pkg: str, apply: bool) -> Path:
    new_dir = old_dir.parent / new_pkg
    if not old_dir.exists():
        sys.exit(f"expected package directory missing: {old_dir}")
    if new_dir.exists():
        sys.exit(f"target package already exists: {new_dir}")
    if apply:
        old_dir.rename(new_dir)
    else:
        print(f"dry-run: rename {old_dir} -> {new_dir}")
    return new_dir


def replace_proj_name(root: Path, new_pkg: str, apply: bool) -> int:
    pat = re.compile(r"\bproj_name\b")
    n_changed = 0
    for p in iter_text_files(root):
        rp = str(p.resolve())
        if rp in PROTECTED:
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except Exception:
            continue
        ns = pat.sub(new_pkg, s)
        if ns != s:
            n_changed += 1
            if apply:
                p.write_text(ns, encoding="utf-8")
            else:
                print(f"dry-run: update {p}")
    return n_changed


def update_pyproject(pyproj: Path, new_name: str, apply: bool):
    s = pyproj.read_text(encoding="utf-8")
    s2 = re.sub(r'(?m)^(project\.name\s*=\s*")[^"]+(")', rf'\1{new_name}\2', s)
    s2 = s2.replace("proj_name", new_name)
    if s2 != s:
        if apply:
            pyproj.write_text(s2, encoding="utf-8")
        else:
            print("dry-run: update pyproject.toml project.name and occurrences")


# --- 新增：統一將版本設為 1.0.0 ---
def set_versions(new_pkg: str, apply: bool):
    # 1) pyproject.toml -> project.version = "1.0.0"
    s = PYPROJECT.read_text(encoding="utf-8")
    s2, n = re.subn(r'(?m)^(project\.version\s*=\s*")[^"]+(")', r'\g<1>1.0.0\2', s)
    if n == 0:
        # 若缺少 version 欄位則在 [project] 區段內追加
        s2 = re.sub(r'(?m)^\[project\]\s*$', "[project]\nversion = \"1.0.0\"", s, count=1)
        if s2 == s:
            # 若沒找到 [project]，則附加到檔尾（fallback）
            s2 = s.rstrip() + '\n[project]\nversion = "1.0.0"\n'
    if s2 != s:
        if apply:
            PYPROJECT.write_text(s2, encoding="utf-8")
        else:
            print("dry-run: set pyproject.project.version = 1.0.0")

    # 2) src/<pkg>/__init__.py -> __version__ = "1.0.0"
    init_py = (SRC / new_pkg / "__init__.py")
    if not init_py.exists():
        if apply:
            init_py.parent.mkdir(parents=True, exist_ok=True)
            init_py.write_text('__version__ = "1.0.0"\n', encoding="utf-8")
        else:
            print(f"dry-run: create {init_py} with __version__ = 1.0.0")
        return
    t = init_py.read_text(encoding="utf-8")
    t2, n2 = re.subn(r'(?m)^__version__\s*=\s*["\'][^"\']*["\']\s*$', '__version__ = "1.0.0"', t)
    if n2 == 0:
        t2 = t.rstrip() + '\n__version__ = "1.0.0"\n'
    if t2 != t:
        if apply:
            init_py.write_text(t2, encoding="utf-8")
        else:
            print(f"dry-run: set {init_py} __version__ = 1.0.0")


def git_remote_exists(name: str) -> bool:
    try:
        out = subprocess.check_output(["git", "remote"], text=True, cwd=ROOT)
        return name in out.split()
    except Exception:
        return False


def set_git_remotes(new_origin: str, apply: bool):
    if git_remote_exists("origin") and not git_remote_exists("upstream"):
        if apply:
            sh(["git", "remote", "rename", "origin", "upstream"])
        else:
            print("dry-run: git remote rename origin -> upstream")
    if new_origin and not git_remote_exists("origin"):
        if apply:
            sh(["git", "remote", "add", "origin", new_origin])
        else:
            print(f"dry-run: git remote add origin {new_origin}")


def ensure_template_branch(apply: bool):
    have_upstream_main = False
    try:
        out = subprocess.check_output(["git", "ls-remote", "--heads", "upstream", "main"], text=True, cwd=ROOT)
        have_upstream_main = bool(out.strip())
    except Exception:
        have_upstream_main = False
    if apply:
        sh(["git", "fetch", "--all"], check=False)
        if have_upstream_main:
            sh(["git", "checkout", "-B", "template", "upstream/main"], check=False)
        else:
            sh(["git", "checkout", "-B", "template"], check=False)
        sh(["git", "checkout", "-B", "main"], check=False)
        sh(["git", "merge", "--no-edit", "template"], check=False)
    else:
        base = "upstream/main" if have_upstream_main else "HEAD"
        print(f"dry-run: create/update 'template' from {base}, merge into 'main'")


def create_env_and_install(apply: bool, no_uv: bool):
    if no_uv or not have("uv"):
        if not have("uv"):
            print("uv not found. skip venv+install.")
        return
    if apply:
        sh(["uv", "venv"])
        sh(["uv", "pip", "install", "--editable", "."], check=False)
    else:
        print("dry-run: uv venv && uv pip install --editable .")


def install_pre_push_hook(apply: bool):
    hooks_dir = ROOT / ".git" / "hooks"
    src = ROOT / "scripts" / "git_hook" / "pre-push"
    dst = hooks_dir / "pre-push"
    if not src.exists():
        print("pre-push hook source not found; skip"); return
    if apply:
        hooks_dir.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        os.chmod(dst, 0o755)
    else:
        print(f"dry-run: install hook {src} -> {dst}")


def validate_new_name(name: str):
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
        sys.exit("invalid package name. use [a-zA-Z_][a-zA-Z0-9_]*")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new-name", required=True, help="new top-level package name, e.g., my_project")
    ap.add_argument("--origin", default="", help="git origin url to add after renaming origin->upstream")
    ap.add_argument("--apply", action="store_true", help="execute changes")
    ap.add_argument("--no-uv", action="store_true", help="skip uv venv+install")
    args = ap.parse_args()

    if not PYPROJECT.exists():
        sys.exit("pyproject.toml not found. run from repo root.")
    if not git_clean():
        sys.exit("git working tree not clean. commit or stash first.")
    validate_new_name(args.new_name)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{mode}: init new package = {args.new_name}")

    rename_package(PKG_OLD, args.new_name, args.apply)
    n_files = replace_proj_name(ROOT, args.new_name, args.apply)
    print(f"files updated for identifier rename: {n_files}")
    update_pyproject(PYPROJECT, args.new_name, args.apply)
    # 設定版本為 1.0.0（pyproject 與 __init__.py）
    set_versions(args.new_name, args.apply)
    set_git_remotes(args.origin, args.apply)
    ensure_template_branch(args.apply)
    create_env_and_install(args.apply, args.no_uv)
    install_pre_push_hook(args.apply)
    print("done.")


if __name__ == "__main__":
    main()
