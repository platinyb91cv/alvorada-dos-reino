from PIL import Image
import numpy as np, json, io
from scipy import ndimage as nd
U='/root/.claude/uploads/415342e0-77a1-5a94-8f8a-71375aa47804/'
SH={'javali':('ec9157ad',2),'gazela':('3fd169c5',2),'peixe':('f8ecf8be',2),'lobo':('353545b3',2),'ovelha':('109ef895',3),'elefante':('63bb10c8',3)}
# quadros: nome -> (linha,coluna)
FR={
 'gazela':{'walk':[(0,0),(0,1),(0,2),(0,3)],'graze':(1,0),'idle':(1,1),'hit':(1,2),'dead':(1,3)},
 'javali':{'idle':(0,0)},
 'lobo':{'walk':[(0,0),(0,1),(0,2),(0,3)],'idle':(1,0),'atk':(1,1),'hit':(1,2),'dead':(1,3)},
 'ovelha':{'walk':[(0,0),(0,1),(0,2),(0,3)],'graze':(1,0),'idle':(1,1),'hit':(1,2),'dead':(1,3)},
 'elefante':{'walk':[(0,0),(0,1),(0,2),(0,3)],'trumpet':(1,0),'atk':(1,1),'hit':(1,2),'dead':(1,3),'idle':(2,0)},
}
PEIXE={'agua':[(0,0),(0,1),(0,2)],'salto':(1,0),'carcaca':(1,1),'carne':(1,2),'cesto':(1,3)}
def cell(f,rows,r,c,soft=False):
  im=np.array(Image.open(U+f+'-image.png').convert('RGB')).astype(float);H,W,_=im.shape
  x0=int(c*W/4)+6;x1=int((c+1)*W/4)-6;y0=int(r*H/rows)+6;y1=int((r+1)*H/rows)-6
  cl=im[y0:y1,x0:x1]
  dark=(cl.mean(2)<90).mean(1)>.6
  for yy in [y for y in np.nonzero(dark)[0] if y<14 or y>cl.shape[0]-15]:
    cl[max(0,yy-2):yy+3]=np.median(cl[2:10,2:10].reshape(-1,3),0)
  samp=np.concatenate([cl[2:10,2:10].reshape(-1,3),cl[2:10,-10:-2].reshape(-1,3),cl[-10:-2,2:10].reshape(-1,3),cl[-10:-2,-10:-2].reshape(-1,3)]);bg=np.median(samp,0)
  d=np.sqrt(((cl-bg)**2).sum(2))
  mag=(cl[:,:,1]<cl[:,:,0]*.45)&(cl[:,:,1]<cl[:,:,2]*.55)&(cl[:,:,0]>120)&(cl[:,:,2]>100)
  lo,hi=(26,90) if soft else (34,80)
  a=np.clip((d-lo)/(hi-lo),0,1);a[mag&(d<(70 if soft else 110))]=0
  m=a>.4;lab,n=nd.label(m)
  if n:
    sizes=nd.sum(m,lab,range(1,n+1));big=sizes.max();keep=np.zeros_like(m)
    sl=nd.find_objects(lab)
    for i,sz in enumerate(sizes):
      hh=sl[i][0].stop-sl[i][0].start;ww=sl[i][1].stop-sl[i][1].start
      if hh<=6 and ww>m.shape[1]*.25:continue   # linha da grelha
      if sz>=max(12,big*.004):keep|=lab==(i+1)
    keep=nd.binary_dilation(keep,iterations=2);a=np.where(keep,a,0)
  rgb=cl.copy();semi=(a>0)&(a<1)
  for ch in range(3):rgb[:,:,ch]=np.where(semi,np.clip((cl[:,:,ch]-bg[ch]*(1-a))/np.maximum(a,.05),0,255),cl[:,:,ch])
  ex=np.clip(np.minimum(rgb[:,:,0],rgb[:,:,2])-rgb[:,:,1]-8,0,None)
  rgb[:,:,0]-=ex*.9;rgb[:,:,2]-=ex*.8
  a=np.where(ex>60,a*.3,a)
  return np.dstack([np.clip(rgb,0,255),a*255]).astype(np.uint8)
imgs={};meta={}
for an,fr in FR.items():
  f,rows=SH[an];names=[]
  flat=[]
  for k,v in fr.items():
    if isinstance(v,list):
      for i,rc in enumerate(v):flat.append((f'{k}{i}',rc))
    else:flat.append((k,v))
  cells={k:cell(f,rows,*rc) for k,rc in flat}
  # caixa comum (mantém posição relativa entre quadros)
  boxes=[Image.fromarray(a,'RGBA').getbbox() for a in cells.values()]
  X0=min(b[0] for b in boxes);Y0=min(b[1] for b in boxes);X1=max(b[2] for b in boxes);Y1=max(b[3] for b in boxes)
  ref=cells['walk0' if 'walk0' in cells else 'idle'];al=ref[:,:,3]>110;ys,xs=np.nonzero(al);foot=ys.max();head=ys.min()
  bot=xs[ys>=foot-(foot-head)*.08];fx=(xs.min()+xs.max())/2
  meta[an]={'fx':round(fx-X0,1),'fy':int(foot-Y0),'h':int(foot-head),'w':int(xs.max()-xs.min()),'f':{}}
  for k,a in cells.items():imgs[(an,k)]=Image.fromarray(a[Y0:Y1,X0:X1],'RGBA')
for k,rc in PEIXE.items():
  f,rows=SH['peixe']
  if isinstance(rc,list):
    for i,x in enumerate(rc):
      a=Image.fromarray(cell(f,rows,*x,soft=True),'RGBA');imgs[('peixe',f'{k}{i}')]=a.crop(a.getbbox())
  else:
    a=Image.fromarray(cell(f,rows,*rc,soft=k=='salto'),'RGBA');imgs[('peixe',k)]=a.crop(a.getbbox())
meta['peixe']={'f':{}}
# escala: reduz tudo a 50% (as folhas são grandes; no jogo os animais têm 20-50 px)
SC=.5
RW=2048;x=y=rowh=0;pos={};W=0
for key,im in imgs.items():
  im=im.resize((max(1,round(im.width*SC)),max(1,round(im.height*SC))),Image.LANCZOS);imgs[key]=im
  if x+im.width>RW:x=0;y+=rowh+2;rowh=0
  pos[key]=(x,y,im.width,im.height);x+=im.width+2;rowh=max(rowh,im.height);W=max(W,x)
H=y+rowh;at=Image.new('RGBA',(W,H),(0,0,0,0))
for key,im in imgs.items():at.paste(im,pos[key][:2]);meta[key[0]]['f'][key[1]]=list(pos[key])
for an in FR:
  for k in ('fx','fy','h','w'):meta[an][k]=round(meta[an][k]*SC,1)
buf=io.BytesIO();at.save(buf,'WEBP',quality=84,method=6);open('fauna.webp','wb').write(buf.getvalue());at.save('fauna.png');json.dump(meta,open('fauna.json','w'))
print(W,H,len(buf.getvalue()));pv=Image.new('RGBA',(W,H),(93,143,62,255));pv.alpha_composite(at);pv.save('fauna_prev.png')
