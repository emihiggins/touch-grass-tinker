# R02 deterministic boundary checkpoint

Implemented offline on 2026-10-08. This is synthetic planner-boundary evidence,
not model-robustness, real-terrain, or operational evidence.

## Scope

`tests/test_r02_boundaries.py` adds a standard-library-only, replayable suite:

- 24 seeded bounded graphs with independent route validation;
- unknown IDs, disconnected/reversed paths, closures, and snapshot tampering;
- hard difficulty maxima and lift exclusions at planner and validator boundaries;
- edge-removal and fixed-route budget monotonicity;
- bijective node renaming and compaction/expansion preservation;
- timezone-aware supported boundaries and explicit rejection of naive timestamps.

Language-stress and prompt-injection concerns remain diagnostic only; this
checkpoint does not create labels or claim inference robustness. No provider,
paid call, terrain activation, or historical evidence rewrite was used.

## Evidence command

```text
python3 -m unittest tests.test_r02_boundaries tests.test_routing tests.test_compact
```

The seed family and minimal fixtures are in the exact test source above. Any
failure includes its replay seed via unittest’s subtest output.
