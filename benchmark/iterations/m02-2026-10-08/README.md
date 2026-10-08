# M02 initial review packet — 2026-10-08

This is a small **TRAINING candidate** packet (12 rows), generated offline for Emi review. It is same-agent authored, fictional, and seed-derived; it is not an independently authored holdout and must not be described as human-reviewed. The labels are provisional and all rows are `human_reviewed: false`, `decision: pending`.

- `training-review-packet.jsonl` is the review surface; no row is approved for training.
- `iteration-manifest.json` records exact request/context/graph/label hashes, normalized duplicate keys, family boundaries, near-duplicate flags, and sparse coverage.
- Candidate, validation/development, and final boundaries are reserved in the manifest. Existing `benchmark/v2` evaluation files remain historical/frozen and are not copied into a holdout.
- Review must confirm the request, UI context, catalog/graph, expected intent, and any edge behavior. Approval must bind all current hashes; unresolved or changed rows stay out of export.

Known limitation: this first packet is coverage-oriented and intentionally too small for training. The manifest reports missing/sparse categories; it makes no representativeness claim. No provider calls, API keys, personal trip data, paid work, or training run were used.
