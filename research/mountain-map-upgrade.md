# Mountain map and real-resort data upgrade

Research checked 2026-10-06. **Proposed work, not shipped functionality.** No paid mapping service, live feed, or new resort routing integration has been enabled.

## Recommendation

Keep the lightweight SVG as the offline/print fallback, improve its geographic proportions and legibility first, then prototype **MapLibre GL JS in 2D** using a bounded Alpendorf snapshot. Add terrain shading only after choosing a DEM source with explicit redistribution/hosting terms. Make 3D an optional orientation aid, not the default itinerary view.

Use existing raw OpenStreetMap topology for routing research and OpenSkiData for discovery/display enrichment. These are different jobs: attractive trail lines are not proof of traversable connections, direction, boarding permission, opening hours or safe access.

## What the current sketch needs

The current SVG independently scales longitude and latitude into a 700×480 view. This can distort shape and provides little surrounding context. Prioritize:

1. Aspect-preserving local projection, north indicator, scale and consistent framing.
2. Named lift stations, selected start/end, numbered itinerary legs and direction arrows.
3. Selected-route casing, distinct lift/piste styles and a legend that works without color alone.
4. Linked map/itinerary selection, keyboard-accessible details and zoom/reset controls.
5. Terrain context: hillshade/contours, then optional tilt; retain legible flat print output.

Do not present the fictional demonstration graph as a georeferenced real resort. Distinguish schematic and geographic modes visibly.

## Renderer choices

| Option | Strength | Cost/tradeoff | Decision |
|---|---|---|---|
| Existing SVG | Offline, printable, no runtime dependency | Manual interaction/label placement; limited terrain | Improve first; keep fallback |
| MapLibre GL JS | GeoJSON line layers, interactive map, raster DEM hillshade and terrain | WebGL/device testing; separate data/tile licensing and asset delivery | Preferred geographic-map prototype |
| OpenSnowMap overlay | Existing ski cartography; piste-only embedding explicitly permitted | Provider-dependent; no bulk downloading; relief layers not generally offered for reuse | Reference/optional online overlay, not offline foundation |

MapLibre example tiles are demonstration resources, not a production-service commitment. The library license does not license arbitrary basemaps or terrain tiles. Pin a library release and keep license notices if adopted. Reuse its renderer rather than build a custom terrain engine.

## Verified sources and bounded samples

| Source | Confirmed evidence | Best use | Limits |
|---|---|---|---|
| Existing Alpendorf raw OSM lab | Local graph has 469 nodes, 495 edges (488 piste, 7 lift); source refs and original difficulty retained; explicitly unreviewed | First real-geometry prototype without another large download | Partial extract, not whole-resort coverage; route durations/operations need validation |
| OpenSkiData | Public metadata fetched successfully; daily worldwide downloadable areas/runs/lifts/spots, schema 16.0.0 | Resort discovery and display enrichment | Derived geometry/merging does not establish routing topology; content-hash IDs change |
| South Tyrol OpenDataHub | Public one-record SkiArea request returned Plose; 28 total records; boundary polygon and position; parent LicenseInfo CC0, ClosedData false, holder IDM; metadata updated October 2 | Second candidate resort and descriptive/boundary metadata | This sample is not a lift/piste network or verified live operational feed; linked images/resources have separate terms |
| OpenSnowMap | Published policy permits piste-only tiles with attribution/referrer, forbids bulk downloads | Cartographic reference | Do not hotlink its relief layer or treat cached tiles as an offline dataset |

OpenSkiData metadata observed at 23:40 UTC: OSM source timestamp `2026-10-06T22:03:51Z`; build finished `2026-10-06T23:30:21Z`; 12,443 ski areas, 230,136 run features, 33,285 lifts. Uncompressed GeoJSON sizes: areas 21,141,162 bytes; runs 834,595,010; lifts 114,285,659. These are snapshot observations, not guaranteed future counts. We inspected metadata rather than downloading the worldwide datasets. OpenSkiData requests automated downloads no more than once daily and **does not permit direct reuse of its hosted vector tiles**. A server-side import should fetch permitted downloads once, filter to a resort, and serve a versioned local snapshot—not fetch global data in a user's browser.

The Alpendorf counts were reproduced by loading `data/terrain/alpendorf-lab.json` and counting `nodes`, `edges` and `edge.kind`. That verifies structure only, not connectivity correctness or field safety. Earlier native-node and processed-geometry findings remain in [the source audit](data-sources.md).

## Data model and adoption gates

- Preserve provider IDs and upstream OSM way/node references; do not use OpenSkiData content hashes as durable resort IDs.
- Store source URL, fetch/source timestamps, original-byte hash, schema version, bounding area, license and attribution beside every snapshot. Keep derived database licensing distinct from MIT application code.
- Preserve native difficulty and regional convention alongside normalized rank. Green/blue/red are not universal global equivalents. Unknown or ambiguous grades stay unknown until mapped explicitly.
- Separate display GeoJSON from directed routing edges. Station boarding/alighting, lift direction, actual junctions and pedestrian connectors need explicit evidence. Crossing lines or nearby endpoints must not silently create connections.
- Represent operational status as known-open, known-closed or unknown, with observation time and source; `operating` lifecycle status is not “open now.” Stale or missing data must never silently mean open.
- Retain missing duration/schedule fields as missing; distinguish estimates from operator values. Resort branding, piste-map artwork and photos are not automatically covered by OSM/parent metadata licenses.
- Audit with existing GIS tooling such as QGIS plus the existing importer/graph tests. Review disconnected components, endpoints, geometry direction, grade mapping and source lineage before offering routing outside a clearly labeled lab.

## Sequenced implementation plan

### M1 — readable sketch (small, no external services)

Acceptance: aspect preserved at desktop/mobile sizes; start/end and leg numbers visible; lift/run styles distinguishable without color; selected leg readable by keyboard and text; print remains unclipped with attribution and schematic/geographic label. Test existing routes unchanged. Regenerate screenshots, video and media hashes only after implementation.

### M2 — one-resort geographic prototype

Use existing Alpendorf first. Add MapLibre behind an explicit geographic-lab view, with locally served resort GeoJSON and an SVG fallback for unavailable WebGL. Default to flat view. Acceptance: source/license/date shown; no secret, paid request or prohibited hosted tile request; route and map selections agree; mobile touch and fallback verified. Before adding terrain, record actual DEM license, coverage, size and hosting costs. No 3D accuracy claim from an unverified elevation source.

### M3 — reproducible resort import

Create a bounded-source adapter using native OSM identifiers for routing and separately licensed metadata for display. Add Plose as a candidate only after a geometry sample and license audit. Acceptance: deterministic snapshot manifest, missing-field report, disconnected-component report, explicit grade-convention mapping and no automatic proximity connections; all imported edges trace to source. Qualified resort/domain review remains required for real navigation.

### M4 — operations integration, only if verified

Investigate operator-authorized feeds and OpenDataHub's relevant endpoints. No free reusable live lift-status feed was established by this research. Acceptance before adoption: endpoint and record-level terms, resort/edge ID mapping, freshness contract, stale/unknown behavior, closure handling and rate-limit policy verified. If unavailable, keep the product a planning/demo tool with explicit unknown status; do not scrape a resort website and infer reuse rights.

M1 can proceed independently. M2/M3 can be prototyped without paid services or another model experiment. Publication and changing repository visibility remain the owner's actions.

## Primary sources

- [OpenSkiData documentation and usage/attribution policy](https://www.openskidata.org/)
- [OpenSkiData build metadata](https://tiles.openskimap.org/metadata.json)
- [OpenSkiData schema](https://github.com/russellporter/openskidata-format)
- [MapLibre hillshade example](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-hillshade-layer/)
- [MapLibre terrain example](https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/)
- [MapLibre GeoJSON line example](https://maplibre.org/maplibre-gl-js/docs/examples/add-a-geojson-line/)
- [MapLibre software license](https://github.com/maplibre/maplibre-gl-js/blob/main/LICENSE.txt)
- [OpenDataHub bounded sample](https://tourism.api.opendatahub.com/v1/SkiArea?pagesize=1)
- [OpenDataHub licensing](https://docs.opendatahub.com/licensing/)
- [OpenSnowMap reuse policy](https://www.opensnowmap.org/iframes/about.eng.html)

OpenSkiData publishes the combined attribution: “Data from OpenSkiData / OpenSkiMap.org, © OpenStreetMap contributors (ODbL), Skimap.org, Who's On First, © Mapterhorn.” Carry the applicable source notices with imported data; do not replace them with the application's MIT notice.

## First implementation checkpoint

Aspect-preserving projection, zoom/fit controls, selected-route casing/arrows, first-visit step numbers, start/finish labels, geographic north/approximate scale and print-fit behavior are implemented. Offline browser checks cover 495 Alpendorf edges, 320px reflow and keyboard zoom. This is a partial M1 delivery: full station-name labeling, linked itinerary selection and panning remain open. MapLibre, terrain shading and additional resort imports remain planned.

## Interactive map checkpoint

M1 now includes pointer/keyboard panning, known catalog station labels and grouped-itinerary-to-source-edge highlighting. Unknown station names remain unlabeled rather than invented. M2 now has an optional vendored MapLibre 5.6.2 geographic view over the same local Alpendorf data, flat by default, with renderer-failure fallback and SVG printing. Browser checks require actual rendered features and reject external network requests. No new resort import, basemap, DEM, operational feed or field validation is implied. M3/M4 remain planned.

The deterministic `python3 scripts/audit_resort_snapshot.py` audit now records exact snapshot hash, components, source-reference coverage and duration assumptions in [the Alpendorf report](evidence/alpendorf-snapshot-audit.json). This advances M3 provenance checks but is not an adoption approval or a new dataset.

## Second-region import checkpoint — October 7

A bounded [Plose OSM fixture](../data/terrain/plose-research/README.md) now exercises explicit regional configuration, privacy sanitization, source/derived hashes and exact offline reconstruction. It retains 61 nodes/62 edges and is not enabled in the app. The importer refuses implicit non-Austrian grade mappings. Regression checks preserve the historical Alpendorf graph. This advances M3 tooling/provenance; qualified access review, live operations, elevation and a complete second-resort product integration remain open.

## Directed-connectivity follow-up

[Source review packets](evidence/resort-review/README.md) now cover 70 Alpendorf and 8 Plose ways. The directed audit finds no cycle in the Plose fixture despite weak connectivity, so it cannot support lap planning as imported. Alpendorf has a 204-node strongly connected component; other nodes do not belong to a nontrivial directed cycle. Resolve source direction/coverage gaps with evidence rather than synthetic connections. This is a concrete adoption blocker, not a failure of the model benchmark.

## Coverage investigation

A [wider Plose sample](../data/terrain/plose-expanded-research/README.md) retains 247 nodes/251 edges but still no directed cycle. Four excluded `piste:type=connection` ways provide a concrete review lead: allowing their source direction hypothetically creates 20 cyclic nodes. Saved routing graphs remain unchanged. Sanitization now retains unsupported piste types for review rather than discarding the evidence; such types remain non-routable. Qualified transfer/access evidence is the next gate.
