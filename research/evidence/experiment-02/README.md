# Exploratory SFT02 result — 2026-10-09

**Completed real training: base10/16; trained10/16. No aggregate improvement.**
The application retains its base/offline configuration; this is not promotion evidence.

Emi explicitly selected exploratory retraining on the existing47 approved examples.
Qwen3-8B, rank16 LoRA, learning rate3e-5, three epochs, nine optimizer updates with
batches16/16/15. Every row appears once per epoch. Same prompt, renderer, sampling
seed/temperature and512-token output limit in this run's paired comparison.
The eight new unreviewed labels were excluded. No new untouched final set was used.

## Paired diagnostic comparison

- Both models succeed on10 of the16 previously exposed historical pilot cases.
- Paired gain: `eval-review-011`; paired loss: `eval-review-005`.
- Base:14 structurally/semantically accepted outputs, two semantic rejections.
- Trained:13 accepted outputs, two JSON/schema rejections and one semantic rejection.
- No observed gold-route-validity regression in this small pilot; this is not a
  real-world safety claim. All failures remain in the denominator.
- No transport failure, resubmission, automatic repair or repeat training run occurred.

This combined batch-size/learning-rate recipe cannot isolate the effect of either
change. Older pilot9/16 and fresh-base13/16 results concern other runs and/or cases;
they are not the paired baseline for this experiment. Historical reports are untouched.

## Reproducibility and cost

Preregistration commit `d593f4b` was pushed before paid submission. The exact plan
hash and all nine batch-ID lists are in `preregistered-plan.json`. Execution summary
confirms nine completed forward/backward operations and nine optimizer updates,
plus two saved checkpoints. Saved prediction texts are unchanged; transport IDs
and private checkpoint paths are replaced with hashes in committed evidence.
Both saved score reports reproduce offline from these predictions.

Current published prices yielded a conservative estimate of$0.9783, not an invoice.
The full$1.25 reservation remains unresolved. Total project commitments are$3.00,
including earlier$1.75 holds, against the$10 ceiling; no hold was released on an
assumption of free or failed work. Both temporary checkpoints expire six hours after
saving. No topup, public deployment or repository visibility change occurred.

Verification before launch:260 tests pass in the pinned environment; standard
release and secret scans passed. This consumes the second planned configuration.
Do not launch a third automatically. Next useful model work is reviewed data and
new evaluation preparation, not repeating this run for a better score.

## Follow-up diagnosis

[Case-level postmortem and data priorities](postmortem.md) distinguish blocked malformed outputs from accepted routes under incorrect extracted constraints. The aggregate10/16 tie remains unchanged.
