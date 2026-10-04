# Corta as folhas da natureza (arvores.png, recursos.png, decoracoes.png = 64bd6836/7463140b/a5bd951c)
# e as texturas (textura-relva/terra/areia = 59dab8f3/2022f0d1/677e1a9c). Gera flora.js para colar no index.html.
from PIL import Image
import numpy as np, json, io, base64
from scipy import ndimage as nd
U='/root/.claude/uploads/415342e0-77a1-5a94-8f8a-71375aa47804/'
SS=2
def cell(f,r,c,rows=2,soft=False):
  im=np.array(Image.open(U+f+'-image.png').convert('RGB')).astype(float);H,W,_=im.shape
  x0=int(c*W/4)+7;x1=int((c+1)*W/4)-7;y0=int(r*H/rows)+7;y1=int((r+1)*H/rows)-7
  cl=im[y0:y1,x0:x1].copy()
  samp=np.concatenate([cl[2:10,2:10].reshape(-1,3),cl[2:10,-10:-2].reshape(-1,3),cl[-10:-2,2:10].reshape(-1,3),cl[-10:-2,-10:-2].reshape(-1,3)]);bg=np.median(samp,0)
  d=np.sqrt(((cl-bg)**2).sum(2))
  mag=(cl[:,:,1]<cl[:,:,0]*.45)&(cl[:,:,1]<cl[:,:,2]*.55)&(cl[:,:,0]>120)&(cl[:,:,2]>100)
  lo,hi=(26,90) if soft else (34,80)
  a=np.clip((d-lo)/(hi-lo),0,1);a[mag&(d<(70 if soft else 110))]=0
  m=a>.4;lab,n=nd.label(m)
  if n:
    sizes=nd.sum(m,lab,range(1,n+1));big=sizes.max();keep=np.zeros_like(m);sl=nd.find_objects(lab)
    for i,sz in enumerate(sizes):
      hh=sl[i][0].stop-sl[i][0].start;ww=sl[i][1].stop-sl[i][1].start
      if (hh<=6 and ww>m.shape[1]*.2) or (ww<=6 and hh>m.shape[0]*.2):continue
      if sz>=max(10,big*.003):keep|=lab==(i+1)
    keep=nd.binary_dilation(keep,iterations=2);a=np.where(keep,a,0)
  rgb=cl.copy();semi=(a>0)&(a<1)
  for ch in range(3):rgb[:,:,ch]=np.where(semi,np.clip((cl[:,:,ch]-bg[ch]*(1-a))/np.maximum(a,.05),0,255),cl[:,:,ch])
  ex=np.clip(np.minimum(rgb[:,:,0],rgb[:,:,2])-rgb[:,:,1]-8,0,None)
  rgb[:,:,0]-=ex*.9;rgb[:,:,2]-=ex*.8
  a=np.where(ex>60,a*.3,a)
  img=Image.fromarray(np.dstack([np.clip(rgb,0,255),a*255]).astype(np.uint8),'RGBA')
  return img.crop(img.getbbox())
T,R,D='64bd6836','7463140b','a5bd951c'
# nome: (folha, linha, coluna, altura alvo em px de jogo, tipo de âncora)
L={
 'oak0':(T,0,0,100,'trunk'),'oak1':(T,0,1,98,'trunk'),'oak2':(T,0,2,94,'trunk'),'oak3':(T,0,3,98,'trunk'),
 'pine0':(T,1,0,116,'trunk'),'pine1':(T,1,1,104,'trunk'),'palm0':(T,1,2,104,'trunk'),'palm1':(T,1,3,104,'trunk'),
 'berry0':(R,0,0,42,'base'),'berry1':(R,0,1,36,'base'),'stone0':(R,0,2,38,'base'),'stone1':(R,0,3,32,'base'),
 'gold0':(R,1,0,38,'base'),'gold1':(R,1,1,30,'base'),'stump':(R,1,2,22,'base'),'logs':(R,1,3,20,'base'),
 'tuft':(D,0,0,17,'base'),'flowerA':(D,0,1,12,'base'),'flowerB':(D,0,2,12,'base'),'shrub':(D,0,3,18,'base'),
 'pebble':(D,1,0,9,'base'),'moss':(D,1,1,12,'base'),'shell':(D,1,2,9,'base'),'reed':(D,1,3,28,'base'),
}
imgs={};meta={}
for k,(f,r,c,h,an) in L.items():
  im=cell(f,r,c,soft=f==D)
  A=np.array(im)[:,:,3]>110;ys,xs=np.nonzero(A);bot=ys.max()
  if an=='trunk':
    band=xs[ys>=bot-max(3,(bot-ys.min())*.04)];ax=(band.min()+band.max())/2
  else:ax=(xs.min()+xs.max())/2
  sc=h*SS/im.height;w2=max(1,round(im.width*sc));h2=h*SS
  im2=im.resize((w2,h2),Image.LANCZOS)
  imgs[k]=im2;meta[k]={'w':w2/SS,'h':h,'ax':round(ax*sc/SS,1),'ay':round((bot+1)*sc/SS,1)}
RW=1024;x=y=rowh=0;W=0
for k,im in sorted(imgs.items(),key=lambda kv:-kv[1].height):
  if x+im.width>RW:x=0;y+=rowh+2;rowh=0
  meta[k]['f']=[x,y,im.width,im.height];x+=im.width+2;rowh=max(rowh,im.height);W=max(W,x)
H=y+rowh;at=Image.new('RGBA',(W,H),(0,0,0,0))
for k,im in imgs.items():at.paste(im,tuple(meta[k]['f'][:2]))
buf=io.BytesIO();at.save(buf,'WEBP',quality=86,method=6);open('flora.webp','wb').write(buf.getvalue());json.dump(meta,open('flora.json','w'))
pv=Image.new('RGBA',(W,H),(93,143,62,255));pv.alpha_composite(at);pv.save('flora_prev.png')
print('atlas',W,H,len(buf.getvalue()))
# texturas sem costura
def seamless(f,n,gain=1,con=1):
  a=np.array(Image.open(U+f+'-image.png').convert('RGB')).astype(float);S=a.shape[0]
  mu=a.mean((0,1));a=np.clip((mu+(a-mu)*con)*gain,0,255)
  b=np.roll(np.roll(a,S//2,0),S//2,1)
  t=np.minimum(np.arange(S),S-1-np.arange(S))/(S*.22);t=np.clip(t,0,1);t=t*t*(3-2*t)
  w=(t[:,None]*t[None,:])[:,:,None]
  o=a*w+b*(1-w)
  im=Image.fromarray(o.astype(np.uint8)).resize((n,n),Image.LANCZOS)
  buf=io.BytesIO();im.save(buf,'WEBP',quality=82,method=6);im.save(f'tex_{f}.png');return buf.getvalue()
tex={k:seamless(f,n,g,cn) for k,(f,n,g,cn) in {'grass':('59dab8f3',512,1.14,1.1),'dirt':('2022f0d1',512,1.0,1.15),'sand':('677e1a9c',512,.97,2.2)}.items()}
for k,v in tex.items():print(k,len(v))
js='const FLORA={ready:false,img:null,tex:{},meta:'+json.dumps(meta,separators=(',',':'))+'};\n'
js+="(()=>{let n=0;const done=()=>{if(++n===4){FLORA.ready=true;floraApply()}};const im=new Image();im.onload=()=>{FLORA.img=im;done()};im.src='data:image/webp;base64,"+base64.b64encode(buf.getvalue()).decode()+"';\n"
for k,v in tex.items():js+=f"  {{const t=new Image();t.onload=()=>{{FLORA.tex.{k}=t;done()}};t.src='data:image/webp;base64,"+base64.b64encode(v).decode()+"';}\n"
js+="})();\n"
open('flora.js','w').write(js);print('js',len(js))
