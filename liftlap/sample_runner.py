"""Pinned SDK sampling runner. Dry-run by default; live requires explicit budget flags.

No training. No retry of submissions or semantic failures. Existing runs cannot resume
or overwrite: ambiguous submissions must be reconciled by request ID first.
"""
import argparse
import asyncio
import hashlib
import json
import math
from pathlib import Path
import time
import uuid
from .corpus import read,conversation,audit
from .render_audit import load_renderer,sha
from scripts.benchmark import validate_intent

def parse_output(text,stop_reason,catalog):
    if stop_reason!='stop':return None,'truncated_or_unknown_stop'
    try:
        def unique(pairs):
            obj={}
            for k,v in pairs:
                if k in obj:raise ValueError('duplicate key')
                obj[k]=v
            return obj
        intent=json.loads(text,object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        validate_intent(intent,{p['id'] for p in catalog})
        return intent,'valid'
    except (ValueError,TypeError,KeyError):return None,'invalid_json_or_schema'

def estimate(prompts,max_output,input_rate,output_rate):
    if any(not math.isfinite(x) or x<0 for x in (input_rate,output_rate)):raise ValueError('Invalid rates')
    return (sum(len(p) for p in prompts)*input_rate+len(prompts)*max_output*output_rate)/1_000_000

def append(path,row):
    with Path(path).open('a') as f:
        f.write(json.dumps(row,sort_keys=True)+'\n');f.flush()

class SDKSampler:
    def __init__(self,client,model,model_path,stop,max_output,polls=12,poll_interval=1):
        self.client=client;self.model=model;self.model_path=model_path;self.stop=stop
        self.max_output=max_output;self.polls=polls;self.poll_interval=poll_interval
        self.session_id=None;self.sampling_session_id=None;self.seq_id=0
    async def sample(self,tokens,request_key,on_submitted):
        import tinker
        from tinker.types.sample_request import SampleRequest
        from tinker.types.future_retrieve_request import FutureRetrieveRequest
        from tinker.proto.response_conv import deserialize_proto_response
        if self.sampling_session_id is None:
            from tinker.types.create_session_request import CreateSessionRequest
            from tinker.types.create_sampling_session_request import CreateSamplingSessionRequest
            session=await self.client.service.create_session(request=CreateSessionRequest(tags=['liftlap-baseline-smoke'],user_metadata=None,sdk_version=tinker.__version__))
            self.session_id=session.session_id
            sampling=await self.client.service.create_sampling_session(request=CreateSamplingSessionRequest(session_id=self.session_id,sampling_session_seq_id=0,base_model=self.model,model_path=self.model_path))
            self.sampling_session_id=sampling.sampling_session_id
        await self.client.service.session_heartbeat(session_id=self.session_id,max_retries=0)
        sequence_id=self.seq_id;self.seq_id+=1
        request=SampleRequest(prompt=tinker.ModelInput.from_ints(tokens),num_samples=1,
            sampling_session_id=self.sampling_session_id,seq_id=sequence_id,
            sampling_params=tinker.SamplingParams(max_tokens=self.max_output,temperature=0,seed=20261006,stop=self.stop))
        future=await self.client.sampling.asample(request=request,extra_headers={'X-Idempotency-Key':request_key,'X-Tinker-Sampling-Backpressure':'1'},max_retries=0)
        on_submitted(future.request_id)
        for iteration in range(self.polls):
            response=await self.client.futures.with_raw_response.retrieve(
                request=FutureRetrieveRequest(request_id=future.request_id),timeout=5,max_retries=0,
                extra_headers={'Accept':'application/x-protobuf'})
            if 'application/x-protobuf' in response.http_response.headers.get('content-type',''):
                result=deserialize_proto_response(response.http_response.content,tinker.SampleResponse)
                if len(result.sequences)!=1:raise ValueError('Unexpected sample count')
                seq=result.sequences[0]
                return {'tokens':seq.tokens,'stop_reason':seq.stop_reason,'request_id':future.request_id,
                        'prompt_cache_hit_tokens':result.prompt_cache_hit_tokens,'polls':iteration+1}
            body=await response.json()
            if body.get('type')!='try_again':raise ValueError('Unexpected future response')
            if iteration+1<self.polls:await asyncio.sleep(self.poll_interval)
        raise TimeoutError('Future polling bound reached')

async def run_cases(cases,prompts,tokenizer,stop,sampler,directory,run_id):
    rows=[];halt=False
    for index,(case,prompt) in enumerate(zip(cases,prompts,strict=True)):
        row={'id':case['id'],'intent':None,'input_tokens':len(prompt),'billable_usage_verified':False}
        if halt:
            row['status']='not_attempted_after_transport_failure'
        else:
            request_key=f'{run_id}-{index}'
            append(directory/'events.jsonl',{'id':case['id'],'event':'submission_start','request_key':request_key})
            started=time.monotonic()
            try:
                def submitted(request_id):append(directory/'events.jsonl',{'id':case['id'],'event':'submitted','request_id':request_id})
                result=await asyncio.wait_for(sampler.sample(prompt,request_key,submitted),timeout=90)
                ids=result['tokens'];payload=ids[:-1] if ids and ids[-1] in stop else ids
                text=tokenizer.decode(payload)
                intent,status=parse_output(text,result['stop_reason'],case['catalog'])
                row.update(intent=intent,status=status,raw_output=text,output_tokens=len(ids),
                           stop_reason=result['stop_reason'],request_id=result['request_id'],
                           prompt_cache_hit_tokens=result.get('prompt_cache_hit_tokens'),polls=result.get('polls'))
            except Exception as error:
                code=getattr(error,'status_code',None)
                row.update(status='transport_or_provider_failure',http_status=code if type(code) is int else None)
                response=getattr(error,'response',None)
                if response is not None:row['failed_endpoint']=response.request.url.path
                if isinstance(sampler,SDKSampler):row['sampling_session_id']=sampler.sampling_session_id
                halt=True
            row['elapsed_seconds']=time.monotonic()-started
        append(directory/'predictions.jsonl',row);rows.append(row)
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prompt',default='benchmark/baseline-prompt.txt')
    p.add_argument('cases');p.add_argument('--run-dir',required=True);p.add_argument('--live',action='store_true')
    p.add_argument('--budget-usd',type=float);p.add_argument('--input-usd-per-million',type=float);p.add_argument('--output-usd-per-million',type=float)
    p.add_argument('--credits-confirmed',action='store_true');p.add_argument('--model-path')
    p.add_argument('--max-requests',type=int,default=100);p.add_argument('--scenarios',help='Optional development scenario map; predictions keyed by scenario IDs')
    a=p.parse_args();cases=read(a.cases)
    if audit(cases)['errors']:p.error('Corpus audit failed')
    if a.scenarios:
        specs=json.loads(Path(a.scenarios).read_text());lookup={c['id']:c for c in cases}
        cases=[{**lookup[s['seed_case_id']],'id':s['id']} for s in specs]
    if not cases or len(cases)>a.max_requests or len({c['id'] for c in cases})!=len(cases):p.error('Empty, duplicate or over-limit case set')
    config=json.loads(Path('training/sft-plan.json').read_text())
    prompt=Path(a.prompt).read_text()
    tokenizer,renderer=load_renderer('.tokenizer-qwen3','training/tokenizer-manifest.json')
    prompts=[renderer.build_generation_prompt(conversation(c,prompt,target=False)['messages']).to_ints() for c in cases]
    max_output=config['sampling']['max_tokens']
    if any(len(x)+max_output>config['max_length'] for x in prompts):p.error('Prompt plus output reservation exceeds context')
    projected=None
    if a.live:
        if not a.credits_confirmed or any(x is None for x in (a.budget_usd,a.input_usd_per_million,a.output_usd_per_million)):
            p.error('Live requires verified credits, budget and current token rates')
        if not math.isfinite(a.budget_usd) or a.budget_usd<=0:p.error('Invalid budget')
        projected=estimate(prompts,max_output,a.input_usd_per_million,a.output_usd_per_million)
        if projected>a.budget_usd:p.error('Token-based upper estimate exceeds approved budget')
    directory=Path(a.run_dir)
    if directory.exists():p.error('Run directory exists; refusing overwrite/resubmission')
    directory.mkdir(parents=True);run_id=str(uuid.uuid4())
    manifest={'run_id':run_id,'mode':'live' if a.live else 'dry_run','model':config['model_name'],'model_path':a.model_path,
              'renderer':config['renderer_name'],'count':len(cases),'max_output_tokens':max_output,'temperature':0,
              'sampling_seed':20261006,'input_tokens':sum(map(len,prompts)),'upper_estimate_usd':projected,
              'budget_usd':a.budget_usd,'input_usd_per_million':a.input_usd_per_million,'output_usd_per_million':a.output_usd_per_million,
              'budget_caveat':'Estimate from supplied rates, not a provider-enforced spending cap or invoice.',
              'runner_sha256':sha(__file__),'prompt_file':a.prompt,
              'hashes':{f:sha(f) for f in [a.cases,'training/sft-plan.json',a.prompt,'training/tokenizer-manifest.json','training/render-requirements.lock']},
              'status':'prepared','model_calls':0}
    if a.scenarios:manifest['hashes'][a.scenarios]=sha(a.scenarios)
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if not a.live:
        print(json.dumps({'status':'dry_run_ready','count':len(cases),'model_calls':0,'manifest':str(directory/'manifest.json')}));return
    async def execute():
        from .tinker_sdk import make_client
        async with make_client() as client:
            sampler=SDKSampler(client,config['model_name'],a.model_path,renderer.get_stop_sequences(),max_output)
            return await run_cases(cases,prompts,tokenizer,renderer.get_stop_sequences(),sampler,directory,run_id)
    manifest.update(status='running',model_calls=None)
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    rows=asyncio.run(execute())
    manifest.update(status='completed_with_failures' if any(r['status']!='valid' for r in rows) else 'completed',
                    submission_attempts=sum(r['status']!='not_attempted_after_transport_failure' for r in rows),model_calls=None)
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':manifest['status'],'count':len(rows),'valid_outputs':sum(r['status']=='valid' for r in rows)}))

if __name__=='__main__':main()
