---
title: "Lift-Lap Planner: let the model read the request, not invent the mountain"
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 1: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05)*

<!-- Emi: publish after making the repository public and checking the linked video/code while signed out. See dev-posting-checklist.md; this note is not part of the public article. -->

## What I Built
<!-- What does it do, and how does it get people off the screen and into the world?  Who is it for? -->

“Only blue runs, no drag lifts, and get me back in 45 minutes.”

That sounds like a simple request. It contains several different things: a hard difficulty ceiling, a lift exclusion, a time budget and a return constraint. “Mostly blues” means something different from “only blues.” A route that looks plausible but quietly loses one of those conditions is not a useful answer.

Lift-Lap Planner is a ski-outing planning experiment built around that distinction. The intended experience is short: express the constraints, check the interpretation, and take away a compact itinerary. Less map deliberation is the goal—not a measured screen-time saving yet.

The local prototype can interpret a limited vocabulary, ask the user to confirm constraints, search a bounded graph, and produce a printable or downloadable simulated itinerary. It includes fictional terrain and an explicitly unreviewed OpenStreetMap terrain lab. It is not live lift information or on-mountain navigation, and it has not been field-tested on skis.

The browser offers Rules, a clearly labelled recorded AI example, and opt-in live Qwen3-8B base-model interpretation. Live inference stays server-side; schema-invalid responses cannot create routes. The user sees the original request and selected settings, reviews the interpretation, and can correct the time budget, maximum difficulty and hard lift exclusions locally before confirming. Draft corrections invalidate the previous outing; unsupported interpretations still cannot be used to plan. The printed itinerary retains the approved constraints and interpretation source. The rejected fine-tuned checkpoint is not used.

The map-first interface separates and names fictional lift and piste lines, supports panning and known station labels, and links each itinerary visit to its map segments. Previous/Next controls distinguish repeated laps; Focus step frames the selected leg. Per-leg estimates include the scenario’s assumed queues, and the local text export keeps approved constraints and simulation warnings with the itinerary. An optional MapLibre view uses local Alpendorf geometry and a bundled, attributed hillshade tile, so it works without a tile-service account. The SVG sketch remains available when WebGL fails and for printing. Elevation provides visual context only; it does not establish safe slopes or change the route calculations.

## Demo
<!-- Share a deployed link or a video demo. -->

[Watch/download the demo](https://github.com/emihiggins/touch-grass-tinker/raw/refs/heads/main/demo/walkthrough.webm). The app itself runs locally; this is a recorded demonstration, not a hosted planning service. It shows an exact replay of a real Qwen3-8B app response, its incorrect softening of “no drag lifts,” a local hard-exclusion correction, confirmation and simulated planning. The recording is labelled replay—not continuous live inference. The live browser call was verified separately. [Reproduction and disclosures](https://github.com/emihiggins/touch-grass-tinker/blob/main/demo/README.md).

The recording covers corrected simulated planning, step inspection, local text export, closed lifts, an unsupported request, mobile layout and the offline Alpendorf geographic view. [Browser and print evidence](https://github.com/emihiggins/touch-grass-tinker/tree/main/research/evidence/app-integration) accompanies the reproducible local demo; it is not evidence of a public deployment.

## Code
<!-- Show us the code!  You can embed a GitHub repo directly into your post. -->

[Project repository](https://github.com/emihiggins/touch-grass-tinker). Original code is MIT-licensed; OpenStreetMap terrain data remains under ODbL with attribution. Run the offline demo with Python 3.11+ using the README instructions.

The dependency-free planner and saved-result scoring run on Python 3.11 or newer. The optional Tinker/Cookbook environment has separate version locks and a pinned tokenizer. Model weights are not bundled; training and baseline inference use Tinker's hosted service.

## How I Built It
<!-- Which open-source AI did you use (open-weight models, agent harnesses, frameworks, local inference), and how is your project built around it? -->

### Separate language from geometry

The model's job is to turn words into a small, strict intent object. Python owns the graph search and checks the route against the interpreted constraints. Unknown place IDs and invalid intents do not get a best-effort route.

There is a second distinction in evaluation: a route must satisfy the human-reviewed **reference request (gold label)**, not merely the model's own interpretation. Otherwise, a model could drop “no drag lifts,” find a route that uses one, and congratulate itself for solving an easier problem.

The planner distinguishes an exhausted bounded search from a search limit. Returned routes pass a separate validator checking connectivity, edge direction, difficulty, closures and time. This establishes consistency with the supplied graph and scenario—not that a real piste is safe or open.

### Refuse to invent connections

The first processed terrain graph looked promising until an audit found 62–107 metre geometry gaps. I retained the failed audit and moved to native OpenStreetMap node connections instead of snapping nearby endpoints together. Native source connectivity is a better starting point, but direction, boarding access and real-world terrain still need review. The lab displays those limits rather than treating a connected line as permission to ski it.

### Measure before fine-tuning

I used Qwen/Qwen3-8B through Tinker, with the pinned Cookbook's `qwen3_disable_thinking` renderer. The visible development comparison currently looks like this:

| Interpreter | Strict request successes | Meaning |
|---|---:|---|
| Rules-v1 | 14/20 | Limited deterministic grammar |
| Base model, prompt v1 | 6/20 | First live development smoke |
| Same base model, prompt v2 | 13/20 | Prompt development on visible cases |
| Fine-tuned model | Not evaluated on this v1 set | See separate v2 pilot trial below |

These are development results, not held-out accuracy. Prompt v2 improved nine cases and regressed two relative to v1. All eight route/no-route outcomes succeeded, but only two of eight clarification cases did. The rules baseline still wins overall. That is an important result: a tuned model needs to earn its complexity, not just beat a deliberately weak prompt.

The [raw outputs and reports](https://github.com/emihiggins/touch-grass-tinker/tree/main/research/evidence/base-v2-development) retain the failures. Forty completed inference requests across both prompts have an estimated uncached token cost of $0.00988101; this is not a verified invoice, excludes uncertain rejected-request billing, and is not a training or cost-reduction result.

All 48 AI-assisted training candidates were reviewed by the project owner. The agreed corrections are implemented in a separate v2 corpus of 47 source-reviewed, deterministically migrated rows; the overlapping case is excluded. All 16 pilot cases were reviewed and frozen before predictions. They were not an untouched final benchmark. Local rendering verifies that prompts receive no training loss and targets fit without truncation. Emi subsequently approved all 16 fresh cases, and their labels and graph bundle were frozen before evaluating the retained base candidate.

### What the full-data trial showed

After the integration smoke, I preregistered one full-data trial: 47 human-reviewed examples, rank 16 LoRA, learning rate 0.0001 and three full-batch training passes. On the same 16-case reviewed pilot, the base model passed 9 tasks and the trained model passed 7. Training improved two cases and regressed on four. Schema validity was 15/16 for the base and 10/16 for the trained model. Valid JSON alone was not enough, and the trained model also regressed on schema compliance.

The trial failed its screening rule. I retained the base as the candidate rather than presenting the tuned checkpoint as an improvement. These pilot cases were not untouched final evidence; the separate fresh 16-case set was human-approved and frozen before its evaluation. See the [complete paired evidence](https://github.com/emihiggins/touch-grass-tinker/tree/main/research/evidence/experiment-01).

### Fresh evaluation of the retained base model

After independent owner approval, I froze a new 16-case set on four fictional graph layouts and evaluated the unchanged base model once. It passed **13/16 end-to-end tasks**, with **16/16 schema-valid outputs**. Failures involved incomplete surface-lift exclusions, unnecessary duration clarification, and a retained duration where none should be set. All failures remain in the denominator. [Outputs, protocol and report](https://github.com/emihiggins/touch-grass-tinker/tree/main/research/evidence/fresh-base-evaluation) are preserved.

This is a small, same-agent-authored, human-reviewed set—not representative field validation. It is not a base-versus-trained comparison, and 13/16 here must not be compared with 9/16 on different pilot cases as a gain. No model or prompt was tuned using these final outputs. A later, explicitly post-hoc check of the unchanged narrow rules parser scored 0/16 on this compositional wording; that comparison was not used to select a new model and does not describe performance on the parser’s supported grammar.

## Why Does Open Innovation Matter?
<!-- Why does open innovation matter for what you built?  What did it make possible that a closed API wouldn't? -->

The useful freedom here is the ability to inspect and adapt the language component while keeping the planner and evaluator fixed. An open-weight base model makes a task-specific fine-tuning experiment possible; the open-source Cookbook exposes the rendering and loss-mask details that can otherwise hide behind a training API. Inspecting those masks caught supervision on prompt framing, which I corrected before any training.

OpenStreetMap also makes the terrain experiment inspectable: another builder can trace a graph edge back to its source. That comes with attribution and ODbL obligations, not blanket permission to relicense the data as application code. Terrain data is credited to © OpenStreetMap contributors.

These are concrete benefits, but not claims that only open models can solve the task. Some closed providers also offer fine-tuning. I have not demonstrated offline model inference, device deployment, a closed-model comparison, or lower cost. The planner runs locally; the measured model calls ran on Tinker.

Nontrivial foundations: [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B), [Tinker SDK](https://github.com/thinking-machines-lab/tinker), [Tinker Cookbook](https://github.com/thinking-machines-lab/tinker-cookbook), [OpenStreetMap](https://www.openstreetmap.org/copyright), [MapLibre GL JS](https://maplibre.org/), and [Mapzen Terrain Tiles](https://registry.opendata.aws/terrain-tiles/). AI coding assistance was used. Licenses and attribution are documented in [THIRD_PARTY_NOTICES.md](https://github.com/emihiggins/touch-grass-tinker/blob/main/THIRD_PARTY_NOTICES.md). No model weights are bundled.

## My Agent Session
<!-- Optional, but judges love it.  Save your session with DevRelay and embed it with the agent_session tag (see the challenge page), or link to it. -->

I used an AI coding agent to build and test the project. I am not sharing a session transcript; the repository instead contains the experiment plans, failures, raw model outputs and reproducible evaluation evidence.

## Prize Categories
<!-- Which partner categories are you entering?  List every one that applies, or remove this section. -->

No partner category is currently claimed. The Tinker trial did not demonstrate a fine-tuning improvement, so I am not entering Best Use of Tinker on the strength of hosted inference or prompt changes. This submission is for the overall Touch Grass challenge.

<!-- Team Submissions: Please pick one member to publish the submission and credit teammates by listing their DEV usernames directly in the body of the post. -->

<!-- Thanks for participating! -->
