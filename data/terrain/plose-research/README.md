# Plose bounded research sample

**Not a selectable application resort, complete resort map, or navigable route dataset.** This is a second-region importer fixture, not an operations feed. No user or model evaluation result is changed by it.

A single OpenStreetMap map request used bbox `11.718,46.680,11.732,46.691` on October 7, 2026. The original response was 510,324 bytes. See [manifest](manifest.json) for exact URL, retrieval time, original response hash, sanitized-input hash, graph hash and import options. Native ways can extend outside the requested bbox; this is not a coverage guarantee.

- [source.osm](source.osm): sanitized OSM nodes and piste/aerialway ways. Contributor identity/history and relations omitted; not original response bytes.
- [graph.json](graph.json): 61 nodes, 62 directed edges (61 piste segments, one lift). Native source IDs retained; no proximity snapping or new connections.
- [import audit](import-audit.json): one area/closed-way and one unknown-grade way excluded.
- [structural audit](structural-audit.json): one weakly connected component, no missing endpoints/source references/geometries. Weak connectivity does **not** establish directed round trips or permitted skier access.

Directions follow unreviewed source way order. All 62 durations are assumed. Italian grade mapping is explicitly provisional: novice/easy → blue, intermediate → red, advanced → black. Original OSM grades are preserved. These settings are not claims about every Italian resort and must be checked with an operator before adoption. Missing operational status remains unknown, never inferred open.

## Licensing

© OpenStreetMap contributors, [ODbL 1.0](../LICENSE-ODbL.md). Derived graph retains database terms; MIT covers original application code, not these data. No resort artwork, photographs or private API data is included.

## Reproduce offline

The test `tests/test_resort_import.py` reconstructs the exact graph and import audit from the sanitized file and manifest options, and verifies that historical Alpendorf output remains unchanged. Run:

```sh
python3 -m unittest discover -s tests -p test_resort_import.py
python3 scripts/audit_resort_snapshot.py --snapshot data/terrain/plose-research/graph.json --output data/terrain/plose-research/structural-audit.json
```

For another bounded sample, use `scripts/import_resort_snapshot.py --source INPUT.osm --config CONFIG.json --out NEW_DIRECTORY`. Configuration supplies source URL/time, matching original_response_sha256 and `import_options` containing graph_id, timezone, difficulty_convention and explicit difficulty_mapping. The command is offline, enforces a 4 MB input limit, sanitizes metadata, records hashes and refuses to overwrite an existing snapshot. It does not establish that a supplied URL/license claim is truthful: verify the provider and reuse terms before adoption.

## Before app adoption

Review coverage, directions, boarding/alighting and walking connections, regional grades and actual operating information. Identify validated start/finish stations. Add tests for disconnected destinations, missing/closed lifts and time windows. Retain an explicit research label until qualified review and field validation exist. Do not offer the sample as a new resort merely because its lines draw successfully.
