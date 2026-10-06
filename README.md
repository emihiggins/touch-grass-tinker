# Lift-Lap Planner

Private project workspace for Emi's Hacktoberfest Week 1 entry, targeting **Best Use of Tinker**.

**Status:** offline reference implementation working. Includes conservative OSM import, a bounded simulation planner, independent route validator, 32 intent-development cases and 8 graph-backed scenarios. A local browser demo and rules baseline now run; no Tinker inference, fine-tuning or field-verified navigation yet.

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

## Next step

[Sampling runner](training/sampling-runner.md): SDK submission/polling is mock-tested and a 20-case local dry run is ready. Live inference awaits budget/credit confirmation.

Latest: 90 tests pass in the optional training environment (ten optional tests skip in the dependency-free environment); paired full-request evaluation covers 20 development scenarios. Rules-v1 succeeds on 14/20 (visible development data, not held-out accuracy). Protected Tinker access is verified with HTTP 200; Qwen3-8B is listed. A pinned Tinker SDK read-only smoke passes; all 80 current candidate/development examples pass Cookbook token/mask checks. 48 training candidates and a review packet are ready. Credits/spending and actual model runs remain pending. See [training checkpoint](training/README.md).

[Offline training readiness](training/README.md) now includes 16 training candidates, split/leakage audit, Cookbook conversation preview export and saved paired intent comparison. No final test set or model runs yet.

Review native OSM terminal access/direction and route choices; the three-field-reviewed-loop gate remains open. Extend the current local UI/API and improve the rules baseline while Tinker access is pending. Expand/review development examples and freeze a separate held-out benchmark before training. Reuse existing open data and Tinker Cookbook tooling.

Keep this repository private as requested. Publishing code, a demo, or the DEV entry is a separate release step. No paid compute has been authorized or started.
