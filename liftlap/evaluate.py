"""Offline graph-backed development harness; no model provider calls."""
import argparse
import json
from pathlib import Path
from collections import defaultdict
from .core import digest
from scripts.benchmark import load_cases,score
from . import fixtures
from .core import plan,validate_route

def evaluate(seed_path,scenario_path,predictions):
    seeds,_=load_cases(seed_path);by_id={c['id']:c for c in seeds}
    specs=json.loads(Path(scenario_path).read_text())
    if len({s['id'] for s in specs}) != len(specs): raise ValueError('Duplicate scenario id')
    for spec in specs:
        gold_status=by_id[spec['seed_case_id']]['gold_intent']['status']
        allowed={'ok','no_route'} if gold_status=='ready' else {gold_status}
        if spec['expected_planner_status'] not in allowed: raise ValueError('Expected outcome conflicts with gold action')
    lookup={}
    for p in predictions:
        if p['id'] in lookup:raise ValueError('Duplicate prediction')
        lookup[p['id']]=p.get('intent')
    if set(lookup)-{s['id'] for s in specs}:raise ValueError('Unknown scenario prediction')
    reports=[]
    for spec in specs:
        c=by_id[spec['seed_case_id']];gold=c['gold_intent'];pred=lookup.get(spec['id'])
        semantic=score([c],[{'id':c['id'],'intent':pred}])['cases'][0]
        g=fixtures.graph();s=fixtures.scenario(g)
        for edge_id,changes in spec['edge_overrides'].items():s['edges'][edge_id].update(changes)
        actual=None;gold_valid=False
        if semantic['valid'] and pred['status']=='ready':
            actual=plan(g,pred,s)
            if actual['status']=='ok':gold_valid=validate_route(g,gold,s,actual['route'])['valid']
        elif semantic['valid']:
            actual={'status':pred['status']}
        success=semantic['exact_match'] and actual is not None and actual['status']==spec['expected_planner_status'] and (actual['status']!='ok' or gold_valid)
        reports.append({'id':spec['id'],'family_id':c['family_id'],'expected_action':('plan' if gold['status']=='ready' else gold['status']),'expected_outcome':spec['expected_planner_status'],'intent_exact_match':semantic['exact_match'],'planner_status':actual['status'] if actual else 'invalid_intent',
                        'route_valid_against_gold':gold_valid if actual and actual['status']=='ok' else None,'success':success})
    slices=defaultdict(lambda: {'count':0,'successes':0})
    for row in reports:
        group=slices[row['expected_outcome']];group['count']+=1;group['successes']+=int(row['success'])
    return {'fixture_hashes': {'graph':digest(fixtures.graph()),'scenario_specs':digest(specs)},'by_expected_outcome':dict(slices),'scope':'synthetic_graph_development_cases_not_model_benchmark','cases':reports,'count':len(reports),'successes':sum(r['success'] for r in reports)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--predictions',required=True)
    p.add_argument('--seed',default='benchmark/development-seed.jsonl')
    p.add_argument('--scenarios',default='benchmark/route-development.json')
    a=p.parse_args();preds=[json.loads(l) for l in Path(a.predictions).read_text().splitlines() if l.strip()]
    print(json.dumps(evaluate(a.seed,a.scenarios,preds),indent=2))

if __name__=='__main__':main()
