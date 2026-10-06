"""Read-only reconciliation of the existing smoke restore and billing window."""
import asyncio,json,contextlib
from pathlib import Path
from .tinker_sdk import make_client
from .billing_check import summarize

async def reconcile(directory):
    from tinker import types
    rows=[json.loads(line) for line in (directory/'fresh-restore-events.jsonl').read_text().splitlines()]
    futures=[r['request_id'] for r in rows if r.get('operation')=='restore_new_model' and r['event']=='submitted']
    if len(futures)!=1:raise ValueError('Expected exactly one existing restore future')
    report={'scope':'read_only_existing_future_and_provisional_billing','compute_mutations':0}
    initial=[json.loads(line) for line in (directory/'training-events.jsonl').read_text().splitlines()]
    session=next(r['session_id'] for r in initial if r['event']=='session_created')
    async with make_client() as client:
        async def future():
            try:
                response=await client.futures.with_raw_response.retrieve(request=types.FutureRetrieveRequest(request_id=futures[0]),timeout=45,max_retries=0)
                data=await response.json()
                state=data.get('type')
                if state in ('try_again','request_failed','error'):
                    return {'status':state,'response_fields':sorted(data)}
                parsed=types.LoadWeightsResponse.model_validate(data)
                if not parsed.model_id:return {'status':'unexpected_response','response_fields':sorted(data)}
                (directory/'reconciled-restore.json').write_text(json.dumps({'request_id':futures[0],'response':parsed.model_dump(mode='json'),'status':'completed'},indent=2)+'\n')
                return {'status':'completed','model_identity_recorded_privately':True}
            except Exception as error:return {'status':'read_failed','error_type':type(error).__name__,'http_status':getattr(error,'status_code',None)}
        async def billing():
            try:
                r=await client.get('/api/v1/billing/usage/events',options={'params':{'starting_on':'2026-10-05T00:00:00Z','ending_before':'2026-10-07T00:00:00Z'}},cast_to=types.BillingUsageResponse)
                return summarize(r.model_dump(mode='json',warnings=False))
            except Exception as error:return {'status':'read_failed','error_type':type(error).__name__}
        async def heartbeat():
            while True:
                await client.service.session_heartbeat(session_id=session,max_retries=0,timeout=10)
                await asyncio.sleep(10)
        maintenance=asyncio.create_task(heartbeat())
        try:
            report['restore'],report['billing']=await asyncio.gather(future(),billing())
        finally:
            maintenance.cancel()
            with contextlib.suppress(asyncio.CancelledError,Exception):await maintenance
        report['existing_session_heartbeat_maintenance']=True
    (directory/'reconciliation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run_dir');a=p.parse_args()
    print(json.dumps(asyncio.run(reconcile(Path(a.run_dir))),indent=2))
