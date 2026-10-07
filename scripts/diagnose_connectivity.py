"""Source-linked connectivity diagnostics; never changes or approves a routing graph."""
import argparse
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

PROXIMITY_M = 30.0

def distance(a, b):
    lat = math.radians((a[1] + b[1]) / 2)
    dx = math.radians(b[0] - a[0]) * math.cos(lat)
    dy = math.radians(b[1] - a[1])
    return 6_371_000 * math.sqrt(dx * dx + dy * dy)

def source_ways(root):
    result = []
    for way in root.findall("way"):
        tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
        if "piste:type" not in tags and "aerialway" not in tags:
            continue
        result.append({"source_ref": f"way/{way.get('id')}", "version": way.get("version"), "nodes": [node.get("ref") for node in way.findall("nd")], "tags": dict(sorted(tags.items()))})
    return sorted(result, key=lambda way: way["source_ref"])

def diagnose(folder, proximity_m=PROXIMITY_M):
    graph_path = folder / "graph.json"
    source_path = folder / "source.osm"
    graph = json.loads(graph_path.read_text())
    root = ET.parse(source_path).getroot()
    source_nodes = {node.get("id"): [float(node.get("lon")), float(node.get("lat"))] for node in root.findall("node")}
    ways = source_ways(root)
    edges = sorted(graph["edges"], key=lambda edge: edge["id"])
    by_ref = {}
    for edge in edges:
        for ref in edge.get("source_refs", []):
            by_ref.setdefault(ref, []).append(edge)
    node_edges = {}
    for edge in edges:
        for node in (edge["from"], edge["to"]):
            node_edges.setdefault(node, []).append(edge)
    lifts = []
    for way in ways:
        if "aerialway" not in way["tags"] or len(way["nodes"]) < 2:
            continue
        imported = by_ref.get(way["source_ref"], [])
        endpoint_rows = []
        for endpoint_role, node in (("boarding_candidate", way["nodes"][0]), ("alighting_candidate", way["nodes"][-1])):
            incident = sorted(node_edges.get(node, []), key=lambda edge: edge["id"])
            endpoint_rows.append({"role_if_source_direction_is_correct": endpoint_role, "source_node": node, "graph_edge_incidence": [{"edge_id": edge["id"], "kind": edge["kind"], "from": edge["from"], "to": edge["to"]} for edge in incident], "incoming_piste_edge_ids": [edge["id"] for edge in incident if edge["kind"] == "piste" and edge["to"] == node], "outgoing_piste_edge_ids": [edge["id"] for edge in incident if edge["kind"] == "piste" and edge["from"] == node]})
        lifts.append({"source_ref": way["source_ref"], "name": way["tags"].get("name", way["source_ref"]), "aerialway": way["tags"].get("aerialway"), "imported_edge_ids": [edge["id"] for edge in imported], "endpoint_incidence": endpoint_rows, "review_question": "Confirm boarding/alighting terminals and whether a permitted descent reaches or leaves each terminal; source direction is unverified."})
    excluded = []
    for way in ways:
        if way["source_ref"] in by_ref:
            continue
        tags = way["tags"]
        if tags.get("piste:type") == "connection":
            reason = "unsupported_piste_type_connection_not_imported"
        elif tags.get("piste:type") == "downhill" and tags.get("piste:difficulty") not in {"novice", "easy", "intermediate", "advanced"}:
            reason = "unknown_difficulty_excluded_by_importer"
        elif tags.get("piste:type") == "downhill":
            reason = "not_present_in_imported_graph_check_source_and_import_audit"
        elif "aerialway" in tags:
            reason = "lift_not_present_in_imported_graph_check_source_and_import_audit"
        else:
            continue
        excluded.append({"source_ref": way["source_ref"], "name": tags.get("name", way["source_ref"]), "piste_type": tags.get("piste:type"), "aerialway": tags.get("aerialway"), "difficulty": tags.get("piste:difficulty"), "nodes": way["nodes"], "reason": reason, "review_question": "Decide whether this source way is in scope and what dated source evidence, access permission, grade, direction and station relation would be needed; do not infer a connector."})
    candidates = []
    for lift in lifts:
        way = next(item for item in ways if item["source_ref"] == lift["source_ref"])
        for role, node in (("source_start", way["nodes"][0]), ("source_end", way["nodes"][-1])):
            if node not in source_nodes:
                continue
            for candidate in excluded:
                candidate_nodes = [n for n in candidate["nodes"] if n in source_nodes]
                best = min((distance(source_nodes[node], source_nodes[n]) for n in candidate_nodes), default=None)
                if best is not None and best <= proximity_m:
                    candidates.append({"lift_source_ref": lift["source_ref"], "lift_endpoint_role": role, "lift_endpoint_node": node, "excluded_source_ref": candidate["source_ref"], "minimum_endpoint_distance_m": round(best, 3), "evidence_only": True, "review_question": "Inspect source geometry and station/access evidence; proximity does not create incidence or a connector."})
    return {"schema": 1, "scope": "source_linked_connectivity_review_evidence_only", "graph_sha256": hashlib.sha256(graph_path.read_bytes()).hexdigest(), "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(), "proximity_threshold_m": proximity_m, "graph_preserved": True, "automatic_connections_added": 0, "routing_enabled": False, "lift_count": len(lifts), "lifts": lifts, "excluded_source_way_count": len(excluded), "excluded_source_ways": excluded, "proximity_candidates": sorted(candidates, key=lambda item: (item["lift_source_ref"], item["excluded_source_ref"], item["lift_endpoint_role"])), "limitations": ["Exact shared source node and geometric proximity are review evidence, not verified boarding, alighting, permission, direction, grade or safety.", "The bounded extract may omit connecting ways and complete ways may extend outside its requested box.", "OSM relations, operational schedules and current closures are not resolved."]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--proximity-m", type=float, default=PROXIMITY_M)
    args = parser.parse_args()
    result = diagnose(args.folder.resolve(), args.proximity_m)
    output = args.output or args.folder / "connectivity-diagnostics.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("lift_count", "excluded_source_way_count", "automatic_connections_added", "routing_enabled")}))

if __name__ == "__main__":
    main()

