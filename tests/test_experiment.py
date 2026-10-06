import copy,importlib.util,unittest
from liftlap.experiment import compare

class ComparisonTests(unittest.TestCase):
    def report(self,successes,valid=None):
        return {'count':len(successes),'successes':sum(successes),'cases':[{'id':str(i),'success':s,'gold_route_valid':(valid[i] if valid else None)} for i,s in enumerate(successes)]}
    def test_paired_threshold_not_just_net_accuracy(self):
        base=self.report([False,False,True,False]);trained=self.report([True,True,True,False])
        result=compare(base,trained);self.assertTrue(result['screening_pass']);self.assertEqual(result['paired_wins'],['0','1'])
        self.assertFalse(result['statistical_superiority_claim'])
    def test_safety_regression_blocks_candidate(self):
        base=self.report([False,False,True],[None,None,True]);trained=self.report([True,True,True],[None,None,False])
        self.assertFalse(compare(base,trained)['screening_pass'])
    def test_equal_or_worse_does_not_pass(self):
        self.assertFalse(compare(self.report([True,False]),self.report([False,True]))['screening_pass'])

@unittest.skipUnless(importlib.util.find_spec('tinker_cookbook'),'optional training environment')
class ExperimentPreparationTests(unittest.TestCase):
    def test_all_rows_and_frozen_pilot_fit_budget(self):
        from liftlap.experiment import prepare_experiment
        config,train,test,graphs,freeze,tokenizer,renderer,datums,prompts,plan=prepare_experiment()
        self.assertEqual(len(datums),47);self.assertEqual(len(prompts),16)
        self.assertEqual(plan['optimizer_steps'],3)
        self.assertLess(plan['cost_upper_estimate_usd'],1.25)
        self.assertEqual(plan['max_sampling_requests'],32)
        self.assertIn('liftlap/experiment.py',plan['hashes'])
