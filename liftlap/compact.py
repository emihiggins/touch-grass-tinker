"""Scenario-specific contraction of nonbranching piste chains, with reversible paths."""
import collections
import copy
from .core import check_graph,digest,validate_route


def compact(graph,scenario,protected=()):
    check_graph(graph)
    if scenario['graph_hash']!=digest(graph):raise ValueError('Scenario graph mismatch')
    if any('source_edge_ids' in e for e in graph['edges']):raise ValueError('Already compacted')
    incoming=collections.defaultdict(list);outgoing=collections.defaultdict(list)
    for e in graph['edges']:
        incoming[e['to']].append(e);outgoing[e['from']].append(e)
    protected=set(protected)
    for e in graph['edges']:
        if e['kind']=='lift':protected.update([e['from'],e['to']])
    def signature(e):
        state=scenario['edges'].get(e['id'])
        # Unknown/missing states are not silently converted into common defaults.
        if not state or state.get('queue_s')!=0:return None
        return (e['kind'],e.get('difficulty'),e.get('review_status'),e.get('duration_basis'),digest(state))
    following={};previous={}
    for node,ins in incoming.items():
        outs=outgoing[node]
        if node in protected or len(ins)!=1 or len(outs)!=1:continue
        a,b=ins[0],outs[0]
        if a['id']==b['id'] or a['kind']!='piste' or b['kind']!='piste':continue
        if signature(a) is not None and signature(a)==signature(b):
            following[a['id']]=b;previous[b['id']]=a
    used=set();new=[];states={}
    starts=sorted(graph['edges'],key=lambda e:(e['id'] in previous,e['id']))
    for first in starts:
        if first['id'] in used:continue
        chain=[first];used.add(first['id'])
        while chain[-1]['id'] in following:
            nxt=following[chain[-1]['id']]
            if nxt['id'] in used:break
            chain.append(nxt);used.add(nxt['id'])
        edge=copy.deepcopy(first)
        ids=[e['id'] for e in chain]
        edge['id']=first['id'] if len(chain)==1 else 'chain:'+digest(ids)[:20]
        edge['to']=chain[-1]['to'];edge['source_edge_ids']=ids
        edge['duration_s']=sum(e['duration_s'] for e in chain)
        edge['length_m']=sum(e['length_m'] for e in chain)
        edge['source_names']=list(dict.fromkeys(e.get('name',e['id']) for e in chain))
        if all('geometry' in e for e in chain):
            geometry=copy.deepcopy(chain[0]['geometry'])
            for e in chain[1:]:
                if geometry[-1]!=e['geometry'][0]:raise ValueError('Native-node geometry mismatch')
                geometry.extend(e['geometry'][1:])
            edge['geometry']=geometry
        new.append(edge)
        if first['id'] in scenario['edges']:states[edge['id']]=copy.deepcopy(scenario['edges'][first['id']])
    g=copy.deepcopy(graph);g['edges']=new
    kept={e[k] for e in new for k in ['from','to']}|protected
    g['nodes']=[n for n in graph['nodes'] if n['id'] in kept]
    g['original_graph_hash']=digest(graph)
    s=copy.deepcopy(scenario);s['edges']=states;s['graph_hash']=digest(g)
    return g,s


def expand_route(original,scenario,compacted,result,intent,*,lab=False):
    if compacted.get('original_graph_hash')!=digest(original):raise ValueError('Wrong original graph')
    if result.get('graph_hash')!=digest(compacted):raise ValueError('Wrong compact graph')
    lookup={e['id']:e for e in compacted['edges']}
    expanded={'edge_ids':[sid for eid in result['edge_ids'] for sid in lookup[eid]['source_edge_ids']],
              'total_seconds':result['total_seconds'],'graph_hash':digest(original),'scenario_hash':digest(scenario)}
    if not validate_route(original,intent,scenario,expanded,lab=lab)['valid']:raise ValueError('Expanded route failed original validation')
    return expanded
