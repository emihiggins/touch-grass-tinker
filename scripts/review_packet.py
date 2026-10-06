"""Generate a readable label-review packet without promoting any training rows."""
import json
from pathlib import Path
from liftlap.corpus import read

def main():
    cases=read('benchmark/training-candidates.jsonl')
    lines=['# Training candidate review packet','',
           'All rows are AI-assisted candidates. Human review is pending. Editing this packet does not update labels or mark rows approved.',
           '', 'For each case check: explicit request versus UI defaults; hard/soft difficulty; lift exclusions; deadline math; clarification/unsupported codes. Record corrections in the canonical JSONL and re-run corpus audit.',
           '', '**Quarantine:** candidate 009 overlaps development wording; exclude or revise with fresh lineage before approval.',
           '', 'No held-out examples appear here. No route feasibility is labeled.']
    for c in cases:
        lines += ['',f'## {c["id"]} — {c["family_id"]}', '', '- [ ] Human reviewed', '- Decision: pending', '- Reviewer/corrections:', '',
                  '**Request:** '+c['request_text'], '', '**UI context:**', '```json', json.dumps(c['ui_context'],indent=2), '```',
                  '', '**Catalog:** '+ '; '.join(f'{p["id"]}: {p["label"]} (aliases: {", ".join(p["aliases"])})' for p in c['catalog']),
                  '', '**Proposed label:**', '```json',json.dumps(c['gold_intent'],indent=2),'```']
    Path('training/review-packet.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
