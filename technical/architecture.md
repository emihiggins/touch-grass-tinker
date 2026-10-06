# Proposed implementation architecture

> Current intent changes: [version 2 contract](intent-v2.md). The original v1 design below is retained for provenance; implementation status is in [v2 checkpoint](../delivery/v2-checkpoint.md).

Status: production design; a limited [offline reference implementation](../delivery/offline-checkpoint.md) now runs. Data findings live in [research](../research/feasibility.md). Implement the [requirements](../product/requirements.md) and [evaluation protocol](../delivery/evaluation.md).

## Choices

Python backend (FastAPI, Pydantic, NetworkX) plus a small React/TypeScript/Vite frontend with MapLibre. Tinker training/evaluation stays in Python. Use local versioned JSON/JSONL artifacts, not a database, accounts, agent framework or vector store. At implementation start pin compatible stable versions and lock Python with uv and frontend with npm/package-lock. No third-party dependencies have yet been installed. The current reference planner is standard-library-only; this does not claim the production API/UI or NetworkX adapter is implemented.

One CPU server can serve the built frontend and API. Training and live interpretation use remote Tinker SDK clients. Local laptop plus video is the zero-hosting-spend fallback; a public deployment remains a release decision. No offline inference promise. An explicitly selected cached replay mode may work without model access but must be visibly labeled and cannot be presented as a live tuned-model run.

## Boundaries and flow

1. Import pinned source → normalized graph + provenance + review flags.
2. Browser selects sector, start, time and scenario, submits request.
3. Interpret using base/tuned/rules adapter → typed intent or clarification.
4. Show extracted hard constraints and preferences as editable chips; unresolved required fields prevent planning.
5. Pure planner receives validated intent + immutable graph + scenario; independent validator checks result.
6. Render valid itinerary or precise no-route/timeout reason. Invalid model JSON never reaches graph operations.

The model sees request text and a compact allowed-place catalog, not raw HTML, API keys or an enormous terrain dump. It cannot execute tools, construct arbitrary URLs, change graph data or override a closed edge.

## Canonical data contracts

All JSON carries `schema_version: 1`; unknown keys rejected. IDs are local stable IDs mapped to upstream IDs and snapshot hash.

- `GraphSnapshot`: id/hash, source/revision/license, sector, timezone=`Europe/Vienna`, difficulty_convention=`AT`, nodes[], edges[], places[].
- `Node`: id, lon/lat, elevation_m nullable, source_refs[], review_status.
- `Edge`: id, from, to, kind=`lift|piste|verified_transfer`, geometry, difficulty nullable, lift_type nullable, length_m, duration_s (>0), duration_basis=`source|assumed|measured`, source_refs[], review_status. Preserve parallel edges; never flatten different pistes between identical nodes. Null critical fields exclude the edge from constrained planning.
- `Place`: id, label, aliases[], node_id, access_review. MVP meeting points are audited lift stations; restaurants are deferred until their access links are validated.
- `Scenario`: id, simulated=true, date, timezone, edge_states (`open|closed|unknown`), open intervals, queue_s per lift, source/timestamps where real data is ever used. Unknown is not open. Simulation flags accompany every response and printed card.
- `Intent`: status=`ready|clarify|unsupported`; start_place_id; finish_place_id; start_time (ISO with offset); duration_minutes (15..240); hard_max_difficulty (`blue|red|black`); excluded_lift_types[]; preferred_difficulties[]; prefer_variety boolean; clarification_fields[]; unsupported_preferences[]. Required fields can be supplied by explicit UI selections. No implicit mapping of “intermediate” to a particular regional color. No model self-confidence threshold.
- `Itinerary`: edge_ids[], per-edge arrival/departure/wait seconds, total_seconds, finish_place_id, assumptions[], graph_hash, scenario_id, validation_passed. Any claimed preference match must be computed from the itinerary.

Semantics: “only blues” sets a hard maximum blue; “mostly blues” sets a soft preference and still requires a hard maximum from user/UI. “No drag lifts” excludes t-bar, platter and rope-tow; magic carpets remain a separately named option. “No surface lifts” additionally excludes carpets. Negated exclusions and corrections are explicit training cases. Conflicts ask clarification rather than silently picking the permissive interpretation. Meeting deadlines intersect with the duration bound; all clock handling is deterministic in the resort timezone.

## Proposed HTTP interface

- `GET /api/sector`: audited display graph, place catalog, provenance and available scenarios; no secrets.
- `POST /api/interpret`: `{request_text, ui_context, adapter}` → `{intent, model_version, elapsed_ms, request_id}`. 2,000-character request limit; reject external content/oversized bodies. Default tuned adapter only after its smoke gate passes.
- `POST /api/plan`: `{intent, scenario_id, graph_hash}` → discriminated result `ok|clarify|no_route|search_limit|unavailable`. Server selects graph/scenario from allowlist; no arbitrary client graph execution.
- `GET /api/health`: readiness only, never credentials.

HTTP 422 for invalid schema, 429 for rate limit, 503 for unavailable model. Domain-level no-route is a typed 200 response. API budget: one generation per explicit request, at most one bounded transient retry. No model auto-repair loops. Server deadline 30 seconds for interpretation; deterministic planner deadline 2 seconds. Client cancel aborts its request; record if remote work may already have incurred usage. Idempotency keys prevent duplicate in-flight submissions per session.

## Planner design

A ski outing is not simply shortest path from base to base (the empty route wins). Use a bounded loop/itinerary search with positive travel time and independent constraints.

- Filter unreviewed/closed/unknown/excluded edges. Check source node and finish node belong to the sector. A result requires at least one lift and one piste.
- NetworkX MultiDiGraph stores parallel edges. Precompute optimistic return-to-finish time lower bounds using reverse Dijkstra with nonnegative base durations (ignoring queues/closures for the lower bound only).
- Search state: node, elapsed seconds, edge visit counts, distinct piste set, path and scenario clock. Expand outgoing edges while checking actual scenario boarding/open-window and completion time. Queue delays are nonnegative; require traversal to finish within permitted interval. Waiting for a future opening is deferred in MVP.
- Cap routes at 40 edges, at most two uses per edge, 20,000 expanded states and 2 seconds. Use deterministic beam width 200 for large searches. Lexicographic objective among valid completed routes: preferred unique piste distance, total unique piste distance, then shorter total time. Reward repeat pistes zero additional uniqueness. Do not claim global optimality.
- A search cap produces `search_limit`, not proof of impossibility. Only return `no_route` for exhaustive bounded search or a proven reachability/time obstruction. Explain which bounds apply.
- Run a separate validator on every candidate: contiguous directed edge IDs, scenario windows/queues, max difficulty, lift exclusions, start/finish, time and nonempty ski outing. Recompute everything, distrust returned aggregates. If validation fails, discard result and log a planner defect.
- Compare bounded exhaustive search on tiny synthetic graphs against the heuristic for valid-result parity and objective quality. A missed heuristic route must not be reported as mathematically impossible.

## UI, privacy and operation

Routes: `/` planner, `/compare` recorded benchmark/demo comparison, `/about` sources and limitations. No auth personas: anonymous demo visitor only; configuration and training artifacts are not public API routes. Mobile card-first view at 360px, desktop map/list split at 1280px. Keyboard-visible focus, accessible labels, textual route equivalent, non-color difficulty labels and reduced-motion map transitions. States: initial example, loading/cancel, clarification, no-route, search-limit, model-unavailable and valid plan.

Do not request GPS, store precise user locations, persist raw user prompts by default or send them to analytics. The remote model receives only submitted text/context; disclose this in the UI. Request logs contain IDs, adapter/checkpoint, duration, token counts, result codes and graph/scenario hashes. Training datasets contain original/consented examples, not visitor logs. Keep API keys server-side; validate IDs, escape labels and avoid raw HTML. Public deployment adds same-origin checks, per-client limits and a global usage cap; no open unauthenticated proxy to unlimited training or sampling.

Build static assets, load the graph at startup, fail readiness if hashes/contracts fail, and retain a previous pinned graph/checkpoint config for rollback. Serve over HTTPS if deployed. Demo replay mode is a distinct visible mode, never a silent fallback. Errors do not expose provider responses or secrets.

## Current local demo deviation (2026-10-06)

The [local demo checkpoint](../delivery/local-demo.md) implements a plain HTML/CSS/JS + loopback Python HTTP server, not production FastAPI/React/MapLibre. It uses a rules adapter and a labeled SVG schematic with no external tiles/assets. Native-node compaction merges only nonbranching piste chains with identical constraints/scenario state; expansion must pass the original graph validator, including the original 40-source-edge limit. Node contraction is not a relaxation of terrain review or search bounds.

The two-step UI reviews extracted constraints before requesting a plan. Controls can be changed and reinterpreted; direct per-chip editing is not implemented. Start time is fixed and unsupported clauses block planning. Rules-v1 grammar is deliberately explicit and residual text is reported; development results are not held-out scores. See implementation checkpoint for exact HTTP routes, security boundary and incomplete requirements.
