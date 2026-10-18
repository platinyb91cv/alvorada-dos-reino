from pathlib import Path
import subprocess,json,hashlib,struct,math
from PIL import Image,ImageDraw
import argparse
p=argparse.ArgumentParser();p.add_argument('--blender',default='blender');p.add_argument('--output',required=True);p.add_argument('--reuse',action='store_true');args=p.parse_args();R=Path(args.output).resolve();R.mkdir(parents=True,exist_ok=True);D=Path(__file__).resolve().parent.parent;units=['guerreiro','lanceiro','espadachim','arqueiro','besteiro']
for u in units:
 out=R/u;out.mkdir(parents=True,exist_ok=True)
 if not (args.reuse and (out/'render-report.json').exists()):
  with (out/'blender.log').open('w') as log:
   p=subprocess.run([args.blender,'-b','--python',str(D/'scripts/render_review.py'),'--','--unit',u,'--output',str(out)],stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode==0 and 'PILOT_RENDER_COMPLETE' in (out/'blender.log').read_text(errors='replace'),u
 report=json.loads((out/'render-report.json').read_text()); b=(D/(u+'.glb')).read_bytes();j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]]);start=28+struct.unpack_from('<I',b,12)[0]
 def vals(idx):
  a=j['accessors'][idx];v=j['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];return [struct.unpack_from('<'+'f'*n,b,start+v.get('byteOffset',0)+a.get('byteOffset',0)+i*v.get('byteStride',n*4)) for i in range(a['count'])]
 clips=[]
 for a in j['animations']:
  ts=[x[0] for s in a['samplers'] for x in vals(s['input'])];clips.append({'name':a['name'],'durationSeconds':max(ts)-min(ts),'walkCycles':1,'cycleCountMethod':'One contiguous full left/right gait cycle selected by matching foot phase; not a seamless periodic clip.'})
 names=[j['nodes'][n]['name'] for n in j['skins'][0]['joints']];samples=report['samples'];delta=[samples[-1]['Hips'][i]-samples[0]['Hips'][i] for i in range(3)]
 proof={'name':u,'glbBytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'boneCount':len(names),'boneNames':names,'clips':clips,'triangles':report['triangles'],'heightMeters':report['heightMeters'],'heightMeasurement':'Imported Blender mesh bounds at first selected walking frame; metres, not requested rig height.','forwardAxis':{'glTF':'+Z','Blender':'-Y','evidence':'Front-facing S render looks along local +Y onto the model; face points -Y. Root travels -Y, stance feet move +Y relative to hips.'},'rootDisplacementPerWalkCycle':{'bone':'Hips','coordinateSystem':'Blender Z-up metres','vectorMeters':delta,'horizontalMeters':math.hypot(*delta[:2]),'distanceMeters':math.sqrt(sum(x*x for x in delta))},'endpointMaxRotationDifferenceDegrees':max(report['rawClipEndpointRotationDifferenceDegrees'].values()),'gameIntegration':False,'knownIssues':['Relaxed shared villager walk; military march not yet supplied.','Root motion retained; loop endpoints differ; needs game speed/cycle adaptation.','No weapons or combat clips.'],'preview':{'directions':['SE','S','SW','W','NW','N','NE','E'],'framesPerDirection':8,'phases':[i/8 for i in range(8)],'cellPixels':128}}
 a=j['animations'][0];ch=next(c for c in a['channels'] if c['target']['path']=='translation' and j['nodes'][c['target']['node']]['name']=='Hips');v=vals(a['samplers'][ch['sampler']]['output']);node=ch['target']['node'];scale=[1,1,1]
 while True:
  parent=next((x for x in j['nodes'] if node in x.get('children',[])),None)
  if parent is None:break
  assert 'matrix' not in parent and parent.get('rotation',[0,0,0,1])==[0,0,0,1]
  scale=[x*y for x,y in zip(scale,parent.get('scale',[1,1,1]))];node=j['nodes'].index(parent)
 delta=[(v[-1][k]-v[0][k])*scale[k] for k in range(3)];proof['blenderImportedBoneHeadMotion']=proof['rootDisplacementPerWalkCycle'];proof['rootDisplacementPerWalkCycle']={'bone':'Hips','coordinateSystem':'glTF Y-up metres','vectorMeters':delta,'horizontalMeters':math.hypot(delta[0],delta[2]),'distanceMeters':math.sqrt(sum(x*x for x in delta)),'method':'Original GLB translation channel endpoints multiplied by ancestor scales; no ancestor rotations.'}
 assert len(b)<50000000 and len(names)==24 and len(list((out/'frames').glob('*.png')))==64
 (D/(u+'.verification.json')).write_text(json.dumps(proof,indent=2)+'\n')
 sheet=Image.new('RGB',(8*128+48,8*148),(27,32,38));draw=ImageDraw.Draw(sheet)
 for d,label in enumerate(proof['preview']['directions']):
  draw.text((4,d*148+65),label,fill='white')
  for f in range(8):
   im=Image.open(out/'frames'/f'{d:02d}-{f:02d}.png').convert('RGBA');sheet.paste(im,(48+f*128,d*148),im);draw.text((52+f*128,d*148+130),str(f),fill='white')
 sheet.save(D/(u+'_8dir.png'));print('REVIEW_COMPLETE',u,flush=True)
