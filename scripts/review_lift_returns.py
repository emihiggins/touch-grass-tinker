"""Report piste-only return paths for structural review, never route approval."""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path


def review(graph):
    adjacency = {}
    for edge in sorted(graph['edges'], key=lambda e: e['id']):
        if edge['kind'] == 'piste':
            adjacency.setdefault(edge['from'], []).append(edge)
    rows = []
    for lift in sorted((e for e in graph['edges'] if e['kind'] == 'lift'), key=lambda e: e['id']):
        queue = deque([(lift['to'], [])])
        seen = {lift['to']}
        result = None
        while queue:
            node, path = queue.popleft()
            if node == lift['from']:
                result = path
                break
            for edge in adjacency.get(node, []):
                if edge['to'] not in seen:
                    seen.add(edge['to'])
                    queue.append((edge['to'], path + [edge['id']]))
        rows.append({'lift_edge_id': lift['id'], 'name': lift['name'],
                     'source_refs': lift.get('source_refs', []),
                     'piste_only_return_edge_ids': result,
                     'structural_return_found': result is not None,
                     'review_status': 'unreviewed'})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('graph', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raw = args.graph.read_bytes()
    output = {'schema': 1, 'graph_sha256': hashlib.sha256(raw).hexdigest(),
              'method': 'Directed breadth-first search using piste edges only; fewest segments, not fastest or recommended route.',
              'routing_approved': False,
              'limitations': 'Assumes imported direction; ignores access, grades, closures and timing. Absence means no path in this extract, not no real-world descent.',
              'lifts': review(json.loads(raw))}
    args.output.write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
