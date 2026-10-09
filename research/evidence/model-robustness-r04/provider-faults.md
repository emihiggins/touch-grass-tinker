# R04 offline provider faults and recovery

This checkpoint reuses the pinned SDK's existing `httpx.MockTransport`, asyncio
and SQLite. No provider request, billing query or real reservation was made.
Fixtures use a temporary ledger and synthetic credential sentinel only.

## Evidence

`tests/test_runtime_faults.py` exercises twelve SDK wire fault combinations:
429, 503, 404, connection/read failure, read timeout, and malformed JSON,
each at submission and at retrieval after a returned future ID. Every combination
makes exactly one sampling submission, performs no submission retry, preserves
all-case accounting and stops subsequent cases. 404 is a generic missing-resource
simulation, not proof of a provider's exact expired-checkpoint response.

A coroutine that returns a future ID then stalls hits the configured deadline
(default unchanged at 90 seconds; test override 0.01 seconds). Its full budget
reservation survives reopening the ledger and prevents an over-budget next attempt.
An independent subprocess exits immediately after committing a reservation: the
restarted ledger retains the hold. Two separate processes racing to reserve more
than the remaining stage allowance cannot both succeed. These are local commitment
checks, not provider-enforced spending limits or machine power-loss guarantees.

A failed live adapter rejects a second live request without another `_run` call.
Explicit Rules selection still produces an editable offline interpretation, with no
automatically planned route. This rehearses manual offline recovery, not a deployed
model-feature-flag rollback or provider cancellation.

## Diagnostic stream

New `diagnostics.jsonl` entries contain only version, SHA-256 of the run ID, attempt
index, elapsed milliseconds, typed outcome/failure category, whether a returned
future ID was observed, `automatic_retry: false`, and a statement that the runner
does not settle reservations. No raw user text, model output, exception message,
credential, provider ID or endpoint appears in this stream. Hashes are correlation
keys, not a claim of anonymization. No future ID observed does **not** establish
that the provider rejected or never charged a submission.

Existing private research `predictions.jsonl` / `events.jsonl` and live-app request
artifacts are unchanged and may contain raw outputs, requests and provider IDs;
they must not be mistaken for redacted telemetry or shared as such. These diagnostics
are not durable billing evidence. A process termination may leave no terminal event.
Use the existing manifest for model/config hashes; this checkpoint does not add a
telemetry aggregation service or claim measured fallback/rejection rates.

## Remaining scope

R04 remains partial. Header trickling, planner CPU deadlines, provider cancellation,
full feature-flag rollback and real provider behavior are not established here.
No paid fallback, retry policy, budget settlement or historical artifact changed.

## Verification result

Pinned optional environment: all 256 tests pass (including the 12 SDK fault
combinations). Standard release: 256 run, 26 optional skips, zero failures.
Targeted final fault assertions: five tests pass. Historical R03 artifacts reproduce,
saved fresh base remains 13/16, and isolated packaging is deterministic. No UI source
changed, so existing browser evidence was not recaptured or relabeled.
