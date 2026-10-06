"""One fixed base-model evaluation; no training, tuning, or mutation retries."""
import argparse,asyncio,contextlib,json
from pathlib import Path
from .corpus import read,conversation
from .core import digest
from .evaluation_v2 import evaluate
from .render_audit import load_renderer,sha
from .sample_runner import SDKSampler,run_cases,estimate
from .training_smoke import save
from .spend import Ledger

ROOT=Path('benchmark/v2/final-review')
KEY='fresh-base-evaluation-01'

def prepare():
    cases=read(ROOT/'cases.jsonl');graphs=json.loads((ROOT/'graphs.json').read_text());freeze=json.loads((ROOT/'freeze.json').read_text())
    evaluate(cases,graphs,[],freeze=freeze)
    if len(cases)!=16:raise ValueError('Fixed sixteen-case evaluation required')
    tokenizer,renderer=load_renderer('.tokenizer-qwen3','training/tokenizer-manifest.json')
    prompt=Path('benchmark/v2/baseline-prompt.txt').read_text()
    prompts=[renderer.build_generation_prompt(conversation(c,prompt,target=False)['messages']).to_ints() for c in cases]
    if any(len(p)+512>4096 for p in prompts):raise ValueError('Context overflow')
    bound=estimate(prompts,512,.195,.6)
    if bound>.05:raise ValueError('Reservation insufficient')
    files=[str(ROOT/p) for p in ['cases.jsonl','graphs.json','freeze.json']]+['benchmark/v2/baseline-prompt.txt','training/tokenizer-manifest.json','training/budget-authorization.json','liftlap/final_evaluation.py','liftlap/sample_runner.py','liftlap/evaluation_v2.py']
    manifest={'run_key':KEY,'model':'Qwen/Qwen3-8B','model_path':None,'count':16,'temperature':0,'seed':20261006,'max_output_tokens':512,'max_context_tokens':4096,'reservation_usd':.05,'upper_estimate_usd':bound,'hashes':{p:sha(p) for p in files},'status':'prepared','policy':'No tuning or reruns based on final outputs; retain every failure in denominator'}
    manifest['plan_sha256']=digest(manifest)
    return cases,graphs,freeze,tokenizer,renderer,prompts,manifest

async def execute(d,prepared):
    from .tinker_sdk import make_client
    cases,graphs,freeze,tokenizer,renderer,prompts,manifest=prepared
    async with make_client() as client:
        raw=client.futures.with_raw_response;original=raw.retrieve
        async def retrieve(**kwargs):
            kwargs['timeout']=45
            return await original(**kwargs)
        raw.retrieve=retrieve
        sampler=SDKSampler(client,manifest['model'],None,renderer.get_stop_sequences(),512,polls=12)
        async def heartbeat():
            while True:
                if sampler.session_id:await client.service.session_heartbeat(session_id=sampler.session_id,max_retries=0,timeout=10)
                await asyncio.sleep(10)
        keeper=asyncio.create_task(heartbeat())
        try:
            rows=await run_cases(cases,prompts,tokenizer,renderer.get_stop_sequences(),sampler,d,KEY)
            report=evaluate(cases,graphs,rows,freeze=freeze);save(d/'report.json',report)
            failed=any(r['status'] in ('transport_or_provider_failure','not_attempted_after_transport_failure') for r in rows)
            return {'status':'halted_requires_reconciliation' if failed else 'completed','successes':report['successes'],'valid_schemas':sum(r['status']=='valid' for r in rows)}
        finally:
            keeper.cancel()
            with contextlib.suppress(asyncio.CancelledError,Exception):await keeper

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true');p.add_argument('--run-dir',required=True);p.add_argument('--plan-sha256');a=p.parse_args()
    prepared=prepare();m=prepared[-1];d=Path(a.run_dir)
    if d.exists():p.error('Existing run; refuse overwrite or resubmission')
    if a.live:
        if a.plan_sha256!=m['plan_sha256']:p.error('Dry-plan hash mismatch')
        auth=json.loads(Path('training/budget-authorization.json').read_text())
        if auth.get('account_credits_verified') is not True:p.error('Missing credit evidence')
        Ledger('runs/project-spend.sqlite',auth).reserve(KEY,'experiments',.05,'Frozen fresh evaluation '+m['plan_sha256'])
    d.mkdir(parents=True);save(d/'manifest.json',m)
    if not a.live:print(json.dumps(m));return
    m['status']='running';save(d/'manifest.json',m)
    try:m.update(asyncio.run(asyncio.wait_for(execute(d,prepared),timeout=900)))
    except BaseException as e:m.update(status='halted_requires_reconciliation',error_type=type(e).__name__)
    m['billing_status']='Reservation held pending verified billing';save(d/'manifest.json',m)
    print(json.dumps({k:m[k] for k in ['status','successes','valid_schemas'] if k in m}))
    if m['status']!='completed':raise SystemExit(1)
if __name__=='__main__':main()
