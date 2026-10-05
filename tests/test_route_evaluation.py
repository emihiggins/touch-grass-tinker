import copy
import json
from pathlib import Path
import unittest
from liftlap.evaluate import evaluate
from scripts.benchmark import load_cases
ROOT=Path(__file__).resolve().parents[1]

class RouteEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.seed=ROOT/'benchmark/development-seed.jsonl';self.routes=ROOT/'benchmark/route-development.json'
        cases,_=load_cases(self.seed);by_id={c['id']:c for c in cases}
        self.predictions=[{'id':s['id'],'intent':copy.deepcopy(by_id[s['seed_case_id']]['gold_intent'])} for s in json.loads(self.routes.read_text())]
    def test_gold_fixtures_have_expected_route_outcomes(self):
        report=evaluate(self.seed,self.routes,self.predictions)
        self.assertEqual(report['successes'],8)
    def test_satisfying_wrong_extracted_intent_is_not_success(self):
        self.predictions[3]['intent']['hard_max_difficulty']='red'
        result=evaluate(self.seed,self.routes,self.predictions)['cases'][3]
        self.assertEqual(result['planner_status'],'ok')
        self.assertFalse(result['route_valid_against_gold'])
        self.assertFalse(result['success'])
    def test_missing_predictions_not_dropped(self):
        report=evaluate(self.seed,self.routes,[])
        self.assertEqual(report['count'],8);self.assertEqual(report['successes'],0)

if __name__=='__main__':unittest.main()
