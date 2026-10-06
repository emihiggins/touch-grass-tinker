# Human review checkpoint — 2026-10-06

Emi reviewed all 48 candidates. Exact human notes, timestamp, explicit decision, reviewed-content hash and separately identified agent responses are stored in the canonical `benchmark/training-candidates.jsonl`. The [generated packet](review-packet.md) displays them; regenerating it no longer resets decisions to pending.

- **41 explicit label approvals**, including 011's approval with a question.
- **40 non-quarantined approvals**: 009 is approved semantically but still overlaps development wording.
- **7 held labels**: 004, 005, 013, 028, 032, 036, 043. Notes/questions are not converted into approvals.
- All rows remain in the candidate partition until adjudication and final dataset selection. There is no approved training run or frozen test yet.

## Adjudication and product implications

| Case | Human feedback | Recorded response / next action |
|---|---|---|
| 004 | Blue-only skier may struggle with t-bars | Piste difficulty does not establish lift comfort. Recommend a separate explicit lift preference, not an inferred exclusion. Current label held pending agreement. |
| 005 | Avoid vs no gondolas; possible access-lift exception | The current schema only has hard exclusions. A soft-avoidance field needs a versioned contract and planner objective. Never silently override an exclusion for the first lift; surface any exception as a user-visible choice. Held. |
| 009 | Approved | Approval recorded. Leakage quarantine remains; exclude it from eventual training or replace it with genuinely new reviewed material. Do not just reword to evade the audit. |
| 011 | Approved; should missing ability default to hardest? | Approval retained. Keep null and clarify; unknown ability must not silently grant the hardest grade. |
| 013 | Five hours = 300 minutes; consider last lifts | Correction retained as requested, not written as invalid schema-v1 gold. A clear duration is not missing information. Next contract version must preserve it; planner checks actual edge operating windows without inventing a resort closing time. Last lift closure is not necessarily the latest possible finish after descent. |
| 028 | Ten minutes rather than null | Correction retained. Current schema has a 15-minute minimum; change the contract consistently before relabeling. Planner may return infeasible, but interpretation should preserve the explicit ten-minute request. |
| 032 | Multiple preferred grades imply variety? | Recommend no automatic variety flag: acceptable/preferred grades and distinct-run variety are different objectives. Current label held rather than inferred approved. |
| 036 | Maybe start place should be null | Exact source says **when**, not where. The UI still selects valley; only start_time is unresolved. No label edit. Held pending acknowledgment. |
| 043 | Red-or-easier allows easier variety | Blue/red are permitted by the ceiling. This does not necessarily request mixing grades or distinct runs. Keep variety separate; crowding still unsupported. Held. |

## Contract migration before further training

Duration handling and soft lift preferences affect schemas, prompts, examples, scorer, rules adapter, UI/API limits and planner behavior. Use a versioned change and retain the existing v1 measurements unchanged. Do not report old predictions as evaluated on revised gold without explicitly labeling a rescoring. Resolve duration bounds as an operational resource limit separately from what the user said. Do not invent live operating hours from the language-only catalog.

Human review is now complete as an activity; resolution of these seven labels is not. No second pass over the 40 undisputed, non-quarantined approvals is needed unless their request/context/catalog/gold changes. Any such change invalidates the approval hash. Export and training preflight reject disputed, stale or quarantined approvals even if `human_reviewed` is true.

## Evidence scope

The reviewer changed no gold labels in this checkpoint: the two numerical corrections conflict with v1 and remain explicit requested changes. Previously saved model scores remain v1 historical evidence. Old rendering/batching artifacts refer to earlier corpus hashes; the refreshed batch rehearsal and review audit cover the current metadata. Offline batch coverage still does not authorize these candidates for training.
