import asyncio,json,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
from liftlap.app_model import LiveModel,ModelUnavailable,replay
from liftlap.server import context,handle_api
from liftlap.core import digest

class AppModelTests(unittest.TestCase):
 def test_live_disabled_and_rules_explicit(self):
  with self.assertRaises(ValueError):handle_api('/api/interpret',{'adapter':'live'})
  self.assertEqual(handle_api('/api/interpret',{})['adapter'],'rules-v2')
 def test_replay_requires_exact_context(self):
  _,ui,cat=context('synthetic');text='Only blues';intent=handle_api('/api/interpret',{'text':text})['intent']
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'demo';p.mkdir();(p/'model-replay.json').write_text(json.dumps({'request_sha256':digest({'request_text':text,'ui_context':ui,'catalog':cat}),'intent':intent}))
   self.assertEqual(replay(d,text,ui,cat)['intent'],intent)
   with self.assertRaises(ModelUnavailable):replay(d,text,{**ui,'duration_minutes':90},cat)
 def test_busy_cap_and_ambiguous_failure(self):
  m=LiveModel.__new__(LiveModel);m.lock=threading.Lock();m.halted=False;m.attempts=10
  with self.assertRaises(ModelUnavailable):m.interpret('',{},[])
  m.attempts=0;m.lock.acquire()
  with self.assertRaises(ModelUnavailable):m.interpret('',{},[])
  m.lock.release();m.halted=True
  with self.assertRaises(ModelUnavailable):m.interpret('',{},[])
 def test_valid_model_is_not_planned_automatically(self):
  _,ui,cat=context('synthetic');i=handle_api('/api/interpret',{'text':'only blues'})['intent']
  class Fake:
   def interpret(self,*args):return {'intent':i,'adapter':'test'}
  r=handle_api('/api/interpret',{'adapter':'live'},Fake())
  self.assertEqual(r['intent'],i);self.assertNotIn('route',r)

 def test_semantic_failure_remains_editable_without_retry(self):
  from unittest.mock import AsyncMock, Mock
  _,ui,cat=context('synthetic')
  intent=handle_api('/api/interpret',{'text':'only blues'})['intent']
  intent.update(status='clarify',clarification_fields=['duration_minutes'])
  with tempfile.TemporaryDirectory() as directory:
   model=LiveModel.__new__(LiveModel)
   model.lock=threading.Lock();model.halted=False;model.attempts=0;model.directory=Path(directory)
   model.prompt='fixture';model.renderer=Mock()
   model.renderer.build_generation_prompt.return_value.to_ints.return_value=[1,2]
   model._run=AsyncMock(return_value={'status':'invalid_semantic','intent':None,'raw_output':json.dumps(intent)})
   result=handle_api('/api/interpret',{'adapter':'live'},model)
   self.assertEqual(result['intent'],intent)
   self.assertFalse(result['semantic_validation']['plan_allowed'])
   self.assertFalse(result['semantic_validation']['valid'])
   self.assertEqual(model.attempts,1);model._run.assert_awaited_once()
