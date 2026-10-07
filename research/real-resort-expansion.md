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

## Ikon/Epic Colorado candidates — October 7 follow-up

Added partial [Winter Park](../data/terrain/winter-park-research/README.md) and [Breckenridge](../data/terrain/breckenridge-research/README.md) extracts to the **browse-only** preview, not planner selection.

| Sample | Nodes | Piste segments | Lifts | Weak components | Nodes on directed cycles |
|---|---:|---:|---:|---:|---:|
| Winter Park | 523 | 508 | 12 | 13 | 93 |
| Breckenridge | 1,136 | 1,125 | 21 | 29 | 5 |

These are graph segments, not unique trail counts. Both are incomplete, with major connectivity gaps. The first Winter Park request exceeded the 4 MB limit and was discarded; a narrower area was downloaded. No limit was bypassed. Breckenridge source contains 31 expert-tagged ways; their native evidence is retained, but expert terrain is excluded rather than collapsed to black. A future expert-grade contract must be separately designed and reviewed before routing it.

The official [Winter Park Ikon page](https://www.ikonpass.com/en/destinations/winter-park-resort) identified the destination. Official Epic/Whistler page fetches were blocked; Breckenridge is retained as an Epic research candidate, not a verified current access entitlement. No blackout/day/tier/season rules or operator feed are encoded. Pass names do not license official map artwork.

The four-sample review viewer now uses an external same-origin script compatible with the server CSP. Projection is centered with longitude correction, smaller-component filtering actually filters components, and changing sample/filter clears old details. Browser evidence covers all four datasets at390/768/1440px, keyboard segment selection, no body overflow, within-viewBox geometry and zero external requests. Axe's test-only script uses CSP bypass for injection; normal interaction checks do not bypass CSP. This closes the earlier unverified preview gap, not the real-world access/coverage gap.

## Colorado connectivity diagnostics — October 7, 2026

The deterministic diagnose_connectivity.py report links source OSM ways to imported graph edges without changing either graph. It records both directed endpoint incidence and a bounded 30 m proximity search as review evidence only; it does not add connectors or enable routing.

| Sample | Source passenger aerialways | Imported aerialways | Passenger lift endpoints | Endpoints with no exact incoming/outgoing piste incidence | Excluded source ways | Proximity candidates |
|---|---:|---:|---:|---:|---:|---:|
| Winter Park | 12 | 12 | 24 | 15 | 2 | 1 |
| Breckenridge | 21 | 21 | 42 | 40 | 35 | 10 |

A follow-up classification audit corrected the original source-lift counts: station outlines and freight aerialways are not passenger lifts. Winter Park's extra aerialway was a station polygon; Breckenridge had two station ways and one goods aerialway. These remain source evidence but are excluded from passenger endpoint counts. The earlier17/26 and46/48 endpoint figures included those non-passenger objects and are superseded by15/24 and40/42. All imported graphs are unchanged. Winter Park's Dogpatch exclusion is a closed/area way, not an ordinary missing directed trail. Breckenridge's31 expert-tagged excluded ways remain unpromoted.

Prioritized questions are: identify each lift's actual boarding and alighting terminals; verify whether a permitted, directionally valid descent reaches each terminal; inspect the excluded source ways and any station relations; and determine whether the bounded extract omits connecting coverage. Exact shared nodes and nearby geometry are evidence for that review, not inferred incidence. The saved graph.json files remain byte-for-byte unchanged by diagnostics.

The output packets are data/terrain/winter-park-research/connectivity-diagnostics.json and data/terrain/breckenridge-research/connectivity-diagnostics.json. Their limitations remain: OSM relations, current operations, access permissions, closures, safety and measured timing were not resolved.

## Station evidence and map inspection

The hash-matched original Winter Park response was still available locally. A bounded, allowlisted extraction now retains station-node coordinates/tags and directly matching relation members, without contributor identities. Fifteen passenger-lift endpoint entries carry `aerialway=station`. No directly matching lift/endpoint relations occur in this bounded response; that does not establish upstream absence. The raw-byte hash, graph hash and original fetch date bind the supplement to its source.

The review preview's lift selector shows source-start/end markers, exact incoming/outgoing piste counts and links to source nodes. These markers are not verified boarding/alighting directions. Breckenridge uses saved sanitized coordinates and explicitly reports raw station tags as not recovered. Other resorts with no endpoint diagnostic have that selector disabled. Nothing adds connectors, modifies graph bytes or enables routing.

Next useful evidence is focused source review of the15 Winter Park passenger endpoints without exact piste incidence, followed by independently verified boarding/transfer/access observations. More automatic snapping would hide rather than resolve that gap.


## Excluded source geometry review (2026-10-07)

The offline browse-only research viewer now exposes excluded source geometry without promoting it into routing. Winter Park shows the closed `Dogpatch` area and station infrastructure separately; Breckenridge shows excluded expert directed lines such as `Imperial Bowl`, with native tags, importer reason, status, and source-way links. Closed areas, directed lines, and non-passenger infrastructure have distinct labels. The overlay is diagnostic evidence only: no connectors, grade changes, or routing edges are inferred.

The generated artifact validates each diagnostic and station supplement against the saved source/graph hashes. Browser checks covered 390px rendering, keyboard selection, source-link rendering, overlay toggling, and zero requests outside the local viewer.
