# Estábulo: a arte original tinha a base rodada (face esquerda ~0,44 e direita ~0,79 em vez de 2:1, canto da frente 31 px à direita).
# Corrige só os quadros estabulo_0/1/2/n2/n3: corte vertical por coluna (as paredes continuam verticais) + reamostragem
# horizontal por troços, para a base ficar no losango 2:1 com o canto da frente ao centro. Os outros quadros do atlas não mudam.
# Uso: python3 arte/edificios-3d/scripts/corrigir_estabulo.py <repo>
import sys,json,io,hashlib,importlib.util
from pathlib import Path
from PIL import Image
repo=Path(sys.argv[1]);out=repo/'arte/edificios-3d/estabulo-corrigido';out.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('base',repo/'arte/edificios-3d/scripts/corrigir_estabulo_base.py')
html_p=repo/'www/index.html';html=html_p.read_text();i=html.index('const BLD3D_DATA=');j=html.index('\n',i);data=json.loads(html[i+17:html.index(';',i)])
atlas_p=repo/'www/assets/edificios-extra'/data['file'];old=Image.open(atlas_p).convert('RGBA');SC=data['scale']
tiles={n:(old.crop((x,y,x+w,y+h)),ax,ay) for n,(x,y,w,h,ax,ay) in data['frames'].items()}
src=open(spec.origin).read().split('for n in sys.argv[1:]')[0];ns={};exec(src,ns)
for n in ['estabulo_0','estabulo_n2','estabulo_n3']:
  tiles[n][0].save(out/(n+'_original.png'));ns['fix'](str(out/(n+'_original.png')),str(out/(n+'.png')))
fixed={n:Image.open(out/(n+'.png')).convert('RGBA') for n in ['estabulo_0','estabulo_n2','estabulo_n3']}
import numpy as np
def put(name,im):
  a=np.asarray(im.getchannel('A'))>40;bot=[(np.nonzero(a[:,c])[0].max() if a[:,c].any() else -1) for c in range(im.width)];bx=int(np.argmax(bot))  # canto da frente
  tiles[name]=(im,float(bx),round(im.height-(3+3)*16*SC,2))
for n in ['estabulo_0','estabulo_1','estabulo_2']:put(n,fixed['estabulo_0'])
put('estabulo_n2',fixed['estabulo_n2']);put('estabulo_n3',fixed['estabulo_n3'])
order=sorted(tiles,key=lambda n:-tiles[n][0].height);AW=2048;gap=2;x=y=gap;row=0;place={}
for n in order:
  w,h=tiles[n][0].size
  if x+w+gap>AW:x=gap;y+=row+gap;row=0
  place[n]=(x,y);x+=w+gap;row=max(row,h)
at=Image.new('RGBA',(AW,y+row+gap));F={}
for n,(t,ax_,ay_) in tiles.items():p=place[n];at.paste(t,p);F[n]=[p[0],p[1],t.width,t.height,ax_,ay_]
buf=io.BytesIO();at.save(buf,'WEBP',lossless=True,quality=100,method=6);b=buf.getvalue();atlas_p.write_bytes(b)
data['atlasSha256']=hashlib.sha256(b).hexdigest();data['frames']=dict(sorted(F.items()))
html=html[:i]+'const BLD3D_DATA='+json.dumps(data,separators=(',',':'))+';'+html[j:];html_p.write_text(html)
vp=repo/'arte/edificios-3d/verification.json';v=json.loads(vp.read_text());v['atlasSha256']=data['atlasSha256'];vp.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
print(at.size,len(b),len(F))
