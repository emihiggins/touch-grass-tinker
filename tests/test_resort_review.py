import json,unittest
from pathlib import Path
from scripts.build_resort_review import main
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
