# M02 initial review packet — 2026-10-08

This is a small **TRAINING candidate** packet (12 rows), generated offline for Emi review. It is same-agent authored, fictional, and seed-derived; it is not an independently authored holdout and must not be described as human-reviewed. The labels are provisional and all rows are `human_reviewed: false`, `decision: pending`.

- `training-review-packet.jsonl` is the review surface; no row is approved for training.
- `iteration-manifest.json` is the preserved original m02-1 report, superseded by `iteration-manifest-v2.json`. Its graph-hash and boundary claims were overstated; see the repair notes below.
- Candidate, validation/development, and final boundaries are reserved in the manifest. Existing `benchmark/v2` evaluation files remain historical/frozen and are not copied into a holdout.
- Review must confirm the request, UI context, catalog/graph, expected intent, and any edge behavior. Approval must bind all current hashes; unresolved or changed rows stay out of export.

Known limitation: this first packet is coverage-oriented and intentionally too small for training. The manifest reports missing/sparse categories; it makes no representativeness claim. No provider calls, API keys, personal trip data, paid work, or training run were used.

## M02 isolation and audit repair

The five R03 reproducibility failures reported by PR #32 were introduced by that
checkpoint, not pre-existing: adding M02 helpers changed the hash-bound historical
`liftlap/corpus.py`. The repair restores that module byte-for-byte to its pre-M02
version and isolates review diagnostics in `liftlap/corpus_m02.py`. Frozen R03
reports, predictions, labels and scores are not regenerated.

The revised **m02-2** manifest preserves audit errors, groups split aliases into
training/development/final partitions, detects declared family and historical-source
cross-partition reuse, and reports packet-limit violations. Approval metadata must
use `approval_version: m02-2`, identify a reviewer, and bind canonical JSON of all
row fields except `review` via `approval_hash`. Changing lineage, split, graph or
constraints invalidates that approval. This is a tooling check, not human review.

There is **no M02 training exporter** in this checkpoint. Neither a manifest nor
an approval flag authorizes export. All 12 rows remain blocked and unapproved.
Legacy corpus exports continue to reject the new candidate split names.

No graph is supplied in these rows: `graph_sha256` is now null, and the old hash
is correctly named `catalog_constraints_sha256`. The 12 distinct declared family
IDs do not establish 12 independent families or graph diversity. These rows use
legacy intent-v1 labels and merely prefix existing seeds with “Draft M02 wording:”.
They require a lineage-correct, intent-v2, blind-first replacement packet before
requesting label review. Unsupported intents, missing budgets and positive routes
remain absent. A full-source-corpus overlap audit is still required before a freeze;
within-packet checks cannot establish independence from unseen rows.

Reproduce the revised report (offline):

```python
import json
from pathlib import Path
from liftlap.corpus import read
from liftlap.corpus_m02 import iteration_manifest
root = Path("benchmark/iterations/m02-2026-10-08")
report = iteration_manifest(read(root / "training-review-packet.jsonl"))
assert report == json.loads((root / "iteration-manifest-v2.json").read_text())
```

### Repair verification

- Standard-library release suite: 239 tests run, 25 optional skips, no failures.
- Pinned optional environment: all 239 tests passed, no skips.
- All five historical R03 artifact comparisons reproduce exactly again.
- Revised M02 manifest reproduces exactly; approval mutation, partition alias,
  source-lineage overlap, duplicate/error propagation, graph absence and packet-limit
  fixtures pass.
- Saved fresh-base result remains 13/16; isolated package built twice identically.
- No model calls, training, label approvals or frozen artifact modifications.
## Review tooling added after m02-2

`scripts/m02_review.py` now produces a versioned offline report and exposes the only M02 export path. It checks candidate rows against the full source corpus for historical-source and normalized request/context/catalog overlap. Export is fail-closed: it accepts only `train_candidate` rows with intent-v2, current `m02-2` human approval, exact current hashes, no audit or near-duplicate errors, and no source overlap. It never approves rows or calls a provider.

The current 12-row packet remains intentionally blocked. Reproduce its report with:

```bash
python3 scripts/m02_review.py \
  benchmark/iterations/m02-2026-10-08/training-review-packet.jsonl
```

The command exits non-zero while review is pending; this is expected. A future reviewed packet must carry intent-v2 labels and be checked with `--source` paths for every candidate/development/final source corpus before any export.
