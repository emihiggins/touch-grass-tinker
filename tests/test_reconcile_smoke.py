import json,tempfile,unittest
from pathlib import Path
from liftlap.complete_reconciled_smoke import verify

class ReconciledCompletionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.d=Path(self.tmp.name)
        self.write('manifest.json',{'status':'halted_requires_reconciliation','hashes':{}})
        self.write('reconciled-restore.json',{'status':'completed','request_id':'known','response':{'model_id':'session:train:1'}})
        self.write('fresh-restore-events.jsonl',{'event':'submitted','operation':'restore_new_model','request_id':'known'})
        self.write('training-events.jsonl',{'event':'session_created','session_id':'session'})
    def write(self,name,value):(self.d/name).write_text(json.dumps(value)+'\n')
    def test_unknown_receipt_cannot_authorize_new_mutation(self):
        self.write('reconciled-restore.json',{'status':'completed','request_id':'wrong','response':{'model_id':'session:train:1'}})
        with self.assertRaisesRegex(ValueError,'identity'):verify(self.d)
    def test_existing_sampler_request_blocks_repeat(self):
        self.write('extra-events.jsonl',{'event':'submission_start','operation':'save_sampler'})
        with self.assertRaisesRegex(ValueError,'already exist'):verify(self.d)
    def test_completed_attempt_cannot_be_reentered(self):
        (self.d/'reconciled-finish-events.jsonl').touch()
        with self.assertRaisesRegex(ValueError,'already attempted'):verify(self.d)
