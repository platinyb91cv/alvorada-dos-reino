# Atlas HD (h=128) a partir dos renders 512px: reduz (não amplia) -> nítido. Mesma ordem/estados/âncoras que os atlas armados (h=64).
import json,hashlib,sys,io
from pathlib import Path
from PIL import Image
H=128;W=2048;Q=sys.argv[2] if len(sys.argv)>2 else 'lossless'
name=sys.argv[1];d=Path('/tmp/claude-0/sp/hd')/name;r=json.loads((d/'render-report.json').read_text())
old=json.loads(Path(f'/tmp/claude-0/wt/www/assets/units3d-armados/{name}.json').read_text())
sc=H/r['bodyReferencePixels'];meta={'h':H,'directions':8,'framesPerDirection':r['framesPerDirection'],'states':r['states'],'directionLabels':r['labels'],'f':[]}
if 'locomotion' in old:meta['locomotion']=old['locomotion']
assert meta['states']==old['states'] and meta['framesPerDirection']==old['framesPerDirection']
fr=sorted(r['frames'],key=lambda f:(f['direction'],f['i']));assert len(fr)==8*r['framesPerDirection']
tiles=[];x=y=2;row=0
for f in fr:
  im=Image.open(d/'frames'/f"{f['direction']:02d}-{f['i']:02d}.png").convert('RGBA');b=im.getbbox();assert b and min(b[:2])>0 and max(b[2:])<r['res'],('cortado',name,f)
  t=im.crop(b);t=t.resize((max(1,round(t.width*sc)),max(1,round(t.height*sc))),Image.Resampling.LANCZOS)
  if x+t.width+2>W:x=2;y+=row+4;row=0
  meta['f'].append([x,y,t.width,t.height,round((f['anchor'][0]-b[0])*sc,4),round((f['anchor'][1]-b[1])*sc,4)]);tiles.append(t);x+=t.width+4;row=max(row,t.height)
at=Image.new('RGBA',(W,y+row+2))
for t,f in zip(tiles,meta['f']):at.paste(t,tuple(f[:2]))
buf=io.BytesIO()
if Q=='lossless':at.save(buf,'WEBP',lossless=True,method=6)
else:at.save(buf,'WEBP',quality=int(Q),alpha_quality=100,method=6)
b=buf.getvalue();o=Path('/tmp/claude-0/wt/www/assets/units3d-hd');o.mkdir(exist_ok=True);(o/f'{name}.webp').write_bytes(b)
meta['atlasSha256']=hashlib.sha256(b).hexdigest();(o/f'{name}.json').write_text(json.dumps(meta,separators=(',',':')))
prov={'unit':name,'source':'arte/unidades-armadas/'+name+'.glb','glbSha256':r['glbSha256'],'renderResolution':r['res'],'cyclesSamples':r['samples'],'bodyReferencePixels':r['bodyReferencePixels'],'h':H,'downscaleFactor':sc,'atlasSha256':meta['atlasSha256'],'encoding':Q,'additionalMeshyCredits':0}
pv=Path('/tmp/claude-0/wt/arte/unidades-hd');pv.mkdir(exist_ok=True);(pv/f'{name}.verification.json').write_text(json.dumps(prov,indent=1))
print(name,at.size,len(b),round(sc,3))
