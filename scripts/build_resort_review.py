import json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1]
REVIEW_TAGS = {"name", "piste:type", "piste:difficulty", "aerialway", "oneway", "piste:oneway", "aerialway:access", "access", "ski", "foot", "access:conditional", "ski:conditional", "opening_hours", "seasonal", "aerialway:duration"}

def source_evidence(root):
 return {f"way/{way.get('id')}": {"version":way.get('version'), "tags":{t.get('k'):t.get('v') for t in way.findall('tag') if t.get('k') in REVIEW_TAGS}} for way in root.findall('way')}

def digest(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def geometry_segments(nodes, coords):
 """Return contiguous known-node runs; never draw across an omitted node."""
 segments=[];current=[]
 for node in nodes:
  point=coords.get(node)
  if point is None:
   if current:segments.append(current);current=[]
  else:current.append(point)
 if current:segments.append(current)
 return segments

def verify_snapshot(folder, manifest, diagnostics=None):
 actual_graph=digest(folder/"graph.json");actual_source=digest(folder/"source.osm")
 if manifest["graph_sha256"]!=actual_graph or manifest["sanitized_sha256"]!=actual_source:
  raise ValueError("Snapshot bytes do not match manifest")
 if diagnostics is not None and (diagnostics["graph_sha256"]!=actual_graph or diagnostics["source_sha256"]!=actual_source):
  raise ValueError("Stale diagnostics")
 return actual_graph,actual_source

def excluded_geometry(nodes, coords):
 segments=geometry_segments(nodes,coords)
 result={"geometry":[point for segment in segments for point in segment],"geometry_complete":all(node in coords for node in nodes)}
 if not result["geometry_complete"]:result["geometry_segments"]=segments
 return result
S={"winter-park":("Winter Park, Colorado, US (partial)","winter-park-research"),"breckenridge":("Breckenridge, Colorado, US (partial)","breckenridge-research"),"wachusett":("Wachusett Mountain, US","wachusett-research"),"patscherkofel":("Patscherkofel, AT","patscherkofel-research")}
T="""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Lift-Lap resort review</title><style>body{font:16px system-ui;max-width:1200px;margin:auto;padding:20px;background:#f7faf4;color:#183b3a}.warn{border-left:5px solid #b54112;padding:12px;background:#fff6ed}.grid{display:grid;grid-template-columns:280px 1fr;gap:20px}.box{background:white;border:1px solid #cbdad0;padding:16px;border-radius:8px}.map{width:100%;min-width:0;aspect-ratio:900/560;height:auto}.wrap{overflow:auto;border:1px solid #cbdad0}.e{fill:none;stroke-width:2;cursor:pointer;vector-effect:non-scaling-stroke}.lift{stroke:#203f3f;stroke-dasharray:7 5}.piste{stroke:#326f9c}.selected{stroke:#b54112!important;stroke-width:6}.dis{opacity:.25}.excluded{fill:none;stroke:#9a5b19;stroke-width:2;stroke-dasharray:3 4;opacity:.82}.excluded.closed-area{fill:#f3d9b2;fill-opacity:.22}.excluded.selected{stroke:#b54112;stroke-width:6;opacity:1}.audit{margin-top:16px;border-top:1px solid #cbdad0;padding-top:12px}.audit-list{max-height:270px;overflow:auto;padding-left:20px}.audit-list button{max-width:100%;overflow-wrap:anywhere;font:inherit;text-align:left;background:none;border:0;color:#94330e;text-decoration:underline;cursor:pointer;padding:6px 0}.audit-list button:focus{outline:3px solid #b54112;outline-offset:2px}.muted{color:#55706b}.pill{display:inline-block;background:#e8f1eb;border-radius:9px;padding:4px;margin:3px}dt{font-weight:bold;margin-top:8px}dd{margin:0;color:#55706b;overflow-wrap:anywhere}a{color:#94330e}select{max-width:100%}label[for="lift-review"]{display:block;margin-bottom:6px}*{box-sizing:border-box}.box{min-width:0}p{overflow-wrap:anywhere}.endpoint{fill:#fff;stroke:#94330e;stroke-width:3}.endpoint-label{fill:#183b3a;font:bold 14px system-ui}.e:focus{stroke:#b54112;stroke-width:6;outline:none}@media(max-width:750px){.grid{grid-template-columns:1fr}}</style><main><h1>Resort data review</h1><p class="warn"><b>Browse-only research preview.</b> Unreviewed geometry; not a route selector. No routing, access, direction, operating, timing, safety, or coverage claims. Do not use for navigation.</p><div class="grid"><aside class="box"><label for="s">Research sample</label><select id="s"></select><p><label><input id="l" type="checkbox" checked> Lifts</label><br><label><input id="p" type="checkbox" checked> Pistes</label><br><label><input id="d" type="checkbox" checked> Include smaller components</label><br><label><input id="x" type="checkbox" checked> Excluded source geometry</label></p><p id="cov"></p><label for="lift-review">Lift endpoint review</label><select id="lift-review"></select><p id="lift-summary"></p></aside><section class="box"><h2>Source geometry</h2><p>Solid lines: pistes (color is not difficulty). Dashed: lifts. Pale: smaller disconnected components. Select a segment for native grade and source.</p><div id="sum"></div><div class="wrap"><svg id="map" class="map" viewBox="0 0 900 560" role="group" aria-label="Unreviewed resort geometry"></svg></div><p id="status" role="status" aria-live="polite">Select a segment.</p><div id="detail" tabindex="-1"></div><section id="lift-detail" aria-label="Source lift endpoint evidence"></section><section class="audit" aria-labelledby="excluded-heading"><h3 id="excluded-heading">Excluded source geometry</h3><p class="muted">Browse-only source evidence. These shapes are excluded from the sanitized routing graph; their native grade and reason are not routing decisions.</p><ol id="excluded-list" class="audit-list"></ol></section></section></div><section class="box"><h2>Source and review limits</h2><p id="src"></p><p>Native grade is the original OSM tag, not a cross-resort guarantee. Disconnected is structural, not evidence of a connector. Source links are explicit user actions. © OpenStreetMap contributors; ODbL 1.0. No external requests occur until you choose a source link.</p></section></main><script id="data" type="application/json">__DATA__</script><script src="/resort-review.js" defer></script>"""
def main():
 d={}
 for k,(label,n) in S.items():
  x=R/"data/terrain"/n;d[k]={"label":label,"graph":json.loads((x/"graph.json").read_text()),"manifest":json.loads((x/"manifest.json").read_text())}
  verify_snapshot(x,d[k]["manifest"])
  d[k]["source_evidence"]=source_evidence(ET.parse(x/"source.osm").getroot())
  if (x/"connectivity-diagnostics.json").exists():
   diag=json.loads((x/"connectivity-diagnostics.json").read_text());m=d[k]['manifest']
   actual_graph,actual_source=verify_snapshot(x,m,diag)
   root=ET.fromstring((x/'source.osm').read_bytes());coords={v.get('id'):[float(v.get('lon')),float(v.get('lat'))] for v in root.findall('node')}
   supplement=json.loads((x/'station-evidence.json').read_text()) if (x/'station-evidence.json').exists() else None
   if supplement and (supplement['graph_sha256']!=actual_graph or supplement['raw_source_sha256']!=m['original_response_sha256']):raise ValueError('Stale station evidence')
   ways={w.get('id'): w for w in root.findall('way')}
   reasons={v['way_id']:v['reason'] for v in json.loads((x/'import-audit.json').read_text()).get('skipped_ways',[]) if 'way_id' in v}
   excluded=[]
   for item in diag.get('excluded_source_ways', []):
    ref=item['source_ref'].split('/',1)[-1]
    way=ways.get(ref)
    if way is None: continue
    nodes=item.get('nodes',[])
    closed=len(nodes)>2 and nodes[0]==nodes[-1]
    tags={t.get('k'):t.get('v') for t in way.findall('tag')}
    shape=excluded_geometry(nodes,coords)
    excluded.append({**item,'reason':reasons.get(ref,item.get('reason')),'classification':'nonpassenger-infrastructure' if item.get('aerialway') else ('closed-area' if closed and tags.get('area')=='yes' and shape['geometry_complete'] else 'source-line'),'native_tags':tags,'status':'excluded from sanitized graph',**shape})
   for item in diag.get('excluded_non_passenger_aerialways', []):
    ref=item['source_ref'].split('/',1)[-1]
    way=ways.get(ref)
    if way is None or any(x['source_ref']==item['source_ref'] for x in excluded): continue
    nodes=[n.get('ref') for n in way.findall('nd')]
    tags={t.get('k'):t.get('v') for t in way.findall('tag')}
    shape=excluded_geometry(nodes,coords)
    excluded.append({**item,'name':tags.get('name') or item['source_ref'],'nodes':nodes,'classification':'nonpassenger-infrastructure','reason':'non-passenger infrastructure excluded from routing','native_tags':tags,'status':'excluded from sanitized graph',**shape})
   d[k]['excluded_source']=excluded
   for lift in diag['lifts']:
    for e in lift['endpoint_incidence']:
     e['coordinate']=coords.get(e['source_node'])
     matches=[v for v in supplement['endpoints'] if v['source_node']==e['source_node'] and v['lift_source_ref']==lift['source_ref']] if supplement else []
     e['station_tags']=matches[0]['tags'] if matches else None
   d[k]['diagnostics']=diag
 (R/"web/resort-review.html").write_text(T.replace("__DATA__",json.dumps(d,separators=(",",":")).replace("<","\\u003c")))
if __name__=="__main__":main()
