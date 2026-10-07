import unittest
from liftlap.billing_check import summarize

class BillingSummaryTests(unittest.TestCase):
    def test_safe_summary_does_not_conflate_estimate_and_invoice(self):
        r=summarize({'data':[{'user_name':'private','session_id':'private','estimated_cost_usd':.01,'event_info':{'type':'sampling_prefill'}}, {'estimated_cost_usd':None,'event_info':{'type':'checkpoint'}}], 'sessions':{'private':{}},'cost_data_through':None})
        self.assertEqual(r['priced_events'],1);self.assertEqual(r['unpriced_events'],1)
        self.assertIsNone(r['estimated_gross_usd']);self.assertEqual(r['priced_subtotal_usd'],.01);self.assertFalse(r['project_reconciled'])
        self.assertNotIn('private',str(r))
    def test_empty_usage_is_not_proof_of_zero_bill(self):
        r=summarize({});self.assertFalse(r['project_reconciled'])
        self.assertEqual(r['event_count'],0)

    def test_unpriced_events_are_not_zero_cost(self):
        r=summarize({'data':[{'event_info':{'type':'training'}}]})
        self.assertIsNone(r['estimated_gross_usd']);self.assertFalse(r['pricing_complete']);self.assertEqual(r['pricing_status'],'prices_unavailable')
    def test_explicit_zero_is_distinct_from_unknown(self):
        r=summarize({'data':[{'estimated_cost_usd':0,'event_info':{'type':'sampling'}}]})
        self.assertEqual(r['estimated_gross_usd'],0);self.assertTrue(r['pricing_complete']);self.assertFalse(r['project_reconciled'])
