# Local interpretation corrections

## Purpose
A ready model/rules interpretation may have the wrong duration or maximum grade. Let the user correct those fields locally, just as hard exclusions can be corrected, while keeping the original request/settings visible.

## Behavior
- Whole-minute budgets 1–1440; explicit grade selection including no stated maximum.
- Draft edits invalidate any displayed itinerary and disable confirmation.
- Apply validates the local fields, updates approved intent and records only changed fields in provenance.
- Lift edits do not bypass pending time/grade drafts. Combined correction provenance survives later changes.
- Draft time/grade edits can be discarded without another interpretation; applied lift edits remain intact and the old route stays invalidated.
- User must confirm after applying. Unsupported/unresolved interpretation states are not promoted to ready.
- Print and text downloads use corrected approved constraints. Frozen model evidence and saved response files are unchanged.

## Existing foundations
Native HTML form validation, existing intent/schema validation, original request display and routing validator. No framework or additional provider call required.

## Evidence
`browser-corrections.cjs` verifies invalid/zero/fractional/out-of-horizon edits, stale-route clearing, lift-toggle bypass prevention, planner payload, original-settings preservation, combined provenance and actual downloaded text. Existing responsive, map, recovery and recording checks remain required.
