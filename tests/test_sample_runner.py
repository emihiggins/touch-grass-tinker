import asyncio
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from liftlap.corpus import read
from liftlap.sample_runner import parse_output,estimate,run_cases,SDKSampler

class RunnerTests(unittest.TestCase):
    def setUp(self):self.case=read('benchmark/development-seed.jsonl')[0]
    def test_strict_json_and_truncation(self):
        text=json.dumps(self.case['gold_intent'])
        self.assertEqual(parse_output(text,'stop',self.case['catalog'])[1],'valid')
        self.assertIsNone(parse_output(text,'length',self.case['catalog'])[0])
        self.assertIsNone(parse_output('```json\n'+text+'\n```','stop',self.case['catalog'])[0])
        self.assertIsNone(parse_output(text[:-1]+',"status":"ready"}','stop',self.case['catalog'])[0])
    def test_estimate(self):
        self.assertAlmostEqual(estimate([[1]*10,[2]*20],50,1,2),.00023)
        for rate in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):estimate([[1]],10,rate,1)
    def test_transport_failure_halts_and_keeps_denominator(self):
        class Failing:
            calls=0
            async def sample(self,*args):self.calls+=1;raise RuntimeError('sensitive message')
        sampler=Failing()
        class Tokenizer:
            def decode(self,x):return ''
        with tempfile.TemporaryDirectory() as d:
            rows=asyncio.run(run_cases([self.case,self.case],[[1],[2]],Tokenizer(),[],sampler,Path(d),'test'))
            self.assertEqual(sampler.calls,1);self.assertEqual(len(rows),2)
            self.assertEqual(rows[1]['status'],'not_attempted_after_transport_failure')
            self.assertNotIn('sensitive',Path(d,'predictions.jsonl').read_text())
    def test_bad_answer_not_retried(self):
        class Bad:
            calls=0
            async def sample(self,tokens,key,callback):
                self.calls+=1;callback('future-test');return {'tokens':[1],'stop_reason':'stop','request_id':'future-test'}
        class Tokenizer:
            def decode(self,x):return 'not json'
        sampler=Bad()
        with tempfile.TemporaryDirectory() as d:
            rows=asyncio.run(run_cases([self.case],[[1]],Tokenizer(),[],sampler,Path(d),'test'))
            self.assertEqual(sampler.calls,1);self.assertIsNone(rows[0]['intent'])
            self.assertEqual(rows[0]['raw_output'],'not json')

@unittest.skipUnless(importlib.util.find_spec('tinker'),'optional SDK required')
class SDKSamplingTests(unittest.TestCase):
    @patch.dict(os.environ,{'TINKER_API_KEY':'oc-sent-v2.fixture.end','HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_submission_pending_then_real_proto_decode(self):
        import httpx,numpy as np
        from tinker.proto import tinker_public_pb2 as pb
        from liftlap.tinker_sdk import make_client
        wire=pb.SampleResponse();seq=wire.sequences.add();seq.tokens=np.array([10,20],dtype=np.int32).tobytes();seq.stop_reason=pb.STOP_REASON_STOP
        calls=[]
        def respond(req):
            calls.append(req)
            if req.url.path.endswith('/create_session'):return httpx.Response(200,json={'session_id':'session-1'})
            if req.url.path.endswith('/create_sampling_session'):return httpx.Response(200,json={'sampling_session_id':'sampling-1'})
            if req.url.path.endswith('/session_heartbeat'):return httpx.Response(200,json={})
            if req.url.path.endswith('/asample'):return httpx.Response(200,json={'request_id':'future-1'})
            if len(calls)==5:return httpx.Response(200,json={'type':'try_again','request_id':'future-1','queue_state':'active'})
            return httpx.Response(200,content=wire.SerializeToString(),headers={'Content-Type':'application/x-protobuf'})
        async def execute():
            submitted=[]
            async with make_client(httpx.MockTransport(respond)) as client:
                r=await SDKSampler(client,'Qwen/Qwen3-8B',None,[151645],512,poll_interval=0).sample([1,2],'run-1',submitted.append)
            self.assertEqual(r['tokens'],[10,20]);self.assertEqual(submitted,['future-1'])
        asyncio.run(execute())
        body=json.loads(calls[3].content)
        self.assertEqual(body['sampling_session_id'],'sampling-1');self.assertEqual(body['seq_id'],0)
        self.assertEqual(body['num_samples'],1);self.assertEqual(body['sampling_params']['max_tokens'],512)
        self.assertEqual(calls[3].headers['X-Idempotency-Key'],'run-1')
        self.assertEqual(calls[3].headers['X-Tinker-Sampling-Backpressure'],'1')
        self.assertEqual(len(calls),6)
    @patch.dict(os.environ,{'TINKER_API_KEY':'oc-sent-v2.fixture.end','HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_pending_poll_bound(self):
        import httpx
        from liftlap.tinker_sdk import make_client
        calls=[]
        def respond(req):
            calls.append(req)
            if req.url.path.endswith('/create_session'):return httpx.Response(200,json={'session_id':'session-2'})
            if req.url.path.endswith('/create_sampling_session'):return httpx.Response(200,json={'sampling_session_id':'sampling-2'})
            if req.url.path.endswith('/session_heartbeat'):return httpx.Response(200,json={})
            return httpx.Response(200,json={'request_id':'future-2'} if req.url.path.endswith('/asample') else {'type':'try_again'})
        async def execute():
            async with make_client(httpx.MockTransport(respond)) as client:
                with self.assertRaises(TimeoutError):
                    await SDKSampler(client,'Qwen/Qwen3-8B',None,[151645],512,polls=2,poll_interval=0).sample([1],'run-2',lambda _:None)
        asyncio.run(execute());self.assertEqual(len(calls),6)

class DecodeStopTests(unittest.TestCase):
    def test_only_terminal_stop_token_is_removed(self):
        from liftlap.sample_runner import decode_sample
        class Tokens:
            def decode(self,ids):return repr(ids)
        self.assertEqual(decode_sample(Tokens(),[1,9],[9]),'[1]')
        self.assertEqual(decode_sample(Tokens(),[9,1],[9]),'[9, 1]')
        self.assertEqual(decode_sample(Tokens(),[1],[]),'[1]')
