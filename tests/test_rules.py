import unittest
from liftlap.rules import interpret
from scripts.benchmark import load_cases
class RulesTests(unittest.TestCase):
 def setUp(self):
  self.c=load_cases('benchmark/development-seed.jsonl')[0][0]
 def parse(self,s):return interpret(s,self.c['ui_context'],self.c['catalog'])['intent']
 def test_common_request(self):
  x=self.parse('Only blues, no drag lifts, 90 minutes please.')
  self.assertEqual(x['status'],'ready');self.assertEqual(x['duration_minutes'],90);self.assertEqual(x['hard_max_difficulty'],'blue')
  self.assertEqual(x['excluded_lift_types'],['platter','rope-tow','t-bar'])
 def test_unknown_semantics_abstains(self):
  self.assertEqual(self.parse('Take a helicopter to a remote glacier')['status'],'unsupported')
 def test_negation_not_exclusion(self):
  self.assertEqual(self.parse('I do not need to avoid gondolas.')['excluded_lift_types'],[])
 def test_deadline(self):
  self.assertEqual(self.parse('Two hours, back by 11:15')['duration_minutes'],75)
 def test_unknown_place_clarifies(self):
  x=self.parse('Finish at Eagle Cafe.');self.assertEqual(x['status'],'clarify');self.assertIsNone(x['finish_place_id'])
 def test_long_input_rejected(self):
  with self.assertRaises(ValueError):self.parse('x'*2001)
if __name__=='__main__':unittest.main()
