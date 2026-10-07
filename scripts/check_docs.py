"""Check repository Markdown local file links and current-media provenance."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[];count=0
    for path in ROOT.rglob('*.md'):
        relative=path.relative_to(ROOT)
        if any(x in relative.parts for x in ['.git','.venv','.venv-tinker','.tokenizer-qwen3','runs','dist','node_modules']):continue
        count+=1
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('http:','https:','mailto:','#')):continue
            target=target.split('#')[0].split(' "')[0]
            if target and not (path.parent/target).exists():errors.append(f'{relative}: missing {target}')
    article=(ROOT/'submission/dev-post.md').read_text()
    expected=['What I Built','Demo','Code','How I Built It','Why Does Open Innovation Matter?','My Agent Session','Prize Categories']
    if re.findall(r'^## (.+)$',article,re.M)!=expected:errors.append('Submission template headings/order changed')
    if 'published: false' not in article:errors.append('Submission draft must remain unpublished')
    manifest=json.loads((ROOT/'research/evidence/app-integration/current-media.json').read_text())
    for name,expected in manifest['sha256'].items():
        path=ROOT/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:errors.append('Stale current media/source: '+name)
    if errors:raise SystemExit('\n'.join(errors))
    print(json.dumps({'markdown_files_checked':count,'broken_local_file_links':0,'current_media_hashes':'matched','external_urls_and_markdown_anchors':'not_validated_here'}))
if __name__=='__main__':main()
