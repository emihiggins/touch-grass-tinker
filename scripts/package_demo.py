"""Build and verify a credentials-free, allowlisted local demo archive."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    files=sorted([*ROOT.glob('liftlap/*.py'),*ROOT.glob('web/*'),*ROOT.glob('demo/*')])+[ROOT/'scripts/benchmark.py',ROOT/'data/terrain/alpendorf-lab.json',ROOT/'data/terrain/README.md',ROOT/'data/terrain/LICENSE-ODbL.md']
    files=[p for p in files if p.is_file()]
    assert all(not any(x in p.parts for x in ['runs','.venv-tinker','.tokenizer-qwen3','.git']) for p in files)
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='liftlap-package-') as temp:
        d=Path(temp)
        for p in files:
            target=d/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        check='''import json
from liftlap.server import handle_api
payload={'adapter':'replay','text':'Only blues, no drag lifts, 45 minutes','minutes':60,'difficulty':'blue'}
r=handle_api('/api/interpret',payload);assert r['adapter']=='qwen3-8b-base-recorded'
i=r['intent'];i['excluded_lift_types']=['platter','rope-tow','t-bar'];i['avoided_lift_types']=[]
assert handle_api('/api/plan',{'intent':i})['status']=='ok'
assert handle_api('/api/plan',{'intent':i,'closures':'all_lifts'})['status']=='no_route'
try:handle_api('/api/interpret',{'adapter':'live'})
except ValueError:pass
else:raise AssertionError('Live mode unexpectedly enabled')
print('Isolated offline replay/correction/route/closure preflight passed')
'''
        env={k:v for k,v in os.environ.items() if k not in ['PYTHONPATH','TINKER_API_KEY']}
        subprocess.run([sys.executable,'-c',check],cwd=d,env=env,check=True)
        archive=out/'liftlap-local-demo.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for p in files:z.write(d/p.relative_to(ROOT),p.relative_to(ROOT))
        report={'scope':'isolated_offline_package_not_hosted_deployment','file_count':len(files),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'replay_correction_route_closure_passed':True,'live_disabled':True,'contains_credentials':False,'files':[str(p.relative_to(ROOT)) for p in files]}
        (ROOT/'research/evidence/app-integration/package-check.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:v for k,v in report.items() if k!='files'}))
if __name__=='__main__':main()
