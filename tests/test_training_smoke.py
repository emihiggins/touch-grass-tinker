import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

@unittest.skipUnless(importlib.util.find_spec('tinker_cookbook'),'optional training environment required')
class SmokePlanTests(unittest.TestCase):
    def test_fixed_smoke_has_approved_rows_and_conservative_reservation(self):
        from liftlap.training_smoke import prepare_smoke
        _,cases,_,_,datums,_,plan=prepare_smoke()
        self.assertEqual(len(datums),2);self.assertEqual(len(cases),2)
        self.assertLess(plan['upper_estimate_usd'],plan['reserved_usd'])
        self.assertEqual(plan['checkpoint_ttl_seconds'],3600)
        self.assertIn('liftlap/training_smoke.py',plan['hashes'])
    def test_live_refuses_unbound_plan_before_creating_run(self):
        from liftlap.training_smoke import main
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'run'
            with patch('sys.argv',['smoke','--live','--run-dir',str(path)]):
                with self.assertRaises(SystemExit):main()
            self.assertFalse(path.exists())
