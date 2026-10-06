import concurrent.futures,json,sqlite3,tempfile,unittest
from pathlib import Path
from liftlap.spend import Ledger,units

class SpendTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'spend.sqlite'
        self.auth=json.loads(Path('training/budget-authorization.json').read_text())
        self.ledger=Ledger(self.path,self.auth)
    def test_unreconciled_history_blocks_new_spend(self):
        with self.assertRaisesRegex(ValueError,'unreconciled'):self.ledger.reserve('one','smoke',0.1,'test')
    def test_crash_reservations_persist_and_duplicates_fail(self):
        self.ledger.reconcile_prior(.01,'test invoice')
        self.ledger.reserve('one','smoke',.7,'bounded request')
        reopened=Ledger(self.path,self.auth)
        with self.assertRaises(ValueError):reopened.reserve('two','smoke',.4,'another request')
        reopened.settle('one',.2,'verified invoice')
        with self.assertRaises(sqlite3.IntegrityError):reopened.reserve('one','smoke',.1,'duplicate')
    def test_concurrent_reservations_cannot_overspend(self):
        self.ledger.reconcile_prior(.01,'test invoice')
        def attempt(i):
            try:self.ledger.reserve(str(i),'smoke',.6,'bounded');return True
            except ValueError:return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(attempt,range(2))),1)
    def test_total_cap_counts_prior_usage_and_storage_reservations(self):
        self.ledger.reconcile_prior(9.5,'test invoice')
        self.ledger.reserve('storage','smoke',.4,'maximum storage commitment')
        with self.assertRaises(ValueError):self.ledger.reserve('train','experiments',.2,'bounded')
    def test_amounts_and_settlement_are_conservative(self):
        self.assertEqual(units('0.0000000001'),1)
        for amount in ('NaN','Infinity',-1):
            with self.assertRaises(ValueError):units(amount)
        self.ledger.reconcile_prior(.01,'test invoice')
        self.ledger.reserve('one','smoke',.1,'bounded')
        with self.assertRaises(ValueError):self.ledger.settle('one',.2,'invoice')
        self.assertEqual(self.ledger.snapshot()['unresolved'],1)
    def test_prior_hold_is_unresolved_but_counts_against_project(self):
        self.ledger.reserve_prior(.1,'all historical request upper bounds with margin')
        self.ledger.reserve('smoke','smoke',.25,'bounded smoke')
        self.assertEqual(self.ledger.snapshot()['committed_usd'],.35)
        self.assertEqual(self.ledger.snapshot()['unresolved'],2)
        with self.assertRaises(ValueError):self.ledger.reserve_prior(.01,'cannot overwrite prior hold')
