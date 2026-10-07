# Map-first UI refresh

## Scope and design thesis
A mountain field guide: a compact introduction, a prominent terrain view, an explicit constraint-review workflow and a printable itinerary. Reuse the existing bundled MapLibre renderer, SVG and system fonts; no additional runtime dependency or external asset service.

## Surface inventory
- `/`: initial/loading, terrain selection, rules/recorded/disabled-live modes.
- Interpretation: ready, unsupported input, recorded-input mismatch, corrected hard exclusions, invalidated settings.
- Planning: searching, valid itinerary, no route, search limit and request error (same status surface).
- Maps: fictional schematic, real-source sketch, geographic hillshade, selected itinerary, zoom/pan, elevation failure and WebGL fallback.
- Phone/tablet/desktop, reduced motion, forced colors and A4 print. Auth/billing/publication screens do not exist in this app.

## Implemented
- Shorter introduction and wider map beside a distinct planning panel; phone map first with section jump links.
- One active canvas: geographic view replaces the sketch, which remains the print/failure fallback.
- Fictional display-only separated lift/run paths, named runs, station labels and an explicitly schematic mountain illustration. Source graph, direction, topology, durations and evaluated labels are unchanged.
- Larger map controls, keyed legend, selected-step treatment and focusable itinerary scroll region.
- Local terrain attribution remains visible. No new live-conditions or access claims.

## Acceptance and evidence
- Browser map test: 495 Alpendorf features, itinerary selection, keyboard/pointer pan, hillshade failure, WebGL fallback, no external requests.
- UI test: initial/planned/geographic states at 390, 768 and 1440 pixels; axe WCAG A/AA; incomplete findings retained for manual review. Explicit light theme (no separate dark palette).
- Demo test: approval/correction, unsupported/mismatched requests, closed lifts, stale confirmation, 360px viewport and actual A4 PDF.
- Actual screenshot/PDF inspection, source/media fingerprint refresh, full offline release checks and secret scan before merge. The final A4 sample remains one page with a larger map. SVG text/placeholder contrast checks marked incomplete by axe were manually inspected; labeled control groups and station-marker roles were corrected; they remain in the report, not presented as an accessibility certification.

## Next high-value work
- Qualified review of real-resort access/directions remains necessary before navigation claims; visual polish does not satisfy it.
- Implemented next: [route inspection](route-inspection.md) uses queue-inclusive simulation estimates with explicit uncertainty, not real-world timing.
- A larger independent field evaluation is preferable to tuning on the frozen 16-case result; no new model run is part of this UI change.
