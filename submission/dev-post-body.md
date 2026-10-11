*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 1: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05)*

## What I Built

“Only blue runs, no drag lifts, and get me back in 45 minutes.”

I wanted that sentence to become a short outing—not another evening spent comparing lines on a map. But the most useful moment in building Lift-Lap was watching the model get it wrong: it treated **“no drag lifts” as a preference**, not a prohibition.

A plausible route was not enough. The interpretation had to be visible and correctable first.

**Lift-Lap Planner is a local ski-outing planning prototype:** express a request, inspect its constraints, correct anything the model missed, then generate a compact simulated itinerary. The intended user is a skier who wants less map deliberation and a clear plan to take away. The current prototype is for trying that interaction—not for navigating a real mountain.

The language component uses the open-weight **Qwen3-8B** model through Tinker. A separate Python planner owns connectivity, difficulty, lift restrictions, closures and time. It cannot invent a connecting piste to make a request work.

![Lift-Lap: visible constraints, a fictional mountain map and a confirmed simulated itinerary](https://raw.githubusercontent.com/emihiggins/touch-grass-tinker/main/research/evidence/app-integration/recorded-corrected-desktop.png)

The screen is meant to be the short part: review, confirm, print or download the itinerary, and put the device away. That is a design goal, not a measured screen-time saving. **I have not field-tested it on skis.** Terrain and timings are fictional or explicitly unreviewed; this is not live lift information, avalanche advice or on-mountain navigation.

## Demo

**[Watch/download the recorded walkthrough](https://github.com/emihiggins/touch-grass-tinker/raw/refs/heads/main/demo/walkthrough.webm)** · [Reproduce the demo](https://github.com/emihiggins/touch-grass-tinker/blob/main/demo/README.md)

The silent recording uses an exact replay of a real Qwen3-8B app response. It deliberately preserves the “no drag lifts” mistake. I correct the hard exclusions locally, confirm the constraints, and inspect the simulated route. The interface labels the response as **recorded AI**, not fresh inference.

The walkthrough keeps the request, review, map and itinerary in one fixed desktop frame, with captions and pauses instead of scrolling. A recording-only presentation layout puts the real app panels side by side without changing behavior. It shows itinerary-step inspection and local text export; mobile, closure and geographic-lab checks are separate evidence. There is no hosted public inference service. Anyone can run the default app without credentials using Rules mode or that exact-input recorded example; arbitrary live AI requests require the separately configured research environment.

## Code

**[GitHub repository](https://github.com/emihiggins/touch-grass-tinker)**

With Python 3.11 or newer:

```bash
git clone https://github.com/emihiggins/touch-grass-tinker.git
cd touch-grass-tinker
python3 -m liftlap.server --port 8767
```

Open `http://127.0.0.1:8767` on the same computer. No package installation, model download, API key or paid call is required for the default demo.

Original code is MIT-licensed. OpenStreetMap data and bundled upstream components retain their separate licenses and attribution. Model weights are not bundled. [User guide](https://github.com/emihiggins/touch-grass-tinker/blob/main/docs/user-guide.md) · [Developer guide](https://github.com/emihiggins/touch-grass-tinker/blob/main/docs/development.md) · [Notices](https://github.com/emihiggins/touch-grass-tinker/blob/main/THIRD_PARTY_NOTICES.md).

## How I Built It

### Put the model before the planner, not in charge of it

The model produces a strict intent object. “Only blues” sets a hard ceiling; “mostly blues” expresses a preference. Lift prohibitions and soft avoidance are separate fields. Unsupported live-condition requests should stop for review, not become invented data.

The user sees the original request and selected settings beside the interpretation. Time, maximum difficulty and hard lift exclusions can be corrected without another model call. Editing constraints invalidates the previous outing. A route is created only after confirmation, and printed/exported itineraries retain the approved constraints and interpretation source.

An independent validator checks returned routes against the supplied graph and constraints. That is not the same as proving the model understood the sentence. For evaluation, I also check routes against the human-reviewed reference interpretation. Otherwise a model could drop an exclusion, solve an easier problem, and appear successful.

### Refuse to invent the mountain

An early terrain audit found 62–107 metre geometry gaps. I retained the failed evidence and switched to native OpenStreetMap node connections rather than snapping nearby endpoints together.

The app now has fictional Pine Mountain and an explicitly unreviewed Alpendorf geometry lab. A bundled MapLibre view and attributed hillshade work without a tile-service account; the SVG sketch remains available for printing and renderer failure. Geometry is visual and structural evidence—not proof of permitted boarding, current operations or safe skiing. Additional resort snapshots stay in research review, not the selectable routing menu.

### Let the experiments say “no”

I used Tinker's SDK and the open-source Cookbook's pinned `qwen3_disable_thinking` renderer. Inspecting assistant-only loss masks and target lengths was part of the training preflight. The project owner reviewed the source labels; 47 migrated training examples were retained, excluding an overlapping case.

Two real training configurations completed:

| Experiment | Paired base → trained task successes | Decision |
|---|---:|---|
| First pilot: three full-batch updates, learning rate 1e-4 | 9/16 → 7/16 | Reject tuned candidate |
| Exploratory follow-up: three epochs, batches 16/16/15, learning rate 3e-5 | 10/16 → 10/16 | Retain base |

The follow-up used all 47 examples once per epoch, with nine optimizer updates and no dropped final batch. It gained one case and lost another. Both trials used the already-exposed historical pilot, not an untouched final test. The second recipe changed both batching and learning rate, so it cannot isolate either factor's effect.

Separately, the retained base previously passed **13/16 tasks** on a fresh, human-reviewed, frozen set, with **16/16 schema-valid outputs**. Those are different cases: 13/16 is not a gain over the pilot's 9/16 or 10/16. The fresh set was same-agent-authored and small, not representative field validation; its labels and outputs were not used as training examples for the follow-up.

The follow-up's two malformed outputs each ended with an extra quote. Looking at the complete object underneath still revealed wrong interpretations. Simply stripping punctuation would not have fixed those answers. The persistent problems were semantic: omitted exclusions, ignored destinations and unnecessary clarification.

**No fine-tuning improvement is claimed.** The base remains selected. [Evaluation overview](https://github.com/emihiggins/touch-grass-tinker/blob/main/docs/evaluation.md), [paired follow-up evidence](https://github.com/emihiggins/touch-grass-tinker/tree/main/research/evidence/experiment-02), and [case-level postmortem](https://github.com/emihiggins/touch-grass-tinker/blob/main/research/evidence/experiment-02/postmortem.md) retain the failures and denominators.

## Why Does Open Innovation Matter?

The useful freedom was being able to inspect and change the language component without replacing the planner or evaluator. Qwen3-8B made a task-specific open-weight fine-tuning experiment possible. The Cookbook exposed how messages become tokens and loss masks, so I could audit exactly what received supervision instead of treating training as a black box.

OpenStreetMap provides another kind of inspectability: a graph segment can be traced back to its source. That comes with attribution and ODbL obligations, not permission to relabel the data as application code.

The result is a project another builder can examine, reproduce and challenge—including the decision **not** to use its trained models. That matters more to me than a demo that only shows the successful prompts.

I have not demonstrated that this outperforms a closed model, reduces model costs or runs AI inference offline. The planner runs locally; measured model calls ran on Tinker. Open components made the experiments inspectable, not automatically better.

Foundations: [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B), [Tinker SDK](https://github.com/thinking-machines-lab/tinker), [Tinker Cookbook](https://github.com/thinking-machines-lab/tinker-cookbook), [OpenStreetMap](https://www.openstreetmap.org/copyright), [MapLibre GL JS](https://maplibre.org/) and [Mapzen Terrain Tiles](https://registry.opendata.aws/terrain-tiles/). Terrain attribution: © OpenStreetMap contributors. AI coding assistance was used; [third-party notices](https://github.com/emihiggins/touch-grass-tinker/blob/main/THIRD_PARTY_NOTICES.md) document licenses and attribution.

## My Agent Session

I used an AI coding agent to build and test the project. I am not sharing a session transcript. The repository instead contains preregistered experiment plans, raw model outputs, failed audits, tests and reproducible evaluation evidence.

## Prize Categories

**Best Use of Tinker — submitted for consideration**, alongside the overall Touch Grass challenge.

I used Tinker to fine-tune Qwen3-8B for structured ski-outing intent extraction, with reviewed training examples, audited loss masks, checkpoint/restore handling and paired baseline evaluation. The experiments are reproducible, including their negative results: task success changed from **9/16 to 7/16** in the first trial and **10/16 to 10/16** in the follow-up. Neither trial established an aggregate task-success improvement, and I have not established a latency or cost improvement; the base remains selected.

The category description asks for a clear improvement over a baseline. I am submitting the implementation and evidence for the judges’ consideration, not claiming that these results demonstrate that improvement. No other partner category is claimed.
