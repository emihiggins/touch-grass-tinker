"""Generate reproducible research inventory; never enables a resort in the app."""
import collections,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.audit_resort_snapshot import audit

def entry(folder):
 manifest=json.loads((folder/'manifest.json').read_text())
 graph=json.loads((folder/'graph.json').read_text())
 imported=json.loads((folder/'import-audit.json').read_text())
 report=audit(folder/'graph.json')
 ways=ET.fromstring((folder/'source.osm').read_bytes()).findall('way')
 tags=[{t.attrib['k']:t.attrib['v'] for t in w.findall('tag')} for w in ways]
 return {'id':graph['id'],'directory':folder.relative_to(ROOT).as_posix(),
         'source_url':manifest['source_url'],'fetched_at':manifest['fetched_at'],
         'graph_sha256':manifest['graph_sha256'],'license':manifest['license'],
         'region':graph['difficulty_convention'],'timezone':graph['timezone'],
         'nodes':report['nodes'],'edges':report['edges'],'edge_kinds':report['edge_kinds'],
         'weak_components':len(report['weak_component_sizes']),
         'nodes_on_directed_cycles':report['directed_connectivity']['nodes_on_directed_cycles'],
         'source_ways':len(ways),
         'native_piste_grades':dict(sorted(collections.Counter(t.get('piste:difficulty','unknown') for t in tags if t.get('piste:type')=='downhill').items())),
         'ways_with_opening_hours':sum('opening_hours' in t for t in tags),
         'duration_basis':report['duration_basis'],
         'review_status':'unreviewed','current_operational_status':'unknown','app_enabled':False,
         'next_gate':'Review real junctions, lift boarding and direction; obtain operator access/status evidence. A cycle count is not route approval.'}

def build():
 return {'schema_version':1,'scope':'bounded_research_snapshots_not_complete_resort_inventory',
         'attribution':'© OpenStreetMap contributors; ODbL 1.0. Application code is separately MIT.',
         'snapshots':[entry(p.parent) for p in sorted((ROOT/'data/terrain').glob('*/manifest.json'))]}

if __name__=='__main__':
 target=ROOT/'research/evidence/resort-catalog.json'
 target.write_text(json.dumps(build(),indent=2)+'\n')
 print('Updated research resort catalog')
