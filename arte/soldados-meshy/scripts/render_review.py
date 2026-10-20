import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
U=sys.argv[sys.argv.index('--unit')+1]
O=Path(__file__).resolve().parent.parent
TMP=Path(sys.argv[sys.argv.index('--output')+1]).resolve();TMP.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/(U+'.glb')));S=bpy.context.scene
rig=next(o for o in S.objects if o.type=='ARMATURE');widgets={p.custom_shape for p in rig.pose.bones if p.custom_shape};meshes=[o for o in S.objects if o.type=='MESH'and o not in widgets]
for o in widgets:
 if o:o.hide_render=True
assert meshes and rig.animation_data
clip=sys.argv[sys.argv.index('--clip')+1] if '--clip' in sys.argv else 'Walk'
tracks=list(rig.animation_data.nla_tracks)
chosen=[t for t in tracks if t.name==clip or any(st.name==clip or st.action.name==clip or st.action.name.startswith(clip+'_') for st in t.strips)]
assert len(chosen)==1,(clip,[t.name for t in tracks])
rig.animation_data.action=None
rig.animation_data.use_nla=True
for t in tracks:t.mute=t!=chosen[0]
strip=chosen[0].strips[0];start,end=strip.frame_start,strip.frame_end;S.render.fps=24
root=rig.pose.bones.get('Hips')or rig.pose.bones[0]
def frame(t):
 f=start+(end-start)*t;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
frame(0);points=[o.matrix_world@Vector(p)for o in meshes for p in o.bound_box];floor=min(p.z for p in points);height=max(p.z for p in points)-floor
pivot=bpy.data.objects.new('DirectionOnly',None);S.collection.objects.link(pivot)
for o in [rig]+[o for o in meshes if o.parent is None]:
 matrix=o.matrix_world.copy();o.parent=pivot;o.matrix_world=matrix
camera_data=bpy.data.cameras.new('PilotCamera');camera=bpy.data.objects.new('PilotCamera',camera_data);S.collection.objects.link(camera);S.camera=camera;camera_data.type='ORTHO';camera_data.ortho_scale=height*1.4
target=Vector((0,0,floor+height*.52));camera.location=target+Vector((6,-6,math.sqrt(72)/math.sqrt(3)));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=4;S.cycles.max_bounces=2;S.cycles.diffuse_bounces=1;S.cycles.glossy_bounces=1;S.cycles.transmission_bounces=0;S.cycles.use_denoising=True;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_x=S.render.resolution_y=128;S.render.resolution_percentage=100;S.render.film_transparent=True
S.world=bpy.data.worlds.new('PilotWorld');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.72,.8,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for name,position,power,size in [('Key',(3,-4,6),500,5),('Fill',(-4,-2,3),220,4),('Rim',(0,4,5),350,4)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;ob=bpy.data.objects.new(name,data);S.collection.objects.link(ob);ob.location=position;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
S.view_settings.view_transform='Standard';S.view_settings.look='None'
(TMP/'frames').mkdir(exist_ok=True)
labels=['SE','S','SW','W','NW','N','NE','E'];rows=[];samples=[]
for i in range(97):
 frame(i/96);samples.append({n:list(rig.matrix_world@rig.pose.bones[n].head)for n in ['Hips','LeftHand','RightHand','LeftFoot','RightFoot']if n in rig.pose.bones})
frame(0);first={p.name:p.matrix_basis.to_quaternion().copy()for p in rig.pose.bones};frame(1);seam={p.name:math.degrees(2*math.acos(min(1,abs(first[p.name].normalized().dot(p.matrix_basis.to_quaternion().normalized())))))for p in rig.pose.bones}
root_range={axis:max(s['Hips'][i]for s in samples)-min(s['Hips'][i]for s in samples)for i,axis in enumerate(['x','y','z'])}if 'Hips'in samples[0]else {}
# Camera tracking only. The Meshy action, armature and exported GLB stay untouched.
directions=[1] if clip!='Walk' else range(8)
for direction in directions:
 pivot.rotation_euler.z=math.pi/2-direction*math.pi/4
 count=8 if clip=='Walk' else 6
 for i in range(count):
  phase=i/count if clip=='Walk' else i/(count-1);frame(phase);root_world=rig.matrix_world@root.head;center=Vector((root_world.x,root_world.y,0));camera.location=target+center+Vector((6,-6,math.sqrt(72)/math.sqrt(3)));bpy.context.view_layer.update();anchor=world_to_camera_view(S,camera,Vector((root_world.x,root_world.y,floor)));body_points=[]
  for ob in meshes:
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());body_points.extend(world_to_camera_view(S,camera,ev.matrix_world@Vector(p))for p in ev.bound_box)
  reference=(max(p.y for p in body_points)-min(p.y for p in body_points))*320;row={'direction':direction,'label':labels[direction],'frame':i,'phase':phase,'anchor':[anchor.x*256,(1-anchor.y)*256],'bodyReferencePixels':reference};rows.append(row);S.render.filepath=str(TMP/'frames'/f'{direction:02d}-{i:02d}.png');bpy.ops.render.render(write_still=True)
 print('PILOT_DIRECTION_COMPLETE',direction,flush=True)
report={'sourceModelSha256':hashlib.sha256((O/(U+'.glb')).read_bytes()).hexdigest(),'animationSource':'Meshy library or retained Prime Walk','selectedClip':clip,'animationEdits':'Horizontal root locked in Idle, Attack, Hit only','cameraTrackingOnly':True,'frameRange':[start,end],'durationSeconds':(end-start)/24,'heightMeters':height,'bones':len(rig.data.bones),'triangles':sum(sum(len(p.vertices)-2 for p in ob.data.polygons)for ob in meshes),'rawClipEndpointRotationDifferenceDegrees':seam,'hipsWorldRangeMeters':root_range,'samples':samples,'frames':rows}
(TMP/'render-report.json').write_text(json.dumps(report,indent=2));print('PILOT_RENDER_COMPLETE',flush=True)
