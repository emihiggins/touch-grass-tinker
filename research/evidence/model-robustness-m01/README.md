# M01: target and terminal-token forensic audit

Completed 2026-10-08, offline. No provider calls, spending, new labels or model promotion.

## Findings

- All **47** eligible reviewed training rows round-trip exactly through the pinned Qwen renderer. Prompt loss is zero; all intended assistant tokens, including the terminal token, receive uniform normalized loss. The shifted target range and SDK Datum hashes are recorded per row in [targets.json](targets.json).
- The reconstructed targets end with the renderer's `<|im_end|>` token (151645), not an extra quote or double-serialized JSON string. All targets fit the historical context/output limits. This does **not** establish the cause of model errors.
- A mock HTTP transport test sends all 47 reconstructed Datums through the installed SDK's actual protobuf serialization path. Decoded input tokens, target tokens and weights match the audited canonical hashes exactly. No remote training occurs. Corrupted targets, prompt leakage, zero weights and non-finite weights fail validation.
- The historical dataset, prompt, configuration, tokenizer manifest and dependency-lock hashes still match the experiment manifest; see [provenance.json](provenance.json). This is a local reconstruction: no historical wire capture or sampled output token IDs exist in the saved evidence, so historical remote receipt and the cause of extra quotes cannot be proven.

## Saved-output inventory

[Tuned outputs](tuned-outputs.json) account for every one of the 16 assigned pilot cases, including all six strict failures:

- `eval-review-004`, `009`, `010`, `013`, `016`: a JSON object followed by one extra quote; strict parsing fails.
- `eval-review-015`: valid JSON, but `ready` coexists with the unsupported preference `live_grooming`; schema validation fails.
- All six record `stop`, at 100–105 output tokens, below the 512 cap. These are not demonstrated truncation failures.

[Fresh-base outputs](base-outputs.json) account for all 16 cases and isolate three label mismatches:

- `final-review-005`: only magic carpet excluded; the reviewed surface-lift exclusion also requires t-bar, platter and rope-tow.
- `final-review-010`: duration is correctly extracted as eight minutes, but the model unnecessarily asks to clarify it. Extraction validity must remain separate from route feasibility.
- `final-review-012`: clarification is requested, but the 45-minute context default remains despite the request withholding a budget.

These observations seed M02 coverage and R01 regression fixtures. Insufficient learning, serialization behavior during generation and terminal-token handling remain hypotheses. Three historical optimizer steps do not prove underfitting or overfitting.

## Evidence and privacy boundaries

The manifest contains source/target hashes, counts, suffixes and versions, not request text or full targets. Suffixes come only from the existing reviewed fictional corpus; this command is **not** a general personal-data redactor. Do not publish its output for private request datasets without review.

Raw prediction files are unchanged. Per-output hashes bind the exact saved string encoded as UTF-8; file hashes bind the original JSONL container bytes. Finish reasons and token counts are retained separately from parsing/schema results. No punctuation is stripped, no repair score is calculated, and historical scores remain unchanged (pilot base 9/16, tuned 7/16; separate retained base 13/16).

## Reproduce

Use the existing optional environment pinned by the training dependency locks and tokenizer manifest:

```sh
.venv-tinker/bin/python -m liftlap.render_audit benchmark/v2/training-reviewed.jsonl --config training/experiment-01.json --prompt benchmark/v2/baseline-prompt.txt
python3 -m liftlap.output_forensics --cases benchmark/v2/evaluation-pilot-frozen.jsonl --predictions research/evidence/experiment-01/trained-predictions.jsonl
python3 -m liftlap.output_forensics --cases benchmark/v2/final-review/cases.jsonl --predictions research/evidence/fresh-base-evaluation/predictions.jsonl
.venv-tinker/bin/python -m unittest discover -s tests -p test_render_audit.py -q
python3 -m unittest discover -s tests -p test_output_forensics.py -q
python3 scripts/check_release.py
```

Next package: **R03**, separately versioned granular scoring and machine-readable promotion gates; then R01 and R02. No new training should be launched from this audit.

## Verification at this checkpoint

- Dependency-free release suite: **197 tests, 25 optional skips**, passed; retained-base replay still 13/16; isolated package and deterministic archive checks passed.
- Pinned optional environment: **197 tests, zero skips**, passed, including the 47-row SDK wire comparison.
- Documentation links and `git diff --check` passed. No UI changes, so screenshots were not refreshed.
