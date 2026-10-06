"""Graph-backed v2 evaluation. Unreviewed candidates permit fixture self-check only."""
import argparse,copy,json
from pathlib import Path
from .corpus import read,audit,label_approved
from .core import plan,validate_route,digest
from scripts.benchmark import score


def evaluate(cases,bundles,predictions,*,fixture_self_check=False,freeze=None):
    if not cases or audit(cases)['errors']:raise ValueError('Invalid evaluation corpus')
    if not fixture_self_check and any(c['split']!='test' or not label_approved(c) for c in cases):
        raise ValueError('Model scoring requires frozen human-approved test cases')
    if not fixture_self_check and (not isinstance(freeze,dict) or freeze.get('status')!='frozen'
            or freeze.get('cases_sha256')!=digest(cases) or freeze.get('graph_bundle_sha256')!=digest(bundles)):
        raise ValueError('Missing or stale evaluation freeze manifest')
    if fixture_self_check:
        if predictions is not None:raise ValueError('Self-check cannot consume model predictions')
        predictions=[{'id':c['id'],'intent':c['gold_intent']} for c in cases]
    semantics=score(cases,predictions);lookup={p['id']:p.get('intent') for p in predictions};rows=[]
    for case,semantic in zip(cases,semantics['cases']):
        bundle=bundles[case['scenario_family']];g=bundle['graph'];s=copy.deepcopy(bundle['scenario'])
        for eid,patch in case['edge_overrides'].items():s['edges'][eid].update(patch)
        intent=lookup.get(case['id']);outcome='invalid_intent';valid_route=None;tradeoffs=[]
        if semantic['valid']:
            outcome=intent['status']
            if outcome=='ready':
                try:result=plan(g,intent,s)
                except ValueError:result={'status':'operational_limit','route':None}
                outcome=result['status'];tradeoffs=result.get('preference_tradeoffs',[])
                if outcome=='ok':valid_route=validate_route(g,case['gold_intent'],s,result['route'])['valid']
        rows.append({'id':case['id'],'intent_exact_match':semantic['exact_match'],'outcome':outcome,
                     'expected_outcome':case['expected_planner_status'],'gold_route_valid':valid_route,
                     'preference_tradeoffs':tradeoffs,'success':semantic['exact_match'] and outcome==case['expected_planner_status'] and valid_route is not False})
    return {'scope':'fixture_self_check_not_model_performance' if fixture_self_check else 'reviewed_test_model_evaluation',
            'count':len(rows),'successes':sum(r['success'] for r in rows),'cases':rows,'graph_bundle_sha256':digest(bundles)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases',default='benchmark/v2/evaluation-candidates.jsonl')
    p.add_argument('--graphs',default='benchmark/v2/evaluation-graphs.json')
    p.add_argument('--freeze-manifest',help='Required for model scoring; binds canonical case and graph hashes')
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--fixture-self-check',action='store_true');mode.add_argument('--predictions')
    a=p.parse_args();r=evaluate(read(a.cases),json.loads(Path(a.graphs).read_text()),
                              read(a.predictions) if a.predictions else None,fixture_self_check=a.fixture_self_check,
                              freeze=json.loads(Path(a.freeze_manifest).read_text()) if a.freeze_manifest else None)
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
