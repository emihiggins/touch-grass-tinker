"""Local Cookbook rendering/masking audit and dry-run Datum preparation; no API calls."""
import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
from .corpus import read,conversation,audit

RENDERER='qwen3_disable_thinking'
COOKBOOK_COMMIT='1c03a20fdda98156ccbec15728c0e2764b5a0bc3'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def value_sha(value):
    """Canonical JSON hash, distinct from exact file/text byte hashes."""
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',', ':'),allow_nan=False).encode()).hexdigest()

def datum_payload(datum):
    return {'input_tokens':datum.model_input.to_ints(),
            'target_tokens':datum.loss_fn_inputs['target_tokens'].to_torch().tolist(),
            'weights':datum.loss_fn_inputs['weights'].to_torch().tolist()}

def verify_datum(datum,tokens,prefix_length):
    payload=datum_payload(datum)
    if payload['input_tokens']!=tokens[:-1] or payload['target_tokens']!=tokens[1:]:
        raise ValueError('Next-token alignment mismatch')
    weights=payload['weights'];count=len(tokens)-prefix_length
    if count<=0 or prefix_length<1 or len(weights)!=len(tokens)-1:
        raise ValueError('Invalid shifted mask dimensions')
    expected=[0.]*(prefix_length-1)+[1./count]*count
    if any(not math.isfinite(v) or not math.isclose(v,e,rel_tol=1e-5,abs_tol=1e-8)
           for v,e in zip(weights,expected)):
        raise ValueError('Shifted assistant-only loss weights mismatch')
    return payload

def load_renderer(directory,manifest_path):
    from transformers import AutoTokenizer
    from tinker_cookbook.renderers import get_renderer
    manifest=json.loads(Path(manifest_path).read_text())
    for name,entry in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('Invalid tokenizer filename')
        if sha(Path(directory)/name)!=entry['sha256']:raise ValueError('Tokenizer checksum mismatch')
    dist=importlib.metadata.distribution('tinker-cookbook')
    origin=json.loads(dist.read_text('direct_url.json') or '{}')
    if origin.get('vcs_info',{}).get('commit_id')!=COOKBOOK_COMMIT:raise ValueError('Cookbook commit mismatch')
    tokenizer=AutoTokenizer.from_pretrained(directory,local_files_only=True,trust_remote_code=False)
    return tokenizer,get_renderer(RENDERER,tokenizer)

def render_case(case,prompt,tokenizer,renderer,max_length=2048,max_output=512):
    from tinker_cookbook.renderers import TrainOnWhat
    from tinker_cookbook.supervised.common import datum_from_model_input_weights
    messages=conversation(case,prompt)['messages']
    if [m['role'] for m in messages]!=['system','user','assistant']:raise ValueError('Single-turn contract required')
    model_input,weights=renderer.build_supervised_example(messages,train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
    tokens=model_input.to_ints();w=weights.tolist()
    prefix=renderer.build_generation_prompt(messages[:-1]).to_ints()
    if len(tokens)>max_length:raise ValueError('Example exceeds context; refusing truncation')
    if tokens[:len(prefix)]!=prefix:raise ValueError('Train/inference prefix mismatch')
    if any(v!=0 for v in w[:len(prefix)]):raise ValueError('Prompt tokens receive training loss')
    if len(tokens)!=len(w) or not all(v==1 for v in w[len(prefix):]):raise ValueError('Invalid answer mask')
    answer_tokens=tokens[len(prefix):]
    if not answer_tokens or len(answer_tokens)>max_output:raise ValueError('Target does not fit sampling output budget')
    expected=messages[-1]['content']+tokenizer.decode(renderer.get_stop_sequences())
    if tokenizer.decode(answer_tokens)!=expected:raise ValueError('Assistant target round trip mismatch')
    datum=datum_from_model_input_weights(model_input,weights,max_length=None,reduction='mean')
    payload=verify_datum(datum,tokens,len(prefix))
    shifted_weights=payload['weights']
    return {'id':case['id'],'split':case['split'],'total_tokens':len(tokens),'prompt_tokens':len(prefix),
            'answer_tokens':len(answer_tokens),'prompt_loss_tokens':0,'target_round_trip':True,
            'next_token_alignment':True,'loss_weight_sum':sum(shifted_weights),
            'source_sha256':value_sha({k:case[k] for k in ('request_text','ui_context','catalog')}),
            'target_text_sha256':hashlib.sha256(messages[-1]['content'].encode()).hexdigest(),
            'sequence_sha256':value_sha(tokens),'sdk_datum_sha256':value_sha(payload),
            'assistant_prefix_length':len(prefix),
            'weighted_target_range':{'start_inclusive':len(prefix)-1,'end_exclusive':len(tokens)-1},
            'final_token_ids':answer_tokens[-8:], 'stop_sequence':renderer.get_stop_sequences(),
            'decoded_target_suffix':tokenizer.decode(answer_tokens)[-96:]},datum

def prepare(cases,prompt,tokenizer,renderer,config):
    result=audit(cases)
    if result['errors']:raise ValueError('Corpus structural audit failed')
    reports=[];datums=[]
    for c in cases:
        r,d=render_case(c,prompt,tokenizer,renderer,config['max_length'],config['sampling']['max_tokens'])
        reports.append(r);datums.append(d)
    if not reports:raise ValueError('No cases')
    return {'report_version':'target-audit-v1','environment':{name:importlib.metadata.version(name) for name in ('tinker','tinker-cookbook','transformers','tokenizers','torch')},'scope':'local_rendering_only_not_training_approval','renderer':RENDERER,
            'train_on_what':'last_assistant_message','count':len(reports),
            'max_total_tokens':max(r['total_tokens'] for r in reports),
            'max_answer_tokens':max(r['answer_tokens'] for r in reports),
            'total_sequence_tokens':sum(r['total_tokens'] for r in reports),
            'total_answer_tokens':sum(r['answer_tokens'] for r in reports),
            'truncated_examples':0,'prompt_loss_tokens':0,'cases':reports,'corpus_warnings':result['warnings'],'batch_preview':{'batch_size':config['batch_size'],'complete_batches':len(cases)//config['batch_size'],'leftover_rows':len(cases)%config['batch_size'],'launch_authorized':False}},datums

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('cases');p.add_argument('--tokenizer',default='.tokenizer-qwen3')
    p.add_argument('--tokenizer-manifest',default='training/tokenizer-manifest.json')
    p.add_argument('--config',default='training/sft-plan.json');p.add_argument('--prompt',default='benchmark/baseline-prompt.txt')
    p.add_argument('--preview-datums',help='Optional dry-run payload; never submitted to a provider')
    a=p.parse_args();tokenizer,renderer=load_renderer(a.tokenizer,a.tokenizer_manifest)
    cases=read(a.cases);config=json.loads(Path(a.config).read_text())
    if config['train_on_what']!='last_assistant_message':raise ValueError('Rendering mode must match plan')
    report,datums=prepare(cases,Path(a.prompt).read_text(),tokenizer,renderer,config)
    report['input_sha256']={name:sha(path) for name,path in [('cases',a.cases),('prompt',a.prompt),('config',a.config),('tokenizer_manifest',a.tokenizer_manifest)]}
    report['cookbook_commit']=COOKBOOK_COMMIT
    if a.preview_datums:
        out=Path(a.preview_datums);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(''.join(json.dumps({'id':c['id'],'preview_only':True,'datum':{'input_tokens':d.model_input.to_ints(),'target_tokens':d.loss_fn_inputs['target_tokens'].to_torch().tolist(),'weights':d.loss_fn_inputs['weights'].to_torch().tolist()}},sort_keys=True)+'\n' for c,d in zip(cases,datums)))
        report['preview_datums_sha256']=sha(out)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
