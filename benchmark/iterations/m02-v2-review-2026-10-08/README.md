# M02 intent-v2 replacement review packet

Start with [the blind review sheet](review-first.md), then open
[the proposed interpretations](proposals.md). Eight new fictional requests replace
the old 12-row legacy packet as the next review surface. The old packet is preserved,
not migrated or approved. No response from Emi has been recorded as label approval.

## Scope

- Eight **training candidates**, all unapproved; no validation or final split.
- Five semantic/template families; hard/soft lift, known/unknown budget and grade
  contrast pairs are grouped. All rows share one catalog/context family, not eight
  independent graphs. There is no graph, route success label or terrain claim.
- Covers all surface-lift subtypes, soft versus hard constraints, eight-minute and
  explicitly unknown budgets, green maximum, multiple grade preferences without
  variety, unknown places, and unsupported transport booking.
- Ready/clarify/unsupported labels pass structural and semantic checks. Those checks
  do **not** prove the proposed interpretation matches the prose; Emi adjudicates it.
- Positive/negative routes, closures, disconnected topology, provider injection,
  time ambiguity and broad language diversity remain gaps. Eight rows are not a
  training-ready corpus or a statistically representative evaluation.

`review-manifest.json` records the exact hashes of eight supplied source files
(including historical evaluation only for overlap diagnostics), with zero detected
ID/key/similarity/family conflicts. This is a lexical/declared-lineage check, not
proof of semantic independence. No historical evaluation row was copied into the
new packet. All new candidates are training-only.

## Export repair

PR #34's export path converted candidates to legacy `train` before auditing, which
required a legacy approval hash incompatible with the M02 full-row approval hash.
The corrected path structurally audits candidate rows, then independently enforces
current M02 approval and intent-v2 semantic validity. Tests now include a successful
synthetic approved export, stale approval rejection, contradictory clarification,
missing source audit and cross-partition family leakage. Test approvals are fixture
metadata, not approvals of these candidates.

Export requires an explicitly supplied nonempty source corpus. The caller must
include the full applicable corpus; software cannot infer omitted external data.
CLI reports include source file hashes. Approval binds all row fields except review
metadata, including lineage, split and constraints. Exporting these unapproved
rows fails. No provider calls, training or split freeze occurred.

The older `iteration_manifest` remains the reproducible m02-2 diagnostic format;
this packet uses m02-review-packet-3 metadata to avoid presenting its historical
“no exporter” statement as current capability. `training_export_supported: false`
in this packet means this unapproved packet cannot currently export.

## Verification

Full offline release checks passed: 247 tests run (25 optional skips in the system
interpreter); all 247 passed in the pinned optional environment with no skips.
Historical R03 report comparisons still reproduce, saved fresh base remains 13/16,
and the isolated demo archive reproduced across two builds. The actual review packet
fails export until adjudicated; synthetic test approvals exercise the success path.
