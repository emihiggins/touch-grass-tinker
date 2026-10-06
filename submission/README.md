# Submission readiness — October 6, 2026

**Private preparation checkpoint, not submitted or ready to claim Best Use of Tinker.** Deadline: October 11, 11:59 PM PDT / October 12, 06:59 UTC. [Official requirements and sources](../research/challenge.md).

## Reviewer package

- [DEV article draft](dev-post.md): exact official template headings, actual development metrics and limitations; `published: false`.
- [Two-minute demo storyboard](demo-storyboard.md): steps matching current UI; no video produced yet.
- [Local run instructions](../README.md#run-locally-python-311-no-dependencies).
- [Saved live baseline evidence](../research/evidence/base-v2-development/report.json), [raw predictions](../research/evidence/base-v2-development/predictions.jsonl), [paired prompt development comparison](../research/evidence/base-v2-development/prompt-comparison.json).
- [Training candidate review packet](../training/review-packet.md) and [offline batch rehearsal](../training/batch-rehearsal.md).

## Release gates

| Gate | Evidence / exact remaining work | State |
|---|---|---|
| Article follows official template | All seven headings and both required tags verified against the October 6 challenge page; article written in English | Draft complete |
| Honest development result | Rules 14/20, base v1 6/20, base v2 13/20; denominator/failures retained | Recorded, not held-out |
| Approved corpus | 47 source-reviewed rows migrated to v2 under the agreed changes; 009 excluded. [V2 corpus](../benchmark/v2/README.md) | Partial |
| Independent test | 16-case pilot reviewed: 14 approved, two preferred-blue corrections open; final untouched set/freeze still missing | Partial |
| Real Tinker fine-tuning | Budget authorized: $10 total; account billing/credits, protected-auth integration, guarded execution and actual checkpoint remain pending | Not run |
| Baseline improvement | Same-base, same-renderer independent comparison; report failure if the gain is absent | Missing |
| Trained model in app | Actual checkpoint-linked request → intent → validated route, explicit live/replay mode | Missing; browser uses rules |
| Judge-accessible demo | Record and review video or deploy an appropriately bounded demo; verify access without owner login | Storyboard only |
| Judge-accessible code | Resolve private-repo judging access and original-code license; preserve third-party/model/data obligations | Open; repo stays private |
| Terrain claims | Three reviewed loops/access/direction still unresolved; simulation-only scope is explicit | Open; no field-ready claim |
| Entrant/release | Confirm DEV account/eligibility, teammate credits if applicable, and final publication authority | Open |

Agent-session sharing is optional, not a mandatory blocker. Do not delay required evaluation/video work for a full transcript export. Do not publish an unrelated workspace session.

## Next sequence

1. Resolve the two preferred-blue field corrections in the [reviewed 16-case pilot](../training/evaluation-review-v2.md); then prepare/freeze the final independent benchmark. Contract changes and reviewed training migration are implemented.
2. Integrate protected Tinker training with the existing Cookbook checkpoint lifecycle, bounded spend and uncertain-call recovery. The [local rehearsal](../training/batch-rehearsal.md) is not this integration.
3. Use the [authorized $10 staged budget](../training/budget-authorization.json) after data/config, account billing/credits and bounded accounting checks pass. Authorization is recorded; do not ask again for the same scope. Include prior usage and checkpoint storage.
4. Run a bounded training/checkpoint/sample smoke, then the preregistered comparison; integrate a real model path in the demo.
5. Record the demo, finish result-based writing, resolve code/demo access, and seek final publication approval.

If fine-tuning does not show a defensible gain, do not substitute the 6/20→13/20 prompt change as the category result. Reassess the category honestly; the overall challenge still needs meaningful open-AI integration and an accessible finished submission.


## Checkpoint verification

On October 6, all **97 tests passed** in the pinned optional training environment. The dependency-free run passed 83 tests with 14 optional skips. The real rendered rehearsal covered 48 candidates in three batches; restarting the local cursor after batch one reproduced the remaining 32 rows. The default 32-row configuration was refused. Saved-output scoring reproduced 14/20, 6/20 and 13/20 without provider calls. Local documentation links and the seven official template headings passed checks. No UI code changed; browser/print evidence remains the earlier checkpoint, not a new accessibility audit.
