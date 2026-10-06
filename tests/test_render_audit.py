import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from liftlap.corpus import read
from liftlap.render_audit import load_renderer,render_case,prepare

AVAILABLE=bool(importlib.util.find_spec('tinker_cookbook')) and Path('.tokenizer-qwen3/tokenizer.json').exists()

@unittest.skipUnless(AVAILABLE,'optional Cookbook and pinned tokenizer assets required')
class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokenizer,cls.renderer=load_renderer('.tokenizer-qwen3','training/tokenizer-manifest.json')
        cls.case=read('benchmark/training-candidates.jsonl')[0]
        cls.prompt=Path('benchmark/baseline-prompt.txt').read_text()
    def test_mask_alignment_and_roundtrip(self):
        r,d=render_case(self.case,self.prompt,self.tokenizer,self.renderer)
        self.assertEqual(r['prompt_loss_tokens'],0);self.assertTrue(r['next_token_alignment'])
        self.assertLess(r['answer_tokens'],512)
        self.assertEqual(len(d.model_input.to_ints()),r['total_tokens']-1)
    def test_overlength_rejected_not_truncated(self):
        with self.assertRaisesRegex(ValueError,'refusing truncation'):
            render_case(self.case,self.prompt,self.tokenizer,self.renderer,max_length=100)
    def test_output_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,'output budget'):
            render_case(self.case,self.prompt,self.tokenizer,self.renderer,max_output=5)
    def test_changed_tokenizer_manifest_rejected(self):
        manifest=json.loads(Path('training/tokenizer-manifest.json').read_text())
        manifest['files']['tokenizer.json']['sha256']='0'*64
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'manifest.json';p.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'checksum mismatch'):load_renderer('.tokenizer-qwen3',p)
    def test_batch_preview_never_authorizes(self):
        config=json.loads(Path('training/sft-plan.json').read_text())
        report,_=prepare([self.case],self.prompt,self.tokenizer,self.renderer,config)
        self.assertEqual(report['batch_preview']['complete_batches'],0)
        self.assertFalse(report['batch_preview']['launch_authorized'])
