# Exploratory SFT 02 — preregistration, 2026-10-09

Emi explicitly selected **Exploratory retraining now**, Telegram message2692.
This authorizes the existing47 approved examples, not the eight unreviewed candidates.
This is the second and last planned configuration in the original two-configuration
experiment allowance. No additional configuration is implied.

Freeze Qwen3-8B, rank16 LoRA, three epochs, batch16 with explicit final15, learning
rate0.00003, context4096, same prompt/renderer/temperature0/seed20261006/output512.
Exactly nine optimizer updates; every row once per epoch. Shuffle index lists use
Python random.Random(epoch).shuffle and are hash-bound in the dry manifest. The
pinned renderer supplies the Datums; an explicit batch schedule avoids the Cookbook
loader's dropped tail. No truncated inputs, duplicate padding or automatic resume.
This changes both batching and learning rate; it is a combined-recipe experiment.

Run all16 already-exposed historical pilot cases on current base before training
and the fixed epoch3 checkpoint afterward. No checkpoint selection, new final test,
independent generalization claim or promotion. Always retain the application base.
Store all outcomes, including transport and semantic failures. Stop on uncertain
submissions; never resubmit mutations or repeat a run for a better result.

Reserve $1.25 in the existing experiments stage, including training, 32 maximum
sampling attempts and two six-hour checkpoint objects (512GB per object upper
allowance at $0.10/GB/month). Existing $1.75 holds remain untouched: total becomes
$3.00, below the $10 cap; experiment commitments become $2.65 below $4. No topups.
Current public prices and read-only protected SDK access verified2026-10-09.
Credit evidence remains Emi's Oct6 $10 report, not a current billing API response.
Insufficient-credit rejection stops the run; authorization does not permit topups.

The live command requires the exact dry-plan hash; a stable experiment ledger key
prevents a repeat under another directory. Deadline30minutes. An ambiguous result
remains reserved and awaits read-only reconciliation; optimizer steps are not retried.
Temporary checkpoints expire after six hours; they are not a deployed model service.
