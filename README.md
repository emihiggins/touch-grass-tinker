# Lift-Lap Planner

Private project workspace for Emi's Hacktoberfest Week 1 entry, targeting **Best Use of Tinker**.

**Status:** project initialized and concept selected October 5, 2026. Data-source research, directed graph audit, and implementation/evaluation plans completed. A 32-case development seed and offline intent scorer now exist; 8 scorer tests pass. No application, training run, or model benchmark results yet.

## Source of truth

- [Selected product direction](product/brief.md)
- [Data sources, access checks and recommendation](research/data-sources.md)
- [Follow-up feasibility and audit evidence](research/feasibility.md)
- [Source-loop verification and Tinker access checkpoint](research/loop-verification.md)
- [Executable benchmark seed](benchmark/README.md)
- [Requirements and acceptance criteria](product/requirements.md)
- [Architecture and API contracts](technical/architecture.md)
- [Training and evaluation protocol](delivery/evaluation.md)
- [Challenge requirements and sources](research/challenge.md)
- [Execution gates and evidence plan](delivery/plan.md)
- [Archived alternative](scratchpad/concept.md)

## Next step

Normalize and review exact-node OSM loops: the processed graph failed the three-loop geometry gate. Expand/review the development seed, then freeze a separate held-out benchmark before training. Reuse existing open data and Tinker Cookbook tooling.

Keep this repository private as requested. Publishing code, a demo, or the DEV entry is a separate release step. No paid compute has been authorized or started.
