from PIL import Image,ImageDraw
import numpy as np,cv2,json,io
ks=['guerreiro','espadachim','lanceiro','arqueiro','besteiro','cavaleiro','cavPesada','cavArqueira','ariete','catapulta','trebuchet','sacerdote','v_ocioso','v_madeira','v_pedra','v_ouro','v_agricultura','v_caca','v_construcao','v_transporte','barcoPesca','transporte','gale','incendiario','navioPesado']
FLIP={'arqueiro','besteiro','ariete','transporte','gale'}
RIG={
 'guerreiro':{'hip':.62,'split':.45,'arm':{'polys':[[(.08,.22),(.22,.24),(.2,.36),(.13,.5),(.25,.84),(.12,.87),(0,.55),(0,.4)]],'pivot':(.17,.25)}},
 'espadachim':{'hip':.66,'split':.52,'arm':{'polys':[[(.1,.2),(.3,.2),(.24,.38),(.21,.6),(.06,.6),(.06,.38)],[(0,.49),(.1,.47),(.26,.56),(.82,.86),(.78,.92),(.2,.64),(0,.56)]],'pivot':(.24,.22)}},
 'lanceiro':{'hip':.62,'split':.45,'arm':{'polys':[[(.05,.24),(.24,.26),(.22,.45),(.2,.66),(.02,.66),(.02,.4)],[(.04,.55),(.25,.47),(.31,.49),(1,.71),(.99,.78),(.27,.57),(.1,.65)]],'pivot':(.14,.28)}},
 'arqueiro':{'hip':.63,'split':.32},'besteiro':{'hip':.68,'split':.5},'sacerdote':{},
 'cavaleiro':{'horse':.7,'split':.45},'cavPesada':{'horse':.66,'split':.42},'cavArqueira':{'horse':.7,'split':.45},
 'v_ocioso':{'hip':.64,'split':.45},'v_madeira':{'hip':.6,'split':.45},'v_pedra':{'hip':.6,'split':.45},'v_ouro':{'hip':.6,'split':.45},
 'v_agricultura':{'hip':.65,'split':.4},'v_caca':{'hip':.7,'split':.45},'v_construcao':{'hip':.66,'split':.4},'v_transporte':{'hip':.62,'split':.4},
}
ims=[]
for k in ks:
  im=Image.open(f'cut2_{k}.png');im=im.crop(im.getbbox())
  if k in FLIP:im=im.transpose(Image.FLIP_LEFT_RIGHT)
  r=RIG.get(k,{})
  if 'arm' in r:
    w,h=im.size;mk=Image.new('L',(w,h),0);d=ImageDraw.Draw(mk)
    for poly in r['arm']['polys']:d.polygon([(x*w,y*h) for x,y in poly],fill=255)
    m=np.array(mk);m=cv2.dilate(m,np.ones((2,2),np.uint8))
    a=np.array(im)
    arm=a.copy();arm[:,:,3]=(arm[:,:,3].astype(int)*(m>0)).astype(np.uint8)
    rgb=cv2.inpaint(np.ascontiguousarray(a[:,:,:3]),(m>0).astype(np.uint8),4,cv2.INPAINT_TELEA)
    al=cv2.inpaint(np.ascontiguousarray(a[:,:,3]),(m>0).astype(np.uint8),4,cv2.INPAINT_TELEA)
    hole=m>0;op=(a[:,:,3]>128)&~hole;H0,W0=hole.shape;R=24
    keep=np.zeros_like(hole)
    ys,xs=np.nonzero(hole)
    for y,x in zip(ys,xs):
      if (op[y,max(0,x-R):x].any() and op[y,x+1:x+1+R].any()) or (op[max(0,y-R):y,x].any() and op[y+1:y+1+R,x].any()):keep[y,x]=True
    al=np.where(hole,np.where(keep,np.maximum(al,200),0),a[:,:,3]).astype(np.uint8)
    body=np.dstack([rgb,al])
    ims.append((k,Image.fromarray(body,'RGBA')));ims.append((k+'_arm',Image.fromarray(arm,'RGBA')))
  else:ims.append((k,im))
# empacotar em linhas de até 1300 px
rows=[];cur=[];cw=0
for k,im in ims:
  if cw+im.width+2>1300 and cur:rows.append(cur);cur=[];cw=0
  cur.append((k,im));cw+=im.width+2
rows.append(cur)
W=max(sum(i.width+2 for _,i in r) for r in rows);RH=[max(i.height for _,i in r) for r in rows];H=sum(RH)+2*len(rows)
at=Image.new('RGBA',(W,H),(0,0,0,0));meta={};y0=0
for ri,r in enumerate(rows):
  x=0
  for k,im in r:
    at.paste(im,(x,y0));a=im.split()[3].load();w,h=im.size
    xs=[xx for yy in range(int(h*.9),h) for xx in range(w) if a[xx,yy]>128]
    fx=(min(xs)+max(xs))/2 if xs else w/2
    meta[k]=[x,y0,w,h,round(fx,1),h-2]
    base=k.replace('_arm','')
    if k==base and base in RIG and RIG[base]:
      rr=dict(RIG[base]);
      if 'arm' in rr:rr={**rr,'arm':{'pivot':rr['arm']['pivot']}}
      meta[k].append(rr)
    x+=w+2
  y0+=RH[ri]+2
for k in list(meta):
  if k.endswith('_arm'):meta[k][4:6]=meta[k.replace('_arm','')][4:6]
buf=io.BytesIO();at.save(buf,'WEBP',quality=90,method=6);b=buf.getvalue()
open('atlas.webp','wb').write(b);at.save('atlas.png');open('atlas.json','w').write(json.dumps(meta))
print(W,H,len(b))
