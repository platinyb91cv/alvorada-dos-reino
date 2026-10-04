from PIL import Image
import numpy as np, json, io
from scipy import ndimage as nd
U='/root/.claude/uploads/415342e0-77a1-5a94-8f8a-71375aa47804/'
S={'extra':'61098560','pedra':'6d6c2869','bronze':'cc1f3692','ferro':'8080a8cc','def':'293872f9','est':'37de6fbf'}
# chave -> (folha, linha, coluna)
MAP={
 'centro|0':('pedra',0,0),'casa|0':('pedra',0,1),'armazem|0':('pedra',0,2),'quartel|0':('pedra',0,3),'arquearia|0':('pedra',1,0),'doca|0':('pedra',1,1),'torre|1':('pedra',1,2),'quinta|0':('pedra',1,3),
 'centro|1':('bronze',0,0),'casa|1':('bronze',0,1),'armazem|1':('bronze',0,2),'quartel|1':('bronze',0,3),'arquearia|1':('bronze',1,0),'estabulo|1':('bronze',1,1),'ferreiro|1':('bronze',1,2),'templo|1':('bronze',1,3),
 'centro|2':('ferro',0,0),'casa|2':('ferro',0,1),'armazem|2':('ferro',0,2),'quartel|2':('ferro',0,3),'arquearia|2':('ferro',1,0),'estabulo|2':('ferro',1,1),'ferreiro|2':('ferro',1,2),'templo|2':('ferro',1,3),
 'torre|2':('def',0,0),'torre|3':('def',0,1),'oficina|1':('def',0,2),'maravilha|2':('def',0,3),'portaoMadeira|0':('def',1,0),'portaoPedra|0':('def',1,1),'muralhaMadeira|0':('def',1,2),'muralhaPedra|0':('def',1,3),
 'quinta|1':('extra',1,2),'estabulo|0':('extra',0,3),'ferreiro|0':('extra',1,0),
 'ruina|0':('est',1,2),'ruina|1':('est',1,3),
}
def cell(f,r,c):
  im=np.array(Image.open(U+S[f]+'-image.png').convert('RGB')).astype(float);H,W,_=im.shape
  x0=int(c*W/4)+6;x1=int((c+1)*W/4)-6;y0=int(r*H/2)+6;y1=int((r+1)*H/2)-6
  cl=im[y0:y1,x0:x1]
  samp=np.concatenate([cl[2:10,2:10].reshape(-1,3),cl[2:10,-10:-2].reshape(-1,3),cl[-10:-2,2:10].reshape(-1,3),cl[-10:-2,-10:-2].reshape(-1,3)]);bg=np.median(samp,0)
  d=np.sqrt(((cl-bg)**2).sum(2))
  mag=(cl[:,:,1]<cl[:,:,0]*.42)&(cl[:,:,1]<cl[:,:,2]*.5)&(cl[:,:,0]>120)&(cl[:,:,2]>100)
  a=np.clip((d-34)/(80-34),0,1);a[mag&(d<110)]=0
  # sombras arroxeadas fora da base: escuro com tom magenta -> transparente
  purple=(cl[:,:,0]>cl[:,:,1]*1.35)&(cl[:,:,2]>cl[:,:,1]*1.35)&(cl.mean(2)<150)
  a[purple]=np.minimum(a[purple],.0)
  m=a>.5;lab,n=nd.label(m)
  if n:
    sizes=nd.sum(m,lab,range(1,n+1));big=sizes.max();keep=np.zeros_like(m)
    for i,sz in enumerate(sizes):
      if sz>=max(30,big*.01):keep|=lab==(i+1)
    keep=nd.binary_fill_holes(keep);keep=nd.binary_dilation(keep,iterations=1);a=np.where(keep,a,0)
  rgb=cl.copy();semi=(a>0)&(a<1)
  for ch in range(3):rgb[:,:,ch]=np.where(semi,np.clip((cl[:,:,ch]-bg[ch]*(1-a))/np.maximum(a,.05),0,255),cl[:,:,ch])
  pink=(rgb[:,:,0]>150)&(rgb[:,:,2]>120)&(rgb[:,:,1]<.5*np.minimum(rgb[:,:,0],rgb[:,:,2]))
  a=np.where(pink,a*.0,a)
  # tirar o tom magenta que fica nas bordas (despill): reduz vermelho+azul acima do verde
  ex=np.clip(np.minimum(rgb[:,:,0],rgb[:,:,2])-rgb[:,:,1]-6,0,None)
  edge=(a<.98)|nd.binary_dilation(a<.5,iterations=2)
  f=np.where(edge,1.0,.55)
  rgb[:,:,0]-=ex*f;rgb[:,:,2]-=ex*f*.8
  a=np.where(edge&(ex>40),a*.35,a)
  out=np.dstack([np.clip(rgb,0,255),a*255]).astype(np.uint8);img=Image.fromarray(out,'RGBA');bb=img.getbbox();img=img.crop(bb)
  # base em losango: extremos esquerdo/direito na metade de baixo e ponto mais baixo
  al=np.array(img)[:,:,3]>110;ys,xs=np.nonzero(al);yb=ys.max();h=yb-ys.min()
  low=ys>ys.min()+h*.45;xl=xs[low].min();xr=xs[low].max()
  # linha onde está o canto esquerdo (para o centro do losango)
  yl=ys[low][xs[low]==xl].mean()
  return img,dict(xl=int(xl),xr=int(xr),yb=int(yb),yl=float(yl))
imgs={};meta={}
for k,(f,r,c) in MAP.items():
  img,mm=cell(f,r,c);imgs[k]=img;meta[k]=mm
# atlas
RW=2048;x=y=rowh=0;pos={};W=0
for k,im in imgs.items():
  if x+im.width>RW:x=0;y+=rowh+2;rowh=0
  pos[k]=(x,y,im.width,im.height);x+=im.width+2;rowh=max(rowh,im.height);W=max(W,x)
H=y+rowh;at=Image.new('RGBA',(W,H),(0,0,0,0))
for k,im in imgs.items():at.paste(im,pos[k][:2]);meta[k]['f']=list(pos[k])
buf=io.BytesIO();at.save(buf,'WEBP',quality=82,method=6);open('bld.webp','wb').write(buf.getvalue());at.save('bld_atlas.png');json.dump(meta,open('bld.json','w'))
print(W,H,len(buf.getvalue()))
# pré-visualização
pv=Image.new('RGBA',(W,H),(93,143,62,255));pv.alpha_composite(at);pv.resize((W//2,H//2)).save('bld_prev.png')
