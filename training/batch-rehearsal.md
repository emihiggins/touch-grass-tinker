# Offline Cookbook batching and resume-cursor rehearsal

This milestone reuses `SupervisedDatasetFromHFDataset` from the pinned official Cookbook. It adds no training service and makes no provider calls. Candidate labels remain unapproved, including quarantined candidate 009. This is an inspection of local data flow, not a training export.

## What it closes

- Verify real Cookbook batches contain the intended SDK Datums in order.
- Reject a batch size that silently discards the tail: 48 candidates / planned batch 32 would drop 16.
- Exercise an explicit **rehearsal-only batch size 16**, covering all 48 candidates in three batches. The canonical SFT plan remains unchanged; finalize batching after data review.
- Use the actual Cookbook training-loop shuffle policy (`set_epoch(seed=epoch_idx)`). Its default loop does **not** consume our plan's `shuffle_seed`. The report records this mismatch so future integration cannot pretend that field was honored.
- Bind the batch schedule to cases/labels, exact token payloads and weights, prompt, config, renderer code, tokenizer manifest and environment lock.
- Reconstruct the suffix after a local step cursor only when the expected schedule hash matches; changed labels/config/tokens refuse continuation.

## Reproduce without API access

```bash
.venv-tinker/bin/python -m liftlap.training_rehearsal --batch-size 16 > /tmp/liftlap-batch-plan.json
# A cursor rehearsal after the first batch; no checkpoint is loaded:
PLAN_SHA=$(python3 -c 'import json; print(json.load(open("/tmp/liftlap-batch-plan.json"))["plan_sha256"])')
.venv-tinker/bin/python -m liftlap.training_rehearsal --batch-size 16 --start-step 1 --expected-plan-sha256 "$PLAN_SHA"
```

Omitting the override refuses the current tail-dropping configuration. Non-training partitions, duplicate IDs, invalid batch sizes and out-of-range cursors fail. Unit tests exercise actual Cookbook batching and deterministic continuation, not a reimplementation of its shuffle.

Evidence: [batch schedule](../research/evidence/training-batch-rehearsal.json). All output retains `launch_authorized: false`, `provider_calls: 0`, and `checkpoint_loaded: false`.

## What it does not close

This is **not remote checkpoint/resume proof**. The installed Cookbook already supports training checkpoints and optimizer restoration; prefer adapting that implementation over writing a second trainer. Before invoking it, resolve the protected-auth compatibility path, launch gates, finite budget/accounting, checkpoint identity and ambiguous remote-call recovery. A local cursor must never be used to guess whether a remote optimizer step completed.

The next provider milestone is a bounded, separately authorized training → state save → optimizer restore → sampler export → sample smoke. It requires approved data and exact hashes. Do not run `tinker_cookbook.supervised.train.main` directly as a workaround: it constructs its own ServiceClient and does not inherit our sentinel-auth and budget controls. No turnkey live training command is delivered here.
