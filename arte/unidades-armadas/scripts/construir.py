import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parent;O=R.parent;unit=sys.argv[sys.argv.index('--unit')+1];D=R/unit;D.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);S=bpy.context.scene;S.render.fps=24
src=O/'espadachim-comparacao/espadachim-postura-v2.glb' if unit=='espadachim' else O/'piloto-aldeao-meshy/walk-cycle.glb' if unit=='aldeao' else O/'soldados-armados-revisao/originais'/(unit+'.glb')
bpy.ops.import_scene.gltf(filepath=str(src));rig=next(o for o in S.objects if o.type=='ARMATURE');bodies=[o for o in S.objects if o.type=='MESH'];rig.animation_data.action=None
def pose(clip,phase):
 for t in rig.animation_data.nla_tracks:t.mute=t.name!=clip
 t=next(t for t in rig.animation_data.nla_tracks if t.name==clip);st=t.strips[0];f=st.frame_start+(st.frame_end-st.frame_start)*phase;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
def actionsamples(clip,count=33):
 rows=[]
 for i in range(count):
  pose(clip,i/(count-1));root=rig.pose.bones['Hips'];world=rig.matrix_world@root.matrix
  if clip!='Death':
   shift=Vector((-world.translation.x,-world.translation.y,0));root.location+=root.bone.matrix_local.to_3x3().inverted()@rig.matrix_world.to_3x3().inverted()@shift;bpy.context.view_layer.update()
  rows.append({p.name:(p.location.copy(),p.rotation_quaternion.copy(),p.scale.copy()) for p in rig.pose.bones})
 return rows
def install(clip,rows):
 rig.animation_data.action=None
 for t in rig.animation_data.nla_tracks:t.mute=True
 a=bpy.data.actions.new('Armed_'+clip);rig.animation_data.action=a
 for i,row in enumerate(rows,1):
  for n,(loc,q,scale) in row.items():
   p=rig.pose.bones[n];p.rotation_mode='QUATERNION';p.location=loc;p.rotation_quaternion=q;p.scale=scale
   for key in ('location','rotation_quaternion','scale'):p.keyframe_insert(data_path=key,frame=i,group=n)
 rig.animation_data.action=None;t=next((t for t in rig.animation_data.nla_tracks if t.name==clip),None)
 if t is None:t=rig.animation_data.nla_tracks.new();t.name=clip
 for st in list(t.strips):t.strips.remove(st)
 t.strips.new(clip,1,a)
retarget={};oldprops={}
if unit=='aldeao':
 # Retarget the already-paid and corrected work clips; preserve the new body.
 oldfile=O/'unidades-3d/aldeao/aldeao-jogo.blend';report=json.loads((oldfile.parent/'build-report.json').read_text());names=[report['rig']]+[n for ns in report['props'].values() for n in ns]
 with bpy.data.libraries.load(str(oldfile),link=False) as (a,b):b.objects=names
 loaded={o.name:o for o in b.objects if o};oldrig=next(o for o in b.objects if o and o.type=='ARMATURE')
 for o in b.objects:
  if o:S.collection.objects.link(o);o.hide_set(False)
 bpy.context.view_layer.update()
 oldrig.animation_data.action=None;tracks=list(oldrig.animation_data.nla_tracks)
 src_rest={n:(oldrig.matrix_world@oldrig.data.bones[n].matrix_local) for n in rig.pose.bones.keys()};dst_rest={n:(rig.matrix_world@rig.data.bones[n].matrix_local) for n in rig.pose.bones.keys()};scale=(dst_rest['Hips'].translation.z/src_rest['Hips'].translation.z)
 for track in tracks:
  clip=track.name
  if clip not in report['clips']:continue
  for t in tracks:t.mute=t!=track
  for t in rig.animation_data.nla_tracks:t.mute=True
  rows=[];st=track.strips[0];N=33
  for i in range(N):
   f=st.frame_start+(st.frame_end-st.frame_start)*i/(N-1);S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
   desired={n:((oldrig.matrix_world@oldrig.pose.bones[n].matrix).to_quaternion()@src_rest[n].to_quaternion().inverted()@dst_rest[n].to_quaternion()) for n in rig.pose.bones.keys()};row={}
   for p in rig.pose.bones:
    n=p.name;parent=p.parent;relative=((dst_rest[parent.name].inverted()@dst_rest[n]) if parent else (rig.matrix_world.inverted()@dst_rest[n]));pq=desired[parent.name] if parent else rig.matrix_world.to_quaternion();q=relative.to_quaternion().inverted()@pq.inverted()@desired[n];loc=Vector((0,0,0))
    if n=='Hips':
     point=oldrig.matrix_world@oldrig.pose.bones[n].head;delta=(point-src_rest[n].translation)*scale
     if clip!='Death':delta.x=delta.y=0
     loc=rig.data.bones[n].matrix_local.to_3x3().inverted()@rig.matrix_world.to_3x3().inverted()@delta
    row[n]=(loc,q,Vector((1,1,1)))
   rows.append(row)
  retarget[clip]=rows
 # Bring the existing tool meshes across as rigid geometry; no new generation.
 for t in tracks:t.mute=t.name!='Idle'
 S.frame_set(1);bpy.context.view_layer.update()
 for kind,labels in report['props'].items():
  oldprops[kind]=[]
  for label in labels:
   obj=next(o for o in b.objects if o and o.name.split('.')[0]==label);bone=obj.parent_bone;oldmatrix=obj.matrix_world.copy();hand=(oldrig.matrix_world@oldrig.pose.bones[bone].matrix);relative=hand.inverted()@oldmatrix
   world=rig.matrix_world@rig.data.bones[bone].matrix_local@relative
   mesh=obj.data.copy();ob=bpy.data.objects.new('Existente_'+label,mesh);S.collection.objects.link(ob)
   for v in mesh.vertices:v.co=world@v.co
   g=ob.vertex_groups.new(name=bone);g.add(list(range(len(mesh.vertices))),1,'REPLACE');mod=ob.modifiers.new('RigidHand','ARMATURE');mod.object=rig;oldprops[kind].append(ob.name)
 for obj in b.objects:
  if obj and obj.name in bpy.data.objects:bpy.data.objects.remove(obj,do_unlink=True)
 for t in list(rig.animation_data.nla_tracks):
  if t.name not in retarget:rig.animation_data.nla_tracks.remove(t)
 for clip,rows in retarget.items():install(clip,rows)
else:
 if unit!='espadachim':
  samples={t.name:actionsamples(t.name) for t in list(rig.animation_data.nla_tracks)}
  for clip,rows in samples.items():install(clip,rows)
 if unit=='besteiro':
  rows=actionsamples('Idle');
  for i,row in enumerate(rows):
   recoil=.07*math.exp(-((i/32-.48)/.10)**2)
   for bone in ('RightForeArm','LeftForeArm'):loc,q,s=row[bone];row[bone]=(loc,q@Quaternion(Vector((1,0,0)),recoil),s)
  install('Attack',rows)
# Close distal hand vertices using the same local edit as the approved pilot.
if unit!='espadachim':
 for mesh in bodies:
  for bone in ('RightHand','LeftHand'):
   group=mesh.vertex_groups.get(bone)
   if not group:continue
   bm=rig.matrix_world@rig.data.bones[bone].matrix_local;inv=bm.inverted()
   for v in mesh.data.vertices:
    weight=next((g.weight for g in v.groups if g.group==group.index),0)
    if weight<.85:continue
    p=inv@(mesh.matrix_world@v.co)
    if p.y<=13:continue
    angle=min(2.55,(p.y-13)/4.4);p.y=13+4.4*math.sin(angle);p.z+=4.4*(1-math.cos(angle));v.co=mesh.matrix_world.inverted()@(bm@p)
props=oldprops;bindings={};palm_cache={}
def palm_local(bone):
 if bone in palm_cache:return palm_cache[bone]
 points=[]
 for body in bodies:
  g=body.vertex_groups.get(bone)
  if g:points.extend(body.matrix_world@v.co for v in body.data.vertices if any(x.group==g.index and x.weight>.85 for x in v.groups))
 palm_cache[bone]=(rig.matrix_world@rig.data.bones[bone].matrix_local).inverted()@(sum(points,Vector())/len(points));return palm_cache[bone]
def add_meshy(kind,file,bone='RightHand',local=None):
 pose('Idle',0);before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(O/'armas-meshy-piloto/modelos'/file));meshes=[o for o in S.objects if o not in before and o.type=='MESH']
 if local is None:
  grip=palm_local(bone)
  local=Matrix.Translation(grip)@Matrix(((0,0,1),(1,0,0),(0,1,0))).to_4x4()@Matrix.Scale(100,4)
 rest=rig.matrix_world@rig.data.bones[bone].matrix_local@local
 for ob in meshes:
  mw=ob.matrix_world.copy()
  normal_matrix=(rest@mw).to_3x3().inverted().transposed();normals=[(normal_matrix@n.vector).normalized() for n in ob.data.corner_normals]
  for v in ob.data.vertices:v.co=rest@mw@v.co
  ob.data.normals_split_custom_set(normals)
  ob.matrix_world=Matrix.Identity(4);ob.name='Meshy_'+kind;g=ob.vertex_groups.new(name=bone);g.add(list(range(len(ob.data.vertices))),1,'REPLACE');mod=ob.modifiers.new('RigidHand','ARMATURE');mod.object=rig
 props[kind]=[o.name for o in meshes];bindings[kind]=(bone,local.copy())
if unit=='espadachim':props={'sword':[o.name for o in bodies[1:]]};bodies=bodies[:1]
elif unit=='guerreiro':add_meshy('axe','axe-2.glb')
elif unit=='lanceiro':add_meshy('spear','spear-2.glb')
elif unit=='arqueiro':
 # Calibrate bow upright in the guard pose, then keep its hand-local transform.
 pose('Attack',.4);m=rig.matrix_world@rig.pose.bones['LeftHand'].matrix;h=m@palm_local('LeftHand');world=Matrix.Translation(h)@Matrix.Rotation(math.pi,4,'Z');local=m.inverted()@world;add_meshy('bow','bow-2.glb','LeftHand',local)
elif unit=='besteiro':
 pose('Idle',.2);right=rig.matrix_world@rig.pose.bones['RightHand'].matrix;left=rig.matrix_world@rig.pose.bones['LeftHand'].matrix;forward=(left.translation-right.translation).normalized();up=Vector((0,0,1));x=up.cross(forward).normalized();y=forward.cross(x).normalized();rot=Matrix((x,y,forward)).transposed().to_4x4();world=Matrix.Translation(right@palm_local('RightHand'))@rot;add_meshy('crossbow','crossbow.glb','RightHand',right.inverted()@world)
elif unit=='aldeao':
 # Replace only the axe with the already-paid curved Meshy axe.
 for n in props.get('axe',[]):bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 add_meshy('axe','axe-2.glb')
support_errors=[]
if unit in ('guerreiro','lanceiro','besteiro','arqueiro'):
 def wm(n):return rig.matrix_world@rig.pose.bones[n].matrix
 def turn(n,q):
  m=wm(n);rig.pose.bones[n].matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(m.translation,q,m.to_scale());bpy.context.view_layer.update()
 def ik_left(target,side='Left'):
  upper,lower,hand=side+'Arm',side+'ForeArm',side+'Hand'
  a,b,c=[wm(n).translation.copy() for n in (upper,lower,hand)];l1=(b-a).length;l2=(c-b).length;axis=(target-a).normalized();distance=min((target-a).length,l1+l2-.001);bend=b-a-axis*(b-a).dot(axis)
  if bend.length<.001:bend=Vector((1,0,-1))-axis*axis.dot(Vector((1,0,-1)))
  bend.normalize();along=(l1*l1-l2*l2+distance*distance)/(2*distance);elbow=a+axis*along+bend*math.sqrt(max(0,l1*l1-along*along));turn(upper,(b-a).rotation_difference(elbow-a)@wm(upper).to_quaternion());b,c=[wm(n).translation for n in (lower,hand)];turn(lower,(c-b).rotation_difference(target-b)@wm(lower).to_quaternion());support_errors.append((wm(hand).translation-target).length)
 updated={};aim_yaw=0
 if unit=='arqueiro':
  pose('Attack',.5);delta=wm('LeftHand').translation-wm('RightHand').translation;aim_yaw=-math.pi/2-math.atan2(delta.y,delta.x)
 for clip in [t.name for t in rig.animation_data.nla_tracks if t.name!='Death']:
  if unit=='guerreiro' and clip not in ('Idle','Attack'):continue
  rows=[]
  for i in range(33):
   phase=i/32;pose(clip,phase)
   if unit=='guerreiro':
    axis=Vector((-.10,-.34,.94)) if clip=='Idle' else Vector((.1,-math.sin(math.pi*phase)*.9-.2,math.cos(math.pi*phase)*.9+.1));x=axis.normalized();fore=wm('RightHand').translation-wm('RightForeArm').translation;y=(fore-x*fore.dot(x)).normalized();turn('RightHand',Matrix((x,y,x.cross(y))).transposed().to_quaternion())
   elif unit in ('lanceiro','besteiro'):
    kind='spear' if unit=='lanceiro' else 'crossbow';bone,local=bindings[kind];forward=Vector((0,-.98,.15)) if clip=='Attack' or unit=='besteiro' else Vector((0,-.86,.51));forward.normalize();x=Vector((0,0,1)).cross(forward).normalized();y=forward.cross(x).normalized();weapon_q=Matrix((x,y,forward)).transposed().to_quaternion();hand_q=weapon_q@local.to_quaternion().inverted();turn(bone,hand_q);center=wm('Spine').translation+Vector((-.02,-.12-(.04*math.sin(phase*math.pi) if clip=='Attack' else 0),-.16));ik_left(center-wm(bone).to_3x3()@palm_local(bone),'Right');turn(bone,hand_q);grip=wm(bone)@local.translation;desired=grip+forward*.20;lx=-forward;ly=(Vector((0,0,-1))-lx*lx.dot(Vector((0,0,-1)))).normalized();lq=Matrix((lx,ly,lx.cross(ly))).transposed().to_quaternion();turn('LeftHand',lq);offset=wm('LeftHand').to_3x3()@palm_local('LeftHand');ik_left(desired-offset);turn('LeftHand',lq)
   else:
    if clip=='Attack':turn('Hips',Quaternion((0,0,1),aim_yaw)@wm('Hips').to_quaternion())
    bone,local=bindings['bow'];turn(bone,Quaternion((0,0,1),math.pi)@local.to_quaternion().inverted())
   rows.append({p.name:(p.location.copy(),p.rotation_quaternion.copy(),p.scale.copy()) for p in rig.pose.bones})
  updated[clip]=rows
 for clip,rows in updated.items():install(clip,rows)
default={'guerreiro':'axe','lanceiro':'spear','espadachim':'sword','arqueiro':'bow','besteiro':'crossbow','aldeao':None}[unit]
for kind,labels in props.items():
 for n in labels:
  o=bpy.data.objects[n];world=o.matrix_world.copy();o.parent=rig;o.parent_type='OBJECT';o.matrix_world=world;o.hide_render=kind!=default;o.hide_set(False)
clips={t.name:{'source':'existing Meshy clip/local approved offsets','frames':t.strips[0].frame_end-t.strips[0].frame_start+1} for t in rig.animation_data.nla_tracks}
for t in rig.animation_data.nla_tracks:t.mute=False
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for ob in bodies:ob.select_set(True)
for kind,labels in props.items():
 for n in labels:bpy.data.objects[n].select_set(True)
bpy.context.view_layer.objects.active=rig;bpy.ops.export_scene.gltf(filepath=str(D/(unit+'-jogo.glb')),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True)
pose('Idle',.2);S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=4;S.cycles.use_denoising=True;S.cycles.max_bounces=2;S.render.threads_mode='FIXED';S.render.threads=2;S.render.film_transparent=True;S.render.image_settings.file_format='PNG'
S.world=bpy.data.worlds.new('Warm studio');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[1].default_value=.45;S.view_settings.view_transform='AgX'
for loc,power,color in [((-3,-4,5),550,(1,.9,.78)),((4,-2,3),240,(.8,.88,1)),((1,3,4),400,(1,.9,.75))]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.size=4;light.data.color=color;light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(4,-4,3.3));S.camera=bpy.context.object;S.camera.data.type='ORTHO'
report={'unit':unit,'body':bodies[0].name,'bodyMeshes':[o.name for o in bodies],'rig':rig.name,'clips':clips,'props':props,'defaultProp':default,'bones':len(rig.data.bones),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bodies),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'newMeshyCredits':0,'localRetargetedClips':list(retarget),'supportHandMaximumResidualMetres':max(support_errors,default=0)}
(D/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');bpy.ops.wm.save_as_mainfile(filepath=str(D/(unit+'-jogo.blend')));print('ARMED_BUILT',unit,flush=True)
