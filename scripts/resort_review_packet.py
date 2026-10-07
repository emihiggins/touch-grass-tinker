"""Generate read-only source-way review packets; never confer approval."""
import argparse,csv,hashlib,json,xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def spreadsheet_safe(value):
 text=str(value)
 return "'"+text if text.lstrip().startswith(('=','+','-','@')) or text.startswith(('\t','\r','\n')) else text

def build(graph_path,source_path):
 graph_raw=graph_path.read_bytes();source_raw=source_path.read_bytes();graph=json.loads(graph_raw)
 ways={w.attrib['id']:{t.attrib['k']:t.attrib['v'] for t in w.findall('tag')} for w in ET.fromstring(source_raw).findall('way')}
 groups=defaultdict(list)
 for edge in graph['edges']:
  for ref in edge.get('source_refs',[]):groups[ref].append(edge)
 rows=[]
 for ref,edges in sorted(groups.items()):
  tags=ways.get(ref.removeprefix('way/'),{})
  restrictions={k:v for k,v in tags.items() if any(word in k for word in ('access','oneway','opening','season','duration','ski'))}
  rows.append({'source_ref':ref,'source_url':'https://www.openstreetmap.org/'+ref,'name':edges[0]['name'],'kind':edges[0]['kind'],'edge_count':len(edges),'native_grade':tags.get('piste:difficulty','unknown'),'normalized_grades':','.join(sorted({e['difficulty'] for e in edges if e.get('difficulty')})),'source_restrictions':json.dumps(restrictions,sort_keys=True),'review_status':'pending','review_questions':'Confirm direction, grade, access, boarding/transfers and coverage; supply dated operating-source evidence.','reviewer_notes':''})
 return rows,{'graph_sha256':hashlib.sha256(graph_raw).hexdigest(),'source_sha256':hashlib.sha256(source_raw).hexdigest(),'ways':len(rows),'edges':len(graph['edges']),'review_status':'unreviewed','warning':'Blank restrictions mean missing source tags, not unrestricted access. CSV is a review aid, not an approval ledger.'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--graph',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();rows,manifest=build(a.graph,a.source)
 a.out.mkdir(parents=True,exist_ok=False)
 if rows:
  with (a.out/'ways.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows({k:spreadsheet_safe(v) for k,v in row.items()} for row in rows)
 (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
