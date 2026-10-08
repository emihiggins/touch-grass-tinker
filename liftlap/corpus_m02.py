"""Versioned M02 review diagnostics; never authorizes training or freezes splits."""
from collections import Counter
import copy
import hashlib
import json
import re
from .corpus import audit
from .corpus import conversation

PARTITIONS = {
    'train_candidate': 'training', 'training_candidate': 'training', 'train': 'training',
    'development_seed': 'development', 'development': 'development',
    'validation_candidate': 'development', 'evaluation_candidate': 'final',
    'test': 'final', 'final_candidate': 'final', 'final': 'final',
}


def partition(split):
    return PARTITIONS.get(split, split)


def approval_hash(case):
    """Bind all declared material, including lineage and split, but not review metadata."""
    return _sha({key: value for key, value in case.items() if key != 'review'})


def label_approved(case):
    review = case.get('review', {})
    return (review.get('human_reviewed') is True
            and review.get('decision') == 'approved'
            and review.get('approval_version') == 'm02-2'
            and bool(review.get('reviewer'))
            and review.get('reviewed_content_sha256') == approval_hash(case)
            and not review.get('quarantine_reason'))


def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def row_hashes(case):
    """Hashes used by the review gate; each binds the current material independently."""
    return {'request_sha256': hashlib.sha256(case['request_text'].encode()).hexdigest(),
            'context_sha256': _sha(case.get('ui_context', {})),
            'graph_sha256': _sha(case['graph']) if case.get('graph') else None,
            'catalog_constraints_sha256': _sha({'catalog': case.get('catalog', []), 'edge_overrides': case.get('edge_overrides', {}), 'gold_example_route': case.get('gold_example_route')}),
            'label_sha256': _sha(case['gold_intent'])}


def source_lineage_overlaps(cases, source_cases):
    """Report candidate rows that reuse source IDs or reviewed material."""
    candidate_by_source = {}
    candidate_by_key = {}
    for case in cases:
        source_id = case.get('provenance', {}).get('historical_source_id')
        if source_id:
            candidate_by_source.setdefault(source_id, []).append(case['id'])
        candidate_by_key.setdefault(normalized_row_key(case), []).append(case['id'])
    overlaps = []
    for source in source_cases:
        source_id = source.get('id')
        if source_id in candidate_by_source:
            overlaps.append('historical-source-id: ' + source_id + ' => ' + ', '.join(candidate_by_source[source_id]))
        key = normalized_row_key(source)
        if key in candidate_by_key:
            overlaps.append('normalized-row: ' + source_id + ' => ' + ', '.join(candidate_by_key[key]))
    return sorted(set(overlaps))


def approved_export(cases, prompt, *, source_cases=()):
    """Export only current, approved v2 training rows; fail closed otherwise."""
    if not cases:
        raise ValueError('No M02 rows supplied')
    normalized = copy.deepcopy(cases)
    for case in normalized:
        if case.get('split') == 'train_candidate':
            case['split'] = 'train'
    report = audit(normalized)
    errors = list(report['errors'])
    errors.extend('source overlap: ' + item for item in source_lineage_overlaps(cases, source_cases))
    errors.extend('near duplicate review required: ' + item for item in report['warnings'])
    for case in cases:
        cid = case.get('id', '<missing>')
        if case.get('split') != 'train_candidate':
            errors.append('M02 export requires train_candidate split: ' + cid)
        if case.get('gold_intent', {}).get('schema_version') != 2:
            errors.append('M02 export requires intent-v2: ' + cid)
        if not label_approved(case):
            errors.append('M02 approval required: ' + cid)
        for name, value in row_hashes(case).items():
            stored = case.get('review', {}).get(name)
            if stored is not None and stored != value:
                errors.append('stale ' + name + ': ' + cid)
    if errors:
        raise ValueError('; '.join(sorted(set(errors))))
    return [conversation(case, prompt) for case in cases]

def normalized_row_key(case):
    """Diagnostic duplicate key for request, context, catalog and edge overrides."""
    text = re.sub(r'\s+', ' ', case['request_text'].casefold()).strip()
    return _sha({'request': text, 'context': case.get('ui_context', {}), 'catalog': case.get('catalog', []), 'edge_overrides': case.get('edge_overrides', {})})

def _family_overlaps(cases):
    locations = {}
    for case in cases:
        for field in ('family_id', 'template_family_id', 'graph_family_id'):
            value = case.get(field)
            if value: locations.setdefault((field, value), set()).add(partition(case.get('split')))
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
    normalized = copy.deepcopy(cases)
    for case in normalized:
        case['split'] = {
            'training_candidate': 'train_candidate',
            'validation_candidate': 'development_seed',
            'final_candidate': 'evaluation_candidate', 'final': 'test',
        }.get(case['split'], case['split'])
    report = audit(normalized)
    overlaps = sorted(_family_overlaps(cases))
    errors = list(report['errors']) + ['cross-partition ' + item for item in overlaps]
    if len(cases) > packet_size:
        errors.append('packet exceeds review limit')
    source_locations = {}
    for case in cases:
        source = case.get('provenance', {}).get('historical_source_id')
        if source:
            source_locations.setdefault(source, set()).add(partition(case['split']))
        if not label_approved(case):
            errors.append('current M02 approval required: ' + case['id'])
    for source, partitions in source_locations.items():
        if len(partitions) > 1:
            errors.append('cross-partition historical source: ' + source)

    families = {}
    for case in cases: families.setdefault(case.get('family_id') or case.get('template_family_id'), []).append(case['id'])
    rows = []
    for case in cases:
        rows.append({'id': case['id'], 'family_id': case.get('family_id'), 'template_family_id': case.get('template_family_id'), 'graph_family_id': case.get('graph_family_id'), 'source': case.get('provenance', {}), 'split': case.get('split'), 'review_state': 'unapproved' if not label_approved(case) else 'approved-source', **row_hashes(case), 'normalized_row_sha256': normalized_row_key(case)})
    return {'manifest_version': 'm02-2', 'iteration': iteration, 'authorship': 'same-agent authored; Emi review required; fictional/offline only', 'boundaries': {'candidate': ['training_candidate'], 'development': ['validation_candidate'], 'final': ['final_candidate', 'final'], 'historical_evaluation': ['evaluation_candidate', 'test'], 'export_requires': 'no M02 exporter implemented; diagnostics never authorize export'}, 'packet_limit': packet_size, 'candidate_count': len(cases), 'family_count': len(families), 'family_sizes': {k: len(v) for k, v in families.items()}, 'split_counts': dict(Counter(c.get('split') for c in cases)), 'family_overlap': overlaps, 'blocking_errors': sorted(set(errors)), 'training_export_supported': False, 'limitations': ['Family identifiers are declarations, not verified lineage.', 'Compare against the full source corpus before any split freeze.', 'Null graph hashes mean no graph supplied; no graph diversity claim.', 'Legacy schema-v1 seed derivatives need intent-v2 and semantic review.'], 'near_duplicate_review_flags': report['warnings'], 'coverage': coverage_report(cases), 'rows': rows, 'status': 'review-required; not training-ready'}

