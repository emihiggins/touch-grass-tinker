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

    def test_corrupt_shifted_masks_and_tokens_rejected(self):
        import copy
        from liftlap.render_audit import verify_datum
        report, datum = render_case(self.case,self.prompt,self.tokenizer,self.renderer)
        tokens = datum.model_input.to_ints() + [datum.loss_fn_inputs['target_tokens'].to_torch().tolist()[-1]]
        for kind in ('zero', 'prompt', 'nonfinite', 'target'):
            broken = copy.deepcopy(datum)
            key = 'target_tokens' if kind == 'target' else 'weights'
            tensor = broken.loss_fn_inputs[key]
            data = tensor.to_torch().tolist()
            if kind == 'zero': data[:] = [0.] * len(data)
            elif kind == 'prompt': data[0],data[-1] = data[-1],data[0]
            elif kind == 'nonfinite': data[-1] = float('nan')
            else: data[-1] += 1
            from tinker import types
            broken.loss_fn_inputs[key] = types.TensorData(data=data,dtype=tensor.dtype,shape=tensor.shape)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                verify_datum(broken,tokens,report['prompt_tokens'])

    def test_manifest_hashes_bind_actual_datum(self):
        from liftlap.render_audit import datum_payload,value_sha
        report, datum = render_case(self.case,self.prompt,self.tokenizer,self.renderer)
        self.assertEqual(report['sdk_datum_sha256'],value_sha(datum_payload(datum)))
        self.assertTrue(report['decoded_target_suffix'].endswith('<|im_end|>'))
        self.assertEqual(report['weighted_target_range']['end_exclusive'],report['total_tokens']-1)

    def test_all_reviewed_datums_match_sdk_wire_payload(self):
        import asyncio
        import os
        import httpx
        import numpy as np
        from unittest.mock import patch
        from tinker.proto import tinker_public_pb2 as pb
        from tinker.proto.response_conv import _tensor_data_from_proto
        from liftlap.render_audit import datum_payload,value_sha
        from liftlap.tinker_sdk import make_client
        from liftlap.training_transport import TrainingTransport
        cases=read('benchmark/v2/training-reviewed.jsonl')
        config=json.loads(Path('training/experiment-01.json').read_text())
        report,datums=prepare(cases,Path('benchmark/v2/baseline-prompt.txt').read_text(),
                              self.tokenizer,self.renderer,config)
        observed=[]
        def respond(req):
            path=req.url.path.rsplit('/',1)[-1]
            if path=='forward_backward':
                content=req.content
                if req.headers.get('Content-Encoding')=='zstd':
                    import zstandard
                    content=zstandard.ZstdDecompressor().decompress(content)
                wire=pb.ForwardBackwardRequest.FromString(content)
                for row in wire.data:
                    payload={'input_tokens':[token for chunk in row.model_input for token in np.frombuffer(chunk.encoded_text.tokens,dtype=np.int32).tolist()],
                             **{key:_tensor_data_from_proto(row.loss_fn_inputs[key]).to_torch().tolist()
                                for key in ('target_tokens','weights')}}
                    observed.append(value_sha(payload))
                return httpx.Response(200,json={'request_id':'forward'})
            if path=='optim_step':return httpx.Response(200,json={'request_id':'optimizer'})
            if path=='retrieve_future':
                if json.loads(req.content)['request_id']=='forward':
                    return httpx.Response(200,content=pb.ForwardBackwardOutput().SerializeToString(),
                                          headers={'content-type':'application/x-protobuf'})
                return httpx.Response(200,json={'type':'optim_step'})
            raise AssertionError(path)
        async def run(journal):
            async with make_client(httpx.MockTransport(respond)) as client:
                transport=TrainingTransport(client,journal,poll_interval=0)
                transport.model='fixture-model'
                await transport.train_step(datums)
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ,
                {'TINKER_API_KEY':'oc-sent-v2.fixture.end','HTTPS_PROXY':'http://127.0.0.1:1'}):
            asyncio.run(run(Path(directory)/'events.jsonl'))
        self.assertEqual(len(observed),47)
        self.assertEqual(observed,[r['sdk_datum_sha256'] for r in report['cases']])
