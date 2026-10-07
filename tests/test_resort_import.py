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
