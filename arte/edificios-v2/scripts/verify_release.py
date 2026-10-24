"""Validate selected frames, anchors, flags and runtime byte budgets."""
from pathlib import Path
import json,hashlib,re
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parents[1];P=D/'publicacao';REPO=D.parents[1];WWW=REPO/'www'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(P/'manifest.json');baseline=read(P/'baseline.json');proof=read(P/'atlas.verification.json')
meta=read(WWW/'assets/edificios-v2/bld-v2.json');compat=read(WWW/'assets/edificios-v2/bld-compatibilidade.json')
atlas=Image.open(WWW/'assets/edificios-v2/bld-atlas-v2.webp').convert('RGBA');assert list(atlas.size)==proof['atlasDimensions']
assert sha(WWW/'assets/edificios-v2/bld-atlas-v2.webp')==proof['atlasSha256']
assert len(meta)==37 and set(meta)=={e['key'] for e in manifest['entries']}
flags=[];anchors=[]
for e in manifest['entries']:
    m=meta[e['key']];x,y,w,h=m['f'];assert x>=0 and y>=0 and x+w<=atlas.width and y+h<=atlas.height
    im=Image.open(P/e['path']).convert('RGBA');assert sha(P/e['path'])==e['sha256'] and im.size==(w,h)
    c=np.array(im);rgb=c[:,:,:3]/255;r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];mx=rgb.max(2);dl=mx-rgb.min(2);hue=((r-g)/np.maximum(dl,1e-9)+4)*60
    eligible=((mx==b)|((mx==r)&(b>g)&(r-b<.12)))&(dl>=.06)&(dl/np.maximum(mx,1e-9)>.16)&(hue>188)&(hue<282)&(c[:,:,3]>=8)
    if e['type']=='ruina':assert not eligible.any() and e['flagBounds'] is None
    else:
        x0,y0,x1,y1=e['flagBounds'];mask=np.zeros(eligible.shape,bool);mask[y0:y1,x0:x1]=True
        # Anti-aliasing can leave isolated insignificant pixels; record rather than hide them.
        outside=int((eligible&~mask).sum());flags.append(dict(key=e['key'],outsideFlagTintPixels=outside));assert outside<8,(e['key'],outside)
    n=e['tiles'][0];k=2*n*32*1.03/(m['xr']-m['xl'])*e['artFactor'];CW=np.ceil(w*k)+4;CH=np.ceil(h*k)+4
    if not e['thin']:
        ox=np.floor((m['xl']+m['xr'])/2*k+2+.5);oy=np.floor(m['yb']*k+2-n*16*(1+e['artFactor'])+.5)
        prior=e['expectedLogicalSprite'];d=[abs(CW-prior['CW']),abs(CH-prior['CH']),abs(ox-prior['ox']),abs(oy-prior['oy'])]
        assert max(d)<=2,(e['key'],d);anchors.append(dict(key=e['key'],maxRoundingDifferencePx=max(d)))
jogo=read(P/'jogo.verification.json');assert len(jogo['checks'])==37 and not jogo['errors']
assert all(c['finite'] and c['positive'] and c.get('anchorError',0)<=.51 for c in jogo['checks'])
assert {a['age'] for a in jogo['ages']}=={0,1,2}
for age in (0,1,2):assert (P/'capturas'/f'vila-idade-{age}.png').is_file()
sizes=dict(indexBytes=(WWW/'index.html').stat().st_size,wwwBytes=sum(f.stat().st_size for f in WWW.rglob('*') if f.is_file()),assetsBytes=sum(f.stat().st_size for f in (WWW/'assets').rglob('*') if f.is_file()))
growth={k:round((v/baseline[k]-1)*100,3) for k,v in sizes.items()}
assert growth['indexBytes']<=10
report=dict(status='PASS',managedFrames=37,preservedLegacyFrames=list(compat),baseline=baseline,current=sizes,growthPercent=growth,
            decodedAtlasRgbaBytes=proof['decodedRgbaBytes'],oldDecodedAtlasRgbaBytes=proof['legacyDecodedRgbaBytes'],
            anchorChecks=anchors,flagChecks=flags,realGameChecks=37,agesCaptured=[0,1,2],androidDeviceTested=False)
(P/'integracao.verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(status='PASS',current=sizes,growthPercent=growth,managed=37,preserved=len(compat),realGameChecks=37)))
