import copy,importlib.util,json,unittest
from pathlib import Path
from liftlap.corpus import read
from liftlap.evaluation_v2 import evaluate

class FrozenFinalTests(unittest.TestCase):
    def test_changed_label_or_graph_rejected(self):
        p=Path('benchmark/v2/final-review');cases=read(p/'cases.jsonl');graphs=json.loads((p/'graphs.json').read_text());freeze=json.loads((p/'freeze.json').read_text())
        self.assertEqual(evaluate(cases,graphs,[],freeze=freeze)['count'],16)
        changed=copy.deepcopy(cases);changed[0]['gold_intent']['duration_minutes']=99
        with self.assertRaises(ValueError):evaluate(changed,graphs,[],freeze=freeze)
        bad=copy.deepcopy(freeze);bad['graph_bundle_sha256']='stale'
        with self.assertRaises(ValueError):evaluate(cases,graphs,[],freeze=bad)
    @unittest.skipUnless(importlib.util.find_spec('tinker_cookbook'),'optional dependencies')
    def test_fixed_candidate_fits_reserved_budget(self):
        from liftlap.final_evaluation import prepare
        *_,prompts,m=prepare()
        self.assertEqual(len(prompts),16);self.assertIsNone(m['model_path'])
        self.assertLess(m['upper_estimate_usd'],m['reservation_usd'])
        self.assertEqual(m['model'],'Qwen/Qwen3-8B')
