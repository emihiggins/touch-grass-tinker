"""Build and verify a credentials-free, allowlisted local demo archive."""
import hashlib,json,os,shutil,socket,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    files=sorted([*ROOT.glob('liftlap/*.py'),*ROOT.glob('web/*'),*ROOT.glob('demo/*')])+[ROOT/'LICENSE',ROOT/'THIRD_PARTY_NOTICES.md',ROOT/'research/maplibre-assets.json',ROOT/'research/elevation-tile.json',ROOT/'data/terrain/alpendorf-source.osm',*[ROOT/'research/evidence/app-integration'/n for n in ['recorded-corrected-desktop.png','mobile.png','print-preview.png','corrected-itinerary.pdf','live-browser.json']],ROOT/'launch-demo.sh',ROOT/'launch-demo.bat',ROOT/'scripts/benchmark.py',ROOT/'data/terrain/alpendorf-lab.json',ROOT/'data/terrain/README.md',ROOT/'data/terrain/LICENSE-ODbL.md']
    files=[p for p in files if p.is_file()]
    assert all(not any(x in p.parts for x in ['runs','.venv-tinker','.tokenizer-qwen3','.git']) for p in files)
    out=ROOT/'dist';out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='liftlap-package-') as temp:
        d=Path(temp)
        for p in files:
            target=d/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        (d/'START-HERE.txt').write_bytes((ROOT/'demo/START-HERE.txt').read_bytes())
        check='''import json,threading,urllib.request
from http.server import ThreadingHTTPServer
from liftlap.server import handle_api,Handler
payload={'adapter':'replay','text':'Only blues, no drag lifts, 45 minutes','minutes':60,'difficulty':'blue'}
r=handle_api('/api/interpret',payload);assert r['adapter']=='qwen3-8b-base-recorded'
i=r['intent'];i['excluded_lift_types']=['platter','rope-tow','t-bar'];i['avoided_lift_types']=[]
assert handle_api('/api/plan',{'intent':i})['status']=='ok'
assert handle_api('/api/plan',{'intent':i,'closures':'all_lifts'})['status']=='no_route'
try:handle_api('/api/interpret',{'adapter':'live'})
except ValueError:pass
else:raise AssertionError('Live mode unexpectedly enabled')
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
    base=f'http://127.0.0.1:{server.server_port}'
    for path,mime in [('/','text/html'),('/app.js','text/javascript'),('/style.css','text/css'),('/maplibre-gl-csp.js','text/javascript'),('/maplibre-gl-csp-worker.js','text/javascript'),('/maplibre-gl.css','text/css'),('/terrain/12/2198/1435.png','image/png'),('/terrain-notices.txt','text/plain')]:
        with urllib.request.urlopen(base+path,timeout=5) as response:
            assert response.status==200 and response.headers['Content-Type'].startswith(mime),(path,response.status)
            assert response.read(),path
    with urllib.request.urlopen(base+'/api/context?terrain=alpendorf',timeout=5) as response:
        context=json.load(response);assert len(context['graph']['edges'])==495
        assert context['live_model_enabled'] is False
finally:
    server.shutdown();server.server_close();thread.join(timeout=5)
print('Isolated offline replay/correction/route/closure and packaged HTTP assets passed')
'''
        env={k:v for k,v in os.environ.items() if k not in ['PYTHONPATH','TINKER_API_KEY']}
        archive=out/'liftlap-local-demo.zip'
        archive_paths=sorted([p.relative_to(ROOT) for p in files]+[Path('START-HERE.txt')])
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for relative in archive_paths:
                info=zipfile.ZipInfo(relative.as_posix(),date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100755 if relative.name=='launch-demo.sh' else 0o100644)<<16;info.create_system=3
                z.writestr(info,(d/relative).read_bytes())
        unpacked=d/'unpacked demo with spaces';unpacked.mkdir()
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None,'Archive CRC check failed'
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
            z.extractall(unpacked)
        subprocess.run([sys.executable,'-c',check],cwd=unpacked,env=env,check=True)
        # Test the actual helper from OUTSIDE the extracted package directory.
        if os.name != 'nt':
            helper=['sh',str(unpacked/'launch-demo.sh')]
        else:
            helper=['cmd','/c',str(unpacked/'launch-demo.bat')]
        version=subprocess.run(helper+['--version'],cwd=d,env=env,capture_output=True,text=True,timeout=10)
        assert version.returncode==0 and 'offline demo' in version.stdout,version.stderr
        invalid=subprocess.run(helper+['--port','0'],cwd=d,env=env,capture_output=True,text=True,timeout=10)
        assert invalid.returncode==2 and '1 to 65535' in invalid.stderr,invalid
        with socket.socket() as listener:
            listener.bind(('127.0.0.1',0));listener.listen(1)
            port=listener.getsockname()[1]
            occupied=subprocess.run(helper+['--port',str(port)],cwd=d,env=env,capture_output=True,text=True,timeout=10)
            assert occupied.returncode==2 and 'already in use' in occupied.stderr,occupied
            assert listener.fileno()!=-1
        report={'scope'  :'isolated_offline_package_not_hosted_deployment','launcher_external_cwd_passed':True,'launcher_platform':sys.platform,'file_count':len(archive_paths),'packaged_http_assets_passed':True,'root_start_guide':True,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'replay_correction_route_closure_passed':True,'live_disabled':True,'contains_credentials':False,'files':[p.as_posix() for p in archive_paths]}
        (ROOT/'research/evidence/app-integration/package-check.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:v for k,v in report.items() if k!='files'}))
if __name__=='__main__':main()
