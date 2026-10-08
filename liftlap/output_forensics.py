"""Read-only forensic inventory of saved fictional benchmark outputs; no repairs/scoring changes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from .corpus import read
from .render_audit import sha
from scripts.benchmark import normalize, validate_intent


def inspect_outputs(cases, predictions, *, max_output_tokens=512):
    ids = [c['id'] for c in cases]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate case id')
    lookup = {}
    for prediction in predictions:
        if prediction['id'] in lookup or prediction['id'] not in ids:
            raise ValueError('Duplicate or unknown prediction id')
        lookup[prediction['id']] = prediction
    rows = []
    for case in cases:
        p = lookup.get(case['id'], {})
        raw = p.get('raw_output')
        row = {'id': case['id'], 'saved_status': p.get('status', 'missing_prediction'),
               'stop_reason': p.get('stop_reason'), 'output_tokens': p.get('output_tokens'),
               'raw_output_sha256': hashlib.sha256(raw.encode('utf-8')).hexdigest() if isinstance(raw, str) else None,
               'strict_json': False, 'strict_schema': False, 'field_differences': [],
               'at_output_cap': p.get('output_tokens', -1) == max_output_tokens,
               'truncation_established': False}
        parsed = None
        try:
            if not isinstance(raw, str):
                raise ValueError('Missing raw output')
            parsed = json.loads(raw)
            row['strict_json'] = True
        except ValueError:
            row['observation'] = 'missing_raw_output' if raw is None else 'malformed_json'
            if isinstance(raw, str):
                # Inspect a prefix only to describe trailing bytes; never repair or score it.
                try:
                    prefix, end = json.JSONDecoder().raw_decode(raw.lstrip())
                    trailing = raw.lstrip()[end:]
                    if isinstance(prefix, dict) and trailing == '"':
                        row['observation'] = 'json_object_followed_by_quote'
                except ValueError:
                    pass
        if row['strict_json']:
            try:
                validate_intent(parsed, {p['id'] for p in case['catalog']})
                row['strict_schema'] = True
                actual, expected = normalize(parsed), normalize(case['gold_intent'])
                row['field_differences'] = sorted(k for k in expected if actual[k] != expected[k])
                row['observation'] = 'intent_mismatch' if row['field_differences'] else 'intent_match'
            except (ValueError, TypeError, KeyError) as error:
                row['observation'] = 'schema_rejection'
                row['schema_error_type'] = type(error).__name__
            row['saved_intent_matches_raw'] = p.get('intent') == parsed
        # A length cap or finish reason alone is not proof of what caused malformed output.
        rows.append(row)
    return {'report_version': 'saved-output-forensics-v1', 'count': len(rows),
            'observations': dict(Counter(r['observation'] for r in rows)), 'cases': rows,
            'raw_output_hash_encoding': 'exact saved string encoded as UTF-8; container file hash recorded separately',
            'repairs_applied': 0, 'historical_scores_changed': False,
            'causal_conclusion': 'undetermined; saved decoded strings do not preserve sampled token IDs'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', required=True)
    parser.add_argument('--predictions', required=True)
    args = parser.parse_args()
    report = inspect_outputs(read(args.cases), read(args.predictions))
    report['input_sha256'] = {name: sha(path) for name, path in
                              [('cases', args.cases), ('predictions', args.predictions)]}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
