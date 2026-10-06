"""Approved deterministic migration; preserves v1 sources and measured artifacts."""
import copy,json,hashlib
from pathlib import Path
from liftlap.corpus import read,review_hash,audit

TRAIN_SOFT={5,8,14,38,46,48}

def migrate(case,training=False):
    row=copy.deepcopy(case);gold=row['gold_intent'];number=int(row['id'].split('-')[-1])
    original_hash=review_hash(case)
    if training:
        review=case.get('review',{})
        eligible=review.get('decision')=='approved' or (number in (5,13,28) and review.get('decision')=='change_requested')
        if (not eligible or review.get('human_reviewed') is not True or review.get('reviewed_content_sha256')!=original_hash or review.get('quarantine_reason')):
            raise ValueError('Migration requires current human-reviewed source and approved transformation')
    gold['schema_version']=2;gold['avoided_lift_types']=[]
    if (training and number in TRAIN_SOFT) or (not training and number==6):
        gold['avoided_lift_types']=sorted(gold['excluded_lift_types']);gold['excluded_lift_types']=[]
    duration={13:300,28:10}.get(number) if training else (5 if number==31 else None)
    if duration is not None:
        gold['duration_minutes']=duration;gold['clarification_fields'].remove('duration_minutes')
        gold['status']='unsupported' if gold['unsupported_preferences'] else 'clarify' if gold['clarification_fields'] else 'ready'
        row['gold_required_fields']=list(gold['clarification_fields'])
        row['expected_action']='interpret_only' if gold['status']=='ready' else gold['status']
    if training and number==35:
        gold['preferred_difficulties']=['blue']
    row['migration']={'from_schema':1,'source_review_hash':original_hash,'basis':'Emi approved duration preservation and avoid-vs-no semantics on 2026-10-06; deterministic migration, not a fresh independent label review'}
    if training and number==35:
        row['migration']['grade_target_basis']='Emi clarified blue target with easier green connections at 21:16 UTC'
    if training:
        row['split']='train'
        row['review']['decision']='approved'
        row['review']['approval_basis']='Original human review plus explicitly agreed deterministic v2 transformation'
        row['review']['reviewed_content_sha256']=review_hash(row)
        row['review']['original_review']=copy.deepcopy(case['review'])
        row['notes']='Approved v2 migration. Not a held-out case or terrain feasibility label.'
    return row

def main():
    train=[migrate(c,True) for c in read('benchmark/training-candidates.jsonl') if c['id']!='train-candidate-009']
    dev=[migrate(c) for c in read('benchmark/development-seed.jsonl')]
    report=audit(train+dev)
    if report['errors'] or report['warnings']:raise ValueError(report)
    out=Path('benchmark/v2');out.mkdir(exist_ok=True)
    for name,rows in [('training-reviewed.jsonl',train),('development.jsonl',dev)]:
        (out/name).write_text(''.join(json.dumps(c,sort_keys=True)+'\n' for c in rows))
    report.update(scope='approved_v2_migration_not_independent_test',excluded_training_ids=['train-candidate-009'],
                  input_sha256={f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in ['benchmark/training-candidates.jsonl','benchmark/development-seed.jsonl']},
                  output_sha256={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['training-reviewed.jsonl','development.jsonl']})
    (out/'migration-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
