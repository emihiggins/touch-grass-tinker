"""Offline corpus audit/export. No provider calls; no automatic test splitting."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from scripts.benchmark import validate_intent

SPLITS = {'train_candidate', 'train', 'development', 'development_seed', 'evaluation_candidate', 'test',
          'training_candidate', 'validation_candidate', 'final_candidate', 'final'}

def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]

def fingerprint(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))

def review_hash(case):
    payload = {key: case[key] for key in ('id', 'request_text', 'ui_context', 'catalog', 'gold_intent')}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def row_hashes(case):
    """Hashes used by the review gate; each binds the current material independently."""
    return {'request_sha256': hashlib.sha256(case['request_text'].encode()).hexdigest(),
            'context_sha256': _sha(case.get('ui_context', {})),
            'graph_sha256': _sha({'catalog': case.get('catalog', []), 'edge_overrides': case.get('edge_overrides', {}), 'gold_example_route': case.get('gold_example_route')}),
            'label_sha256': _sha(case['gold_intent'])}

def normalized_row_key(case):
    """Context-aware duplicate key including graph/context."""
    text = re.sub(r'\s+', ' ', case['request_text'].casefold()).strip()
    return _sha({'request': text, 'context': case.get('ui_context', {}), 'catalog': case.get('catalog', []), 'edge_overrides': case.get('edge_overrides', {})})

def _family_overlaps(cases):
    locations = {}
    for case in cases:
        for field in ('family_id', 'template_family_id', 'graph_family_id'):
            value = case.get(field)
            if value: locations.setdefault((field, value), set()).add(case.get('split'))
    return [f'{field}:{value} => {sorted(splits)}' for (field, value), splits in locations.items() if len(splits) > 1]

def coverage_report(cases):
    tags = Counter()
    for case in cases:
        intent = case.get('gold_intent', {})
        tags[f"status:{intent.get('status')}"] += 1
        tags[f"grade:{intent.get('hard_max_difficulty') or 'missing'}"] += 1
        tags[f"budget:{'known' if intent.get('duration_minutes') is not None else 'missing'}"] += 1
        tags[f"route:{'positive' if case.get('gold_example_route') else 'negative_or_unset'}"] += 1
        tags[f"review:{'approved' if label_approved(case) else 'unapproved'}"] += 1
    expected = ['status:ready', 'status:clarify', 'status:unsupported', 'grade:missing', 'budget:known', 'budget:missing', 'route:positive', 'route:negative_or_unset']
    return {'counts': dict(tags), 'sparse_or_missing': [key for key in expected if not tags[key]], 'interpretation': 'descriptive coverage only; no representativeness claim'}

def iteration_manifest(cases, *, iteration='m02-2026-10-08', packet_size=12):
    """Build a review manifest without approving or assigning rows to a final split."""
    report = audit(cases)
    families = {}
    for case in cases: families.setdefault(case.get('family_id') or case.get('template_family_id'), []).append(case['id'])
    rows = []
    for case in cases:
        rows.append({'id': case['id'], 'family_id': case.get('family_id'), 'template_family_id': case.get('template_family_id'), 'graph_family_id': case.get('graph_family_id'), 'source': case.get('provenance', {}), 'split': case.get('split'), 'review_state': 'unapproved' if not label_approved(case) else 'approved-source', **row_hashes(case), 'normalized_row_sha256': normalized_row_key(case)})
    return {'manifest_version': 'm02-1', 'iteration': iteration, 'authorship': 'same-agent authored; Emi review required; fictional/offline only', 'boundaries': {'candidate': ['training_candidate'], 'development': ['validation_candidate'], 'final': ['final_candidate', 'final'], 'historical_evaluation': ['evaluation_candidate', 'test'], 'export_requires': 'human_reviewed approval and exact current hashes'}, 'packet_limit': packet_size, 'candidate_count': len(cases), 'family_count': len(families), 'family_sizes': {k: len(v) for k, v in families.items()}, 'split_counts': dict(Counter(c.get('split') for c in cases)), 'family_overlap': sorted(_family_overlaps(cases)), 'near_duplicate_review_flags': report['warnings'], 'coverage': coverage_report(cases), 'rows': rows, 'status': 'review-required; not training-ready'}

def label_approved(case):
    """Approval binds to the request, context, catalog and exact reviewed label."""
    review = case.get('review', {})
    return (review.get('human_reviewed') is True and review.get('decision') == 'approved'
            and review.get('reviewed_content_sha256') == review_hash(case)
            and not review.get('quarantine_reason'))

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
        if split == 'train' and not label_approved(c):
            errors.append(f'training requires current approved, non-quarantined label: {cid}')
        text = fingerprint(c['request_text'])
        if not text: errors.append(f'empty request: {cid}')
        if text in texts: errors.append(f'duplicate text: {texts[text]} / {cid}')
        texts[text] = cid
        partition = 'test' if split == 'evaluation_candidate' else 'development' if split == 'development_seed' else 'train' if split == 'train_candidate' else split
        for field in ('template_family_id', 'graph_family_id'):
            # Legacy seeds predate template lineage; keep each semantic family together.
            value = c.get(field, c.get('family_id') if field == 'template_family_id' else None)
            if not value: errors.append(f'missing {field}: {cid}'); continue
            key = (field, value)
            if key in groups and groups[key] != partition: errors.append(f'cross-split {field}: {value}')
            groups[key] = partition
        if not c.get('provenance'): errors.append(f'missing provenance: {cid}')
        if split == 'test' and not label_approved(c):
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
    if not preview and any(not label_approved(c) for c in selected):
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
