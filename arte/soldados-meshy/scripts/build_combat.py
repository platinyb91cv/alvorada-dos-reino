from pathlib import Path
import json,struct,hashlib,copy,math,argparse
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--previous',required=True);p.add_argument('--assets',required=True);args=p.parse_args();S=Path(args.source);P=Path(args.previous);D=Path(args.assets)
def read(p):
 b=p.read_bytes();assert b[:4]==b'glTF' and len(b)==struct.unpack_from('<I',b,8)[0];n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);return j,b[28+n:28+n+j['buffers'][0]['byteLength']],b
width={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4};dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def packed(j,bin,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];assert not a.get('sparse');w=width[a['componentType']]*dims[a['type']];o=v.get('byteOffset',0)+a.get('byteOffset',0);return b''.join(bin[o+k*v.get('byteStride',w):o+k*v.get('byteStride',w)+w] for k in range(a['count']))
def rows(j,bin,i):
 a=j['accessors'][i];assert a['componentType']==5126;w=dims[a['type']];return list(struct.iter_unpack('<'+'f'*w,packed(j,bin,i)))
def ahash(j,bin,a):
 h=hashlib.sha256()
 for c in a['channels']:
  s=a['samplers'][c['sampler']];h.update(j['nodes'][c['target']['node']]['name'].encode());h.update(c['target']['path'].encode());h.update(packed(j,bin,s['input']));h.update(packed(j,bin,s['output']))
 return h.hexdigest()
for u in ['guerreiro','lanceiro','espadachim','arqueiro','besteiro']:
 j,base,old=read(P/(u+'.glb'));src,sbin,raw=read(S/u/'motions.glb');original=copy.deepcopy(j);nodes={n['name']:i for i,n in enumerate(j['nodes']) if 'name'in n};bones=[j['nodes'][i]['name'] for i in j['skins'][0]['joints']];assert len(bones)==24 and bones==[src['nodes'][i]['name']for i in src['skins'][0]['joints']]
 for name in bones+['Armature']:
  a=j['nodes'][nodes[name]];b=next(n for n in src['nodes'] if n.get('name')==name)
  for k,default in [('translation',[0,0,0]),('rotation',[0,0,0,1]),('scale',[1,1,1])]:assert max(abs(x-y)for x,y in zip(a.get(k,default),b.get(k,default)))<1e-4,(u,name,k)
 parts=[base];length=len(base)
 def append(data,accessor):
  global length
  pad=(-length)%4
  if pad:parts.append(bytes(pad));length+=pad
  view=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':length,'byteLength':len(data)});parts.append(data);length+=len(data);a=copy.deepcopy(accessor);a['bufferView']=view;a['byteOffset']=0;a.pop('sparse',None);a.pop('min',None);a.pop('max',None);i=len(j['accessors']);j['accessors'].append(a);return i
 names={'Idle':'Combat_Stance','Walk':'Spear_Walk_inplace','Attack':{'guerreiro':'Right_Hand_Sword_Slash','lanceiro':'Thrust_Slash','espadachim':'Right_Hand_Sword_Slash','arqueiro':'Archery_Shot'}.get(u),'Hit':'Hit_Reaction','Death':'dying_backwards'};animations=[];proofs=[]
 for clip,key in names.items():
  if key is None:continue
  if clip=='Walk' and u in ['arqueiro','besteiro']:
   a=copy.deepcopy(original['animations'][0]);a['name']='Walk';animations.append(a);proofs.append({'clip':'Walk','source':'previous pilot GLB','sourceFileSha256':hashlib.sha256(old).hexdigest(),'sourceAnimationSha256':ahash(original,base,original['animations'][0]),'retainedExistingValues':True,'rootLocked':False});continue
  source=next(a for a in src['animations']if a['name']==key);a=copy.deepcopy(source);a['name']=clip;root_locked=False
  # Independent sampler copies avoid shared-accessor side effects.
  for c in a['channels']:
   name=src['nodes'][c['target']['node']]['name'];c['target']['node']=nodes[name];s=a['samplers'][c['sampler']];ss=source['samplers'][c['sampler']];s['input']=append(packed(src,sbin,ss['input']),src['accessors'][ss['input']]);data=packed(src,sbin,ss['output']);ac=src['accessors'][ss['output']]
   if clip in ['Idle','Attack','Hit'] and name=='Hips' and c['target']['path']=='translation':
    assert ac['type']=='VEC3' and ac['componentType']==5126 and s.get('interpolation','LINEAR')!='CUBICSPLINE';v=[list(r)for r in rows(src,sbin,ss['output'])];anchor=j['nodes'][nodes['Hips']]['translation']
    for r in v:r[0]=anchor[0];r[2]=anchor[2]
    data=b''.join(struct.pack('<fff',*r)for r in v);root_locked=True
   s['output']=append(data,ac)
  animations.append(a);proofs.append({'clip':clip,'source':key,'sourceFileSha256':hashlib.sha256(raw).hexdigest(),'sourceAnimationSha256':ahash(src,sbin,source),'rootLocked':root_locked,'modifiedComponents':['Hips.translation.x','Hips.translation.z']if root_locked else []})
 j['animations']=animations;pad=(-length)%4
 if pad:parts.append(bytes(pad));length+=pad
 j['buffers'][0]['byteLength']=length;js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);bin=b''.join(parts);out=struct.pack('<4sIIII',b'glTF',2,28+len(js)+len(bin),len(js),0x4e4f534a)+js+struct.pack('<II',len(bin),0x004e4942)+bin
 assert len(out)<50000000;(D/(u+'.glb')).write_bytes(out)
 # Preserve all geometry, skin and material descriptors and their original binary bytes.
 assert j['nodes']==original['nodes'] and j['skins']==original['skins'] and j['meshes']==original['meshes'] and j['materials']==original['materials'] and bin[:len(base)]==base
 for pr,a in zip(proofs,animations):pr['outputAnimationSha256']=ahash(j,bin,a)
 previous=json.loads((P/(u+'.verification.json')).read_text());previous.update({'sha256':hashlib.sha256(out).hexdigest(),'glbBytes':len(out),'clips':[],'rootLockCoordinateSystem':'glTF Y-up; constant Hips X/Z, original Y retained','sourceProof':proofs,'originalGeometrySkinMaterialsPreserved':True,'walkRetained':u in ['arqueiro','besteiro'],'rootDisplacementPerWalkCycle':None,'knownIssues':['No weapons or shields; no game integration.','Spear Walk is an infantry-walk approximation, not a dedicated march preset.']+(['Previous Prime Walk retained with root displacement and imperfect seam.']if u in ['arqueiro','besteiro']else[])+(['Attack intentionally omitted; future Forge3D clip to derive from Combat Idle.']if u=='besteiro'else[])})
 hashes=[]
 for a,pr in zip(animations,proofs):
  times=[r[0]for s in a['samplers']for r in rows(j,bin,s['input'])];ch=next(c for c in a['channels']if j['nodes'][c['target']['node']]['name']=='Hips'and c['target']['path']=='translation');v=rows(j,bin,a['samplers'][ch['sampler']]['output']);scale=j['nodes'][nodes['Armature']]['scale'];delta=[(v[-1][k]-v[0][k])*scale[k]for k in range(3)];extent=[(max(r[k]for r in v)-min(r[k]for r in v))*scale[k]for k in range(3)];clip={'name':a['name'],'durationSeconds':max(times)-min(times),'animationSha256':pr['outputAnimationSha256'],'rootDisplacementMeters':delta,'rootRangeMeters':extent,'horizontalRootRangeMeters':math.hypot(extent[0],extent[2]),'rootLocked':pr['rootLocked']};previous['clips'].append(clip);hashes.append(pr['outputAnimationSha256'])
  if a['name']=='Walk':previous['rootDisplacementPerWalkCycle']={'bone':'Hips','coordinateSystem':'glTF Y-up metres','vectorMeters':delta,'horizontalMeters':math.hypot(delta[0],delta[2]),'distanceMeters':math.sqrt(sum(x*x for x in delta)),'cycleCount':1,'durationSeconds':clip['durationSeconds']}
  if pr['rootLocked']:assert clip['horizontalRootRangeMeters']<1e-8
 assert len(set(hashes))==len(hashes)
 previous.pop('endpointMaxRotationDifferenceDegrees',None);previous.pop('blenderImportedBoneHeadMotion',None);previous['heightMeasurement']='Imported mesh bounds from the original pilot, unchanged geometry; metres.';previous['forwardAxis']={'glTF':'+Z','Blender':'-Y','evidence':'Original model orientation and eight-direction preview; original geometry and skin retained.'};previous['combatCreditsConsumed']=15;previous['retainedActionCostEquivalent']=9 if u=='besteiro'else(12 if u=='arqueiro'else 15);previous['walkCycleMeasurement']={'cycles':1,'durationSeconds':next(c['durationSeconds']for c in previous['clips']if c['name']=='Walk'),'source':'Previously selected contiguous Prime gait cycle'if previous['walkRetained']else'Full single-cycle Spear Walk preset','gameCadenceIntegrated':False};previous['preview']['walkSource']='Retained previous eight-direction images'if previous['walkRetained']else'Rerendered current Walk'
 (D/(u+'.verification.json')).write_text(json.dumps(previous,indent=2)+'\n');print('COMBAT_BUILT',u,len(animations),len(out),flush=True)
