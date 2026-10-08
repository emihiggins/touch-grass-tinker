# R01 semantic-contract checkpoint

Implemented offline on 2026-10-08.

## Scope

- Added `liftlap/semantic_contract.py`, a pure typed validator returning stable issue
  codes and field paths.
- Added opt-in contract envelope version 1 with field provenance
  (`user`, `context`, `missing`) and explicit unknown markers. User values
  win over context; context only fills a missing field.
- Planning and sampling boundaries now validate semantics before route generation
  or acceptance.
- Added synthetic regression fixtures for malformed ready state, clarification
  precedence, explicit unknown values, short valid budgets, and context override
  behavior.

Legacy intent-v2 objects remain accepted without provenance and historical
evaluation/scoring files were not rewritten. The validator does not inspect
request prose or infer difficulty, lift comfort, or defaults.

## Evidence

Command:

```
python3 -m unittest tests.test_semantic_contract tests.test_contract_v2 tests.test_server tests.test_sample_runner tests.test_evaluation_v3
```

Result: **49 tests passed, 2 existing skips**.

The valid-but-infeasible fixture reaches deterministic `no_route`; malformed
semantic output is rejected before `plan`. This is offline evidence only and
does not establish model accuracy or qualified terrain capability.
