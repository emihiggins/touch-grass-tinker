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

## Correction/recovery follow-up (2026-10-08)

The first checkpoint did not reject a clarification retaining its disputed value, and one context-fill test accepted that contradiction. This follow-up fixes that gap rather than treating the original test as sufficient evidence.

- Clarification with a retained value, or a missing required value omitted from clarification, now returns a typed issue. The server rejects it before planning and exposes structured issues over HTTP 422.
- A structurally valid but semantically rejected live interpretation can be reviewed and corrected locally without another paid call. The sampler still marks the original output `invalid_semantic`; no repaired model score is claimed.
- Time/difficulty clarification can be corrected in the existing UI, with the original request/settings retained. Other missing place/time fields and unsupported requests still require request/form changes. Unknown maximum difficulty stays unknown and cannot plan.
- Applying time/difficulty corrections does not remove hard lift exclusions. Editing clears route/export state; late responses cannot republish stale routes. Exclusions change only through explicit user edits.
- Envelope validation rejects malformed values, boolean versions, duplicate/unsupported unknown markers, extra envelope fields and context-value conflicts. Resolution uses a copy and cannot mutate the source extraction. Explicit unknown clears the field and requests clarification; it never inherits a UI default. Partial provenance is still opt-in metadata, not proof the model interpreted free text correctly.

### Browser and transport evidence

[Recovery matrix](recovery-browser.json) covers 390, 768 and 1440px with injected **synthetic** semantic failures. It verifies local recovery, four surface-lift exclusions, valid eight-minute no-route handling, unknown maximum blocking, corrected text export and delayed-response invalidation, with zero extra interpretation calls. Automated WCAG A/AA checks show no violations; color-contrast incomplete findings remain for manual review. The phone clarification and pending-edit captures were visually inspected; no horizontal overflow was observed.

```sh
BASE_URL=http://127.0.0.1:8767 PLAYWRIGHT_MODULE=/path/to/playwright-core AXE_SCRIPT=/path/to/axe.min.js node scripts/browser-semantic-corrections.cjs
```

Additional existing recorded-demo, correction/export, accessibility, request recovery and map checks ran against a separate loopback server on 8771 (temporary copies only changed the test URL). The existing server on 8767 was left alone. Current demo media was regenerated without provider calls. Unit/HTTP tests exercise the actual server and model adapter with mocked sampling; browser injection is not evidence of real model accuracy.

Final verification: dependency-free release ran **232 tests (25 optional skips)**; pinned optional environment passed **all 232**. Historical retained-base replay remains 13/16. Isolated package and deterministic archive checks passed. Recorded correction PDF has one page (page object and page-tree counts agree); its print preview was visually checked. Formatting, JavaScript syntax, documentation links and whitespace checks passed.
