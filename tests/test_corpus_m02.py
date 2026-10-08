"""M02 diagnostics must not weaken frozen evaluation or review boundaries."""
import copy
import json
from pathlib import Path
import unittest

from liftlap.corpus import read
from liftlap.corpus_m02 import (approval_hash, approved_export, iteration_manifest,
                                label_approved, row_hashes, source_lineage_overlaps)

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

    def test_full_source_overlap_is_explicit(self):
        row = copy.deepcopy(self.cases[0])
        self.assertTrue(source_lineage_overlaps([row], [row]))

    def test_approved_export_requires_v2_and_current_approval(self):
        row = copy.deepcopy(self.cases[0])
        row['gold_intent'] = dict(row['gold_intent'], schema_version=2, avoided_lift_types=[])
        row['review'] = dict(human_reviewed=True, decision='approved', reviewer='Emi Higgins',
                             approval_version='m02-2', reviewed_content_sha256=approval_hash(row))
        with self.assertRaisesRegex(ValueError, 'source overlap'):
            approved_export([row], 'prompt', source_cases=[row])

    def test_approved_export_rejects_unreviewed_packet(self):
        with self.assertRaisesRegex(ValueError, 'approval required'):
            approved_export([self.cases[0]], 'prompt', source_cases=[self.cases[1]])

    def approved_fixture(self):
        row = copy.deepcopy(self.cases[0])
        row['split'] = 'train_candidate'
        row['gold_intent'].update(schema_version=2, avoided_lift_types=[])
        row['review'] = dict(human_reviewed=True, decision='approved', reviewer='test fixture only',
                            approval_version='m02-2', reviewed_content_sha256=approval_hash(row))
        return row

    def test_successful_export_uses_m02_not_legacy_approval(self):
        row = self.approved_fixture()
        before = copy.deepcopy(row)
        result = approved_export([row], 'prompt', source_cases=[self.cases[1]])
        self.assertEqual(json.loads(result[0]['messages'][-1]['content']), row['gold_intent'])
        self.assertEqual(row, before)
        row['gold_intent']['duration_minutes'] += 1
        with self.assertRaisesRegex(ValueError, 'M02 approval required'):
            approved_export([row], 'prompt', source_cases=[self.cases[1]])

    def test_export_requires_sources_and_semantic_consistency(self):
        row = self.approved_fixture()
        with self.assertRaisesRegex(ValueError, 'source corpus audit'):
            approved_export([row], 'prompt')
        row['gold_intent'].update(status='clarify', clarification_fields=['duration_minutes'])
        row['review']['reviewed_content_sha256'] = approval_hash(row)
        with self.assertRaisesRegex(ValueError, 'clarification_retains_value'):
            approved_export([row], 'prompt', source_cases=[self.cases[1]])

    def test_source_audit_detects_family_leakage_and_similar_prose(self):
        row = self.approved_fixture()
        source = copy.deepcopy(row)
        source.update(id='source-test', split='test', request_text=row['request_text'] + ' please')
        issues = source_lineage_overlaps([row], [source])
        self.assertTrue(any('similar-request' in issue for issue in issues))
        self.assertTrue(any('cross-partition-template_family_id' in issue for issue in issues))

    def test_new_packet_is_semantically_valid_blind_and_unapproved(self):
        from liftlap.semantic_contract import validate_intent_semantics
        root = Path('benchmark/iterations/m02-v2-review-2026-10-08')
        rows = read(root / 'candidates.jsonl')
        report = json.loads((root / 'review-manifest.json').read_text())
        import hashlib
        sources = []
        for path, digest in report['source_sha256'].items():
            self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(), digest)
            sources.extend(read(path))
        self.assertEqual(source_lineage_overlaps(rows, sources), report['source_overlap'])
        self.assertEqual(report['source_overlap'], [])
        self.assertEqual(iteration_manifest(rows)['rows'], report['rows'])
        self.assertEqual(len({row['template_family_id'] for row in rows}), 5)
        self.assertEqual(len({row['graph_family_id'] for row in rows}), 1)
        for row in rows:
            self.assertTrue(validate_intent_semantics(row['gold_intent'], {p['id'] for p in row['catalog']}).valid)
            self.assertFalse(label_approved(row))
        blind = (root / 'review-first.md').read_text()
        self.assertNotIn('gold_intent', blind)
        self.assertNotIn('approval hash:', blind)
        with self.assertRaisesRegex(ValueError, 'M02 approval required'):
            approved_export(rows, 'prompt', source_cases=sources)

    def test_cli_approved_export_succeeds_and_unapproved_writes_nothing(self):
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = self.approved_fixture()
            packet, source, output = (root / name for name in ('packet.jsonl', 'source.jsonl', 'out.jsonl'))
            packet.write_text(json.dumps(row) + '\n')
            source.write_text(json.dumps(self.cases[1]) + '\n')
            command = [sys.executable, 'scripts/m02_review.py', str(packet), '--source', str(source), '--export', str(output)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(len(read(output)), 1)
            output.unlink()
            row['review']['decision'] = 'pending'
            packet.write_text(json.dumps(row) + '\n')
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(output.exists())
