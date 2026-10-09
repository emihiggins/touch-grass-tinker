"""Read-only postmortem of SFT02. Never repairs predictions or authorizes promotion."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from liftlap.corpus import read
from liftlap.evaluation_v3 import strict_json
from liftlap.semantic_contract import validate_intent_semantics
from scripts.benchmark import normalize


def inspect_output(raw, catalog, gold):
    result = {'strict_json': False, 'prefix_only_forensics': False, 'trailing_suffix': None,
              'semantic_issues': [], 'field_mismatches': None}
    try:
        candidate = strict_json(raw)
        result['strict_json'] = True
    except (ValueError, TypeError):
        # Expose a complete prefix only for forensics. Never return a replacement prediction.
        try:
            _, end = json.JSONDecoder().raw_decode(raw.lstrip())
            text = raw.lstrip()
            candidate = strict_json(text[:end])
            result.update(prefix_only_forensics=True, trailing_suffix=text[end:])
        except (ValueError, TypeError, AttributeError):
            return result
    semantic = validate_intent_semantics(candidate, {p['id'] for p in catalog})
    result['semantic_issues'] = [issue.code for issue in semantic.issues]
    if not isinstance(candidate, dict): return result
    try:
        actual, expected = normalize(candidate), normalize(gold)
        result['field_mismatches'] = [
            {'field': key, 'expected': expected.get(key), 'observed': actual.get(key)}
            for key in sorted(set(actual) | set(expected)) if actual.get(key) != expected.get(key)
        ]
    except (ValueError, TypeError, KeyError):
        pass
    return result


def generate():
    root = ROOT / 'research/evidence/experiment-02'
    case_path = ROOT / 'benchmark/v2/evaluation-pilot-frozen.jsonl'
    cases = read(case_path)
    inputs = [case_path]
    arms = {}
    for name in ('base', 'trained'):
        prediction_path = root / (name + '-predictions.jsonl')
        report_path = root / (name + '-report.json')
        inputs.extend([prediction_path, report_path])
        predictions = read(prediction_path)
        reports = json.loads(report_path.read_text())['cases']
        ids = [c['id'] for c in cases]
        if [p['id'] for p in predictions] != ids or [r['id'] for r in reports] != ids:
            raise ValueError('Exact case alignment required; missing/reordered attempts cannot disappear')
        rows = []
        for case, prediction, report in zip(cases, predictions, reports, strict=True):
            rows.append({'id': case['id'], 'saved_status': prediction['status'],
                         'saved_task_success': report['success'],
                         'accepted_route_violates_reviewed_constraints': report['outcome'] == 'ok' and report['gold_route_valid'] is False,
                         'stop_reason': prediction.get('stop_reason'),
                         'output_tokens': prediction.get('output_tokens'),
                         **inspect_output(prediction.get('raw_output'), case['catalog'], case['gold_intent'])})
        arms[name] = {'count': len(rows), 'task_successes': sum(r['saved_task_success'] for r in rows),
                      'accepted_routes_violating_reviewed_constraints': sum(r['accepted_route_violates_reviewed_constraints'] for r in rows),
                      'invalid_json': sum(not r['strict_json'] for r in rows),
                      'forensic_prefixes_still_wrong': sum(r['prefix_only_forensics'] and bool(r['field_mismatches'] or r['semantic_issues']) for r in rows),
                      'cases': rows}
    paired = [{'id': a['id'], 'base_success': a['saved_task_success'], 'trained_success': b['saved_task_success']}
              for a, b in zip(arms['base']['cases'], arms['trained']['cases'], strict=True)]
    return {'version': 'sft02-postmortem-1', 'scope': 'offline_reviewed_gold_diagnostics_not_runtime_safety_or_repaired_scores',
            'provider_calls': 0, 'predictions_modified': False, 'promotion_decision': 'retain_base',
            'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
            'arms': arms, 'paired': paired,
            'limits': ['Historical pilot is exposed, not an untouched final set.',
                       'Gold-relative violations require reviewed answers unavailable to the live application.',
                       'Prefix inspection never authorizes JSON repair or changes the saved score.',
                       'No inference about retraining causes or constrained-decoding efficacy from one run.']}


if __name__ == '__main__':
    print(json.dumps(generate(), indent=2, sort_keys=True))
