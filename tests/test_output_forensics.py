import copy
import unittest
from liftlap.corpus import read
from liftlap.output_forensics import inspect_outputs


class OutputForensicsTests(unittest.TestCase):
    def setUp(self):
        self.cases = read('benchmark/v2/evaluation-pilot-frozen.jsonl')
        self.predictions = read('research/evidence/experiment-01/trained-predictions.jsonl')

    def test_all_six_failures_preserved_without_repairs(self):
        original = copy.deepcopy(self.predictions)
        report = inspect_outputs(self.cases, self.predictions)
        self.assertEqual(report['count'], 16)
        self.assertEqual(report['observations']['json_object_followed_by_quote'], 5)
        self.assertEqual(report['observations']['schema_rejection'], 1)
        failures = [r for r in report['cases'] if not r['strict_schema']]
        self.assertTrue(all(r['stop_reason'] == 'stop' and not r['at_output_cap'] for r in failures))
        self.assertEqual(self.predictions, original)
        self.assertEqual(report['repairs_applied'], 0)

    def test_base_failure_fields(self):
        report = inspect_outputs(read('benchmark/v2/final-review/cases.jsonl'),
                                 read('research/evidence/fresh-base-evaluation/predictions.jsonl'))
        failures = {r['id']: r['field_differences'] for r in report['cases'] if r['field_differences']}
        self.assertEqual(failures, {'final-review-005': ['excluded_lift_types'],
                                   'final-review-010': ['clarification_fields', 'status'],
                                   'final-review-012': ['duration_minutes']})

    def test_missing_duplicate_unknown_and_nonobject(self):
        self.assertEqual(inspect_outputs(self.cases, [])['observations'], {'missing_raw_output': 16})
        with self.assertRaises(ValueError):
            inspect_outputs(self.cases, self.predictions + self.predictions[:1])
        with self.assertRaises(ValueError):
            inspect_outputs(self.cases, [{'id': 'unknown'}])
        report = inspect_outputs(self.cases[:1], [{'id': self.cases[0]['id'], 'raw_output': '[]'}])
        self.assertEqual(report['observations'], {'schema_rejection': 1})
