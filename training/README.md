# Training and model research

This directory preserves the completed Tinker experiments and their reproducibility artifacts. It is not required to run the default offline app. Start with the [developer guide](../docs/development.md) and [evaluation summary](../docs/evaluation.md).

## Completed work

- 47 reviewed/migrated training examples, with the overlapping original candidate009 excluded.
- Pinned Qwen3-8B tokenizer, Tinker SDK and Cookbook renderer; assistant-only target masks and context lengths audited.
- A real training/checkpoint/optimizer-restore/sampler smoke completed. Its one output was schema-valid but semantically wrong.
- One preregistered full-data experiment:47 rows per batch, three training passes, rank16 LoRA. On the16-case pilot, base9/16 vs tuned7/16; tuned checkpoint rejected.
- The retained base achieved13/16 on a separate frozen human-reviewed set. No further tuning used those outputs.

## Protocols and evidence

- [Full-data preregistered protocol](experiment-01.md) and [results](../research/evidence/experiment-01/README.md).
- [Fresh evaluation approvals](final-review.md), [freeze](../benchmark/v2/final-review/freeze.json), [results](../research/evidence/fresh-base-evaluation/README.md).
- [Original review packet](review-packet.md), [v2 pilot review](evaluation-review-v2.md) and [data index](../benchmark/v2/README.md).
- `render-requirements.lock`, `tokenizer-manifest.json`: pinned optional research environment.
- `sft-plan*.json`, `batch-rehearsal.md`, `remote-smoke.md`, `sampling-runner.md`: dated plans/checkpoints. They are not proof of a permanent deployed trained model.

## Reuse safely

Saved results can be scored without provider access. Live execution requires optional dependencies, a compatible protected provider setup, a new owner-authorized budget/ledger and an explicit run plan. The original project's authorization is historical evidence—not permission for a contributor to spend money. Do not reset the ledger or reuse run keys to repeat paid work.

One-hour smoke and six-hour experiment checkpoints were temporary. Do not assume old checkpoint paths remain usable. No model weights or reusable trained deployment are bundled.

For ordinary development, use the offline modes and `python3 scripts/check_release.py`. Completed protocols and immutable evidence are preserved; do not interpret their original pending gates as current task assignments.
