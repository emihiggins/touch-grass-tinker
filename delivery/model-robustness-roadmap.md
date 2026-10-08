# Model quality and robustness roadmap

Status: **in progress — M01, R01 and R03 implemented offline** · 2026-10-08. This is the canonical execution queue for the next model/robustness iteration, not a replacement for frozen protocols or the as-built architecture.

## Outcome and evidence

Improve reliable intent extraction and failure handling without weakening the deterministic routing boundary. More training is not itself success. Historical measurements remain in [evaluation](../docs/evaluation.md): pilot base 9/16 versus tuned 7/16; retained base 13/16 on the separate reviewed set. These are small, same-agent-authored, human-reviewed fictional sets, not proof of real-world accuracy.

The next work starts with observed failure classes: malformed tuned output, incomplete lift exclusions, contradictory clarification state, and a stale UI duration overriding an explicit request for clarification. Causes are hypotheses until audited. Existing renderer checks already cover assistant-only loss, target round-trip and next-token alignment.

## Canonical work queue

Each ID below has exactly one detailed specification in the linked domain plan. Package acceptance boxes are updated only with linked implementation evidence. A coding agent owns implementation/evidence; Emi reviews new labels; qualified resort reviewers own external operational evidence.

| ID | Priority | Work package | Dependencies | Specification |
| --- | --- | --- | --- | --- |
| M01 | P0 | Target and terminal-token forensic audit | None | [Training](../training/next-iteration-plan.md#m01-target-audit) |
| M02 | P0 | Reviewed, family-split data expansion | M01 taxonomy | [Training](../training/next-iteration-plan.md#m02-data-and-splits) |
| M03 | P1 | One bounded checkpoint-selection experiment | M01, M02, R03, budget readiness | [Training](../training/next-iteration-plan.md#m03-bounded-sft) |
| M04 | P1 | Constrained-output feasibility comparison | M01, R03 | [Training](../training/next-iteration-plan.md#m04-constrained-output) |
| R01 | P0 | Semantic validation and explicit-context precedence | None | [Robustness](../technical/robustness-plan.md#r01-semantic-contract) |
| R02 | P0 | Deterministic boundary and adversarial/property checks | R01 | [Robustness](../technical/robustness-plan.md#r02-planner-boundary-and-adversarial-tests) |
| R03 | P0 | Versioned granular scoring and promotion gates | None | [Robustness](../technical/robustness-plan.md#r03-metrics-and-promotion) |
| R04 | P1 | Bounded runtime failure handling and observability | R01, R02 | [Robustness](../technical/robustness-plan.md#r04-runtime-reliability) |
| D01 | P1 | Qualified real-resort operational data pilot | R02; external evidence for activation | [Robustness](../technical/robustness-plan.md#d01-resort-qualification) |

## Current checkpoint

M01 is implemented: [47-row target audit, SDK wire checks and saved-failure inventory](../research/evidence/model-robustness-m01/README.md). No paid calls or model/runtime changes. R03 is also implemented: [versioned metrics, all-attempt accounting and promotion gates](../research/evidence/model-robustness-r03/README.md). R01 is implemented offline: [typed semantic-contract checkpoint](../research/evidence/model-robustness-r01/README.md). R02 is next; remaining packages are not yet implemented. Historical raw outputs and scores are unchanged.

## Execution and delivery

1. **Offline foundation:** implement M01, R03, R01, then R02. Preserve raw evidence and introduce versioned reports rather than rescoring history under new rules.
2. **Data preparation:** implement M02 tooling and draft candidates; request human review in manageable packets with changed rows clearly identified. Continue R04 and D01 evidence tooling while awaiting review.
3. **Model research:** complete M04 capability probe without replacing the runtime. Preregister M03 only after data freeze, token accounting and current prices/access are verified. Do not change prompt, decoding and training simultaneously in one causal comparison.
4. **Release decision:** apply R03 gates; publish all attempted outcomes internally. Promote only a qualified candidate behind a reversible feature flag. Otherwise retain the current base and document the negative result.
5. **Independent terrain lane:** D01 may produce review tooling without activating any new real-world route. Missing operator/field evidence is a documented external dependency, not a reason to block unrelated software work.

For each package: small branch/PR, relevant regression checks, documentation and evidence updates, secret scan, private merge. Run full release checks when runtime/data/generator integration changes; documentation-only updates need link/coverage checks. Refresh screenshots only for visible changes. Never edit generated HTML without its generator and regeneration test. Repository visibility and DEV publication remain Emi-controlled.

## Spending and experiment limits

[Budget authorization](../training/budget-authorization.json) remains authoritative: $10 total, staged $1 smoke / $4 experiments / $5 justified reserve. This roadmap spends nothing. Previously reported $1.75 commitments remain held until reconciled; they are not a current invoice or proof of available credit. Old prices, account balances and expired checkpoints must not be assumed current.

M03 defaults to **one remaining training configuration** in the original two-configuration experiment allowance. Checkpoint evaluations are budgeted explicitly. M04 must not quietly add another training configuration, paid hosting or an unbounded backend deployment. Additional experiments require a recorded justification within authorized reserve, or new authorization if outside the existing scope/cap. Reserve worst-case input/output, all evaluations, checkpoint storage and unresolved submissions before launch. Stop on ambiguous mutation results; reconcile existing future IDs, never duplicate training automatically.

## Review and blocker handling

- Human labels: Emi sees request, context and proposed interpretation, with disagreements unresolved until adjudicated. Approval is bound to exact bytes; material edits invalidate it.
- Billing/provider access: verify when needed; while blocked continue offline work. No API keys in review packets.
- Resort activation: requires qualified source/field review, not a conversational approval of topology.
- No action is required from Emi merely to accept these plans. Later review requests should identify exact rows or evidence gaps.

## Roadmap completion criteria

- [ ] Every M/R/D package has implementation evidence or a named external blocker and next action.
- [ ] All attempted model outcomes, including failed transports and invalid outputs, are reported.
- [ ] New evaluation splits are immutable and historical evidence is unchanged.
- [ ] Promotion/rollback decision is recorded; failure to improve is an acceptable research outcome.
- [ ] Updated user/developer docs distinguish local prototype, model research and qualified real-world capability.
