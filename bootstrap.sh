#!/usr/bin/env bash
# Bootstrap entrypoint for developer environment setup.
#
# Responsibilities:
# - select *what* setup step to run
# - ensure required system dependencies exist (git, python3)
# - delegate all logic to setup.py
#
# Interface:
#   ./bootstrap.sh [tree|env|projects|all]
#
# This file should remain boring.

set -euo pipefail

ACTION="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -------------------------------------------------------------------
# System dependencies
# -------------------------------------------------------------------
# Declarative list of required commands.
# Installation is performed in a single apt invocation if needed.

# Add any required packages here for the bootstrap process.
# These should be minimal. Pakages needed for the env setup itself
# should be handled in setup.py.
REQUIRED_PKGS=(git python3)
MISSING_PKGS=()

for pkg in "${REQUIRED_PKGS[@]}"; do
  if ! command -v "$pkg" >/dev/null 2>&1; then
    MISSING_PKGS+=("$pkg")
  fi
done

if [ "${#MISSING_PKGS[@]}" -ne 0 ]; then
  sudo apt update
  sudo apt install -y "${MISSING_PKGS[@]}"
fi

# -------------------------------------------------------------------
# Delegate to Python facade
# -------------------------------------------------------------------

python3 "${SCRIPT_DIR}/setup.py" "${ACTION}"
