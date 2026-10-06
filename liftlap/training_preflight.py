"""Offline readiness report only. Never launches training or calls a provider."""
import argparse
import hashlib
import json
from pathlib import Path
from .corpus import audit,read,label_approved

GATES={'corpus_review_complete','independent_test_frozen','rendered_masks_and_no_truncation_verified',
       'dependency_versions_locked_and_smoked','baseline_recorded','account_access_verified','credits_and_spend_cap_verified'}

def check(cases,config):
    report=audit(cases);blockers=list(report['errors'])+list(report['warnings'])
    train=[c for c in cases if c['split']=='train'];candidates=[c for c in cases if c['split']=='train_candidate']
    if not train:blockers.append('No approved training rows')
    if any(not label_approved(c) for c in train):blockers.append('Training labels need current explicit approval without quarantine')
    if not any(c['split']=='test' for c in cases):blockers.append('Independent test partition absent')
    if not any(c['split'] in {'development','development_seed'} for c in cases):blockers.append('Development partition absent')
    gates=config.get('launch_gates',{})
    for gate in sorted(GATES):
        if gates.get(gate) is not True:blockers.append('Unmet gate: '+gate)
    batch=config.get('batch_size');batch_valid=type(batch) is int and batch>0
    if not batch_valid:blockers.append('batch_size must be a positive integer')
    full=len(train)//batch if batch_valid else 0;dropped=len(train)%batch if batch_valid else len(train)
    if full==0:blockers.append('Training would execute zero complete batches')
    if dropped:blockers.append('Incomplete final batch would silently drop training rows')
    if config.get('test_size')!=0:blockers.append('Cookbook random row splitting must remain disabled')
    if config.get('train_on_what') not in {'all_assistant_messages','last_assistant_message'}:blockers.append('Assistant-only supervision required')
    if type(config.get('max_length')) is not int or config['max_length']<=0:blockers.append('Invalid max_length')
    if type(config.get('epochs')) is not int or config['epochs']<=0:blockers.append('Invalid epochs')
    return {'status':'blocked' if blockers else 'declarations_complete_evidence_review_required',
            'launch_authorized':False,'scope':'offline_structural_preflight_not_evidence_verification_or_spend_permission',
            'approved_train_count':len(train),'candidate_count':len(candidates),'complete_batches_per_epoch':full,
            'dropped_rows_per_epoch':dropped,'blockers':sorted(set(blockers)),
            'note':'Boolean gates are declarations, not proof. Verify linked evidence, tokenizer/masks, holdout provenance and budget before a runner is enabled.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('files',nargs='+');p.add_argument('--config',default='training/sft-plan.json')
    a=p.parse_args();r=check([c for f in a.files for c in read(f)],json.loads(Path(a.config).read_text()))
    r['input_sha256']={f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in [*a.files,a.config]}
    print(json.dumps(r,indent=2))
    raise SystemExit(1 if r['blockers'] else 0)

if __name__=='__main__':main()
