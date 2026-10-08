"""M02 diagnostics must not weaken frozen evaluation or review boundaries."""
import copy
import json
from pathlib import Path
import unittest

from liftlap.corpus import read
from liftlap.corpus_m02 import approval_hash, iteration_manifest, label_approved, row_hashes

PACKET = 'benchmark/iterations/m02-2026-10-08/training-review-packet.jsonl'


class M02Tests(unittest.TestCase):
    def setUp(self):
        self.cases = read(PACKET)

    def test_approval_binds_lineage_split_graph_and_constraints(self):
        row = self.cases[0]
        row['review'] = dict(human_reviewed=True, decision='approved', reviewer='fixture',
                             approval_version='m02-2', reviewed_content_sha256=approval_hash(row))
        self.assertTrue(label_approved(row))
        for key, value in [('family_id', 'new'), ('split', 'final'), ('graph', {'nodes': []}),
                           ('edge_overrides', {'lift': 'closed'}), ('provenance', {'source': 'new'})]:
            changed = copy.deepcopy(row)
            changed[key] = value
            with self.subTest(key=key):
                self.assertFalse(label_approved(changed))
        row['review']['approval_version'] = 'legacy'
        self.assertFalse(label_approved(row))

    def test_partition_aliases_and_historical_source_leakage(self):
        a, b = self.cases[:2]
        b['family_id'] = a['family_id']
        b['split'] = 'train_candidate'
        self.assertEqual(iteration_manifest([a, b])['family_overlap'], [])
        b['split'] = 'validation_candidate'
        b['provenance']['historical_source_id'] = a['provenance']['historical_source_id']
        result = iteration_manifest([a, b])
        self.assertTrue(result['family_overlap'])
        self.assertTrue(any('historical source' in e for e in result['blocking_errors']))

    def test_audit_errors_duplicates_and_packet_limit_are_not_discarded(self):
        cases = [copy.deepcopy(self.cases[0]), copy.deepcopy(self.cases[0])]
        cases[1]['gold_intent']['status'] = 'invalid'
        result = iteration_manifest(cases, packet_size=1)
        for expected in ['duplicate id:', 'duplicate text:', 'invalid intent:', 'packet exceeds']:
            self.assertTrue(any(expected in e for e in result['blocking_errors']), expected)
        self.assertFalse(result['training_export_supported'])

    def test_graph_absence_is_not_catalog_hash(self):
        hashes = row_hashes(self.cases[0])
        self.assertIsNone(hashes['graph_sha256'])
        row = copy.deepcopy(self.cases[0])
        row['graph'] = {'nodes': ['a'], 'edges': []}
        initial = row_hashes(row)['graph_sha256']
        self.assertIsNotNone(initial)
        row['graph']['nodes'].append('b')
        self.assertNotEqual(row_hashes(row)['graph_sha256'], initial)

    def test_revised_manifest_reproduces_and_does_not_mutate_packet(self):
        before = copy.deepcopy(self.cases)
        result = iteration_manifest(self.cases)
        self.assertEqual(self.cases, before)
        self.assertEqual(result, json.loads(Path(PACKET).with_name('iteration-manifest-v2.json').read_text()))
        self.assertEqual(len(result['blocking_errors']), 12)
        self.assertTrue(all(r['review_state'] == 'unapproved' for r in result['rows']))
