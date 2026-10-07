import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class DiscoveryQualification(unittest.TestCase):
    def test_packet_is_bound_and_explicit_about_unknowns(self):
        packet = json.loads((ROOT / "research/evidence/resort-review/discovery-qualification.json").read_text())
        self.assertEqual(packet["graph_sha256"], hashlib.sha256((ROOT / "data/terrain/winter-park-research/graph.json").read_bytes()).hexdigest())
        self.assertEqual(packet["source_sha256"], hashlib.sha256((ROOT / "data/terrain/winter-park-research/source.osm").read_bytes()).hexdigest())
        self.assertFalse(packet["routing_approved"])
        self.assertEqual(len(packet["topology"]["return"]["edge_ids"]), 8)
        self.assertIsNone(packet["topology"]["lift"]["native_direction_tag"])
        self.assertEqual(packet["topology"]["return"]["native_grade"], "easy")
        self.assertIn("permitted skier access", packet["topology"]["lift"]["unknown_fields"])
