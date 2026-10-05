"""Read-only structural audit; no claim of real-world route validation.
Usage: python3 research/scripts/audit_graph.py /path/to/terrain.json
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

raw = Path(sys.argv[1]).read_bytes()
data = json.loads(raw)
nodes = {n['id']: n for n in data['nodes']}

def reachable(adj, start):
    seen = {start}
    todo = [start]
    while todo:
        for nxt in adj.get(todo.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return seen

results = {}
for label, allowed in [('all', {'blue', 'red', 'black'}), ('blue_only', {'blue'})]:
    piste = collections.defaultdict(set)
    adj = collections.defaultdict(set)
    invalid = []
    uphill = []
    for t in data['trails']:
        if t['difficulty'] not in allowed:
            continue
        a, b = t['fromNodeId'], t['toNodeId']
        if a not in nodes or b not in nodes:
            invalid.append(t['id'])
            continue
        piste[a].add(b)
        adj[a].add(b)
        coords = t['geometry']['coordinates']
        if len(coords[0]) > 2 and len(coords[-1]) > 2 and coords[-1][2] > coords[0][2] + 5:
            uphill.append(t['id'])
    loops = []
    for lift in data['lifts']:
        stations = lift['stationNodeIds']
        for a, b in zip(stations, stations[1:]):
            if a not in nodes or b not in nodes:
                invalid.append(lift['id'])
            else:
                adj[a].add(b)
        if len(stations) >= 2 and stations[0] in reachable(piste, stations[-1]):
            loops.append({'id': lift['id'], 'name': lift['name'].get('en'), 'type': lift['type']})
    # Mutual reachability partition is equivalent to SCCs; adequate for this tiny audit.
    reach = {n: reachable(adj, n) for n in nodes}
    remaining = set(nodes)
    components = []
    while remaining:
        start = min(remaining)
        component = {n for n in remaining if n in reach[start] and start in reach[n]}
        remaining -= component
        components.append(sorted(component))
    components.sort(key=lambda c: (-len(c), c[0]))
    results[label] = {
        'strong_component_sizes': [len(c) for c in components],
        'largest_component_node_ids': components[0],
        'lift_then_piste_only_return_candidates': loops,
        'missing_node_references': invalid,
        'pistes_ending_over_5m_above_start': uphill,
    }
print(json.dumps({
    'source_sha256': hashlib.sha256(raw).hexdigest(),
    'source_revision': 'ce3b2a11b782c17f9f58fae3cea7008e09d4d55f',
    'method': 'Piste from/to direction; lift station order; no walking links; no status/time validation. Geometric evidence only.',
    'results': results,
}, indent=2, ensure_ascii=False))
