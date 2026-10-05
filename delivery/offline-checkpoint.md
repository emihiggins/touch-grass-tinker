# Offline implementation checkpoint

Implemented 2026-10-05; no Tinker calls or paid compute. This file owns implemented scope and reproduction instructions. Product requirements remain in [requirements](../product/requirements.md).

## Working pieces

- `liftlap/import_osm.py`: native-node import; source provenance, explicit source grades/types and assumed timing. No snapping or transfer invention. Rejects missing references, unknown grades, explicit access restrictions, reversed-direction tags and exactly overlapping conflicting grades. Relations and all possible restrictions are not fully interpreted; all imported terrain stays unreviewed.
- `liftlap/core.py`: bounded breadth-first reference search and separate validator. Start=finish requires a nonempty lift+piste outing. Checks closures/unknown states, per-edge intervals, queues, time budget, grade, excluded lift types, graph/scenario hashes and explicit review mode. Different edges between identical nodes stay distinct.
- `liftlap/fixtures.py`: original fictional terrain/scenario data; no geography claims.
- `liftlap/evaluate.py`: 8 development scenarios check interpretation, planner status and returned-route compliance with **gold**, not predicted, constraints.
- Existing 32-case intent seed/scorer remains available. No trained/prompted/rules model metrics exist.

## Run and verification

```bash
python3 -m liftlap
python3 -m unittest discover -s tests -v
python3 scripts/benchmark.py benchmark/development-seed.jsonl
python3 -m liftlap --osm data/terrain/alpendorf-source.osm --start-node 2591901158 --lab
```

The real-data lab run imports 469 nodes / 495 edges from the sanitized pinned source and returns a simulated route that passes the independent graph/scenario validator. [Saved output](../research/evidence/offline-route-demo.json) contains its hashes, path IDs and assumptions. The normalized [lab data](../data/terrain/README.md) retains the original download hash; reimporting sanitized XML changes only the source hash and downstream graph/scenario hashes, as documented there.

Source graph is not terrain-verified. Explicit `--lab` is required to route on it. Simulated January 2027 all-open conditions and durations are illustrative, not a forecast, current operation or measured field result. No personal coordinates or credentials are collected.

## Deliberate limits versus production design

This is a small exact-within-bounds reference, not the planned NetworkX/beam-search/API/UI implementation. Standard Python runs it without installing anything. The host lacks pip/ensurepip/uv, so no system package changes were made; an incomplete ignored `.venv` from the bootstrap check is not used. `pyproject.toml` declares an empty dependency set. A future managed production environment should install and lock its own dependencies.

Search uses at most 20,000 expanded states, 40 edges, two visits per edge and a two-second wall clock. A limit without a candidate returns `search_limit`, never unqualified infeasibility. A valid candidate may be returned with incomplete-search metadata; no optimality claim. Piste edges currently correspond to source-node segments, so the 40-edge bound can restrict real-map coverage independently of skiing duration; production should contract non-branching chains without losing source evidence.

Preference objective: preferred unique piste distance, then unique distance if variety requested (otherwise traversed piste distance), then lower time. It is a simple disclosed heuristic objective, not a proven human-utility metric. Waiting for lifts to open, restaurant access, intermediate lift boarding, missing direction/permission interpretation and production-ready XML/input security are out of scope here. API boundary validation and deployment limits remain planned; do not expose this internal reference directly as a public service.

## Next executable work

1. Contract source-node chains at true junctions while retaining complete geometry/source IDs; compare expanded routes through the existing validator.
2. Finish terrain/terminal access review; expand to a third meaningful loop only with source evidence. Do not change `review_status` merely because graph tests pass.
3. Add a transparent rules baseline and production Intent contract, then API/UI on top of these tested behaviors.
4. Continue authoring/reviewing independent graph-backed development examples. Freeze held-out data only after conventions and baseline setup are settled.
5. When Tinker access is ready, run authenticated capability check, confirm credits/budget and renderer smoke before any sampling/training. No credential request repeated this turn.
