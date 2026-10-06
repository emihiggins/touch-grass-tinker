"""Finish the original smoke only after its exact restore future is reconciled."""
import asyncio,contextlib,json,sqlite3
from pathlib import Path
from .render_audit import sha
from .training_smoke import prepare_smoke,save

def verify(directory):
    m=json.loads((directory/'manifest.json').read_text())
    if m['status']!='halted_requires_reconciliation' or (directory/'reconciled-finish-events.jsonl').exists():raise ValueError('Completion already attempted or smoke not halted')
    for path,expected in m['hashes'].items():
        # Code fixes are reviewed separately; the exact training data/config remain fixed.
        if not path.endswith('.py') and sha(path)!=expected:raise ValueError('Training inputs changed')
    known=json.loads((directory/'reconciled-restore.json').read_text())
    rows=[json.loads(x) for x in (directory/'fresh-restore-events.jsonl').read_text().splitlines()]
    submitted=[r for r in rows if r['event']=='submitted' and r.get('operation')=='restore_new_model']
    initial=[json.loads(x) for x in (directory/'training-events.jsonl').read_text().splitlines()]
    session=next(r['session_id'] for r in initial if r['event']=='session_created')
    if known['status']!='completed' or len(submitted)!=1 or submitted[0]['request_id']!=known['request_id'] or known['response']['model_id']!=f'{session}:train:1':raise ValueError('Restore identity mismatch')
    for file in directory.glob('*events.jsonl'):
        if any(r.get('operation')=='save_sampler' or r.get('event')=='sample_submitted' for r in map(json.loads,file.read_text().splitlines())):raise ValueError('Sampler mutation may already exist')
    with sqlite3.connect('runs/project-spend.sqlite') as db:
        if db.execute('SELECT amount,state FROM commitments WHERE id=?',(directory.name,)).fetchone()!=(250000000,'reserved'):raise ValueError('Reservation missing')
    return m,session,known['response']['model_id']

async def execute(directory,m,session,model):
    from .tinker_sdk import make_client
    from .training_transport import TrainingTransport
    from .sample_runner import SDKSampler,parse_output,decode_sample
    config,cases,tokenizer,renderer,_,tokens,_=prepare_smoke()
    sampler=None
    async with make_client() as c:
        raw=c.futures.with_raw_response;original=raw.retrieve
        async def retrieve(**kwargs):
            kwargs['timeout']=45;return await original(**kwargs)
        raw.retrieve=retrieve
        async def heartbeats():
            while True:
                await c.service.session_heartbeat(session_id=session,max_retries=0,timeout=10)
                if sampler is not None and sampler.session_id:
                    await c.service.session_heartbeat(session_id=sampler.session_id,max_retries=0,timeout=10)
                await asyncio.sleep(10)
        keeper=asyncio.create_task(heartbeats())
        try:
            t=TrainingTransport(c,directory/'reconciled-finish-events.jsonl',polls=10)
            t.model=model;t.session=session;t.sequence=0
            t.record('restore_reconciled')
            path=await t.checkpoint('integration-sampler',sampler=True)
            state=json.loads((directory/'state-inspection.json').read_text())['path']
            m.update(state_checkpoint=state,sampler_checkpoint=path,optimizer_restore_response_received=True)
            save(directory/'manifest.json',m)
            sampler=SDKSampler(c,config['model_name'],path,renderer.get_stop_sequences(),512,polls=10)
            result=await sampler.sample(tokens,directory.name+'-sample',lambda rid:t.record('sample_submitted',request_id=rid))
            text=decode_sample(tokenizer,result['tokens'],renderer.get_stop_sequences());intent,status=parse_output(text,result['stop_reason'],cases[0]['catalog'])
            save(directory/'sample.json',{'text':text,'intent':intent,'status':status,'stop_reason':result['stop_reason'],'output_tokens':len(result['tokens'])})
            return {'status':'completed' if status=='valid' else 'completed_sample_invalid','sample_status':status,'scope':'integration_smoke_not_independent_quality_or_exact_restore_equivalence'}
        finally:
            keeper.cancel()
            with contextlib.suppress(asyncio.CancelledError,Exception):await keeper

def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run_dir');a=p.parse_args();d=Path(a.run_dir)
    m,session,model=verify(d)
    try:m.update(asyncio.run(asyncio.wait_for(execute(d,m,session,model),timeout=600)))
    except BaseException as e:m.update(status='halted_requires_reconciliation',completion_error_type=type(e).__name__)
    save(d/'manifest.json',m);print(json.dumps({'status':m['status'],'sample_status':m.get('sample_status')}))
    if m['status']!='completed':raise SystemExit(1)
if __name__=='__main__':main()
