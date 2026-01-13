# dev-bootstrap

Minimal bootstrap for my development environment.

This repository provides a small, explicit entrypoint for creating a
repeatable `~/dev` workspace and cloning a curated set of repositories.

This is intentionally **not** a general-purpose tool.

---

## Why this exists

- I want a repeatable way to recreate my development environment
- I do not want a framework, toolchain, or configuration system
- I want something safe to re-run and easy to delete and rebuild

This repository encodes a **procedure**, not a solution.

---

## How it works

- `bootstrap.sh` is the stable entrypoint
  - ensures required system dependencies exist (git, python)
  - selects *what* step to run
- `setup.py` contains all implementation logic
  - defines *how* each step is performed

The Bash interface is considered stable.  
All behavior and customization lives in Python.

The workspace root defaults to:

```

~/dev

```

and is defined in `setup.py` as `DEV`.

---

## Repository installs (explicit opt-in)

Repositories cloned by this bootstrap **may optionally** provide a file named:

```

dev-bootstrap.install.sh

```

If present, this script is executed **only when the repository is cloned
during the current bootstrap run**.

Important properties:

- Explicit opt-in only
- No guessing
- No conventions
- No implicit installs
- Existing repositories are **never** re-installed automatically

Repositories without this file are cloned only.

Each repository fully controls its own installation behavior.

---

## Usage

```bash
git clone git@github.com:juicer149/dev-bootstrap.git
cd dev-bootstrap
chmod +x bootstrap.sh
./bootstrap.sh
```

---

## Available actions

```bash
./bootstrap.sh tree
```

Create directory structure only.

```bash
./bootstrap.sh shell
```

Clone and install the shell environment (shell runtime).

```bash
./bootstrap.sh editor
```

Editor setup (e.g. Neovim).

```bash
./bootstrap.sh terminal
```

Terminal setup (tmux, wezterm, related tooling).

```bash
./bootstrap.sh env
```

Run shell → editor → terminal in order.

```bash
./bootstrap.sh projects
```

Clone project repositories.

```bash
./bootstrap.sh all
```

Run `env` followed by `projects`.

---

## Customization

All customization lives in `setup.py`.

* Directory structure is defined in `TREE`
* Repositories are defined in:

  * `SHELL_REPOS`
  * `EDITOR_REPOS`
  * `TERMINAL_REPOS`
  * `PROJECT_REPOS`

To add or remove repositories or folders, edit these mappings directly.
No other files need to be changed.

---

## Design philosophy

This repository defines the **Dev Environment ABI**.

It does not contain configuration logic.
It defines:

* directory structure
* repository boundaries
* explicit install points

Each cloned repository owns its own domain:

* shells configure shells
* editors configure editors
* terminals configure terminals
* no repository configures another

Cross-cutting behavior is expressed only via:

* directory placement
* explicit install hooks

---

## Design notes

* Safe to run multiple times
* Safe to delete `~/dev` and re-run
* No persistent state
* Repositories control their own installation
* Intentionally boring by design
