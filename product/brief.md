# Lift-Lap Planner: selected direction

Emi selected this concept on October 5, 2026. Resort, stack and training method remain open.

## User outcome

A resort skier states their ability, preferred terrain, excluded lift types, available time and meeting point. The app produces a connected sequence of lift rides and pistes, reducing time spent studying a map.

Example: “Two hours, mostly blues, no drag lifts, and meet my friend at the base café at noon.”

## Proposed technical boundary

- A Tinker-fine-tuned model translates requests into structured constraints and identifies ambiguity.
- A deterministic graph planner validates connectivity, directions, difficulty, exclusions and scenario availability. The model cannot invent terrain or override graph checks.
- A map and compact itinerary explain the plan, assumptions and estimated times.
- Start with one audited sector; no live tracking or turn-by-turn navigation.
- Opening states, queues and duration estimates must be labeled according to source. Simulated conditions are not current resort information. No guarantees of arrival time.

## Tinker hypothesis

Fine-tuning improves correct constraint interpretation and end-to-end fulfillment relative to a competently prompted identical base model. Compare also with a simple parser. An itinerary is judged against independent ground-truth user constraints, not just the model's own interpretation. Split evaluation by request family and graph layout. Synthetic graphs can support training; evaluate transfer to the audited real graph. No improvement is claimed yet.

The language component, dataset and experiments must constitute substantial original work; reuse and credit existing terrain data and graph-processing work. A graph solver alone is not a meaningful Tinker integration.

See [data-source research](../research/data-sources.md) for the proposed resort and unresolved access/quality gates, and [delivery plan](../delivery/plan.md) for evidence gates.
