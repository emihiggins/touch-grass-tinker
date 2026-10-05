"""Find source-node downhill loops without geometric snapping.
Usage: python3 research/scripts/audit_osm_loops.py map.osm
"""
import collections
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

raw=Path(sys.argv[1]).read_bytes();root=ET.fromstring(raw)
ways=[];adj=collections.defaultdict(list)
for w in root.findall('way'):
    tags={x.attrib['k']:x.attrib['v'] for x in w.findall('tag')}
    nodes=[n.attrib['ref'] for n in w.findall('nd')]
    ways.append((w.attrib['id'],tags,nodes))
    if tags.get('piste:type')=='downhill' and tags.get('piste:difficulty') in {'novice','easy'} and tags.get('area')!='yes' and nodes and nodes[0]!=nodes[-1]:
        for a,b in zip(nodes,nodes[1:]):adj[a].append((b,w.attrib['id']))
results=[]
for wid,t,ns in ways:
    if t.get('aerialway') not in {'chair_lift','gondola','platter','t-bar','rope_tow'} or len(ns)<2:continue
    q=collections.deque([(ns[-1],[])]);seen={ns[-1]};found=None
    while q:
        n,path=q.popleft()
        if n==ns[0]:found=path;break
        for nxt,way_id in sorted(adj[n]):
            if nxt not in seen:
                seen.add(nxt);q.append((nxt,path+[{'from':n,'to':nxt,'way_id':way_id}]))
    results.append({'lift_name':t.get('name'),'osm_way_id':wid,'type':t['aerialway'],
                    'bottom_node_id':ns[0],'top_node_id':ns[-1],
                    'exact_node_easy_downhill_return':found is not None,
                    'piste_way_ids':list(dict.fromkeys(e['way_id'] for e in found or [])),
                    'node_pair_count':len(found or [])})
print(json.dumps({'osm_sha256':hashlib.sha256(raw).hexdigest(),
  'method':'Native shared node IDs only; explicit downhill novice/easy ways, excluding areas/closed ways; source order assumed lift-up/piste-down; no transfers, snapping, relation inheritance or operating status.',
  'results':results},indent=2,ensure_ascii=False))
