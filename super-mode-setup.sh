#!/usr/bin/env bash
# POSIX wrapper for super-mode-setup. Forwards all arguments to the
# Python script. Tries python3 first; falls back to python on PATH.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    exec python3 "${SCRIPT_DIR}/super-mode-setup.py" "$@"
fi

if command -v python >/dev/null 2>&1; then
    exec python "${SCRIPT_DIR}/super-mode-setup.py" "$@"
fi

echo "ERROR: no Python found on PATH. Install Python 3.11+ and re-run." >&2
exit 1
