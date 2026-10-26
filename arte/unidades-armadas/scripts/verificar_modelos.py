import bpy,json,hashlib,struct,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parent;units=['aldeao','guerreiro','lanceiro','espadachim','arqueiro','besteiro'];summary=[]
for unit in units:
 D=R/unit;p=D/(unit+'-jogo.glb');raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);binary=raw[28+n:];assert raw[:4]==b'glTF' and len(raw)==struct.unpack_from('<I',raw,8)[0]
 def read(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];cols={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],cols),dtype='<f4',buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',cols*4),4)).copy()
 clips=[];roots={};digests=[];durations={}
 for c in j['animations']:
  digest=hashlib.sha256()
  for ch in c['channels']:
   a=read(c['samplers'][ch['sampler']]['output']);assert np.isfinite(a).all();digest.update(a.tobytes())
   if j['nodes'][ch['target']['node']].get('name')=='Hips' and ch['target']['path']=='translation':
    drift=max(float(np.ptp(a[:,0])),float(np.ptp(a[:,2])))*.01;roots[c['name']]=drift
    if c['name']!='Death':assert drift<1e-4,(unit,c['name'],drift)
  durations[c['name']]=max(float(read(s['input']).max()) for s in c['samplers']);digests.append(digest.hexdigest());clips.append(c['name'])
 assert {'Idle','Walk','Attack','Hit','Death'}<=set(clips);assert len(set(digests))==len(digests)
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==24
 report=json.loads((D/'build-report.json').read_text());proof={'unit':unit,'reimported':True,'reimportedClipsDistinct':True,'bones':24,'boneNames':list(rig.data.bones.keys()),'clips':clips,'horizontalRootDriftMetresByClip':roots,'sha256':hashlib.sha256(raw).hexdigest(),'sourceSha256':report['sourceSha256'],'bodyTriangles':report['triangles'],'bytes':len(raw),'additionalMeshyCredits':0,'supportHandMaximumResidualMetres':report.get('supportHandMaximumResidualMetres'),'source':'Existing Meshy models and motions; local posture/hand layers and villager retarget; no paid requests'};assert len(raw)<50*1024*1024
 proof['clipDurationsSeconds']=durations
 (D/'verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');summary.append(proof);print('MODEL_OK',unit,flush=True)
(R/'models.verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
