# Offline demo startup improvement — 2026-10-07

Implemented on dedicated branch `improve-offline-startup`:

- Added `--version`, validated port range, exact loopback URL startup output, friendly occupied-port recovery, and exit status 2 without terminating another process.
- Added dependency-free `launch-demo.sh` and `launch-demo.bat`; the ZIP preserves the shell helper executable bit.
- Updated START-HERE, demo README, and developer setup documentation.

Verification:

- Actual extracted ZIP launched from `/tmp/lift lap.*` with `sh ./launch-demo.sh --port 18768`, served HTTP successfully, and shut down cleanly.
- Occupied-port diagnostic and invalid-port error verified; Windows execution not claimed.
- `scripts/package_demo.py` and `scripts/check_release.py` passed offline, including deterministic archive checks and no provider calls.
- Server tests passed with loopback proxy bypass; gitleaks binary was unavailable in this runtime, so the previously recorded secret scan remains the latest available scan.

No provider calls, spend, visibility change, or public publication.
