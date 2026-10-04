from PIL import Image
import numpy as np
from scipy import ndimage as nd
im=np.array(Image.open('sheet.png').convert('RGB')).astype(float)
BOX={'v_ocioso':(440,112,494,240),'v_madeira':(507,112,571,240),'v_pedra':(584,108,646,240),'v_ouro':(660,112,721,240),'v_agricultura':(734,112,804,239),'v_caca':(807,112,878,241),'v_construcao':(880,112,954,240),'v_transporte':(959,112,1026,236),
 'barcoPesca':(1003,607,1091,738),'transporte':(1102,610,1201,736),'gale':(1206,630,1320,746),'incendiario':(1330,617,1406,741),'navioPesado':(1412,592,1509,746)}
for k,(x0,y0,x1,y1) in BOX.items():
  c=im[y0:y1,x0:x1];H,W,_=c.shape
  rb=np.array(Image.open(f'cut_{k}.png'))[:,:,3].astype(float)/255
  # fundo local: plano ajustado às bordas (gradiente suave)
  border=np.concatenate([c[0],c[-1],c[:,0],c[:,-1]])
  bgc=np.median(border,axis=0)
  # luminância e croma em relação ao fundo
  d=np.sqrt(((c-bgc)**2).sum(2))
  lum=c.mean(2);blum=bgc.mean()
  sat=c.max(2)-c.min(2);bsat=bgc.max()-bgc.min()
  score=np.maximum(d, 0)
  ck=np.clip((score-11)/(26-11),0,1)
  # sombras projectadas: mais escuras que o fundo e sem cor → fora
  shadow=(lum<blum-2)&(sat<bsat+10)
  ck[shadow]*=0.0
  ck[(rb<.5)&(lum<blum+14)&(sat<bsat+16)]=0
  a=np.maximum(rb,ck)
  if k.startswith('v_'):
    low=np.zeros_like(a,bool);low[int(H*.5):]=True
    a[low&(lum<blum+18)&(sat<bsat+14)]=0
  m=a>.5
  filled=nd.binary_fill_holes(m);holes=filled&~m;hl,hn=nd.label(holes)
  if hn:
    hs=nd.sum(holes,hl,range(1,hn+1))
    for i,sz in enumerate(hs):
      if sz<=30:m|=hl==(i+1)
  lab,n=nd.label(m);sizes=nd.sum(m,lab,range(1,n+1))
  keep=np.zeros_like(m)
  big=max(sizes) if n else 0
  for i,sz in enumerate(sizes):
    if sz>=max(60,big*.08):keep|=lab==(i+1)
  # alfa final: dentro da máscara (com buracos preenchidos) opaco, borda suave
  inner=nd.binary_erosion(keep,iterations=1)
  alpha=np.where(inner,1.0,np.where(keep,np.maximum(a,.55),0))
  out=np.dstack([c,alpha*255]).clip(0,255).astype(np.uint8)
  Image.fromarray(out,'RGBA').save(f'cut2_{k}.png')
  print(k,n,int(keep.sum()))
