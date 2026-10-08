# R04 bounded local HTTP ingress checkpoint

The standard-library `ThreadingHTTPServer` spawned unbounded handler threads and
`server.timeout = 5` did not constrain reads within handlers. No new framework is
needed: `BoundedHTTPServer` caps admission before creating threads.

## Declared local-demo capacity

Frozen defaults live in `liftlap/http_limits.py`: eight active connections, OS
listen backlog eight, existing 16,384-byte body limit, five-second socket idle
limit and five-second absolute body-read deadline. There is no application queue.
These are conservative limits for one user and a handful of concurrent browser
assets, not measured production capacity. The existing adapter permits only one
live model request concurrently and retains its existing 90-second sample bound.
A 25-call local rules-dispatch observation measured median 0.059 ms and maximum
2.423 ms; this excludes network/provider time and does not validate remote latency.
The five-second body allowance covers local interactive JSON submission, not model
execution. Tests override it to 0.3 seconds for deterministic fault injection.

## Proven checks

- Excess connections receive 503 before parsing or dispatch; no queued model call.
- Partial body timeout returns 408 with `body_timeout`; partial progress does not
  reset the absolute body deadline. EOF returns 400 `incomplete_body`.
- Duplicate/missing/invalid Content-Length and Transfer-Encoding are rejected;
  oversized bodies return 413 before dispatch. No submitted text is echoed.
- A stalled request releases capacity; a following complete request succeeds.
- Existing browser recovery suite passes against the new server: failed, delayed,
  out-of-order terrain/plan responses cannot publish stale routes. See
  `request-recovery.json` and the fresh `recovery.png` capture.

Browser reproduction used `scripts/browser-recovery.cjs` with only the loopback
port changed to 8771 and output redirected here; a final screenshot was added.
No UI sources or old screenshots were altered. Current-media provenance records
this compatibility review rather than pretending the old images were recaptured.

## Explicit remaining work

This is **not completion of R04**. Header reads have an inactivity timeout, not an
absolute whole-header deadline; trickled headers can occupy at most the configured
slots. Busy-response writes also have a socket timeout. The backlog is an OS hint,
not an application request queue guarantee. There is no new CPU-planner deadline,
provider cancellation proof, structured event telemetry, paid-fault matrix, or
rollback/spend-restart rehearsal in this checkpoint. Client disconnection does not
prove cancellation or zero provider cost. No retry, paid fallback, settlement,
model configuration, training or real-terrain activation changed.

## Release verification

251 tests passed in the pinned optional environment; standard release suite ran
251 with 25 optional skips and zero failures. Historical report reproduction and
saved base 13/16 remain unchanged. The isolated archive reproduced identically;
its packaged HTTP asset probe now uses `BoundedHTTPServer` too. Fresh browser
recovery reported zero page errors and zero provider calls. Screenshot inspected.
