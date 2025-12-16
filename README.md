# dev-bootstrap

Minimal bootstrap for my development environment.

This repository contains a small, explicit entrypoint for setting up
my local `~/dev` workspace and cloning a handful of core repositories.

## Why this exists

- I want a repeatable way to recreate my development environment
- I do not want a framework, tool, or configuration system
- I want something safe to re-run and easy to delete and rebuild

This repo encodes a *procedure*, not a general solution.

## How it works

- `bootstrap.sh` is the entrypoint
  - ensures required system dependencies exist
  - selects *what* step to run
- `setup.py` contains all setup logic
  - defines *how* each step is performed

The Bash interface is considered stable.
All implementation details live in Python.

## Usage

```bash
git clone git@github.com:juicer149/dev-bootstrap.git
cd dev-bootstrap
chmod +x bootstrap.sh
./bootstrap.sh
````

Run specific steps:

```bash
./bootstrap.sh tree
./bootstrap.sh env
./bootstrap.sh projects
```

## Customization

All customization lives in `setup.py`.

- Directory structure is defined in `TREE`
- Git repositories are defined in `ENV_REPOS` and `PROJECT_REPOS`

To add or remove repositories or folders, edit those mappings directly.
No other files need to be changed.


## Notes

* Safe to run multiple times
* Safe to delete `~/dev` and re-run
* Intentionally boring by design
