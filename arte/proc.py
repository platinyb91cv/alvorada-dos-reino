from PIL import Image
import numpy as np, json
from scipy import ndimage as nd
U='/root/.claude/uploads/415342e0-77a1-5a94-8f8a-71375aa47804/'
# unidade: (ficheiro, altura alvo em px da figura, quadros walk, quadros atk, apagar tronco)
UNITS={
 'guerreiro':('ae8af52b',110,[(0,1),(0,2),(0,3),(0,2)],[(1,0),(1,1),(1,2),(1,3)],0),
 'espadachim':('67297f27',110,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],0),
 'lanceiro':('111b51d3',110,[(0,1),(0,2),(0,3),(0,2)],[(1,0),(1,1),(1,2),(1,3)],0),
 'arqueiro':('ad256a17',110,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],0),
 'sacerdote':('36a6f569',110,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],0),
 'cavaleiro':('bb4095f2',130,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],0),
 'cavArqueira':('3688d025',130,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],0),
 'v_madeira':('14ea5ffa',105,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],1),
 'v_pedra':('352dccdd',105,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],1),
 'v_construcao':('f67621a2',105,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],1),
 'v_agricultura':('f2538b24',105,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],0),
 'v_caca':('34963695',105,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],0),
 'ariete':('92d77dfe',110,[(0,0),(0,1),(0,2),(0,3)],[(1,0),(1,1),(1,2),(1,3)],0),
 'catapulta':('6a5c8663',110,[(1,0),(1,0),(1,0),(1,0)],[(1,0),(1,1),(1,2),(1,3)],0),
}
def cells(f):
  im=np.array(Image.open(U+f+'-image.png').convert('RGB')).astype(float);H,W,_=im.shape
  cw=W/4;ch=H/2;out={}
  for r in range(2):
    for c in range(4):
      x0=int(c*cw)+5;x1=int((c+1)*cw)-5;y0=int(r*ch)+5;y1=int((r+1)*ch)-5
      cell=im[y0:y1,x0:x1]
      samp=np.concatenate([cell[2:12,2:12].reshape(-1,3),cell[2:12,-12:-2].reshape(-1,3),cell[-40:-30,2:12].reshape(-1,3)])
      bg=np.median(samp,0)
      d=np.sqrt(((cell-bg)**2).sum(2))
      # magenta: muito vermelho+azul e pouco verde -> fundo mesmo que varie
      mag=(cell[:,:,1]<cell[:,:,0]*.45)&(cell[:,:,1]<cell[:,:,2]*.5)&(cell[:,:,0]>110)&(cell[:,:,2]>90)
      a=np.clip((d-38)/(85-38),0,1);a[mag&(d<120)]=0
      out[(r,c)]=(cell,a,bg)
  return out
frames={};meta={}
for u,(f,th,wk,at,trunk) in UNITS.items():
  cs=cells(f);proc={}
  for key,(cell,a,bg) in cs.items():
    a=a.copy()
    if trunk and key==(1,2):a[:, -30:]=0
    m=a>.5;lab,n=nd.label(m)
    if n:
      sizes=nd.sum(m,lab,range(1,n+1));mi=int(np.argmax(sizes))+1
      ys,xs=np.nonzero(lab==mi);bx0,bx1,by0,by1=xs.min(),xs.max(),ys.min(),ys.max()
      keep=lab==mi
      for i in range(1,n+1):
        if i==mi or sizes[i-1]<4:continue
        yy,xx=np.nonzero(lab==i)
        if yy.min()>by1-2:continue            # texto por baixo da figura
        if xx.max()<bx0-25 or xx.min()>bx1+25:continue
        keep|=lab==i
      keep=nd.binary_dilation(keep,iterations=2)
      a=np.where(keep,a,0)
    # tirar o tom magenta das bordas
    rgb=cell.copy();semi=(a>0)&(a<1)
    for ch in range(3):
      rgb[:,:,ch]=np.where(semi,np.clip((cell[:,:,ch]-bg[ch]*(1-a))/np.maximum(a,.05),0,255),cell[:,:,ch])
    pink=(rgb[:,:,0]>140)&(rgb[:,:,2]>110)&(rgb[:,:,1]<.55*np.minimum(rgb[:,:,0],rgb[:,:,2]))
    lum=(rgb[:,:,0]*.3+rgb[:,:,1]*.59+rgb[:,:,2]*.11)[...,None]
    rgb=np.where(pink[...,None],np.clip(lum*1.25+40,0,255).repeat(3,2),rgb)
    proc[key]=np.dstack([rgb,a*255]).astype(np.uint8)
  seq=wk+at
  # caixa comum a todos os quadros (mantém o movimento relativo)
  boxes=[];
  for key in seq:
    al=proc[key][:,:,3];ys,xs=np.nonzero(al>20);boxes.append((xs.min(),ys.min(),xs.max(),ys.max()))
  X0=min(b[0] for b in boxes);Y0=min(b[1] for b in boxes);X1=max(b[2] for b in boxes);Y1=max(b[3] for b in boxes)
  al=proc[wk[0]][:,:,3];ys,xs=np.nonzero(al>20);fh=ys.max()-ys.min();footY=ys.max()
  bot=xs[ys>=footY-fh*.08];footX=(bot.min()+bot.max())/2
  s=th/fh
  imgs=[]
  for key in seq:
    im=Image.fromarray(proc[key][Y0:Y1+1,X0:X1+1],'RGBA');im=im.resize((max(1,round(im.width*s)),max(1,round(im.height*s))),Image.LANCZOS);imgs.append(im)
  frames[u]=imgs;meta[u]={'fx':round((footX-X0)*s,1),'fy':round((footY-Y0)*s,1),'h':th}
  print(u,imgs[0].size)
# atlas
rows=[];x=0;row=[];RW=2000
allf=[(u,i,im) for u in frames for i,im in enumerate(frames[u])]
W=0;H=0;y=0;rowh=0;pos={}
x=0
for u,i,im in allf:
  if x+im.width>RW:x=0;y+=rowh+2;rowh=0
  pos[(u,i)]=(x,y,im.width,im.height);x+=im.width+2;rowh=max(rowh,im.height);W=max(W,x)
H=y+rowh
at=Image.new('RGBA',(W,H),(0,0,0,0))
for u,i,im in allf:at.paste(im,pos[(u,i)][:2])
for u in frames:meta[u]['f']=[list(pos[(u,i)]) for i in range(8)]
import io
buf=io.BytesIO();at.save(buf,'WEBP',quality=80,method=6);open('anim.webp','wb').write(buf.getvalue());at.save('anim_atlas.png')
json.dump(meta,open('anim.json','w'))
print(W,H,len(buf.getvalue()))
