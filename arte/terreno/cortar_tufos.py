import numpy as np, json
from PIL import Image
from scipy import ndimage
im=np.asarray(Image.open('/mnt/user-data/uploads/alvorada-edificios/relva-tufos/tufos.png').convert('RGB')).astype(np.float32)
H=W=2048;C=512;K=0.19  # 2x do mundo: tufo ~70 px de largura no atlas -> ~35 px no mundo (meio losango)
tiles=[];meta=[]
for r in range(4):
  for c in range(4):
    a=im[r*C:(r+1)*C,c*C:(c+1)*C]
    mn=a.min(2);sat=a.max(2)-mn
    white=(mn>=236)&(sat<=20)
    lab,_=ndimage.label(white);border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(border))
    pocket=white&~bg&(mn>=246)   # brancos fechados entre lâminas (petalas ficam: sao sombreadas)
    bg=bg|pocket
    # cor->alfa na orla: perto do fundo, a transparencia segue a distancia ao branco
    d=ndimage.distance_transform_edt(~bg)
    wa=np.clip((255-mn)/70,0,1)
    alpha=np.where(bg,0,np.where(d<=2.5,np.maximum(wa,0),1.0))
    # desfazer mistura com branco na orla
    A=np.clip(alpha,1e-3,1)[...,None];col=np.clip((a-255*(1-A))/A,0,255);col=np.where(alpha[...,None]>=.999,a,col)
    lab2,n2=ndimage.label(ndimage.binary_dilation(alpha>.08,iterations=3))
    if n2>1:
        sz=ndimage.sum(np.ones_like(alpha),lab2,range(1,n2+1));keep=1+int(np.argmax(sz));alpha=np.where(lab2==keep,alpha,0)
    rgba=np.dstack([col,alpha*255]).astype(np.uint8);t=Image.fromarray(rgba,'RGBA')
    bb=t.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox();t=t.crop(bb)
    t=t.resize((max(1,round(t.width*K)),max(1,round(t.height*K))),Image.LANCZOS)
    # tom: um pouco mais escuro e a base a fundir-se com a relva do chão
    arr=np.asarray(t).astype(np.float32);hh=arr.shape[0];g=np.linspace(0,1,hh)[:,None]
    shade=.86-.30*np.clip((g-.55)/.45,0,1)**1.3
    ground=np.array([92,112,48],np.float32);mix=.25*np.clip((g-.6)/.4,0,1)
    arr[...,:3]=np.clip((arr[...,:3]*shade[...,None])*(1-mix[...,None])+ground*mix[...,None],0,255)
    t=Image.fromarray(arr.astype(np.uint8),'RGBA')
    tiles.append(t)
kind=['c','c','c','c','a','a','a','a','f','f','f','t','t','s','c','c']  # curto, alto, flor, trevo, seco
AW=0;x=0;F=[]
gap=2;HH=max(t.height for t in tiles)
atlas=Image.new('RGBA',(sum(t.width+gap for t in tiles)+gap,HH+2*gap))
x=gap
for t in tiles:
  atlas.paste(t,(x,gap+HH-t.height));F.append([x,gap+HH-t.height,t.width,t.height]);x+=t.width+gap
atlas.save('/tmp/claude-0/wt/www/assets/terreno/tufos.webp','WEBP',quality=88,method=6,alpha_quality=90)
json.dump({'f':F,'k':kind},open('meta.json','w'))
print(atlas.size,[f[2:] for f in F])
big=Image.new('RGBA',atlas.size,(110,128,60,255));big.alpha_composite(atlas);big.resize((atlas.width*3,atlas.height*3),Image.NEAREST).save('check.png')
