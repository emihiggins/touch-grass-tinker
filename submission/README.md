# Submission handoff — October 11, 2026

**Deadline: October 11 at 11:59 PM PDT / October 12 at 06:59 UTC.**
The official challenge and contest rules were rechecked on October11. The repo
remains private and the article unpublished; Emi controls both publication actions.

## Ready-to-use materials

1. **[Final article](dev-post.md)** — title/tags plus the official seven-section structure.
2. **[Copy-ready article body](dev-post-body.md)** — paste this into DEV's body editor, without YAML.
3. **[Final posting checklist](dev-posting-checklist.md)** — visibility, signed-out checks, preview and publish.
4. **[Demo video](../demo/walkthrough.webm)** and [reproduction guide](../demo/README.md) — credential-free fixed-frame recorded-AI/correction flow, not a hosted service.
5. **[Repository README](../README.md)**, [user guide](../docs/user-guide.md), [developer guide](../docs/development.md), [evaluation](../docs/evaluation.md), [licenses](../THIRD_PARTY_NOTICES.md).
6. **[Dated verification record](verification.json)** — actual checks and remaining owner actions, not a claim of DEV publication.

## Requirement-to-artifact checklist

| Official requirement | Prepared artifact / evidence | Status |
| --- | --- | --- |
| New project and repository within entry window | First commit705672c: October5 20:10:56 UTC, after the16:00 UTC opening; current work predates deadline | Verified local Git history; no post-deadline changes yet |
| Open-source AI at core, Touch Grass theme | Article explains Qwen3-8B intent extraction, deterministic planning and compact outdoor itinerary goal | Implemented prototype; no field-use claim |
| Published DEV post, template and tags | Final article; tags `devchallenge`, `hf26challenge` | Prepared; Emi must publish |
| Demo and code link | Recorded video, repository link, local quick start | Files verified locally; signed-out access awaits visibility switch |
| Why open innovation matters | Article's dedicated section and upstream credits | Prepared |
| Credit nontrivial foundations | Article, MIT license, ODbL and third-party notices | Prepared; licenses remain separate |
| Agent session | Explicitly omitted; optional under current rules | No transcript or private context exported |
| Partner category request | Best Use of Tinker requested; actual fine-tuning and both trial results disclosed | Clear-improvement criterion remains unproven; organizers decide |
| Entrant eligibility / team credit | Official rules and posting checklist | Emi verifies personal eligibility and any teammates |

## Submission claims

- Trial01: paired base9/16 → tuned7/16. Trial02: paired base10/16 → tuned10/16.
- Separate fresh set: base13/16; not a gain over either pilot and not field validation.
- Live inference is optional research setup, not available through the default clone-and-run path.
- Video is exact replay of one real model response and its local correction, not continuous live inference.
- Both temporary trained checkpoints were configured to expire after six hours; no current hosted tuned model is promised.
- Existing eight-label review is for future research and does not block submission. No labels are silently approved.

No new training, paid calls, visibility changes, DEV publication or public release
uploads are part of this preparation. Billing remains unreconciled: $3.00 total local
commitments are reservations, not actual charged cost. That does not block publishing
the honest completed-results article.

## Tinker category interpretation — October 11 update

The [contest rules](https://dev.to/page/hacktoberfest-week1-2026-10-05-contest-rules) say entries are automatically eligible for partner categories whose technology they meaningfully use. The [category description](https://dev.to/challenges/hacktoberfest-week1-2026-10-05) specifically asks for fine-tuning and a clear improvement in performance, latency or cost over a baseline. The earlier blanket recommendation not to enter was too categorical: the article now requests consideration based on genuine Tinker use, while explicitly stating that the improvement criterion has not been demonstrated. This is not an organizer ruling or a new experimental result.
