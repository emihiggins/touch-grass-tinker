# Lift-Lap demonstration

`walkthrough.webm` is a real Chromium screen recording of the app. It is silent; the on-screen labels and the chapter guide below explain the actions. The recording uses an **exact-input replay of one real Qwen3-8B base-model app call**, then Rules mode. It is not continuous live inference or a fine-tuned model demonstration.

## Fixed-frame walkthrough

The October 11 recording uses one **2560 × 1440 desktop frame** throughout: no page scrolling, viewport changes, cuts between device sizes or rapid zooming. Captions, a visible pointer and reading pauses explain the sequence. A **recording-only presentation layout** places the real request, review, map and itinerary panels side by side; it does not change their data, validation or event handlers. The standard application layout is unchanged.

1. Load the example and select Recorded AI.
2. Inspect the mistake: “no drag lifts” was softened into avoidance.
3. Correct t-bar, platter and rope-tow as hard exclusions, without another interpretation call.
4. Confirm and inspect the simulated route and its approved constraints.
5. Select an itinerary leg and download the local text itinerary.

This focused video no longer includes the old mobile/closure/unsupported-request montage. Those checks remain in the browser evidence and can be reproduced separately.

Re-record with the existing Playwright installation and a local server:

```sh
python3 -m liftlap.server --port 8772
# In a second terminal; PLAYWRIGHT_MODULE may point to playwright-core:
node scripts/record-walkthrough.cjs
```

`--preview` runs the same assertions quickly without replacing the video. `DEMO_URL` selects another local server. The recording checks zero window-scroll events, a constant viewport, submitted hard exclusions, no extra interpretation during correction and exported disclosures. See [recording evidence](../research/evidence/app-integration/fixed-frame-video.json).

The real live browser request was verified before recording: see `research/evidence/app-integration/live-browser.json`. Its semantic failure is preserved. The independent route validator checks supplied constraints—not whether the model interpreted the original sentence correctly, and not real-world terrain safety.

## Run without credentials

From the repository or unpacked demo bundle, with Python3.11+:

```sh
python3 -m liftlap.server --port 8767
```
The ZIP root also contains launch-demo.sh and launch-demo.bat helpers. They select a Python command but do not install anything or take over an occupied port; pass --port 8768 when needed. Use --version without starting a server.

Open http://127.0.0.1:8767 on the same machine. Choose Load example request, then Recorded AI. Rules works on other supported requests. The bundle does not enable paid inference. Stop with Ctrl-C. Do not expose this local prototype publicly unchanged.

Video playback: open `walkthrough.webm` in a compatible browser/player. Repository visibility controls access to the video. It becomes downloadable with the repository; no separate host is required. It is not a public deployment of the app.

## Current visuals

[Desktop](../research/evidence/app-integration/recorded-corrected-desktop.png), [mobile](../research/evidence/app-integration/mobile.png), [one-page print preview](../research/evidence/app-integration/print-preview.png) and [PDF](../research/evidence/app-integration/corrected-itinerary.pdf) reflect the latest UI. The current video uses the focused fixed-frame flow above. The geographic lab and mobile/print screenshots are separate evidence, not chapters in this video. Older `research/evidence/ui-*` images and the initial live-call screenshot are historical evidence, not current marketing captures.

## Standalone ZIP entry point

The generated ZIP includes `START-HERE.txt` at its root, with Python/Windows launch commands and troubleshooting. The packager extracts the finished archive and verifies its real HTTP UI, worker, CSS, terrain tile and Alpendorf context, plus offline interpretation/planning. No model service is used by this check.

The current walkthrough also selects itinerary visits and uses Next to inspect the following leg. Per-leg times include the scenario’s assumed queue time; they are not current resort estimates.

The reproduction check also downloads the plain-text itinerary and verifies that confirmed hard exclusions and simulation/timing disclosures are retained.
