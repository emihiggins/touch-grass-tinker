# Development seed v1

32 individually authored, AI-assisted original requests across 25 families, with explicit UI context and a fictional place catalog. No external user data or resort records. Gold labels were reviewed during authoring by the agent; **not human-reviewed**. They are not an untouched held-out test, training dataset or measured model result.

## Scope and label rules

This is an executable first slice of the [evaluation protocol](../delivery/evaluation.md): intent semantics only. No scenario graph is attached and route feasibility is deliberately unlabeled (`expected_action: interpret_only` for ready cases). Do not score these cases as successful ski outings. A future graph-backed benchmark must add independent route feasibility and validation.

Explicit user corrections override prior utterances/UI values. Otherwise the selected UI context fills unspecified fields. A deadline may shorten but does not automatically extend the selected duration: with 60 minutes selected at 10:00, “back by noon” still means a 60-minute outing; “two hours, back by 11:15” explicitly requests 120 minutes but the deadline caps it to 75. Unsupported preferences require a choice to drop them, not silent fallback. Unknown destination names and out-of-range durations trigger clarification. These conventions must appear in the baseline prompt too.

The seed contains hard/soft difficulty, exclusions/negation, correction, durations/deadlines, aliases, variety, absent fields, contradictory requests and unsupported live-condition requests. All current examples belong to development. New test examples must be split by family/template provenance before expansion; do not promote this visible seed to an untouched test set.

## Run without installing dependencies

From repository root, Python 3.10+:

```bash
python3 scripts/benchmark.py benchmark/development-seed.jsonl
python3 -m unittest discover -s tests -v
python3 scripts/benchmark.py benchmark/development-seed.jsonl --predictions /path/to/predictions.jsonl
```

Prediction format: one JSON object per line with `id` and `intent`. Missing/malformed intents count as failures; duplicate/unknown IDs abort rather than silently drop records. Metric is strict normalized intent match, with order-insensitive lists and equivalent timestamp normalization. It is **not** route success. The gold round-trip test checks the scorer, not a model. No model results exist yet.

[Manifest](manifest.json) records the current content hash; this is a reproducibility hash, not a claim that final evaluation is frozen. Code is standard-library-only. No training/sample calls or dependencies are needed for local checks.

## Graph-backed development scenarios

[route-development.json](route-development.json) adds 8 original synthetic scenarios referencing the seed: feasible outings, closure/exclusion conflicts, unknown status, queue-induced infeasibility and a changed finish node. `python3 -m liftlap.evaluate --predictions /path/to/predictions.jsonl` scores predictions keyed by **route scenario ID**, not seed ID. It combines normalized gold-intent agreement with planner status and independently checks a returned route against gold constraints. Cases remain development-only and not human-reviewed.

Tests passing gold intents through this pipeline are fixture self-checks, never base/tuned model accuracy. A deliberately weakened difficulty constraint yields a route that the planner can execute, but the gold validator and scorer reject it.

## Rules baseline v1

`liftlap/rules.py` is an explicit grammar baseline, independent of any model or prediction file. It handles basic grade/time/exclusion/alias/deadline patterns and abstains on unparsed language. [Saved predictions](rules-v1-predictions.jsonl) replay through the existing scorer. [Report](../research/evidence/rules-v1-development.json): **22/32 exact matches**, on this visible development set used during parser development. This is NOT held-out generalization or a trained-model comparison. No cases were removed to improve the headline.

Reproduce predictions by calling `interpret(request_text, ui_context, catalog)['intent']` for each JSONL row, then pass `{id, intent}` records to `scripts/benchmark.py --predictions`. Do not mutate or weaken this comparator after observing model scores; improve and freeze it with the other baselines before held-out evaluation.

## Training preparation

See [training readiness](../training/README.md) for the separate 16-case candidate batch, split audit, conversation exporter and paired comparison CLI. Candidates are not held-out data. One cross-partition near-duplicate warning remains quarantined for review; no production training export is ready.

## Complete-action development comparison

`request-development.json` includes all eight route fixtures plus 12 clarification/unsupported cases. Rules-v1 scores **14/20** on these visible development cases; saved predictions are in `rules-v1-request-predictions.jsonl`. `python3 -m liftlap.request_compare BASELINE TUNED` compares saved scenario-keyed predictions using gold-route validation and outcome slices. No tuned results exist. See [current readiness](../training/README.md).
