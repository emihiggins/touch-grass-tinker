import copy
import unittest
from liftlap.corpus import read, label_approved, export
from liftlap.training_preflight import check
import json
from pathlib import Path

class HumanReviewTests(unittest.TestCase):
    def setUp(self):
        self.cases=read('benchmark/training-candidates.jsonl')

    def test_review_is_not_blanket_approval(self):
        self.assertEqual(sum(c['review']['human_reviewed'] for c in self.cases),48)
        self.assertEqual(sum(c['review']['decision']=='approved' for c in self.cases),41)
        self.assertEqual(sum(label_approved(c) for c in self.cases),40)
        for n in (4,5,9,13,28,32,36,43):
            self.assertFalse(label_approved(self.cases[n-1]))

    def test_quarantine_and_disputes_cannot_be_promoted(self):
        config=json.loads(Path('training/sft-plan.json').read_text())
        for n in (4,5,9,13,28,32,36,43):
            row=copy.deepcopy(self.cases[n-1]);row['split']='train'
            with self.subTest(case=n):
                with self.assertRaises(ValueError):export([row],'prompt')
                self.assertTrue(any('approved' in e or 'approval' in e for e in check([row],config)['blockers']))

    def test_editing_reviewed_content_invalidates_approval(self):
        for field in ('gold_intent','request_text','ui_context','catalog'):
            row=copy.deepcopy(self.cases[0])
            if field=='gold_intent':row[field]['duration_minutes']=60
            elif field=='request_text':row[field]+=' No t-bars.'
            elif field=='ui_context':row[field]['finish_place_id']='ridge'
            else:row[field][0]['label']='Changed place'
            self.assertFalse(label_approved(row),field)

    def test_explicit_approved_label_export_and_no_review_leakage(self):
        row=copy.deepcopy(self.cases[0]);row['split']='train'
        result=export([row],'prompt')
        self.assertEqual(len(result),1)
        self.assertNotIn('Emi Higgins',json.dumps(result))
        self.assertNotIn('human_note',json.dumps(result))

    def test_duration_corrections_retained_without_invalid_v1_gold(self):
        for n,value in ((13,300),(28,10)):
            row=self.cases[n-1]
            self.assertEqual(row['review']['requested_changes']['duration_minutes'],value)
            self.assertEqual(row['review']['decision'],'change_requested')
            self.assertIsNone(row['gold_intent']['duration_minutes'])
