# Intent v2 — approved semantics, October 6

Canonical owner of the v2 contract. v1 remains supported for historical baseline replay; do not rewrite v1 gold or reports. [Architecture](architecture.md) retains the original target design.

## Changes

- `schema_version: 2`; all original fields remain, plus mandatory `avoided_lift_types: string[]` using the same lift enum as hard exclusions. Lists are unique and disjoint. Hard exclusion wins if both are requested.
- “Avoid” is soft; “no”, “without”, “exclude” and “skip” are hard. A request to avoid a lift does not authorize hiding its use. There is no special first-lift exemption.
- `duration_minutes` is a positive integer or null. Preserve explicit 5/10/300 minute requests. Null means missing, contradictory or nonpositive input, not “outside the old product range.” Deadline capping still intersects the explicit/selected duration.
- Operational guard: the current single-day simulation planner and UI support 1–1440 minutes. Larger positive intent values remain interpretable but the planner rejects them explicitly as outside its horizon. This is separate from extraction missingness and does not alter the user's duration.
- Maximum grade remains explicit user/UI information. Do not infer lift comfort from grade, infer the hardest grade from missing ability, or infer variety from allowed/preferred grades. “When to start” is time, not place.

## Planner behavior

Within unchanged state/time/edge/visit bounds, prefer fewer traversals of softly avoided lift types before the existing grade-preference, ski-distance and elapsed-time objectives. This is a disclosed heuristic, not a guarantee of the best human tradeoff. A short compliant outing may be returned; a time budget is not a promise to fill every minute.

Never admit a hard-excluded lift. Every selected soft-avoidance miss is disclosed in `preference_tradeoffs`, recomputed on original edges after compaction. The UI shows soft and hard preferences separately before confirmation and shows actual tradeoffs in the itinerary and print view. Do not claim a soft miss is unavoidable: bounded search may not find every alternative.

Operating windows are checked per edge. A 300-minute request never permits boarding a closed lift. Do not invent closing times absent from the scenario; a lift's last boarding time is not necessarily the skier's final descent finish time. The conservative prototype requires edge traversal completion by its supplied close time.

Directed reachability now rejects a disconnected finish before route search. This proves absence of a path only in the supplied graph, not real-world impossibility. Bounds and missing terrain still limit all positive/negative real-world claims.

## Compatibility and provenance

`validate_intent` dispatches by explicit schema version. The scorer compares all fields, including soft avoidance and version, so a v1 prediction cannot silently pass a v2 label. Rules default to v1 for historical command compatibility; the current browser calls rules v2 explicitly. The old sampled outputs retain their original corpus/prompt/version hashes and 6/20 and 13/20 development outcomes; they are not v2 scores.

v2 prompt, training data and development data live under `benchmark/v2/`. The deterministic migration changes only approved semantics, excludes training candidate 009, and records original human review plus approved migration provenance. It refuses changed/unapproved/quarantined sources. Other v1 review records remain intact. The revised corpus is not claimed to have received a fresh independent human review.
