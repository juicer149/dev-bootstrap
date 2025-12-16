#!/usr/bin/env python3
"""
Bootstrap facade for developer environment setup.

This script is intentionally minimal and procedural.

Architecture
------------
- This file defines a *single facade* (`Setup`) that exposes a small,
  stable API to Bash.
- Bash selects *what* to run
  (tree | shell | editor | terminal | env | projects | all).
- Python encapsulates *how* it is done.

Design principles
-----------------
- No CLI parsing (no argparse, flags, or subcommands)
- No persistent state
- No configuration language (config is plain Python data)
- Explicit opt-in for install hooks
- Idempotent operations where possible

This is NOT:
- a framework
- a generic setup tool
- a reusable library

This IS:
- a named procedure
- safe to run multiple times
- safe to delete and re-run after wiping ~/dev

If this file grows:
- new steps go behind new `Setup.<action>()` methods
- the Bash interface must remain unchanged
"""

from pathlib import Path
import subprocess
import sys

# ========== CONSTANTS ==========

BOOTSTRAP_INSTALL_SCRIPT = "dev-bootstrap.install.sh"

# ========= CONFIG (MVP) =========
#
# Customization guide:
#
# - To add directories:
#   Edit TREE. Keys are top-level folders under ~/dev.
#   Values are lists of subdirectories to create.
#
# - To add git repositories:
#   Add entries to *_REPOS mappings.
#   Keys are destination paths.
#   Values are git clone URLs.
#
# Repositories may optionally provide:
#   dev-bootstrap.install.sh
# This script is executed ONLY if the repository was cloned
# during the current bootstrap run.
#
# No other parts of this file need to be modified.

DEV = Path.home() / "dev"
# DEV = Path.home() / "test_dev"  # for testing

# Directory tree structure
TREE = {
    "env": ["shell", "editor", "terminal"],
    "project": ["packages", "sandbox"],
    "tools": [],
}

# Environment repositories
EDITOR_REPOS = {
    DEV / "env/editor/nvim": "git@github.com:lalrak/nvim-config.git",
}

TERMINAL_REPOS = {
    DEV / "env/terminal/wezterm": "git@github.com:lalrak/wezterm-config.git",
}

# Project repositories
PROJECT_REPOS = {
    DEV / "project/packages/curate": "git@github.com:juicer149/curate.git",
    DEV / "project/packages/architech": "git@github.com:juicer149/architech.git",
    # add more project repos here
}

# ========= LOW-LEVEL MECHANISMS =========
# These functions implement mechanisms, not policy.

def _mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    print(f"[dir] {path}")


def _git_clone(url: str, dest: Path) -> bool:
    """
    Clone a git repository if it does not already exist.

    Returns True if the repository was cloned during this call,
    False if it already existed.
    """
    if dest.exists() and (dest / ".git").exists():
        print(f"[=] exists {dest}")
        return False

    subprocess.run(
        ["git", "clone", url, str(dest)],
        check=True,
    )
    return True


def _run_bootstrap_install(repo: Path) -> None:
    """
    Run dev-bootstrap.install.sh if the repository provides it.

    Presence of the file is an explicit opt-in.
    """
    script = repo / BOOTSTRAP_INSTALL_SCRIPT

    if not script.exists():
        print(f"[=] no bootstrap install for {repo.name}")
        return

    print(f"[run] bootstrap install for {repo.name}")
    subprocess.run(
        ["bash", str(script)],
        check=True,
    )


def _process_repos(
    repos: dict[Path, str],
    label: str,
    *,
    enabled: bool = True,
) -> None:
    """
    Clone repositories and run bootstrap install hooks.

    If enabled=False, the step is acknowledged but skipped.
    """
    if not enabled:
        print(f"[{label}] not implemented yet")
        return

    for path, url in repos.items():
        cloned = _git_clone(url, path)
        if cloned:
            _run_bootstrap_install(path)


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
    def shell() -> None:
        _ensure_tree()
        _process_repos({}, "shell", enabled=False)

    @staticmethod
    def editor() -> None:
        _ensure_tree()
        _process_repos(EDITOR_REPOS, "editor")

    @staticmethod
    def terminal() -> None:
        _ensure_tree()
        _process_repos(TERMINAL_REPOS, "terminal", enabled=False)

    @staticmethod
    def env() -> None:
        """
        High-level environment setup.
        Order matters.
        """
        Setup.shell()
        Setup.editor()
        Setup.terminal()

    @staticmethod
    def projects() -> None:
        _ensure_tree()
        _process_repos(PROJECT_REPOS, "projects")

    @staticmethod
    def all() -> None:
        Setup.env()
        Setup.projects()


# ========= DISPATCH =========

ACTIONS = {
    "tree": Setup.tree,
    "shell": Setup.shell,
    "editor": Setup.editor,
    "terminal": Setup.terminal,
    "env": Setup.env,
    "projects": Setup.projects,
    "all": Setup.all,
}

# ========= ENTRYPOINT =========

def main() -> None:
    if len(sys.argv) != 2:
        print(
            "usage: setup.py "
            "[tree|shell|editor|terminal|env|projects|all]"
        )
        sys.exit(1)

    action = sys.argv[1]

    if action not in ACTIONS:
        print(f"unknown action: {action}")
        sys.exit(1)

    try:
        ACTIONS[action]()
    except subprocess.CalledProcessError as e:
        print(f"[error] command '{action}' failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
