import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from liftlap.evaluate import evaluate
from liftlap.corpus import read

class RequestEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.seed='benchmark/development-seed.jsonl';self.spec='benchmark/request-development.json'
        by_id={c['id']:c for c in read(self.seed)}
        self.specs=json.loads(Path(self.spec).read_text())
        self.preds=[{'id':s['id'],'intent':copy.deepcopy(by_id[s['seed_case_id']]['gold_intent'])} for s in self.specs]
    def test_gold_fixture_replay(self):
        r=evaluate(self.seed,self.spec,self.preds)
        self.assertEqual(r['successes'],20)
        self.assertEqual(r['by_expected_outcome']['clarify']['count'],8)
        self.assertEqual(r['by_expected_outcome']['unsupported']['count'],4)
    def test_nonplanning_never_calls_planner(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'specs.json';p.write_text(json.dumps(self.specs[8:]))
            with patch('liftlap.evaluate.plan',side_effect=AssertionError('must not plan')):
                self.assertEqual(evaluate(self.seed,p,self.preds[8:])['successes'],12)
    def test_wrong_clarification_fails(self):
        self.preds[8]['intent']['clarification_fields']=['duration_minutes']
        self.assertFalse(evaluate(self.seed,self.spec,self.preds)['cases'][8]['success'])
    def test_missing_unsupported_fails(self):
        self.preds[14]['intent']['unsupported_preferences']=[]
        self.assertFalse(evaluate(self.seed,self.spec,self.preds)['cases'][14]['success'])
    def test_duplicate_scenarios_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'specs.json';p.write_text(json.dumps([self.specs[0]]*2))
            with self.assertRaises(ValueError):evaluate(self.seed,p,[])
