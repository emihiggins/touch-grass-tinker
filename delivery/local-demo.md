> **Historical planning/checkpoint document.** Retained for provenance, not a current feature or task list. Use the [current documentation](../docs/README.md) for the implemented app, completed experiments and supported setup.

> Current status: [app integration and recorded demo](../delivery/app-integration.md). Older checkpoint sections below are historical, not remaining execution gates.

# Local demo checkpoint — 2026-10-06

## Delivered

1. **Reversible graph contraction:** 469 nodes / 495 edges → 67 nodes / 93 edges on the current all-open lab scenario with the start/finish protected. Only nonbranching piste chains with matching difficulty, review status, duration basis and scenario state merge. Lifts, junctions, start/finish and state changes remain boundaries. Every source edge appears once in the contraction mapping. Geometry mismatches fail rather than snap. Source-edge count/visit bounds remain enforced. Expanded returned routes pass the original graph/scenario validator. [Evidence](../research/evidence/compaction-check.json).
2. **Rules-v1 comparator:** explicit grammar and abstention, 22/32 exact matches on the visible development seed. This is not a held-out result and not Tinker use. All predictions/failures preserved in [benchmark](../benchmark/README.md).
3. **Local UI:** terrain selection, time/grade controls, optional rules text, parsed-constraint review, explicit confirmation, map schematic, itinerary, all-lifts-closed scenario and print view. Supports fictional Pine Mountain and unreviewed Alpendorf lab data. Labelled simulation throughout. No external fonts, map tiles, model APIs or analytics.

## Run

```bash
python3 -m liftlap.server --port 8767
```

Open `http://127.0.0.1:8767` **on that same machine**. This is not a public deployment or a Telegram-accessible URL. Bind is fixed to loopback. Stop with Ctrl-C. No model key or dependencies required. Verification server is stopped after checks, not left running as a service.

## HTTP surface and limits

- `GET /`: single-screen demo, initial/loading/review/unsupported/no-route/success states.
- `GET /api/context?terrain=synthetic|alpendorf`: graph/catalog/context from server-owned data.
- `POST /api/interpret`: terrain, optional text, minutes and difficulty → rules intent plus recognized/unparsed text.
- `POST /api/plan`: server-owned terrain/scenario choice and strict intent → compact search, source expansion, original validation and human-readable steps.
- Only allowlisted static assets are served; other routes return 404. Host validation and same-origin POST checks; 16 KB body limit and 2,000-character language limit; strict place catalog/intent checks; content-security policy; no raw prompt logs.

This is an internal prototype, not a production service. No authentication, public rate limiter, global quotas, durable request cancellation or hardened request-read timeout. Do not expose it publicly unchanged. It cannot call Tinker or other providers. Fixed 2027-01-15 10:00 local scenario; timings and closures are assumed. On-mountain safety, terrain permission and real-time suitability are not established by software tests.

## Verification performed

- 47 standard-library unit/integration tests passed, including compaction/expansion, original-node bounds, independent validator, rules parsing/abstention, HTTP confirmation flow, closures, invalid input, origin rejection and body limits.
- Node syntax check passed for browser JS.
- Real Chromium flows at 1280px desktop and 360px mobile: fictional route, closed-lift no-route, unsupported wording blocked, Alpendorf lab route, input focus and reduced-motion media exercised. No page errors; no mobile horizontal overflow.
- Inspected [mobile screenshot](../research/evidence/ui-mobile.png); [desktop screenshot](../research/evidence/ui-desktop.png) saved.
- Actual A4 [PDF](../research/evidence/ui-itinerary.pdf) generated; explicit PDF page objects counted in [UI report](../research/evidence/ui-check.json). Full print raster/legibility review and comprehensive keyboard/accessibility audit remain open.
- Browser smoke script: `PLAYWRIGHT_MODULE=/path/to/playwright-core node scripts/browser-smoke.cjs`, while local server runs on 8767. Browser tooling is external to the dependency-free app, not bundled as a locked runtime dependency.

## Remaining gaps

Real-world terrain review / third meaningful loop, ambiguity-heavy language support, typed production API and independent full contract coverage, actual Tinker access/training, held-out evaluation, public deployment and submission. UI lacks a dedicated comparison screen and direct editing of parsed chips; form edits invalidate previous confirmation and require another review. SVG display is a schematic, not a navigational basemap. All requirements stay partial until their complete acceptance criteria are evidenced.
