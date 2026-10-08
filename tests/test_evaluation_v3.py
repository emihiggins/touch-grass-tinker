import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from liftlap.core import digest, plan
from liftlap.corpus import read
from liftlap.evaluation_v3 import collect_runs, evaluate, repeatability, strict_json
from liftlap.promotion import POLICY, decide


class GranularScoringTests(unittest.TestCase):
    def setUp(self):
        root = Path('benchmark/v2/final-review')
        self.cases = read(root / 'cases.jsonl')
        self.graphs = json.loads((root / 'graphs.json').read_text())
        self.freeze = json.loads((root / 'freeze.json').read_text())
        self.predictions = read('research/evidence/fresh-base-evaluation/predictions.jsonl')

    def manifest(self, cases=None, run_id='base', lane='primary'):
        return {'run_id': run_id, 'assigned_case_ids': [c['id'] for c in (cases or self.cases)],
                'lane': lane, 'model': 'fixture', 'model_version': run_id,
                'prompt_sha256': 'a'*64, 'renderer_sha256': 'b'*64,
                'decoding': {'seed': 1, 'temperature': 0}, 'environment': {'python': 'fixture'},
                'policy_sha256': digest(POLICY), 'reserved_usd': 1, 'reconciled_usd': None}

    def run_report(self, predictions=None, run_id='base', lane='primary'):
        return evaluate(self.cases, self.graphs, self.predictions if predictions is None else predictions,
                        freeze=self.freeze, manifest=self.manifest(run_id=run_id, lane=lane))

    def test_saved_historical_reports_reproduce_exactly(self):
        from scripts.score_robustness_history import generate
        root = Path('research/evidence/model-robustness-r03')
        for name, artifact in generate().items():
            with self.subTest(artifact=name):
                self.assertEqual(json.loads((root/name).read_text()), artifact)

    def test_saved_base_fields_semantics_and_denominators(self):
        report = self.run_report()
        self.assertEqual(report['count'], 16)
        self.assertEqual(report['metrics']['task_success']['count'], 13)
        self.assertEqual(report['metrics']['schema_valid']['count'], 16)
        self.assertEqual(report['metrics']['hard_exclusion_violation']['count'], 1)
        self.assertEqual(report['cases'][4]['exclusions']['false_negative'], 3)
        self.assertEqual(report['cases'][9]['outcome'], 'semantic_rejection')
        self.assertEqual(report['cases'][11]['semantic_issues'],
                         [{'code': 'clarification_retains_value', 'path': 'duration_minutes'}])
        self.assertIsNone(report['costs']['reconciled_usd'])
        self.assertEqual(sum(g['count'] for g in report['groups']['family'].values()), 16)

    def test_strict_json_rejects_duplicate_nonfinite_and_extra_quote(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{}"'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                strict_json(raw)

    def test_missing_transport_wrong_ids_and_stop(self):
        preds = copy.deepcopy(self.predictions[:4])
        preds[0] = {'id': self.cases[0]['id'], 'status': 'timeout', 'elapsed_seconds': 90}
        preds[1]['raw_output'] = '{}"'
        wrong = copy.deepcopy(self.cases[2]['gold_intent']); wrong['start_place_id'] = 'invented'
        preds[2]['raw_output'] = json.dumps(wrong)
        preds[3]['stop_reason'] = 'length'
        report = self.run_report(preds)
        self.assertEqual(report['missing_predictions'], 12)
        self.assertEqual(report['metrics']['task_success']['count'], 0)
        self.assertEqual(report['metrics']['transport_completed']['count'], 3)
        self.assertEqual(report['metrics']['task_success']['denominator'], 16)
        self.assertEqual(report['metrics']['latency_seconds']['p95'], 90)
        self.assertIsNone(report['metrics']['output_tokens']['complete_total'])
        self.assertFalse(report['cases'][2]['schema_valid'])
        with self.assertRaises(ValueError):
            self.run_report([{'id': 'unassigned'}])
        with self.assertRaises(ValueError):
            self.run_report(self.predictions + self.predictions[:1])

    def test_all_failed_repeatability_and_fallback_separation(self):
        a = self.run_report([], 'a'); b = self.run_report([], 'b')
        # Repeat the same model, not two candidates.
        b['manifest']['model_version'] = 'a'
        b['manifest_sha256'] = digest(b['manifest'])
        b['report_sha256'] = digest({k:v for k,v in b.items() if k != 'report_sha256'})
        repeated = repeatability([a, b], ['a', 'b'])
        self.assertEqual(repeated['agreement_rate'], 0)
        self.assertEqual(repeated['task_success_rate'], 0)
        fallback = self.run_report(self.predictions, 'fallback', 'fallback')
        all_runs = collect_runs([a, fallback], ['a', 'fallback'])
        self.assertEqual(all_runs['lanes']['primary']['task_success']['count'], 0)
        self.assertEqual(all_runs['lanes']['fallback']['task_success']['count'], 13)
        with self.assertRaises(ValueError):
            collect_runs([a], ['a', 'missing-run'])

    def test_consistently_wrong_is_not_correct(self):
        a = self.run_report(run_id='same')
        b = evaluate(self.cases,self.graphs,self.predictions,freeze=self.freeze,
                     manifest={**self.manifest(run_id='same'), 'run_id':'repeat'})
        repeated = repeatability([a,b], ['same','repeat'])
        self.assertEqual(repeated['agreement_rate'], 1)
        self.assertEqual(repeated['task_success_rate'], 13/16)

    def test_invalid_proposal_intercepted_without_gold_leakage(self):
        case = self.cases[0]; bundle = self.graphs[case['scenario_family']]
        proposal = plan(bundle['graph'], case['gold_intent'], bundle['scenario'])
        proposal['route']['edge_ids'] = ['invented-edge']
        with patch('liftlap.evaluation_v3.plan', return_value=proposal):
            row = self.run_report()['cases'][0]
        self.assertTrue(row['schema_valid'])
        self.assertTrue(row['safety_intercepted'])
        self.assertFalse(row['route_accepted'])
        self.assertEqual(row['proposal_validation']['reason'], 'unknown_edge')
        self.assertFalse(row['task_success'])

    def test_gold_rejection_is_not_a_runtime_interception(self):
        predictions = copy.deepcopy(self.predictions)
        intent = copy.deepcopy(self.cases[0]['gold_intent'])
        intent['hard_max_difficulty'] = 'black'
        predictions[0]['raw_output'] = json.dumps(intent)
        row = self.run_report(predictions)['cases'][0]
        self.assertTrue(row['hard_max_violation'])
        self.assertTrue(row['accepted_route_violates_gold'])
        self.assertFalse(row['safety_intercepted'])
        self.assertFalse(row['task_success'])

    def test_frozen_manifest_and_report_integrity(self):
        changed = copy.deepcopy(self.freeze); changed['cases_sha256'] = 'stale'
        with self.assertRaises(ValueError):
            evaluate(self.cases,self.graphs,[],freeze=changed,manifest=self.manifest())
        report = self.run_report(); report['cases'][0]['task_success'] = False
        with self.assertRaises(ValueError):
            collect_runs([report], ['base'])


class PromotionTests(unittest.TestCase):
    setUp = GranularScoringTests.setUp
    manifest = GranularScoringTests.manifest
    run_report = GranularScoringTests.run_report
    def pair(self, phase='validation', cases=None, selection=None):
        cases = cases or self.cases[:4]
        freeze = {'status':'frozen', 'cases_sha256':digest(cases),
                  'graph_bundle_sha256':digest(self.graphs), 'evaluation_partition':phase}
        preds = [{'id':c['id'], 'raw_output':json.dumps(c['gold_intent']), 'status':'valid', 'stop_reason':'stop'}
                 for c in cases]
        reports = []
        for name, predictions in [('base',preds[2:]),('candidate',preds)]:
            manifest = self.manifest(cases, name)
            if selection:
                manifest['validation_decision_sha256'] = selection['decision_sha256']
            reports.append(evaluate(cases,self.graphs,predictions,freeze=freeze,manifest=manifest))
        return reports

    def regressions(self):
        return {'expected_case_ids':['boundary-fixture'], 'candidate_model_version':'candidate',
                'policy_sha256':digest(POLICY), 'suite_source_sha256':'c'*64,
                'cases':[{'id':'boundary-fixture','passed':True,'accepted_route_violations':0}]}

    def test_validation_threshold_tie_policy_and_diagnostics(self):
        base, candidate = self.pair()
        decision = decide(base,candidate,phase='validation',regressions=self.regressions(),policy=POLICY)
        self.assertEqual(decision['decision'],'eligible_for_final')
        self.assertEqual(decision['additional_successes'],2)
        tied = decide(candidate,candidate,phase='validation',regressions=self.regressions(),policy=POLICY)
        self.assertEqual(tied['decision'],'retain_base')
        historical = decide(self.run_report(),self.run_report(),phase='validation',regressions={},policy=POLICY)
        self.assertIn('candidate_not_primary_validation',historical['reasons'])
        self.assertEqual(json.loads(Path('training/promotion-policy-v1.json').read_text()),POLICY)

    def test_final_requires_locked_selection_and_distinct_set(self):
        base,candidate = self.pair()
        prior = decide(base,candidate,phase='validation',regressions=self.regressions(),policy=POLICY)
        final_base,final_candidate = self.pair('final',self.cases[4:8],prior)
        result = decide(final_base,final_candidate,phase='final',regressions=self.regressions(),policy=POLICY,validation_decision=prior)
        self.assertEqual(result['decision'],'promote_candidate')
        missing = decide(final_base,final_candidate,phase='final',regressions=self.regressions(),policy=POLICY)
        self.assertEqual(missing['decision'],'retain_base')
        self.assertEqual(missing['action'],'reject_candidate_no_retuning_on_final')
        failed = decide(final_candidate,final_base,phase='final',regressions=self.regressions(),policy=POLICY,validation_decision=prior)
        self.assertEqual(failed['decision'],'retain_base')

    def test_failed_missing_or_wrong_candidate_regressions(self):
        base,candidate = self.pair()
        for evidence in ({}, {**self.regressions(),'candidate_model_version':'other'},
                         {**self.regressions(),'cases':[]}):
            result = decide(base,candidate,phase='validation',regressions=evidence,policy=POLICY)
            self.assertEqual(result['decision'],'retain_base')
            self.assertIn('mandatory_regressions_missing_mismatched_or_failed',result['reasons'])

    def test_critical_regression_and_schema_rate_cannot_hide_in_total(self):
        base,candidate = self.pair()
        # Controlled saved-report gate fixture, explicitly rehashed after changing the row.
        candidate['cases'][2]['critical_extraction_failure'] = True
        candidate['report_sha256'] = digest({k:v for k,v in candidate.items() if k != 'report_sha256'})
        result = decide(base,candidate,phase='validation',regressions=self.regressions(),policy=POLICY)
        self.assertIn('new_critical_extraction_regressions',result['reasons'])
        self.assertEqual(result['decision'],'retain_base')

    def test_lower_schema_rate_is_an_independent_gate(self):
        base,candidate = self.pair()
        # Gate fixture: no success threshold can waive a lower syntax/schema rate.
        for row in base['cases']: row['schema_valid'] = True
        candidate['cases'][-1]['schema_valid'] = False
        for report in (base,candidate):
            report['report_sha256'] = digest({k:v for k,v in report.items() if k != 'report_sha256'})
        result = decide(base,candidate,phase='validation',regressions=self.regressions(),policy=POLICY)
        self.assertIn('lower_strict_schema_rate',result['reasons'])
        self.assertEqual(result['decision'],'retain_base')
