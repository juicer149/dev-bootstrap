#!/usr/bin/env python3
"""
Bootstrap facade for developer environment setup.

This script defines a *stable procedural ABI* for recreating a personal
development environment.

Architecture
------------
- Bash selects *what* procedure to run.
- Python defines *how* each procedure is executed.
- The exposed surface is intentionally small and stable.

Actions are divided into:
- leaf actions      → perform concrete work (clone, mkdir, run scripts)
- composite actions → orchestrate other actions only

No action performs implicit discovery or guessing.

Design principles
-----------------
- No CLI parsing (no flags, no subcommands, no argparse)
- No persistent state
- No configuration language (config = Python data)
- Explicit opt-in for install hooks
- Idempotent operations where possible

This is NOT:
- a framework
- a general-purpose setup tool
- a reusable library

This IS:
- a named procedure
- safe to run multiple times
- safe to delete ~/dev and re-run
"""

from pathlib import Path
import subprocess
import sys


# =========================================================
# CONSTANTS
# =========================================================

BOOTSTRAP_INSTALL_SCRIPT = "dev-bootstrap.install.sh"


# =========================================================
# CONFIGURATION
# =========================================================

DEV = Path.home() / "dev"
# DEV = Path.home() / "test_dev"  # for testing


# ---------------------------------------------------------
# Directory structure
# ---------------------------------------------------------

TREE = {
    "env": ["shell", "editor", "terminal"],
    "project": ["packages", "sandbox"],
    "tools": [],
}


# ---------------------------------------------------------
# Repository groups
#
# IMPORTANT SEMANTICS:
# These mappings group repositories by *which setup step
# activates them*, not by what they "are".
#
# They represent procedural filters, not ontology.
# ---------------------------------------------------------

SHELL_REPOS = {
    DEV / "env/shell": "git@github.com:juicer149/shell-env.git",
}

EDITOR_REPOS = {
    DEV / "env/editor/nvim": "git@github.com:juicer149/nvim-config.git",
}

TERMINAL_REPOS = {
    DEV / "env/terminal/wezterm": "git@github.com:juicer149/wezterm-config.git",
    DEV / "env/terminal/tmux": "git@github.com:juicer149/tmux-config.git",
    DEV / "env/terminal/ai": "git@github.com:juicer149/ai-env.git",
}

PROJECT_REPOS = {
    DEV / "project/packages/curate": "git@github.com:juicer149/curate.git",
    DEV / "project/packages/architech": "git@github.com:juicer149/architech.git",
}


# =========================================================
# LOW-LEVEL MECHANISMS
# These implement mechanisms, not policy.
# =========================================================

def _mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    print(f"[dir] {path}")


def _git_clone(url: str, dest: Path) -> bool:
    """
    Clone a git repository if it does not already exist.

    Returns:
        True  → repository was cloned during this invocation
        False → repository already existed
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
    Run dev-bootstrap.install.sh if the repository explicitly provides it.
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


# =========================================================
# FACADE
# This is the *only* surface exposed to Bash.
# =========================================================

class Setup:
    """
    Facade for bootstrap actions.

    Leaf actions:
        - shell
        - editor        - terminal
        - projects

    Composite actions (orchestration only):
        - env
        - all
    """

    @staticmethod
    def tree() -> None:
        _ensure_tree()

    @staticmethod
    def shell() -> None:
        _ensure_tree()
        _process_repos(SHELL_REPOS, "shell")

    @staticmethod
    def editor() -> None:
        _ensure_tree()
        _process_repos(EDITOR_REPOS, "editor")

    @staticmethod
    def terminal() -> None:
        _ensure_tree()
        _process_repos(TERMINAL_REPOS, "terminal")

    @staticmethod
    def env() -> None:
        """
        High-level environment setup.

        This action performs orchestration only.
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


# =========================================================
# DISPATCH
# =========================================================

ACTIONS = {
    "tree": Setup.tree,
    "shell": Setup.shell,
    "editor": Setup.editor,
    "terminal": Setup.terminal,
    "env": Setup.env,
    "projects": Setup.projects,
    "all": Setup.all,
}


# =========================================================
# ENTRYPOINT
# =========================================================

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
