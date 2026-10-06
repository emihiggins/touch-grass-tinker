# Sampling runner: dry-run verified, live execution not yet verified

`liftlap.sample_runner` uses the pinned SDK adapter and the checksum-verified Cookbook renderer. It never trains a model. It supports base model sampling or an explicit saved model path, uses one sample per request, temperature 0, fixed seed, 512 output tokens, and the same prompt/rendering contract for both adapters.

## Completed verification

- Actual local dry run for all 20 development scenarios: 12,319 input tokens; reserves at most 10,240 output tokens. No API calls.
- SDK HTTP mock tests exercise real request serialization and real protobuf sample decoding, pending polling and timeout bounds.
- Tests verify invalid JSON, duplicate keys, truncation, unchanged failure denominator, no semantic retries and stopping after a transport/provider failure.
- All 90 tests pass in the optional environment. The real capabilities read was verified earlier; **real sampling endpoint behavior remains unproven**.

## Run offline

```bash
.venv-tinker/bin/python -m liftlap.sample_runner benchmark/development-seed.jsonl --scenarios benchmark/request-development.json --run-dir runs/my-new-dry-run
```

No provider client is created without `--live`. The directory must not exist; runs never overwrite or automatically resume. Input, config, prompt, tokenizer and dependency-lock hashes are recorded. Without `--scenarios`, predictions use the case IDs for intent-only evaluation. With it, predictions use scenario IDs for full-request evaluation. No gold labels enter generation prompts.

## Proposed first live experiment — awaiting budget/credit confirmation

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

The runner uses pinned private SDK auth and protobuf conversion seams; upgrades require revalidation. Sample futures are requested directly using the documented `base_model` / `model_path` request fields, without a high-level training session. Training/checkpoint/resume remains a distinct unimplemented milestone.

## Score saved results

```bash
python3 -m liftlap.evaluate --scenarios benchmark/request-development.json --predictions runs/base-dev-smoke-001/predictions.jsonl
```

Later use `liftlap.request_compare` on base/tuned scenario-keyed files. Keep identical fixtures, decoding and rendering. No tuned model currently exists.
