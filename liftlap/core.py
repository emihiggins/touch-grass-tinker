"""Bounded offline reference planner and independent route validator.
Standard library only; not the planned production NetworkX adapter.
"""
import collections
import datetime as dt
import hashlib
import json
import math
import time

RANK={'green':0,'blue':1,'red':2,'black':3}
LIFTS={'chairlift','gondola','cable-car','t-bar','platter','rope-tow','magic-carpet'}

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def stamp(value):
    value=dt.datetime.fromisoformat(value)
    if value.tzinfo is None:raise ValueError('Timezone required')
    return value

def positive(value):
    return type(value) in (int,float) and math.isfinite(value) and value>0

def check_graph(graph):
    if graph.get('schema_version')!=1:raise ValueError('Unsupported graph version')
    nodes=graph['nodes'];edges=graph['edges']
    if len({n['id'] for n in nodes})!=len(nodes):raise ValueError('Duplicate node')
    ids={n['id'] for n in nodes}
    if len({e['id'] for e in edges})!=len(edges):raise ValueError('Duplicate edge')
    for e in edges:
        if e['from'] not in ids or e['to'] not in ids:raise ValueError('Missing node reference')
        if not positive(e['duration_s']) or not positive(e['length_m']):raise ValueError('Invalid edge weight')
        if e['kind'] not in {'lift','piste'}:raise ValueError('Unsupported edge kind')
        if e['kind']=='piste' and e['difficulty'] not in RANK:raise ValueError('Missing difficulty')
        if e['kind']=='lift' and e['lift_type'] not in LIFTS:raise ValueError('Missing lift type')
    return {e['id']:e for e in edges}

def check_request(graph,intent,scenario):
    edges=check_graph(graph)
    if intent.get('status')!='ready':raise ValueError('Intent not ready')
    if intent.get('hard_max_difficulty') not in RANK:raise ValueError('Missing maximum difficulty')
    if not isinstance(intent.get('excluded_lift_types'),list) or not set(intent['excluded_lift_types'])<=LIFTS:raise ValueError('Invalid lift exclusions')
    if not isinstance(intent.get('preferred_difficulties'),list) or not set(intent['preferred_difficulties'])<=set(RANK):raise ValueError('Invalid difficulty preferences')
    if type(intent.get('prefer_variety')) is not bool:raise ValueError('Missing variety preference')
    minutes=intent.get('duration_minutes')
    version=intent.get('schema_version',1)
    if type(version) is not int or version not in (1,2):raise ValueError('Unsupported intent version')
    if version==2:
        from scripts.benchmark import validate_intent
        validate_intent(intent,{n['id'] for n in graph['nodes']})
    if type(minutes) is not int or not (15<=minutes<=240 if version==1 else 1<=minutes<=1440):raise ValueError('Planner horizon exceeded: v2 supports 1–1440 minutes')
    start=stamp(intent['start_time'])
    nodes={n['id'] for n in graph['nodes']}
    if intent.get('start_place_id') not in nodes or intent.get('finish_place_id') not in nodes:raise ValueError('Unknown place/node')
    if scenario.get('graph_hash')!=digest(graph):raise ValueError('Scenario graph mismatch')
    if scenario.get('simulated') is not True:raise ValueError('Only simulated scenarios supported')
    if scenario.get('date')!=start.astimezone(__import__('zoneinfo').ZoneInfo(graph['timezone'])).date().isoformat():raise ValueError('Scenario date mismatch')
    for edge_id,state in scenario['edges'].items():
        if edge_id not in edges:raise ValueError('Unknown scenario edge')
        if state['status'] not in {'open','closed','unknown'}:raise ValueError('Invalid edge status')
        q=state['queue_s']
        if type(q) not in (int,float) or not math.isfinite(q) or q<0:raise ValueError('Invalid queue time')
        if edges[edge_id]['kind']!='lift' and q!=0:raise ValueError('Queue assigned to non-lift')
        if stamp(state['opens_at'])>=stamp(state['closes_at']):raise ValueError('Invalid open interval')
    return edges,start,minutes*60

def validate_route(graph,intent,scenario,result,*,lab=False):
    """Recompute legality independently of search, never trust totals or flags."""
    try:edges,start,budget=check_request(graph,intent,scenario)
    except (ValueError,KeyError,TypeError):return {'valid':False,'reason':'invalid_input'}
    if graph.get('review_status')!='synthetic' and not lab:return {'valid':False,'reason':'unreviewed_graph'}
    if result.get('graph_hash')!=digest(graph) or result.get('scenario_hash')!=digest(scenario):return {'valid':False,'reason':'snapshot_mismatch'}
    path=result.get('edge_ids',[])
    if not isinstance(path,list) or not path:return {'valid':False,'reason':'empty_outing'}
    position=intent['start_place_id'];elapsed=0;kinds=set();visits=collections.Counter()
    for eid in path:
        try:e=edges[eid]
        except (KeyError,TypeError):return {'valid':False,'reason':'unknown_edge'}
        if not lab and e.get('review_status') not in {'synthetic','verified'}:return {'valid':False,'reason':'unreviewed_edge'}
        if e['from']!=position:return {'valid':False,'reason':'disconnected'}
        if e['kind']=='piste' and RANK[e['difficulty']]>RANK[intent['hard_max_difficulty']]:return {'valid':False,'reason':'difficulty'}
        if e['kind']=='lift' and e['lift_type'] in intent['excluded_lift_types']:return {'valid':False,'reason':'excluded_lift'}
        state=scenario['edges'].get(eid)
        if state is None or state['status']!='open':return {'valid':False,'reason':'not_open'}
        arrival=start+dt.timedelta(seconds=elapsed)
        if arrival<stamp(state['opens_at']):return {'valid':False,'reason':'not_yet_open'}
        elapsed+=state['queue_s']+e['duration_s']
        if start+dt.timedelta(seconds=elapsed)>stamp(state['closes_at']):return {'valid':False,'reason':'closed_before_completion'}
        if elapsed>budget:return {'valid':False,'reason':'deadline'}
        visits[eid]+=1;position=e['to'];kinds.add(e['kind'])
    if position!=intent['finish_place_id']:return {'valid':False,'reason':'wrong_finish'}
    if kinds!={'lift','piste'}:return {'valid':False,'reason':'not_ski_outing'}
    if sum(len(edges[eid].get('source_edge_ids',[eid])) for eid in path)>40 or max(visits.values())>2:return {'valid':False,'reason':'path_bound'}
    if not isinstance(result.get('total_seconds'),(int,float)) or not math.isclose(result['total_seconds'],elapsed,abs_tol=1e-6):return {'valid':False,'reason':'incorrect_total'}
    return {'valid':True,'reason':'valid_simulated_outing','total_seconds':elapsed}

def preference_tradeoffs(graph,intent,result):
    """Disclose actual soft-preference misses, never claim unavoidable/optimal."""
    edges={e['id']:e for e in graph['edges']}
    used=[eid for eid in result['edge_ids'] if edges[eid]['kind']=='lift'
          and edges[eid]['lift_type'] in intent.get('avoided_lift_types',[])]
    return [{'kind':'soft_lift_avoidance','edge_ids':used,
             'lift_types':sorted({edges[eid]['lift_type'] for eid in used}),
             'message':'This outing uses a lift you preferred to avoid. Hard exclusions remain enforced; alternatives may exist outside this bounded search.'}] if used else []

def plan(graph,intent,scenario,*,lab=False,max_states=20000,timeout_s=2,max_edges=40,max_visits=2):
    edges,start,budget=check_request(graph,intent,scenario)
    if graph.get('review_status')!='synthetic' and not lab:
        return {'status':'unreviewed_graph','simulated':True,'route':None}
    if not 1<=max_edges<=40 or not 1<=max_visits<=2 or max_states<1 or timeout_s<=0:raise ValueError('Invalid search bounds')
    adj=collections.defaultdict(list)
    for e in edges.values():adj[e['from']].append(e)
    for values in adj.values():values.sort(key=lambda e:e['id'])
    reachable={intent['start_place_id']};frontier=list(reachable)
    while frontier:
        for edge in adj[frontier.pop()]:
            if edge['to'] not in reachable:reachable.add(edge['to']);frontier.append(edge['to'])
    if intent['finish_place_id'] not in reachable:
        return {'status':'no_route','route':None,'simulated':True,'expanded_states':0,
                'scope':'finish_unreachable_in_supplied_directed_graph','reasons':['finish_unreachable']}
    todo=collections.deque([(intent['start_place_id'],0,[],frozenset(),{})])
    began=time.monotonic();expanded=0;best=None;best_score=None;limited=False;depth_pruned=False;blocked=set()
    while todo:
        if expanded>=max_states or time.monotonic()-began>=timeout_s:limited=True;break
        position,elapsed,path,kinds,visits=todo.popleft();expanded+=1
        if position==intent['finish_place_id'] and kinds=={'lift','piste'}:
            unique=[edges[eid] for eid in sorted(set(path)) if edges[eid]['kind']=='piste']
            preferred=sum(e['length_m'] for e in unique if e['difficulty'] in intent['preferred_difficulties'])
            ski_distance = sum(e['length_m'] for e in unique) if intent['prefer_variety'] else sum(edges[eid]['length_m'] for eid in path if edges[eid]['kind']=='piste')
            avoided=sum(1 for eid in path if edges[eid]['kind']=='lift' and edges[eid]['lift_type'] in intent.get('avoided_lift_types',[]))
            score=(-avoided,preferred,ski_distance,-elapsed) if intent.get('schema_version')==2 else (preferred,ski_distance,-elapsed)
            if best_score is None or score>best_score:
                best_score=score;best={'edge_ids':path,'total_seconds':elapsed,'graph_hash':digest(graph),'scenario_hash':digest(scenario)}
        source_count=sum(len(edges[eid].get('source_edge_ids',[eid])) for eid in path)
        if source_count>=max_edges:depth_pruned=True;continue
        for e in adj[position]:
            if source_count+len(e.get('source_edge_ids',[e['id']]))>max_edges:depth_pruned=True;continue
            if not lab and e.get('review_status') not in {'synthetic','verified'}:
                blocked.add('unreviewed_edge');continue
            if visits.get(e['id'],0)>=max_visits:depth_pruned=True;continue
            if e['kind']=='piste' and RANK[e['difficulty']]>RANK[intent['hard_max_difficulty']]:
                blocked.add('difficulty');continue
            if e['kind']=='lift' and e['lift_type'] in intent['excluded_lift_types']:
                blocked.add('excluded_lift');continue
            state=scenario['edges'].get(e['id'])
            if not state:
                blocked.add('missing_state');continue
            if state['status']!='open':
                blocked.add('closed' if state['status']=='closed' else 'unknown_status');continue
            arrival=start+dt.timedelta(seconds=elapsed)
            end=elapsed+state['queue_s']+e['duration_s']
            if arrival<stamp(state['opens_at']):
                blocked.add('not_yet_open');continue
            if end>budget:
                blocked.add('deadline');continue
            if start+dt.timedelta(seconds=end)>stamp(state['closes_at']):
                blocked.add('closed_before_completion');continue
            v=visits.copy();v[e['id']]=v.get(e['id'],0)+1
            todo.append((e['to'],end,path+[e['id']],kinds|{e['kind']},v))
    if best is not None:
        verification=validate_route(graph,intent,scenario,best,lab=lab)
        if not verification['valid']:raise RuntimeError('Planner produced invalid candidate: '+verification['reason'])
        return {'status':'ok','route':best,'simulated':True,'lab':lab,'search_complete':not limited and not depth_pruned,'expanded_states':expanded,'optimality_claim':False,'validation':verification,'preference_tradeoffs':preference_tradeoffs(graph,intent,best)}
    status='search_limit' if limited or depth_pruned else 'no_route'
    result={'status':status,'route':None,'simulated':True,'expanded_states':expanded,'scope':'bounded_reference_search'}
    if status=='no_route':result['reasons']=sorted(blocked)
    return result
