# Next model iteration: executable research plan

Status: **planned; no new run authorized by this document alone**. Queue, sequencing and budget ownership: [roadmap](../delivery/model-robustness-roadmap.md). Historical protocols remain immutable.

## M01 Target audit

Implemented offline 2026-10-08: [findings, limitations and reproduction](../research/evidence/model-robustness-m01/README.md).

**Hypothesis, not diagnosis:** malformed tuned completions may reflect target serialization, terminal handling or insufficient learning. The first run used three epochs of one 47-row batch: only three optimizer updates. That does not establish either overfitting or underfitting.

Saved tuned predictions contain five JSON objects followed by an extra quote (pilot004/009/010/013/016), and another schema failure (015). Their saved stop reasons are `stop`, with roughly 100–105 output tokens, below the 512 cap. Do not describe these as demonstrated truncation. Fresh-base errors include incomplete surface-lift expansion (005), unnecessary clarification despite an explicit eight-minute duration (010), and retaining a 45-minute UI default when the user declines to provide a budget (012).

**Implementation:** extend `liftlap/render_audit.py`, `corpus.py`, `training_preflight.py` and tests, reusing existing pinned renderer/mask checks. Produce a redacted per-row diagnostic manifest containing source/target hashes, tokenizer/renderer/SDK versions, assistant prefix length, weighted-token range, final token IDs, stop sequence and exact decoded target suffix. Compare the actual SDK training datum with audited shifted targets. Reconstruct all 47 targets and inspect duplicate serialization, quotes, boundary tokens and zero/incorrect loss weights. Analyze saved raw outputs separately from decoded/validated outputs; retain raw bytes and finish reasons.

Do not strip arbitrary trailing punctuation to pass evaluation. A recognized transport/model terminal token may be removed only by a documented, tested decoding rule; keep strict historical scores unchanged. Any exploratory repair score must be separately named and never substituted for task success.

- [x] Every eligible training row round-trips; prompt loss is zero and intended assistant tokens carry loss.
- [x] SDK-bound inputs/targets match audited hashes; malformed fixtures fail before submission.
- [x] Report accounts for all six tuned schema failures and three fresh-base failures, separating observation from causal hypotheses.
- [x] No frozen dataset, raw prediction or old score is rewritten.

## M02 Data and splits

Target **approximately 200–400 reviewed examples**, subject to useful coverage rather than padding to a quota. Provisional allocation at 400 total: 240 train, 80 validation, 80 final. Ratios/counts must be frozen before training and are not a claim of statistical power. Reuse existing reviewed rows only in training after audit; known historical evaluation cases remain diagnostic fixtures, not new holdout rows.

**Schema:** a versioned manifest tracks example ID, family ID, source/provenance, graph/context hashes, scenario tags, expected intent, reviewer identity/decision, approval hash and split. Family IDs group paraphrases, contrast pairs and shared scenario templates; split families, not individual rows. Deduplicate normalized text plus contexts; run similarity review for near duplicates. New final families/graphs should be independently authored where possible; if not, disclose same-author limitations.

Coverage: hard versus soft exclusions; all surface-lift subtypes; max versus preferred grades; green/blue and native regional grades; multiple preferences without inferred variety; short/long/unknown budgets; explicit correction of UI defaults; missing time versus missing place; negation, contradictions and out-of-domain requests; unfamiliar names and IDs; disconnected destinations and closures. Balance ready/clarify and positive/negative examples. Keep personally identifying trip data out of fixtures.

**Implementation:** extend corpus/review/export tools and `benchmark/v2` conventions without changing frozen directories. New candidates live under a new versioned iteration directory. Generate blind-first review packets; export only approved exact-hash rows. Reserve final labels/predictions from training and checkpoint-selection tooling. A final set viewed for error-driven development becomes diagnostic and must not be represented as untouched again.

- [ ] Split manifest has zero cross-split family overlap; duplicate/similarity report is reviewed.
- [ ] Every exported row is human-approved against current request/context/label hashes.
- [ ] Coverage report flags missing or sparse categories rather than implying representativeness.
- [ ] Final split is frozen before candidate evaluation; candidate selection uses validation only.

## M03 Bounded SFT

Keep the pinned Tinker/Cookbook path and existing spend/transport wrappers. Do not replace training infrastructure to conduct a small experiment.

**Predeclare one configuration** after M01/M02 and R03. Keep model, LoRA rank, prompt and decoding fixed against the matching base. Suggested hypothesis for the remaining configuration: smaller minibatches with more updates and a lower learning rate than the historical 1e-4. Provisional values are batch16, LR3e-5, rank16, maximum three epochs, checkpoints after each epoch. These are proposed values, not proven optimal parameters or a runnable authorization. Freeze exact values after offline token/cost feasibility; do not change them mid-run based on final results.

The loader must support the final partial batch: every example exactly once per epoch, no hidden dropped tail. If the pinned loader cannot, implement/test explicit tail handling or choose an audited divisible batching strategy without duplicating data silently. Record actual shuffle mechanism and seed behavior; verify resume restores optimizer, step, data/config hashes and random state where relevant. Audit context ceiling with no truncation.

Evaluate the fixed base and each retained checkpoint on validation. Select by the preregistered critical-constraint gate, then task success, then syntax rate; prefer the base on ties. Account for all checkpoint sampling/storage costs. Final evaluation is one locked comparison on the new untouched final split after candidate selection. Record paired wins/losses and uncertainty; 16-case historical differences do not establish significance. If no tuned checkpoint passes validation, stop and report failure rather than tuning against final labels.

Ablations belong in a **later** separately preregistered run: vary only learning rate or update budget while holding the other constant. This initial minibatch/LR change tests a combined recipe, not an isolated causal claim. No rank/model-size/hyperparameter sweep hidden inside the current allowance.

- [ ] Run manifest freezes dataset/prompt/render/scorer hashes, parameters, selection and stop rules before paid submission.
- [ ] Offline rehearsal proves full row coverage, tail/resume behavior and budget bounds.
- [ ] Persistent reservation includes base/validation/final sampling and finite checkpoint expiry.
- [ ] All submitted attempts and all validation checkpoints appear in results; no retries cherry-picked out.
- [ ] R03 promotion gates decide deployment; failed tuning leaves the base active.

## M04 Constrained output

Existing-solution preflight (2026-10-08): [XGrammar documentation](https://xgrammar.mlc.ai/docs/latest/) identifies an open-source structured-generation library (documentation version 0.2.8). The [vLLM structured-output documentation](https://docs.vllm.ai/en/latest/features/structured_outputs/) fetch was rate-limited; current integration was not verified. Tinker structured-decoding capability is **unresolved**, not assumed supported. Check the pinned SDK schema and official documentation before proposing an adapter.

First create a capability matrix: backend/version, supported JSON Schema subset, enums/nullable fields, stop behavior, streaming, hardware/runtime requirements and license. Prefer a maintained supported integration; do not build a custom grammar engine. If Tinker lacks support and no suitable local backend is available, document the feasibility blocker and continue R01/R02. No new paid service or GPU assumed.

If feasible, compare unconstrained versus constrained decoding with identical model/prompt/cases, on development/validation only, as a separately budgeted inference experiment. Preserve semantic checks: grammar can guarantee shape only within its supported schema, not correct time, exclusions or graph identifiers. Unsupported schemas must fail configuration explicitly, not silently degrade.

- [ ] Capability evidence is pinned and a local malformed-schema/unsupported-feature probe passes.
- [ ] Both arms report syntax, semantic and end-to-end outcomes, latency and token costs.
- [ ] Strict parsing remains; syntactically valid but wrong outputs do not count as successes.
- [ ] Integration is optional and reversible; absent backend does not break offline mode.
