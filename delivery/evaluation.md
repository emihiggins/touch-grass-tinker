# Fine-tuning and evaluation protocol

Status: [32-case development seed and offline intent scorer](../benchmark/README.md) implemented; no final training/test splits, graph-backed benchmark or model calls yet. Freeze version 1 before baseline measurement. This file owns numeric experiment targets; [requirements](../product/requirements.md) owns acceptance traceability.

## Hypothesis and task

Tinker SFT on an open-weight model improves faithful ski-request interpretation, especially hard versus soft constraints, exclusions, corrections, ambiguity and place aliases. The graph solver remains fixed for all adapters. Never score only whether a planner can satisfy the model's own extracted intent: compare with independently authored gold intent and scenario.

Candidate: Qwen/Qwen3-8B, same `qwen3_disable_thinking` renderer for baseline and tuned. Choose after access/license/credit confirmation and a 10-example parse smoke. Do not switch to a weaker baseline after observing strong results. Qwen3.5-4B is an alternative only if an explicitly motivated comparison is added; current listed token prices are higher.

## Corpus

Start with 1,200 train / 150 development / 200 frozen test cases. Reduced-scope fallback: 400 / 80 / 100, explicitly disclosed with wider uncertainty. These are targets, not existing assets.

Each JSONL record: id, split, family_id, graph_family_id, request_text, ui_context, catalog, scenario_id/hash, gold_intent, expected_action (`plan|clarify|unsupported|infeasible`), gold_required_fields, author/provenance, reviewed flag. All examples get schema validation; manually review every development/test case and at least 10% of training examples stratified by family. Keep a separate original language corpus and licensed terrain artifacts; do not silently relabel OSM-derived records as unrestricted.

Coverage across all splits: simple requests, hard/soft difficulty, surface-lift distinctions, negative scope, corrections, relative/absolute deadlines, place aliases, ambiguous/missing fields, conflicting requirements and requests for unavailable terrain features. Include feasible and independently provable infeasible graph cases. Never make every difficult prompt infeasible or correlate one phrase with one answer.

Split graph/template/paraphrase families BEFORE expanding examples. Synthetic train graphs and place names differ from held-out synthetic graphs. Real audited-sector cases form a separate transfer slice; names/catalog are supplied at inference, not memorized. Deduplicate normalized texts and review near-duplicates across splits. Final test file is hash-locked and not used in prompt/model/hyperparameter selection.

Expected-action nuance: clear but impossible constraints are `ready` intent followed by an infeasible planning outcome, not language ambiguity. Unsupported “quietest snow” or “shortest queues right now” cannot become fabricated graph attributes. A human-authored rubric fixes accepted interpretations of phrases before testing.

## Comparators and training

1. Deterministic rules parser with honest supported vocabulary and abstention.
2. Same pretrained instruction-capable model with a carefully developed prompt/schema and examples selected ONLY on development data.
3. Same model/renderer/prompt/decoding with Tinker LoRA weights.

Proposed first SFT configuration: rank 16, batch 32, one epoch, learning rate 1e-4; these are starting hypotheses, not experimentally validated settings. Train assistant target tokens only using Cookbook conversation-file builder; inspect rendered/masked examples before launch. Save checkpoint and resume metadata. Maximum two planned configurations selected on development performance (second may use two epochs or LR 5e-5, not an uncontrolled sweep). Tokenize to estimate real usage before launching. Stop if access/credit/spend cap is unverified.

Primary experiments share maximum output 512 tokens and temperature 0 (or smallest supported deterministic setting), prompt token budget and timeout. Truncations/invalid JSON are failures, not retried until correct. Record all retries separately. API availability failures are reported separately from semantic accuracy; replay failed calls under a documented fixed retry policy, never drop hard cases.

Optional RL comes only after SFT and a trustworthy scorer, with available time/credits. A reward must check gold constraints, correct clarification and no unsupported additions; valid JSON alone or any feasible route is not sufficient. No RL required to complete the entry.

## Metrics and honest success target

Primary: **request success** on the full test set, stratified by expected action. Planning requests require exact hard-constraint semantics and a validated route satisfying gold intent; clarification requires the correct missing/conflicting fields; unsupported requests must not invent capabilities. Proven infeasible fixtures require correct interpretation and correct infeasibility outcome. Keep heuristic-search failures separately visible.

Secondary: exact normalized intent match, per-field precision/recall, hard-constraint violations, unnecessary clarification, unsupported-ID rate, invalid/truncated JSON, route validator defects, and preference fulfillment. Count invalid output as failure. Report numerator/denominator per slice and representative failures, not only aggregate accuracy.

Project target (not contest rule): at least +10 percentage points request success over the prompted same-base model on 200 held-out cases, with a paired bootstrap 95% interval whose lower bound is above zero; no increase in hard-constraint violations. If target fails, report that honestly; use development data for the next change and obtain a new untouched test if prior test inspection influences development. Do not keep rerunning until significance appears. A same-quality latency/cost improvement can be a separate preregistered experiment, not a post-hoc replacement headline.

Latency/cost: use interleaved base/tuned order, identical service conditions, at least 50 paired requests repeated three times after documented warm-up. Report p50/p95, sample size, input/output tokens, cache effects and actual billable usage. Keep training cost separate from per-request inference cost. These are hosted-service measurements, not claims about on-device performance.

Artifacts: split manifest/hashes; model/SDK/Cookbook versions; renderer and prompt; training config; run/checkpoint IDs; raw predictions; per-case scorer output; aggregate metrics and paired uncertainty; actual cost ledger; run timestamps. Redact credentials. One pure scorer must reproduce results from saved predictions without a model call.

## Stop/go gates

- If prompted baseline is already near ceiling, improve task relevance/benchmark difficulty on development data or pivot before training; do not handicap the baseline.
- If rules parser is as good, disclose it and assess whether customization adds real value.
- If graph defects dominate outcomes, fix/re-freeze graph and rerun every adapter consistently; do not attribute graph repairs to fine-tuning.
- The demo must display a real tuned run or explicitly labeled recorded run with provenance. No invented training, on-snow use or savings.
