"""Remove isolated resampling tint flecks outside the approved cloth masks."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parents[1]/'publicacao'
manifest=json.loads((D/'manifest.json').read_text(encoding='utf-8'))
for e in manifest['entries']:
    file=D/e['path'];a=np.array(Image.open(file).convert('RGBA')).astype(float);c=a[:,:,:3]/255
    r,g,b=c[:,:,0],c[:,:,1],c[:,:,2];mx=c.max(2);dl=mx-c.min(2);h=((r-g)/np.maximum(dl,1e-9)+4)*60
    eligible=((mx==b)|((mx==r)&(b>g)&(r-b<.12)))&(dl>=.06)&(dl/np.maximum(mx,1e-9)>.16)&(h>188)&(h<282)&(a[:,:,3]>=8)
    inside=np.zeros(eligible.shape,bool)
    if e['flagBounds']:
        x0,y0,x1,y1=e['flagBounds'];inside[y0:y1,x0:x1]=True
    clean=eligible&~inside;lum=a[:,:,0]*.299+a[:,:,1]*.587+a[:,:,2]*.114
    for channel,factor in enumerate((1.02,1.,.96)):a[:,:,channel]=np.where(clean,np.minimum(255,lum*factor),a[:,:,channel])
    a[a[:,:,3]==0,:3]=0;Image.fromarray(a.astype('uint8')).save(file,optimize=True)
    e['resamplingTintFlecksNeutralized']=int(clean.sum());e['sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS tint masks:',len(manifest['entries']))
