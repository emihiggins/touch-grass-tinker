import copy
import json
from pathlib import Path
import unittest
from liftlap.corpus import read
from scripts.analyze_experiment02 import generate, inspect_output


class PostmortemTests(unittest.TestCase):
    def test_evidence_reproduces_without_rescoring(self):
        expected=json.loads(Path('research/evidence/experiment-02/postmortem.json').read_text())
        self.assertEqual(generate(),expected)
        for arm in expected['arms'].values():
            self.assertEqual(arm['count'],16)
            self.assertEqual(arm['task_successes'],10)
        self.assertEqual(expected['arms']['base']['accepted_routes_violating_reviewed_constraints'],4)
        self.assertEqual(expected['arms']['trained']['accepted_routes_violating_reviewed_constraints'],2)
        self.assertEqual(expected['arms']['trained']['forensic_prefixes_still_wrong'],2)

    def test_prefix_is_forensics_only_and_does_not_hide_wrong_constraints(self):
        case=read('benchmark/v2/evaluation-pilot-frozen.jsonl')[5]
        wrong=copy.deepcopy(case['gold_intent']);wrong['excluded_lift_types']=[]
        raw=json.dumps(wrong)+'"'
        result=inspect_output(raw,case['catalog'],case['gold_intent'])
        self.assertFalse(result['strict_json'])
        self.assertTrue(result['prefix_only_forensics'])
        self.assertEqual(result['trailing_suffix'],'"')
        self.assertIn('excluded_lift_types',[m['field'] for m in result['field_mismatches']])
        self.assertNotIn('intent',result)

    def test_duplicates_and_unparseable_output_are_not_salvaged(self):
        case=read('benchmark/v2/evaluation-pilot-frozen.jsonl')[0]
        for raw in ('{"status":"ready","status":"clarify"}', 'not JSON', None):
            result=inspect_output(raw,case['catalog'],case['gold_intent'])
            self.assertFalse(result['strict_json'])
            self.assertFalse(result['prefix_only_forensics'])
