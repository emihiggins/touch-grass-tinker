# Real-resort expansion: data before navigation

Checked/imported October 7, 2026. Goal: progress from fictional demonstrations to a useful, independently validated real-resort product. More geometry alone is not enough.

## New evidence

Two bounded OpenStreetMap API downloads (each below the existing 4 MB research limit) add contrasting regional samples. Named source ways identify Wachusett's Polar Express/Conifer Connection and Patscherkofelbahn/Olympiaabfahrt. These are bounded areas, not resort boundary definitions. Complete source ways can extend outside requested boxes.

| Research sample | Nodes | Edges | Lifts | Weak components | Nodes on directed cycles |
|---|---:|---:|---:|---:|---:|
| [Wachusett, Massachusetts](../data/terrain/wachusett-research/README.md) | 506 | 520 | 8 | 9 | 32 |
| [Patscherkofel, Austria](../data/terrain/patscherkofel-research/README.md) | 139 | 144 | 2 | 3 | 0 |

Edges are raw graph segments, **not unique ski runs**. Cycles may omit required lifts or represent erroneous source direction; they do not prove a usable ski lap. Neither sample is enabled in the app. Times are assumed and current operating status is unknown.

The US sample uses explicit provisional novice/easy→green, intermediate→blue, advanced→black mapping, rather than inheriting Austrian blue/red/black. Native tags stay available for review. Expert, freeride and unrecognized grades are not collapsed to black. Difficulty labels are local and cannot guarantee equal difficulty across resorts.

[Machine-readable catalog](evidence/resort-catalog.json) inventories all separate research snapshots with source dates, hashes, component counts, timing basis and unknown operational state. The existing Alpendorf selectable simulation remains separate; its source/graph and UI are unchanged. Plose and its wider extract are two snapshots of one resort, not two resorts.

## Source choice and limitations

Reuse the existing conservative native-node OSM importer rather than build another map stack. OSM supplies topology/source references under ODbL; keep derived databases and attribution separate from MIT application code. OpenSkiData is useful for discovery/display but its derived geometries do not establish boarding topology. Earlier [source research](mountain-map-upgrade.md) documents download and hosted-tile restrictions.

Current general web-search requests timed out. No new official operator feed, reuse permission or live status claim was established in this pass. Download URLs and hashes are recorded in each manifest. Operator artwork, photos and websites are not bundled or assumed to share OSM's license.

## Prioritized path to real users

1. **One-resort topology review first.** Start with existing Alpendorf and use Wachusett to test US grade behavior. Work through source-linked way packets: verify lift boarding/alighting, descent direction, transfer paths, access restrictions and missing coverage. Never snap nearby lines automatically. Acceptance: every enabled edge has dated review evidence and every offered lap passes a reviewed lift→descent→return fixture; unresolved edges remain disabled.
2. **Versioned resort catalog and browse-only preview.** Build on the current research catalog. The generated [`web/resort-review.html`](../web/resort-review.html), also served at `/research-review.html` by the loopback demo, shows both bounded samples, date/hash/ODbL attribution, native grades, source-way inspection, weak components, keyboard-selectable SVG geometry, and explicit no-routing warnings. Run `python3 scripts/build_resort_review.py` to regenerate it. It makes no network requests; unreviewed data remains outside the planner. Browser-render evidence is still a release gap if automation is unavailable.
3. **Operator-authorized status adapter.** Obtain explicit reuse terms and stable IDs for lift/run openings, hours and closures. Store observed-at, expiry and provenance separately from static OSM geometry. Acceptance: stale/missing observations cannot become open; closure changes invalidate affected itineraries. No scraping or operator contact undertaken in this pass.
4. **Measured timing and field validation.** Replace blanket speeds with measured lift journeys, transfers and conservative queue ranges. Acceptance: estimates carry source/date/confidence and are checked against consenting local testers; mismatch and return-time failures remain visible.
5. **Controlled real-user pilot.** Only after the above gates, offer one resort with a clear coverage boundary and fallback to official information. Include incident reporting, map corrections and offline route access. Do not expand broadly before the first resort is reliable.

## Reproduction

`python3 scripts/resort_catalog.py` rebuilds the inventory offline. `python3 scripts/check_release.py` checks data fingerprints and exact import reproduction, alongside existing application tests. Original raw downloads stay outside the repository; sanitized OSM source and separate hashes are retained. No training data, model calls, paid services or app screenshots changed.
