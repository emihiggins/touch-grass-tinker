#!/bin/sh
set -eu
if command -v python3 >/dev/null 2>&1; then exec python3 -m liftlap.server "$@"; fi
if command -v python >/dev/null 2>&1; then exec python -m liftlap.server "$@"; fi
echo "Lift-Lap needs Python 3.11 or newer. Install Python, then run this file again." >&2
exit 1
