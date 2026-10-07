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
