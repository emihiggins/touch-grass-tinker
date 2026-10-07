import copy
import math
import unittest
from liftlap import fixtures as f
from liftlap.core import plan,validate_route,digest,check_graph
from liftlap.import_osm import import_osm

class RoutingTests(unittest.TestCase):
    def setUp(self):self.g=f.graph();self.i=f.intent();self.s=f.scenario(self.g)
    def test_nonempty_base_to_base(self):
        r=plan(self.g,self.i,self.s)['route']
        self.assertTrue(r['edge_ids']);self.assertTrue(validate_route(self.g,self.i,self.s,r)['valid'])
        self.assertNotIn('red',r['edge_ids'])
    def test_excluded_surface_lifts(self):
        self.i['excluded_lift_types']=['rope-tow'];r=plan(self.g,self.i,self.s)
        self.assertEqual(r['status'],'ok');self.assertNotIn('tow',r['route']['edge_ids'])
    def test_closed_and_unknown_lifts_no_route(self):
        for status in ['closed','unknown']:
            with self.subTest(status=status):
                self.s['edges']['chair']['status']=status;self.s['edges']['tow']['status']=status
                self.assertEqual(plan(self.g,self.i,self.s)['status'],'no_route')
    def test_no_route_reports_actual_closure_reason(self):
        for eid in ['chair','tow']: self.s['edges'][eid]['status']='closed'
        result=plan(self.g,self.i,self.s)
        self.assertEqual(result['status'],'no_route')
        self.assertEqual(result['reasons'],['closed'])

    def test_no_route_reports_disconnected_finish_reason(self):
        self.g['edges']=[e for e in self.g['edges'] if e['to']!='summit']
        self.i['finish_place_id']='summit'
        self.s=f.scenario(self.g)
        result=plan(self.g,self.i,self.s)
        self.assertEqual(result['reasons'],['finish_unreachable'])

    def test_no_route_reports_actual_time_reason(self):
        self.i['duration_minutes']=15
        for eid in ['chair','tow']: self.s['edges'][eid]['queue_s']=1000
        result=plan(self.g,self.i,self.s)
        self.assertEqual(result['status'],'no_route')
        self.assertIn('deadline',result['reasons'])

    def test_time_and_queue_make_route_infeasible(self):
        for eid in ['chair','tow']:self.s['edges'][eid]['queue_s']=2000
        self.assertEqual(plan(self.g,self.i,self.s)['status'],'no_route')
    def test_early_closure(self):
        for state in self.s['edges'].values():state['closes_at']='2027-01-15T10:00:30+01:00'
        self.assertEqual(plan(self.g,self.i,self.s)['status'],'no_route')
    def test_missing_state_is_not_open(self):
        del self.s['edges']['chair'];del self.s['edges']['tow']
        self.assertEqual(plan(self.g,self.i,self.s)['status'],'no_route')
    def test_future_opening_not_waited_for(self):
        for state in self.s['edges'].values():state['opens_at']='2027-01-15T11:00:00+01:00'
        self.assertEqual(plan(self.g,self.i,self.s)['status'],'no_route')
    def test_search_limits_not_infeasibility(self):
        self.assertEqual(plan(self.g,self.i,self.s,max_states=1)['status'],'search_limit')
        self.assertEqual(plan(self.g,self.i,self.s,max_edges=1)['status'],'search_limit')
    def test_parallel_edges_preserved(self):
        self.assertEqual(sum(e['from']=='summit' and e['to']=='base' for e in self.g['edges']),2)
    def test_unreviewed_requires_explicit_lab(self):
        self.g['review_status']='unreviewed';self.s=f.scenario(self.g)
        self.assertEqual(plan(self.g,self.i,self.s)['status'],'unreviewed_graph')
        self.assertEqual(plan(self.g,self.i,self.s,lab=True)['status'],'ok')
    def test_edge_review_flag_cannot_hide_under_synthetic_graph(self):
        for e in self.g['edges']:
            if e['kind']=='lift':e['review_status']='unreviewed'
        self.s=f.scenario(self.g)
        self.assertEqual(plan(self.g,self.i,self.s)['status'],'no_route')
        result=plan(self.g,self.i,self.s,lab=True)['route']
        self.assertEqual(validate_route(self.g,self.i,self.s,result)['reason'],'unreviewed_edge')

    def test_hash_and_dates_enforced(self):
        self.s['date']='2027-01-16'
        with self.assertRaises(ValueError):plan(self.g,self.i,self.s)
        self.s=f.scenario(self.g);self.s['graph_hash']='wrong'
        with self.assertRaises(ValueError):plan(self.g,self.i,self.s)
    def test_equivalent_timezone(self):
        self.i['start_time']='2027-01-15T09:00:00+00:00'
        self.assertEqual(plan(self.g,self.i,self.s)['status'],'ok')
    def test_invalid_weight_and_missing_node(self):
        for val in [0,-1,float('nan'),float('inf'),True]:
            g=copy.deepcopy(self.g);g['edges'][0]['duration_s']=val
            with self.assertRaises(ValueError):check_graph(g)
        self.g['edges'][0]['to']='imaginary'
        with self.assertRaises(ValueError):check_graph(self.g)
    def test_validator_rejects_fabrication_and_reversed_path(self):
        r=plan(self.g,self.i,self.s)['route']
        for edit in [{'edge_ids':[]},{'edge_ids':['imaginary']},{'total_seconds':1},{'edge_ids':['blue','chair']},{'scenario_hash':'wrong'}]:
            bad=copy.deepcopy(r);bad.update(edit)
            self.assertFalse(validate_route(self.g,self.i,self.s,bad)['valid'])
    def test_validator_uses_gold_not_permissive_prediction(self):
        r={'edge_ids':['chair','red'],'total_seconds':500,'graph_hash':digest(self.g),'scenario_hash':digest(self.s)}
        self.assertEqual(validate_route(self.g,self.i,self.s,r)['reason'],'difficulty')
    def test_validator_rechecks_closure(self):
        r=plan(self.g,self.i,self.s)['route'];self.s['edges']['chair']['status']='closed'
        r['scenario_hash']=digest(self.s)
        self.assertEqual(validate_route(self.g,self.i,self.s,r)['reason'],'not_open')
    def test_import_skips_restricted_unknown_and_ambiguous(self):
        xml=b'''<osm><node id="a" lon="0" lat="0"/><node id="b" lon="0.001" lat="0"/>
        <way id="1"><nd ref="a"/><nd ref="b"/><tag k="piste:type" v="downhill"/><tag k="piste:difficulty" v="easy"/></way>
        <way id="2"><nd ref="a"/><nd ref="b"/><tag k="piste:type" v="downhill"/><tag k="piste:difficulty" v="intermediate"/></way>
        <way id="3"><nd ref="a"/><nd ref="b"/><tag k="aerialway" v="chair_lift"/><tag k="access" v="private"/></way>
        <way id="4"><nd ref="a"/><nd ref="b"/><tag k="piste:type" v="downhill"/></way></osm>'''
        g,a=import_osm(xml);self.assertEqual(g['edges'],[])
        self.assertEqual({s['reason'] for s in a['skipped_ways']},{'conflicting_overlap_difficulty','restricted_access','unknown_difficulty'})
    def test_import_native_ids_no_snapping(self):
        xml=b'''<osm><node id="a" lon="0" lat="0"/><node id="b" lon="0.001" lat="0"/><node id="c" lon="0.001" lat="0"/>
        <way id="1"><nd ref="a"/><nd ref="b"/><tag k="aerialway" v="chair_lift"/></way>
        <way id="2"><nd ref="c"/><nd ref="a"/><tag k="piste:type" v="downhill"/><tag k="piste:difficulty" v="easy"/></way></osm>'''
        g,_=import_osm(xml);self.assertEqual({n['id'] for n in g['nodes']},{'a','b','c'})
        self.assertEqual(g['review_status'],'unreviewed')
        self.assertTrue(all(e['duration_basis']=='assumed' for e in g['edges']))

if __name__=='__main__':unittest.main()
