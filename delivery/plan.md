> **Historical planning/checkpoint document.** Retained for provenance, not a current feature or task list. Use the [current documentation](../docs/README.md) for the implemented app, completed experiments and supported setup.

# Delivery plan and evidence gates

Status: structural/source audits and offline seed/scorer implemented. The three-loop derivative-graph gate failed; [source checkpoint](../research/loop-verification.md) records the replacement path. A dependency-free offline importer/planner/validator and synthetic graph-backed evaluation now run; see [checkpoint](offline-checkpoint.md). A loopback demo UI/API, rules baseline and reversible compaction are now implemented; see [local demo](local-demo.md). No trained model integration. Contest facts and exact deadline: [challenge research](../research/challenge.md).

## Canonical map

- [Product brief](../product/brief.md): selected outcome and original contribution.
- [Requirements](../product/requirements.md): complete R01–R12 acceptance ownership/status.
- [Data research](../research/data-sources.md): sources, permissions and initial audit.
- [Feasibility](../research/feasibility.md): official resort references, directed audit and model/library preflight.
- [Architecture](../technical/architecture.md): contracts, API, planner, UI and operation.
- [Evaluation](evaluation.md): dataset, training, comparators and numeric targets.

## Dependency lanes and milestones

Dates are planning targets in UTC, not automation schedules. No polling jobs will be created.

| Phase | Target | Dependencies | Reviewable output | Requirements |
|---|---|---|---|---|
| A: data audit + contracts | Oct 6 | pinned terrain and official references | reviewed bounded sector, source manifest, normalized schema, at least 3 loops; synthetic graph fixtures | R01 |
| B: intent corpus + baseline | Oct 6–7 | Intent contract; Tinker access for baseline only | original split/frozen corpus, scorer, prompt/rules comparators, baseline report | R02, R03, R08, R11 |
| C: deterministic planner | Oct 7 | A; can proceed while B awaits model access | bounded planner, separate validator, feasibility/search-limit tests | R04, R06 |
| D: SFT + comparison | Oct 8 | B passing; verified credits/budget | real run/checkpoint, saved predictions and honest held-out result | R08, R09, R11 |
| E: interface + integration | Oct 8–9 | A/C; can start with labeled fixtures before D | mobile planner, constraint confirmation, map/card, explicit model/replay modes | R05, R07, R09, R10 |
| F: demo + reproducibility | Oct 10 | C/D/E | end-to-end traces, repeatable results, video, usability notes | R06, R07, R11 |
| G: write-up + release review | Oct 11 | F | English submission draft, code access/license, working demo/video links | R12 |

Parallel lanes mean independent work ordering, not authorization to spawn agents. If late, cut RL, live feeds, restaurant destinations, multi-resort coverage and visual polish. Do not cut baseline quality, graph validation or honest result reporting. Draft the story while experiments run, leaving metrics explicitly unfilled until measured.

## First implementation handoff

1. Read the requirements/contracts and pinned-source audit; initialize locked Python/frontend projects only when implementation starts.
2. Audit Alpendorf candidate: geometry-to-node alignment, source type/difficulty, lift direction, station access, duration provenance and closed-loop feasibility. Do not force-connect disconnected components. If sector fails after half a day, select a smaller OSM resort/sector rather than repair the whole region.
3. Implement pure contracts/scorer/graph validation before UI integration. Use original tiny fixtures to expose cycles, parallel edges, deadlines, closures and heuristic limits.
4. Author small development corpus; benchmark rules and competently prompted base; use this to verify task value before expanding training data.
5. Confirm Tinker login/credits/model availability and explicit allowable spending cap. A tiny checkpoint→sample smoke precedes full training. No API credential should be sent in chat or committed.
6. Follow dependency lanes and preserve measured evidence at each material commit.

## Verification suite (planned, not passing evidence)

- Import rejects missing IDs/durations, flags uphill anomalies, preserves parallel edges and excludes unreviewed links.
- Planner tests: directed return path, no-route, only-blues versus preference, no-drag exclusions, closed/unknown edge, missed closing time, time zone/date, start=finish nonempty outing, no teleportation, search cap distinct from infeasible.
- Independent validator adversarial fixtures: reverse edge, incorrect aggregates, absent edge, changed scenario hash, over-budget, forbidden piste and fabricated ID.
- Tiny exhaustive reference demonstrates bounded-search correctness; heuristic may miss routes but must not emit invalid ones or claim proven impossibility.
- Scorer uses gold labels independent of extraction; development/test provenance, family splits and dedup checks pass. Saved-response replay is byte-stable for deterministic per-case output.
- Browser: complete flow at 360px and 1280px, keyboard/text alternative, loading/cancel, clarification, provider failure and print labels.
- Operational: keys absent from client bundles/logs; input/rate/global-budget limits; startup rejects corrupt graph; rollback selects previous graph/model config.

## Historical planning claim ledger

Current submission evidence and remaining release gates are in [submission readiness](../submission/README.md). Rows below describe the original planning checkpoint, not current capabilities.

| Proposed claim | Necessary evidence | Current status |
|---|---|---|
| Finds constraint-compliant ski outings | R01/R04 plus graph audit and independent validation | Planned |
| Fine-tuning improves request understanding | R08 with frozen test and comparator metrics | Planned |
| Uses a real Tinker-trained model | R09 checkpoint-linked end-to-end trace | Planned |
| Uses real terrain with simulated winter conditions | R01/R05 provenance and visible scenario labels | Candidate terrain inspected; app planned |
| Helps reduce screen time | Timed usability comparison against manual map planning | Hypothesis, no claim allowed yet |
| Works offline / knows live lift status / field-tested skiing | Separate demonstrated capability | Out of scope; must not claim |

## Decisions and execution gates

Selected: Lift-Lap Planner; narrow language-to-constraints fine-tuning; deterministic route validation; private repo. Recommended: Alpendorf audited sector, Python/NetworkX + React/MapLibre, Qwen3-8B SFT. These recommendations can proceed to implementation within the user's future build scope, but are not evidence of working integrations.

Unresolved: audited sector acceptance, Tinker access and credits, spending allowance, final dependency versions, license choice for original code, deployment location, final data-publication arrangement and entrant eligibility. These do not block local planning/corpus design. Public repository visibility changes, deployment publication and DEV submission remain separate release actions.

Main risks: corrupted topology, shallow language task already solved by prompting, synthetic language leakage, no measured gain, remote latency, time pressure, and October not permitting a Flachau ski field test. Use a clearly described planning/usability trial; do not rebrand an outdoor laptop demo as an on-snow test.

## Completion policy

Each requirement row has exactly one owner in the requirements file. Mark implemented/verified only when linked evidence exists. Initial structural graph evidence does not satisfy R01's real-world audit. Before submission, verify accessible code/demo, attributions, record late changes as required, and obtain release authority without changing private visibility implicitly.
