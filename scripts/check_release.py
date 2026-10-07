"""Offline release verification. Never creates provider calls or publishes anything."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main():
    subprocess.run([sys.executable,'scripts/check_docs.py'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'scripts/check_assets.py'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-q'],cwd=ROOT,check=True)
    from liftlap.corpus import read
    from liftlap.evaluation_v2 import evaluate
    p=ROOT/'benchmark/v2/final-review'
    result=evaluate(read(p/'cases.jsonl'),json.loads((p/'graphs.json').read_text()),read(ROOT/'research/evidence/fresh-base-evaluation/predictions.jsonl'),freeze=json.loads((p/'freeze.json').read_text()))
    assert result['successes']==13 and result['count']==16
    assert (ROOT/'LICENSE').read_text().startswith('MIT License\n')
    hashes=[]
    for _ in range(2):
        subprocess.run([sys.executable,'scripts/package_demo.py'],cwd=ROOT,check=True)
        hashes.append(hashlib.sha256((ROOT/'dist/liftlap-local-demo.zip').read_bytes()).hexdigest())
    assert hashes[0]==hashes[1],'Archive is not deterministic'
    print(json.dumps({'offline_checks':'passed','saved_base_result':'13/16','deterministic_archive_sha256':hashes[0],'provider_calls':0}))
if __name__=='__main__':main()
