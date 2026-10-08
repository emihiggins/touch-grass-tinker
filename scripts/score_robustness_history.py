"""Reproduce separate R03 historical diagnostics; never promote or call a provider."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from liftlap.core import digest
from liftlap.corpus import read
from liftlap.evaluation_v2 import evaluate as historical_evaluate
from liftlap.evaluation_v3 import collect_runs, evaluate
from liftlap.promotion import POLICY, decide
from liftlap.render_audit import sha


def generate():
    experiment = json.loads(Path('research/evidence/experiment-01/manifest.json').read_text())
    fresh = json.loads(Path('research/evidence/fresh-base-evaluation/manifest.json').read_text())
    reports = []
    artifacts = {}
    for name, folder, cases_path, graphs_path, freeze_path, predictions_path, saved in [
        ('pilot-base', 'experiment-01', 'benchmark/v2/evaluation-pilot-frozen.jsonl',
         'benchmark/v2/evaluation-graphs.json', 'benchmark/v2/evaluation-pilot-freeze.json',
         'research/evidence/experiment-01/base-predictions.jsonl', experiment),
        ('pilot-tuned', 'experiment-01', 'benchmark/v2/evaluation-pilot-frozen.jsonl',
         'benchmark/v2/evaluation-graphs.json', 'benchmark/v2/evaluation-pilot-freeze.json',
         'research/evidence/experiment-01/trained-predictions.jsonl', experiment),
        ('fresh-base', 'fresh-base-evaluation', 'benchmark/v2/final-review/cases.jsonl',
         'benchmark/v2/final-review/graphs.json', 'benchmark/v2/final-review/freeze.json',
         'research/evidence/fresh-base-evaluation/predictions.jsonl', fresh)]:
        cases = read(cases_path); graphs = json.loads(Path(graphs_path).read_text())
        freeze = json.loads(Path(freeze_path).read_text()); predictions = read(predictions_path)
        manifest = {'run_id': name, 'assigned_case_ids': [c['id'] for c in cases], 'lane': 'primary',
                    'model': 'Qwen/Qwen3-8B',
                    'model_version': ('sampler-sha256:' + experiment['checkpoint_fingerprints']['sampler_checkpoint']) if name == 'pilot-tuned' else None,
                    'prompt_sha256': saved['hashes']['benchmark/v2/baseline-prompt.txt'],
                    'renderer_sha256': None, 'renderer_name': 'qwen3_disable_thinking',
                    'environment': None, 'decoding': {'seed': 20261006, 'temperature': 0, 'max_tokens': 512},
                    'policy_sha256': None, 'policy_note': 'Historical runs predate R03 policy; diagnostics only.',
                    'reserved_usd': .05 if name == 'fresh-base' else None, 'reconciled_usd': None,
                    'reservation_scope': 'fresh-base-evaluation-01' if name == 'fresh-base' else 'shared pilot-sft-01 reservation; no per-arm allocation',
                    'historical_manifest_sha256': sha('research/evidence/' + folder + '/manifest.json'),
                    'input_file_sha256': {p: sha(p) for p in (cases_path, graphs_path, freeze_path, predictions_path)}}
        report = evaluate(cases, graphs, predictions, freeze=freeze, manifest=manifest)
        old = historical_evaluate(cases, graphs, predictions, freeze=freeze)
        artifacts[name + '-manifest.json'] = manifest
        artifacts[name + '-report.json'] = report
        artifacts[name + '-historical-comparison.json'] = {
            'historical_successes': old['successes'], 'new_diagnostic_successes': report['metrics']['task_success']['count'],
            'count': old['count'], 'historical_report_rewritten': False}
        reports.append(report)
    artifacts['attempt-inventory.json'] = collect_runs(reports, ['pilot-base', 'pilot-tuned', 'fresh-base'])
    artifacts['promotion-decision.json'] = decide(reports[0], reports[1], phase='validation', regressions={}, policy=POLICY)
    artifacts['provenance.json'] = {'scope': 'historical_diagnostics_only', 'provider_calls': 0,
                                   'policy_sha256': digest(POLICY),
                                   'historical_experiment_reservation_usd': 1.25,
                                   'historical_fresh_evaluation_reservation_usd': .05,
                                   'reconciled_cost_usd': None,
                                   'cost_note': 'Historical holds, not current balance/invoice. Shared experiment reservation not allocated or counted twice.',
                                   'repeatability_experiment_run': False,
                                   'repeatability_note': 'Only synthetic regression fixtures; no remote repeatability claim.',
                                   'code_sha256': {p: sha(p) for p in ('scripts/score_robustness_history.py', 'liftlap/evaluation_v3.py', 'liftlap/promotion.py')}}
    return artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New directory; existing evidence is never overwritten')
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        parser.error('Output already exists; choose a new directory')
    artifacts = generate()
    output.mkdir(parents=True)
    for name, value in artifacts.items():
        # Compact JSON keeps the full per-family metrics without thousands of whitespace lines.
        (output / name).write_text(json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n')
    print(json.dumps({'files':len(artifacts), 'provider_calls':0,
                      'decision':artifacts['promotion-decision.json']['decision']}))


if __name__ == '__main__':
    main()
