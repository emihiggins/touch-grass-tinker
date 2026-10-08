# Robustness implementation plan

Status: **in progress; R03 implemented offline**. Work IDs, sequencing and budget: [roadmap](../delivery/model-robustness-roadmap.md). This plan extends existing validation, recovery and transport behavior rather than asserting those systems are absent. Preserve [intent v2](intent-v2.md) and historical evaluation semantics; version any changed contract/scorer.

## R01 Semantic contract

Start in `liftlap/app_model.py`, `core.py`, `server.py` and the existing intent validator; inspect current call sites before choosing the shared module. Introduce a pure semantic check returning structured issue codes and field paths, independent of UI wording. Model output is untrusted input.

Cases: clarification of an unknown budget must not silently retain a UI duration; explicit eight minutes is a valid extracted duration even when no route fits; surface-lift exclusion must cover the contract-defined subtypes; explicit user corrections take precedence over UI defaults. Do not infer these through brittle keyword matching alone. Prefer a versioned extraction contract carrying field provenance (`user`, `context`, `missing`) and explicit override/unknown markers, validated against allowed fields. Conflicts that cannot be deterministically established require a clear user correction/clarification, not invented values. Audit compatibility before adding fields; legacy v2 artifacts remain readable.

Separate three phases: structural parsing; semantic consistency; route feasibility. A valid short budget can yield no route, not a parser error. Unknown maximum grade remains unknown, not the hardest resort grade. Never infer lift comfort from grade. Semantic failure prevents planning and presents editable fields while retaining the original request. Hard exclusions cannot be weakened by recovery buttons without an explicit user edit.

- [ ] Regression fixtures cover historical failure classes with synthetic variants, explicit overrides and ambiguous language.
- [ ] Ready/clarify state, required values and provenance cannot contradict each other without a typed issue.
- [ ] Valid-but-infeasible intent reaches feasibility handling; invalid intent never reaches route generation.
- [ ] UI/export agree on corrected constraints; editing invalidates stale routes before replanning.
- [ ] Contract migration is opt-in/versioned; old frozen outputs retain old scores.

## R02 Planner boundary and adversarial tests

Keep model responsibility limited to intent extraction. Graph IDs, connectivity, directions, closures, time feasibility and hard constraints are checked by deterministic code and the independent route validator. Do not feed untrusted model-generated edges into the graph. Compact display steps must retain exact original edge IDs for validation.

Build a table-driven property/metamorphic suite using the existing unittest runner first; add a property-testing dependency only if reproducible generators and shrinking justify it. Generate small bounded graphs with replayable seeds. Properties: accepted routes use known directed edges and respect hard maxima/exclusions; removing an edge cannot create a new feasible route; reducing the budget cannot make an otherwise identical fixed route feasible; renaming IDs bijectively preserves feasibility; compaction preserves original path validation. Do not assert heuristic route optimality or that increasing a budget always preserves the exact selected route.

Language stress fixtures: double negation, conflicting instructions, typos, mixed units, regional grades, unknown resort names, embedded JSON, oversized requests and prompt injection demanding ignored restrictions. Treat request text as data, never execution/tool instructions. Preserve uncertainty rather than guessing intent. Pin expected metamorphic relationships only where meaning is genuinely equivalent; human-review ambiguous variants.

Time cases: midnight rollover, timezone-aware timestamps, DST repeated/nonexistent local times, boundary closing times, stale operating data. If current contract cannot represent an ambiguous time, reject/clarify explicitly rather than invent a timezone. Do not broaden the supported time contract accidentally through a test patch.

- [ ] Every generated accepted route passes independent validation; injected invalid paths are rejected.
- [ ] Failures emit seed/minimal fixture for replay and enter a regression corpus.
- [ ] Injection cannot alter graph data, hard constraints, model tools or provider configuration.
- [ ] Unsupported temporal cases fail explicitly and supported boundaries have regression tests.

## R03 Metrics and promotion

Implemented offline 2026-10-08: [contract and limitations](granular-evaluation-v1.md), [saved evidence](../research/evidence/model-robustness-r03/README.md). This ships scorer/gate tooling, not a new model or runtime semantic changes.

Extend `liftlap/evaluation_v2.py` through a new versioned report/scorer; retain original replay tooling. Record per-case transport outcome, raw-output hash, parsing/schema status, field errors, semantic issues, clarification correctness, proposed-route validity and end-to-end task outcome. Preserve every assigned case in the denominator, including timeouts and malformed outputs. Report transport completion separately, not by excluding failed requests.

Metrics: strict syntax/schema rate; exact intent match; per-field accuracy and exclusion-set precision/recall; hard-max/hard-exclusion violation counts; clarification false-positive/false-negative counts; end-to-end success; runtime percentiles; input/output tokens and reserved/reconciled costs. Break down by scenario and family, with sample counts. A schema-valid unsafe proposal rejected downstream is an extraction failure but a successful safety interception—report both. Report fallback results separately from primary-model success.

For repeatability, run a small predeclared validation subset repeatedly only within its reservation; report agreement **and correctness**. Consistently wrong is not robust. Record model/version, prompt/graph/renderer hashes, decoding seed and environment. Deterministic settings are not a guarantee of identical remote results.

**Proposed promotion rule, frozen before execution:** no accepted route violates a hard constraint in mandatory regression tests; no new critical extraction regressions against the base on validation; at least two additional validation task successes and no lower strict schema rate. Choose the base on ties. For a candidate passing validation, run the fixed final comparison and require no new critical regressions and higher final task success before promotion. Report uncertainty/paired outcomes; these operational gates do not establish statistical significance. A failing final result rejects this candidate; it must not trigger tuning on the same final set.

- [x] Scorer fixtures independently cover malformed output, wrong IDs, missing predictions, transport failure and all-failed repeatability.
- [x] Report totals reconcile exactly to the frozen case manifest and all attempted runs.
- [x] Historical replay is unchanged; new metrics are separately versioned.
- [x] Promotion decision and reasons are machine-readable and reproducible from saved outputs.

## R04 Runtime reliability

Audit existing bounded retry, stale-request cancellation, server validation, export state and spend reservations before adding mechanisms. Extend `sample_runner.py`, `tinker_sdk.py`, `training_transport.py`, `spend.py` and server/UI tests only where coverage or behavior is missing.

Set explicit per-operation deadlines and resource limits (input bytes, output tokens, concurrency, queue length). Values should derive from measured local/remote latency and declared deployment capacity; freeze them in configuration, not scattered constants. Read-only future inspection may retry within a deadline; ambiguous mutation submission must remain reserved and await reconciliation. Distinguish UI cancellation from provider cancellation: abandoning a response does not prove zero provider cost.

Failure matrix: 429/5xx, read timeout, connection loss before/after acceptance, malformed/partial responses, expired checkpoint, process restart, duplicate click, changed terrain during response, unavailable optional backend. No automatic paid fallback or unbounded repair loop. Offline/manual correction remains available and honestly labeled.

Structured logs contain correlation/run IDs, elapsed time, typed outcomes, model/config hashes and reservation status; redact credentials and avoid raw user requests by default. Track schema/semantic rejection and fallback rates. Route activation must be behind a reversible config flag; rollback restores the known base/offline mode without modifying immutable evidence or releasing uncertain holds.

- [ ] Fault-injection tests prove no duplicate charged mutation and no stale route publication.
- [ ] Budget accounting survives restart and concurrent attempts; unresolved calls stay counted.
- [ ] All operations terminate within configured bounds; failures expose useful recovery without weakening constraints.
- [ ] Rollback rehearsal succeeds without provider calls; logs contain no credentials or raw personal trip text.

## D01 Resort qualification

Build on existing source hashes, connectivity diagnostics, excluded-geometry preview and Discovery packet. Begin with one bounded Winter Park Discovery lift/return-path candidate; more imported geometry is not an activation criterion. Keep other resorts browse-only while evidence is incomplete.

Propose a versioned qualification record: source/version/hash; license/attribution; directed edge IDs; boarding/alighting/transfer evidence; native grade and regional mapping; access restrictions; operator status source and observed time; validity/expiry; timing measurement method/range; qualified reviewer and decision; unresolved blockers. Bind approval to the exact graph and evidence. Source updates invalidate affected decisions; never manufacture connectors from proximity. Field timing includes queues and uncertainty, not just geometric length.

State machine: `research → reviewed_geometry → operationally_verified → expired/suspended`. Promotion requires terminal/access/direction/transfer evidence, appropriately licensed current operational information and qualified timing checks. Expiry comes from source semantics/update policy and a recorded maximum age; do not invent a universal safe TTL. Unknown/stale operational status cannot be presented as open. Review/simulation mode may remain available with explicit non-navigation labeling.

Prefer an official documented feed/license where available. Public map visibility alone is not permission to redistribute an operator map or rely on it as live status. No operator outreach is sent without authorization. Qualified external reviewers/field observations are a real dependency; prepare a compact packet and continue other work while waiting.

- [ ] Activation rejects missing, expired, mismatched-hash or revoked evidence.
- [ ] Status-feed outage/source change suspends affected operational recommendations and explains why.
- [ ] Every activated segment has attributable direction/access/transfer/timing evidence, with uncertainty visible.
- [ ] Source refresh and rollback preserve original extracts and review history; no inferred connection is silently promoted.
- [ ] User documentation separates route simulation from any later operationally qualified pilot.
