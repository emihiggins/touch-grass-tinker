# Lift-Lap Planner data-source investigation

Checked 2026-10-05. Distinguish directly inspected data from documented capabilities and unverified possibilities.

## Recommendation

Use **OpenSkiData / OpenStreetMap** as the primary terrain source. Evaluate **Snow Space Salzburg (Flachau/Wagrain/St. Johann)** first because a small ODbL routing-graph export already exists. Do not adopt its full graph unchanged: it is unreviewed and fragmented. Select a small audited sector, or derive one from upstream OSM if the candidate is unsuitable. Use explicitly simulated operating states for the initial demo; live operations are a separate integration gate.

This is a resort candidate, not a final selection. Data reuse does not substitute for the original Tinker training task and evidence required by the challenge.

## 1. OpenSkiData: primary global source

- Official downloads and terms: https://openskidata.org/
- Runs: https://tiles.openskimap.org/geojson/runs.geojson
- Lifts: https://tiles.openskimap.org/geojson/lifts.geojson
- Ski areas: https://tiles.openskimap.org/geojson/ski_areas.geojson
- Stations/crossings/spots: https://tiles.openskimap.org/geojson/spots.geojson
- Build metadata: https://tiles.openskimap.org/metadata.json
- Processor: https://github.com/russellporter/openskidata-processor
- Typed schema: https://github.com/russellporter/openskidata-format

**Verified:** official site describes GeoJSON, CSV and GeoPackage exports, elevation profiles, run difficulty and regional conventions, lift types/durations, source IDs and ski-area membership. Lift download HEAD returned HTTP 200. Metadata GET succeeded with curl (Python urllib initially returned 403). Full global datasets were not downloaded or audited.

Metadata observed: format 16.0.0; build finished 2026-10-04T23:32:47.931Z; OSM timestamp 2026-10-04T22:04:43Z; 12,272 ski areas, 230,106 run features, 33,278 lifts and 33,907 spots. A run feature is not necessarily one named piste. Uncompressed runs approximately 844 MB, lifts 116 MB; prefer a bounded extract over repeated global downloads.

**Important semantics:** the schema's `Status` explicitly describes lifecycle state, NOT real-time availability. `operating` means in operation when conditions permit, not open now. See https://github.com/russellporter/openskidata-format/blob/master/src/Status.ts . Feature IDs are content hashes and can change between builds; retain upstream OSM IDs plus pinned snapshot identifiers.

**Terms:** ODbL; retain all source attribution. Official ready-made attribution: “Data from OpenSkiData / OpenSkiMap.org, © OpenStreetMap contributors (ODbL), Skimap.org, Who's On First, © Mapterhorn”. Applicable derivative-database share-alike obligations must be met on public use/release; the application code license is a separate decision. Automated downloads at most once per day. Direct use of hosted vector tiles is prohibited; render our bounded GeoJSON or host our own tiles.

## 2. SlopePlan Flachau graph: fastest candidate, with serious audit limits

- Repository and derivation notes: https://github.com/srgal/slopeplan-data
- Inspected revision: `ce3b2a11b782c17f9f58fae3cea7008e09d4d55f`
- Terrain: https://raw.githubusercontent.com/srgal/slopeplan-data/ce3b2a11b782c17f9f58fae3cea7008e09d4d55f/flachau/terrain.json
- POIs (listed, not audited): https://github.com/srgal/slopeplan-data/blob/main/flachau/pois.json
- License read: https://github.com/srgal/slopeplan-data/blob/main/LICENSE

**Downloaded and parsed:** terrain is 298,467 bytes, version `osd-2026.10.02`, generated 2026-10-02T09:08:57.788Z. SHA-256: `6e6201d12a0ba7f6eb7df6c2a4f0dd64008d3b2394dc8e46f0a3bbaaa73fae0b`.

Independent structural audit:

- 179 nodes; 231 piste segments (114 blue, 103 red, 14 black); 45 lifts.
- Lift types: 15 chairlifts, 9 gondolas, 8 platters, 5 rope tows, 5 T-bars, 1 cable car and 2 magic carpets.
- Zero missing node references in piste endpoints and consecutive lift station pairs.
- Ignoring all candidate walking links, treating each piste endpoint pair and consecutive lift-station pair as undirected edges solely for a connectivity diagnostic gives **13 weak components**: 73, 69, 11, 5, 4, 3, and seven components of 2 nodes.
- All 10 candidate walking connections are `verified: false`; exclude by default. Never join nearby geometry automatically merely to make routes possible.
- All 45 lift schedules are null. Real-time status and hours are explicitly absent according to the README.
- Upstream review status is `unreviewed`. Its provenance `validUntil` is not a live operating guarantee. Directionality, terrain fidelity, duration accuracy and route feasibility have NOT been verified.

ODbL derivative of OSM/OpenSkiData. Attribute upstream work and preserve license. Snapshot was inspected in temporary storage; raw third-party data is not committed to this repository. Pin and vendor with its license/attribution only when selected. Check unknown/modeled attributes such as `requiresSkating` and ride-duration provenance before using them as hard facts.

## 3. Raw OpenStreetMap: source-of-truth fallback for topology

- Piste tagging: https://wiki.openstreetmap.org/wiki/Piste_Maps
- Lift tagging: https://wiki.openstreetmap.org/wiki/Key:aerialway
- Overpass documentation: https://wiki.openstreetmap.org/wiki/Overpass_API
- License: https://www.openstreetmap.org/copyright

Use a bounded Overpass query for downhill piste ways/relations, aerialways, station nodes and relevant POIs; retain native way/node IDs for topology and audit. Documentation inspected for piste semantics; no Overpass extract was executed in this investigation.

Pistes can be polygons, centerlines, or grouped relations. Downhill ways conventionally point downhill, but mapping errors remain possible. Shared nodes help establish connectivity; geometric crossings alone do not. Validate terminals, grade-separated crossings, direction, boarding/alighting and return-to-base paths. Preserve regional difficulty conventions; blue in Austria is not interchangeable with blue in North America.

ODbL applies. API availability and completeness vary. Cache one snapshot for the experiment rather than requesting data at every user interaction.

## 4. South Tyrol Open Data Hub: alternative/enrichment

- API documentation: https://tourism.api.opendatahub.com/swagger/index.html
- Ski areas: https://tourism.api.opendatahub.com/v1/SkiArea?pagesize=1
- Activities/POIs endpoint (catalog-discovered): https://tourism.api.opendatahub.com/v1/ODHActivityPoi
- Licensing: https://docs.opendatahub.com/licensing/

**Directly verified:** unauthenticated ski-area GET returned JSON with 28 total results; sampled Plose record has geographic geometry, multilingual descriptions and `LicenseInfo` identifying CC0, `ClosedData: false`, holder IDM Südtirol. This establishes accessible ski-area metadata, not a complete routing graph.

Search surfaced lift/slope catalogs and a snow-report dataset described as limited-access. Their specific records, status freshness and access rights were NOT verified. Check each record's LicenseInfo; external resources/images have separate licensing. Do not infer that metadata access grants live operational data access. Strong candidate if we choose a South Tyrol resort, not an enrichment source for Austrian Flachau by default.

## 5. Live status, opening hours, queues and travel time

No freely reusable live operations feed was established in this investigation. Resort websites and commercial aggregators may display reports; visibility is not an API/reuse license. A Skiresort snow-report page was accessible but is not adopted as an ingestion source. Do not scrape third-party private endpoints or buy a feed as part of this research.

For MVP, explicitly label a simulated winter-day scenario with closure flags and operating windows. Queue delays and ski travel times remain model assumptions. Never use OSM lifecycle status as open-now. Future official status adapters need permitted access, source timestamps, expiry rules, stable ID mapping and unknown/stale behavior.

## Next gates

1. Choose a connected sector in the candidate graph; verify against current official resort information without copying copyrighted map artwork.
2. Inspect enough lift/piste cycles to establish downhill direction, board/alight nodes and realistic return paths; remove unverified connectors.
3. Determine actual versus assumed durations and difficulty. Exclude unsupported constraints rather than inventing fields.
4. Preserve frozen source hashes and licenses; maintain any corrected derivative graph separately from application code.
5. Build language training examples on original synthetic graphs/scenarios, with a separately held-out audited real-graph evaluation. Split paraphrase families to prevent leakage; measure baseline before training.
6. If the sector cannot be validated quickly, choose a smaller resort via an OSM extract rather than repairing the entire region.
