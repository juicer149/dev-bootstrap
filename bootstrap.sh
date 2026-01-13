#!/usr/bin/env bash
# =========================================================
# Bootstrap entrypoint (Dev Environment ABI launcher)
#
# Role
# ----
# This script is the *stable, boring entrypoint* for
# invoking the developer environment procedure.
#
# Responsibilities:
#   - Select *which* procedure to run
#   - Ensure minimal system prerequisites exist
#   - Delegate all logic to the Python ABI facade
#
# Non-responsibilities:
#   - No environment logic
#   - No configuration
#   - No discovery or guessing
#   - No orchestration
#
# This file must remain boring.
# =========================================================

set -euo pipefail

ACTION="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------
# System prerequisites
#
# These are *bootstrap-level* requirements only.
# Environment-specific dependencies belong in setup.py
# or in repository install hooks.
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# Delegate to ABI facade
# ---------------------------------------------------------

python3 "${SCRIPT_DIR}/setup.py" "${ACTION}"
