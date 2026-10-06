"""Read-only, deterministic structural audit; never certifies skier access."""
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
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
 return {'schema':1,'scope':'structural_snapshot_audit_not_access_or_safety_validation','snapshot':str(path.relative_to(ROOT)),'snapshot_sha256':hashlib.sha256(raw).hexdigest(),'original_source_sha256':g['source_sha256'],'license':g['source_license'],'attribution':g['attribution'],'review_status':g['review_status'],'difficulty_convention':g['difficulty_convention'],'nodes':len(nodes),'edges':len(g['edges']),'edge_kinds':dict(sorted(Counter(e['kind'] for e in g['edges']).items())),'weak_component_sizes':sorted(components,reverse=True),'missing_endpoint_edges':missing,'without_source_refs':sum(not e.get('source_refs') for e in g['edges']),'without_geometry':sum(not e.get('geometry') for e in g['edges']),'duration_basis':dict(sorted(Counter(e.get('duration_basis','unknown') for e in g['edges']).items())),'open_gates':['Direction/access review','Station boarding and transfers','Operator schedules and current closures','Measured timing and field validation'],'automatic_connections_added':0}
if __name__=='__main__':
 report=audit(ROOT/'data/terrain/alpendorf-lab.json');out=ROOT/'research/evidence/alpendorf-snapshot-audit.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
