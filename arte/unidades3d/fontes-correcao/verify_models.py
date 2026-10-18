import bpy,json,math,hashlib,sys
from pathlib import Path
O=Path(sys.argv[sys.argv.index('--sources')+1]).resolve()if '--sources'in sys.argv else Path(__file__).resolve().parent.parent
for unit in json.loads((O/'manifest.json').read_text())['units']:
 if '--unit'in sys.argv and unit['id']!=sys.argv[sys.argv.index('--unit')+1]:continue
 name=unit['id'];d=O/name;bpy.ops.wm.open_mainfile(filepath=str(d/(name+'-jogo.blend')));report=json.loads((d/'build-report.json').read_text());rig=bpy.data.objects[report['rig']];rig.animation_data.action=None;root=rig.pose.bones['Hips'];checks={};positions=[]
 for track in rig.animation_data.nla_tracks:track.mute=track.name!='Walk'
 samples=[]
 for i in range(49):
  f=1+23*i/48;bpy.context.scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();positions.append(rig.matrix_world@root.head);samples.append({n:rig.matrix_world@rig.pose.bones[n].matrix.translation for n in ('LeftFoot','RightFoot')})
 for foot in ('LeftFoot','RightFoot'):
  low=min(r[foot].z for r in samples);high=max(r[foot].z for r in samples);vel=[samples[i+1][foot].y-samples[i-1][foot].y for i in range(1,48)if samples[i][foot].z<low+(high-low)*.35];checks[foot]=sum(vel)/len(vel);assert checks[foot]>0,(name,foot,'reversed gait',checks)
 drift=max(math.hypot(p.x-positions[0].x,p.y-positions[0].y)for p in positions);assert drift<1e-4,(name,drift)
 aim_dot=None
 if name in ('arqueiro','besteiro'):
  for track in rig.animation_data.nla_tracks:track.mute=track.name!='Attack'
  bpy.context.scene.frame_set(16);bpy.context.view_layer.update();v=rig.matrix_world@(rig.pose.bones['LeftHand'].head-rig.pose.bones['RightHand'].head);v.z=0;v.normalize();aim_dot=-v.y;assert aim_dot>.9,(name,'aim misses forward target',aim_dot)
 rigidity={}
 for labels in report['props'].values():
  for label in labels:
   ob=bpy.data.objects[label];edge=ob.data.edges[0].vertices;lengths=[]
   for clip in report['clips']:
    for track in rig.animation_data.nla_tracks:track.mute=track.name!=clip
    for phase in (0,.5,1):
     bpy.context.scene.frame_set(1+round((report['clips'][clip]['frames']-1)*phase));bpy.context.view_layer.update();lengths.append(((ob.matrix_world@ob.data.vertices[edge[0]].co)-(ob.matrix_world@ob.data.vertices[edge[1]].co)).length)
   variation=max(lengths)-min(lengths);assert variation<1e-4,(name,label,variation);rigidity[label]=variation
 [bpy.data.objects.remove(ob,do_unlink=True)for ob in list(bpy.data.objects)];[bpy.data.actions.remove(a)for a in list(bpy.data.actions)];bpy.ops.import_scene.gltf(filepath=str(d/(name+'-jogo.glb')));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');actions=list(bpy.data.actions);reimport_clips={a.name for a in actions if a.name in report['clips']};assert set(report['clips']).issubset(reimport_clips),(name,reimport_clips);widgets={p.custom_shape for p in rig.pose.bones if p.custom_shape};meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'and o not in widgets];assert meshes and len(rig.data.bones)>=24;triangles=sum(sum(len(p.vertices)-2 for p in ob.data.polygons)for ob in meshes);assert triangles<8000,(name,triangles)
 rig.animation_data.action=None;clip_hashes={};roundtrip_drifts={}
 for clip in report['clips']:
  tracks=[t for t in rig.animation_data.nla_tracks if t.name==clip];assert tracks,(name,'missing exported track',clip);strip=tracks[0].strips[0];rows=[];roots=[]
  for track in rig.animation_data.nla_tracks:track.mute=track.name!=clip
  for phase in (0,.25,.5,.75,1):
   f=strip.frame_start+(strip.frame_end-strip.frame_start)*phase;bpy.context.scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();roots.append(rig.matrix_world@rig.pose.bones['Hips'].head);rows.extend(round(x,6)for bone in rig.pose.bones for row in (rig.matrix_world@bone.matrix) for x in row)
  clip_hashes[clip]=hashlib.sha256(json.dumps(rows).encode()).hexdigest();roundtrip_drifts[clip]=max(math.hypot(p.x-roots[0].x,p.y-roots[0].y)for p in roots);assert roundtrip_drifts[clip]<1e-4,(name,clip,'exported root drifts',roundtrip_drifts[clip])
 assert len(set(clip_hashes.values()))==len(clip_hashes),(name,'exported clips are identical')
 result={'reimportedClipPoseSha256':clip_hashes,'reimportedClipsDistinct':True,'reimportedRootDriftByClip':roundtrip_drifts,'optimizedGlbSha256':hashlib.sha256((d/(name+'-jogo.glb')).read_bytes()).hexdigest(),'unit':name,'reimported':True,'meshes':len(meshes),'triangles':triangles,'bones':len(rig.data.bones),'clips':sorted(reimport_clips),'forwardAimDot':aim_dot,'stanceVelocityY':checks,'rootHorizontalDrift':drift,'rigidProps':rigidity};(d/'verification.json').write_text(json.dumps(result,indent=2));print('VERIFIED_UNIT',json.dumps(result),flush=True)
