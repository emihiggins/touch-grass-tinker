# Granular evaluation and promotion v1 (R03)

Implemented 2026-10-08. This is an **offline report contract for intent v2**, not a runtime change or a new score for historical claims. Entry points: `liftlap.evaluation_v3`, `liftlap.promotion`, `scripts/score_robustness_history.py`. It reuses the standard-library corpus audit, strict intent validator, deterministic planner and independent route validator; no new framework/dependency is needed.

## Inputs and identity

A scoring run consumes reviewed cases, a hash-frozen graph/case manifest, saved raw predictions, and a separate run manifest. The manifest must name a unique `run_id`, explicitly assign every case ID in frozen order, and declare lane `primary` or `fallback`. Predictions may be missing but cannot have unknown/duplicate IDs. Each retry/repeat is a separate run; `collect_runs` requires exact agreement with the expected run inventory. It cannot discover omitted runs outside that inventory: the experiment runner must provide the complete journal-derived inventory.

The report binds canonical case/graph/freeze/prediction/manifest hashes, scorer and dependency source hashes, and an integrity hash of its complete contents. It carries model/version, prompt/renderer hashes, decoding (including seed), and version-only environment metadata from the run manifest. Unknown historical metadata stays null. Do not place credentials, environment-variable dumps or personal requests in manifests.

A report checksum detects edits, not authenticity or proof of chronological preregistration. M03 must freeze its run manifest and inventory before submission. The policy file is [promotion-policy-v1.json](../training/promotion-policy-v1.json); its canonical JSON digest must be bound to new runs. Historical freezes lacking `evaluation_partition` are **historical_diagnostic**, never validation/final promotion evidence.

## Denominators and metrics

- Every assigned case remains in every case-rate denominator. A missing prediction is a failure, not a skipped row. Transport completion, JSON syntax, schema, exact intent and task success are separate counters/rates.
- Strict JSON rejects extra trailing punctuation, duplicate keys and nonfinite constants. Scoring parses raw strings again; it never trusts a saved parsed `intent` or strips punctuation. Output hashes bind the exact saved UTF-8 string. Missing/unknown/non-stop completions cannot succeed even if their JSON happens to validate.
- Per-field accuracy uses normalized validated intent values and the full assigned denominator. Invalid/missing outputs get no correct fields. Set order and equivalent timezone offsets normalize using the original contract.
- Exclusion-set precision/recall is micro-averaged over true/false positive/negative elements. Invalid/missing outputs contribute an empty predicted set. Empty precision/recall denominators are null, not perfect scores. Report schema coverage alongside these ratios.
- Hard-max violations include raising the reviewed ceiling or supplying a ceiling when the reviewed value is unknown. Hard-exclusion violations count cases omitting at least one reviewed hard exclusion. Critical extraction failures also include ready output when clarification/unsupported was required, or an accepted route invalid against reviewed intent.
- Clarification false positives/negatives compare clarify versus non-clarify status. Clarification correctness additionally requires the exact requested field set. Unavailable output with expected clarification counts as a false negative; other unavailable outputs are not declared correct.
- Typed scorer-only semantic observations flag a retained value in a requested clarification field or a missing value omitted from clarification. These prevent task success/planning in this scorer, **not in the unchanged live adapter**. R01 will implement the versioned runtime semantic/provenance contract.
- Route proposals come only from deterministic graph search. The independent validator checks the proposal against predicted intent (simulated acceptance/interception) and separately against reviewed intent (reference correctness). A gold/reference rejection is **not** a runtime safety interception: the live app has no gold label. These are offline simulated routes, not observations of delivered real-world routes. No-route/operational-limit outcomes remain distinct from malformed/semantic output.
- Task success requires exact intent, matching expected planner outcome, and no accepted route invalid against reviewed constraints. Runtime percentiles use nearest-rank p50/p95 over observed durations, including failed attempts; missing latency is counted explicitly. Token totals expose observed sums, coverage, and null complete totals when incomplete. Known prompt tokens on a failed submission are not proof of billed input.
- Reserved/reconciled costs are metadata, never inferred billing. Unknown costs remain null, and shared experiment reservations must not be charged again to each sampling arm. Collection separates primary/fallback lanes and preserves costs by run.

All case metrics are also broken down by scenario and family with sample counts. Repeated runs require the same primary cases, graph and model/prompt/renderer/decoding configuration. Agreement requires every repeated output to complete with a valid schema; all-failed repeats have zero agreement and zero correctness. Consistently wrong outputs can have perfect agreement but low task success. The reporting helper does not reserve money or authorize an experiment.

## Promotion state machine

`decide` consumes two integrity-checked reports, the exact supported policy and candidate-bound mandatory-regression evidence. It has no deployment side effects.

1. **Validation:** matching frozen cases/graphs, scorer/dependencies and base-model/prompt/renderer/decoding comparison; primary validation reports; policy-bound complete provenance; a complete passing regression inventory with zero accepted-route violations; no new critical extraction regressions; at least two more task successes and no lower strict schema rate. Otherwise retain base. Ties retain base.
2. A passing validation decision is `eligible_for_final`, **not promotion**. Its hash, base/candidate versions and comparison configuration lock selection.
3. **Final:** distinct final cases with matching frozen base/candidate comparison, the same locked versions/configuration and validation-decision hash on both manifests; mandatory regressions; no new critical regressions/accepted-route violations; at least one more task success. Only then return `promote_candidate`. Missing, mismatched or failing evidence retains base. Final failure records `reject_candidate_no_retuning_on_final`.

Regression evidence must enumerate exact expected case IDs and outcomes, candidate version, policy hash and suite-source hash. A bare `passed: true` is insufficient. R02/M03 must supply real suite/run artifacts; synthetic gate fixtures are not deployment evidence. Qualified terrain activation remains separate (D01).

Decisions include reasons, paired wins/losses, new critical regressions, report/evidence hashes and sample/discordant-pair counts. These operational gates do not claim statistical significance; the small authored corpus and paired outcomes must remain visible. Reports do not establish operational safety or qualified resort access.

## Reproduction and tests

```sh
python3 scripts/score_robustness_history.py --output /tmp/touch-grass-r03-new
python3 -m unittest discover -s tests -p test_evaluation_v3.py -q
```

The history command refuses an existing output directory and produces all three saved-run reports, an exact attempt inventory, old-versus-new counts and a machine-readable **retain_base** decision. It does not rewrite original artifacts. See [R03 evidence](../research/evidence/model-robustness-r03/README.md).

For a new run:

```sh
python3 -m liftlap.evaluation_v3 --cases CASES --graphs GRAPHS --predictions PREDICTIONS --freeze FREEZE --manifest RUN_MANIFEST
python3 -m liftlap.promotion --base BASE_REPORT --candidate CANDIDATE_REPORT --phase validation --regressions REGRESSION_EVIDENCE --policy training/promotion-policy-v1.json
```

Final comparison adds `--phase final --validation-decision VALIDATION_DECISION`. No CLI launches sampling, training, fallback or deployment.
