---
title: "Lift-Lap Planner: let the model read the request, not invent the mountain"
published: false
tags: devchallenge, hf26challenge
---

*This is a submission draft for the [Hacktoberfest Open-Source AI Challenge Week 1: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05).*

> Private working draft, October 6. Not ready to publish: demo/video access, code access and the Tinker fine-tuning result remain open. This note must not disappear until those gaps are resolved. Links below currently point into a private repository.

## What I Built

“Only blue runs, no drag lifts, and get me back in 45 minutes.”

That sounds like a simple request. It contains several different things: a hard difficulty ceiling, a lift exclusion, a time budget and a return constraint. “Mostly blues” means something different from “only blues.” A route that looks plausible but quietly loses one of those conditions is not a useful answer.

Lift-Lap Planner is a ski-outing planning experiment built around that distinction. The intended experience is short: express the constraints, check the interpretation, and take away a compact itinerary. Less map deliberation is the goal—not a measured screen-time saving yet.

The local prototype can interpret a limited vocabulary, ask the user to confirm constraints, search a bounded graph, and produce a printable simulated itinerary. It includes fictional terrain and an explicitly unreviewed OpenStreetMap terrain lab. It is not live lift information or on-mountain navigation, and it has not been field-tested on skis.

The current browser uses a deterministic rules parser. Open-weight-model interpretation is working separately in the evaluation pipeline; the browser is not yet connected to a trained model.

## Demo

**Pending: a judge-accessible video or deployed demo link.** The current interface runs locally, not at a public URL.

The [recording storyboard](https://github.com/emihiggins/touch-grass-tinker/blob/main/submission/demo-storyboard.md) covers a successful simulated outing, closed lifts and an unsupported request. Existing [desktop](https://github.com/emihiggins/touch-grass-tinker/blob/main/research/evidence/ui-desktop.png) and [mobile](https://github.com/emihiggins/touch-grass-tinker/blob/main/research/evidence/ui-mobile.png) images are development captures, not evidence of a public deployment.

## Code

[Project repository](https://github.com/emihiggins/touch-grass-tinker) — currently private. Reviewer access and the license for original code must be resolved before publication. I am not presenting a private link as accessible source code.

The dependency-free planner and saved-result scoring run on Python 3.11 or newer. The optional Tinker/Cookbook environment has separate version locks and a pinned tokenizer. Model weights are not bundled; training and baseline inference use Tinker's hosted service.

## How I Built It

### Separate language from geometry

The model's job is to turn words into a small, strict intent object. Python owns the graph search and checks the route against the interpreted constraints. Unknown place IDs and invalid intents do not get a best-effort route.

There is a second distinction in evaluation: a route must satisfy the independently authored **gold request**, not merely the model's own interpretation. Otherwise, a model could drop “no drag lifts,” find a route that uses one, and congratulate itself for solving an easier problem.

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
| Fine-tuned model | Not run | No checkpoint or improvement claim |

These are development results, not held-out accuracy. Prompt v2 improved nine cases and regressed two relative to v1. All eight route/no-route outcomes succeeded, but only two of eight clarification cases did. The rules baseline still wins overall. That is an important result: a tuned model needs to earn its complexity, not just beat a deliberately weak prompt.

The [raw outputs and reports](https://github.com/emihiggins/touch-grass-tinker/tree/main/research/evidence/base-v2-development) retain the failures. Forty completed inference requests across both prompts have an estimated uncached token cost of $0.00988101; this is not a verified invoice, excludes uncertain rejected-request billing, and is not a training or cost-reduction result.

All 48 AI-assisted training candidates have now been reviewed by the project owner: 45 explicit label approvals (one remains quarantined for overlap) and three agreed changes awaiting contract implementation. Local rendering verifies that prompts receive no training loss and targets fit without truncation. Independent human-reviewed test data, approved training data, actual fine-tuning and a same-base comparison are still required.

## Why Does Open Innovation Matter?

The useful freedom here is the ability to inspect and adapt the language component while keeping the planner and evaluator fixed. An open-weight base model makes a task-specific fine-tuning experiment possible; the open-source Cookbook exposes the rendering and loss-mask details that can otherwise hide behind a training API. Inspecting those masks caught supervision on prompt framing, which I corrected before any training.

OpenStreetMap also makes the terrain experiment inspectable: another builder can trace a graph edge back to its source. That comes with attribution and ODbL obligations, not blanket permission to relicense the data as application code. Terrain data is credited to © OpenStreetMap contributors.

These are concrete benefits, but not claims that only open models can solve the task. Some closed providers also offer fine-tuning. I have not demonstrated offline model inference, device deployment, a closed-model comparison, or lower cost. The planner runs locally; the measured model calls ran on Tinker.

Nontrivial foundations: [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B), [Tinker SDK](https://github.com/thinking-machines-lab/tinker), [Tinker Cookbook](https://github.com/thinking-machines-lab/tinker-cookbook), and [OpenStreetMap](https://www.openstreetmap.org/copyright). AI coding assistance was used. Model/software license terms and terrain notices remain separate release checks.

## My Agent Session

Optional; not exported for this submission yet. Any shared export must be project-scoped and reviewed for private workspace content. No public session link is claimed.

## Prize Categories

**Intended category: Best Use of Tinker — not yet demonstrated.** The category requires actual fine-tuning and a clear improvement over a baseline. Hosted base-model inference and prompt improvements alone do not satisfy it. Before claiming this category, add the real checkpoint, independently evaluated result and in-app tuned-model trace. If there is no defensible improvement, report that outcome honestly and reassess the category claim.
