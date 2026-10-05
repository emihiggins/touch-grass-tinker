import argparse,json
from pathlib import Path
from . import fixtures
from .core import plan
from .import_osm import import_osm

def main():
    p=argparse.ArgumentParser(description='Offline simulated ski routing; no model calls or live status.')
    p.add_argument('--osm');p.add_argument('--start-node');p.add_argument('--lab',action='store_true')
    a=p.parse_args();g=fixtures.graph();audit=None;i=fixtures.intent()
    if a.osm:
        if not a.start_node:p.error('--start-node required with --osm')
        g,audit=import_osm(Path(a.osm).read_bytes());i['start_place_id']=i['finish_place_id']=a.start_node
    s=fixtures.scenario(g)
    result=plan(g,i,s,lab=a.lab)
    print(json.dumps({'mode':'SIMULATION ONLY','terrain_review':g['review_status'],'import_audit':audit,'result':result},indent=2))

if __name__=='__main__':main()
