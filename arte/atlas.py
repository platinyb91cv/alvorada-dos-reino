from PIL import Image
import json,base64,io
ks=['guerreiro','espadachim','lanceiro','arqueiro','besteiro','cavaleiro','cavPesada','cavArqueira','ariete','catapulta','trebuchet','sacerdote','v_ocioso','v_madeira','v_pedra','v_ouro','v_agricultura','v_caca','v_construcao','v_transporte','barcoPesca','transporte','gale','incendiario','navioPesado']
FLIP={'arqueiro','besteiro','ariete','transporte','gale'}
ims=[]
for k in ks:
  im=Image.open(f'cut2_{k}.png');im=im.crop(im.getbbox())
  if k in FLIP:im=im.transpose(Image.FLIP_LEFT_RIGHT)
  ims.append((k,im))
rows=[ims[:12],ims[12:]];W=max(sum(i.width+2 for _,i in r) for r in rows);RH=[max(i.height for _,i in r) for r in rows];H=sum(RH)+2
at=Image.new('RGBA',(W,H),(0,0,0,0));meta={}
for ri,r in enumerate(rows):
  x=0;y0=0 if ri==0 else RH[0]+2
  for k,im in r:
    at.paste(im,(x,y0))
    a=im.split()[3].load();w,h=im.size
    xs=[xx for yy in range(int(h*.9),h) for xx in range(w) if a[xx,yy]>128]
    fx=(min(xs)+max(xs))/2 if xs else w/2
    meta[k]=[x,y0,w,h,round(fx,1),h-2]
    x+=w+2
buf=io.BytesIO();at.save(buf,'WEBP',quality=90,method=6);b=buf.getvalue()
open('atlas.webp','wb').write(b);at.save('atlas.png')
open('atlas.json','w').write(json.dumps(meta))
print(W,H,len(b))
