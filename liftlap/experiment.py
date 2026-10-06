"""Hash-bound single-configuration exploratory comparison. Dry run by default."""
import argparse,asyncio,contextlib,hashlib,json
from pathlib import Path
from .corpus import read,audit,label_approved,conversation
from .render_audit import prepare,load_renderer,sha
from .training_smoke import save
from .core import digest
from .evaluation_v2 import evaluate
from .spend import Ledger

CONFIG='training/experiment-01.json'

def prepare_experiment():
    config=json.loads(Path(CONFIG).read_text())
    if (config['model_name'],config['epochs'],config['batch_size'],config['lora_rank'],config['learning_rate'])!=('Qwen/Qwen3-8B',3,47,16,.0001):raise ValueError('Unregistered configuration')
    train=read(config['training_cases']);test=read(config['evaluation_cases'])
    if len(train)!=47 or len(test)!=16 or not all(label_approved(c) for c in train+test):raise ValueError('Wrong corpus or review state')
    check=audit(train+test)
    if check['errors'] or check['warnings']:raise ValueError('Corpus overlap/audit failure')
    graphs=json.loads(Path(config['graph_bundle']).read_text());freeze=json.loads(Path(config['evaluation_freeze']).read_text())
    evaluate(test,graphs,[],freeze=freeze) # verify labels and exact frozen artifacts before model calls
    tokenizer,renderer=load_renderer('.tokenizer-qwen3','training/tokenizer-manifest.json');prompt=Path(config['prompt']).read_text()
    report,datums=prepare(train,prompt,tokenizer,renderer,config)
    prompts=[renderer.build_generation_prompt(conversation(c,prompt,target=False)['messages']).to_ints() for c in test]
    if any(len(x)+512>config['max_length'] for x in prompts):raise ValueError('Evaluation context overflow')
    train_cost=report['total_sequence_tokens']*config['epochs']*.44/1e6
    sampling_cost=2*(sum(map(len,prompts))*.195+len(test)*512*.6)/1e6
    storage_cost=2*512*.1*config['checkpoint_ttl_seconds']/3600/720
    total=train_cost+sampling_cost+storage_cost
    if total>config['reservation_usd']:raise ValueError('Reservation below conservative estimate')
    files=[CONFIG,'training/experiment-01.md',config['training_cases'],config['evaluation_cases'],config['evaluation_freeze'],config['graph_bundle'],config['prompt'],
           'training/tokenizer-manifest.json','training/budget-authorization.json','training/render-requirements.lock',
           'liftlap/experiment.py','liftlap/training_transport.py','liftlap/sample_runner.py','liftlap/tinker_sdk.py','liftlap/spend.py']
    plan={'experiment_id':config['experiment_id'],'scope':config['scope'],'hashes':{f:sha(f) for f in files},
          'train_count':len(train),'evaluation_count':len(test),'epochs':3,'batch_size':47,'optimizer_steps':3,'train_tokens':report['total_sequence_tokens']*3,
          'max_sampling_requests':32,'cost_upper_estimate_usd':total,'reservation_usd':config['reservation_usd'],'checkpoint_ttl_seconds':config['checkpoint_ttl_seconds'],'status':'prepared'}
    plan['plan_sha256']=digest(plan)
    return config,train,test,graphs,freeze,tokenizer,renderer,datums,prompts,plan


def compare(base,trained):
    pairs=list(zip(base['cases'],trained['cases'],strict=True))
    if any(b['id']!=t['id'] for b,t in pairs):raise ValueError('Paired case alignment mismatch')
    wins=[b['id'] for b,t in pairs if not b['success'] and t['success']]
    losses=[b['id'] for b,t in pairs if b['success'] and not t['success']]
    regressions=[b['id'] for b,t in pairs if b['gold_route_valid'] is True and t['gold_route_valid'] is False]
    return {'scope':'exploratory_reviewed_pilot_not_untouched_final_benchmark','count':base['count'],
            'base_successes':base['successes'],'trained_successes':trained['successes'],'paired_wins':wins,'paired_losses':losses,
            'gold_route_validity_regressions':regressions,'screening_pass':len(wins)-len(losses)>=2 and not regressions,
            'statistical_superiority_claim':False,'selection_rule':'At least2 additional successes and no gold-route validity regression'}

async def execute(d,prepared):
    from .tinker_sdk import make_client
    from .training_transport import TrainingTransport
    from .sample_runner import SDKSampler,run_cases
    config,train,test,graphs,freeze,tokenizer,renderer,datums,prompts,manifest=prepared
    samplers=[];trainer=None
    async with make_client() as client:
        raw=client.futures.with_raw_response;original=raw.retrieve
        async def retrieve(**kwargs):kwargs['timeout']=45;return await original(**kwargs)
        raw.retrieve=retrieve
        async def heartbeat():
            while True:
                ids={s.session_id for s in samplers if s.session_id}
                if trainer is not None and trainer.session:ids.add(trainer.session)
                for session in ids:await client.service.session_heartbeat(session_id=session,max_retries=0,timeout=10)
                await asyncio.sleep(10)
        keeper=asyncio.create_task(heartbeat())
        async def predictions(label,model_path):
            dest=d/label;dest.mkdir()
            sampler=SDKSampler(client,config['model_name'],model_path,renderer.get_stop_sequences(),512,polls=12);samplers.append(sampler)
            rows=await run_cases(test,prompts,tokenizer,renderer.get_stop_sequences(),sampler,dest,d.name+'-'+label)
            report=evaluate(test,graphs,rows,freeze=freeze);save(dest/'report.json',report)
            if any(r['status'] in ('transport_or_provider_failure','not_attempted_after_transport_failure') for r in rows):raise RuntimeError('Transport failure; future reconciliation required')
            return report
        try:
            base=await predictions('base',None)
            save(d/'progress.json',{'stage':'baseline_complete','successes':base['successes']})
            trainer=TrainingTransport(client,d/'training-events.jsonl',polls=12)
            await trainer.create(config['model_name'],config['lora_rank'])
            for epoch in range(3):
                output=await trainer.train_step(datums,config['learning_rate'])
                save(d/'progress.json',{'stage':'training','completed_epochs':epoch+1,'metrics':output.metrics})
            state=await trainer.checkpoint('experiment01-state',ttl_seconds=config['checkpoint_ttl_seconds'])
            manifest['state_checkpoint']=state;save(d/'manifest.json',manifest)
            sampler_path=await trainer.checkpoint('experiment01-sampler',sampler=True,ttl_seconds=config['checkpoint_ttl_seconds'])
            manifest['sampler_checkpoint']=sampler_path;save(d/'manifest.json',manifest)
            trained=await predictions('trained',sampler_path)
            result=compare(base,trained);save(d/'comparison.json',result)
            return {'status':'completed','comparison':result}
        finally:
            keeper.cancel()
            with contextlib.suppress(asyncio.CancelledError,Exception):await keeper

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true');p.add_argument('--run-dir',required=True);p.add_argument('--plan-sha256');a=p.parse_args()
    prepared=prepare_experiment();config=prepared[0];manifest=prepared[-1];d=Path(a.run_dir)
    if d.exists():p.error('Existing run; refuse resubmission')
    if a.live:
        if a.plan_sha256!=manifest['plan_sha256']:p.error('Dry-plan hash mismatch')
        authorization=json.loads(Path('training/budget-authorization.json').read_text())
        if authorization.get('account_credits_verified') is not True:p.error('Credits evidence missing')
        ledger=Ledger('runs/project-spend.sqlite',authorization)
        # Stable configuration key prevents rerunning this configuration under another directory.
        ledger.reserve(config['experiment_id'],'experiments',config['reservation_usd'],'Preregistered config and code '+manifest['plan_sha256'])
    d.mkdir(parents=True);save(d/'manifest.json',manifest)
    if not a.live:print(json.dumps(manifest));return
    manifest['status']='running';save(d/'manifest.json',manifest)
    try:manifest.update(asyncio.run(asyncio.wait_for(execute(d,prepared),timeout=1800)))
    except BaseException as e:manifest.update(status='halted_requires_reconciliation',error_type=type(e).__name__)
    manifest['billing_status']='Full reservation retained pending reconciled usage';save(d/'manifest.json',manifest)
    print(json.dumps({k:v for k,v in manifest.items() if k in ('status','error_type','comparison')}))
    if manifest['status']!='completed':raise SystemExit(1)
if __name__=='__main__':main()
