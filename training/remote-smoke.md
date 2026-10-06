# Protected remote smoke — implementation checkpoint

## What is implemented

`liftlap.training_transport.TrainingTransport` uses the installed Tinker 0.32.0 request/response types with the existing protected `make_client()` (no plaintext credential fallback and client retries disabled). Training Datums come from the existing Cookbook renderer, not a new payload format.

Sequence: create tagged session → create LoRA model → forward/backward → optimizer step → save state with optimizer → restore state with optimizer → save sampler weights. The state and sampler checkpoints default to a one-hour TTL; the adapter permits at most 24 hours. Checkpoint overwrite is disabled. The transport is now wrapped by `liftlap.training_smoke`, a hash-bound, metered two-example integration launcher. It does not launch the full experiment.

Every mutation is journaled and fsynced before submission. Future IDs are persisted before polling. Polling is bounded; transport errors, provider failures, cancellation and timeout halt the instance. An existing journal cannot be reused, and ambiguous mutations are never retried automatically. Error bodies and credentials are not journaled. The local journal can contain private session/model/checkpoint IDs and belongs under ignored `runs/`.

## Verified offline

HTTP mock tests exercise the real pinned SDK wire serialization, protected-header seam and response parsing:

- model creation, state checkpoint → optimizer restore → sampler checkpoint;
- increasing model sequence IDs and explicit checkpoint TTL;
- real protobuf forward/backward submission and response parsing;
- Adam optimizer serialization;
- bounded pending-future timeout, no resubmission after timeout;
- ambiguous model submission attempted once and transport halted;
- journal restart refusal and sanitized failure recording.

These tests do **not** prove a remote training update, checkpoint restore equivalence or usable trained sampler. There is no real trained checkpoint yet.

## Remaining before the live smoke

1. Available account credits confirmed by Emi: $10 at 21:55 UTC. Auto-top-up status remains unknown; do not enable or rely on top-ups. Retain the authorized $10 total project cap, including prior usage.
2. Reconcile historic/ambiguous sampling charges. The October 6 read-only account window returned six priced sampling events totaling $0.004948914 with `cost_data_through=null`. That is provisional account-wide usage, not a project invoice. The previous conservative completed-call estimate is $0.00988101; neither proves that rejected submissions were free.
3. Verify current training/checkpoint/storage prices and a conservative checkpoint-size bound. TTL limits duration, not byte size or operation charges.
4. Add the launch wrapper that validates data/config evidence, reserves the entire smoke cost in the shared ledger **before session creation**, checks configuration/run counts and writes result/checkpoint artifacts. This adapter must not be invoked as an unmetered shortcut.
5. Run at most the planned bounded smoke, retain its ledger reservation until billing is reconciled, and validate the restored sampler before experiments. Use the pilot only with its disclosed limitations; stronger independent performance claims still need a fresh final benchmark.

No live CLI is exposed yet. To verify offline:

```sh
.venv-tinker/bin/python -m unittest discover -s tests -p 'test_training_transport.py'
```


## Metered launcher (current)

`python -m liftlap.training_smoke --run-dir runs/<new-dry-name>` prepares the exact two-example plan. Live mode requires its `--plan-sha256`, matching data/config/code hashes, user credit evidence and a shared SQLite ledger with prior usage accounted for. The launcher reserves $0.25 before session creation and never reuses a run directory. Total runtime is bounded to15minutes; transport submissions have no automatic retry.

The first prior-usage entry is a $0.10 **unreconciled hold**, not an invoice assertion. The sum of full saved live-run upper estimates plus the diagnostic request bound is below that hold (see `research/evidence/smoke-budget-bound.json`). This permits conservative budget accounting while the provider invoice is delayed; it does not label rejected calls free. Both holds remain until billing evidence supports settlement.

The fixed smoke saves two1hour checkpoint objects and budgets512decimalGB per object—more than a full10B-parameter state at32bytes/parameter with margin, far above the expected rank16LoRA payload. Its cost upper estimate is about$0.144, including training and one512-token sample; the reservation is$0.25. No full-model performance or exact restored-weight-equivalence claim follows from this integration smoke. Auto-top-ups are neither enabled nor relied on.

Earlier remaining-work lists above describe pre-launch preparation. Full experiments still require stronger evidence and their own gated launcher; this smoke deliberately does not consume or tune on frozen evaluation cases.


### First live attempt and explicit recovery

The first forward/backward completed remotely, but its5second read timed out. A read-only retrieval of the saved future confirmed completion, then the optimizer step was submitted once and completed. The state-save future likewise completed after a read timeout; its saved URI was recovered by read-only inspection. No forward/backward, optimizer or state-save mutation was replayed.

The old-model restore endpoint returned HTTP400 before a future ID. The installed SDK's create-via-load path restores into a fresh model using session_id/model_seq_id and optimizer=True; this is the supported recovery being validated. Remaining future reads use30seconds, with submissions still non-retrying. Exact private journals live in ignored `runs/training-smoke-live-001/`; sanitized results are published only after the run ends.


## Observed result — first live smoke

**Incomplete.** Real forward/backward and optimizer step completed for two examples; the one-hour state checkpoint was saved. Old-model restore was rejected before a future ID. Fresh-model restore was submitted, but bounded read-only retrieval never produced its result. No sampler checkpoint or sample was produced. Do not claim this is a successful training/save/restore/sample smoke or a measured fine-tuning gain.

`research/evidence/training-smoke-result.json` is the sanitized record. Private request IDs, checkpoint URI, journals, exact original source snapshot and narrowly scoped one-time recovery scripts remain in ignored `runs/training-smoke-live-001/`. Mutations were not replayed. The $0.25 reservation remains held, alongside the $0.10 prior-usage hold. These are commitments, not verified charges.

The reusable transport now uses the SDK's fresh-model restore addressing and30second bounded future reads; it retries only reads, never mutation submission. Offline tests cover both corrections. The original smoke input/source hashes are retained in the private snapshot. Do not rerun an expired dry plan: changed code invalidates it. The next action is to inspect the existing restore future, not begin another training run.
