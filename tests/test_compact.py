import copy,unittest
from liftlap import fixtures as f
from liftlap.core import plan,validate_route,digest
from liftlap.compact import compact,expand_route
class CompactTests(unittest.TestCase):
 def setUp(self):
  self.g=f.graph();self.g['nodes'].append({'id':'junction'})
  blue=next(e for e in self.g['edges'] if e['id']=='blue');blue['to']='junction';blue['duration_s']=100;blue['length_m']=400
  tail=copy.deepcopy(blue);tail.update(id='tail',**{'from':'junction','to':'base','duration_s':200,'length_m':800});self.g['edges'].append(tail)
  self.i=f.intent();self.s=f.scenario(self.g)
 def test_roundtrip_and_objective_match(self):
  g,s=compact(self.g,self.s,['base','summit'])
  self.assertEqual(len(g['edges']),len(self.g['edges'])-1)
  r=plan(g,self.i,s)['route'];x=expand_route(self.g,self.s,g,r,self.i)
  self.assertTrue(validate_route(self.g,self.i,self.s,x)['valid'])
  self.assertEqual(x['total_seconds'],plan(self.g,self.i,self.s)['route']['total_seconds'])
 def test_protected_node_not_removed(self):
  g,_=compact(self.g,self.s,['junction'])
  self.assertEqual(len(g['edges']),len(self.g['edges']))
 def test_different_state_or_difficulty_not_merged(self):
  self.s['edges']['tail']['status']='closed';g,_=compact(self.g,self.s)
  self.assertEqual(len(g['edges']),len(self.g['edges']))
  self.s=f.scenario(self.g);self.g['edges'][-1]['difficulty']='red';self.s['graph_hash']=digest(self.g)
  g,_=compact(self.g,self.s);self.assertEqual(len(g['edges']),len(self.g['edges']))
 def test_source_edge_bound_preserved(self):
  self.i['excluded_lift_types']=['rope-tow'];self.i['hard_max_difficulty']='blue'
  g,s=compact(self.g,self.s,['base','summit'])
  self.assertEqual(plan(g,self.i,s,max_edges=2)['status'],'search_limit')
 def test_every_source_edge_once(self):
  g,_=compact(self.g,self.s)
  ids=[i for e in g['edges'] for i in e['source_edge_ids']]
  self.assertEqual(sorted(ids),sorted(e['id'] for e in self.g['edges']))
if __name__=='__main__':unittest.main()
