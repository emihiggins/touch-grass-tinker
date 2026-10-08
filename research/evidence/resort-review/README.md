# Resort source-review packets

These are **unreviewed source-way inventories**, not more model-label homework and not approval to offer real navigation. No reviewer decisions are inferred.

- [Alpendorf CSV](alpendorf/ways.csv), [bound manifest](alpendorf/manifest.json): 70 source ways / 495 directed edges.
- [Plose CSV](plose/ways.csv), [bound manifest](plose/manifest.json): 8 source ways / 62 directed edges.

Each row links to its OSM way, preserves native and normalized grade, summarizes source restriction tags and provides review questions/notes. A missing tag means unknown—not permitted or open. Current OSM pages may have changed since the snapshot: review the saved source and hash before applying a decision. Spreadsheet formula-like source values are written as literal cells.

## Findings that block adoption

The [Plose structural audit](../../../data/terrain/plose-research/structural-audit.json) has one weak component but no directed cycle. It cannot support a directed lap as imported, even before constraints are considered. Do not reverse paths or add transfers simply to obtain a loop. Determine whether missing geographic coverage, source direction or station connectivity explains it using permitted primary evidence.

The [Alpendorf audit](../alpendorf-snapshot-audit.json) has a 204-node strongly connected component plus 265 singleton components. Its two weak components alone were not an adequate measure of route coverage. A directed cycle still does not establish permission, suitability, lift hours or feasible timing.

All imported edge times remain estimates. A qualified resort/domain reviewer should check source geometry, direction, native grade convention, terminal boarding/alighting and actual transfer access. Current operational evidence must be dated, attributable and licensed separately.

## Workflow

1. Copy the packet to a new dated review location; preserve the source packet and manifest.
2. Record reviewer identity/qualification, evidence URLs/date and affected edge IDs in that review's notes. Do not edit source hashes to make them match changed data.
3. Proposed graph corrections become a new snapshot with regression cases; old fixture and measured model results remain intact.
4. Re-run structural audits, constraints and route validation before any app integration. Human review of these CSVs alone does not create a production-navigation capability.

Generate a new packet offline with `python3 scripts/resort_review_packet.py --graph GRAPH.json --source SOURCE.osm --out NEW_DIRECTORY`. Existing output directories are refused so decisions cannot be overwritten by regeneration. The packet is a review aid; approval-state enforcement is not implemented.

The standalone resort preview builder verifies the manifest, diagnostic, and station-evidence hashes against the current `source.osm` and `graph.json` bytes before rendering. Excluded ways with missing source nodes are rendered as separate known-node segments (or omitted when the source way itself is absent); the preview never joins across an unknown gap.

The browse-only preview now displays source versions and allowlisted native access,
direction, operating and duration tags for imported segments and selected lifts.
Missing tags are explicitly unknown; neither a source tag nor imported edge
orientation constitutes independent direction/access or current-status approval.
These annotations are derived from hash-checked snapshots without modifying graphs.

Search/selection transition checks cover selecting a filtered-out result, revealing
it again, lift-to-search marker reset, search-to-lift highlighting and switching to
excluded geometry. Each browser scenario restores its named sample after testing
terrain changes; screenshots are not attributed to a previously selected resort.

Focus controls are generated from the canonical template and preserved by
regeneration tests. Browser checks exercise keyboard focus, padded selected bounds,
Fit all restoration, hidden-selection reset and cleared-selection disabling at
three widths. Focused-area screenshots record actual clipped-context rendering.
