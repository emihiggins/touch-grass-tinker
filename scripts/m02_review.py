"""Offline M02 review report/export; never calls a provider or approves labels."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from liftlap.corpus import read
from liftlap.corpus_m02 import approved_export, iteration_manifest, source_lineage_overlaps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet')
    parser.add_argument('--source', action='append', default=[])
    parser.add_argument('--manifest')
    parser.add_argument('--export')
    parser.add_argument('--prompt', default='benchmark/v2/baseline-prompt.txt')
    args = parser.parse_args()
    cases = read(args.packet)
    sources = [row for path in args.source for row in read(path)]
    report = iteration_manifest(cases)
    report['manifest_version'] = 'm02-cli-3'
    report['boundaries']['export_requires'] = 'current M02 approvals, intent-v2 semantic validity and explicit source corpus audit'
    report['training_export_supported'] = True
    report['status'] = 'diagnostic report; use export gate for eligibility'
    report['limitations'] = ['Supplied source files only; completeness requires review.', 'No automatic label approval or split freeze.', 'Declared families and lexical similarity do not prove semantic independence.']
    overlaps = source_lineage_overlaps(cases, sources)
    report['full_source_overlap'] = overlaps
    if overlaps:
        report['blocking_errors'] = sorted(set(report['blocking_errors'] + ['full-source overlap: ' + item for item in overlaps]))
    report['source_sha256'] = {path: hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in args.source}
    report['source_audit_scope'] = 'explicit supplied files only; completeness must be reviewed'
    report['packet_sha256'] = hashlib.sha256(Path(args.packet).read_bytes()).hexdigest()
    if args.export:
        payload = ''.join(json.dumps(row, sort_keys=True) + '\n' for row in approved_export(cases, Path(args.prompt).read_text(), source_cases=sources))
        Path(args.export).write_text(payload)
        report['export_count'] = len(payload.splitlines())
        report['export_sha256'] = hashlib.sha256(payload.encode()).hexdigest()
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    if report['blocking_errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
