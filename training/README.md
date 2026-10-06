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
