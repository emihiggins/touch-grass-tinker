# Version 2 datasets and frozen evaluations

See the [evaluation guide](../../docs/evaluation.md) for current results and reproduction commands.

| Artifact | Role | Status |
|---|---|---|
| [training-reviewed.jsonl](training-reviewed.jsonl) |47 human-reviewed, deterministically migrated training rows | Used in the completed trial; original candidate009 excluded for overlap |
| [development.jsonl](development.jsonl) |32 visible development rows | Not held out or newly human reviewed |
| [baseline-prompt.txt](baseline-prompt.txt) | v2 model instruction | Preserved for completed experiments |
| [evaluation-pilot-frozen.jsonl](evaluation-pilot-frozen.jsonl) |16 reviewed pilot cases | [Frozen](evaluation-pilot-freeze.json); base9/16 vs trained7/16 |
| [final-review/cases.jsonl](final-review/cases.jsonl) |16 fresh reviewed cases | [Frozen](final-review/freeze.json); retained base13/16 |

The pilot [source review rows](evaluation-candidates.jsonl), [graph bundle](evaluation-graphs.json), [review manifest](evaluation-review-manifest.json), and [migration manifest](migration-manifest.json) preserve lineage. The fresh set has a separate [graph bundle](final-review/graphs.json).

## Limits

Both evaluation sets are small, fictional, authored by the project agent and reviewed by the owner. The pilot informed implementation and is not untouched. The fresh set was frozen before its base-model predictions, and no tuning used its outputs. The later unchanged-rules comparator is explicitly post-hoc. These sets replace the initially proposed larger protocol for this iteration; they do not support broad statistical or field-safety claims.

A fixture self-check with gold intents is not model performance. The evaluator requires human-approved rows and exact case/graph freeze hashes. Do not silently edit frozen inputs or promote visible development rows into an untouched benchmark.

V2 supports normalized green below blue, soft lift avoidance distinct from hard exclusions, and explicit positive requested durations. Resort-specific grading and actual operating feasibility remain separate from intent parsing.

## Offline scoring

```bash
python3 -m liftlap.evaluation_v2 \
  --cases benchmark/v2/final-review/cases.jsonl \
  --graphs benchmark/v2/final-review/graphs.json \
  --freeze-manifest benchmark/v2/final-review/freeze.json \
  --predictions research/evidence/fresh-base-evaluation/predictions.jsonl
```

Run from repository root. This reproduces13/16 without provider calls. The one-row batch in `sft-plan-v2.json` belongs to the earlier integration smoke; the completed full-data trial used47-row batches for three passes. [Training guide](../../training/README.md).
