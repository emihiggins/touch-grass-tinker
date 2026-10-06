import asyncio,importlib.util,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

@unittest.skipUnless(importlib.util.find_spec('tinker'),'optional pinned SDK required')
class TrainingTransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.journal=Path(self.tmp.name)/'events.jsonl'
    @patch.dict(os.environ,{'TINKER_API_KEY':'oc-sent-v2.fixture.end','HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_checkpoint_restore_wire_sequence_and_expiration(self):
        import httpx
        from liftlap.tinker_sdk import make_client
        from liftlap.training_transport import TrainingTransport
        requests=[];pending={};index=0
        def respond(req):
            nonlocal index
            body=json.loads(req.content);path=req.url.path.rsplit('/',1)[-1];requests.append((path,body))
            if path=='create_session':return httpx.Response(200,json={'session_id':'session-fixture'})
            if path=='retrieve_future':return httpx.Response(200,json=pending[body['request_id']])
            result={'create_model':{'model_id':'model-fixture','type':'create_model'},'save_weights':{'path':'tinker://model-fixture/weights/smoke'},'load_weights':{'model_id':'session-fixture:train:1'},'save_weights_for_sampler':{'path':'tinker://model-fixture/sampler_weights/smoke'}}[path]
            index+=1;key=str(index);pending[key]=result
            return httpx.Response(200,json={'request_id':key})
        async def run():
            async with make_client(httpx.MockTransport(respond)) as client:
                t=TrainingTransport(client,self.journal,poll_interval=0)
                await t.create('Qwen/Qwen3-8B')
                path=await t.checkpoint('smoke');await t.restore(path)
                await t.checkpoint('smoke',sampler=True)
        asyncio.run(run())
        changes=[(p,b) for p,b in requests if p in ('save_weights','load_weights','save_weights_for_sampler')]
        self.assertEqual(changes[0][1]['seq_id'],1)
        self.assertNotIn('seq_id',changes[1][1])
        self.assertEqual(changes[1][1]['model_seq_id'],1)
        self.assertEqual(changes[1][1]['session_id'],'session-fixture')
        self.assertEqual(changes[2][1]['seq_id'],1)
        self.assertEqual(changes[2][1]['model_id'],'session-fixture:train:1')
        self.assertEqual(changes[0][1]['ttl_seconds'],3600)
        self.assertFalse(changes[0][1]['overwrite'])
        self.assertTrue(changes[1][1]['optimizer'])
        self.assertEqual(changes[2][1]['ttl_seconds'],3600)
        self.assertNotIn('oc-sent',self.journal.read_text())
        with self.assertRaises(FileExistsError):TrainingTransport(None,self.journal)

    @patch.dict(os.environ,{'TINKER_API_KEY':'oc-sent-v2.fixture.end','HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_ambiguous_submission_halts_without_retry(self):
        import httpx
        from liftlap.tinker_sdk import make_client
        from liftlap.training_transport import TrainingTransport
        calls=[]
        def respond(req):
            calls.append(req.url.path)
            if req.url.path.endswith('create_session'):return httpx.Response(200,json={'session_id':'fixture'})
            raise httpx.ReadTimeout('private exception text',request=req)
        async def run():
            async with make_client(httpx.MockTransport(respond)) as client:
                t=TrainingTransport(client,self.journal,poll_interval=0)
                with self.assertRaises(Exception):await t.create('Qwen/Qwen3-8B')
                with self.assertRaises(RuntimeError):await t.create('Qwen/Qwen3-8B')
        asyncio.run(run());self.assertEqual(len(calls),2)
        self.assertNotIn('private exception',self.journal.read_text())

    @patch.dict(os.environ,{'TINKER_API_KEY':'oc-sent-v2.fixture.end','HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_training_wire_and_bounded_future_timeout(self):
        import httpx
        from tinker import types
        from tinker.proto import tinker_public_pb2 as pb
        from liftlap.tinker_sdk import make_client
        from liftlap.training_transport import TrainingTransport
        calls=[];retrievals=0
        def respond(req):
            nonlocal retrievals
            path=req.url.path.rsplit('/',1)[-1];calls.append(path)
            if path=='forward_backward':
                content=req.content
                if req.headers.get('Content-Encoding')=='zstd':
                    import zstandard;content=zstandard.ZstdDecompressor().decompress(content)
                request=pb.ForwardBackwardRequest.FromString(content)
                self.assertEqual(request.model_id,'fixture-model');self.assertEqual(request.seq_id,1)
                return httpx.Response(200,json={'request_id':'forward'})
            if path=='optim_step':
                body=json.loads(req.content);self.assertEqual(body['seq_id'],2)
                self.assertEqual(body['adam_params']['learning_rate'],.0001)
                return httpx.Response(200,json={'request_id':'optimizer'})
            body=json.loads(req.content)
            if body['request_id']=='forward':
                output=pb.ForwardBackwardOutput()
                return httpx.Response(200,content=output.SerializeToString(),headers={'content-type':'application/x-protobuf'})
            retrievals+=1;return httpx.Response(200,json={'type':'try_again'})
        async def run():
            async with make_client(httpx.MockTransport(respond)) as client:
                t=TrainingTransport(client,self.journal,polls=2,poll_interval=0);t.model='fixture-model'
                datum=types.Datum(model_input=types.ModelInput.from_ints([1]),loss_fn_inputs={
                    'target_tokens':types.TensorData(data=[2],dtype='int64',shape=[1]),
                    'weights':types.TensorData(data=[1.],dtype='float32',shape=[1])})
                with self.assertRaises(TimeoutError):await t.train_step([datum])
                with self.assertRaises(RuntimeError):await t.train_step([datum])
        asyncio.run(run())
        self.assertEqual(calls.count('forward_backward'),1)
        self.assertEqual(calls.count('optim_step'),1);self.assertEqual(retrievals,2)

    @patch.dict(os.environ,{'TINKER_API_KEY':'oc-sent-v2.fixture.end','HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_read_timeout_retries_only_future_retrieval(self):
        import httpx
        from liftlap.tinker_sdk import make_client
        from liftlap.training_transport import TrainingTransport
        calls=[];reads=0
        def respond(req):
            nonlocal reads
            path=req.url.path.rsplit('/',1)[-1];calls.append(path)
            if path=='create_session':return httpx.Response(200,json={'session_id':'fixture'})
            if path=='create_model':return httpx.Response(200,json={'request_id':'known'})
            reads+=1
            if reads==1:raise httpx.ReadTimeout('temporary',request=req)
            return httpx.Response(200,json={'model_id':'fixture-model','type':'create_model'})
        async def run():
            async with make_client(httpx.MockTransport(respond)) as c:
                t=TrainingTransport(c,self.journal,polls=2,poll_interval=0)
                self.assertEqual(await t.create('Qwen/Qwen3-8B'),'fixture-model')
        asyncio.run(run())
        self.assertEqual(calls.count('create_model'),1);self.assertEqual(reads,2)
