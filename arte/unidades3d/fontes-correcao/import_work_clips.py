import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent.parent;P=O.parent/'correcao-aldeao-guerreiro/segunda-volta'
for name in ['aldeao','guerreiro']:
 d=O/name;bpy.ops.wm.open_mainfile(filepath=str(d/(name+'-jogo.blend')));S=bpy.context.scene;r=json.loads((d/'build-report.json').read_text());rig=bpy.data.objects[r['rig']];body=bpy.data.objects[r['body']];rig.animation_data.action=None
 if name=='aldeao':
  evidence={}
  for state,clip in [('mine','Mine'),('build','Build'),('butcher','Butcher')]:
   for tr in rig.animation_data.nla_tracks:tr.mute=True
   before=set(bpy.data.objects);actions=set(bpy.data.actions);bpy.ops.import_scene.gltf(filepath=str(P/(state+'.glb')));extra=set(bpy.data.objects)-before;source=next(o for o in extra if o.type=='ARMATURE');action=next(a for a in bpy.data.actions if a not in actions)
   assert set(source.pose.bones.keys())==set(rig.pose.bones.keys())
   rest_error=max(((source.matrix_world@source.data.bones[p.name].head_local)-(rig.matrix_world@p.bone.head_local)).length for p in rig.pose.bones);assert rest_error<1e-4,(state,rest_error)
   for tr in source.animation_data.nla_tracks:tr.mute=True
   source.animation_data.action=action
   if action.slots:source.animation_data.action_slot=action.slots[0]
   start,end=action.frame_range;root=source.pose.bones['Hips'];rest=source.matrix_world@root.bone.head_local;rows=[];positions=[]
   for i in range(32):
    f=start+(end-start)*i/31;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();point=source.matrix_world@root.head;shift=Vector((rest.x-point.x,rest.y-point.y,0));root.location+=root.bone.matrix_local.to_3x3().inverted()@source.matrix_world.to_3x3().inverted()@shift;bpy.context.view_layer.update();positions.append({n:list(source.matrix_world@source.pose.bones[n].head)for n in ['Hips','Head','LeftHand','RightHand']});rows.append({p.name:(p.location.copy(),p.rotation_quaternion.copy(),p.scale.copy())for p in source.pose.bones})
   for ob in extra:bpy.data.objects.remove(ob,do_unlink=True)
   new=bpy.data.actions.new('MeshyPrime_'+clip);rig.animation_data.action=new
   for f,row in enumerate(rows,1):
    for p in rig.pose.bones:
     p.location,p.rotation_quaternion,p.scale=row[p.name]
     for channel in ['location','rotation_quaternion','scale']:p.keyframe_insert(data_path=channel,frame=f)
   rig.animation_data.action=None;track=next((tr for tr in rig.animation_data.nla_tracks if tr.name==clip),None)
   if track is None:track=rig.animation_data.nla_tracks.new();track.name=clip
   for strip in list(track.strips):track.strips.remove(strip)
   track.strips.new(clip,1,new)
   motion=json.loads((P/(state+'-motion-status.json')).read_text());retarget=json.loads((P/(state+'-retarget-status.json')).read_text());r['clips'][clip]={'source':'Meshy Text to Motion Prime: '+state,'frames':32,'motionTaskId':motion['id'],'retargetTaskId':retarget['id']};evidence[clip]={'sourceSha256':hashlib.sha256((P/(state+'.glb')).read_bytes()).hexdigest(),'sourceRestBoneErrorMeters':rest_error,'sourceFrameRange':[start,end],'motionCredits':motion['consumed_credits'],'retargetCredits':retarget['consumed_credits'],'sampledJoints':positions}
  assert len({v['sourceSha256']for v in evidence.values()})==3
  (d/'work-motion-provenance.json').write_text(json.dumps(evidence,indent=2))
 # Recalculate solid-tool normals after the geometry review.
 for kind,labels in r['props'].items():
  if kind not in ['axe','hoe','knife']:continue
  for label in labels:
   me=bpy.data.objects[label].data;bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 # Export the existing optimized body with all verified animation tracks.
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);body.select_set(True);bpy.context.view_layer.objects.active=rig
 if r['defaultProp']:
  for label in r['props'][r['defaultProp']]:ob=bpy.data.objects[label];ob.hide_set(False);ob.hide_render=False;ob.select_set(True)
 for tr in rig.animation_data.nla_tracks:tr.mute=False
 bpy.ops.export_scene.gltf(filepath=str(d/(name+'-jogo.glb')),export_format='GLB',use_selection=True,export_animations=True,export_skins=True,export_force_sampling=True,export_animation_mode='NLA_TRACKS')
 for tr in rig.animation_data.nla_tracks:tr.mute=tr.name!='Idle'
 S.frame_set(10);(d/'build-report.json').write_text(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(d/(name+'-jogo.blend')));print('WORK_CLIPS_INTEGRATED',name,list(r['clips']),flush=True)
