"""Conservative native-node OSM importer. No snapping, inferred transfers or live status."""
import collections
import hashlib
import math
import xml.etree.ElementTree as ET

LIFT_TYPES={'chair_lift':'chairlift','gondola':'gondola','cable_car':'cable-car','t-bar':'t-bar','platter':'platter','rope_tow':'rope-tow','magic_carpet':'magic-carpet'}
DIFFICULTY={'novice':'blue','easy':'blue','intermediate':'red','advanced':'black'}
SUPPORTED_ONEWAY={'yes','no','1','0','true','false','-1'}
CONDITIONAL_RESTRICTION_KEYS=('access:conditional','ski:conditional','aerialway:access:conditional')

def restriction_tags(tags):
    """Return source restriction tags that the importer deliberately does not evaluate."""
    return {k:tags[k] for k in (*CONDITIONAL_RESTRICTION_KEYS,'access','ski','aerialway:access')
            if k in tags and (k in CONDITIONAL_RESTRICTION_KEYS or tags[k].lower()=='conditional')}

def source_coordinates(root):
    """Reject ambiguous identities and invalid geometry before any graph is built."""
    if root.tag != 'osm':
        raise ValueError('Expected an OSM snapshot root')
    coords = {}
    for node in root.findall('node'):
        ident = node.get('id')
        if not ident or ident in coords:
            raise ValueError('Missing or duplicate OSM node ID')
        try:
            lon, lat = float(node.attrib['lon']), float(node.attrib['lat'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('OSM node requires numeric longitude and latitude') from exc
        if not math.isfinite(lon) or not math.isfinite(lat) or not -180 <= lon <= 180 or not -90 <= lat <= 90:
            raise ValueError('OSM coordinates must be finite and within geographic bounds')
        coords[ident] = [lon, lat]
    way_ids = set()
    for way in root.findall('way'):
        ident = way.get('id')
        if not ident or ident in way_ids:
            raise ValueError('Missing or duplicate OSM way ID')
        way_ids.add(ident)
    return coords

def distance(a,b):
    la,lb=math.radians(a[1]),math.radians(b[1]);dl=math.radians(b[0]-a[0]);dp=lb-la
    return 12742000*math.asin(min(1,math.sqrt(math.sin(dp/2)**2+math.cos(la)*math.cos(lb)*math.sin(dl/2)**2)))

def import_osm(raw, *, graph_id='alpendorf-osm-lab', timezone='Europe/Vienna', difficulty_convention='AT', difficulty_mapping=None):
    # Existing default is the historical Austrian lab. Other regions must opt in.
    from zoneinfo import ZoneInfo
    ZoneInfo(timezone)
    if not graph_id or not difficulty_convention:raise ValueError('Explicit graph identity and difficulty convention required')
    if difficulty_mapping is None:
        if difficulty_convention!='AT':raise ValueError('Non-AT imports require an explicit difficulty mapping')
        difficulty_mapping=DIFFICULTY
    if not difficulty_mapping or any(v not in {'green','blue','red','black'} for v in difficulty_mapping.values()):
        raise ValueError('Unsupported normalized difficulty mapping')
    root=ET.fromstring(raw)
    coords=source_coordinates(root)
    edges=[];skipped=[]
    for way in root.findall('way'):
        wid=way.attrib['id'];t={x.attrib['k']:x.attrib['v'] for x in way.findall('tag')};ns=[n.attrib['ref'] for n in way.findall('nd')]
        piste=t.get('piste:type')=='downhill';lift=t.get('aerialway') in LIFT_TYPES
        if not piste and not lift:continue
        reason=None
        if t.get('area')=='yes' or len(ns)<2 or ns[0]==ns[-1]:reason='area_or_closed_way'
        elif any(n not in coords for n in ns):reason='missing_node'
        elif restriction_tags(t):reason='conditional_access_requires_review'
        elif any(t.get(k) in {'no','private'} for k in ('access','ski','aerialway:access')):reason='restricted_access'
        elif any(k in t and t[k].lower() not in SUPPORTED_ONEWAY for k in ('oneway','piste:oneway')):reason='unknown_oneway_requires_review'
        elif t.get('oneway')=='-1' or t.get('piste:oneway')=='-1':reason='reversed_direction_requires_review'
        elif piste and t.get('piste:difficulty') not in difficulty_mapping:reason='unknown_difficulty'
        if reason:
            item={'way_id':wid,'reason':reason}
            source_restrictions=restriction_tags(t)
            source_directions={k:t[k] for k in ('oneway','piste:oneway') if k in t}
            if source_restrictions: item['source_restriction_tags']=source_restrictions
            if reason=='unknown_oneway_requires_review': item['source_direction_tags']=source_directions
            skipped.append(item);continue
        # Lift is one terminal-to-terminal edge; preserve whole geometry. Pistes split at every source node.
        chunks=[(0,ns)] if lift else [(i,[a,b]) for i,(a,b) in enumerate(zip(ns,ns[1:]))]
        for index,chunk in chunks:
            geometry=[coords[n] for n in chunk];length=sum(distance(a,b) for a,b in zip(geometry,geometry[1:]))
            if length<=0:continue
            duration=max(1,length/(3 if lift else 4))
            edges.append({'id':f'osm:way:{wid}:{index}','from':chunk[0],'to':chunk[-1],'kind':'lift' if lift else 'piste',
              'name':t.get('name',f'OSM way {wid}'),'difficulty':difficulty_mapping.get(t.get('piste:difficulty')) if piste else None,
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
    graph={'schema_version':1,'id':graph_id,'timezone':timezone,'difficulty_convention':difficulty_convention,'review_status':'unreviewed',
      'source_sha256':hashlib.sha256(raw).hexdigest(),'attribution':'© OpenStreetMap contributors; ODbL 1.0',
      'source_license':'https://www.openstreetmap.org/copyright','nodes':[{'id':n,'lon':coords[n][0],'lat':coords[n][1]} for n in sorted(used)],
      'edges':sorted(edges,key=lambda e:e['id'])}
    return graph,{'skipped_ways':skipped,'node_count':len(graph['nodes']),'edge_count':len(edges),
      'assumptions':['Way order used as directed travel; lift terminals unreviewed.','Durations assume lift 3m/s, piste 4m/s, minimum 1s; no measured timing.','All edges unreviewed; no operational route approval.','Relations and permission/time restrictions are not fully interpreted.']}
