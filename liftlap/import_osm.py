"""Conservative native-node OSM importer. No snapping, inferred transfers or live status."""
import collections
import hashlib
import math
import xml.etree.ElementTree as ET

LIFT_TYPES={'chair_lift':'chairlift','gondola':'gondola','cable_car':'cable-car','t-bar':'t-bar','platter':'platter','rope_tow':'rope-tow','magic_carpet':'magic-carpet'}
DIFFICULTY={'novice':'blue','easy':'blue','intermediate':'red','advanced':'black'}

def distance(a,b):
    la,lb=math.radians(a[1]),math.radians(b[1]);dl=math.radians(b[0]-a[0]);dp=lb-la
    return 12742000*math.asin(min(1,math.sqrt(math.sin(dp/2)**2+math.cos(la)*math.cos(lb)*math.sin(dl/2)**2)))

def import_osm(raw):
    root=ET.fromstring(raw)
    coords={n.attrib['id']:[float(n.attrib['lon']),float(n.attrib['lat'])] for n in root.findall('node')}
    edges=[];skipped=[]
    for way in root.findall('way'):
        wid=way.attrib['id'];t={x.attrib['k']:x.attrib['v'] for x in way.findall('tag')};ns=[n.attrib['ref'] for n in way.findall('nd')]
        piste=t.get('piste:type')=='downhill';lift=t.get('aerialway') in LIFT_TYPES
        if not piste and not lift:continue
        reason=None
        if t.get('area')=='yes' or len(ns)<2 or ns[0]==ns[-1]:reason='area_or_closed_way'
        elif any(n not in coords for n in ns):reason='missing_node'
        elif any(t.get(k) in {'no','private'} for k in ('access','ski','aerialway:access')):reason='restricted_access'
        elif t.get('oneway')=='-1' or t.get('piste:oneway')=='-1':reason='reversed_direction_requires_review'
        elif piste and t.get('piste:difficulty') not in DIFFICULTY:reason='unknown_difficulty'
        if reason:skipped.append({'way_id':wid,'reason':reason});continue
        # Lift is one terminal-to-terminal edge; preserve whole geometry. Pistes split at every source node.
        chunks=[(0,ns)] if lift else [(i,[a,b]) for i,(a,b) in enumerate(zip(ns,ns[1:]))]
        for index,chunk in chunks:
            geometry=[coords[n] for n in chunk];length=sum(distance(a,b) for a,b in zip(geometry,geometry[1:]))
            if length<=0:continue
            duration=max(1,length/(3 if lift else 4))
            edges.append({'id':f'osm:way:{wid}:{index}','from':chunk[0],'to':chunk[-1],'kind':'lift' if lift else 'piste',
              'name':t.get('name',f'OSM way {wid}'),'difficulty':DIFFICULTY.get(t.get('piste:difficulty')) if piste else None,
              'lift_type':LIFT_TYPES[t['aerialway']] if lift else None,'geometry':geometry,'length_m':round(length,3),'duration_s':round(duration,3),
              'duration_basis':'assumed','review_status':'unreviewed','source_refs':[f'way/{wid}'],
              'source_version':way.attrib.get('version'),'source_difficulty':t.get('piste:difficulty')})
    # Overlapping ways with contradictory normalized grades are not a blue shortcut.
    signatures=collections.defaultdict(set)
    for e in edges:
        if e['kind']=='piste':
            signature=tuple(sorted(tuple(c) for c in e['geometry']))
            signatures[signature].add(e['difficulty'])
    ambiguous={k for k,v in signatures.items() if len(v)>1}
    retained=[]
    for e in edges:
        if e['kind']=='piste' and tuple(sorted(tuple(c) for c in e['geometry'])) in ambiguous:
            skipped.append({'edge_id':e['id'],'reason':'conflicting_overlap_difficulty'})
        else:retained.append(e)
    edges=retained
    used={e[k] for e in edges for k in ('from','to')}
    graph={'schema_version':1,'id':'alpendorf-osm-lab','timezone':'Europe/Vienna','difficulty_convention':'AT','review_status':'unreviewed',
      'source_sha256':hashlib.sha256(raw).hexdigest(),'attribution':'© OpenStreetMap contributors; ODbL 1.0',
      'source_license':'https://www.openstreetmap.org/copyright','nodes':[{'id':n,'lon':coords[n][0],'lat':coords[n][1]} for n in sorted(used)],
      'edges':sorted(edges,key=lambda e:e['id'])}
    return graph,{'skipped_ways':skipped,'node_count':len(graph['nodes']),'edge_count':len(edges),
      'assumptions':['Way order used as directed travel; lift terminals unreviewed.','Durations assume lift 3m/s, piste 4m/s, minimum 1s; no measured timing.','All edges unreviewed; no operational route approval.','Relations and permission/time restrictions are not fully interpreted.']}
