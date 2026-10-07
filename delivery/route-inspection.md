# Route inspection iteration

## User value
Move through repeated laps without losing which visit is selected; understand each leg's assumed duration and position in the outing; focus the relevant map geometry.

## Existing components reused
The existing API already groups itinerary legs and supplies travel seconds. Reuse it, the native button/list controls, SVG transforms and bundled MapLibre fitBounds. No new runtime library or service.

## Implemented behavior
- Grouped leg durations include scenario queue time. Each leg includes cumulative start/end seconds and an explicit assumed-time basis.
- Previous/Next controls select individual itinerary visits; focus acts on exact edge membership in either renderer.
- Geographic clicks cycle repeated visits just like SVG clicks.
- Settings/terrain/reinterpretation invalidate old inspection state.
- Non-itinerary geographic features show source information without retaining an unrelated leg's timing.
- Printed and on-screen step labels show estimated minutes; no current-queue or live-arrival claims.

## Acceptance
- Queue-bearing fixture: grouped durations sum exactly to validated outing time; adjacent cumulative times meet; repeated visits remain separate.
- Browser: Previous/Next and focus work, repeated edge visits advance, changing terrain hides the old inspector, existing rendering/fallback checks still pass.
- Responsive/axe checks, refreshed recording/PDF, saved model evaluation and packaged demo remain valid.

## Remaining product boundary
These estimates are simulation inputs. Real-resort durations, access and operations still require independently reviewed data; displaying estimates does not validate them.
