import unittest
from liftlap.billing_check import summarize

class BillingSummaryTests(unittest.TestCase):
    def test_safe_summary_does_not_conflate_estimate_and_invoice(self):
        r=summarize({'data':[{'user_name':'private','session_id':'private','estimated_cost_usd':.01,'event_info':{'type':'sampling_prefill'}}, {'estimated_cost_usd':None,'event_info':{'type':'checkpoint'}}], 'sessions':{'private':{}},'cost_data_through':None})
        self.assertEqual(r['priced_events'],1);self.assertEqual(r['unpriced_events'],1)
        self.assertEqual(r['estimated_gross_usd'],.01);self.assertFalse(r['project_reconciled'])
        self.assertNotIn('private',str(r))
    def test_empty_usage_is_not_proof_of_zero_bill(self):
        r=summarize({});self.assertFalse(r['project_reconciled'])
        self.assertEqual(r['event_count'],0)
