# Starting execution plan

This is a setup-stage handoff, not a complete implementation specification. [Research](../research/challenge.md) owns contest facts; the [product brief](../product/brief.md) owns the selected Lift-Lap Planner direction; [data research](../research/data-sources.md) owns source findings.

## Ordered milestones

1. **Task and access:** refine the selected skier language-to-constraints task; confirm Tinker access, available free credits, a suitable open-weight model/license, and the training budget. Do not incur paid usage without authorization. Run a tiny sampling/training/checkpoint smoke test before a full study.
2. **Benchmark first:** author licensed or original examples with provenance. Split by scenario family before training; freeze a held-out test set and deterministic scorer. Evaluate a competently prompted base model, not an artificially weak baseline. Keep test data out of training and model selection.
3. **Fine-tune:** adapt an official Cookbook recipe. Start with SFT/LoRA; introduce RL only if a reliable reward and time justify it. Record versions, model ID, dataset hashes, hyperparameters, seed, checkpoint, run duration and actual usage.
4. **Compare:** run baseline and tuned models on identical test inputs, prompt/rendering policy, decoding limits, hardware/service and measurement conditions. Save raw responses and scorer output. Report task success and failure breakdowns, sample size and uncertainty; repeat latency measurements and separate training cost from inference cost. Include a deterministic non-model comparator where applicable. A gain over the base model alone does not prove the task needs AI.
5. **Outdoor demo:** implement the smallest experience that uses the tuned model and minimizes screen time. Demonstrate actual use outside and document failures. Until validated, describe all capabilities as planned.
6. **Submission:** write a clear evidence-led story, supply reproducible instructions and benchmark artifacts, credit dependencies, settle code access/license, verify eligibility and publish before the deadline. Public release and submission are not authorized by the initial private-repo setup request.

## Evidence gates (not yet passed)

- [ ] A real Tinker fine-tuning run and its checkpoint are traceable to versioned training data and configuration.
- [ ] Held-out results demonstrate a clear performance, latency or cost improvement over the disclosed baseline; no invented numbers or cherry-picked-only evidence.
- [ ] Tests exercise task constraints, invalid inputs and degraded behavior; product requirements and measurable thresholds are fixed before implementation.
- [ ] The application actually uses the tuned model, with a reproducible end-to-end demo.
- [ ] An outdoor trial supports the screen-time and usability story; any offline claim is tested in airplane mode.
- [ ] Publication artifacts satisfy the linked contest requirements and are accessible to judges.

## Open decisions and risks

Product concept is selected; model, final dataset/resort, stack, application license and hosting remain open. Tinker credentials/credits are an execution gate, not a blocker to repository setup. Primary risks are negligible fine-tuning gains, data leakage, weak AI necessity, limited time, and an underdeveloped write-up. Reserve the final day for evidence and writing; cut features before cutting evaluation.
