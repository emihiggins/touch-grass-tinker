import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from liftlap.experiment02 import batch_indices, execute


class BatchTests(unittest.TestCase):
    def test_every_row_once_per_epoch_with_partial_tail(self):
        batches = batch_indices(47,16,3)
        self.assertEqual([len(b) for b in batches], [16,16,15]*3)
        for start in (0,3,6):
            self.assertEqual(sorted(i for b in batches[start:start+3] for i in b), list(range(47)))
        self.assertEqual(batches, batch_indices(47,16,3))
        self.assertNotEqual(batches[:3], batches[3:6])

    def test_invalid_and_small_batches(self):
        for values in ((0,16,3),(47,0,3),(47,16,0),(True,16,3)):
            with self.assertRaises(ValueError): batch_indices(*values)
        self.assertEqual(len(batch_indices(2,16,1)[0]), 2)

    def test_executor_sends_tail_and_stops_on_training_failure(self):
        for failing in (False,True):
            with self.subTest(failing=failing), tempfile.TemporaryDirectory() as tmp:
                steps=[];checkpoints=[]
                class Client:
                    futures=SimpleNamespace(with_raw_response=SimpleNamespace(retrieve=AsyncMock()))
                    async def __aenter__(self): return self
                    async def __aexit__(self,*args): pass
                class Trainer:
                    session=None
                    def __init__(self,*args,**kwargs): pass
                    async def create(self,*args): pass
                    async def train_step(self,datums,lr):
                        steps.append((datums,lr))
                        if failing: raise RuntimeError('fixture transport stop')
                        return SimpleNamespace(metrics={})
                    async def checkpoint(self,name,**kwargs):
                        checkpoints.append(name);return 'fixture-checkpoint'
                class Sampler:
                    session_id=None
                    def __init__(self,*args,**kwargs): pass
                config=json.loads(Path('training/experiment-02.json').read_text())
                renderer=SimpleNamespace(get_stop_sequences=lambda:[])
                prepared=(config,[],[],{}, {},None,renderer,list(range(47)),[],{})
                report={'count':1,'successes':1,'cases':[{'id':'fixture','success':True,'gold_route_valid':True}]}
                sampling=AsyncMock(return_value=[{'status':'valid'}])
                with patch('liftlap.tinker_sdk.make_client',return_value=Client()), patch('liftlap.training_transport.TrainingTransport',Trainer), patch('liftlap.sample_runner.SDKSampler',Sampler), patch('liftlap.sample_runner.run_cases',sampling), patch('liftlap.experiment02.evaluate',return_value=report):
                    if failing:
                        with self.assertRaises(RuntimeError): asyncio.run(execute(Path(tmp),prepared))
                        self.assertEqual(len(steps),1);self.assertEqual(checkpoints,[])
                        self.assertEqual(sampling.await_count,1)
                    else:
                        result=asyncio.run(execute(Path(tmp),prepared))
                        self.assertEqual([len(d) for d,_ in steps],[16,16,15]*3)
                        self.assertTrue(all(lr==.00003 for _,lr in steps))
                        self.assertEqual(len(checkpoints),2)
                        self.assertEqual(sampling.await_count,2)
                        self.assertEqual(result['comparison']['promotion_decision'],'retain_base')


@unittest.skipUnless(importlib.util.find_spec('tinker_cookbook'),'optional pinned renderer required')
class PreparationTests(unittest.TestCase):
    def test_rehearsal_is_complete_and_budgeted(self):
        from liftlap.experiment02 import prepare_experiment
        prepared=prepare_experiment();plan=prepared[-1]
        self.assertEqual(plan['optimizer_steps'],9)
        self.assertEqual(plan['train_count'],47)
        self.assertEqual(plan['max_sampling_requests'],32)
        self.assertLess(plan['cost_upper_estimate_usd'],1.25)
        self.assertEqual([len(b) for b in plan['batches']],[16,16,15]*3)
