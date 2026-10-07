"""Read-only, deterministic structural audit; never certifies skier access."""
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def directed_audit(g):
 nodes={n['id'] for n in g['nodes']};forward={n:set() for n in nodes};reverse={n:set() for n in nodes}
 for e in g['edges']:
  if e['from'] in nodes and e['to'] in nodes:
   forward[e['from']].add(e['to']);reverse[e['to']].add(e['from'])
 # Iterative Kosaraju: no recursion limit for larger future snapshots.
 visited=set();order=[]
 for start in sorted(nodes):
  if start in visited:continue
  stack=[(start,False)]
  while stack:
   n,done=stack.pop()
   if done:order.append(n);continue
   if n in visited:continue
   visited.add(n);stack.append((n,True))
   stack.extend((v,False) for v in sorted(forward[n],reverse=True) if v not in visited)
 visited=set();sizes=[];cyclic=0
 for start in reversed(order):
  if start in visited:continue
  stack=[start];visited.add(start);component=[]
  while stack:
   n=stack.pop();component.append(n)
   for v in sorted(reverse[n]):
    if v not in visited:visited.add(v);stack.append(v)
  sizes.append(len(component))
  if len(component)>1 or start in forward[start]:cyclic+=len(component)
 return {'strong_component_sizes':sorted(sizes,reverse=True),'nodes_on_directed_cycles':cyclic,'source_nodes':sorted(n for n in nodes if forward[n] and not reverse[n]),'sink_nodes':sorted(n for n in nodes if reverse[n] and not forward[n]),'interpretation':'Directed cycles are a topology property only, not permission, closure, grade or time feasibility.'}

def audit(path):
 raw=path.read_bytes();g=json.loads(raw);nodes={n['id'] for n in g['nodes']};adj={n:set() for n in nodes};missing=[]
 for e in g['edges']:
  if e['from'] not in nodes or e['to'] not in nodes:missing.append(e['id']);continue
  adj[e['from']].add(e['to']);adj[e['to']].add(e['from'])
 remaining=set(nodes);components=[]
 while remaining:
  stack=[min(remaining)];remaining.remove(stack[0]);size=0
  while stack:
   n=stack.pop();size+=1
   for nxt in sorted(adj[n]&remaining):remaining.remove(nxt);stack.append(nxt)
  components.append(size)
 return {'directed_connectivity':directed_audit(g),'schema':2,'scope':'structural_snapshot_audit_not_access_or_safety_validation','snapshot':str(path.relative_to(ROOT)),'snapshot_sha256':hashlib.sha256(raw).hexdigest(),'graph_source_sha256':g['source_sha256'],'license':g['source_license'],'attribution':g['attribution'],'review_status':g['review_status'],'difficulty_convention':g['difficulty_convention'],'nodes':len(nodes),'edges':len(g['edges']),'edge_kinds':dict(sorted(Counter(e['kind'] for e in g['edges']).items())),'weak_component_sizes':sorted(components,reverse=True),'missing_endpoint_edges':missing,'without_source_refs':sum(not e.get('source_refs') for e in g['edges']),'without_geometry':sum(not e.get('geometry') for e in g['edges']),'duration_basis':dict(sorted(Counter(e.get('duration_basis','unknown') for e in g['edges']).items())),'open_gates':['Direction/access review','Station boarding and transfers','Operator schedules and current closures','Measured timing and field validation'],'automatic_connections_added':0}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--snapshot',type=Path,default=ROOT/'data/terrain/alpendorf-lab.json');p.add_argument('--output',type=Path,default=ROOT/'research/evidence/alpendorf-snapshot-audit.json');a=p.parse_args()
 report=audit(a.snapshot.resolve());out=a.output;out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
