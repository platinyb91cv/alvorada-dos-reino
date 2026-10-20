from pathlib import Path
import json,hashlib,sys
from PIL import Image,ImageDraw
O=Path(sys.argv[sys.argv.index('--sources')+1]).resolve()if '--sources'in sys.argv else Path(__file__).resolve().parent.parent
names=[u['id']for u in json.loads((O/'manifest.json').read_text())['units']]
if '--unit'in sys.argv:names=[sys.argv[sys.argv.index('--unit')+1]]
for name in names:
 d=O/name;r=json.loads((d/'render-report.json').read_text());
 if name=='arqueiro':assert r.get('sourceModelSha256')==hashlib.sha256((d/(name+'-jogo.glb')).read_bytes()).hexdigest(),'Archer must be rerendered after archery fix'
 scale=64/r['bodyReferencePixels'];meta={'h':64,'directions':8,'framesPerDirection':r['framesPerDirection'],'states':r['states'],'directionLabels':r['labels'],'f':[]};tiles=[];x=y=2;row=0;width=2048
 if name=='aldeao':meta['states']['carryIdle']=[meta['states']['carry'][0]]
 if (d/'stride-verification.json').exists():
  stride=json.loads((d/'stride-verification.json').read_text());meta['locomotion']={'walk':{'phaseScale':stride['visualPhaseMultiplier'],'strideTiles':stride['strideTiles'],'animFactor':stride['recommendedAnimFactor']}}
  if 'carry'in stride:meta['locomotion']['carry']={'phaseScale':stride['carry']['visualPhaseMultiplier'],'strideTiles':stride['carry']['strideTiles'],'animFactor':stride['carry']['recommendedAnimFactor']}
 for f in r['frames']:
  im=Image.open(d/'frames'/f"{f['direction']:02d}-{f['i']:02d}.png").convert('RGBA');b=im.getbbox();assert b and min(b[:2])>0 and max(b[2:])<r['resolution'],('clipped',name,f)
  tile=im.crop(b);tile=tile.resize((max(1,round(tile.width*scale)),max(1,round(tile.height*scale))),Image.Resampling.LANCZOS)
  if x+tile.width+2>width:x=2;y+=row+4;row=0
  meta['f'].append([x,y,tile.width,tile.height,round((f['anchor'][0]-b[0])*scale,4),round((f['anchor'][1]-b[1])*scale,4)]);tiles.append(tile);x+=tile.width+4;row=max(row,tile.height)
 atlas=Image.new('RGBA',(width,y+row+2));assert atlas.height<=8192
 for tile,frame in zip(tiles,meta['f']):atlas.paste(tile,tuple(frame[:2]))
 for direction in range(8):
  for state in ('walk','attack'):
   ids=meta['states'][state];hashes={hashlib.sha256(tiles[direction*meta['framesPerDirection']+i].tobytes()).digest()for i in ids};assert len(hashes)>=min(4,len(ids)),('not animated',name,direction,state)
 atlas.save(d/'atlas.png');atlas.save(d/'atlas.webp',lossless=True,method=6);meta['atlasSha256']=hashlib.sha256((d/'atlas.webp').read_bytes()).hexdigest();(d/'atlas.json').write_text(json.dumps(meta,separators=(',',':')))
 sheet=Image.new('RGB',(960,400),'#303947');draw=ImageDraw.Draw(sheet)
 for direction in range(8):
  i=direction*meta['framesPerDirection']+meta['states']['idle'][0];tile=tiles[i];ax,ay=meta['f'][i][-2:];xx=(direction%4)*240+120;yy=(direction//4)*200+170;sheet.paste(tile,(round(xx-ax),round(yy-ay)),tile);draw.text(((direction%4)*240+12,(direction//4)*200+12),meta['directionLabels'][direction],fill='white')
 sheet.save(d/'oito-direcoes.png');print(name,atlas.size,len(meta['f']),(d/'atlas.webp').stat().st_size,flush=True)
