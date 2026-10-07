# Patscherkofel bounded research snapshot

Imported October 7, 2026 from the OpenStreetMap map API. This is **not whole-resort coverage, current operating data, or a navigation product**. It is not selectable in the application.

- [Source and license manifest](manifest.json): retrieval URL, bounding box, raw/sanitized/derived hashes and explicit regional difficulty mapping.
- [Structural audit](structural-audit.json): disconnected components, directed cycles, source lineage and assumed timing.
- [Import exclusions](import-audit.json): unknown grades, restricted or ambiguous ways remain excluded.
- [Source-way review packet](../../../research/evidence/resort-review/patscherkofel/ways.csv): pending direction/access/boarding review.

OSM data is © OpenStreetMap contributors, ODbL 1.0; see [database license](../LICENSE-ODbL.md). MIT covers our code, not this database. Contributor identities/history are removed from the saved snapshot. All durations are assumptions. Native grades remain preserved; normalized mappings are provisional and must be checked locally. Missing operating tags mean unknown, never open.

Reproduce this graph by passing source.osm and manifest.json import_options to liftlap.import_osm.import_osm. The regression suite checks exact graph and exclusion-report equality.
