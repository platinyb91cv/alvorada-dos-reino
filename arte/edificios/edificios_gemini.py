# Edifícios pintados no Gemini (gemini/<tipo><idade>.png): recorta o magenta, mede a base e junta ao atlas dos edifícios do jogo.
# uso: python3 centro_gemini.py ../../www/index.html   (lê o atlas atual do index.html e escreve-o de volta)
import re,io,sys,json,base64,colorsys
import numpy as np
from PIL import Image
from scipy import ndimage as nd
TW=420 # largura final de um edifício 3x3 no atlas (px) — chega para o ecrã (3 casas = ~400 px a SS 2); 2x2 -> 2/3
def cut(path,TW=TW):
  cl=np.array(Image.open(path).convert('RGB')).astype(float)
  bg=np.array([255.,0.,255.])
  samp=np.concatenate([cl[2:12,2:12].reshape(-1,3),cl[2:12,-12:-2].reshape(-1,3)]);bg=np.median(samp,0)
  d=np.sqrt(((cl-bg)**2).sum(2))
  a=np.clip((d-60)/(140-60),0,1)
  # sombras arroxeadas que o Gemini pinta sobre o magenta -> transparentes
  r0,g0,b0=cl[:,:,0],cl[:,:,1],cl[:,:,2];purple=(r0>g0*1.3+12)&(b0>g0*1.3+12)&(np.abs(r0-b0)<45)&(b0<r0*1.25)
  a=np.where(purple,0,a)
  m=a>.5;lab,n=nd.label(m);sizes=nd.sum(m,lab,range(1,n+1));big=sizes.max();keep=np.zeros_like(m)
  for i,sz in enumerate(sizes):
    if sz>=60:keep|=lab==(i+1)
  keep=nd.binary_fill_holes(keep);keep=nd.binary_dilation(keep,iterations=1);a=np.where(keep,a,0)
  rgb=cl.copy();semi=(a>0)&(a<1)
  for ch in range(3):rgb[:,:,ch]=np.where(semi,np.clip((cl[:,:,ch]-bg[ch]*(1-a))/np.maximum(a,.05),0,255),cl[:,:,ch])
  # despill: tira o magenta das bordas (vermelho+azul acima do verde)
  ex=np.clip(np.minimum(rgb[:,:,0],rgb[:,:,2])-rgb[:,:,1]-8,0,None);edge=nd.binary_dilation(a<.9,iterations=3)
  f=np.where(edge,1.0,.4);rgb[:,:,0]-=ex*f;rgb[:,:,2]-=ex*f*.85;a=np.where(edge&(ex>60),a*.3,a)
  # ardósia/pedra azulada -> cinzento (só os panos azul-real mudam com a cor da equipa)
  r,g,b=[np.clip(rgb[:,:,i],0,255)/255 for i in range(3)];M=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b);dl=M-mn
  sat=np.where(M>0,dl/np.maximum(M,1e-6),0);blu=(b>=r)&(b>=g)&(dl>.02)&(sat<.42)
  L=(r*.3+g*.59+b*.11)
  for i,(ch) in enumerate((r,g,b)):
    tgt=L*np.array([1.0,1.0,1.04])[i];rgb[:,:,i]=np.where(blu,(ch*.25+tgt*.75)*255,rgb[:,:,i])
  out=np.dstack([np.clip(rgb,0,255),a*255]).astype(np.uint8);img=Image.fromarray(out,'RGBA');img=img.crop(img.getbbox())
  k=TW/img.width;img=img.resize((TW,round(img.height*k)),Image.LANCZOS)
  al=np.array(img)[:,:,3]>110;ys,xs=np.nonzero(al);yb=ys.max();h=yb-ys.min()
  low=ys>ys.min()+h*.45;xl=xs[low].min();xr=xs[low].max();yl=ys[low][xs[low]==xl].mean()
  return img,dict(xl=int(xl),xr=int(xr),yb=int(yb),yl=float(yl))
html=sys.argv[1];s=open(html,encoding='utf-8').read()
i=s.index('const BLDART=');j=s.index("im.src='data:image/webp;base64,",i)+len("im.src='data:image/webp;base64,");k2=s.index("'",j)
mm=re.search(r'(const BLDART=\{wide:true,ready:false,img:null,meta:)(\{.*?\}\})(,)',s);meta=json.loads(mm.group(2))
at=Image.open(io.BytesIO(base64.b64decode(s[j:k2]))).convert('RGBA')
# o atlas pode já ter os centros do Gemini (linha de baixo): volta a cortar a partir da altura original
import glob,os
# todos os edifícios pintados no Gemini: gemini/<tipo><idade>.png (ex.: quartel1.png, torre3.png)
SIZE={'casa':2,'armazem':2,'ferreiro':2,'torre':2,'doca':2,'maravilha':4}
items=[]
for f in sorted(glob.glob('gemini/*.png')):
  n=os.path.basename(f)[:-4];m2=re.match(r'([a-z]+)(\d)$',n)
  if not m2:continue
  t,a=m2.group(1),m2.group(2);sz=SIZE.get(t,3)
  im,mt=cut(f,TW=round(TW*sz/3));items.append((t+'|'+a,im,mt))
new={k for k,_,_ in items}
# células antigas que continuam em uso (muralhas, portões, doca, quinta, ruínas...)
for k,v in list(meta.items()):
  if k in new:continue
  x,y,w,h=v['f'];items.append((k,at.crop((x,y,x+w,y+h)),{kk:vv for kk,vv in v.items() if kk!='f'}))
meta={}
# empacotar em prateleiras (mais altos primeiro)
items.sort(key=lambda it:-it[1].height)
RW=2048;x=0;y=0;rowh=0;pos=[]
for k,im,mt in items:
  if x+im.width>RW:x=0;y+=rowh+2;rowh=0
  pos.append((x,y));x+=im.width+2;rowh=max(rowh,im.height)
W=RW;H=y+rowh
na=Image.new('RGBA',(W,H),(0,0,0,0))
for (k,im,mt),(px,py) in zip(items,pos):
  na.paste(im,(px,py));mt['f']=[px,py,im.width,im.height];meta[k]=mt
print('Gemini:',sorted(new))
buf=io.BytesIO();na.save(buf,'WEBP',quality=84,method=6);b64=base64.b64encode(buf.getvalue()).decode()
s=s[:j]+b64+s[k2:]
s=re.sub(r'(const BLDART=\{wide:true,ready:false,img:null,meta:)(\{.*?\}\})(,)',lambda q:q.group(1)+json.dumps(meta)+q.group(3),s,count=1)
open(html,'w',encoding='utf-8').write(s);na.save('bld_atlas_gemini.png')
print('atlas',na.size,len(buf.getvalue())//1024,'KB')
