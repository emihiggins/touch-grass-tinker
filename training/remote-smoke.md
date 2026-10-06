# Protected remote smoke — implementation checkpoint

## What is implemented

`liftlap.training_transport.TrainingTransport` uses the installed Tinker 0.32.0 request/response types with the existing protected `make_client()` (no plaintext credential fallback and client retries disabled). Training Datums come from the existing Cookbook renderer, not a new payload format.

Sequence: create tagged session → create LoRA model → forward/backward → optimizer step → save state with optimizer → restore state with optimizer → save sampler weights. The state and sampler checkpoints default to a one-hour TTL; the adapter permits at most 24 hours. Checkpoint overwrite is disabled. This is a transport component, **not an authorized live launcher**.

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
