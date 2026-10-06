# Experiment01 — declared before model predictions

One configuration: Qwen3-8B, rank16 LoRA, Adam learning rate0.0001, full batch47, three epochs (=three optimizer steps). All47 approved migrated examples appear in every step. The small corpus does not warrant sweeping hyperparameters. This is a new adapter from the same base, not continuation from the two-example smoke.

Run all16 frozen reviewed-pilot requests on the base before training, then on the trained checkpoint. Same prompt, tokenizer, renderer, temperature0, seed20261006, output ceiling512, scenarios, scorer and failure denominator. Save exact per-case outputs; never remove or retry a semantic error. Hash-bind inputs, code and configuration before spending.

Primary descriptive outcomes: intent exact match and end-to-end task success out of16. Show paired wins, losses, unchanged cases, schema failures and transport failures. Screening threshold: at least two additional task successes and no gold-constrained route-validity regression. Otherwise retain the base as the safer candidate; do not call one-step smoke or prompt improvements a fine-tuning gain.

This pilot is human-reviewed but not untouched: authored cases and corrections informed code/prompt semantics. No statistical generalization claim. An independently reviewed fresh final benchmark is still required for stronger claims. No further tuning on pilot outputs is authorized by this plan; any second experiment needs its own rationale fixed before running.

Reserve$1.25 from the already-approved$4 experiment stage, including two6hour checkpoint objects with512GB/object conservative storage allowances, plus training and both sampling batches. Prior$0.35 holds remain untouched. Maximum project commitments after reserving:$1.60. No top-ups, paid hosting or publication. The checkpoints are temporary6hour development artifacts, not a persistent public model service.

Context ceiling4096tokens, verified before live calls: full evaluation prompts plus512reserved output tokens exceed the earlier2048smoke ceiling for some cases. Neither training nor evaluation inputs are truncated.
