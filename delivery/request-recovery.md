# Terrain and request recovery

## Findings
- Interpretation completion unconditionally re-enabled its submit button, including while a different terrain was loading.
- Failed terrain fetches left the previous SVG visible and enabled interpretation without a current graph.

## Fix
A shared submit-state rule requires a loaded graph, no pending terrain load and no pending interpretation. Terrain loads clear stale graphics and provenance. Failures expose a specific retry action; stale generation results never replace the current terrain or confirmed plan. Retries fetch terrain only, not model inference.

## Evidence
`browser-recovery.cjs` intercepts actual API requests and releases held responses in controlled order. It verifies failed-load cleanup, successful retry, old interpretation completion during new terrain loading, out-of-order terrain responses and plan completion after settings change. Response completion and browser frames are awaited before assertions. Existing map/accessibility/demo checks and release gates remain required.

No new runtime library: native fetch, existing generation counters and native buttons suffice. No provider calls or additional spending.
