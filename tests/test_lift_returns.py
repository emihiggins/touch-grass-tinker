import unittest
from scripts.review_lift_returns import review

class LiftReturns(unittest.TestCase):
    def test_only_directed_pistes_can_close_return(self):
        lift = {'id':'lift','name':'Test','kind':'lift','from':'bottom','to':'top'}
        reverse = {'id':'reverse','kind':'piste','from':'bottom','to':'top'}
        extra_lift = {'id':'other','name':'Other','kind':'lift','from':'top','to':'bottom'}
        result = review({'edges':[lift,reverse,extra_lift]})
        self.assertIsNone(next(r for r in result if r['lift_edge_id']=='lift')['piste_only_return_edge_ids'])
        down = {'id':'down','kind':'piste','from':'top','to':'bottom'}
        self.assertEqual(review({'edges':[lift,down]})[0]['piste_only_return_edge_ids'], ['down'])

    def test_cycle_does_not_hide_missing_return(self):
        edges = [{'id':'lift','name':'Test','kind':'lift','from':'bottom','to':'a'},
                 {'id':'ab','kind':'piste','from':'a','to':'b'},
                 {'id':'ba','kind':'piste','from':'b','to':'a'}]
        self.assertFalse(review({'edges':edges})[0]['structural_return_found'])

    def test_saved_winter_park_report_matches_graph(self):
        import hashlib, json
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        raw = (root/'data/terrain/winter-park-research/graph.json').read_bytes()
        saved = json.loads((root/'research/evidence/resort-review/winter-park-lift-returns.json').read_text())
        self.assertEqual(saved['graph_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(saved['lifts'], review(json.loads(raw)))
        self.assertFalse(saved['routing_approved'])
