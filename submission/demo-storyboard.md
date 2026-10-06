> Superseded by the recorded walkthrough in [demo/README.md](../demo/README.md). The original storyboard below is retained as planning history; its unimplemented/no-training statements are not current status.

# Two-minute demo recording plan

Status: executable storyboard, not a recorded video. Use the current rules/simulation build; do not narrate it as tuned inference. No public host is required if a judge-accessible video is supplied.

## Setup

```bash
python3 -m liftlap.server --port 8767
```

Open `http://127.0.0.1:8767` on the same machine. Hide unrelated tabs, notifications and terminal environment. Use fictional Pine Mountain first. Existing smoke coverage follows these same core paths in `scripts/browser-smoke.cjs`.

| Time | Action | Narration / visible proof |
|---|---|---|
| 0:00–0:15 | Show full screen, including simulation notice | “A prototype for turning a short request into a checkable ski outing. This demo uses rules, fictional terrain and assumed conditions.” |
| 0:15–0:40 | Type `Only blues, no drag lifts, 45 minutes`; select Review my constraints | Show difficulty, excluded lift types and time. Explain why confirmation comes before search. |
| 0:40–1:00 | Confirm & plan outing | Show route, time and itinerary. The independent validator checks the supplied graph and scenario, not real-world access. |
| 1:00–1:20 | Set All lifts closed; review and confirm again | Show the no-outing result, not a fabricated detour. |
| 1:20–1:35 | Type `Fly me to Mars`; review | Show that the plan button is disabled until interpretation is resolved. |
| 1:35–1:50 | Show saved development results beside the app | Rules 14/20, base v1 6/20, base v2 13/20. State that these are visible development cases; no fine-tuning result yet. |
| 1:50–2:00 | Return to a valid fictional outing; open print view | Close on the pocket-itinerary idea. No measured screen-time claim. |

Optional appendix: show Alpendorf with its unreviewed-terrain notice and OSM attribution. Do not imply the schematic is a navigational basemap. Rehearse manually before recording; do not claim current print legibility or keyboard-only completion based solely on the prior browser smoke.

## Final trained-model segment (not recordable yet)

Once implemented, replace the rules-only narration with an actual checkpoint-linked request; show mode, parsed constraints and independent route validation. Add frozen-test results, including regressions. Keep saved replay visibly distinct from live inference. Do not edit failures out of an evaluation narrative.

## Release check

- Record an actual video, inspect its audio/text, and check playback without account-specific access.
- Add its real URL to the DEV draft; a local screenshot or this storyboard is not a video.
- Preserve simulation/provenance labels in the frame.
- Get publication authority before uploading or exposing the repository/demo.
