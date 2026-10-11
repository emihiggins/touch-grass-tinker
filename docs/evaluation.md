# Evaluation and reproducibility

All figures below retain failures in their denominators. Small fictional sets and same-agent case authorship limit generalization; human review does not make them representative of real resorts.

| Set | Result | Evidence |
|---|---|---|
| Historical v1 visible development,20 cases | Rules14/20; base prompt1 6/20; base prompt2 13/20 | [Development outputs](../research/evidence/base-v2-development/report.json) |
| First v2 reviewed pilot trial,16 cases | Base9/16; tuned7/16 | [Preregistered paired trial](../research/evidence/experiment-01/README.md) |
| Second trial on the exposed pilot,16 cases | Base10/16; tuned10/16 | [Exploratory follow-up](../research/evidence/experiment-02/README.md) |
| Fresh v2 frozen human-reviewed set,16 cases | Retained base13/16; schemas16/16 | [Final base results](../research/evidence/fresh-base-evaluation/README.md) |
| Same fresh set, later unchanged-rules check | Rules0/16 | [Post-hoc comparator](../research/evidence/fresh-rules-comparison/README.md) |

The trained model was rejected before fresh evaluation. The fresh13/16 is not an improvement over the pilot9/16: they are different cases. The rules comparator was added after model outputs and did not drive model selection. The later owner-authorized exploratory retraining reused the approved47 training rows and exposed pilot only; it did not use the fresh final labels/outputs as training examples. It tied its contemporaneous base10/16 and was not promoted. No independent generalization claim is made. Earlier development prompt improvements are not fine-tuning gains.

## Reproduce without a model call

```bash
python3 -m liftlap.evaluation_v2 \
  --cases benchmark/v2/final-review/cases.jsonl \
  --graphs benchmark/v2/final-review/graphs.json \
  --freeze-manifest benchmark/v2/final-review/freeze.json \
  --predictions research/evidence/fresh-base-evaluation/predictions.jsonl
```

Expected:13 successes out of16. `python3 scripts/check_release.py` also checks this automatically. The evaluator verifies reviewed-label and frozen case/graph hashes before model scoring. A gold fixture self-check is not model accuracy.

## Data lineage

The training corpus has47 reviewed, deterministically migrated examples. Original candidate009 was excluded for development overlap. The32 v2 development rows are separate; the reviewed pilot and fresh set each have16 cases. [Data index](../benchmark/v2/README.md).

Cases, prompts, rendering, plans and evidence from completed experiments are preserved. New model selection or training requires a new protocol and appropriately independent evaluation, not edits to frozen artifacts or repeated attempts until a preferred headline appears.

## Latest failure analysis

[Read-only SFT02 postmortem](../research/evidence/experiment-02/postmortem.md) covers all32 paired outputs. Four base and two tuned routes violated reviewed constraints despite being accepted under their own interpretation; those counts are evaluation-only and not evidence of field safety. Both malformed tuned outputs also have incorrect contents. No post-hoc JSON repair changes the reported scores.
