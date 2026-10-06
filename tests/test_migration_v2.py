import copy,json,unittest
from pathlib import Path
from liftlap.corpus import read,audit,export,label_approved,review_hash
from liftlap.core import digest
from liftlap.evaluation_v2 import evaluate
from scripts.migrate_v2 import migrate

class MigrationTests(unittest.TestCase):
    def test_migration_is_reproducible_and_quarantine_excluded(self):
        original=read('benchmark/training-candidates.jsonl')
        actual=read('benchmark/v2/training-reviewed.jsonl')
        self.assertEqual([migrate(c,True) for c in original if c['id']!='train-candidate-009'],actual)
        self.assertEqual(len(actual),47);self.assertTrue(all(label_approved(c) for c in actual))
        report=audit(actual+read('benchmark/v2/development.jsonl')+read('benchmark/v2/evaluation-candidates.jsonl'))
        self.assertEqual(report['errors'],[]);self.assertEqual(report['warnings'],[])
        self.assertEqual(len(export(actual,'prompt')),47)
    def test_migration_rejects_changed_or_quarantined_source(self):
        source=read("benchmark/training-candidates.jsonl")
        changed=copy.deepcopy(source[0]);changed["request_text"]+=" Changed."
        for row in (changed,source[8]):
            with self.assertRaises(ValueError):migrate(row,True)

    def test_requested_labels_now_valid_v2(self):
        rows={c['id']:c for c in read('benchmark/v2/training-reviewed.jsonl')}
        for n,value in [(13,300),(28,10)]:
            g=rows[f'train-candidate-{n:03}']['gold_intent']
            self.assertEqual(g['duration_minutes'],value);self.assertEqual(g['status'],'ready')
        for n in (5,8,14,38,46,48):
            g=rows[f'train-candidate-{n:03}']['gold_intent']
            self.assertTrue(g['avoided_lift_types']);self.assertEqual(g['excluded_lift_types'],[])
    def test_evaluation_candidates_are_not_training_or_frozen_test(self):
        cases=read('benchmark/v2/evaluation-candidates.jsonl')
        bundles=json.loads(Path('benchmark/v2/evaluation-graphs.json').read_text())
        with self.assertRaises(ValueError):export(cases,'prompt')
        with self.assertRaisesRegex(ValueError,'human-approved'):evaluate(cases,bundles,[])
        report=evaluate(cases,bundles,None,fixture_self_check=True)
        self.assertEqual(report['successes'],16)
        self.assertEqual(report['scope'],'fixture_self_check_not_model_performance')

    def test_frozen_scoring_rejects_changed_graph_and_counts_missing_outputs(self):
        cases=read('benchmark/v2/evaluation-candidates.jsonl')
        bundles=json.loads(Path('benchmark/v2/evaluation-graphs.json').read_text())
        # Test-only simulated approval: canonical candidate files remain unreviewed.
        for row in cases:
            row['split']='test';row['review'].update(human_reviewed=True,decision='approved',reviewed_content_sha256=review_hash(row))
        freeze={'status':'frozen','cases_sha256':digest(cases),'graph_bundle_sha256':digest(bundles)}
        report=evaluate(cases,bundles,[],freeze=freeze)
        self.assertEqual(report['count'],16);self.assertEqual(report['successes'],0)
        bundles['fork']['graph']['edges'][0]['duration_s']+=1
        with self.assertRaisesRegex(ValueError,'freeze'):evaluate(cases,bundles,[],freeze=freeze)
