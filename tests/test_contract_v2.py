import copy
import unittest
from liftlap import fixtures
from liftlap.core import plan,validate_route,digest
from liftlap.rules import interpret
from liftlap.server import context,handle_api
from scripts.benchmark import validate_intent,score

class ContractV2Tests(unittest.TestCase):
    def setUp(self):
        self.graph,self.ui,self.catalog=context('synthetic')
    def parse(self,text):
        return interpret(text,self.ui,self.catalog,schema_version=2)['intent']
    def test_durations_are_not_missingness(self):
        for text,value in [('five hours',300),('10 minutes',10),('5 minutes',5)]:
            intent=self.parse(text);self.assertEqual(intent['duration_minutes'],value)
            self.assertEqual(intent['status'],'ready');validate_intent(intent,{'base','summit'})
        self.assertEqual(self.parse('back by 10:10')['duration_minutes'],10)
    def test_v1_is_still_v1(self):
        v1=interpret('five hours',self.ui,self.catalog)['intent']
        self.assertIsNone(v1['duration_minutes']);self.assertEqual(v1['status'],'clarify')
        self.assertNotIn('avoided_lift_types',v1)
    def test_avoid_and_no_have_different_contracts(self):
        soft=self.parse('avoid gondolas');hard=self.parse('no gondolas')
        self.assertEqual(soft['avoided_lift_types'],['gondola']);self.assertEqual(soft['excluded_lift_types'],[])
        self.assertEqual(hard['avoided_lift_types'],[]);self.assertEqual(hard['excluded_lift_types'],['gondola'])
        row={'id':'one','catalog':self.catalog,'gold_intent':soft}
        self.assertFalse(score([row],[{'id':'one','intent':hard}])['cases'][0]['exact_match'])
    def test_soft_lists_mandatory_valid_and_disjoint(self):
        for change in ({'avoided_lift_types':['unknown']},{'avoided_lift_types':['gondola','gondola']},
                       {'avoided_lift_types':['gondola'],'excluded_lift_types':['gondola']}):
            intent=self.parse('');intent.update(change)
            with self.assertRaises(ValueError):validate_intent(intent,{'base','summit'})
        intent=self.parse('');del intent['avoided_lift_types']
        with self.assertRaises(ValueError):validate_intent(intent,{'base','summit'})
    def test_soft_avoidance_ranks_alternative_first(self):
        intent=self.parse('avoid chairlifts, 30 minutes');g=fixtures.graph();s=fixtures.scenario(g)
        result=plan(g,intent,s)
        self.assertEqual(result['status'],'ok');self.assertNotIn('chair',result['route']['edge_ids'])
        self.assertEqual(result['preference_tradeoffs'],[])
    def test_soft_access_lift_disclosed_but_hard_never_waived(self):
        g=fixtures.graph();g['edges']=[e for e in g['edges'] if e['id'] not in ('tow','practice')]
        g['edges'][0]['lift_type']='gondola';s=fixtures.scenario(g)
        soft=self.parse('avoid gondolas');result=plan(g,soft,s)
        self.assertEqual(result['status'],'ok');self.assertEqual(result['preference_tradeoffs'][0]['lift_types'],['gondola'])
        self.assertTrue(validate_route(g,soft,s,result['route'])['valid'])
        hard=self.parse('no gondolas')
        self.assertEqual(plan(g,hard,s)['status'],'no_route')
        self.assertFalse(validate_route(g,hard,s,result['route'])['valid'])
    def test_long_budget_does_not_override_closure(self):
        g=fixtures.graph();s=fixtures.scenario(g)
        for state in s['edges'].values():state['closes_at']='2027-01-15T10:01:00+01:00'
        self.assertEqual(plan(g,self.parse('five hours'),s)['status'],'no_route')
    def test_short_duration_can_be_infeasible_not_clarify(self):
        result=plan(fixtures.graph(),self.parse('1 minute'),fixtures.scenario(fixtures.graph()))
        self.assertEqual(result['status'],'no_route')
    def test_resource_horizon_separate_from_semantic_duration(self):
        intent=self.parse('1500 minutes');validate_intent(intent,{'base','summit'})
        self.assertEqual(intent['duration_minutes'],1500)
        with self.assertRaisesRegex(ValueError,'horizon'):plan(fixtures.graph(),intent,fixtures.scenario(fixtures.graph()))
    def test_api_roundtrip_duration_and_soft_preference(self):
        for minutes in (10,300):
            intent=handle_api('/api/interpret',{'minutes':minutes,'text':'avoid chairlifts'})['intent']
            self.assertEqual(intent['schema_version'],2)
            result=handle_api('/api/plan',{'intent':intent})
            self.assertEqual(result['status'],'ok');self.assertTrue(result['validation']['valid'])
