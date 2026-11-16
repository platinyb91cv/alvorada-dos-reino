# Cavalaria HD: render 512px (Cycles, mesma luz da infantaria HD) -> atlas h=128. Ponto de apoio relativo copiado do atlas atual
# (mesma posição no jogo) e escala tal que o tamanho no ecrã é igual (128/44,8 = 2,857× mais píxeis).
import json,hashlib,sys,io,re
from pathlib import Path
from PIL import Image
name=sys.argv[1];H=96;W=2048
html=Path('/tmp/claude-0/wt/www/index.html').read_text();old=json.loads(re.search(r'const UNIT3D_CAV_DATA=(\{[^\n]+\});',html).group(1))[name]
d=Path('/tmp/claude-0/sp/cavhd')/name;r=json.loads((d/'render-report.json').read_text())
fpd=old['framesPerDirection'];assert r['framesPerDirection']==fpd and r['states']==old['states']
fr={(f['direction'],f['i']):f for f in r['frames']};K=H/old['h']
ref=old['f'][1*fpd+0];im0=Image.open(d/'frames'/'01-00.png');b0=im0.getbbox();sc=ref[3]*K/(b0[3]-b0[1])  # escala global pelo quadro parado a sul
meta={'h':H,'directions':8,'framesPerDirection':fpd,'states':old['states'],'directionLabels':old['directionLabels'],'locomotion':old['locomotion'],'f':[]}
tiles=[];x=y=2;row=0
for dd in range(8):
  for i in range(fpd):
    ox,oy,ow,oh,oax,oay=old['f'][dd*fpd+i];im=Image.open(d/'frames'/f'{dd:02d}-{i:02d}.png').convert('RGBA');b=im.getbbox();assert b and min(b[:2])>0 and max(b[2:])<r['res'],('cortado',name,dd,i)
    t=im.crop(b);t=t.resize((max(1,round(t.width*sc)),max(1,round(t.height*sc))),Image.Resampling.LANCZOS)
    if x+t.width+2>W:x=2;y+=row+4;row=0
    meta['f'].append([x,y,t.width,t.height,round(oax/ow*t.width,4),round(oay/oh*t.height,4)]);tiles.append(t);x+=t.width+4;row=max(row,t.height)
at=Image.new('RGBA',(W,y+row+2))
for t,f in zip(tiles,meta['f']):at.paste(t,tuple(f[:2]))
buf=io.BytesIO();at.save(buf,'WEBP',lossless=True,method=6);b=buf.getvalue()
o=Path('/tmp/claude-0/wt/www/assets/units3d-hd');(o/f'{name}.webp').write_bytes(b);meta['atlasSha256']=hashlib.sha256(b).hexdigest();(o/f'{name}.json').write_text(json.dumps(meta,separators=(',',':')))
prov={'unit':name,'source':'arte/cavalaria-3d (montar_cavalaria.py: Horse.blend CC0 + cavaleiro de arte/unidades-armadas)','rigSha256':r['glbSha256'],'renderResolution':r['res'],'cyclesSamples':r['samples'],'h':H,'downscaleFactor':sc,'atlasSha256':meta['atlasSha256'],'encoding':'lossless','additionalMeshyCredits':0}
(Path('/tmp/claude-0/wt/arte/unidades-hd')/f'{name}.verification.json').write_text(json.dumps(prov,indent=1))
print(name,at.size,len(b),round(sc,3))
