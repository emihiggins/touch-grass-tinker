"""Offline corpus audit/export. No provider calls; no automatic test splitting."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from scripts.benchmark import validate_intent

SPLITS = {'train_candidate', 'train', 'development', 'development_seed', 'test'}

def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]

def fingerprint(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))

def audit(cases):
    errors, warnings = [], []
    seen, texts, groups = set(), {}, {}
    for c in cases:
        cid = c['id']; split = c['split']
        if cid in seen: errors.append(f'duplicate id: {cid}')
        seen.add(cid)
        if split not in SPLITS: errors.append(f'invalid split: {cid}')
        try: validate_intent(c['gold_intent'], {p['id'] for p in c['catalog']})
        except (ValueError, TypeError, KeyError): errors.append(f'invalid intent: {cid}')
        text = fingerprint(c['request_text'])
        if not text: errors.append(f'empty request: {cid}')
        if text in texts: errors.append(f'duplicate text: {texts[text]} / {cid}')
        texts[text] = cid
        partition = 'development' if split == 'development_seed' else 'train' if split == 'train_candidate' else split
        for field in ('template_family_id', 'graph_family_id'):
            # Legacy seeds predate template lineage; keep each semantic family together.
            value = c.get(field, c.get('family_id') if field == 'template_family_id' else None)
            if not value: errors.append(f'missing {field}: {cid}'); continue
            key = (field, value)
            if key in groups and groups[key] != partition: errors.append(f'cross-split {field}: {value}')
            groups[key] = partition
        if not c.get('provenance'): errors.append(f'missing provenance: {cid}')
        if split == 'test' and c.get('review', {}).get('human_reviewed') is not True:
            errors.append(f'test requires human review: {cid}')
    # Surface overlap for review, not a claim of semantic deduplication.
    for i, a in enumerate(cases):
        for b in cases[i+1:]:
            if a['split'] == b['split']: continue
            x, y = set(fingerprint(a['request_text']).split()), set(fingerprint(b['request_text']).split())
            if x and y and len(x & y) / len(x | y) >= .7:
                warnings.append(f'near duplicate review: {a["id"]} / {b["id"]}')
    return {'count': len(cases), 'splits': dict(Counter(c['split'] for c in cases)),
            'errors': sorted(set(errors)), 'warnings': warnings,
            'scope': 'structural_audit_not_independent_label_review_or_test_freeze'}

def conversation(c, prompt, target=True):
    messages = [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': json.dumps(
        {k: c[k] for k in ('request_text', 'ui_context', 'catalog')}, sort_keys=True)}]
    if target: messages.append({'role': 'assistant', 'content': json.dumps(c['gold_intent'], sort_keys=True)})
    return {'messages': messages}

def export(cases, prompt, preview=False):
    report = audit(cases)
    if report['errors']: raise ValueError('; '.join(report['errors']))
    if report['warnings'] and not preview: raise ValueError('Resolve near-duplicate warnings before training export')
    selected = [c for c in cases if c['split'] == ('train_candidate' if preview else 'train')]
    if not selected: raise ValueError('No eligible training rows; development/test rows cannot be exported for training')
    if not preview and any(c.get('review', {}).get('human_reviewed') is not True for c in selected):
        raise ValueError('Training export requires reviewed labels; use candidate preview for inspection')
    return [conversation(c, prompt) for c in selected]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('files', nargs='+'); p.add_argument('--output')
    p.add_argument('--preview-candidates', action='store_true')
    p.add_argument('--prompt', default='benchmark/baseline-prompt.txt')
    a = p.parse_args(); cases = [c for f in a.files for c in read(f)]
    report = audit(cases)
    report['input_sha256'] = {f: hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in a.files}
    if a.output:
        prompt = Path(a.prompt).read_text()
        rows = export(cases, prompt, a.preview_candidates)
        payload = ''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows)
        Path(a.output).write_text(payload)
        report.update(export_count=len(rows), export_sha256=hashlib.sha256(payload.encode()).hexdigest(),
                      prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(), preview_only=a.preview_candidates)
    print(json.dumps(report, indent=2))
    if report['errors']: raise SystemExit(1)

if __name__ == '__main__': main()
