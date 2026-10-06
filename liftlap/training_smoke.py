"""Two-example protected training smoke. Dry run default; no experiment loop."""
import argparse,asyncio,json,hashlib,os
from pathlib import Path
from .corpus import read,label_approved,conversation
from .render_audit import load_renderer,prepare,sha
from .spend import Ledger

FILES=['benchmark/v2/training-reviewed.jsonl','benchmark/v2/baseline-prompt.txt','training/sft-plan-v2.json','training/tokenizer-manifest.json','training/render-requirements.lock','liftlap/training_smoke.py','liftlap/training_transport.py','liftlap/sample_runner.py','liftlap/tinker_sdk.py','liftlap/spend.py','training/budget-authorization.json']

def save(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');os.replace(tmp,path)

def prepare_smoke():
    config=json.loads(Path(FILES[2]).read_text())
    if config['model_name']!='Qwen/Qwen3-8B' or config['lora_rank']!=16 or config['max_length']!=2048 or config['learning_rate']!=0.0001:raise ValueError('Unpriced model/config')
    cases=read(FILES[0])
    if len(cases)!=47 or any(not label_approved(c) for c in cases):raise ValueError('Training corpus approval mismatch')
    selected=cases[:2];prompt=Path(FILES[1]).read_text()
    tokenizer,renderer=load_renderer('.tokenizer-qwen3',FILES[3])
    report,datums=prepare(selected,prompt,tokenizer,renderer,config)
    sample=renderer.build_generation_prompt(conversation(selected[0],prompt,target=False)['messages']).to_ints()
    # One step on both examples; 2 checkpoint objects expire after one hour.
    # 512 decimal GB per object > full 10B-parameter state at32bytes/parameter.
    # Actual LoRA state should be far smaller; this is a conservative accounting bound.
    cost=report['total_sequence_tokens']*.44/1e6+(len(sample)*.195+512*.6)/1e6+2*512*.1/720
    if cost>.25:raise ValueError('Smoke reservation insufficient')
    return config,selected,tokenizer,renderer,datums,sample,{'schema':1,'scope':'integration_smoke_not_quality_evaluation','ids':[c['id'] for c in selected],
        'hashes':{f:sha(f) for f in FILES},'training_tokens':report['total_sequence_tokens'],'upper_estimate_usd':cost,
        'reserved_usd':.25,'checkpoint_count':2,'checkpoint_ttl_seconds':3600,'checkpoint_upper_gb_each':512,
        'prior_usage_hold_usd':.1,'rates_checked_on':'2026-10-06','prices_url':'https://tinker-docs.thinkingmachines.ai/tinker/models/models_and_pricing/',
        'status':'prepared','live_calls':False}

async def execute(client,directory,config,datums,prompt_tokens,renderer,tokenizer,manifest):
    from .training_transport import TrainingTransport
    from .sample_runner import SDKSampler,parse_output,decode_sample
    transport=TrainingTransport(client,directory/'training-events.jsonl',polls=60)
    await transport.create(config['model_name'],config['lora_rank'])
    await transport.train_step(datums,config['learning_rate'])
    state=await transport.checkpoint('integration-state',ttl_seconds=3600)
    await transport.restore(state)
    sampler_path=await transport.checkpoint('integration-sampler',sampler=True,ttl_seconds=3600)
    # Save paths immediately: a later sample failure must not hide existing storage.
    manifest.update(state_checkpoint=state,sampler_checkpoint=sampler_path,optimizer_restore_response_received=True)
    save(directory/'manifest.json',manifest)
    sampler=SDKSampler(client,config['model_name'],sampler_path,renderer.get_stop_sequences(),512,polls=60)
    result=await sampler.sample(prompt_tokens,directory.name+'-sample',lambda rid:transport.record('sample_submitted',request_id=rid))
    text=decode_sample(tokenizer,result['tokens'],renderer.get_stop_sequences());case=read(FILES[0])[0]
    intent,status=parse_output(text,result['stop_reason'],case['catalog'])
    save(directory/'sample.json',{'text':text,'intent':intent,'status':status,'stop_reason':result['stop_reason'],'output_tokens':len(result['tokens'])})
    return {'status':'completed' if status=='valid' else 'completed_sample_invalid','sample_status':status,'state_checkpoint':state,'sampler_checkpoint':sampler_path,
            'scope':'remote_integration_only_not_independent_quality_or_restore_equivalence'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true');p.add_argument('--run-dir',required=True)
    p.add_argument('--ledger',default='runs/project-spend.sqlite');p.add_argument('--plan-sha256',help='Required live binding to reviewed dry-run plan')
    a=p.parse_args();config,cases,tokenizer,renderer,datums,prompt,manifest=prepare_smoke()
    plan_hash=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest();manifest['plan_sha256']=plan_hash
    directory=Path(a.run_dir)
    if directory.exists():p.error('Run directory exists; never overwrite or resubmit')
    if a.live:
        if a.plan_sha256!=plan_hash:p.error('Live requires matching dry-run plan hash')
        authorization=json.loads(Path(FILES[-1]).read_text())
        if authorization.get('account_credits_verified') is not True:p.error('Account credit evidence required')
        if authorization['total_project_cap_usd']!=10:p.error('Unexpected authorization cap')
        # Must already contain prior conservative hold or reconciled billing.
        ledger=Ledger(a.ledger,authorization)
        ledger.reserve(directory.name,'smoke',.25,'Hash-bound two-example smoke '+plan_hash+'; two1h checkpoints,512GB upper allowance each')
    directory.mkdir(parents=True);save(directory/'manifest.json',manifest)
    if not a.live:print(json.dumps({'status':'dry_run','plan_sha256':plan_hash,'upper_estimate_usd':manifest['upper_estimate_usd']}));return
    manifest.update(status='running',live_calls=True);save(directory/'manifest.json',manifest)
    async def run():
        from .tinker_sdk import make_client
        async with make_client() as client:
            async with asyncio.timeout(900):return await execute(client,directory,config,datums,prompt,renderer,tokenizer,manifest)
    try:manifest.update(asyncio.run(run()))
    except BaseException as error:
        manifest.update(status='halted_requires_reconciliation',error_type=type(error).__name__)
    manifest['budget_settlement']='Reservation retained until billing verified; never assume failure is free'
    save(directory/'manifest.json',manifest)
    print(json.dumps({k:manifest[k] for k in ['status','reserved_usd','plan_sha256']}))
    if manifest['status']!='completed':raise SystemExit(1)

if __name__=='__main__':main()
