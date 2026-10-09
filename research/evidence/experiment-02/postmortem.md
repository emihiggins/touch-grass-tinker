# SFT02 postmortem and next data priorities

## What the tie conceals

Both arms remain **10/16**. No score has been repaired or replaced. The read-only
[postmortem](postmortem.json) inspects all32 saved outputs with exact case alignment
and source hashes. Reproduce with `python3 scripts/analyze_experiment02.py`.

The base returned four routes accepted under its interpretation but invalid against
the reviewed constraints (006,010,011,014). The tuned arm returned two (010,014).
This is **gold-relative evaluation**, not a check the live application can perform
without the reviewed answer. Do not convert “no paired gold-validity regression”
into “all produced routes obey the user's actual intent.”

Two changes explain the difference:011 now preserves the two-minute budget, while
006 stops on malformed JSON rather than returning a softened gondola prohibition.
The latter is interception, not successful interpretation. One soft preference is
lost at005, leaving aggregate task success unchanged. Small exposed-pilot counts
cannot establish a general safety improvement.

## Case-level findings and work order

| Case | Base → trained | Confirmed failure or gain | Next data/review target |
| --- | --- | --- | --- |
| 005 | pass → fail | Soft gondola avoidance disappears; route validity alone misses this preference loss | Contrast hard prohibition, soft avoidance, and no preference using shared families |
| 006 | fail → fail | Base softens a hard prohibition; tuned JSON has an extra quote and its object prefix omits the prohibition entirely | Explicit “even if the only access” hard constraints; no access-lift exception invented |
| 010 | fail → fail | Both retain only magic-carpet exclusion rather than all four surface-lift types | Universal category plus named example; verify full subtype expansion |
| 011 | fail → pass | Trained output preserves two minutes instead of the50-minute UI default | Retain short-budget contrast coverage; feasibility belongs to the planner |
| 013 | fail → fail | Unnecessary clarification retains the disputed maximum; variety request also lost; tuned adds trailing quote | Valid context inheritance versus explicit unknown, paired with variety requests |
| 014 | fail → fail | Explicit destination is replaced by the UI default; route goes to wrong finish | Known place alias override paired with genuinely unknown destinations |
| 015 | fail → fail | Both emit ready while listing unsupported live grooming | Unsupported status and live-data claims must be adjudicated consistently |

The pending eight-row review packet already contains hard/soft surface constraints,
short/unknown budgets, grade preferences and an unknown-place example. It does not
fully cover known-destination overrides, valid-context/variety contrast, or live
conditions versus static routing. Add those families after reviewing the existing
packet, not by copying these evaluation rows into training under new IDs.

## Formatting is not the whole problem

The two malformed tuned outputs (006,013) are complete JSON objects followed by an
extra quote. Both stop normally below the512-token output cap. Inspection of the
object prefix is **forensic only**:006 still omits a hard exclusion;013 still retains
a disputed clarification value and misses variety. Deleting the trailing quote
would not turn either into a correct answer. This is not an experiment measuring
constrained decoding, which could change the generated contents as well as syntax.
No decoder repair, prediction edit, re-score or causal diagnosis is introduced here.

## Recommended next experiment prerequisites

1. Adjudicate the [existing eight training candidates](../../../benchmark/iterations/m02-v2-review-2026-10-08/review-first.md); none is implicitly approved by this analysis.
2. Expand the three missing contrast families above, with truthful lineage and
   independent review. Keep all error-driven examples in training/development.
3. Add graph-bearing positive and negative route cases, including a disconnected
   requested finish and single-access-lift exclusion. Data checks must compare route
   behavior against the proposed label before human approval.
4. Keep this pilot diagnostic forever. A new independently reviewed final split
   must not be authored by recycling this error inventory.
5. Probe constrained-output feasibility separately, without claiming formatting
   constraints solve semantic omissions. Both planned training configurations are
   consumed; do not launch a third automatically.

The application still requires explicit constraint review. Deterministic schema
and semantic validation cannot detect every mismatch with natural-language intent.
No keyword patch fitted to these seven pilot cases is proposed.
