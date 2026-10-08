import json,unittest
from pathlib import Path
from scripts.build_resort_review import main, excluded_geometry, verify_snapshot
R=Path(__file__).resolve().parents[1]
class T(unittest.TestCase):
 def test_artifact(self):
  main();h=(R/'web/resort-review.html').read_text()
  for x in ('Wachusett Mountain, US','Patscherkofel, AT','Browse-only research preview','Include smaller components'):self.assertIn(x,h)
  self.assertNotIn('fetch(',h);self.assertIn('src="/resort-review.js"',h);self.assertNotIn('<script>const',h)
 def test_data(self):
  main();h=(R/'web/resort-review.html').read_text();d=json.loads(h.split('<script id="data" type="application/json">')[1].split('</script>')[0])
  self.assertEqual(len(d['winter-park']['graph']['edges']),520);self.assertEqual(len(d['breckenridge']['graph']['edges']),1146);self.assertEqual(len(d['wachusett']['graph']['nodes']),506);self.assertEqual(len(d['patscherkofel']['graph']['nodes']),139)
  for x in d.values():self.assertTrue(x['manifest']['fetched_at']);self.assertEqual(x['graph']['review_status'],'unreviewed')

 def test_current_preview_evidence_fingerprints(self):
  import hashlib
  m=json.loads((R/'research/evidence/resort-review/current-media.json').read_text())
  for name,expected in m['sha256'].items():
   self.assertEqual(hashlib.sha256((R/name).read_bytes()).hexdigest(),expected,name)

 def test_exclusion_reasons_and_area_are_source_backed(self):
  main();h=(R/'web/resort-review.html').read_text();d=json.loads(h.split('<script id="data" type="application/json">')[1].split('</script>')[0])
  dog=next(e for e in d['winter-park']['excluded_source'] if e['name']=='Dogpatch')
  self.assertEqual(dog['reason'],'area_or_closed_way');self.assertEqual(dog['classification'],'closed-area')
  self.assertEqual(dog['native_tags']['area'],'yes')
  experts=[e for e in d['breckenridge']['excluded_source'] if e.get('difficulty')=='expert']
  self.assertEqual(len(experts),31)
  self.assertTrue(all(e['status']=='excluded from sanitized graph' for e in experts))
 def test_missing_source_node_is_a_gap_not_a_join(self):
   shape=excluded_geometry(["a","missing","b","c"],{"a":[1.0,2.0],"b":[3.0,4.0],"c":[5.0,6.0]})
   self.assertFalse(shape["geometry_complete"])
   self.assertEqual(shape["geometry_segments"], [[[1.0,2.0]], [[3.0,4.0],[5.0,6.0]]])
   self.assertNotEqual(shape["geometry_segments"][0][-1],shape["geometry_segments"][1][0])

 def test_tampered_snapshot_bytes_fail_closed(self):
   import tempfile, shutil
   with tempfile.TemporaryDirectory() as td:
    folder=Path(td); shutil.copy(R/'data/terrain/winter-park-research/graph.json',folder/'graph.json'); shutil.copy(R/'data/terrain/winter-park-research/source.osm',folder/'source.osm')
    manifest=json.loads((R/'data/terrain/winter-park-research/manifest.json').read_text())
    diagnostics=json.loads((R/'data/terrain/winter-park-research/connectivity-diagnostics.json').read_text())
    (folder/'graph.json').write_bytes((folder/'graph.json').read_bytes()+b'\n tampered')
    with self.assertRaisesRegex(ValueError,'Snapshot bytes'):
     verify_snapshot(folder,manifest,diagnostics)

 def test_source_tamper_without_diagnostics_fails(self):
   import tempfile, shutil
   with tempfile.TemporaryDirectory() as td:
    folder=Path(td)
    source=R/'data/terrain/wachusett-research'
    for name in ('graph.json','source.osm'): shutil.copy(source/name,folder/name)
    manifest=json.loads((source/'manifest.json').read_text())
    verify_snapshot(folder,manifest)
    (folder/'source.osm').write_bytes((folder/'source.osm').read_bytes()+b'\n')
    with self.assertRaisesRegex(ValueError,'Snapshot bytes'):
     verify_snapshot(folder,manifest)

 def test_native_evidence_allowlist_and_unknowns(self):
   import xml.etree.ElementTree as ET
   from scripts.build_resort_review import source_evidence
   root=ET.fromstring('<osm><way id="1" version="2" user="private"><tag k="access" v="no"/><tag k="oneway" v="-1"/><tag k="contact:email" v="private@example.invalid"/></way><way id="2"/></osm>')
   evidence=source_evidence(root)
   self.assertEqual(evidence['way/1'],{'version':'2','tags':{'access':'no','oneway':'-1'}})
   self.assertEqual(evidence['way/2']['tags'],{})
   self.assertNotIn('private',json.dumps(evidence))

 def test_regeneration_preserves_focus_controls(self):
   main()
   html=(R/'web/resort-review.html').read_text()
   self.assertIn('id="focus-selection"',html)
   self.assertIn('id="fit-all"',html)
   main()
   self.assertEqual(html,(R/'web/resort-review.html').read_text())
