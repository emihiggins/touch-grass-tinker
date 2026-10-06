# App integration and demo — October6

## Delivered

- Server-side Qwen3-8B base interpretation using the already pinned SDK, renderer, prompt and strict schema. Model calls are opt-in; the default server is dependency-free Rules/recorded mode.
- Real browser request completed through `/api/interpret`, then explicit confirmation and a validated simulated route. The model softened “no drag lifts” into avoided lifts: this semantic error is retained in the evidence, not called a successful interpretation.
- Hard exclusion checkboxes correct the intent locally, remove overlapping soft preferences, invalidate an existing route and require confirmation. They do not cause another model call.
- Recorded mode checks the exact input/context/catalog hash. Changed inputs are refused rather than assigned a canned model answer. Source and user-correction disclosure persists on the itinerary and print view.
- Desktop/mobile/print generation, unsupported input, closures, stale confirmation and replay mismatch checks. Actual silent WebM recording in `demo/walkthrough.webm`; see `demo/README.md`.

## Run offline

```sh
python3 -m liftlap.server --port 8767
```

Open the loopback URL on the same machine. Load example, select Recorded AI, review/correct exclusions, confirm. Other text can use Rules mode. Neither mode calls the provider. The app never serves run directories, keys, source files or arbitrary paths.

## Live verification and financial bound

The private verification server was started through the existing protected Gateway environment with:

```sh
.venv-tinker/bin/python -m liftlap.server --port 8768 --live-model
```

This already consumed the one-time `app-demo-01` reservation key. **Do not rerun it to reset the allowance.** Startup refuses a duplicate key. This is intentionally a bounded demonstration, not a production service. One live model request ran, under a pre-reserved$0.10 envelope permitting at most10 attempts, each input-token-checked below$0.01. Failures consume an attempt; ambiguous provider outcomes pause the adapter without retry. The shared ledger retains the full reservation pending billing. Total holds$1.75, not actual invoiced cost.

Credentials stay server-side via the existing protected SDK path. Live request and provider evidence stay under ignored `runs/app-demo-01`; the UI discloses provider transmission and private local retention. The published replay candidate contains only fictional text/context and model intent, no provider IDs.

## Verification

-149 tests pass in the optional environment; standard-library run149 with22 optional skips.
-`scripts/browser-ai-live.cjs`: real live interpretation/confirmation/route connection (semantic caveat above).
-`scripts/browser-ai-demo.cjs`: offline replay/correction/closure/unsupported/mismatch/mobile flow and video recording.
-`scripts/browser-smoke.cjs`: original fictional and Alpendorf flows.
-`python3 scripts/package_demo.py`: allowlisted archive under ignored `dist/`, tested in an isolated temporary directory without repository state, keys or optional model packages. No claim of hosted deployment or fresh Git checkout provenance.

## Remaining release decisions

[Concrete publication choices](../submission/release-decision.md): code visibility, original-code license, video upload and DEV account/publication. The server remains loopback-only; no authentication/public quotas/real-world terrain verification are implied. Public hosting would need a separately designed deployment, not changing the bind address. A downloadable demo/video is sufficient for the proposed release path, subject to challenge review.

## Release-focused followups

MIT is approved and applied; the demo archive includes the license and terrain notices and builds deterministically. The original request/settings are visible in confirmation, and approved constraints remain on the itinerary. A keyboard focus-loss bug was fixed. Targeted keyboard activation/correction, visible focus and320px reflow pass; this is not a full accessibility certification. The regenerated A4 PDF is one page; its raster was visually inspected and all approved limits, hard exclusions, recorded source and simulation notices are legible. [Print preview](../research/evidence/app-integration/print-preview.png).

Emi alone will change GitHub visibility and publish to DEV. [Posting checklist](../submission/dev-posting-checklist.md). No public host or new inference was created for these improvements.
