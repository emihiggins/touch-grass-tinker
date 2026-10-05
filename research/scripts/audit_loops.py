"""Compare three candidate loops with a separately fetched OSM extract.
No inference of current opening, safe access or field validation.
Usage: python3 research/scripts/audit_loops.py terrain.json map.osm
"""
import collections
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

terrain_raw = Path(sys.argv[1]).read_bytes()
osm_raw = Path(sys.argv[2]).read_bytes()
data = json.loads(terrain_raw)
root = ET.fromstring(osm_raw)
osm_nodes = {n.attrib['id']: (float(n.attrib['lon']), float(n.attrib['lat'])) for n in root.findall('node')}

def key(c):
    return tuple(round(v, 7) for v in c[:2])

def meters(a, b):
    lat1,lat2 = math.radians(a[1]),math.radians(b[1])
    dl = math.radians(b[0]-a[0]); dp=lat2-lat1
    return 6371000*2*math.asin(min(1,math.sqrt(math.sin(dp/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dl/2)**2)))

osm_ways = []
segments = collections.defaultdict(list)
for w in root.findall('way'):
    tags = {t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
    refs = [n.attrib['ref'] for n in w.findall('nd')]
    if not ('piste:type' in tags or tags.get('aerialway') in {'chair_lift','gondola','platter','t-bar','rope_tow'}):
        continue
    coords = [osm_nodes[n] for n in refs if n in osm_nodes]
    item={'id':w.attrib['id'],'version':w.attrib.get('version'),'tags':tags,'coords':coords}
    osm_ways.append(item)
    for a,b in zip(coords,coords[1:]):
        segments[(key(a),key(b))].append((item,True))
        segments[(key(b),key(a))].append((item,False))

def source_check(edge):
    coords=edge['geometry']['coordinates']; matches={}; covered=0; total=0
    for a,b in zip(coords,coords[1:]):
        if key(a)==key(b):continue
        total+=1
        found=segments.get((key(a),key(b)),[])
        if found:covered+=1
        for w,forward in found:
            matches[w['id']]={'osm_way_id':w['id'],'version':w['version'],'name':w['tags'].get('name'),
              'piste_type':w['tags'].get('piste:type'),'difficulty':w['tags'].get('piste:difficulty'),
              'aerialway':w['tags'].get('aerialway'),'ref':w['tags'].get('ref')}
    return {'exact_coordinate_segments':covered,'total_coordinate_segments':total,'source_ways':sorted(matches.values(),key=lambda w:w['osm_way_id'])}

adj=collections.defaultdict(list)
for t in data['trails']:
    if t['difficulty']=='blue':adj[t['fromNodeId']].append(t)
loops=[]
for lift in data['lifts']:
    if lift['name'].get('en') not in {'Hirschkogelbahn','Straßalmbahn','Obergassalmbahn'}:continue
    start,goal=lift['stationNodeIds'][-1],lift['stationNodeIds'][0]
    q=collections.deque([(start,[])]);seen={start};path=None
    while q:
        node,route=q.popleft()
        if node==goal:path=route;break
        for e in sorted(adj[node],key=lambda e:e['id']):
            if e['toNodeId'] not in seen:seen.add(e['toNodeId']);q.append((e['toNodeId'],route+[e]))
    if path is None:raise ValueError('No candidate return path')
    chain=[lift]+path
    gaps=[meters(a['geometry']['coordinates'][-1],b['geometry']['coordinates'][0]) for a,b in zip(chain,chain[1:]+chain[:1])]
    loops.append({'lift':lift['name']['en'],'lift_id':lift['id'],'lift_source_check':source_check(lift),
      'piste_segments':[{'id':e['id'],'name':e['name']['en'],'difficulty':e['difficulty'],'ref':e['ref'],'source_check':source_check(e)} for e in path],
      'piste_distance_m':sum(e['lengthM'] for e in path),'junction_gaps_m':[round(v,2) for v in gaps],
      'max_junction_gap_m':round(max(gaps),2),'review_status':'candidate_not_terrain_verified'})
print(json.dumps({'terrain_sha256':hashlib.sha256(terrain_raw).hexdigest(),'osm_extract_sha256':hashlib.sha256(osm_raw).hexdigest(),
 'osm_bounds':root.find('bounds').attrib if root.find('bounds') is not None else None,
 'method':'7-decimal XY coordinate-pair matching; reversed pairs count as geometry corroboration only. No topology fixes or status inference.',
 'loops':loops},indent=2,ensure_ascii=False))
