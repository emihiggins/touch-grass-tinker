import json
import tempfile
import unittest
from pathlib import Path

from scripts.diagnose_connectivity import diagnose


class ConnectivityDiagnosticsTests(unittest.TestCase):
    def test_source_linked_diagnostics_are_non_mutating(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "source.osm").write_text(
                '<osm><node id="a" lat="39" lon="-105"/><node id="b" lat="39.0001" lon="-105"/>'
                '<node id="c" lat="39.0002" lon="-105"/><node id="d" lat="39.00021" lon="-105"/>'
                '<way id="1" version="1"><nd ref="a"/><nd ref="b"/><tag k="aerialway" v="chair_lift"/>'
                '<tag k="name" v="Lift"/></way><way id="2" version="1"><nd ref="c"/><nd ref="d"/>'
                '<tag k="piste:type" v="connection"/><tag k="name" v="Connector"/></way>'
                '<way id="3" version="1"><nd ref="b"/><nd ref="c"/><tag k="piste:type" v="downhill"/>'
                '<tag k="piste:difficulty" v="expert"/></way></osm>'
            )
            graph = {
                "nodes": [{"id": node, "lon": -105, "lat": 39 + index * 0.0001}
                          for index, node in enumerate("abcd")],
                "edges": [{"id": "lift", "from": "a", "to": "b", "kind": "lift",
                           "source_refs": ["way/1"]}],
            }
            (folder / "graph.json").write_text(json.dumps(graph))
            result = diagnose(folder)
            self.assertEqual(result["lift_count"], 1)
            self.assertEqual(result["excluded_source_way_count"], 2)
            self.assertEqual(result["automatic_connections_added"], 0)
            self.assertFalse(result["routing_enabled"])
            self.assertEqual(graph, json.loads((folder / "graph.json").read_text()))
            self.assertEqual(result["lifts"][0]["endpoint_incidence"][1]["source_node"], "b")


if __name__ == "__main__":
    unittest.main()

