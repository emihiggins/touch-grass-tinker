"""Offline intent-only seed validation/scoring. Not an end-to-end routing benchmark."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

FIELDS = {'schema_version', 'status', 'start_place_id', 'finish_place_id', 'start_time',
          'duration_minutes', 'hard_max_difficulty', 'excluded_lift_types',
          'preferred_difficulties', 'prefer_variety', 'clarification_fields', 'unsupported_preferences'}
LISTS = {'excluded_lift_types', 'preferred_difficulties', 'clarification_fields', 'unsupported_preferences'}
LIFTS = {'chairlift', 'gondola', 'cable-car', 't-bar', 'platter', 'rope-tow', 'magic-carpet'}
DIFFICULTIES = {'blue', 'red', 'black'}
REQUIRED = {'start_place_id', 'finish_place_id', 'start_time', 'duration_minutes', 'hard_max_difficulty'}

def validate_intent(x, place_ids):
    if not isinstance(x, dict) or set(x) != FIELDS:
        raise ValueError('Intent fields do not match contract')
    if type(x['schema_version']) is not int or x['schema_version'] != 1:
        raise ValueError('Invalid schema version')
    if x['status'] not in {'ready', 'clarify', 'unsupported'}:
        raise ValueError('Invalid status')
    for f in ['start_place_id', 'finish_place_id']:
        if x[f] is not None and (not isinstance(x[f], str) or x[f] not in place_ids):
            raise ValueError('Unknown place')
    if x['start_time'] is not None:
        try:
            stamp = dt.datetime.fromisoformat(x['start_time'])
            if stamp.tzinfo is None:
                raise ValueError('Timezone required')
        except (ValueError, TypeError):
            raise ValueError('Invalid start time')
    minutes = x['duration_minutes']
    if minutes is not None and (type(minutes) is not int or not 15 <= minutes <= 240):
        raise ValueError('Invalid duration')
    if x['hard_max_difficulty'] is not None and x['hard_max_difficulty'] not in DIFFICULTIES:
        raise ValueError('Invalid difficulty')
    if type(x['prefer_variety']) is not bool:
        raise ValueError('Invalid variety flag')
    for f in LISTS:
        v = x[f]
        if not isinstance(v, list) or any(not isinstance(t, str) for t in v) or len(v) != len(set(v)):
            raise ValueError('Invalid unique string list')
    if not set(x['excluded_lift_types']) <= LIFTS:
        raise ValueError('Unknown lift type')
    if not set(x['preferred_difficulties']) <= DIFFICULTIES:
        raise ValueError('Invalid preference')
    if not set(x['clarification_fields']) <= REQUIRED:
        raise ValueError('Unknown clarification field')
    if x['status'] == 'ready' and (any(x[f] is None for f in REQUIRED) or x['clarification_fields'] or x['unsupported_preferences']):
        raise ValueError('Ready intent incomplete')
    if x['status'] == 'clarify' and not x['clarification_fields']:
        raise ValueError('Clarification fields required')
    if x['status'] == 'unsupported' and not x['unsupported_preferences']:
        raise ValueError('Unsupported preference required')
    return x

def normalize(x):
    y = {k: sorted(v) if k in LISTS else v for k, v in x.items()}
    if y['start_time'] is not None:
        y['start_time'] = dt.datetime.fromisoformat(y['start_time']).astimezone(dt.timezone.utc).isoformat()
    return y

def load_cases(path):
    raw = Path(path).read_bytes()
    cases = [json.loads(line) for line in raw.splitlines() if line.strip()]
    ids, texts = set(), set()
    for c in cases:
        if c['id'] in ids or c['request_text'].strip().casefold() in texts:
            raise ValueError('Duplicate case or text')
        ids.add(c['id']); texts.add(c['request_text'].strip().casefold())
        if c['split'] != 'development_seed' or c['review']['human_reviewed'] is not False:
            raise ValueError('Seed must not claim frozen test or human review')
        validate_intent(c['gold_intent'], {p['id'] for p in c['catalog']})
    return cases, hashlib.sha256(raw).hexdigest()

def score(cases, predictions):
    lookup = {}
    for p in predictions:
        if p['id'] in lookup:
            raise ValueError('Duplicate prediction id')
        lookup[p['id']] = p.get('intent')
    if set(lookup) - {c['id'] for c in cases}:
        raise ValueError('Unknown prediction id')
    rows = []
    for c in cases:
        try:
            predicted = validate_intent(lookup.get(c['id']), {p['id'] for p in c['catalog']})
            a, b = normalize(predicted), normalize(c['gold_intent'])
            mismatch = sorted(k for k in FIELDS if a[k] != b[k])
            rows.append({'id': c['id'], 'valid': True, 'exact_match': not mismatch, 'mismatched_fields': mismatch})
        except (ValueError, TypeError, KeyError):
            rows.append({'id': c['id'], 'valid': False, 'exact_match': False, 'mismatched_fields': ['invalid_or_missing_output']})
    return {'metric': 'intent_exact_match_only_not_route_success', 'count': len(rows),
            'correct': sum(r['exact_match'] for r in rows), 'invalid': sum(not r['valid'] for r in rows), 'cases': rows}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cases')
    parser.add_argument('--predictions')
    args = parser.parse_args()
    cases, sha = load_cases(args.cases)
    if args.predictions:
        preds = [json.loads(l) for l in Path(args.predictions).read_text().splitlines() if l.strip()]
        report = score(cases, preds)
    else:
        report = {'validated_cases': len(cases), 'families': sorted({c['family_id'] for c in cases}), 'scope': 'development_seed_only'}
    report['corpus_sha256'] = sha
    print(json.dumps(report, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
