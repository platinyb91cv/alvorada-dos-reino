"""Rebuild the new atlas and integrate it, preserving legacy art and metadata."""
from pathlib import Path
import json,math,hashlib,re
from PIL import Image
D=Path(__file__).resolve().parents[1];REPO=D.parents[1];OUT=D/'publicacao'
data=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'));entries=data['entries']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
legacy=Image.open(OUT/'legacy/bld-atual.webp').convert('RGBA')
legacy_meta=json.loads((OUT/'legacy/bld-atual.json').read_text(encoding='utf-8'))
extra=[]
for key,m in legacy_meta.items():
    if key not in {e['key'] for e in entries}:
        extra.append(dict(key=key,meta=m))
assert {e['key'] for e in extra}=={'mercado|1','mercado|2','oficina|2'}
all_entries=entries+extra

def shelves(width):
    rows=[];positions={}
    for e in sorted(all_entries,key=lambda e:(-e['meta']['f'][3],-e['meta']['f'][2])):
        w,h=e['meta']['f'][2:];w+=4;h+=4
        candidates=[r for r in rows if r['x']+w<=width and h<=r['h']]
        if candidates:r=min(candidates,key=lambda r:width-r['x']-w)
        else:r={'x':0,'y':sum(t['h'] for t in rows),'h':h};rows.append(r)
        positions[e['key']]=[r['x']+2,r['y']+2];r['x']+=w
    return width,sum(r['h'] for r in rows),positions

W,H,positions=min((shelves(w) for w in (1024,1536,2048)),key=lambda v:v[0]*v[1])
atlas=Image.new('RGBA',(W,H));meta={}
for e in all_entries:
    if 'path' in e:im=Image.open(OUT/e['path']).convert('RGBA')
    else:
        sx,sy,iw,ih=e['meta']['f'];im=legacy.crop((sx,sy,sx+iw,sy+ih))
    x,y=positions[e['key']]
    atlas.paste(im,(x,y));m=dict(e['meta']);m['f']=[x,y,im.width,im.height];meta[e['key']]=m
runtime=REPO/'www/assets/edificios-v2';runtime.mkdir(parents=True,exist_ok=True)
target=runtime/'bld-atlas-v2.webp';atlas.save(target,'WEBP',quality=86,method=6,exact=True)
managed={e['key']:meta[e['key']] for e in entries}
preserved={e['key']:meta[e['key']] for e in extra}
(runtime/'bld-v2.json').write_text(json.dumps(managed,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(OUT/'bld-v2.json').write_text(json.dumps(managed,ensure_ascii=False,indent=2),encoding='utf-8')
(runtime/'bld-compatibilidade.json').write_text(json.dumps(preserved,separators=(',',':')),encoding='utf-8')
html=REPO/'www/index.html';raw=html.read_bytes().decode('utf-8-sig');lines=raw.splitlines(keepends=True)
for i,line in enumerate(lines):
    end='\r\n' if line.endswith('\r\n') else '\n'
    if line.startswith('const BLDART='):
        lines[i]='const BLDART={wide:true,ready:false,img:null,meta:'+json.dumps(meta,separators=(',',':'))+',teams:new Map(),cache:new Map()};'+end
    elif 'BLDART.img=im' in line and 'im.src=' in line:
        lines[i]=re.sub(r"im.src='[^']+'", "im.src='assets/edificios-v2/bld-atlas-v2.webp'",line,count=1)
html.write_bytes(''.join(lines).encode('utf-8'))
old=Image.open(OUT/'legacy/bld-atual.webp')
report=dict(keys=len(meta),managedKeys=len(managed),preservedLegacyKeys=list(preserved),atlasDimensions=[W,H],atlasBytes=target.stat().st_size,atlasSha256=sha(target),
            decodedRgbaBytes=W*H*4,legacyDecodedRgbaBytes=old.width*old.height*4,
            metadataSha256=sha(runtime/'bld-v2.json'),indexBytes=html.stat().st_size,indexSha256=sha(html))
(OUT/'atlas.verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
