"""Fetch only pinned tokenizer assets, never model weights or credentials."""
import hashlib
import json
from pathlib import Path
import urllib.request

def main():
    manifest=json.loads(Path('training/tokenizer-manifest.json').read_text())
    out=Path('.tokenizer-qwen3');out.mkdir(exist_ok=True)
    for name,info in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('Invalid asset filename')
        path=out/name
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==info['sha256']:continue
        url=f'https://huggingface.co/{manifest["model"]}/resolve/{manifest["revision"]}/{name}'
        with urllib.request.urlopen(url,timeout=30) as response:data=response.read(info['bytes']+1)
        if len(data)!=info['bytes'] or hashlib.sha256(data).hexdigest()!=info['sha256']:raise ValueError('Asset checksum mismatch')
        path.write_bytes(data)
    print('Pinned tokenizer assets verified; no model weights downloaded.')

if __name__=='__main__':main()
