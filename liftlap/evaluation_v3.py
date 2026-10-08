"""Offline granular scoring v1 for intent-v2 artifacts; never changes runtime or old scores."""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
import math
from pathlib import Path

from .core import RANK, digest, plan, validate_route
from .corpus import audit, label_approved, read
from scripts.benchmark import FIELDS_V2, REQUIRED, normalize, validate_intent

VERSION = 'granular-evaluation-v1'
TRANSPORT_FAILURES = {'transport_or_provider_failure', 'timeout', 'provider_error'}
NOT_ATTEMPTED = {'not_attempted_after_transport_failure', 'not_attempted'}


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('Nonfinite JSON constant')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid_constant)


def semantic_issues(intent):
    """Scoring-only consistency observations; not the future R01 provenance contract."""
    issues = []
    if intent['status'] == 'clarify':
        for field in sorted(REQUIRED):
            if field in intent['clarification_fields'] and intent[field] is not None:
                issues.append({'code': 'clarification_retains_value', 'path': field})
            if intent[field] is None and field not in intent['clarification_fields']:
                issues.append({'code': 'missing_value_not_clarified', 'path': field})
    return issues


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def percentile(values, fraction):
    """Nearest-rank percentile, with missing observations reported separately."""
    return sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)] if values else None


def summarize(rows):
    count = len(rows)
    flags = ('transport_completed', 'syntax_valid', 'schema_valid', 'intent_exact_match',
             'clarification_correct', 'task_success', 'hard_max_violation',
             'hard_exclusion_violation', 'critical_extraction_failure',
             'clarification_false_positive', 'clarification_false_negative',
             'safety_intercepted', 'accepted_route_violates_gold')
    result = {'count': count}
    for key in flags:
        total = sum(r[key] is True for r in rows)
        result[key] = {'count': total, 'denominator': count, 'rate': total / count if count else None}
    result['per_field_accuracy'] = {field: {'correct': sum(r['field_correct'].get(field, False) for r in rows),
                                           'denominator': count,
                                           'rate': sum(r['field_correct'].get(field, False) for r in rows)/count if count else None}
                                    for field in sorted(FIELDS_V2)}
    tp = sum(r['exclusions']['true_positive'] for r in rows)
    fp = sum(r['exclusions']['false_positive'] for r in rows)
    fn = sum(r['exclusions']['false_negative'] for r in rows)
    result['exclusion_set'] = {'true_positive': tp, 'false_positive': fp, 'false_negative': fn,
                               'precision': tp / (tp + fp) if tp + fp else None,
                               'recall': tp / (tp + fn) if tp + fn else None,
                               'schema_valid_cases': sum(r['schema_valid'] for r in rows),
                               'policy': 'invalid/missing outputs contribute no predicted exclusions; null for empty denominator'}
    times = [r['elapsed_seconds'] for r in rows if r['elapsed_seconds'] is not None]
    result['latency_seconds'] = {'observed': len(times), 'missing': count - len(times),
                                 'p50': percentile(times, .5), 'p95': percentile(times, .95),
                                 'method': 'nearest_rank_including_observed_failed_attempts'}
    for key in ('input_tokens', 'output_tokens'):
        observed = [r[key] for r in rows if r[key] is not None]
        result[key] = {'observed_sum': sum(observed), 'observed_cases': len(observed),
                       'missing_cases': count - len(observed),
                       'complete_total': sum(observed) if len(observed) == count else None}
    return result


def score_case(case, bundle, prediction):
    p = prediction or {}
    raw = p.get('raw_output')
    status = p.get('status', 'missing_prediction')
    transport = ('missing' if prediction is None else 'failed' if status in TRANSPORT_FAILURES
                 else 'not_attempted' if status in NOT_ATTEMPTED
                 else 'completed' if isinstance(raw, str) else 'unknown')
    row = {'id': case['id'], 'scenario': case['scenario_family'], 'family': case['family_id'],
           'transport_outcome': transport, 'transport_completed': transport == 'completed',
           'saved_status': status, 'stop_reason': p.get('stop_reason'),
           'raw_output_sha256': hashlib.sha256(raw.encode()).hexdigest() if isinstance(raw, str) else None,
           'syntax_valid': False, 'schema_valid': False, 'intent_exact_match': False,
           'field_correct': {}, 'field_errors': sorted(FIELDS_V2), 'semantic_issues': [],
           'clarification_correct': False, 'clarification_false_positive': False,
           'clarification_false_negative': case['gold_intent']['status'] == 'clarify',
           'hard_max_violation': False, 'hard_exclusion_violation': False,
           'critical_extraction_failure': False, 'safety_intercepted': False,
           'accepted_route_violates_gold': False, 'proposal_validation': None,
           'gold_proposal_validation': None, 'route_accepted': False,
           'outcome': 'invalid_output', 'expected_outcome': case['expected_planner_status'],
           'task_success': False, 'normalized_intent_sha256': None}
    row['elapsed_seconds'] = p.get('elapsed_seconds') if number(p.get('elapsed_seconds')) else None
    for key in ('input_tokens', 'output_tokens'):
        value = p.get(key)
        row[key] = value if type(value) is int and value >= 0 else None
    gold = case['gold_intent']
    row['exclusions'] = {'true_positive': 0, 'false_positive': 0,
                         'false_negative': len(gold['excluded_lift_types'])}
    try:
        if not isinstance(raw, str):
            raise ValueError('Missing raw output')
        intent = strict_json(raw)
        row['syntax_valid'] = True
        validate_intent(intent, {p['id'] for p in case['catalog']})
        row['schema_valid'] = True
    except (ValueError, TypeError, KeyError):
        return row
    actual, expected = normalize(intent), normalize(gold)
    row['normalized_intent_sha256'] = digest(actual)
    row['field_correct'] = {field: actual[field] == expected[field] for field in sorted(FIELDS_V2)}
    row['field_errors'] = [field for field, correct in row['field_correct'].items() if not correct]
    row['intent_exact_match'] = not row['field_errors']
    row['semantic_issues'] = semantic_issues(intent)
    row['clarification_correct'] = ((intent['status'] == 'clarify') == (gold['status'] == 'clarify')
                                    and actual['clarification_fields'] == expected['clarification_fields'])
    row['clarification_false_positive'] = intent['status'] == 'clarify' and gold['status'] != 'clarify'
    row['clarification_false_negative'] = intent['status'] != 'clarify' and gold['status'] == 'clarify'
    predicted_exclusions, gold_exclusions = set(intent['excluded_lift_types']), set(gold['excluded_lift_types'])
    row['exclusions'] = {'true_positive': len(predicted_exclusions & gold_exclusions),
                         'false_positive': len(predicted_exclusions - gold_exclusions),
                         'false_negative': len(gold_exclusions - predicted_exclusions)}
    ceiling, expected_ceiling = intent['hard_max_difficulty'], gold['hard_max_difficulty']
    row['hard_max_violation'] = (ceiling is not None and
                                  (expected_ceiling is None or RANK[ceiling] > RANK[expected_ceiling]))
    row['hard_exclusion_violation'] = bool(gold_exclusions - predicted_exclusions)
    row['critical_extraction_failure'] = (row['hard_max_violation'] or row['hard_exclusion_violation']
                                           or (intent['status'] == 'ready' and gold['status'] != 'ready'))
    if transport != 'completed' or p.get('stop_reason') != 'stop':
        row['outcome'] = 'incomplete_transport_or_stop'
        return row
    if row['semantic_issues']:
        row['outcome'] = 'semantic_rejection'
        return row
    row['outcome'] = intent['status']
    if intent['status'] == 'ready':
        graph = bundle['graph']
        scenario = copy.deepcopy(bundle['scenario'])
        for edge_id, patch in case['edge_overrides'].items():
            scenario['edges'][edge_id].update(patch)
        try:
            proposal = plan(graph, intent, scenario)
        except ValueError:
            proposal = {'status': 'operational_limit', 'route': None}
        row['outcome'] = proposal['status']
        if proposal.get('route') is not None:
            row['proposal_validation'] = validate_route(graph, intent, scenario, proposal['route'])
            row['gold_proposal_validation'] = validate_route(graph, gold, scenario, proposal['route'])
            row['route_accepted'] = row['proposal_validation']['valid']
            row['safety_intercepted'] = not row['route_accepted']
            row['accepted_route_violates_gold'] = row['route_accepted'] and not row['gold_proposal_validation']['valid']
            if row['accepted_route_violates_gold']:
                row['critical_extraction_failure'] = True
            if not row['route_accepted']:
                row['outcome'] = 'route_rejected'
        elif proposal['status'] == 'ok':
            row['outcome'] = 'missing_route'
    row['task_success'] = (row['intent_exact_match'] and row['outcome'] == row['expected_outcome']
                           and not row['accepted_route_violates_gold'])
    return row


def evaluate(cases, bundles, predictions, *, freeze, manifest):
    """One explicitly assigned run; absent predictions stay in the denominator."""
    if (not cases or audit(cases)['errors']
            or any(not label_approved(c) or c['gold_intent'].get('schema_version') != 2 for c in cases)):
        raise ValueError('Human-approved valid corpus required')
    if (freeze.get('status') != 'frozen' or freeze.get('cases_sha256') != digest(cases)
            or freeze.get('graph_bundle_sha256') != digest(bundles)):
        raise ValueError('Missing or stale evaluation freeze')
    ids = [c['id'] for c in cases]
    if manifest.get('assigned_case_ids') != ids or not manifest.get('run_id'):
        raise ValueError('Manifest must assign every frozen case in order')
    if manifest.get('lane') not in {'primary', 'fallback'}:
        raise ValueError('Explicit primary/fallback lane required')
    lookup = {}
    for p in predictions:
        if p['id'] in lookup or p['id'] not in ids:
            raise ValueError('Duplicate or unknown prediction id; preserve attempts as separate runs')
        lookup[p['id']] = p
    costs = {key: manifest.get(key) for key in ('reserved_usd', 'reconciled_usd')}
    if any(v is not None and not number(v) for v in costs.values()):
        raise ValueError('Invalid cost metadata')
    rows = [score_case(c, bundles[c['scenario_family']], lookup.get(c['id'])) for c in cases]
    groups = {}
    for dimension in ('scenario', 'family'):
        grouped = defaultdict(list)
        for row in rows:
            grouped[row[dimension]].append(row)
        groups[dimension] = {key: summarize(values) for key, values in sorted(grouped.items())}
    report = {'report_version': VERSION, 'scope': 'offline_scoring_not_runtime_safety_or_promotion',
              'partition': freeze.get('evaluation_partition', 'historical_diagnostic'),
              'run_id': manifest['run_id'], 'lane': manifest['lane'],
              'cases_sha256': digest(cases), 'graph_bundle_sha256': digest(bundles),
              'freeze_sha256': digest(freeze), 'predictions_sha256': digest(predictions),
              'manifest_sha256': digest(manifest), 'manifest': copy.deepcopy(manifest),
              'scorer_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'dependency_source_sha256': {name: hashlib.sha256((Path(__file__).resolve().parents[1]/name).read_bytes()).hexdigest()
                                            for name in ('liftlap/core.py','liftlap/corpus.py','scripts/benchmark.py')},
              'count': len(rows), 'predictions_present': len(predictions), 'missing_predictions': len(cases)-len(predictions),
              'cases': rows, 'metrics': summarize(rows), 'groups': groups, 'costs': costs,
              'limitations': ['Small authored sets do not establish statistical significance.',
                             'Semantic observations are scorer-only, not the R01 runtime contract.',
                             'Gold rejection is not a runtime safety interception; runtime lacks gold labels.',
                             'Unknown metadata/costs remain null; token counts are not billing proof.']}
    report['report_sha256'] = digest(report)
    return report


def verify_report(report):
    body = {k: v for k, v in report.items() if k != 'report_sha256'}
    if report.get('report_version') != VERSION or report.get('report_sha256') != digest(body):
        raise ValueError('Stale or unsupported report')
    return report


def collect_runs(reports, expected_run_ids):
    """Reconcile a predeclared run inventory, never select the best retry."""
    if not reports or len(set(expected_run_ids)) != len(expected_run_ids):
        raise ValueError('Nonempty unique run inventory required')
    lookup = {}
    for report in reports:
        verify_report(report)
        if report['run_id'] in lookup:
            raise ValueError('Duplicate run')
        lookup[report['run_id']] = report
    if set(lookup) != set(expected_run_ids):
        raise ValueError('Missing or unassigned attempted run')
    return {'report_version': 'attempt-inventory-v1', 'expected_run_ids': expected_run_ids,
            'report_sha256': {key: lookup[key]['report_sha256'] for key in expected_run_ids},
            'lanes': {lane: summarize([row for r in reports if r['lane'] == lane for row in r['cases']])
                      for lane in ('primary', 'fallback')},
            'costs_by_run': {r['run_id']: r['costs'] for r in reports}}


def repeatability(reports, expected_run_ids):
    collect_runs(reports, expected_run_ids)
    first = reports[0]
    if len(reports) < 2 or any(r['lane'] != 'primary' or
            (r['cases_sha256'], r['graph_bundle_sha256'], r['manifest'].get('model_version'),
             r['manifest'].get('prompt_sha256'), r['manifest'].get('renderer_sha256'),
             r['manifest'].get('decoding')) !=
            (first['cases_sha256'], first['graph_bundle_sha256'], first['manifest'].get('model_version'),
             first['manifest'].get('prompt_sha256'), first['manifest'].get('renderer_sha256'),
             first['manifest'].get('decoding')) for r in reports):
        raise ValueError('Repeatability requires matching primary run configurations and at least two runs')
    grouped = zip(*(r['cases'] for r in reports), strict=True)
    rows = []
    for group in grouped:
        completed = all(r['transport_completed'] and r['schema_valid'] and r['stop_reason'] == 'stop' for r in group)
        rows.append({'id': group[0]['id'],
                     'agreement': completed and len({r['normalized_intent_sha256'] for r in group}) == 1,
                     'all_correct': all(r['task_success'] for r in group),
                     'successes': sum(r['task_success'] for r in group), 'attempts': len(group)})
    return {'report_version': 'repeatability-v1', 'count': len(rows), 'runs': len(reports), 'cases': rows,
            'agreement_rate': sum(r['agreement'] for r in rows)/len(rows),
            'all_correct_rate': sum(r['all_correct'] for r in rows)/len(rows),
            'task_success_rate': sum(r['successes'] for r in rows)/(len(rows)*len(reports)),
            'failed_outputs_never_count_as_agreement': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('cases', 'graphs', 'predictions', 'freeze', 'manifest'):
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args()
    report = evaluate(read(args.cases), json.loads(Path(args.graphs).read_text()), read(args.predictions),
                      freeze=json.loads(Path(args.freeze).read_text()),
                      manifest=json.loads(Path(args.manifest).read_text()))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
