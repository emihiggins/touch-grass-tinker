> **Historical planning/checkpoint document.** Retained for provenance, not a current feature or task list. Use the [current documentation](../docs/README.md) for the implemented app, completed experiments and supported setup.

# V2 implementation checkpoint — 2026-10-06

## Delivered

- [Versioned intent contract](../technical/intent-v2.md), browser rules adapter, shared validator/scorer, soft-avoidance ranking and original-edge tradeoff disclosure. Hard exclusions remain strict.
- Positive durations preserved; 10/300-minute cases reach planner validation. Per-edge closures remain binding. UI operational horizon is 1–1440 minutes; semantic schema accepts any positive integer.
- [47-row reviewed v2 training corpus](../benchmark/v2/README.md), 009 excluded, original v1 sources and evidence unchanged. 32 migrated development cases.
- [16-case evaluation review pilot](../training/evaluation-review-v2.md) with four new fictional graph topologies; no model predictions, no human approval or freeze yet. Pilot preparation influenced reachability checking; not an untouched final test set.
- Protected read-only billing endpoint access verified; remaining credits and same-day bill reconciliation are still unverified. No new inference or training calls.

## Verification

117 tests pass in the pinned optional environment; dependency-free suite passes 103 with 14 optional skips. Replayed historical saved predictions still score rules 14/20, base v1 6/20 and base prompt v2 13/20; none are v2-contract accuracy claims.

All 47 v2 training rows and 32 development rows pass local tokenizer/rendering checks with no prompt loss or truncation. The training rehearsal schedules all 47 rows without tail loss using the explicit smoke config. See [render audit](../research/evidence/render-audit-v2-reviewed.json), [development audit](../research/evidence/render-audit-v2-development.json), [batch plan](../research/evidence/training-batch-v2.json) and [blocked preflight](../research/evidence/training-preflight-v2.json).

Existing browser smoke and new `scripts/browser-v2.cjs` pass in Chromium. Checks cover 10/300-minute requests, soft preference review, preference-aware route selection, actual tradeoff visibility, hard-exclusion no-route, stale-output clearing, mobile width 360 and print-view tradeoff visibility. Mobile screenshot visually inspected; no overflow/page errors. PDF generated, but full raster print legibility and comprehensive accessibility remain unverified. New screenshot and PDF are local verification artifacts, not proof of public hosting.

## Next gate

Emi can review the 16 pilot cases without running commands. Independent final-test preparation/freeze and provider training/checkpoint/global-accounting integration remain necessary before the planned experiment. No need to repeat the original 48-case review or approve the same $10 budget again. The exact DEV template and private/unpublished status are preserved.
