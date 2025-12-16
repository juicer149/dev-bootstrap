#!/usr/bin/env python3
"""
Bootstrap facade for developer environment setup.

This script is intentionally minimal and procedural.

Architecture
------------
- This file defines a *single facade* (`Setup`) that exposes a small,
  stable API to Bash.
- Bash selects *what* to run (tree | env | projects | all).
- Python encapsulates *how* it is done.

Design principles
-----------------
- No CLI parsing (no argparse, flags, or subcommands)
- No persistent state
- No configuration language (config is plain Python data)
- Idempotent operations where possible

This is NOT:
- a framework
- a generic setup tool
- a reusable library

This IS:
- a named procedure
- safe to run multiple times
- safe to delete and re-run after wiping ~/dev

Extension model
---------------
Repositories may optionally provide a file named:

    dev-bootstrap.install.sh

If present, this script will be executed after the repository
has been cloned (or re-visited on subsequent runs).

Presence of this file is an explicit opt-in contract.
Bootstrap will never attempt to guess or infer intent.

If this file grows:
- new steps go behind new `Setup.<action>()` methods
- the Bash interface must remain unchanged
"""

from pathlib import Path
import subprocess
import sys

# ========= CONFIG (MVP) =========
#
# Customization guide:
#
# - To add directories:
#   Edit TREE. Keys are top-level folders under ~/dev.
#   Values are lists of subdirectories to create.
#
# - To add git repositories:
#   Add entries to ENV_REPOS or PROJECT_REPOS.
#   Keys are destination paths.
#   Values are git clone URLs.
#
# No other parts of this file need to be modified.

DEV = Path.home() / "dev"
# DEV = Path.home() / "test_dev"  # For testing purposes

TREE = {
    "env": ["editor", "terminal"],
    "project": ["packages", "sandbox"],
    "tools": [],
}

ENV_REPOS = {
    DEV / "env/editor/nvim": "git@github.com:lalrak/nvim-config.git",
    DEV / "env/terminal/wezterm": "git@github.com:lalrak/wezterm-config.git",
}

PROJECT_REPOS = {
    DEV / "project/packages/curate": "git@github.com:juicer149/curate.git",
}

# ========= LOW-LEVEL MECHANISMS =========
# These functions implement mechanisms, not policy.

def _mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    print(f"[dir] {path}")


def _run_bootstrap_install(repo: Path) -> None:
    """
    Run dev-bootstrap.install.sh if the repository provides it.

    This is an explicit opt-in mechanism:
    - if the file exists, it will be executed
    - if not, nothing happens
    """
    script = repo / "dev-bootstrap.install.sh"

    if not script.exists():
        print(f"[=] no bootstrap install for {repo.name}")
        return

    print(f"[run] bootstrap install for {repo.name}")
    subprocess.run(
        ["bash", str(script)],
        check=True,
    )


def _git_clone(url: str, dest: Path) -> None:
    """
    Clone a git repository if missing.

    If the destination already exists and appears to be a git repository,
    cloning is skipped but bootstrap install (if present) is still executed.
    """
    if dest.exists() and (dest / ".git").exists():
        print(f"[=] exists {dest}")
        _run_bootstrap_install(dest)
        return

    subprocess.run(
        ["git", "clone", url, str(dest)],
        check=True,
    )

    _run_bootstrap_install(dest)


def _ensure_tree() -> None:
    for root, children in TREE.items():
        base = DEV / root
        _mkdir(base)
        for child in children:
            _mkdir(base / child)

# ========= FACADE =========
# This is the *only* surface exposed to Bash.

class Setup:
    """
    Facade for bootstrap actions.

    Each method represents a named, idempotent setup step.
    """

    @staticmethod
    def tree() -> None:
        _ensure_tree()

    @staticmethod
    def env() -> None:
        _ensure_tree()
        for path, url in ENV_REPOS.items():
            _git_clone(url, path)

    @staticmethod
    def projects() -> None:
        _ensure_tree()
        for path, url in PROJECT_REPOS.items():
            _git_clone(url, path)

    @staticmethod
    def all() -> None:
        Setup.env()
        Setup.projects()

# ========= DISPATCH =========

ACTIONS = {
    "tree": Setup.tree,
    "env": Setup.env,
    "projects": Setup.projects,
    "all": Setup.all,
}

# ========= ENTRYPOINT =========

def main() -> None:
    if len(sys.argv) != 2:
        print("usage: setup.py [tree|env|projects|all]")
        sys.exit(1)

    action = sys.argv[1]

    if action not in ACTIONS:
        print(f"unknown action: {action}")
        sys.exit(1)

    try:
        ACTIONS[action]()
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()
