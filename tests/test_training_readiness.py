import copy
import json
from pathlib import Path
import unittest
from liftlap.corpus import read
from liftlap.training_preflight import check,GATES
from liftlap.request_compare import compare

class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.cases=read('benchmark/training-candidates.jsonl')
        self.config=json.loads(Path('training/sft-plan.json').read_text())
    def test_current_not_ready(self):
        r=check(self.cases,self.config)
        self.assertFalse(r['launch_authorized']);self.assertEqual(r['approved_train_count'],0)
        self.assertIn('Training would execute zero complete batches',r['blockers'])
    def test_final_batch_loss_reported(self):
        c=copy.deepcopy(self.cases)
        for row in c:row['split']='train';row['review']['human_reviewed']=True
        self.config['batch_size']=10
        r=check(c,self.config)
        self.assertEqual(r['dropped_rows_per_epoch'],6);self.assertEqual(r['complete_batches_per_epoch'],1)
    def test_invalid_batch_no_crash(self):
        for batch in (0,True,-1,'32'):
            self.config['batch_size']=batch
            self.assertIn('batch_size must be a positive integer',check(self.cases,self.config)['blockers'])
    def test_claimed_gates_do_not_authorize(self):
        self.config['launch_gates']={g:True for g in GATES}
        r=check(self.cases,self.config)
        self.assertFalse(r['launch_authorized']);self.assertTrue(r['blockers'])

class PairedRequestTests(unittest.TestCase):
    def setUp(self):
        self.seed='benchmark/development-seed.jsonl';self.spec='benchmark/request-development.json'
        cases={c['id']:c for c in read(self.seed)}
        self.preds=[{'id':s['id'],'intent':copy.deepcopy(cases[s['seed_case_id']]['gold_intent'])} for s in json.loads(Path(self.spec).read_text())]
    def test_identical_zero_delta(self):
        r=compare(self.seed,self.spec,self.preds,self.preds,draws=100)
        self.assertEqual(r['transitions']['both_success'],20)
        self.assertEqual(r['paired_family_bootstrap']['interval_95_percentage_points'],[0,0])
    def test_regression_and_hard_violation_visible(self):
        tuned=copy.deepcopy(self.preds);tuned[3]['intent']['hard_max_difficulty']='red'
        r=compare(self.seed,self.spec,self.preds,tuned,draws=100)
        self.assertEqual(r['transitions']['regressed'],1);self.assertEqual(r['delta_percentage_points'],-5)
        self.assertEqual(r['gold_route_rejections']['tuned'],1)
    def test_missing_rows_are_failures(self):
        r=compare(self.seed,self.spec,self.preds,[],draws=100)
        self.assertEqual(r['tuned_successes'],0);self.assertEqual(r['transitions']['regressed'],20)
    def test_deterministic(self):
        self.assertEqual(compare(self.seed,self.spec,self.preds,self.preds[:10],draws=100),compare(self.seed,self.spec,self.preds,self.preds[:10],draws=100))
