# R03: versioned granular scoring and promotion gates

Offline implementation checkpoint, 2026-10-08. **No new provider calls, model promotion, runtime/UI changes or spending.** [Metric/manifest and gate contract](../../../technical/granular-evaluation-v1.md).

## Saved evidence

- [Pilot base](pilot-base-report.json): 16 assigned cases; 9 task successes.
- [Pilot tuned](pilot-tuned-report.json): 16 assigned cases; 7 task successes.
- [Fresh base](fresh-base-report.json): 16 assigned cases; 13 task successes.
- [Attempt inventory](attempt-inventory.json): all three named saved runs, 48 assigned case attempts. These include two different evaluation sets; pooled counts are accounting, **not a paired performance comparison**.
- [Machine-readable decision](promotion-decision.json): **retain_base**. Historical runs predate the policy, have missing provenance and are diagnostic rather than eligible validation runs; the tuned candidate also fails performance/schema/safety gates. No fresh final test was run.
- [Provenance](provenance.json): source hashes and historical reservation scope. Reconciled costs remain unknown; the shared training experiment reservation is not double-counted across sampling arms.

Per-run manifests and old-versus-new comparison files sit beside each report. Historical 9/16, 7/16 and 13/16 counts reproduce unchanged with the original scorer; the new diagnostics are separately versioned. Full field, exclusion-set, semantic, transport, route, latency/token and family/scenario details are in JSON reports. Existing raw predictions, approved labels and frozen protocols are unchanged.

## Limits and next work

No remote repeatability experiment was run. All-failed and consistently-wrong repetition are tested locally with saved/synthetic fixtures. Old unknown renderer/environment/provider version metadata is null, not reconstructed as historical fact from today's installation. Do not treat a report hash as signed evidence or a simulated gold-route rejection as a live safety interception.

The gate checks report/evidence consistency but cannot independently prove a supplied inventory includes every remote attempt or that a policy was frozen before execution. M03 must bind these to its predeclared journal and reservation; R02 supplies the mandatory regression suite. R01 remains next for runtime semantic/provenance validation. These gates do not activate terrain or certify field safety.

## Reproduce

Run from repository root with Python 3.11+; no optional model packages needed:

```sh
python3 scripts/score_robustness_history.py --output /tmp/touch-grass-r03-new
python3 -m unittest discover -s tests -p test_evaluation_v3.py -q
python3 scripts/check_release.py
```

The output directory must not already exist. Generated JSON is compact to keep complete per-family metrics manageable. Use `python3 -m json.tool PATH` for expanded reading.

## Verification

- Fourteen focused scorer/gate tests pass, including exact regeneration of every saved JSON artifact.
- Full dependency-free release suite passed (210 tests, 25 optional skips before the final artifact-reproduction test was added); saved base replay remains 13/16, and isolated/deterministic packaging passes.
- Pinned optional environment passed all 210 tests without skips; the additional artifact-reproduction test passed separately in the dependency-free environment.
- Documentation links and whitespace checks pass. No visible app changes; screenshot refresh is not required.
