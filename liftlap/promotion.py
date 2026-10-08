"""Offline fail-closed promotion decisions; no deployment or provider side effects."""
import argparse
import json
from pathlib import Path
from .core import digest
from .evaluation_v3 import VERSION, verify_report

POLICY = {'policy_version': 'model-promotion-v1', 'scorer_version': VERSION,
          'validation_minimum_additional_successes': 2, 'validation_allow_lower_schema_rate': False,
          'final_minimum_additional_successes': 1, 'allow_new_critical_extraction_failures': False,
          'allow_accepted_route_violations': False, 'tie_selection': 'base',
          'final_failure_action': 'reject_candidate_no_retuning_on_final',
          'statistical_significance_claim': False}


def check_regressions(evidence, candidate_version):
    """Check hash-bound suite inventory, not a naked passed=true declaration."""
    if not isinstance(evidence, dict):
        return False
    ids = evidence.get('expected_case_ids', [])
    rows = evidence.get('cases', [])
    return (bool(ids) and len(set(ids)) == len(ids) and [r.get('id') for r in rows] == ids
            and evidence.get('candidate_model_version') == candidate_version
            and evidence.get('policy_sha256') == digest(POLICY)
            and valid_hash(evidence.get('suite_source_sha256'))
            and all(r.get('passed') is True and type(r.get('accepted_route_violations')) is int
                    and r['accepted_route_violations'] == 0 for r in rows))


def valid_hash(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def decide(base, candidate, *, phase, regressions, policy, validation_decision=None):
    if policy != POLICY or phase not in ('validation', 'final'):
        raise ValueError('Unsupported policy or phase')
    verify_report(base)
    verify_report(candidate)
    reasons = []
    if (base['cases_sha256'], base['graph_bundle_sha256'], base['freeze_sha256']) != (
            candidate['cases_sha256'], candidate['graph_bundle_sha256'], candidate['freeze_sha256']):
        raise ValueError('Paired comparison needs identical frozen cases/graphs')
    if [r['id'] for r in base['cases']] != [r['id'] for r in candidate['cases']]:
        raise ValueError('Paired case alignment mismatch')
    if (base['scorer_source_sha256'] != candidate['scorer_source_sha256']
            or base['dependency_source_sha256'] != candidate['dependency_source_sha256']):
        reasons.append('scorer_implementation_mismatch')
    for label, report in (('base', base), ('candidate', candidate)):
        m = report['manifest']
        if report['partition'] != phase or report['lane'] != 'primary':
            reasons.append(label + '_not_primary_' + phase)
        if m.get('policy_sha256') != digest(policy):
            reasons.append(label + '_policy_not_bound')
        if (not all(isinstance(m.get(k), str) and m[k] for k in ('model', 'model_version'))
                or not all(valid_hash(m.get(k)) for k in ('prompt_sha256', 'renderer_sha256'))
                or not isinstance(m.get('decoding'), dict) or 'seed' not in m['decoding']
                or not m.get('environment') or not isinstance(m['environment'], dict)):
            reasons.append(label + '_incomplete_provenance')
    for key in ('model', 'prompt_sha256', 'renderer_sha256', 'decoding'):
        if base['manifest'].get(key) != candidate['manifest'].get(key):
            reasons.append('comparison_' + key + '_mismatch')
    if not check_regressions(regressions, candidate['manifest'].get('model_version')):
        reasons.append('mandatory_regressions_missing_mismatched_or_failed')
    pairs = list(zip(base['cases'], candidate['cases'], strict=True))
    wins = [b['id'] for b, c in pairs if not b['task_success'] and c['task_success']]
    losses = [b['id'] for b, c in pairs if b['task_success'] and not c['task_success']]
    critical = [b['id'] for b, c in pairs if c['critical_extraction_failure'] and not b['critical_extraction_failure']]
    if critical:
        reasons.append('new_critical_extraction_regressions')
    if any(c['accepted_route_violates_gold'] for c in candidate['cases']):
        reasons.append('candidate_accepted_route_violations')
    required = policy[phase + '_minimum_additional_successes']
    if len(wins) - len(losses) < required:
        reasons.append('insufficient_additional_task_successes')
    if phase == 'validation' and sum(c['schema_valid'] for c in candidate['cases']) < sum(b['schema_valid'] for b in base['cases']):
        reasons.append('lower_strict_schema_rate')
    if phase == 'final':
        prior = validation_decision or {}
        body = {k: v for k, v in prior.items() if k != 'decision_sha256'}
        if (prior.get('decision_sha256') != digest(body) or prior.get('decision') != 'eligible_for_final'
                or prior.get('phase') != 'validation' or prior.get('policy_sha256') != digest(policy)
                or prior.get('candidate_model_version') != candidate['manifest'].get('model_version')
                or prior.get('base_model_version') != base['manifest'].get('model_version')
                or prior.get('comparison_config_sha256') != comparison_config_sha(candidate)
                or candidate['manifest'].get('validation_decision_sha256') != prior.get('decision_sha256')
                or base['manifest'].get('validation_decision_sha256') != prior.get('decision_sha256')
                or prior.get('cases_sha256') == candidate['cases_sha256']):
            reasons.append('missing_or_mismatched_locked_validation_selection')
    result = {'decision_version': 'promotion-decision-v1', 'phase': phase,
              'policy_sha256': digest(policy), 'base_report_sha256': base['report_sha256'],
              'candidate_report_sha256': candidate['report_sha256'],
              'regressions_sha256': digest(regressions), 'cases_sha256': candidate['cases_sha256'],
              'base_model_version': base['manifest'].get('model_version'),
              'candidate_model_version': candidate['manifest'].get('model_version'),
              'comparison_config_sha256': comparison_config_sha(candidate),
              'paired_wins': wins, 'paired_losses': losses, 'new_critical_regressions': critical,
              'additional_successes': len(wins) - len(losses), 'reasons': sorted(set(reasons)),
              'decision': 'retain_base' if reasons else 'eligible_for_final' if phase == 'validation' else 'promote_candidate',
              'action': 'reject_candidate_no_retuning_on_final' if reasons and phase == 'final' else 'no_runtime_change',
              'uncertainty': {'sample_count': len(pairs), 'discordant_pairs': len(wins) + len(losses),
                              'statistical_significance_claim': False,
                              'note': 'Operational gates, not a statistical superiority or field-safety claim.'}}
    result['decision_sha256'] = digest(result)
    return result


def comparison_config_sha(report):
    return digest({k: report['manifest'].get(k) for k in ('model', 'prompt_sha256', 'renderer_sha256', 'decoding')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base', 'candidate', 'regressions', 'policy'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--phase', required=True, choices=('validation', 'final'))
    parser.add_argument('--validation-decision')
    args = parser.parse_args()
    load = lambda path: json.loads(Path(path).read_text())
    print(json.dumps(decide(load(args.base), load(args.candidate), phase=args.phase,
                            regressions=load(args.regressions), policy=load(args.policy),
                            validation_decision=load(args.validation_decision) if args.validation_decision else None), indent=2))


if __name__ == '__main__':
    main()
