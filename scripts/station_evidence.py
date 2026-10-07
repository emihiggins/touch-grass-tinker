"""Recover review-only station evidence from a hash-matched raw snapshot."""
import argparse,hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
SAFE_TAGS={'aerialway','aerialway:access','name','ele','access','ski','opening_hours','wheelchair','public_transport','type','route','site'}

def build(raw,manifest,diagnostics):
 if len(raw)>4_000_000:raise ValueError('Raw research limit exceeded')
 if hashlib.sha256(raw).hexdigest()!=manifest['original_response_sha256']:raise ValueError('Raw source hash mismatch')
 if diagnostics['graph_sha256']!=manifest['graph_sha256'] or diagnostics['source_sha256']!=manifest['sanitized_sha256']:raise ValueError('Diagnostic snapshot mismatch')
 root=ET.fromstring(raw);nodes={n.get('id'):n for n in root.findall('node')};endpoints=[]
 lift_ids={l['source_ref'].split('/')[1] for l in diagnostics['lifts']}
 def tags(e):return {t.get('k'):t.get('v') for t in e.findall('tag') if t.get('k') in SAFE_TAGS}
 for lift in diagnostics['lifts']:
  for endpoint in lift['endpoint_incidence']:
   node=nodes.get(endpoint['source_node'])
   endpoints.append({'lift_source_ref':lift['source_ref'],'source_node':endpoint['source_node'],
     'coordinate':[float(node.get('lon')),float(node.get('lat'))] if node is not None else None,
     'tags':tags(node) if node is not None else {},'present_in_raw_snapshot':node is not None})
 node_ids={e['source_node'] for e in endpoints};relations=[]
 for r in root.findall('relation'):
  matching=[{k:m.get(k) for k in ('type','ref','role')} for m in r.findall('member') if (m.get('type')=='way' and m.get('ref') in lift_ids) or (m.get('type')=='node' and m.get('ref') in node_ids)]
  if matching:relations.append({'source_ref':'relation/'+r.get('id'),'tags':tags(r),'matching_members':matching,'complete_membership':False})
 return {'schema':1,'scope':'station_review_evidence_not_routing','raw_source_sha256':manifest['original_response_sha256'],'graph_sha256':manifest['graph_sha256'],'source_url':manifest['source_url'],'fetched_at':manifest['fetched_at'],'attribution':manifest['attribution'],'license':manifest['license'],'endpoints':endpoints,'matching_relations':relations,'routing_enabled':False,'limitations':['Only allowlisted tags and directly matching relation members retained; contributor identity removed.','No matching relation in this bounded response does not mean none exists upstream.','Station tags do not establish boarding direction, permitted access or operational status.']}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--raw',type=Path,required=True);a=p.parse_args()
 d=build(a.raw.read_bytes(),json.loads((a.folder/'manifest.json').read_text()),json.loads((a.folder/'connectivity-diagnostics.json').read_text()))
 target=a.folder/'station-evidence.json'
 if target.exists():raise ValueError('Refusing to overwrite prior evidence')
 target.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'endpoints':len(d['endpoints']),'station_tags':sum(e['tags'].get('aerialway')=='station' for e in d['endpoints']),'matching_relations':len(d['matching_relations'])}))
