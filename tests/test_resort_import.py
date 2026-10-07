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
 def test_expanded_plose_reproduces(self):
  folder=ROOT/'data/terrain/plose-expanded-research';m=json.loads((folder/'manifest.json').read_text());g,a=import_osm((folder/'source.osm').read_bytes(),**m['import_options']);self.assertEqual(g,json.loads((folder/'graph.json').read_text()));self.assertEqual(a,json.loads((folder/'import-audit.json').read_text()))

 def test_new_regional_snapshots_reproduce(self):
  for name in ('wachusett','patscherkofel'):
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
