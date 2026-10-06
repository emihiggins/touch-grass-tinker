"""Loopback-only offline demo. Not a production web server or hosted model endpoint."""
import argparse,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from scripts.benchmark import validate_intent
from . import fixtures
from .compact import compact,expand_route
from .core import plan,validate_route
from .rules import interpret

ROOT=Path(__file__).resolve().parents[1]

def context(mode,minutes=60,difficulty='blue'):
    if mode not in {'synthetic','alpendorf'}:raise ValueError('Unknown terrain')
    if type(minutes) is not int or not 15<=minutes<=240:raise ValueError('Minutes must be 15–240')
    if difficulty not in {'blue','red','black'}:raise ValueError('Unknown difficulty')
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

def handle_api(path,payload):
    g,ui,catalog=context(payload.get('terrain','synthetic'),payload.get('minutes',60),payload.get('difficulty','blue'))
    if path=='/api/interpret':
        return interpret(payload.get('text',''),ui,catalog)
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
        r['route']=expanded;r['validation']=validate_route(g,i,s,expanded,lab=lab)
        edges={e['id']:e for e in g['edges']}
        r['steps']=[]
        labels={'chair':'Summit chairlift','tow':'Practice rope tow','blue':'Blue descent','red':'Red descent','practice':'Practice piste'}
        for eid in expanded['edge_ids']:
            e=edges[eid];name=e.get('name',labels.get(eid,eid));key=(name,e['kind'],e.get('difficulty'))
            if r['steps'] and tuple(r['steps'][-1][k] for k in ('name','kind','difficulty'))==key:
                r['steps'][-1]['seconds']+=e['duration_s']
            else:r['steps'].append({'name':name,'kind':e['kind'],'difficulty':e.get('difficulty'),'seconds':e['duration_s']})
    r['terrain_review']=g['review_status'];r['adapter']='rules-v1';r['disclosure']='Simulation only. No Tinker model, live conditions or field verification. Durations are assumptions.'
    return r

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass # no submitted text in access logs
    def send(self,status,data,mime='application/json'):
        raw=json.dumps(data,ensure_ascii=False).encode() if mime=='application/json' else data
        self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers();self.wfile.write(raw)
    def allowed_host(self):
        return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
    def do_GET(self):
        if not self.allowed_host():return self.send(403,{'error':'Loopback host required'})
        url=urlsplit(self.path)
        if url.path=='/api/context':
            try:
                mode=parse_qs(url.query).get('terrain',['synthetic'])[0];g,ui,catalog=context(mode)
                return self.send(200,{'graph':g,'ui_context':ui,'catalog':catalog})
            except ValueError:return self.send(422,{'error':'Invalid terrain'})
        allowed={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript; charset=utf-8'),'/style.css':('style.css','text/css; charset=utf-8')}
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
            result=handle_api(self.path,payload);self.send(200,result)
        except (ValueError,KeyError,TypeError):self.send(422,{'error':'Invalid request; check fields and supported grammar.'})
        except Exception:self.send(500,{'error':'Local planner error; inspect tests before continuing.'})

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8767);a=p.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler);server.timeout=5
    print(f'Local simulation: http://127.0.0.1:{a.port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
