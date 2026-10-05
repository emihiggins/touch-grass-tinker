# Next-priority checkpoint: source topology and access

Checked 2026-10-05. This report supersedes any interpretation that the processed graph's blue-only cycles are ready for routing. Earlier results remain correct as structural graph checks only.

## Source checks performed

- Bounded Overpass calls: primary endpoint returned HTTP 406; alternative timed out at 35 seconds. No repeated polling.
- Direct OSM API map extract succeeded: https://api.openstreetmap.org/api/0.6/map?bbox=13.224,47.303,13.25,47.314 . 1,923,417 bytes / 8,902 XML children observed. This is a source snapshot, not live terrain verification. The complete raw response remains in temporary local storage, not committed; hashes in the evidence reports pin the inspected bytes. A future download may differ.
- Official resort HTML at https://www.snow-space.com/openlifts was accessible and names the lifts. Its status-icon extraction is not a verified live-data feed. Official piste name/number listings do not prove exact junction access.

## Three processed-graph loop checks: gate FAILED

Reproduce with `python3 research/scripts/audit_loops.py /path/to/terrain.json /path/to/map.osm`.
[Machine-readable source/geometry comparisons](evidence/three-loop-source-audit.json).

| Candidate | Downhill length in derivative | Largest consecutive-geometry gap | Source geometry pairs matched | Source piste difficulty overlap |
|---|---:|---:|---:|---|
| Hirschkogelbahn | 1,387 m | 62.39 m | 42/43 | easy and intermediate |
| Straßalmbahn | 1,363 m | 107.09 m | 50/51 | easy and intermediate |
| Obergassalmbahn | 1,007 m | 80.04 m | 27/27 | easy |

The gap metric includes lift→piste, piste→piste and final piste→lift closure. Exact coordinate pair matches can refer to overlapping source ways, so an intermediate overlap is an unresolved ambiguity, not proof the whole path is red. Both findings nevertheless prevent claiming a verified continuous blue itinerary. Source geometry matches include reverse direction for corroboration; this alone does not establish downhill direction.

Decision: **do not use derivative graph node merging as authoritative topology**. Keep it as display/reference data only until repaired with source evidence. Do not force-snap 60–100 m gaps or silently downgrade intermediate segments.

## Raw OSM node-based alternative

Reproduce `python3 research/scripts/audit_osm_loops.py /path/to/map.osm`.
[Raw source audit](evidence/raw-osm-loop-audit.json).

Two lifts have exact-node return paths using explicitly novice/easy downhill ways in this bounded extract:

1. **Obergassalmbahn**, OSM way 253232925. Return uses ways 449539706, 547259393, 49225049, 547259386, 253232939 and 49225053.
2. **Übungslift Obergassalm**, OSM way 125064134. Return uses way 1157486077.

Hirschkogelbahn and Straßalmbahn do not have such exact-node returns under this conservative extraction. This is not proof that no real return exists: missing connectors, relation tags or source mapping gaps can cause false negatives. We will not invent connections.

The two positive paths establish source topology, not field validation, boarding permissions, current operation or confirmed elevations/directions. Lift order and piste way direction follow source conventions and still require audit. One is a rope tow, so “no drag lifts” excludes it. Three fully reviewed lift/descent loops are **not yet verified**; R01 stays open. Next: normalize the two exact-node candidates, inspect terminal geometry/elevation/access, and expand the bounded source sector only if needed for a third loop and meaningful choice. Any scope reduction must be recorded explicitly, not counted as passing the old gate.

## Dataset provenance

Terrain derivative source/revision/license: [initial research](data-sources.md). OSM raw data is © OpenStreetMap contributors, ODbL: https://www.openstreetmap.org/copyright . Generated reports contain derivative identifiers/metadata and retain this attribution. No map artwork or complete raw XML (including contributor metadata) is published here. The evidence snapshots are not claimed to be public-domain original training data.

## Tinker access check

The protected secret store returned empty, and `TINKER_API_KEY` is absent from the current process environment. No authenticated request, balance check, sampling or training was performed. Other uninspected login stores are not assumed absent. Credits and spending allowance remain unknown.

SDK's official default API host is `tinker.thinkingmachines.dev`, base `/services/tinker-prod`, per https://github.com/thinking-machines-lab/tinker/blob/main/src/tinker/lib/base_url.py . A credential should be supplied via protected masked entry, never chat text or repository files. Restrict egress to that host. Protected credentials are available to gateway-host execution, not ordinary native shell commands; late-added credentials may require the next turn before injection.

After credential configuration, first verify authentication/model availability through read-only capability access. Sampling and training wait for confirmed credit/budget coverage. No budget or provider access is inferred from the published model price list.
