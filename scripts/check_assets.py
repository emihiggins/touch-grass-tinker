"""Offline checks of upstream asset fingerprints and derived dataset manifests."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def verify_asset(root,name,expected):
 path=root/name
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Asset hash mismatch: '+str(name))

def check(root=ROOT):
 manifest=json.loads((root/'research/maplibre-assets.json').read_text())
 for asset in manifest['assets']:verify_asset(root,asset['path'],asset['sha256'])
 tile=json.loads((root/'research/elevation-tile.json').read_text());tile_path='web/terrain-12-2198-1435.png';verify_asset(root,tile_path,tile['sha256'])
 raw=(root/tile_path).read_bytes()
 if raw[:8]!=b'\x89PNG\r\n\x1a\n' or list(struct.unpack('>II',raw[16:24]))!=tile['dimensions']:raise ValueError('Elevation image shape changed')
 graph=json.loads((root/'data/terrain/alpendorf-lab.json').read_text());west,south,east,north=tile['bounds']
 if not all(west<=x<=east and south<=y<=north for e in graph['edges'] for x,y in e['geometry']):raise ValueError('Terrain tile no longer covers the Alpendorf graph')
 snapshots=0
 for p in sorted((root/'data/terrain').glob('*/manifest.json')):
  m=json.loads(p.read_text());verify_asset(p.parent,'source.osm',m['sanitized_sha256']);verify_asset(p.parent,'graph.json',m['graph_sha256']);snapshots+=1
 return {'upstream_assets_verified':len(manifest['assets']),'elevation_hash_and_coverage_verified':True,'derived_snapshot_manifests_verified':snapshots,'network_requests':0}
if __name__=='__main__':print(json.dumps(check()))
