"""Loopback-only simulation with opt-in, budgeted model interpretation."""
import argparse,json,errno,sys
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from scripts.benchmark import validate_intent
from . import fixtures
from . import __version__
from .compact import compact,expand_route
from .core import plan,validate_route,preference_tradeoffs
from .rules import interpret

ROOT=Path(__file__).resolve().parents[1]

def context(mode,minutes=60,difficulty='blue'):
    if mode not in {'synthetic','alpendorf'}:raise ValueError('Unknown terrain')
    if type(minutes) is not int or not 1<=minutes<=1440:raise ValueError('Demo planning horizon is 1–1440 minutes')
    if difficulty not in {'green','blue','red','black'}:raise ValueError('Unknown difficulty')
    g=fixtures.graph() if mode=='synthetic' else json.loads((ROOT/'data/terrain/alpendorf-lab.json').read_text())
    if mode=='synthetic':
        positions={'base':(0,0),'summit':(1,1),'mid':(-0.4,0.3)}
        for n in g['nodes']:n['lon'],n['lat']=positions[n['id']]
        for e in g['edges']:e['geometry']=[positions[e['from']],positions[e['to']]]
        catalog=[{'id':'base','label':'Pine Base','aliases':['the base','Pine']},{'id':'summit','label':'Cedar Summit','aliases':['Cedar','the summit']}]
        start='base'
    else:
        start='2591901158';catalog=[{'id':start,'label':'Obergassalm lower station','aliases':['the base','Obergassalm']}]
    ui={'start_place_id':start,'finish_place_id':start,'start_time':'2027-01-15T10:00:00+01:00','duration_minutes':minutes,'hard_max_difficulty':difficulty}
    return g,ui,catalog

def handle_api(path,payload,model=None):
    g,ui,catalog=context(payload.get('terrain','synthetic'),payload.get('minutes',60),payload.get('difficulty','blue'))
    if path=='/api/interpret':
        text=payload.get('text','')
        if not isinstance(text,str) or len(text)>2000:raise ValueError('Invalid text')
        adapter=payload.get('adapter','rules')
        if adapter=='live':
            if model is None:raise ValueError('Live model disabled. Choose Rules or Recorded example.')
            return model.interpret(text,ui,catalog)
        if adapter=='replay':
            from .app_model import replay
            return replay(ROOT,text,ui,catalog)
        if adapter!='rules':raise ValueError('Unknown interpreter')
        return {**interpret(text,ui,catalog,schema_version=2),'adapter':'rules-v2','notice':'Deterministic rules interpretation; not a model response.'}
    if path!='/api/plan':raise ValueError('Unknown endpoint')
    i=payload['intent'];validate_intent(i,{p['id'] for p in catalog})
    if i['status']!='ready':return {'status':i['status'],'route':None}
    # This fixed-date demo does not accept arbitrary clocks/scenarios.
    if i['start_time']!=ui['start_time']:raise ValueError('Demo start is fixed at 10:00 local, January 15, 2027')
    s=fixtures.scenario(g)
    closed=payload.get('closures','none')
    if closed not in {'none','all_lifts'}:raise ValueError('Unknown closure scenario')
    if closed=='all_lifts':
        for e in g['edges']:
            if e['kind']=='lift':s['edges'][e['id']]['status']='closed'
    cg,cs=compact(g,s,[i['start_place_id'],i['finish_place_id']])
    lab=g['review_status']!='synthetic'
    r=plan(cg,i,cs,lab=lab)
    if r['status']=='ok':
        expanded=expand_route(g,s,cg,r['route'],i,lab=lab)
        r['route']=expanded;r['preference_tradeoffs']=preference_tradeoffs(g,i,expanded);r['validation']=validate_route(g,i,s,expanded,lab=lab)
        edges={e['id']:e for e in g['edges']}
        r['steps']=[]
        labels={'chair':'Summit chairlift','tow':'Practice rope tow','blue':'Blue descent','red':'Red descent','practice':'Practice piste'}
        for eid in expanded['edge_ids']:
            e=edges[eid];name=e.get('name',labels.get(eid,eid));key=(name,e['kind'],e.get('difficulty'))
            if r['steps'] and tuple(r['steps'][-1][k] for k in ('name','kind','difficulty'))==key:
                r['steps'][-1]['seconds']+=e['duration_s']+s['edges'][eid]['queue_s'];r['steps'][-1]['queue_seconds']+=s['edges'][eid]['queue_s'];r['steps'][-1]['edge_ids'].append(eid)
            else:r['steps'].append({'name':name,'kind':e['kind'],'difficulty':e.get('difficulty'),'seconds':e['duration_s']+s['edges'][eid]['queue_s'],'queue_seconds':s['edges'][eid]['queue_s'],'edge_ids':[eid]})
        elapsed=0
        for step in r['steps']:
            step['start_seconds']=elapsed
            elapsed+=step['seconds']
            step['end_seconds']=elapsed
            step['duration_basis']='assumed simulation travel and queue times'
    r['terrain_review']=g['review_status'];r['disclosure']='Simulation only. No live conditions or field verification. Durations are assumptions.'
    return r

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass # no submitted text in access logs
    def send(self,status,data,mime='application/json'):
        raw=json.dumps(data,ensure_ascii=False).encode() if mime=='application/json' else data
        self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; worker-src 'self'; frame-ancestors 'none'")
        self.end_headers();self.wfile.write(raw)
    def allowed_host(self):
        return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
    def do_GET(self):
        if not self.allowed_host():return self.send(403,{'error':'Loopback host required'})
        url=urlsplit(self.path)
        if url.path=='/api/context':
            try:
                mode=parse_qs(url.query).get('terrain',['synthetic'])[0];g,ui,catalog=context(mode)
                return self.send(200,{'graph':g,'ui_context':ui,'catalog':catalog,'live_model_enabled':getattr(self.server,'model',None) is not None,'recorded_model_available':mode=='synthetic' and (ROOT/'demo/model-replay.json').exists()})
            except ValueError:return self.send(422,{'error':'Invalid terrain'})
        allowed={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript; charset=utf-8'),'/style.css':('style.css','text/css; charset=utf-8'),'/research-review.html':('resort-review.html','text/html; charset=utf-8')}
        for asset,mime in [('maplibre-gl-csp.js','text/javascript'),('maplibre-gl-csp-worker.js','text/javascript'),('maplibre-gl.css','text/css')]:allowed['/'+asset]=(asset,mime)
        allowed['/terrain/12/2198/1435.png']=('terrain-12-2198-1435.png','image/png')
        allowed['/terrain-notices.txt']=('terrain-notices.txt','text/plain; charset=utf-8')
        if url.path not in allowed:return self.send(404,{'error':'Not found'})
        name,mime=allowed[url.path];self.send(200,(ROOT/'web'/name).read_bytes(),mime)
    def do_POST(self):
        if not self.allowed_host():return self.send(403,{'error':'Loopback host required'})
        origin=self.headers.get('Origin')
        if origin and origin not in {f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}:return self.send(403,{'error':'Cross-origin requests refused'})
        if self.path not in {'/api/interpret','/api/plan'}:return self.send(404,{'error':'Not found'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=16384:return self.send(413,{'error':'Request too large or empty'})
            payload=json.loads(self.rfile.read(size))
            if not isinstance(payload,dict):raise ValueError('Expected JSON object')
            result=handle_api(self.path,payload,getattr(self.server,'model',None));self.send(200,result)
        except (ValueError,KeyError,TypeError) as e:
            from .app_model import ModelUnavailable
            self.send(422,{'error':str(e) if isinstance(e,ModelUnavailable) else 'Invalid request; check fields and interpreter availability.'})
        except Exception:self.send(500,{'error':'Local planner error; inspect tests before continuing.'})

def port_number(value):
    try: port=int(value)
    except ValueError: raise argparse.ArgumentTypeError("PORT must be a number from 1 to 65535")
    if not 1<=port<=65535: raise argparse.ArgumentTypeError("PORT must be a number from 1 to 65535")
    return port

def main():
    p=argparse.ArgumentParser(description="Start the dependency-free, loopback-only Lift-Lap demo server.")
    p.add_argument("--version",action="version",version=f"%(prog)s {__version__} (offline demo)")
    p.add_argument("--port",type=port_number,default=8767,metavar="PORT",help="loopback port (default: 8767)")
    p.add_argument("--live-model",action="store_true",help=argparse.SUPPRESS);a=p.parse_args()
    try: server=ThreadingHTTPServer(("127.0.0.1",a.port),Handler)
    except OSError as error:
        if error.errno==errno.EADDRINUSE: print(f"Cannot start Lift-Lap: port {a.port} is already in use. Choose another port, for example --port {a.port + 1}.",file=sys.stderr)
        else: print(f"Cannot start Lift-Lap on 127.0.0.1:{a.port}: {error}",file=sys.stderr)
        return 2
    server.timeout=5
    if a.live_model:
        from .app_model import LiveModel
        server.model=LiveModel(ROOT)
    print(f"Lift-Lap {__version__} — offline demo ready",flush=True)
    print(f"Open http://127.0.0.1:{a.port} in a browser on this computer. Press Ctrl-C to stop.",flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
    return 0
if __name__=="__main__":raise SystemExit(main())
