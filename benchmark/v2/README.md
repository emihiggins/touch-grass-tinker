# Version 2 data and pending evaluation

- [47 reviewed/migrated training examples](training-reviewed.jsonl): v1 human review plus Emi's approved deterministic duration/soft-avoidance migration. Candidate 009 excluded for development overlap. [Migration manifest](migration-manifest.json).
- [32 migrated development examples](development.jsonl): visible development data, not held out or newly human reviewed.
- [v2 base prompt](baseline-prompt.txt): same-base comparison must use this schema consistently for base and tuned models; prior v1/v2-prompt scores are historical, not v2-contract results.
- [16 evaluation candidates](evaluation-candidates.jsonl), [four original graph layouts](evaluation-graphs.json), [review manifest](evaluation-review-manifest.json), and [human review packet](../../training/evaluation-review-v2.md).

The 16 cases are a **small review pilot**, not the originally planned 100–200-case final benchmark. Same project agent authored their labels; human review is complete: all 16 resolved, with a frozen pilot artifact. Their wording/topologies differ from training/development, but this alone does not establish statistical independence. Do not fine-tune or select prompts on these candidates. If they are used for tuning, relabel them as development and author a new untouched evaluation set.

During fixture construction, the disconnected-finish case exposed the reference search returning a search-limit result after exploring irrelevant loops. A general directed-reachability precheck was added before any freeze/model evaluation. Thus this pilot influenced planner development and must not be called wholly untouched. Preserve that provenance in any later report; stronger claims need a fresh final set.

Current checks establish schema validity, family/text separation, valid authored example routes, and expected simulated graph outcomes. A 16/16 gold self-check is **not model accuracy**. The evaluator refuses model scoring until test rows are human-approved; final freeze must pin full rows AND graph/scenario bundle hashes, not only the intent-review hash.

```bash
python3 -m scripts.migrate_v2
python3 -m liftlap.corpus benchmark/v2/training-reviewed.jsonl benchmark/v2/development.jsonl benchmark/v2/evaluation-candidates.jsonl
python3 -m liftlap.evaluation_v2 --fixture-self-check
.venv-tinker/bin/python -m liftlap.render_audit benchmark/v2/training-reviewed.jsonl --prompt benchmark/v2/baseline-prompt.txt --config training/sft-plan-v2.json
```

`training/sft-plan-v2.json` uses batch size 1 to make a bounded integration smoke possible without dropping the 47th row. This is not a final hyperparameter recommendation. The training runner and global budget accounting remain incomplete; a configuration file and valid rendered datums are not a trained checkpoint.


### Resolved pilot and supported grades

All 16 reviews are resolved, including blue preferences for 009/010 following Emi's green-run clarification. Use `evaluation-pilot-frozen.jsonl` with `evaluation-pilot-freeze.json` for pilot scoring. Source review records remain in `evaluation-candidates.jsonl`. The freeze binds the exact case and graph contents, not a claim of untouched final evaluation. Changes require a new artifact/version, not silent edits to frozen inputs.

V2 permits normalized green below blue; imported real resort grade mappings remain unimplemented/review-required. Tests cover green connectors, blue preference versus ceiling, and red rejection. The fixture self-check is not model performance.
