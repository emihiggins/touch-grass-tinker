# User guide

## Start and stop

From the repository root, run `python3 -m liftlap.server --port 8767` with Python3.11+. Open http://127.0.0.1:8767 on the same computer. Ctrl-C stops it. If the port is occupied, choose another port with `--port`. This is not a hosted service or a phone-accessible URL from another computer.

## Choose an interpretation mode

| Mode | What it does | Network/model requirement |
|---|---|---|
| Rules | Recognizes a deliberately narrow set of phrases and otherwise stops for review | None |
| Recorded AI example | Replays the saved response for exactly the example request and selected time/difficulty/terrain | None |
| Live AI | Sends text, selected context and the place catalog to Qwen3-8B via Tinker | Advanced protected research setup; disabled by default |

Use **Load example request** to restore the recorded example’s settings, then select Recorded AI. The example intentionally includes a model error: “no drag lifts” was interpreted as soft avoidance. Correct the hard exclusions before confirming. This is a demonstration of review, not evidence that models always obey restrictions.

Rules examples: “only blues”, “no drag lifts”, “mostly blues”, “45 minutes”. An empty request uses selected form values. Rules does not understand arbitrary prose. Recorded mode refuses changed requests rather than inventing a new answer.

## Review before planning

The review shows your original request, selected settings and interpreted constraints. Check the maximum difficulty, duration, start/finish, excluded lifts, soft preferences and variety flag. A maximum grade is not necessarily a preferred grade. “Avoid gondolas” is a preference; “no gondolas” is a hard exclusion.

Hard-exclusion checkboxes edit the intent locally without another inference call. Checking a type also removes an overlapping soft avoidance preference. Other interpretation problems require editing the request/form and reviewing again. Clarification or unsupported intent keeps planning disabled.

**Confirm & plan outing** starts the search. Changing inputs or correcting exclusions invalidates old results; late responses from the old request are ignored.

## Understand the result

- **Itinerary:** route validation passed against the confirmed intent and supplied graph/scenario. That does not establish that the original sentence was interpreted correctly or that real terrain is safe.
- **No outing:** no feasible route was found within the implemented bounds/scenario.
- **Search limit:** the search exhausted a resource limit; it does not prove that no route exists.
- **Preference notice:** an outing uses a softly avoided lift. Hard exclusions are not relaxed.

An outing may be shorter than the budget; the search does not promise to fill all available time. The fixed demo starts January15,2027 at10:00 local. All-lifts-closed is a synthetic scenario. The map is a schematic, not a navigational basemap.

## Print and mobile

The print button creates a simulation itinerary with approved constraints, model/rules provenance, corrections, route steps and disclosures. The recorded example has a verified one-page A4 PDF. Other routes/printer settings may paginate differently. The layout was checked at320px and360px widths; targeted keyboard checks are not a full accessibility certification.

## Privacy and troubleshooting

Rules/recorded mode performs no provider calls. Opt-in live mode sends input to Tinker and retains private local run records; do not enter sensitive personal data. No analytics or external map tiles are loaded.

If recorded mode reports a mismatch, load the example again or choose Rules. If live mode is disabled, that is expected in the default installation. If live provider results become uncertain, the adapter pauses rather than retrying paid work. If a route is unavailable, inspect your confirmed constraints and simulated operations; never treat the prototype as on-mountain guidance.

## Reading the mountain sketch

Use +/− and Fit map to inspect the sketch. Drag to pan, or focus the sketch and use arrow keys; Fit map restores the whole area. Select an itinerary step to highlight its source segments in purple. Clicking an SVG route segment cycles through its repeated itinerary visits. Orange arrows show route direction, numbered circles mark each edge’s first itinerary visit, and Start/Finish mark endpoints. Repeated traversals remain listed in the itinerary. Alpendorf uses an aspect-preserving local geographic projection with an approximate scale at fit view; Pine Mountain remains fictional. Printing fits the full map automatically. The SVG has no basemap or hillshade. The optional geographic view adds bounded local elevation shading, never live status.

For Alpendorf, **Open geographic map** enables a locally bundled MapLibre view with touch pan/zoom and clickable lines. It uses the same unreviewed OSM extract, not a new routing dataset. One bundled elevation tile provides hillshade around Alpendorf; panning beyond its bounds has no shading. It is orientation context, not precise slope or snow information. No external tile server is contacted. If WebGL fails, the sketch remains available. Printing always uses the sketch. Known catalog stations are labeled in both views; additional station names are not guessed. Only one map is shown at a time; use **Switch to sketch** to return. On phones, the map appears before the form; **Set your day** jumps to the controls. Fictional mountain outlines and separated run paths are illustrative, not elevation or route geometry.

## Inspecting an outing

Choose a numbered itinerary step, then use **Previous**, **Next** or **Focus step** above the map. Repeated passes remain separate visits; clicking a shared route segment cycles through them in either map. Each leg shows estimated minutes. The inspector shows elapsed time into the outing and its assumed queue allowance—not a live queue or arrival prediction. Changing settings clears the old selection and requires confirmation again.

Use **Save itinerary (.txt)** to download the confirmed constraints and all steps, estimates and source disclosures. The file is created locally; it does not call a model or publish your plan. Keep its simulation warning with it when sharing.

If terrain loading fails, the previous map is cleared and planning remains disabled. Use **Retry terrain loading** to try again. Changing terrain while an interpretation is pending does not submit a second model request; the old result is discarded.

The recorded example is available on Pine Mountain only. Switching to a terrain where the selected mode is unavailable returns the form to offline rules and explains the change. It never silently switches to paid live AI.

## Correcting time and difficulty

For a ready interpretation, **Correct time or difficulty** lets you edit the time budget (whole minutes, 1–1440) and maximum grade without another model call. Applying a change updates the displayed constraints and records which fields the user changed. Then confirm again to plan. Draft edits immediately hide the old route and cannot be confirmed until valid and applied. Original request/settings remain visible for comparison. Unsupported or unresolved interpretations still require editing the request; this form does not bypass those checks.

**Discard time/difficulty edits** restores the currently applied values without undoing separate lift corrections. It does not revive the old route; confirm the current constraints again.
