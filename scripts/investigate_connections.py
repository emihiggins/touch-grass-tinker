"""Counterfactual connectivity only. Does not modify or approve routing graphs."""
import copy,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.audit_resort_snapshot import directed_audit

def investigate(folder):
 g=json.loads((folder/'graph.json').read_text());root=ET.parse(folder/'source.osm').getroot();connections=[]
 for w in root.findall('way'):
  tags={t.get('k'):t.get('v') for t in w.findall('tag')}
  if tags.get('piste:type')=='connection':connections.append({'source_ref':'way/'+w.get('id'),'nodes':[n.get('ref') for n in w.findall('nd')],'tags':tags})
 trial=copy.deepcopy(g);nodes={n.get('id'):{'id':n.get('id'),'lon':float(n.get('lon')),'lat':float(n.get('lat'))} for n in root.findall('node')};known={n['id'] for n in trial['nodes']}
 for c in connections:
  for n in c['nodes']:
   if n not in known:trial['nodes'].append(nodes[n]);known.add(n)
  for a,b in zip(c['nodes'],c['nodes'][1:]):trial['edges'].append({'from':a,'to':b})
 return {'scope':'counterfactual_topology_only_not_route_approval','connections_not_imported':connections,'imported_nodes_on_cycles':directed_audit(g)['nodes_on_directed_cycles'],'if_source_connection_way_order_were_allowed_nodes_on_cycles':directed_audit(trial)['nodes_on_directed_cycles'],'assumption':'Hypothetical directed transfer along source way order, with no permission, schedule, timing or safety verification. No connections added to saved graph.','source_tags_reference':'https://wiki.openstreetmap.org/wiki/Key:piste:type'}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);a=p.parse_args();r=investigate(a.folder);(a.folder/'connectivity-investigation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='connections_not_imported'}))
