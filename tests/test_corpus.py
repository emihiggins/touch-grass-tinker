import copy
import unittest
from liftlap.corpus import audit, export, read, conversation
from liftlap.corpus_m02 import iteration_manifest, row_hashes
from liftlap.compare import compare

class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.cases = read('benchmark/training-candidates.jsonl')
    def test_current_corpora(self):
        self.assertEqual(audit(self.cases + read('benchmark/development-seed.jsonl'))['errors'], [])
    def test_leaked_template_rejected(self):
        cases=copy.deepcopy(self.cases); cases[1]['template_family_id']=cases[0]['template_family_id']; cases[1]['split']='development'
        self.assertTrue(any('cross-split template' in e for e in audit(cases)['errors']))
    def test_leaked_graph_rejected(self):
        cases=copy.deepcopy(self.cases); cases[1]['split']='development'
        self.assertTrue(any('cross-split graph' in e for e in audit(cases)['errors']))
    def test_no_unreviewed_test(self):
        c=copy.deepcopy(self.cases[0]);c['split']='test';c['review']['human_reviewed']=False
        self.assertTrue(audit([c])['errors'])
    def test_normalized_duplicate(self):
        c=copy.deepcopy(self.cases[0]);c['id']='copy';c['request_text']=c['request_text'].upper()+'!!!'
        self.assertTrue(audit([self.cases[0],c])['errors'])
    def test_no_dev_training_export(self):
        with self.assertRaises(ValueError):export(read('benchmark/development-seed.jsonl'),'prompt')
    def test_no_unreviewed_training_export(self):
        c=copy.deepcopy(self.cases[0]);c['split']='train';c['review']['human_reviewed']=False
        with self.assertRaises(ValueError):export([c],'prompt')
    def test_preview_and_inference_separation(self):
        rows=export(self.cases,'prompt',preview=True)
        self.assertEqual(len(rows),len(self.cases))
        self.assertEqual([m['role'] for m in rows[0]['messages']],['system','user','assistant'])
        self.assertNotIn('gold_intent',rows[0]['messages'][1]['content'])
        self.assertEqual(len(conversation(self.cases[0],'prompt',target=False)['messages']),2)
    def test_iteration_manifest_is_review_only_and_hashes_material(self):
        cases = read('benchmark/iterations/m02-2026-10-08/training-review-packet.jsonl')
        manifest = iteration_manifest(cases)
        self.assertEqual(manifest['status'], 'review-required; not training-ready')
        self.assertEqual(manifest['candidate_count'], 12)
        self.assertEqual(manifest['split_counts'], {'training_candidate': 12})
        self.assertTrue(all(row['review_state'] == 'unapproved' for row in manifest['rows']))
        self.assertEqual(set(row_hashes(cases[0])), {'request_sha256', 'context_sha256', 'catalog_constraints_sha256', 'graph_sha256', 'label_sha256'})
        self.assertIn('sparse_or_missing', manifest['coverage'])

    def test_paired_missing_output_is_failure(self):
        c=self.cases[:2];pred=[{'id':x['id'],'intent':x['gold_intent']} for x in c]
        r=compare(c,pred,pred[:1],draws=100)
        self.assertEqual(r['delta_percentage_points'],-50)
        self.assertEqual(r['tuned']['invalid'],1)
    def test_duplicate_prediction_rejected(self):
        c=self.cases[:1];p={'id':c[0]['id'],'intent':c[0]['gold_intent']}
        with self.assertRaises(ValueError): compare(c,[p,p],[p],draws=100)
    def test_identical_predictions_zero_interval(self):
        p=[{'id':x['id'],'intent':x['gold_intent']} for x in self.cases]
        r=compare(self.cases,p,p,draws=100)
        self.assertEqual(r['paired_template_cluster_bootstrap']['interval_95_percentage_points'],[0,0])

if __name__=='__main__':unittest.main()
