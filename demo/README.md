# Lift-Lap demonstration

`walkthrough.webm` is a real Chromium screen recording of the app. It is silent; the on-screen labels and the chapter guide below explain the actions. The recording uses an **exact-input replay of one real Qwen3-8B base-model app call**, then Rules mode. It is not continuous live inference or a fine-tuned model demonstration.

## What to look for

1. Load the example and select Recorded AI. No provider calls are needed.
2. Inspect the interpretation: the model incorrectly softened “no drag lifts” into avoidance.
3. Check t-bar, platter and rope-tow under hard exclusions. This correction happens locally, without secretly rerunning the model.
4. Confirm and plan. The simulated route and printable itinerary carry the recorded-AI/user-correction label.
5. All lifts closed produces no route. Editing the recorded request cannot fabricate a new model response. Rules mode demonstrates an unsupported request.
6. Mobile layout and print output are checked separately as well.

The real live browser request was verified before recording: see `research/evidence/app-integration/live-browser.json`. Its semantic failure is preserved. The independent route validator checks supplied constraints—not whether the model interpreted the original sentence correctly, and not real-world terrain safety.

## Run without credentials

From the repository or unpacked demo bundle, with Python3.11+:

```sh
python3 -m liftlap.server --port 8767
```

Open http://127.0.0.1:8767 on the same machine. Choose Load example request, then Recorded AI. Rules works on other supported requests. The bundle does not enable paid inference. Stop with Ctrl-C. Do not expose this local prototype publicly unchanged.

Video playback: open `walkthrough.webm` in a compatible browser/player. Repository visibility controls access to the video. It becomes downloadable with the repository; no separate host is required. It is not a public deployment of the app.

## Current visuals

[Desktop](../research/evidence/app-integration/recorded-corrected-desktop.png), [mobile](../research/evidence/app-integration/mobile.png), [one-page print preview](../research/evidence/app-integration/print-preview.png) and [PDF](../research/evidence/app-integration/corrected-itinerary.pdf) reflect the latest UI. The recording was regenerated after the map-first layout refresh, separated fictional runs, named stations and single-canvas map switching, including map zoom/fit, route arrows and numbers, alongside original-request/selected-settings review and printed approved constraints. It is silent, with on-screen source labels, and ends with the local Alpendorf geographic view and attributed hillshade. Older `research/evidence/ui-*` images and the initial live-call screenshot are historical evidence, not current marketing captures.

## Standalone ZIP entry point

The generated ZIP includes `START-HERE.txt` at its root, with Python/Windows launch commands and troubleshooting. The packager extracts the finished archive and verifies its real HTTP UI, worker, CSS, terrain tile and Alpendorf context, plus offline interpretation/planning. No model service is used by this check.
