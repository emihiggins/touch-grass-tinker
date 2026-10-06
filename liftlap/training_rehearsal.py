"""Offline Cookbook batch/cursor rehearsal. No training client or provider calls."""
import argparse
import hashlib
import json
from pathlib import Path

from .corpus import read, label_approved
from .render_audit import COOKBOOK_COMMIT, load_renderer, prepare, sha


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def rehearse(cases, datums, config, provenance, *, start_step=0, expected_plan_sha256=None):
    """Exercise the installed Cookbook loader, not a parallel batching algorithm.

    The cursor proves only which local batches would remain. It does NOT load a
    remote checkpoint or establish optimizer state / exactly-once execution.
    """
    batch_size = config.get('batch_size')
    epochs = config.get('epochs')
    for name, value in [('batch_size', batch_size), ('epochs', epochs)]:
        if type(value) is not int or value <= 0:
            raise ValueError(f'{name} must be a positive integer')
    if not cases or len(cases) != len(datums):
        raise ValueError('Nonempty one-to-one case/Datum mapping required')
    if any(c['split'] not in {'train_candidate', 'train'} for c in cases):
        raise ValueError('Development/test rows cannot enter the training rehearsal')
    ids = [c['id'] for c in cases]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate case IDs')
    if len(cases) % batch_size:
        raise ValueError('Cookbook would drop final rows; choose an explicit divisor batch size')
    if type(start_step) is not int or start_step < 0:
        raise ValueError('Invalid resume cursor')
    if start_step and not expected_plan_sha256:
        raise ValueError('Resume requires the original plan hash')

    from datasets import Dataset
    from tinker_cookbook.supervised.data import SupervisedDatasetFromHFDataset

    dataset = SupervisedDatasetFromHFDataset(
        Dataset.from_dict({'row': list(range(len(cases)))}), batch_size,
        map_fn=lambda row: datums[row['row']],
    )
    datum_hashes = [digest({'input_tokens': d.model_input.to_ints(),
                            'loss_fn_inputs': {k: v.to_torch().tolist()
                                               for k, v in d.loss_fn_inputs.items()}})
                    for d in datums]
    batches = []
    for epoch in range(epochs):
        # Pinned supervised.train.main calls set_epoch(seed=epoch_idx), not the
        # sampling seed or sft-plan.shuffle_seed. Match the actual recipe.
        dataset.set_epoch(seed=epoch)
        seen = []
        for batch_index in range(len(dataset)):
            rows = dataset.shuffle_dataset.select(
                range(batch_index * batch_size, (batch_index + 1) * batch_size)
            )['row']
            actual = dataset.get_batch(batch_index)
            if len(actual) != batch_size or any(d is not datums[i] for d, i in zip(actual, rows)):
                raise ValueError('Cookbook case/Datum order mismatch')
            seen.extend(rows)
            batches.append({'step': len(batches), 'epoch': epoch, 'batch': batch_index,
                            'ids': [ids[i] for i in rows],
                            'datum_sha256': [datum_hashes[i] for i in rows]})
        if sorted(seen) != list(range(len(cases))):
            raise ValueError('Epoch omitted or repeated rows')
    identity = {'config': config, 'provenance': provenance, 'cases_sha256': digest(cases),
                'cookbook_commit': COOKBOOK_COMMIT, 'batches': batches}
    plan_hash = digest(identity)
    if expected_plan_sha256 is not None and expected_plan_sha256 != plan_hash:
        raise ValueError('Resume plan mismatch: inputs, config or datums changed')
    if start_step > len(batches):
        raise ValueError('Resume cursor exceeds planned steps')
    return {'scope': 'offline_candidate_batch_and_cursor_rehearsal_not_training',
            'launch_authorized': False, 'provider_calls': 0, 'checkpoint_loaded': False,
            'plan_sha256': plan_hash, 'provenance': provenance,
            'case_count': len(cases), 'batch_size': batch_size, 'epochs': epochs,
            'steps': len(batches), 'dropped_rows': 0, 'epoch_seed_policy': 'Cookbook epoch index',
            'configured_shuffle_seed_used': False,
            'candidate_labels_human_approved': all(
                c['split'] == 'train' and label_approved(c) for c in cases),
            'batches': batches, 'resume_from_step': start_step,
            'remaining_steps': len(batches) - start_step,
            'remaining_ids': [cid for b in batches[start_step:] for cid in b['ids']]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', default='benchmark/training-candidates.jsonl')
    parser.add_argument('--config', default='training/sft-plan.json')
    parser.add_argument('--prompt', default='benchmark/baseline-prompt-v2.txt')
    parser.add_argument('--tokenizer', default='.tokenizer-qwen3')
    parser.add_argument('--tokenizer-manifest', default='training/tokenizer-manifest.json')
    parser.add_argument('--batch-size', type=int, help='Explicit rehearsal override, not a plan edit')
    parser.add_argument('--start-step', type=int, default=0)
    parser.add_argument('--expected-plan-sha256')
    args = parser.parse_args()
    cases = read(args.cases)
    config = json.loads(Path(args.config).read_text())
    if args.batch_size is not None:
        config['batch_size'] = args.batch_size
    if config['train_on_what'] != 'last_assistant_message':
        parser.error('Rendering mode must match verified plan')
    if (type(config['batch_size']) is not int or config['batch_size'] <= 0
            or not cases or len(cases) % config['batch_size']):
        parser.error('Batch size must divide the nonempty corpus; no dropped rows allowed')
    tokenizer, renderer = load_renderer(args.tokenizer, args.tokenizer_manifest)
    _, datums = prepare(cases, Path(args.prompt).read_text(), tokenizer, renderer, config)
    provenance = {name: sha(path) for name, path in [
        ('cases', args.cases), ('config', args.config), ('prompt', args.prompt),
        ('tokenizer_manifest', args.tokenizer_manifest),
        ('environment_lock', 'training/render-requirements.lock'),
        ('rehearsal_code', __file__), ('render_code', 'liftlap/render_audit.py')]}
    report = rehearse(cases, datums, config, provenance, start_step=args.start_step,
                      expected_plan_sha256=args.expected_plan_sha256)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
