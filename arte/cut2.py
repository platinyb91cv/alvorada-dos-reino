from PIL import Image
import numpy as np
from scipy import ndimage as nd
im=np.array(Image.open('sheet.png').convert('RGB')).astype(float)
BOX={'guerreiro':(25,348,112,507),'espadachim':(113,350,204,507),'lanceiro':(215,348,297,508),'arqueiro':(313,355,382,507),'besteiro':(410,370,490,504),
 'cavaleiro':(524,342,644,505),'cavPesada':(650,342,760,510),'cavArqueira':(765,344,890,508),
 'ariete':(904,352,1020,508),'catapulta':(1032,357,1188,508),'trebuchet':(1192,322,1362,524),'sacerdote':(1392,350,1502,515)}
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
  a=np.maximum(rb,ck)
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
