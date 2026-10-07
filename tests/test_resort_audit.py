import unittest
from scripts.audit_resort_snapshot import directed_audit
from scripts.resort_review_packet import spreadsheet_safe
class DirectedAuditTests(unittest.TestCase):
 def test_connected_chain_is_not_round_trip(self):
  g={'nodes':[{'id':x} for x in 'abc'],'edges':[{'from':'a','to':'b'},{'from':'b','to':'c'}]};r=directed_audit(g)
  self.assertEqual(r['strong_component_sizes'],[1,1,1]);self.assertEqual(r['nodes_on_directed_cycles'],0);self.assertEqual(r['sink_nodes'],['c'])
 def test_cycle_and_disconnected_node(self):
  g={'nodes':[{'id':x} for x in 'abcd'],'edges':[{'from':'a','to':'b'},{'from':'b','to':'c'},{'from':'c','to':'a'}]};r=directed_audit(g)
  self.assertEqual(r['strong_component_sizes'],[3,1]);self.assertEqual(r['nodes_on_directed_cycles'],3)

 def test_untrusted_csv_cells_are_literal(self):
  self.assertEqual(spreadsheet_safe("=1+1"),"'=1+1");self.assertEqual(spreadsheet_safe("  @name"),"'  @name");self.assertEqual(spreadsheet_safe("Plose 2"),"Plose 2")
