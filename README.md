# Lift-Lap Planner

Private project workspace for Emi's Hacktoberfest Week 1 entry, targeting **Best Use of Tinker**.

**Status:** working local simulation and live Tinker baseline experiments; no fine-tuned model yet. The UI uses rules, while Qwen3-8B inference is evaluated separately. No public demo or field-verified navigation is claimed.

## Submission materials

- [DEV article draft and release gates](submission/README.md)
- [Two-minute demo storyboard](submission/demo-storyboard.md)
- [Training batch/cursor rehearsal](training/batch-rehearsal.md)

## Run locally (Python 3.11+, no dependencies)

```bash
python3 -m liftlap
python3 -m liftlap.server --port 8767
python3 -m unittest discover -s tests -v
python3 -m liftlap --osm data/terrain/alpendorf-source.osm --start-node 2591901158 --lab
```

The first command uses an original synthetic graph. The server command opens the local-only demo at http://127.0.0.1:8767 (not accessible from another device without separately arranging access). The last explicitly opts into **unreviewed-terrain simulation**, with assumed speeds/queues/closures; it is not a usable on-mountain navigation instruction. Without `--lab`, imported unreviewed terrain is refused. See [offline checkpoint](delivery/offline-checkpoint.md) and [data provenance/license](data/terrain/README.md).

## Source of truth

- [Selected product direction](product/brief.md)
- [Data sources, access checks and recommendation](research/data-sources.md)
- [Follow-up feasibility and audit evidence](research/feasibility.md)
- [Source-loop verification and Tinker access checkpoint](research/loop-verification.md)
- [Executable benchmark seed](benchmark/README.md)
- [Local UI, rules baseline and compaction checkpoint](delivery/local-demo.md)
- [Requirements and acceptance criteria](product/requirements.md)
- [Architecture and API contracts](technical/architecture.md)
- [Training and evaluation protocol](delivery/evaluation.md)
- [Challenge requirements and sources](research/challenge.md)
- [Execution gates and evidence plan](delivery/plan.md)
- [Archived alternative](scratchpad/concept.md)

## Current checkpoint and next step

Prompt v2 scores **13/20** strict development request successes, versus **6/20** for prompt v1 and **14/20** for rules-v1. These are visible development cases, not held-out results or fine-tuning gains. Raw outputs and regressions are preserved in the [training checkpoint](training/README.md).

There are **48 human-reviewed training candidates** and **32 development examples**: 45 labels explicitly approved, including quarantined 009; 44 non-quarantined approvals and 3 agreed changes awaiting implementation. See [review outcomes](training/human-review.md). All 80 pass local Cookbook token/mask checks. The new [offline batch rehearsal](training/batch-rehearsal.md) verifies all 48 candidates in three batches with an explicit batch-size-16 override and hash-bound resume cursors. It rejects the canonical batch-size-32 tail loss; the canonical plan is not changed. No remote checkpoint is loaded and no training is launched.

Next: implement the three agreed label changes and version the duration/soft-avoidance contract, then independent evaluation data, protected training/checkpoint integration and separately authorized training. The [submission readiness page](submission/README.md) tracks the article, actual tuned-model evidence, accessible demo/video and code-release gaps. Source-terrain review and the three-reviewed-loop gate also remain open; all real-terrain use is explicitly unreviewed simulation.

Keep this repository private as requested. Publishing code, a demo or the DEV entry is a separate release step. Earlier inference-only authorization does not authorize training.
