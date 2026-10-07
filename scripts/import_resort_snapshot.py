"""Offline bounded OSM preparation. No downloads, snapping or routing approval."""
import argparse,hashlib,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from liftlap.import_osm import import_osm

def sanitize(raw):
 source=ET.fromstring(raw);root=ET.Element('osm',{'version':'0.6','generator':'LiftLap sanitized research snapshot'})
 for n in source.findall('node'):
  ET.SubElement(root,'node',{k:n.attrib[k] for k in ('id','lat','lon')})
 for way in source.findall('way'):
  tags={t.attrib['k']:t.attrib['v'] for t in way.findall('tag')}
  if 'piste:type' not in tags and 'aerialway' not in tags:continue
  w=ET.SubElement(root,'way',{k:way.attrib[k] for k in ('id','version') if k in way.attrib})
  for child in way:
   if child.tag in {'nd','tag'}:ET.SubElement(w,child.tag,dict(sorted(child.attrib.items())))
 return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 raw=a.source.read_bytes()
 if len(raw)>4_000_000:raise ValueError('Research sample limit is 4MB')
 config=json.loads(a.config.read_text())
 if not config.get('source_url','').startswith('https://') or not config.get('fetched_at'):raise ValueError('HTTPS source URL and retrieval time required')
 if config.get('original_response_sha256')!=hashlib.sha256(raw).hexdigest():raise ValueError('Original response hash does not match input bytes')
 clean=sanitize(raw)
 graph,report=import_osm(clean,**config['import_options'])
 # No overwrite: preserve old snapshots and their evidence.
 a.out.mkdir(parents=True,exist_ok=False)
 (a.out/'source.osm').write_bytes(clean)
 (a.out/'graph.json').write_text(json.dumps(graph,indent=2)+'\n')
 (a.out/'import-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 manifest={**config,'input_sha256':hashlib.sha256(raw).hexdigest(),'sanitized_sha256':hashlib.sha256(clean).hexdigest(),'graph_sha256':hashlib.sha256((a.out/'graph.json').read_bytes()).hexdigest(),'attribution':'© OpenStreetMap contributors; ODbL 1.0','license':'https://www.openstreetmap.org/copyright','sanitization':'Contributor identity/history and relations omitted; only nodes and all piste/aerialway ways retained; unsupported piste types remain non-routable source evidence. Not original response bytes.','review_status':'unreviewed','source_hash_semantics':'Graph source_sha256 identifies sanitized importer input; original response hash is separate.'}
 (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'nodes':len(graph['nodes']),'edges':len(graph['edges']),'review_status':'unreviewed'}))
if __name__=='__main__':main()
