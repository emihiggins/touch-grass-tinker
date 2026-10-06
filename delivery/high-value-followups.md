# Release-focused followups — October6

Owner direction: apply MIT; Emi alone changes visibility and posts to DEV. No new paid training, public deployment, or automatic publication. Finish a bounded set of high-value improvements before handing back.

## 1. Reproducible public-ready checks

Reuse Python unittest, existing Playwright scripts, GitHub Actions, and the available Gitleaks binary; no custom build system or hosting platform.

Acceptance: MIT and terrain notices included in local archive; two builds from identical files yield identical archive SHA; a clean Git worktree passes offline checks with no credentials or optional model packages; public-only CI runs these checks without secrets (private repositories skip the job). Prepared handoff must contain real repo/video links and preserve private visibility.

## 2. Frozen-results audit with a rules comparator

Reuse existing rules interpreter and hash-bound graph evaluator. Score the unchanged rules implementation on the already frozen16-case set, reproduce saved base outputs, and report both with provenance. This comparator is post-hoc and exploratory, not a preregistered selection experiment. Do not tune either interpreter or select another model using these results.

Acceptance: all16 cases remain in denominator, saved model result reproduces13/16, no provider requests, and the report distinguishes original base-selection protocol from the later comparator.

## 3. Preserve approved constraints through confirmation and print

The model's observed softening of a prohibition makes the original request and approved constraints important product information. Reuse semantic HTML and the existing correction controls.

Acceptance: confirmation displays original request and selected settings, local correction invalidates pending route output, itinerary/print includes approved difficulty/time/hard exclusions/soft preferences plus provenance; edited input hides stale output; keyboard operation and mobile reflow checked. No claim that this prevents all semantic errors or establishes field safety.

## Deferred deliberately

More fine-tuning needs a separately justified hypothesis and new evaluation plan; do not spend to chase a prize. Real terrain requires qualified review, live operations data and field validation. Public live hosting needs authentication, quotas and operational design; a public video plus downloadable local demo avoids pretending the loopback server is production-ready. Agent-session sharing is optional and omitted rather than publishing unrelated private history.

## Execution results

MIT applied. Gitleaks history scan passed after narrowly scoped, verified false-positive exclusions. Rules comparator saved:0/16 vs unchanged base13/16, explicitly post-hoc with no tuning. Deterministic package and public-only offline CI implemented. Confirmation displays original request/settings; print retains approved constraints. Keyboard check found and fixed lost focus after the async confirm action;320px reflow and stale-response rejection pass. Fresh Git worktree rehearsal and final one-page print inspection are the last verification steps.
