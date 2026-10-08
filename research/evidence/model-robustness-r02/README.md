# R02 deterministic boundary checkpoint

Implemented offline on 2026-10-08. This is synthetic planner-boundary evidence,
not model-robustness, real-terrain, or operational evidence.

## Scope

`tests/test_r02_boundaries.py` adds a standard-library-only, replayable suite:

- 24 seeded bounded graphs with independent route validation;
- unknown IDs, disconnected/reversed paths, closures, and snapshot tampering,
  with independent fixtures asserting `unknown_edge`, `disconnected`,
  `not_open`, and `snapshot_mismatch`;
- hard difficulty maxima and lift exclusions at planner and validator boundaries;
- edge-removal and fixed-route budget monotonicity;
- bijective edge/node renaming and compaction/expansion preservation;
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

## Coverage correction identified during R01 recovery (repaired 2026-10-08)

The injected-ID/direction/closure cases now use independent scenarios and assert
reason-specific failures. The fixed-route monotonicity case uses valid v2 intents
and an actual deadline crossing. Genuine edge/node renaming, midnight rollover,
and exact closing-boundary fixtures are covered. Language stress/provider-injection
and DST repeated/nonexistent-local-time coverage remain pending: add reviewed
language/provider boundary tests and explicit contract fixtures for DST semantics
before checking those acceptance boxes. Seeded graphs remain synthetic and do not
establish model, provider, terrain, or operational evidence.
