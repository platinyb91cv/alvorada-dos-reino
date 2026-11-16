# Arquearia nova (Kimi: edifício compacto com alpendre de tiro e alvos) -> frames arquearia_0/1/2 do atlas.
# Recorta o branco, corrige a inclinação para 2:1, esbate a borda do chão de terra (funde com a relva), escala pela pegada 3×3.
# Retira arquearia_n2/_n3 antigos (rodados): até haver arte nova por nível, o jogo mostra bandeirolas e escudo.
import sys,json,io,hashlib,colorsys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
src,repo=Path(sys.argv[1]),Path(sys.argv[2]);TARGETS=sys.argv[3:] or ['arquearia_0','arquearia_1','arquearia_2']  # frames a substituir
html_p=repo/'www/index.html';html=html_p.read_text();i=html.index('const BLD3D_DATA=');j=html.index('\n',i);data=json.loads(html[i+17:html.index(';',i)])
atlas_p=repo/'www/assets/edificios-extra'/data['file'];old=Image.open(atlas_p).convert('RGBA');SC=data['scale']
tiles={n:(old.crop((x,y,x+w,y+h)),ax,ay) for n,(x,y,w,h,ax,ay) in data['frames'].items() if n not in TARGETS and not (TARGETS[0]=='arquearia_0' and n in ('arquearia_n2','arquearia_n3'))}
rgb=np.asarray(Image.open(src).convert('RGB')).astype(np.float32);mn=rgb.min(2);sat=rgb.max(2)-mn
white=(mn>=232)&(sat<=18);lab,_=ndimage.label(white);border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0};bg=np.isin(lab,list(border))
sz=ndimage.sum(np.ones_like(mn),lab,range(1,lab.max()+1));pk=np.zeros(lab.max()+1,bool);pk[1:]=sz>=12;bg=bg|(pk[lab]&(lab>0)&(mn>=238)) # buracos brancos fechados (fundo visto entre pilares)
d=ndimage.distance_transform_edt(~bg)
ground=((rgb[...,0]-rgb[...,2])>22)&(mn>105)&(sat<120)          # terra/areia
ground=ndimage.binary_opening(ground,iterations=1)
a=np.where(bg,0.,1.);edge=np.clip(d/16,0,1)
a=np.where(ground,np.minimum(a,edge**1.4),np.where(d<=2,np.clip((255-mn)/60,0,1),a))  # chão esbatido 16 px; resto com orla de 2 px
a=ndimage.uniform_filter(a,2);a[bg]=0
im=Image.fromarray(np.dstack([rgb,a*255]).astype(np.uint8),'RGBA');bb=im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox();im=im.crop(bb)
# inclinação medida 0,538 -> 0,5
al=np.asarray(im.getchannel('A'))>40;ys,xs=np.nonzero(al);cols=np.arange(xs.min(),xs.max()+1);bot=np.array([ys[xs==c].max() for c in cols]);bi=int(np.argmax(bot))
yl=ys[xs<=xs.min()+2].mean();slope=float(__import__('os').environ.get('SLOPE') or (bot[bi]-yl)/max(1,cols[bi]-xs.min()));sy=.5/slope if abs(slope-.5)>.015 else 1  # SLOPE: medida à mão quando o canto não está completo
W,Hh=3,3;tw=(W+Hh)*32*SC*.96;k=tw/im.width;im=im.resize((round(im.width*k),round(im.height*k*sy)),Image.LANCZOS)
px=im.load()
for yy in range(im.height):
  for xx in range(im.width):
    r,g,b,al_=px[xx,yy]
    if al_<8:continue
    h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
    if 188<=h*360<=282 and s<.34:r2,g2,b2=colorsys.hsv_to_rgb(h,min(s,.1),v);px[xx,yy]=(round(r2*255),round(g2*255),round(b2*255),al_)
ax=im.width/2;ay=im.height-(W+Hh)*16*SC
for n in TARGETS:tiles[n]=(im,round(ax,2),round(ay,2))
print('inclinação',round(slope,3),'corr',round(sy,3),'tamanho',im.size)
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
