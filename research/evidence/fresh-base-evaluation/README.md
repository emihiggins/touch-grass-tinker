# Fresh base-model evaluation

Emi approved all16 labels (Telegram message2415). Cases and graph bundle were frozen and the fixed base-only plan committed at d97f0bd before inference. Qwen/Qwen3-8B, unchanged v2 prompt, temperature0, seed20261006, maximum512 output tokens. No training or final-output-driven tuning.

- End-to-end exact successes: **13/16**.
- Schema-valid outputs: **16/16**.
- All16 cases retained in denominator; no transport failures.
- 005: excluded magic carpet but omitted other surface lift types. Matching no-route outcome alone does not count as correct intent.
- 010: unnecessarily asked to clarify duration for an eight-minute outing.
- 012: retained45minutes where requested duration was unspecified; expected null.

Small fictional set authored by the same project agent and reviewed independently by the owner. Not statistically representative, not field safety validation, and not a fine-tuning comparison. The trained model was rejected on the separate pilot and was not evaluated here. Do not compare13/16 here to9/16 on different pilot cases as improvement.

$0.05 reserved for this run; token upper estimate$0.00985728. Total project holds$1.65, not confirmed charges. No checkpoints created. Provider IDs remain private in the ignored run directory.
