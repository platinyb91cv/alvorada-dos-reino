from PIL import Image
import json,base64,io
ks=['guerreiro','espadachim','lanceiro','arqueiro','besteiro','cavaleiro','cavPesada','cavArqueira','ariete','catapulta','trebuchet','sacerdote']
FLIP={'arqueiro','besteiro','ariete'}
ims=[]
for k in ks:
  im=Image.open(f'cut2_{k}.png');im=im.crop(im.getbbox())
  if k in FLIP:im=im.transpose(Image.FLIP_LEFT_RIGHT)
  ims.append((k,im))
W=sum(i.width+2 for _,i in ims);H=max(i.height for _,i in ims)
at=Image.new('RGBA',(W,H),(0,0,0,0));x=0;meta={}
for k,im in ims:
  at.paste(im,(x,0))
  a=im.split()[3].load();w,h=im.size
  # pés: centro da faixa opaca nas últimas linhas
  xs=[xx for yy in range(int(h*.9),h) for xx in range(w) if a[xx,yy]>128]
  fx=(min(xs)+max(xs))/2 if xs else w/2
  meta[k]=[x,0,w,h,round(fx,1),h-2]
  x+=w+2
buf=io.BytesIO();at.save(buf,'WEBP',quality=90,method=6);b=buf.getvalue()
open('atlas.webp','wb').write(b);at.save('atlas.png')
open('atlas.json','w').write(json.dumps(meta))
print(W,H,len(b))
