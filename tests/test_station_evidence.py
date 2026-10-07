import copy,hashlib,unittest
from scripts.station_evidence import build
class StationEvidenceTests(unittest.TestCase):
 def setUp(self):
  self.raw=b'<osm><node id="1" lat="1" lon="2" user="private-person"><tag k="aerialway" v="station"/><tag k="email" v="private-email"/></node><relation id="9" user="private-person"><member type="node" ref="1" role="stop"/><member type="node" ref="3" role="other"/><tag k="type" v="site"/></relation></osm>'
  self.m={'original_response_sha256':hashlib.sha256(self.raw).hexdigest(),'graph_sha256':'g','sanitized_sha256':'s','source_url':'https://example.com','fetched_at':'2026-10-07','attribution':'OSM','license':'ODbL'}
  self.d={'graph_sha256':'g','source_sha256':'s','lifts':[{'source_ref':'way/5','endpoint_incidence':[{'source_node':'1'},{'source_node':'2'}]}]}
 def test_scoped_identity_free_evidence(self):
  d=copy.deepcopy(self.d);r=build(self.raw,self.m,self.d)
  self.assertEqual(self.d,d);self.assertFalse(r['routing_enabled']);self.assertNotIn('private',str(r))
  self.assertEqual(r['endpoints'][0]['coordinate'],[2,1]);self.assertEqual(r['endpoints'][0]['tags'],{'aerialway':'station'})
  self.assertIsNone(r['endpoints'][1]['coordinate']);self.assertFalse(r['endpoints'][1]['present_in_raw_snapshot'])
  self.assertEqual(len(r['matching_relations'][0]['matching_members']),1);self.assertFalse(r['matching_relations'][0]['complete_membership'])
 def test_reject_changed_source_or_diagnostic(self):
  with self.assertRaises(ValueError):build(self.raw+b' ',self.m,self.d)
  self.d['graph_sha256']='changed'
  with self.assertRaises(ValueError):build(self.raw,self.m,self.d)
