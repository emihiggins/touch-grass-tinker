# Sampling runner: live development smoke completed

> Current spending authority: [the $10 staged project budget](budget-authorization.json) supersedes the earlier inference-only cap below. Existing per-run estimation is not project-wide enforcement; shared accounting and prior-charge reconciliation remain required.

`liftlap.sample_runner` uses the pinned SDK adapter and the checksum-verified Cookbook renderer. It never trains a model. It supports base model sampling or an explicit saved model path, uses one sample per request, temperature 0, fixed seed, 512 output tokens, and the same prompt/rendering contract for both adapters.

## Completed verification

- Actual local dry run for all 20 development scenarios: 12,319 input tokens; reserves at most 10,240 output tokens. No API calls.
- SDK HTTP mock tests exercise real request serialization and real protobuf sample decoding, pending polling and timeout bounds.
- Tests verify invalid JSON, duplicate keys, truncation, unchanged failure denominator, no semantic retries and stopping after a transport/provider failure.
- All 90 tests pass in the optional environment. The real capabilities read was verified earlier; **real session-based sampling subsequently passed; results below**.

## Run offline

```bash
.venv-tinker/bin/python -m liftlap.sample_runner benchmark/development-seed.jsonl --scenarios benchmark/request-development.json --run-dir runs/my-new-dry-run
```

No provider client is created without `--live`. The directory must not exist; runs never overwrite or automatically resume. Input, config, prompt, tokenizer and dependency-lock hashes are recorded. Without `--scenarios`, predictions use the case IDs for intent-only evaluation. With it, predictions use scenario IDs for full-request evaluation. No gold labels enter generation prompts.

## First live experiment — approved and completed (historical launch plan)

Run **one 20-case development baseline smoke** on Qwen/Qwen3-8B, no fine-tuning and no automatic submission retries. It is a provider/pipeline smoke and descriptive development result, not final held-out evaluation or the final carefully developed baseline.

Official model pricing JSON, checked 2026-10-06, lists $0.195/million input tokens and $0.60/million output tokens. Reserving every output token gives **$0.008546205** estimated token charges (less than one cent), without assuming cache discounts. This is not an invoice or a provider-enforced spending cap; verify current rates/account credits before execution. Proposed authorization ceiling: **$1, inference only**, with no extra runs automatically scheduled. Do not launch without Emi's approval and credits/billing verification.

After that confirmation, execute through Gateway exec so only protected credential sentinels enter the process:

```bash
.venv-tinker/bin/python -m liftlap.sample_runner benchmark/development-seed.jsonl --scenarios benchmark/request-development.json --run-dir runs/base-dev-smoke-001 --live --max-requests 20 --credits-confirmed --budget-usd 1 --input-usd-per-million 0.195 --output-usd-per-million 0.60
```

The budget guard checks the full run's token-based upper estimate before submission. It does not meter other jobs, verify the supplied rates, check an account balance, or impose a provider-level hard cap. It assumes no hidden non-token charges. No training-spend approval is implied.

## Records and failure policy

- `manifest.json`: prepared/running/completed state, run ID, model/path, decoding, hashes and supplied budget/rates. Actual remote model-call count is unknown once live execution begins; local submission attempts are reported separately.
- `events.jsonl`: submission start and returned future ID. A submission can succeed upstream and fail before returning its ID; treat this as ambiguous rather than retrying automatically.
- `predictions.jsonl`: per-case intent or null, raw decoded output, stop reason, input/output token counts, elapsed time, future ID and reported cache-hit count. These token counts are not verified billing usage.
- Bad JSON, schema violations or length stopping remain semantic failures with no second attempt.
- Provider/transport/schema failures halt subsequent submissions; remaining cases are explicitly `not_attempted_after_transport_failure`, never dropped from the denominator. Summarize availability separately from semantics.
- Each request has a run-specific idempotency key; upstream deduplication semantics have not been live-proven. SDK retries are disabled. At most 12 future polls, each HTTP timeout 5 seconds, one second between pending replies; entire sample has a 90-second bound. These bounds are local: timed-out remote work may still complete and incur charges.
- No automatic restart/resume or cancellation is implemented. Reconcile saved future IDs and any ambiguous submission before a new run. Never reuse successful prompts as a workaround for failures.
- Logs omit raw exception strings/headers. Prompts contain only fictional project data; responses are retained locally under ignored `runs/` for scoring. No credentials are put in prompts or files.

The runner uses pinned private SDK auth and protobuf conversion seams; upgrades require revalidation. The live-proven path creates an SDK session with its version, creates a sampling session for the model/path, heartbeats it before each request, and supplies `sampling_session_id`, monotonic `seq_id` and `X-Tinker-Sampling-Backpressure: 1` when submitting. The earlier direct/sessionless path was rejected as outdated; creation of sessions alone was insufficient without the backpressure header. Training/checkpoint/resume remains a distinct unimplemented milestone.

## Score saved results

```bash
python3 -m liftlap.evaluate --scenarios benchmark/request-development.json --predictions runs/base-dev-smoke-001/predictions.jsonl
```

Later use `liftlap.request_compare` on base/tuned scenario-keyed files. Keep identical fixtures, decoding and rendering. No tuned model currently exists.


## Live outcome — 2026-10-06

Emi approved the inference-only smoke and $1 ceiling in Telegram message 2288. No training was authorized or run. The first two runner attempts plus one same-idempotency-key diagnostic replay were rejected with HTTP 400 before any future ID was returned. We preserved those attempts instead of calling them model-quality failures. Source inspection and isolated session diagnostics established the working request sequence: SDK session, sampling session, heartbeat, monotonic sampling sequence ID and `X-Tinker-Sampling-Backpressure: 1`. Session creation alone did not fix the rejection. The third runner attempt generated all 20 outputs.

**Observed result:** 6/20 strict full-request successes; 11/20 schema-valid outputs. Nine invalid outputs remain failures; none were repaired or retried. Slices: feasible routes 1/4, infeasible requests 2/4, clarification 2/8, unsupported requests 1/4. The rules-v1 comparator scored 14/20 on the same visible development scenarios. This is a weak first prompted-base smoke, **not the final competently developed baseline and not held-out accuracy**. Do not use it as a deliberately weak comparator for a prize claim.

Examples of failure: emitting unsupported lift type `drag` rather than the enumerated surface-lift types; returning `ready` despite a null required field; unnecessary clarification despite UI defaults. Strengthen the baseline prompt with development-only schema/examples, inspect failures and freeze it before formal comparison. No final heldout data exists yet. Further live experiments are not automatically authorized by this completed one-smoke approval.

Observed usage: 12,319 input tokens, 2,459 output tokens; 9,728 input cache-hit tokens reported. At the checked noncached rates the completed run estimates **$0.003877605**, before cache discounts. This is not a verified invoice; rejected-request charges are unverified. The budget preflight reserved under one cent for each 20-case attempt and retained ample margin within the $1 authorization. Pilot median latency 1.858 s and nearest-rank p95 2.330 s include request setup/polling; these are not controlled latency benchmark results.

Saved private artifacts: `research/evidence/base-dev-smoke/` contains actual raw predictions, manifest, submission/future events, the independent graph-backed report, and both rejected runner attempts. The extra diagnostic rejection is described in the report. No secret values are included. Replay scoring without Tinker:

```bash
python3 -m liftlap.evaluate --scenarios benchmark/request-development.json --predictions research/evidence/base-dev-smoke/predictions.jsonl
```

No tuned model exists. Data review, independent test creation, improved/frozen baseline, and training/checkpoint implementation remain pending. The final `baseline_recorded` training gate stays false because a smoke is not the final baseline.
