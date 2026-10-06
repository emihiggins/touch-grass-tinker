"""Opt-in local model adapter. Reuses the pinned SDK/renderer and shared ledger.

A ten-request demo allowance is reserved once, before serving. Every attempt is
persisted before submission; failures consume their slot and are never retried.
"""
import asyncio,contextlib,json,threading,uuid
from pathlib import Path
from .corpus import conversation
from .core import digest
from .sample_runner import SDKSampler,run_cases,estimate
from .render_audit import load_renderer
from .spend import Ledger

class ModelUnavailable(ValueError):pass

class LiveModel:
    def __init__(self,root):
        self.root=Path(root);self.lock=threading.Lock()
        self.tokenizer,self.renderer=load_renderer(str(self.root/'.tokenizer-qwen3'),str(self.root/'training/tokenizer-manifest.json'))
        self.prompt=(self.root/'benchmark/v2/baseline-prompt.txt').read_text()
        auth=json.loads((self.root/'training/budget-authorization.json').read_text())
        if auth.get('account_credits_verified') is not True:raise ValueError('Credit evidence required')
        self.ledger=Ledger(self.root/'runs/project-spend.sqlite',auth)
        # One authorized demonstration session, no restart that silently resets allowance.
        self.ledger.reserve('app-demo-01','experiments',.10,'Up to ten single requests at <=$0.01 each; no training or storage')
        self.directory=self.root/'runs/app-demo-01';self.directory.mkdir()
        self.attempts=0;self.halted=False
    def interpret(self,text,ui,catalog):
        if not self.lock.acquire(blocking=False):raise ModelUnavailable('Model busy. Wait for the current request; no second call was submitted.')
        try:
            if self.halted:raise ModelUnavailable('Model session paused after a provider failure. Use Rules; no automatic retry.')
            if self.attempts>=10:raise ModelUnavailable('Demo allowance reached. Use Rules; no more model calls will be made.')
            case={'id':str(uuid.uuid4()),'request_text':text,'ui_context':ui,'catalog':catalog}
            tokens=self.renderer.build_generation_prompt(conversation(case,self.prompt,target=False)['messages']).to_ints()
            if len(tokens)+512>4096 or estimate([tokens],512,.195,.6)>.01:raise ModelUnavailable('Request exceeds demo context limit; shorten it.')
            self.attempts+=1;d=self.directory/str(self.attempts);d.mkdir()
            (d/'request.json').write_text(json.dumps(case,indent=2)+'\n')
            try:row=asyncio.run(self._run(case,tokens,d))
            except Exception:
                self.halted=True
                raise ModelUnavailable('Model request failed; no automatic retry. Use Rules.') from None
            if row['status'] in ('transport_or_provider_failure','not_attempted_after_transport_failure'):
                self.halted=True
                raise ModelUnavailable('Provider result is uncertain; session paused without retry. Use Rules.')
            if row['status']!='valid':raise ModelUnavailable('Model response failed validation. No route created. Edit your request or use Rules.')
            return {'intent':row['intent'],'adapter':'qwen3-8b-base-live','notice':'Live Qwen3-8B base model via Tinker. Review every constraint; the model can make mistakes.','unparsed':''}
        finally:self.lock.release()
    async def _run(self,case,tokens,d):
        from .tinker_sdk import make_client
        async with make_client() as client:
            raw=client.futures.with_raw_response;original=raw.retrieve
            async def retrieve(**kwargs):
                kwargs['timeout']=45
                return await original(**kwargs)
            raw.retrieve=retrieve
            sampler=SDKSampler(client,'Qwen/Qwen3-8B',None,self.renderer.get_stop_sequences(),512)
            async def heartbeat():
                while True:
                    if sampler.session_id:await client.service.session_heartbeat(session_id=sampler.session_id,max_retries=0,timeout=10)
                    await asyncio.sleep(10)
            task=asyncio.create_task(heartbeat())
            try:return (await run_cases([case],[tokens],self.tokenizer,self.renderer.get_stop_sequences(),sampler,d,'app-demo-'+case['id']))[0]
            finally:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError,Exception):await task

def replay(root,text,ui,catalog):
    p=Path(root)/'demo/model-replay.json'
    if not p.exists():raise ModelUnavailable('Recorded model example is not available.')
    record=json.loads(p.read_text())
    key={'request_text':text,'ui_context':ui,'catalog':catalog}
    if digest(key)!=record['request_sha256']:raise ModelUnavailable('Recorded example only matches the original text and settings. Load the example or choose Rules.')
    from scripts.benchmark import validate_intent
    validate_intent(record['intent'],{p['id'] for p in catalog})
    return {'intent':record['intent'],'adapter':'qwen3-8b-base-recorded','notice':'Recorded Qwen3-8B output from a verified live app call—not a new inference.','unparsed':''}
