# Recorta as 16 poses do Rei (2 folhas 4x2 com fundo magenta) e monta um atlas WebP com âncora nos pés.
# Quadros: 0-3 andar, 4-7 ataque, 8-9 parado, 10 grito, 11 bênção, 12 golpe sofrido, 13-15 queda.
from PIL import Image
import numpy as np, json, io, base64, os
from scipy import ndimage as nd
D=os.path.dirname(os.path.abspath(__file__))
TH=130  # altura da figura de pé no atlas (px)
def cells(path):
  im=np.array(Image.open(path).convert('RGB')).astype(float);H,W,_=im.shape
  cw=W/4;ch=H/2;out={}
  for r in range(2):
    for c in range(4):
      x0=int(c*cw)+4;x1=int((c+1)*cw)-4;y0=int(r*ch)+4;y1=int((r+1)*ch)-4
      cell=im[y0:y1,x0:x1]
      samp=np.concatenate([cell[2:12,2:12].reshape(-1,3),cell[2:12,-12:-2].reshape(-1,3),cell[-12:-2,2:12].reshape(-1,3),cell[-12:-2,-12:-2].reshape(-1,3)])
      bg=np.median(samp,0)
      d=np.sqrt(((cell-bg)**2).sum(2))
      mag=(cell[:,:,1]<cell[:,:,0]*.45)&(cell[:,:,1]<cell[:,:,2]*.5)&(cell[:,:,0]>110)&(cell[:,:,2]>90)
      a=np.clip((d-38)/(85-38),0,1);a[mag&(d<120)]=0
      # componentes: a figura e o que está perto (espada, coroa caída)
      m=a>.5;lab,n=nd.label(m)
      if n:
        sizes=nd.sum(m,lab,range(1,n+1));mi=int(np.argmax(sizes))+1
        ys,xs=np.nonzero(lab==mi);bx0,bx1,by0,by1=xs.min(),xs.max(),ys.min(),ys.max()
        keep=lab==mi
        for i in range(1,n+1):
          if i==mi or sizes[i-1]<6:continue
          yy,xx=np.nonzero(lab==i)
          if xx.max()<bx0-40 or xx.min()>bx1+40 or yy.max()<by0-40:continue
          keep|=lab==i
        keep=nd.binary_dilation(keep,iterations=2);a=np.where(keep,a,0)
      rgb=cell.copy();semi=(a>0)&(a<1)
      for k in range(3):rgb[:,:,k]=np.where(semi,np.clip((cell[:,:,k]-bg[k]*(1-a))/np.maximum(a,.05),0,255),cell[:,:,k])
      pink=(rgb[:,:,0]>140)&(rgb[:,:,2]>110)&(rgb[:,:,1]<.55*np.minimum(rgb[:,:,0],rgb[:,:,2]))
      lum=(rgb[:,:,0]*.3+rgb[:,:,1]*.59+rgb[:,:,2]*.11)[...,None]
      rgb=np.where(pink[...,None],np.clip(lum*1.1+25,0,255).repeat(3,2),rgb)
      out[(r,c)]=np.dstack([rgb,a*255]).astype(np.uint8)
  return out
A=cells(D+'/folha1.png');B=cells(D+'/folha2.png')
SEQ=[A[(0,0)],A[(0,1)],A[(0,2)],A[(0,3)],A[(1,0)],A[(1,1)],A[(1,2)],A[(1,3)],
     B[(0,0)],B[(0,1)],B[(0,2)],B[(0,3)],B[(1,0)],B[(1,1)],B[(1,2)],B[(1,3)]]
SHEET=[0]*8+[1]*8
def anchor(fr,lying=False):
  al=fr[:,:,3]>100;ys,xs=np.nonzero(al);top,bot=ys.min(),ys.max();h=bot-top
  if lying:return (xs.min()+xs.max())/2,bot,h
  band=(ys>top+h*.30)&(ys<top+h*.62)  # tronco: ignora espada e capa nas pontas
  return float(np.median(xs[band])),bot,h
# escala por folha a partir da pose parada / primeiro passo
sc=[TH/anchor(A[(0,0)])[2],TH/anchor(B[(0,0)])[2]]
frames=[];meta=[]
for i,fr in enumerate(SEQ):
  s=sc[SHEET[i]];cx,fy,_=anchor(fr,lying=i>=14)
  al=fr[:,:,3];ys,xs=np.nonzero(al>12);x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
  im=Image.fromarray(fr[y0:y1+1,x0:x1+1],'RGBA');im=im.resize((max(1,round(im.width*s)),max(1,round(im.height*s))),Image.LANCZOS)
  frames.append(im);meta.append([round((cx-x0)*s,1),round((fy-y0)*s,1)])
# atlas
RW=1400;x=y=rowh=0;pos=[];W=0
for im in frames:
  if x+im.width>RW:x=0;y+=rowh+2;rowh=0
  pos.append((x,y,im.width,im.height));x+=im.width+2;rowh=max(rowh,im.height);W=max(W,x)
H=y+rowh;at=Image.new('RGBA',(W,H),(0,0,0,0))
for im,p in zip(frames,pos):at.paste(im,p[:2])
buf=io.BytesIO();at.save(buf,'WEBP',quality=82,method=6);open(D+'/rei.webp','wb').write(buf.getvalue());at.save(D+'/rei_atlas.png')
M={'h':TH,'f':[list(p)+m for p,m in zip(pos,meta)]}
json.dump(M,open(D+'/rei.json','w'))
open(D+'/rei.b64','w').write(base64.b64encode(buf.getvalue()).decode())
print(W,H,len(buf.getvalue()),'bytes');print(M['f'])
