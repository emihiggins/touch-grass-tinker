# Unreviewed Alpendorf lab terrain

**Simulation/research only.** Geometry connectivity is not verified skier access. No current status, measured duration or field validation is included.

Source: © OpenStreetMap contributors, https://www.openstreetmap.org/copyright . This OSM-derived database is provided under [ODbL 1.0](LICENSE-ODbL.md); retain attribution and applicable share-alike obligations. This data license does not choose a license for original application code.

Fetched 2026-10-05 from:
https://api.openstreetmap.org/api/0.6/map?bbox=13.224,47.303,13.25,47.314

Original response SHA-256: `19f5e76f53e54c7c6c64f28eeed2ba1fb9c83e3fa12b53a310de706e12bb9ccd`.

`alpendorf-source.osm` is a sanitized extract: nodes retain only ID/coordinates; ways retain ID/version, node references and tags; relations and contributor identity/history are removed. It is not a byte-identical source archive. `alpendorf-lab.json` is a normalized graph retaining the original response hash. Reimporting the sanitized extract yields the same graph except its source hash (and therefore graph/scenario content hashes). Never compare those hashes as if the original and sanitized files were identical.

Importer: `liftlap/import_osm.py`. No snapping, inferred transfers or relation inheritance. Unknown difficulty, conflicting overlapping difficulty, reversed-direction tags and explicit private/no access are excluded. Directions otherwise follow way order and remain unreviewed. Source-level novice and easy grades are both mapped to Austrian blue for this lab; retained source tags distinguish them. Pistes are split into native node pairs, lifts are terminal-to-terminal edges; intermediate lift boarding is not modeled.

Durations are illustrative assumptions: 3 m/s lift and 4 m/s piste, minimum one second per edge. They are not measured skier speeds or official ride times. All-open statuses in the CLI are synthetic scenario inputs, not facts copied from OSM.
