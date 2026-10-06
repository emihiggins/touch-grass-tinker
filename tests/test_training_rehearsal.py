import copy
import importlib.util
import unittest
from liftlap.training_rehearsal import rehearse

AVAILABLE = bool(importlib.util.find_spec('tinker_cookbook'))


class RehearsalBoundaryTests(unittest.TestCase):
    def test_tail_rejected_before_optional_import(self):
        with self.assertRaisesRegex(ValueError, 'drop final rows'):
            rehearse([{'id': str(i), 'split': 'train_candidate'} for i in range(48)],
                     [None] * 48, {'batch_size': 32, 'epochs': 1}, {})

    def test_development_cannot_enter_training(self):
        with self.assertRaisesRegex(ValueError, 'Development/test'):
            rehearse([{'id': 'dev', 'split': 'test'}], [None],
                     {'batch_size': 1, 'epochs': 1}, {})

    def test_invalid_batch_configuration(self):
        for size in (0, -1, True, 1.5):
            with self.subTest(size=size), self.assertRaises(ValueError):
                rehearse([{'id': 'a', 'split': 'train_candidate'}], [None],
                         {'batch_size': size, 'epochs': 1}, {})


@unittest.skipUnless(AVAILABLE, 'optional Cookbook environment required')
class CookbookRehearsalTests(unittest.TestCase):
    def setUp(self):
        import tinker
        from tinker import types
        self.cases = [{'id': str(i), 'split': 'train_candidate'} for i in range(6)]
        self.datums = [types.Datum(model_input=tinker.ModelInput.from_ints([i + 1]),
                                   loss_fn_inputs={'target_tokens': [i + 2], 'weights': [1.]})
                       for i in range(6)]
        self.config = {'batch_size': 2, 'epochs': 2}

    def run_plan(self, **kwargs):
        return rehearse(self.cases, self.datums, self.config, {'prompt': 'test-hash'}, **kwargs)

    def test_actual_cookbook_batches_cover_each_epoch_once(self):
        report = self.run_plan()
        self.assertEqual(report['steps'], 6)
        for epoch in (0, 1):
            ids = [cid for b in report['batches'] if b['epoch'] == epoch for cid in b['ids']]
            self.assertEqual(sorted(ids), [str(i) for i in range(6)])
        self.assertFalse(report['launch_authorized'])
        self.assertFalse(report['candidate_labels_human_approved'])

    def test_resume_preserves_suffix_and_is_deterministic(self):
        full = self.run_plan()
        self.assertEqual(full, self.run_plan())
        for cursor in (1, 3, 6):
            result = self.run_plan(start_step=cursor, expected_plan_sha256=full['plan_sha256'])
            expected = [cid for b in full['batches'][cursor:] for cid in b['ids']]
            self.assertEqual(result['remaining_ids'], expected)
            self.assertFalse(result['checkpoint_loaded'])

    def test_resume_rejects_changed_labels_or_config(self):
        full = self.run_plan()
        original = copy.deepcopy(self.cases)
        self.cases[0]['label'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'plan mismatch'):
            self.run_plan(start_step=1, expected_plan_sha256=full['plan_sha256'])
        self.cases = original
        self.config['epochs'] = 1
        with self.assertRaisesRegex(ValueError, 'plan mismatch'):
            self.run_plan(start_step=1, expected_plan_sha256=full['plan_sha256'])

    def test_resume_requires_hash_and_valid_bounds(self):
        with self.assertRaisesRegex(ValueError, 'original plan hash'):
            self.run_plan(start_step=1)
        full = self.run_plan()
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            self.run_plan(start_step=7, expected_plan_sha256=full['plan_sha256'])
