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


## Renderer / dry-run payload milestone — 2026-10-06

Pinned Cookbook commit `1c03a20fdda98156ccbec15728c0e2764b5a0bc3` is now installed in `.venv-tinker`, with CPU-only PyTorch 2.10.0 and compatible Transformers 5.5.4 (downgraded from the SDK-only environment's 5.18.0). Use **render-requirements.lock** for this expanded environment; sdk-requirements.lock describes the earlier SDK-only checkpoint. `uv pip check` passes. Expanded venv is about 1.3 GB; tokenizer assets are about 16 MB, both ignored. No model weights were downloaded.

Qwen3-8B tokenizer revision: `b968826d9c46dd6066d109eabc6255188de91218`, with every asset's size and SHA-256 in `tokenizer-manifest.json`. No remote tokenizer code is executed. The rendering audit uses only local checksum-verified assets and verifies the installed Cookbook commit.

```bash
# Linux x86_64 / CPython 3.14: CPU torch wheel is platform-specific.
uv pip sync --python .venv-tinker/bin/python training/render-requirements.lock
python3 -m scripts.fetch_tokenizer
.venv-tinker/bin/python -m liftlap.render_audit benchmark/training-candidates.jsonl --preview-datums runs/dry-run/candidate-datums.jsonl
.venv-tinker/bin/python -m liftlap.render_audit benchmark/development-seed.jsonl
```

The lock contains an exact CPU wheel URL/hash and a pinned Cookbook Git commit; other packages are version-pinned, not artifact-hash-locked. Resolution was dry-run checked against the installed environment; clean-machine reproduction remains untested.

### Measured local rendering results

| Corpus | Cases | Maximum full sequence | Maximum answer | Total sequence tokens |
| --- | ---: | ---: | ---: | ---: |
| Training candidates | 48 | 763 | 134 | 35,755 |
| Visible development | 32 | 748 | 130 | 23,441 |

All 80 pass the 2,048-token sequence and 512-token answer limits without truncation. Each passes exact train/inference prompt-prefix equality, JSON-plus-stop-token round trip, zero prompt-token loss, correct next-token input/target shift and normalized loss weights. These are **token/mask tests**, not trained-model quality or cost measurements.

**Important mode correction:** The initial `all_assistant_messages` mode also supervised four tokens belonging to the assistant's supplied empty-thinking marker. For our one-assistant-turn format, Cookbook `last_assistant_message` excludes that prompt framing and trains only the JSON plus stop token. The plan now uses this mode. This is an intentional training-contract change; keep it identical across future rendering and training. Our preflight accepts either assistant-only mode generally, but the pinned render-audit CLI requires `last_assistant_message` to match this verified path.

Dry-run payloads contain input token IDs, target token IDs and normalized weights for all candidate rows. They are local **preview data**, not a serialized SDK wire request or an approved training export. Candidate labels are still unreviewed, and no provider submission occurs. The reports retain exact corpus/prompt/config/tokenizer hashes; any change requires rerendering. Reported batch size 32 leaves 16 candidate rows over after one full batch; actual launch must resolve batching after the approved dataset is finalized, never silently drop these rows.

Evidence: `research/evidence/render-audit-candidates.json` and `render-audit-development.json`. All 84 tests pass in the expanded environment; the dependency-free suite passes with eight optional tests skipped. A known upstream Pydantic deprecation warning remains in SDK tests.

### Remaining milestone boundary

This closes **current-corpus token rendering and dry-run payload preparation**, not the production training/sampling runner. The final training gate remains false until approved data and its exact hashes pass the same checks. Human label review, a new independent held-out corpus, budget/credits, high-level SDK session integration, checkpoint/resume, bounded job execution and usage accounting remain. No paid API operations were invoked.


## Sampling runner checkpoint

The [bounded sampling runner](sampling-runner.md) is now implemented and mock-tested, with a real local 20-case dry-run manifest. No live inference or training was executed. A concrete baseline-smoke cost estimate and proposed inference-only budget are documented there. Training and checkpoint/resume remain unimplemented.


## Approved live baseline smoke completed

The first [live sampling smoke](sampling-runner.md) completed after session/backpressure integration fixes: 6/20 strict request successes, 11/20 schema-valid outputs; estimated completed-run token charges $0.00388 before cache discounts, invoice unverified. No training ran. This weak development-only prompt must be improved before freezing the formal comparator; no final baseline or held-out result is claimed. Raw outputs and setup failures are retained under `research/evidence/base-dev-smoke/`.


## Prompt-v2 development checkpoint — 2026-10-06

Following Emi's request to update and continue (message 2298), performed one additional 20-case inference-only development run within the $1 budget. No training or unattended experiment loop. `benchmark/baseline-prompt-v2.txt` reorganizes the existing rules into UI-default/explicit-override precedence, complete output schema, enum restrictions and final consistency checks, with one fictional full example. It was written after inspecting v1 errors and gold labels. Original prompt and all v1 results are preserved unchanged.

The runner now accepts `--prompt` and records its selected file/hash plus the runner code hash. Its default remains the original prompt for historical command compatibility; explicitly pass `--prompt benchmark/baseline-prompt-v2.txt` for v2. No answer postprocessing changed. Model, tokenizer, renderer, temperature, seed, max output, graph and gold labels remained fixed. Only prompt changed.

**Result:** 13/20 full-request successes versus v1 6/20; schema-valid outputs 15/20 versus 11/20. Nine cases improved, two regressed, four stayed successful and five stayed unsuccessful. All eight routing outcomes pass; clarification 2/8, unsupported capabilities 3/4. Rules-v1 remains 14/20. Remaining errors include missing clarification flags, unknown-finish handling, conflicting grades and out-of-range duration. The prompt is only a provisional development choice, not a frozen final comparator.

Artifacts: `research/evidence/base-v2-development/` retains raw outputs, event IDs, hashes, outcome report, paired comparison and field differences. Paired bootstrap output is descriptive only because the exact cases informed prompt development. It is **not evidence of generalization, statistical significance for a final experiment, or a Tinker fine-tuning gain**. We did not rerun to remove regressions or reach a desired score.

Cost estimate: v2 inputs 24,959 tokens, outputs 1,894 tokens; $0.006003405 at uncached rates. The two completed inference runs total about **$0.00988101** before cache discounts. Invoice and rejected-submission charges remain unverified. See `research/evidence/inference-ledger.json` for budget/provenance. No training spend was incurred by these calls.

The 48 candidate records also pass rendering with prompt v2, including zero prompt loss and no truncation (`render-audit-candidates-v2.json`). Prompt v1 rendering evidence remains. Gold labels, training eligibility and the independent-test gate are unchanged.

Reproduce without API calls:

```bash
python3 -m liftlap.evaluate --scenarios benchmark/request-development.json --predictions research/evidence/base-v2-development/predictions.jsonl
python3 -m liftlap.request_compare research/evidence/base-dev-smoke/predictions.jsonl research/evidence/base-v2-development/predictions.jsonl
```

Next useful work: review the known ambiguous labels, create an independent evaluation set with new graph/template families, and implement the training/checkpoint path. Do not keep spending on this same tiny development set to manufacture a success headline. Human review and training authorization are still pending. Heartbeat settings were not changed.


## Offline batching rehearsal — 2026-10-06

The [Cookbook batch/cursor rehearsal](batch-rehearsal.md) exercises the installed loader using real locally rendered SDK Datums. It refuses the 48/32 tail loss, verifies an explicit 16-row rehearsal override with complete coverage, and binds continuation to data/config/token hashes. It also documents that the installed trainer shuffles by epoch index, not the plan's shuffle-seed field. No remote checkpoint restoration, training authorization or human review is implied. Submission writing and its remaining gates are now in [submission/README.md](../submission/README.md).


## Human review received — 2026-10-06

All 48 rows were reviewed by Emi: 41 explicit approvals (including quarantined 009), 40 non-quarantined approvals and 7 held labels. [Adjudication and contract implications](human-review.md) are current; earlier unreviewed-corpus statements above are historical. Exact notes are retained in canonical JSONL and the generated packet. No gold labels, development labels, model results or canonical split assignments changed. Explicit duration corrections (300 and 10 minutes) require a versioned migration beyond v1's 15–240 constraint. Review/export now binds approval to request/context/catalog/gold and rejects disputed, changed or quarantined records.


### Review follow-up resolved — 20:27 UTC

Emi agreed to the proposed interpretations for 004/005/032/036/043. Current total: 45 approved v1 labels, including quarantined 009; 44 non-quarantined approvals. Cases 005/013/028 require the agreed soft-avoidance/duration migration; no more clarification is needed from Emi for this batch. Earlier review counts are historical.


## Staged spending authorized — 20:31 UTC

Emi approved the recommended **$10 total project Tinker cap**: $1 smoke, $4 for up to two planned configurations plus evaluation, $5 reserve only for a documented justified follow-up. See [canonical authorization](budget-authorization.json); includes prior usage and checkpoint storage, not $10 on top of the old $1. Historical inference-only restrictions above describe earlier checkpoints and are superseded for authorized training scope. Account balance/credits, uncertain earlier charges, data/contract gates and guarded training integration remain unresolved; the combined credits-and-cap preflight gate stays false. No model calls were made to record this authorization. No new approval is needed merely because training is billable within this scope.


## V2 implementation checkpoint

Agreed semantics are implemented across the local app/planner/scorer, and 47 source-reviewed records are deterministically migrated to v2 (009 excluded). See [current checkpoint](../delivery/v2-checkpoint.md) and [evaluation review packet](evaluation-review-v2.md). Older gate/count statements above describe prior checkpoints. No trained model exists.


## Evaluation pilot review received — 21:09 UTC

Emi reviewed all 16 cases: 14 approved, preferred_difficulties=["blue"] requested for 009/010. Notes are stored verbatim in the evaluation rows and packet. Current gold remains unchanged while reconciling hard-vs-soft field semantics; no freeze or model scoring. The two requested changes can alter the planner unique-distance objective, not only display. No second review of the other 14 is needed.


## Current checkpoint — green/blue clarification resolved

Emi clarified the two requested blue preferences at 21:16 UTC. All 16 pilot labels are resolved; immutable scoring inputs are `benchmark/v2/evaluation-pilot-frozen.jsonl` and `evaluation-pilot-freeze.json`. This is a small human-reviewed pilot, not an untouched final benchmark. Original case 035's v2 migration now follows the same “keep it blue” interpretation; its v1 source is unchanged.

V2 supports normalized green < blue < red < black. Real resort colors must be mapped explicitly and reviewed; this ordering does not establish equivalence across countries. No real green terrain has been added. A blue maximum permits green; a blue target additionally prefers blue. A maximum alone still does not imply a preference or variety.

`liftlap.spend.Ledger` stores atomic persistent project/stage commitments using standard-library SQLite. Prior usage must be reconciled first. New sampling runs require `--project-ledger` and reserve the full estimated token cost before provider submission; ambiguous/finished calls retain reservations until verified billing settlement. Never delete or copy the ledger to regain headroom. Existing historic calls have not been imported as verified charges. This is local control, not a provider hard cap. Reserve-stage justification, two-configuration experiment counting, checkpoint storage bounds, and remote training/checkpoint integration remain outstanding; the ledger alone does not make training launchable.


### Remote training transport

[Remote smoke checkpoint](remote-smoke.md) documents the implemented SDK transport, offline wire tests and remaining metered-launch/billing gates. No real training or checkpoint calls have run.


## Full-data trial01 complete

[Preregistration](experiment-01.md) and [all paired evidence](../research/evidence/experiment-01/README.md): base9/16, trained7/16. Single configuration,47rows per batch,3steps, no tuning loop. Candidate selection remains base. [Fresh16-case review](final-review.md) is the next human gate, not a repeat pilot review. Total commitments$1.60 against$10cap; invoices unresolved.
