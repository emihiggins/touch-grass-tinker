import json,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from liftlap.import_osm import import_osm
from scripts.import_resort_snapshot import sanitize
ROOT=Path(__file__).resolve().parents[1]
class ResortImportTests(unittest.TestCase):
 def test_non_austrian_mapping_is_explicit(self):
  raw=b'<osm><node id="a" lat="0" lon="0"/><node id="b" lat="0.001" lon="0"/><way id="1"><nd ref="a"/><nd ref="b"/><tag k="piste:type" v="downhill"/><tag k="piste:difficulty" v="novice"/></way></osm>'
  with self.assertRaises(ValueError):import_osm(raw,difficulty_convention='FR')
  graph,_=import_osm(raw,graph_id='test-fr',timezone='Europe/Paris',difficulty_convention='FR',difficulty_mapping={'novice':'green'})
  self.assertEqual(graph['edges'][0]['difficulty'],'green');self.assertEqual(graph['edges'][0]['source_difficulty'],'novice')
 def test_sanitization_removes_identity(self):
  raw=b'<osm><node id="a" lat="0" lon="0" user="private" uid="1"><tag k="name" v="private"/></node><way id="1" version="2" user="private"><nd ref="a"/><tag k="aerialway" v="chair_lift"/></way><relation id="3" user="private"/></osm>'
  clean=sanitize(raw);root=ET.fromstring(clean)
  self.assertNotIn(b'private',clean);self.assertFalse(root.findall('relation'));self.assertEqual(root.find('way').get('version'),'2')
 def test_plose_fixture_reproduces(self):
  folder=ROOT/'data/terrain/plose-research';manifest=json.loads((folder/'manifest.json').read_text())
  graph,report=import_osm((folder/'source.osm').read_bytes(),**manifest['import_options'])
  self.assertEqual(graph,json.loads((folder/'graph.json').read_text()));self.assertEqual(report,json.loads((folder/'import-audit.json').read_text()))
 def test_historical_alpendorf_unchanged(self):
  graph,_=import_osm((ROOT/'data/terrain/alpendorf-source.osm').read_bytes());old=json.loads((ROOT/'data/terrain/alpendorf-lab.json').read_text());graph['source_sha256']=old['source_sha256'];self.assertEqual(graph,old)

 def test_connection_evidence_preserved_but_not_routed(self):
  raw=b'<osm><node id="a" lat="0" lon="0"/><node id="b" lat="0.001" lon="0"/><way id="1"><nd ref="a"/><nd ref="b"/><tag k="piste:type" v="connection"/><tag k="piste:difficulty" v="easy"/></way></osm>'
  clean=sanitize(raw);self.assertIn(b'connection',clean);graph,_=import_osm(clean);self.assertEqual(graph['edges'],[])


 def test_unsupported_conditional_access_is_review_excluded_and_preserved(self):
  raw=b'''<osm><node id="a" lat="0" lon="0"/><node id="b" lat="0.001" lon="0"/>
   <way id="1"><nd ref="a"/><nd ref="b"/><tag k="piste:type" v="downhill"/><tag k="piste:difficulty" v="easy"/>
    <tag k="access:conditional" v="no @ (08:00-16:00)"/></way>
   <way id="2"><nd ref="a"/><nd ref="b"/><tag k="aerialway" v="chair_lift"/><tag k="aerialway:access:conditional" v="private @ (Mo-Fr)"/></way></osm>'''
  clean=sanitize(raw);self.assertIn(b'access:conditional',clean);self.assertIn(b'aerialway:access:conditional',clean)
  graph,audit=import_osm(clean)
  self.assertEqual(graph['edges'],[])
  self.assertEqual({x['reason'] for x in audit['skipped_ways']},{'conditional_access_requires_review'})
  self.assertEqual(audit['skipped_ways'][0]['source_restriction_tags']['access:conditional'],'no @ (08:00-16:00)')

 def test_unknown_oneway_is_review_excluded_but_known_values_remain_supported(self):
  raw=b'''<osm><node id="a" lat="0" lon="0"/><node id="b" lat="0.001" lon="0"/>
   <way id="1"><nd ref="a"/><nd ref="b"/><tag k="piste:type" v="downhill"/><tag k="piste:difficulty" v="easy"/><tag k="oneway" v="maybe"/></way>
   <way id="2"><nd ref="a"/><nd ref="b"/><tag k="piste:type" v="downhill"/><tag k="piste:difficulty" v="easy"/><tag k="oneway" v="yes"/></way></osm>'''
  graph,audit=import_osm(raw)
  self.assertEqual(len(graph['edges']),1);self.assertEqual(graph['edges'][0]['source_refs'],['way/2'])
  self.assertEqual(audit['skipped_ways'],[{'way_id':'1','reason':'unknown_oneway_requires_review','source_direction_tags':{'oneway':'maybe'}}])
 def test_expanded_plose_reproduces(self):
  folder=ROOT/'data/terrain/plose-expanded-research';m=json.loads((folder/'manifest.json').read_text());g,a=import_osm((folder/'source.osm').read_bytes(),**m['import_options']);self.assertEqual(g,json.loads((folder/'graph.json').read_text()));self.assertEqual(a,json.loads((folder/'import-audit.json').read_text()))

 def test_new_regional_snapshots_reproduce(self):
  for name in ('wachusett','patscherkofel','winter-park','breckenridge'):
   with self.subTest(resort=name):
    folder=ROOT/'data/terrain'/f'{name}-research';m=json.loads((folder/'manifest.json').read_text())
    g,a=import_osm((folder/'source.osm').read_bytes(),**m['import_options'])
    self.assertEqual(g,json.loads((folder/'graph.json').read_text()))
    self.assertEqual(a,json.loads((folder/'import-audit.json').read_text()))
    self.assertTrue(g['edges']);self.assertTrue(all(e['review_status']=='unreviewed' for e in g['edges']))
    if name=='wachusett':
     self.assertTrue(any(e['difficulty']=='green' for e in g['edges']))
     self.assertFalse(any(e['difficulty']=='red' for e in g['edges']))

 def test_research_catalog_is_current_and_not_live(self):
  from scripts.resort_catalog import build
  catalog=build()
  self.assertEqual(catalog,json.loads((ROOT/'research/evidence/resort-catalog.json').read_text()))
  for row in catalog['snapshots']:
   self.assertFalse(row['app_enabled']);self.assertEqual(row['current_operational_status'],'unknown')

 def test_expert_terrain_is_not_downgraded(self):
  folder=ROOT/'data/terrain/breckenridge-research'
  raw=(folder/'source.osm').read_bytes()
  self.assertIn(b'expert',raw)
  g=json.loads((folder/'graph.json').read_text())
  self.assertFalse(any(e.get('source_difficulty')=='expert' for e in g['edges']))

 def test_invalid_coordinates_rejected_before_geometry(self):
  for lon,lat in [('0','nan'),('inf','0'),('0','-inf'),('181','0'),('0','91'),('-181','0'),('0','-91'),('bad','0')]:
   with self.subTest(lon=lon,lat=lat):
    with self.assertRaises(ValueError):
     import_osm(f'<osm><node id="1" lon="{lon}" lat="{lat}"/></osm>'.encode())
  with self.assertRaisesRegex(ValueError,'numeric'):
   import_osm(b'<osm><node id="1" lat="0"/></osm>')

 def test_duplicate_identities_and_wrong_root_rejected(self):
  for raw in [b'<osm><node id="1" lat="0" lon="0"/><node id="1" lat="1" lon="1"/></osm>',
              b'<osm><way id="1"/><way id="1"/></osm>', b'<osmChange/>', b'<osm><way/></osm>']:
   with self.subTest(raw=raw):
    with self.assertRaises(ValueError):import_osm(raw)

 def test_geographic_boundary_coordinates_are_valid(self):
  from liftlap.import_osm import source_coordinates
  result=source_coordinates(ET.fromstring('<osm><node id="1" lat="90" lon="180"/><node id="2" lat="-90" lon="-180"/></osm>'))
  self.assertEqual(result,{'1':[180,90],'2':[-180,-90]})

 def test_snapshot_cli_rejects_bad_input_without_output(self):
  import hashlib, subprocess, sys, tempfile
  with tempfile.TemporaryDirectory() as td:
   folder=Path(td);source=folder/'source.osm';config=folder/'config.json';out=folder/'out'
   raw=b'<osm><node id="1" lat="nan" lon="0"/></osm>';source.write_bytes(raw)
   config.write_text(json.dumps({'source_url':'https://example.invalid/source','fetched_at':'2026-10-08T00:00:00Z','original_response_sha256':hashlib.sha256(raw).hexdigest(),'import_options':{}}))
   result=subprocess.run([sys.executable,str(ROOT/'scripts/import_resort_snapshot.py'),'--source',str(source),'--config',str(config),'--out',str(out)],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0)
   self.assertIn('finite',result.stderr)
   self.assertFalse(out.exists())
  with self.assertRaisesRegex(ValueError,'snapshot root'):
   sanitize(b'<osmChange/>')
