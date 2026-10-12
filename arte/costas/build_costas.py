# Constrói a folha de costas (ANIMB) a partir de arte/costas/<unid>.png (fundo magenta)
# e injeta no www/index.html. Uso: python3 build_costas.py ../../www/index.html
import numpy as np,io,base64,json,re,sys,os
from PIL import Image
from scipy import ndimage as nd
HMAP={'guerreiro':36,'espadachim':36,'lanceiro':36,'arqueiro':36,'sacerdote':38,'cavaleiro':50,'cavArqueira':50,'aldeao':34}
def cut(path):
  im=np.array(Image.open(path).convert('RGB')).astype(float);bg=np.array([255,0,255.])
  d=np.sqrt(((im-bg)**2).sum(2));a=np.clip((d-70)/(150-70),0,1)
  m=a>.5;lab,n=nd.label(m)
  if n:
    sz=nd.sum(m,lab,range(1,n+1));big=sz.max();keep=np.zeros_like(m)
    for i,s in enumerate(sz):
      if s>=big*.02:keep|=lab==(i+1)
    keep=nd.binary_fill_holes(keep);a=np.where(keep,a,0)
  rgb=im.copy();semi=(a>0)&(a<1)
  for ch in range(3):rgb[:,:,ch]=np.where(semi,np.clip((im[:,:,ch]-bg[ch]*(1-a))/np.maximum(a,.05),0,255),im[:,:,ch])
  ex=np.clip(np.minimum(rgb[:,:,0],rgb[:,:,2])-rgb[:,:,1]-10,0,None);edge=nd.binary_dilation(a<.9,iterations=2)
  f=np.where(edge,1.0,.3);rgb[:,:,0]-=ex*f;rgb[:,:,2]-=ex*f*.9;a=np.where(edge&(ex>60),a*.3,a)
  out=np.dstack([np.clip(rgb,0,255),a*255]).astype(np.uint8);img=Image.fromarray(out,'RGBA');img=img.crop(img.getbbox())
  al=np.array(img)[:,:,3]>120;ys,xs=np.nonzero(al);yb=ys.max();h=yb-ys.min()
  low=ys>ys.min()+h*.9;fx=(xs[low].min()+xs[low].max())/2 if low.any() else img.width/2
  return img,float(round(fx,1))
units=[u for u in HMAP if os.path.exists('arte/costas/%s.png'%u)]
imgs={};meta={};H={}
for u in units:
  img,fx=cut('arte/costas/%s.png'%u);imgs[u]=img;meta[u]={'fx':fx,'fy':img.height,'h':img.height};H[u]=HMAP[u]
# o aldeao serve de costas para todas as tarefas (v_*): mesma imagem, várias chaves
VIL=['v_madeira','v_pedra','v_construcao','v_agricultura','v_caca','v_colher']
if 'aldeao' in units:
  for vk in VIL:
    meta[vk]=dict(meta['aldeao']);H[vk]=34
  imgs2={k:v for k,v in imgs.items() if k!='aldeao'};
  # manter a imagem do aldeao no atlas, referida pelas chaves v_*
  imgs2['aldeao']=imgs['aldeao']
  del meta['aldeao'];del H['aldeao']
  units=[u for u in units if u!='aldeao']+['aldeao']
# atlas em prateleira única
pad=2;W=sum(im.width+pad for im in imgs.values());HH=max(im.height for im in imgs.values())
at=Image.new('RGBA',(W,HH),(0,0,0,0));x=0
VILK=['v_madeira','v_pedra','v_construcao','v_agricultura','v_caca','v_colher']
for u in units:
  im=imgs[u];at.paste(im,(x,0));fr=[x,0,im.width,im.height]
  if u=='aldeao':
    for vk in VILK:meta[vk]['f']=[fr]*9
  else:meta[u]['f']=[fr]*9
  x+=im.width+pad
buf=io.BytesIO();at.save(buf,'WEBP',quality=88,method=6);b64=base64.b64encode(buf.getvalue()).decode()
at.save('arte/costas/costas_atlas.png')
print('atlas',at.size,len(buf.getvalue())//1024,'KB',units)
html=sys.argv[1];s=open(html,encoding='utf-8').read()
# substitui o bloco ANIMB (definição + loader se existir)
pat=re.compile(r"const ANIMB=\{wide:true,ready:false,img:null,meta:.*?\},H:.*?,teams:new Map\(\)\};(\n\(\(\)=>\{const im=new Image\(\);im\.onload=.*?ANIMB\.img=im;ANIMB\.ready=true.*?\}\)\(\);)?",re.S)
new=("const ANIMB={wide:true,ready:false,img:null,meta:"+json.dumps(meta)+",H:"+json.dumps(H)+",teams:new Map()};\n"
 "(()=>{const im=new Image();im.onload=()=>{ANIMB.img=im;ANIMB.ready=true;try{UCACHE.clear();UCBYTES=0}catch(e){}uiDirty=true};im.src='data:image/webp;base64,"+b64+"'})();")
s2,nsub=pat.subn(new,s,count=1)
assert nsub==1,('subs',nsub)
open(html,'w',encoding='utf-8').write(s2);print('injetado, folhas:',units)
