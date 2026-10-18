from pathlib import Path
from PIL import Image
import json,hashlib,math,sys
O=Path(sys.argv[sys.argv.index('--sources')+1]).resolve()if '--sources'in sys.argv else Path(__file__).resolve().parent.parent
B=Path(sys.argv[sys.argv.index('--baseline')+1]).resolve()if '--baseline'in sys.argv else O.parent/'correcao-aldeao-guerreiro'/'antes'
result={}
for name in ['aldeao','guerreiro']:
 d=O/name;old=json.loads((B/name/'render-report.json').read_text());new=json.loads((d/'render-report.json').read_text());meta=json.loads((d/'atlas.json').read_text())
 assert new['states']==old['states']and new['labels']==old['labels']and new['framesPerDirection']==old['framesPerDirection'];assert new['bodyReferencePixels']==old['bodyReferencePixels'];assert meta['h']==64
 errors=[]
 for a,b in zip(old['frames'],new['frames']):
  for field in ['i','state','clip','phase','direction']:assert a[field]==b[field],(name,field)
  errors.append(math.dist(a['anchor'],b['anchor']));im=Image.open(d/'frames'/f"{b['direction']:02d}-{b['i']:02d}.png").convert('RGBA');box=im.getbbox();assert box and min(box[:2])>0 and max(box[2:])<192,(name,b,'clipped')
 assert max(errors)<1e-4,(name,max(errors));atlas=Image.open(d/'atlas.webp').convert('RGBA');unique={}
 for direction in range(8):
  tiles=[]
  for i in meta['states']['walk']:
   x,y,w,h,*_=meta['f'][direction*meta['framesPerDirection']+i];tiles.append(hashlib.sha256(atlas.crop((x,y,x+w,y+h)).tobytes()).hexdigest())
  unique[direction]=len(set(tiles));assert unique[direction]==8,(name,direction,'duplicate walk frames')
 result[name]={'referenceHeight':64,'originalBodyReferencePixels':new['bodyReferencePixels'],'maxGroundAnchorDifferenceIn192pxSource':max(errors),'statesAndDirectionOrderPreserved':True,'unclippedFrames':len(new['frames']),'uniqueWalkFramesByDirection':unique,'beforeAtlasSha256':hashlib.sha256((B/name/'atlas.webp').read_bytes()).hexdigest(),'atlasSha256':meta['atlasSha256']}
out=O.parent/'correcao-aldeao-guerreiro';out.mkdir(parents=True,exist_ok=True);(out/'atlas-alignment-verification.json').write_text(json.dumps(result,indent=2));print('ATLAS_CORRECTION_VERIFIED',json.dumps(result))
