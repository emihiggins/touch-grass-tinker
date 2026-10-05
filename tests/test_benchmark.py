import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('benchmark', ROOT/'scripts/benchmark.py')
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, _ = b.load_cases(ROOT/'benchmark/development-seed.jsonl')

    def test_missing_predictions_count_as_failures(self):
        result = b.score(self.cases, [])
        self.assertEqual(result['invalid'],32)
        self.assertEqual(result['correct'],0)

    def test_gold_roundtrip_is_scorer_self_test_not_model_result(self):
        predictions=[{'id':c['id'],'intent':c['gold_intent']} for c in self.cases]
        self.assertEqual(b.score(self.cases,predictions)['correct'],32)

    def test_weakened_hard_constraint_fails_even_valid_json(self):
        c=self.cases[1];x=copy.deepcopy(c['gold_intent']);x['hard_max_difficulty']='black'
        row=b.score([c],[{'id':c['id'],'intent':x}])['cases'][0]
        self.assertTrue(row['valid']);self.assertFalse(row['exact_match'])
        self.assertIn('hard_max_difficulty',row['mismatched_fields'])

    def test_magic_carpet_exclusion_not_silently_equivalent_to_drag(self):
        c=self.cases[4];x=copy.deepcopy(c['gold_intent']);x['excluded_lift_types'].append('magic-carpet')
        self.assertEqual(b.score([c],[{'id':c['id'],'intent':x}])['correct'],0)

    def test_list_order_and_equivalent_timezones_normalize(self):
        c=self.cases[4];x=copy.deepcopy(c['gold_intent']);x['excluded_lift_types'].reverse()
        x['start_time']='2027-01-15T09:00:00+00:00'
        self.assertEqual(b.score([c],[{'id':c['id'],'intent':x}])['correct'],1)

    def test_invalid_outputs_are_rejected(self):
        base=self.cases[0]['gold_intent']
        edits=[{'rogue':True},{'start_place_id':'invented'},{'duration_minutes':True},
               {'start_time':'2027-01-15T10:00:00'},{'duration_minutes':None},
               {'excluded_lift_types':['gondola','gondola']},{'schema_version':True}]
        for changes in edits:
            with self.subTest(changes=changes):
                x=copy.deepcopy(base);x.update(changes)
                self.assertEqual(b.score([self.cases[0]],[{'id':self.cases[0]['id'],'intent':x}])['invalid'],1)

    def test_duplicate_and_unknown_predictions_fail(self):
        c=self.cases[0];p={'id':c['id'],'intent':c['gold_intent']}
        with self.assertRaises(ValueError):b.score([c],[p,p])
        with self.assertRaises(ValueError):b.score([c],[{'id':'not-a-case','intent':p['intent']}])

    def test_clarification_cannot_be_ready_without_resolution(self):
        c=self.cases[20];x=copy.deepcopy(c['gold_intent']);x['status']='ready'
        self.assertEqual(b.score([c],[{'id':c['id'],'intent':x}])['invalid'],1)

if __name__=='__main__':unittest.main()
