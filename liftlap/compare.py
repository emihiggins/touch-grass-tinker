"""Replay saved paired intent predictions; not end-to-end request-success scoring."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random
from scripts.benchmark import score
from .corpus import read, audit

def compare(cases, baseline, tuned, draws=5000, seed=0):
    if not cases or draws < 100: raise ValueError('Need cases and at least 100 bootstrap draws')
    if audit(cases)['errors']: raise ValueError('Corpus audit failed')
    a, b = score(cases, baseline), score(cases, tuned)
    clusters = defaultdict(list)
    for c, x, y in zip(cases, a['cases'], b['cases']):
        clusters[c.get('template_family_id', c['family_id'])].append(int(y['exact_match']) - int(x['exact_match']))
    values = list(clusters.values()); rng = random.Random(seed); samples = []
    for _ in range(draws):
        sampled = [delta for cluster in rng.choices(values, k=len(values)) for delta in cluster]
        samples.append(sum(sampled) / len(sampled))
    samples.sort()
    return {'metric': a['metric'], 'scope': 'saved_predictions_not_provider_or_route_verification',
            'count': len(cases), 'splits': sorted({c['split'] for c in cases}),
            'baseline': a, 'tuned': b, 'delta_percentage_points': 100 * (b['correct'] - a['correct']) / len(cases),
            'paired_template_cluster_bootstrap': {'clusters': len(values), 'draws': draws, 'seed': seed,
                'interval_95_percentage_points': [100*samples[int(draws*.025)], 100*samples[int(draws*.975)]],
                'warning': 'Few clusters give unreliable uncertainty; development results are not held-out evidence.'}}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('cases'); p.add_argument('baseline'); p.add_argument('tuned')
    a = p.parse_args()
    report = compare(read(a.cases), read(a.baseline), read(a.tuned))
    report['sha256'] = {k: hashlib.sha256(Path(v).read_bytes()).hexdigest() for k,v in vars(a).items()}
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
