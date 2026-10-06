"""Paired full-request DEVELOPMENT comparison against the same fixed fixtures."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random
from .corpus import read
from .evaluate import evaluate

def compare(seed_path, scenario_path, baseline, tuned, draws=5000, seed=0):
    if type(draws) is not int or draws < 100: raise ValueError('Need at least 100 draws')
    a=evaluate(seed_path,scenario_path,baseline);b=evaluate(seed_path,scenario_path,tuned)
    if not a['count']: raise ValueError('Empty scenarios')
    clusters=defaultdict(list);slices=defaultdict(lambda:{'count':0,'baseline_successes':0,'tuned_successes':0})
    transitions={'both_success':0,'improved':0,'regressed':0,'both_failed':0};rows=[]
    for x,y in zip(a['cases'],b['cases']):
        delta=int(y['success'])-int(x['success'])
        clusters[x['family_id']].append(delta)
        group=slices[x['expected_outcome']];group['count']+=1
        group['baseline_successes']+=int(x['success']);group['tuned_successes']+=int(y['success'])
        state='both_success' if x['success'] and y['success'] else 'improved' if delta==1 else 'regressed' if delta==-1 else 'both_failed'
        transitions[state]+=1
        rows.append({'id':x['id'],'transition':state,'baseline':x,'tuned':y})
    rng=random.Random(seed);values=list(clusters.values());samples=[]
    for _ in range(draws):
        sample=[v for group in rng.choices(values,k=len(values)) for v in group]
        samples.append(100*sum(sample)/len(sample))
    samples.sort()
    def violations(report):
        return sum(r['route_valid_against_gold'] is False for r in report['cases'])
    return {'metric':'strict_gold_intent_and_request_outcome_success','scope':'synthetic_development_only_not_held_out',
            'count':a['count'],'baseline_successes':a['successes'],'tuned_successes':b['successes'],
            'delta_percentage_points':100*(b['successes']-a['successes'])/a['count'],
            'paired_family_bootstrap':{'draws':draws,'seed':seed,'clusters':len(values),
                'interval_95_percentage_points':[samples[int(.025*draws)],samples[int(.975*draws)]],
                'caveat':'Shared synthetic graph and visible labels; this interval is not evidence of held-out generalization.'},
            'gold_route_rejections':{'baseline':violations(a),'tuned':violations(b)},
            'search_limit_counts':{name:sum(r['planner_status']=='search_limit' for r in report['cases']) for name,report in [('baseline',a),('tuned',b)]},
            'transitions':transitions,'by_expected_outcome':dict(slices),'cases':rows,'fixture_hashes':a['fixture_hashes']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('baseline');p.add_argument('tuned')
    p.add_argument('--seed',default='benchmark/development-seed.jsonl')
    p.add_argument('--scenarios',default='benchmark/request-development.json')
    a=p.parse_args();r=compare(a.seed,a.scenarios,read(a.baseline),read(a.tuned))
    r['input_sha256']={k:hashlib.sha256(Path(v).read_bytes()).hexdigest() for k,v in vars(a).items()}
    print(json.dumps(r,indent=2))

if __name__=='__main__':main()
