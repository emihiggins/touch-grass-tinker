# Offline training-readiness checkpoint — 2026-10-06

No model has been called or trained. This is dataset/export and saved-prediction tooling, **not an authenticated Tinker runner**. Production training and inference adapters remain to implement and smoke against a locked SDK/Cookbook environment. Runtime stays dependency-free for now.

## Existing assets

- 32 visible development examples unchanged.
- 16 new, original compositional **training candidates**, in a separate fictional Juniper catalog. Covers combined constraints, corrections, deadline caps, missing fields, aliases, exclusions and unsupported capabilities. Agent-authored/reviewed, **not independently or human reviewed**. These are a small inspection batch, not the planned 400+ training examples.
- `python3 -m liftlap.corpus benchmark/development-seed.jsonl benchmark/training-candidates.jsonl` validates labels, duplicate IDs/text, provenance, cross-partition template and graph-family reuse. Semantic topic families may recur; template/paraphrase lineage must not. Legacy seed families conservatively stand in for template groups.
- Token-set near-duplicate warnings require resolution before production export. This is a heuristic, not proof of no leakage. Current warning: `dev-seed-008 / train-candidate-009`; quarantine candidate 009 pending review, do not promote it as-is. All candidates remain ineligible for production training.
- Candidate export for inspecting the Cookbook format:

```bash
python3 -m liftlap.corpus benchmark/development-seed.jsonl benchmark/training-candidates.jsonl --preview-candidates --output /tmp/liftlap-conversations-preview.jsonl
```

Only training candidates enter this explicitly marked preview. Ordinary export accepts only `train` rows, requires human-reviewed labels, and excludes dev/test. This conservative export gate is stricter than the protocol's minimum 10% training review. Keep all partitions in the audit invocation: auditing only a train file cannot detect leakage to omitted partitions. Input/prompt/output SHA-256 values accompany reports. Hashes do not prove independent review or a frozen test.

Each exported line contains `messages`: system prompt, user JSON containing only request/context/catalog, assistant gold JSON. Inference uses the same `conversation(..., target=False)` builder, which omits the answer. IDs/labels/provenance never enter user content.

## Cookbook preflight (confirmed in source, not installed)

[FromConversationFileBuilder and batch implementation](https://github.com/thinking-machines-lab/tinker-cookbook/blob/1c03a20fdda98156ccbec15728c0e2764b5a0bc3/tinker_cookbook/supervised/data.py), inspected 2026-10-06:

- `messages` is the file contract; reuse the existing builder rather than invent a training format.
- Set `test_size=0`: splits are assigned beforehand. A random row split inside the builder is not our held-out protocol.
- Assistant-only loss is supported. Inspect actual rendered token weights and JSON round trips before launch.
- `max_length` can truncate. Count with the actual tokenizer, reject overlength examples; never train silently truncated targets.
- Dataset length is `len(rows) // batch_size`: incomplete batches are dropped. Our 16 candidates with batch 32 would produce **zero batches**. Require a nonzero batch count and explicitly account for all dropped rows or use an exact-divisor batch size. Do not duplicate examples to hide this issue.
- `sft-plan.json` is a project planning artifact, NOT a directly runnable Cookbook config. Gates are false deliberately. Token counts, package versions and actual access are unverified.

## Saved paired comparison

```bash
python3 -m liftlap.compare benchmark/development-seed.jsonl /path/to/base.jsonl /path/to/tuned.jsonl
```

Both files contain `{id, intent}` rows, same IDs and frozen inputs. Missing/invalid intents fail; duplicate/foreign IDs abort. Reports retain per-case mismatches and input hashes, plus deterministic paired template-cluster bootstrap intervals. Few clusters give weak uncertainty. This measures **intent exact match only**, not the primary graph-backed request-success metric. No fabricated model predictions or performance report are supplied. An identical-prediction test checks arithmetic only.

## Next execution gates

1. Review/quarantine ambiguous or duplicate candidates; expand original compositional families with recorded lineage, then human-review labels. Do not inflate count with trivial paraphrases.
2. Author separate development/test graph families; independently review expected actions and feasibility. Freeze manifest/hashes before baseline. Current authoring sees all candidate labels; nothing here is advertised as untouched test data.
3. Install/lock SDK + Cookbook in a functional isolated Python environment; verify candidate commit and model renderer. Build provider runner with bounded retries, raw output/timing/usage records and explicit run identity; malformed/truncated model output counts as failure.
4. Render/tokenize offline, inspect masks and final-batch accounting; estimate cost. Once account access and credits/spend cap are confirmed, run base-model smoke and benchmark before SFT. Key availability alone does not authorize billable work.
5. Score base/tuned identically through the fixed graph validator and gold constraints. Add graph-backed paired request-success reporting before claiming contest improvement.

Terrain review, a third credible loop and competition presentation remain separate pending workstreams. No public deployment or on-snow validation has happened.


## Earlier access and complete-action evaluation checkpoint — 2026-10-06 (401 superseded below)

The Tinker key is now in OpenClaw's protected store, restricted to `tinker.thinkingmachines.dev`, and protected egress is enabled. Read-only capabilities checks returned **HTTP 401**, including the repeatable `python3 -m liftlap.access_check` probe run through Gateway exec. Access is not verified; no billable model calls occurred. The probe has a fixed HTTPS endpoint, refuses redirects, uses inherited proxy/CA settings, and never prints credentials, raw response bodies or exception strings. Native shell does not inherit the protected key; use Gateway exec. No key is in this repository.

Tinker SDK's current `ApiKeyAuthProvider` validates a `tml-` or JWT prefix locally, whereas protected egress supplies an opaque sentinel. Before implementing the authenticated SDK runner, verify a supported auth-provider integration that preserves the sentinel until HTTPS egress. Do not extract the real key, weaken TLS, or put it in plaintext to work around this. Source inspected: https://github.com/thinking-machines-lab/tinker/blob/main/src/tinker/lib/_auth_token_provider.py (2026-10-06; mutable upstream). Exact SDK versions still need locking.

`benchmark/request-development.json` extends the original eight route scenarios with eight clarification and four unsupported requests. Use:

```bash
python3 -m liftlap.evaluate --scenarios benchmark/request-development.json --predictions /path/to/request-predictions.jsonl
```

Predictions are keyed by scenario ID. Correct nonplanning intents are scored without calling the planner; route outcomes still require exact gold semantics and independent gold route validation. Invalid/missing outputs remain failures. Reports include outcome slices and graph/scenario hashes. Malformed duplicate scenario IDs or expectations inconsistent with gold status fail closed. This intentionally conservative success definition requires full normalized intent agreement, including preferences; it does not accept semantically equivalent alternative labels.

[Self-check](../research/evidence/request-evaluator-self-check.json): 20/20 gold-label fixture replay; **not model accuracy, human-reviewed test results or terrain verification**. Original eight-case fixture is preserved. Paired route-success uncertainty, new graph families, independently reviewed holdout and the actual provider runner remain pending. The existing paired comparison CLI still measures intent exact match only.


## Current readiness checkpoint — 2026-10-06

**Authenticated capabilities check succeeded: HTTP 200, 31 listed models, including Qwen/Qwen3-8B.** Protected credential replacement resolved the earlier 401. No training/inference or billing check was performed. The checked-in access evidence now reflects success, and only `account_access_verified` was changed in the training plan.

Credential replacement lesson: `openclaw secrets store set NAME --allow-host HOST` on an existing secret changes host policy only, even if `--kind secret` is supplied. To replace interactively, first run `openclaw secrets store set TINKER_API_KEY --kind secret` and enter at the no-echo prompt, then set the allowed host separately. Never place values in a command argument or tracked file. Gateway exec snapshots refresh on a new turn.

### Full-request baseline and paired comparison

The untouched rules-v1 adapter now has saved predictions for all 20 scenarios:

- Feasible routes: 4/4 successful.
- Infeasible scenarios: 4/4 successful.
- Clarification: 4/8 successful.
- Unsupported features: 2/4 successful.
- Total: **14/20 on visible development fixtures**, not held-out accuracy. Labels were visible during parser development, and these fixtures all share one synthetic graph. No base-model or tuned-model result exists.

Artifacts: `benchmark/rules-v1-request-predictions.jsonl` and `research/evidence/rules-v1-request-development.json`. Reproduce:

```bash
python3 -m liftlap.evaluate --scenarios benchmark/request-development.json --predictions benchmark/rules-v1-request-predictions.jsonl
python3 -m liftlap.request_compare /path/to/base-request-predictions.jsonl /path/to/tuned-request-predictions.jsonl
```

The paired CLI independently runs both prediction sets against fixed gold semantics and graph fixtures, retains improvements/regressions, slices by expected outcome, reports gold-route rejections and search-limit counts, and computes a deterministic paired family-cluster bootstrap interval. Shared-graph dependence and development exposure are explicit caveats; do not use this small fixture set to claim generalization or a contest-winning gain. Missing predictions fail. No cherry-picking or automatic significance-based reruns.

### Offline preflight

```bash
python3 -m liftlap.training_preflight benchmark/development-seed.jsonl benchmark/training-candidates.jsonl
```

Exit 1 means blocked (the expected current result). Checks corpus audit, required partitions, reviewed training labels, explicit launch gates, positive integer batching/epoch/length settings, assistant-only supervision and disabled Cookbook row-splitting. Zero batches and silently dropped final-batch rows block. Input hashes make the report reproducible.

This checker **never authorizes spend or launches training**, even if every declaration is true. Boolean gates are not evidence: independently inspect linked test-freeze provenance, rendered token masks, dependency smoke, baseline run and credit/spend records. Current blockers include the near-duplicate candidate, no approved training rows/test partition, unverified rendering/environment and no approved budget. See `research/evidence/training-preflight.json`.

Next: expand/review original training families and create new independently reviewed evaluation graph families; install and lock a supported SDK/rendering environment; validate sentinel-compatible SDK auth before any billable call. Training data readiness—not access—is now the main project bottleneck.


## SDK and candidate-review milestone — 2026-10-06

Current corpus: **48 original AI-assisted training candidates** (32 added this checkpoint) plus the unchanged 32 development seeds. Still no approved training split or frozen independent test set. The new cases cover compositional ceilings/preferences, negative scope, corrections, known/unknown place IDs, 15/240-minute boundaries, deadline caps, missing fields and conflicting instructions. They are not duplicated paraphrases to reach a count target; 48 remains well below the planned corpus size. Agent review is not human review.

[Review packet](review-packet.md) includes each request, full context/catalog, proposed label and pending reviewer decision. Regenerate with `python3 -m scripts.review_packet`; changing checkboxes is not an approval importer. Candidate 009 remains quarantined for cross-split similarity. Review decisions/corrections must be recorded in canonical JSONL before approval and export. Corpus/evidence hashes were regenerated.

### Installed SDK environment

A separate ignored `.venv-tinker` uses Python 3.14.4 with `tinker==0.32.0`. Full installed package versions are in [sdk-requirements.lock](sdk-requirements.lock); this is a version lock for the verified Linux environment, not a cross-platform or distribution-hash lock. No global Python changes or model weights were installed. Core application still has no third-party runtime dependencies.

Bootstrap used uv 0.12.23's PyPI Linux wheel, verified against SHA-256 `565c6e2874dbeae86c02f3dea97255e878fec672659a73d4930c6b93fcab2fff`. The temporary executable is `/tmp/liftlap-uv`, not a required checked-in artifact. With that uv version available, reproduce:

```bash
uv venv .venv-tinker --python python3.14
uv pip sync --python .venv-tinker/bin/python training/sdk-requirements.lock
.venv-tinker/bin/python -m unittest discover -s tests -v
```

`liftlap.tinker_sdk` performs only the SDK capabilities read. **Live smoke passed**, lists 31 models including Qwen3-8B. It accepts only an opaque Gateway sentinel and configured egress proxy; it refuses plaintext credentials, fixes the Tinker HTTPS origin, preserves CA verification, disables redirects and automatic retries, and suppresses exception bodies. Run through OpenClaw Gateway exec, not native shell:

```bash
.venv-tinker/bin/python -m liftlap.tinker_sdk
```

The integration intentionally uses pinned SDK internals (`AsyncTinker._auth` / `AuthTokenProvider`) because its normal API-key constructor rejects opaque sentinels. This is a **private compatibility seam**, not an upstream-stable API. It fails on SDK version changes; revalidate before upgrading. It does not patch the installed SDK or retrieve/decrypt the real key. Live nested model entries arrived as dictionaries despite type annotations; the adapter supports dictionaries and model objects. Unit tests cover credential mode, destination and redirect refusal; live capability proof is stored separately. Pydantic deprecation warnings may still arise inside SDK mock tests.

This does **not** yet implement high-level `ServiceClient`, sampling-session creation, token rendering/masking, LoRA training, checkpoints or usage accounting. The Cookbook training environment is not installed. The broad `dependency_versions_locked_and_smoked` training gate therefore stays false. Next work is an isolated Cookbook/rendering environment and full provider runner, followed by baseline measurement only when data and spend gates are satisfied.
