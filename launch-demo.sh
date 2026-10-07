#!/bin/sh
set -eu
# Resolve the package directory independently of the caller's working directory.
cd -P -- "$(dirname -- "$0")"
if command -v python3 >/dev/null 2>&1; then
  interpreter=python3
elif command -v python >/dev/null 2>&1; then
  interpreter=python
else
  echo "Lift-Lap needs Python 3.11 or newer. Install Python, then run this file again." >&2
  exit 1
fi
"$interpreter" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "Lift-Lap needs Python 3.11 or newer.")'
exec "$interpreter" -m liftlap.server "$@"
