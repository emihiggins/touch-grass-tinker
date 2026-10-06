# App evidence and media index

## Current UI captures

- `recorded-corrected-desktop.png`: latest recorded-example interpretation with corrected hard exclusions and confirmed route.
- `mobile.png`: latest mobile layout.
- `corrected-itinerary.pdf` and `print-preview.png`: current one-page A4 output, with approved constraints and source disclosure; text and raster inspected.
- `browser-report.json`, `keyboard-check.json`, `print-check.json`: matching targeted checks. Not a comprehensive accessibility audit or field validation.
- [Recorded walkthrough](../../../demo/walkthrough.webm) and `video-playback.json`: latest49-second silent recording. Exact-input recorded mode, not continuous live inference.

## Historical live connection evidence

`live-browser.json` and `live-desktop.png` preserve the earlier real app→Tinker call. They prove that connection was exercised, not the current UI appearance or a semantically correct interpretation. The model softened “no drag lifts”; the error is explicitly recorded. No new paid call was made merely to refresh screenshots.

## Release checks

`package-check.json` records the isolated deterministic package build. `fresh-checkout.json` records the separate clean Git worktree rehearsal. Secret-scan reports are scoped checks, not guarantees of every possible privacy issue. Current docs/media audits are additional release checks; none establishes a hosted app or public repository visibility.
