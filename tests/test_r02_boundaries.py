"""Replayable R02 boundary and metamorphic checks.

These tests deliberately exercise the deterministic planner/validator only. The
seeded graph family is synthetic and is not evidence of model or terrain quality.
"""
import copy
import random
import unittest

from liftlap import fixtures as f
from liftlap.compact import compact, expand_route
from liftlap.core import digest, plan, validate_route


def seeded_graph(seed):
    """Make a small directed graph with a replayable, bounded variation."""
    rng = random.Random(seed)
    graph = f.graph()
    for edge in graph["edges"]:
        edge["duration_s"] += rng.randrange(0, 4) * 5
        edge["length_m"] += rng.randrange(0, 4) * 10
    return graph


def refreshed_scenario(graph):
    scenario = f.scenario(graph)
    for edge in graph["edges"]:
        scenario["edges"][edge["id"]]["queue_s"] = 0
    return scenario


class R02BoundaryTests(unittest.TestCase):
    def test_generated_accepted_routes_pass_independent_validation(self):
        for seed in range(24):
            with self.subTest(seed=seed):
                graph = seeded_graph(seed)
                intent = f.intent()
                scenario = refreshed_scenario(graph)
                result = plan(graph, intent, scenario)
                self.assertEqual(result["status"], "ok", f"seed={seed}")
                self.assertTrue(validate_route(graph, intent, scenario, result["route"])["valid"])

    def test_injected_ids_connectivity_directions_and_status_are_rejected(self):
        graph = f.graph()
        intent = f.intent()
        scenario = f.scenario(graph)
        route = plan(graph, intent, scenario)["route"]
        cases = {
            "unknown_id": {"edge_ids": ["not-in-graph"]},
            "reversed": {"edge_ids": ["blue", "chair"]},
            "closed": {"edge_ids": route["edge_ids"]},
            "wrong_hash": {"scenario_hash": "tampered"},
        }
        scenario["edges"]["chair"]["status"] = "closed"
        for name, edit in cases.items():
            with self.subTest(name=name):
                candidate = copy.deepcopy(route)
                candidate.update(edit)
                self.assertFalse(validate_route(graph, intent, scenario, candidate)["valid"])

    def test_hard_max_and_excluded_lift_are_enforced_by_both_boundaries(self):
        graph = f.graph()
        scenario = f.scenario(graph)
        intent = f.intent()
        intent["hard_max_difficulty"] = "green"
        self.assertNotEqual(plan(graph, intent, scenario)["status"], "ok")
        intent = f.intent()
        intent["excluded_lift_types"] = ["chairlift", "rope-tow"]
        self.assertNotEqual(plan(graph, intent, scenario)["status"], "ok")
        candidate = {"edge_ids": ["chair", "blue"], "total_seconds": 600,
                     "graph_hash": digest(graph), "scenario_hash": digest(scenario)}
        intent["excluded_lift_types"] = ["chairlift"]
        self.assertEqual(validate_route(graph, intent, scenario, candidate)["reason"], "excluded_lift")

    def test_removing_edges_cannot_create_a_route_from_no_route(self):
        for seed in range(12):
            with self.subTest(seed=seed):
                graph = seeded_graph(seed)
                intent = f.intent()
                scenario = refreshed_scenario(graph)
                scenario["edges"]["chair"]["status"] = "closed"
                scenario["edges"]["tow"]["status"] = "closed"
                self.assertEqual(plan(graph, intent, scenario)["status"], "no_route")
                for removed in ("blue", "red", "practice"):
                    smaller = copy.deepcopy(graph)
                    smaller["edges"] = [e for e in smaller["edges"] if e["id"] != removed]
                    smaller_scenario = refreshed_scenario(smaller)
                    smaller_scenario["edges"]["chair"]["status"] = "closed"
                    smaller_scenario["edges"]["tow"]["status"] = "closed"
                    self.assertNotEqual(plan(smaller, intent, smaller_scenario)["status"], "ok")

    def test_fixed_route_budget_is_monotonic(self):
        graph = f.graph()
        scenario = f.scenario(graph)
        route = plan(graph, f.intent(), scenario)["route"]
        short = f.intent()
        short["duration_minutes"] = 1
        long = f.intent()
        long["duration_minutes"] = 60
        self.assertFalse(validate_route(graph, short, scenario, route)["valid"])
        self.assertTrue(validate_route(graph, long, scenario, route)["valid"])

    def test_bijective_node_renaming_preserves_feasibility(self):
        graph = f.graph()
        intent = f.intent()
        scenario = f.scenario(graph)
        renamed = {"base": "n0", "summit": "n1", "mid": "n2"}
        graph2 = copy.deepcopy(graph)
        for node in graph2["nodes"]:
            node["id"] = renamed[node["id"]]
        for edge in graph2["edges"]:
            edge["from"] = renamed[edge["from"]]
            edge["to"] = renamed[edge["to"]]
        intent2 = copy.deepcopy(intent)
        intent2["start_place_id"] = renamed[intent["start_place_id"]]
        intent2["finish_place_id"] = renamed[intent["finish_place_id"]]
        scenario2 = copy.deepcopy(scenario)
        scenario2["graph_hash"] = digest(graph2)
        self.assertEqual(plan(graph, intent, scenario)["status"], plan(graph2, intent2, scenario2)["status"])
        renamed_route = plan(graph2, intent2, scenario2)["route"]
        self.assertTrue(validate_route(graph2, intent2, scenario2, renamed_route)["valid"])

    def test_compaction_preserves_original_path_validation(self):
        graph = f.graph()
        graph["nodes"].append({"id": "junction"})
        blue = next(e for e in graph["edges"] if e["id"] == "blue")
        blue["to"] = "junction"
        tail = copy.deepcopy(blue)
        tail.update(id="tail", **{"from": "junction", "to": "base", "duration_s": 200, "length_m": 800})
        graph["edges"].append(tail)
        scenario = refreshed_scenario(graph)
        compacted, compacted_scenario = compact(graph, scenario, ["base", "summit"])
        intent = f.intent()
        compacted_route = plan(compacted, intent, compacted_scenario)["route"]
        expanded = expand_route(graph, scenario, compacted, compacted_route, intent)
        self.assertTrue(validate_route(graph, intent, scenario, expanded)["valid"])

    def test_temporal_contract_accepts_boundaries_and_rejects_unsupported_naive_time(self):
        graph = f.graph()
        scenario = f.scenario(graph)
        intent = f.intent()
        intent["start_time"] = "2027-01-15T15:00:00+01:00"
        self.assertEqual(plan(graph, intent, scenario)["status"], "ok")
        intent["start_time"] = "2027-01-15T10:00:00"
        with self.assertRaises(ValueError):
            plan(graph, intent, scenario)


if __name__ == "__main__":
    unittest.main()
