"""Generate a readable label-review packet without promoting any training rows."""
import json
from pathlib import Path
from liftlap.corpus import read

def main():
    cases=read('benchmark/training-candidates.jsonl')
    lines=['# Training candidate review packet','',
           'All rows are AI-assisted candidates. Human review decisions are recorded below; reviewed does not mean approved. Editing this packet does not update labels or mark rows approved.',
           '', 'For each case check: explicit request versus UI defaults; hard/soft difficulty; lift exclusions; deadline math; clarification/unsupported codes. Record corrections in the canonical JSONL and re-run corpus audit.',
           '', '**Quarantine:** candidate 009 overlaps development wording; label approved by Emi, but training eligibility remains blocked until leakage is resolved.',
           '', 'No held-out examples appear here. No route feasibility is labeled.']
    for c in cases:
        lines += ['',f'## {c["id"]} — {c["family_id"]}', '', '- ['+('x' if c.get('review',{}).get('human_reviewed') else ' ')+'] Human reviewed',
                  '- Decision: '+c.get('review',{}).get('decision','pending'),
                  '- Reviewer: '+c.get('review',{}).get('reviewer','pending'),
                  '- Reviewed at: '+c.get('review',{}).get('reviewed_at','pending'),
                  '- Human note: '+c.get('review',{}).get('human_note',''),
                  '- Agent response (not human approval): '+c.get('review',{}).get('agent_response','None'),
                  '- Quarantine: '+c.get('review',{}).get('quarantine_reason','None'), '',
                  '**Request:** '+c['request_text'], '', '**UI context:**', '```json', json.dumps(c['ui_context'],indent=2), '```',
                  '', '**Catalog:** '+ '; '.join(f'{p["id"]}: {p["label"]} (aliases: {", ".join(p["aliases"])})' for p in c['catalog']),
                  '', '**Proposed label:**', '```json',json.dumps(c['gold_intent'],indent=2),'```']
    Path('training/review-packet.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
