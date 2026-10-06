# Lift-Lap Planner

A local ski-outing planning experiment for the Hacktoberfest Week1 Touch Grass challenge. Best Use of Tinker is not claimed: no measured fine-tuning gain.

**Status:** local simulation with Rules, recorded-AI and opt-in live Qwen3-8B interpretation. A real app call is verified, with its semantic error preserved and a local correction step demonstrated. The fine-tuned trial did not improve the matched pilot (base9/16, tuned7/16). Retained base:13/16 on a separate frozen fresh set. No hosted app or field-verified navigation is claimed.

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

- [Integration, recorded demo and reproducible local package](delivery/app-integration.md)
- [Fresh base evaluation:13/16](research/evidence/fresh-base-evaluation/README.md)
- [Matched pilot:base9/16 vs trained7/16](research/evidence/experiment-01/README.md)
- [Final posting checklist for Emi](submission/dev-posting-checklist.md)
- [Release-focused followup plan and results](delivery/high-value-followups.md)
- Run all offline release checks: `python3 scripts/check_release.py`

All training/pilot/fresh label reviews are complete. The app requires explicit confirmation and supports hard-lift-exclusion correction before planning. Its recorded example preserves a real model mistake. Rules and exact-input recorded mode work offline; live inference is disabled by default. The real terrain lab remains unreviewed simulation.

Original code is [MIT](LICENSE); terrain and upstream components have [separate notices](THIRD_PARTY_NOTICES.md). Emi will personally change repository visibility and post to DEV. The agent does not perform those actions. Current holds total$1.75 within the authorized$10 Tinker cap, not an invoice. No budget reapproval is needed for the approved scope. Billing reconciliation remains separate from model quality and publication.
