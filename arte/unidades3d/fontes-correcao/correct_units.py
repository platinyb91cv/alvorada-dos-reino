"""Local, reproducible corrections. Always start from the untouched source backup."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
O=Path(sys.argv[sys.argv.index('--sources')+1]).resolve()if '--sources'in sys.argv else Path(__file__).resolve().parent.parent
B=Path(sys.argv[sys.argv.index('--baseline')+1]).resolve()if '--baseline'in sys.argv else O.parent/'correcao-aldeao-guerreiro'/'antes'
names=[sys.argv[sys.argv.index('--unit')+1]]if '--unit'in sys.argv else ['aldeao','guerreiro']
for name in names:
 d=O/name;old=B/name;bpy.ops.wm.open_mainfile(filepath=str(old/(name+'-jogo.blend')))
 S=bpy.context.scene;r=json.loads((old/'build-report.json').read_text());rig=bpy.data.objects[r['rig']];body=bpy.data.objects[r['body']];rig.animation_data.action=None
 def pose(clip,t):
  for track in rig.animation_data.nla_tracks:track.mute=track.name!=clip
  f=1+(r['clips'][clip]['frames']-1)*t;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 def direction(bone,world):
  p=rig.pose.bones[bone];m=rig.matrix_world@p.matrix;current=m.to_3x3()@Vector((0,1,0));q=current.normalized().rotation_difference(Vector(world).normalized());center=m.translation.copy();p.matrix=rig.matrix_world.inverted()@Matrix.Translation(center)@q.to_matrix().to_4x4()@Matrix.Translation(-center)@m;bpy.context.view_layer.update()
 def twist(bone,angle):
  p=rig.pose.bones[bone];p.rotation_quaternion=p.rotation_quaternion@Quaternion((0,1,0),angle);bpy.context.view_layer.update()
 def capture():return {p.name:(p.location.copy(),p.rotation_quaternion.copy(),p.scale.copy())for p in rig.pose.bones}
 # Find consecutive forward extrema of the same foot: the old clip contains ~3 cycles.
 series=[]
 for i in range(481):
  pose('Walk',i/480);series.append((rig.matrix_world@rig.pose.bones['LeftFoot'].head).y)
 minima=[i for i in range(1,480)if series[i]<series[i-1]and series[i]<=series[i+1]]
 first=next((i for i in minima if i<70),0);second=next(i for i in minima if i>first+100)
 a,b=first/480,second/480
 ca,cb=0,1
 if name=='aldeao':
  ys=[]
  for i in range(481):pose('Carry',i/480);ys.append((rig.matrix_world@rig.pose.bones['LeftFoot'].head).y)
  mins=[i for i in range(1,480)if ys[i]<ys[i-1]and ys[i]<=ys[i+1]];cfirst=next(i for i in mins if i<100);csecond=next(i for i in mins if i>cfirst+100);ca,cb=cfirst/480,csecond/480
 originals={}
 for clip in ['Walk','Idle','Carry','Chop']:
  if clip not in r['clips']:continue
  length=r['clips'][clip]['frames'];rows=[]
  for f in range(length):
   t=f/(length-1);source='Idle'if clip=='Chop'else clip;pose(source,.2 if clip=='Chop'else a+(b-a)*t if clip=='Walk'else ca+(cb-ca)*t if clip=='Carry'else t)
   if clip in ('Walk','Idle','Carry'):
    # Preserve leg/root keys. Only the upper-body layer changes their pose.
    if name=='guerreiro':
     for spine in ['Spine02','Spine01','Spine']:direction(spine,(0,-.025,1))
     # Remove the source clip's lowered neck/chin and forward shoulder curl.
     for label in ['neck','Head','LeftShoulder','RightShoulder']:
      p=rig.pose.bones[label];m=rig.matrix_world@p.matrix;rest=rig.matrix_world.to_3x3()@p.bone.matrix_local.to_3x3();m=rest.to_4x4();m.translation=(rig.matrix_world@p.matrix).translation;p.matrix=rig.matrix_world.inverted()@m;bpy.context.view_layer.update()
    for side,sign in [('Left',1),('Right',-1)]:
     foot=rig.matrix_world@rig.pose.bones[side+'Foot'].head;hip=rig.matrix_world@rig.pose.bones['Hips'].head
     swing=-(foot.y-hip.y)*.48 if clip=='Walk'else .005*math.sin(t*2*math.pi)
     if clip=='Carry':
      direction(side+'Arm',(sign*.035,-.065,-.30));direction(side+'ForeArm',(-sign*.04,-.24,-.02))
     else:
      direction(side+'Arm',(sign*.025,swing,-.30));direction(side+'ForeArm',(sign*.025,-.10+swing*.35,-.26))
     twist(side+'Hand',sign*math.radians(65))
   if clip=='Chop':
    # Upright feet and hips from Idle; a distinct lift -> strike -> recovery.
    strike=math.exp(-((t-.53)/.12)**2);lift=(1-math.cos(2*math.pi*t))*.5
    direction('Spine02',(0,-.04-.18*strike,1))
    direction('RightArm',(-.08,-.25,.05+.36*lift-.75*strike))
    direction('RightForeArm',(.035,-.10-.40*strike,.32-.58*strike))
    direction('LeftArm',(.05,-.02,-.30));direction('LeftForeArm',(.02,-.12,-.25))
    # Orient the hand and the attached axe together: lift behind the head, then
    # strike forwards/down. Never hide, detach or independently deform the axe.
    keys=[(0,.3),(.2,-.3),(.35,-.55),(.5,1.9),(.65,2.0),(.8,.5),(1,.3)]
    lo,hi=next((keys[i],keys[i+1])for i in range(len(keys)-1)if keys[i][0]<=t<=keys[i+1][0])
    u=(t-lo[0])/(hi[0]-lo[0]);u=u*u*(3-2*u);angle=lo[1]+(hi[1]-lo[1])*u
    shaft=bpy.data.objects[r['props']['axe'][0]];v=shaft.data.vertices;axis=shaft.matrix_world.to_3x3()@(sum((x.co for x in list(v)[10:]),Vector())/10-sum((x.co for x in list(v)[:10]),Vector())/10)
    hand=rig.pose.bones['RightHand'];m=rig.matrix_world@hand.matrix;q=axis.normalized().rotation_difference(Vector((-.08,-math.sin(angle),math.cos(angle))).normalized());center=m.translation.copy();hand.matrix=rig.matrix_world.inverted()@Matrix.Translation(center)@q.to_matrix().to_4x4()@Matrix.Translation(-center)@m;bpy.context.view_layer.update()
   rows.append(capture())
  # Make all cyclic clips exactly seamless in the corrected action.
  if clip in ('Walk','Carry'):rows[-1]={k:tuple(v.copy()for v in vals)for k,vals in rows[0].items()}
  originals[clip]=rows
 for clip,rows in originals.items():
  track=next(t for t in rig.animation_data.nla_tracks if t.name==clip)
  for t in rig.animation_data.nla_tracks:t.mute=True
  action=bpy.data.actions.new('Corrected_'+clip);rig.animation_data.action=action
  for f,row in enumerate(rows,1):
   for p in rig.pose.bones:
    p.location,p.rotation_quaternion,p.scale=row[p.name]
    for path in ['location','rotation_quaternion','scale']:p.keyframe_insert(data_path=path,frame=f)
  rig.animation_data.action=None
  for strip in list(track.strips):track.strips.remove(strip)
  track.strips.new(clip,1,action)
 r['correction']={'sourceWalkInterval':[a,b],'sourceWalkCycles':1/(b-a),'sourceCarryInterval':[ca,cb]if name=='aldeao'else None,'upperBodyLayer':True,'newGenerations':0}
 if name=='aldeao':r['clips']['Chop']['source']='Idle + local upright lift/strike/recovery layer'
 # Enlarge existing tools about their hand grip, preserving their rigid attachment.
 for kind,labels in r['props'].items():
  if kind not in ['axe','pick','hammer','hoe','knife']:continue
  clip='Chop'if name=='aldeao'and kind=='axe'else 'Attack'if name=='guerreiro'else 'Harvest'if kind=='hoe'else 'Mine'
  # Original prop coordinates were calibrated at phase .3 of these unmodified clips.
  # Recover the original hand-space grip using a temporary old-scene-independent matrix.
  # Parent-bone origin is its tail: the grip is head minus the bone length in local Y.
  for label in labels:
   ob=bpy.data.objects[label]
   pose(clip,.3);hand=rig.matrix_world@rig.pose.bones[ob.parent_bone].head;local_grip=ob.matrix_world.inverted()@hand
   for v in ob.data.vertices:v.co=local_grip+(v.co-local_grip)*1.8
   if 'shaft'in label:
    # Existing shafts were created along local/world Z. 0.017 -> 0.048 m radius.
    center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
    for v in ob.data.vertices:v.co.x=center.x+(v.co.x-center.x)*1.57;v.co.y=center.y+(v.co.y-center.y)*1.57
   elif 'blade'in label:
    center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
    for v in ob.data.vertices:
     v.co.y=center.y+(v.co.y-center.y)*2.2
     if kind=='knife':v.co.x=center.x+(v.co.x-center.x)*1.3
   ob.data.update()
 if name=='aldeao':
  # Basket: an open low-poly container with rim and arched rigid handle.
  pose('Harvest',.3);hand=rig.matrix_world@rig.pose.bones['LeftHand'].head
  mat=bpy.data.materials.get('wood');verts=[];faces=[];N=12
  center=hand+Vector((0,-.02,-.35))
  for z,radius in [(0,.16),(.23,.22),(.23,.185),(.035,.13)]:
   verts.extend(center+Vector((radius*math.cos(i*2*math.pi/N),radius*math.sin(i*2*math.pi/N),z))for i in range(N))
  for level in range(3):
   for i in range(N):j=(i+1)%N;faces.append((level*N+i,level*N+j,(level+1)*N+j,(level+1)*N+i))
  faces.append(tuple(range(3*N,4*N)))
  # Thick arched handle meets the palm, with a silhouette visible at 30px.
  start=len(verts)
  for j in range(17):
   t=j*math.pi/16;c=center+Vector((-.21*math.cos(t),0,.23+.13*math.sin(t)))
   for k in range(6):verts.append(c+Vector((0,.025*math.cos(k*math.pi/3),.025*math.sin(k*math.pi/3))))
  for j in range(16):
   for k in range(6):faces.append((start+j*6+k,start+j*6+(k+1)%6,start+(j+1)*6+(k+1)%6,start+(j+1)*6+k))
  me=bpy.data.meshes.new('ForageBasket');me.from_pydata(verts,[],faces);ob=bpy.data.objects.new('forage_basket',me);S.collection.objects.link(ob);me.materials.append(mat)
  m=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='LeftHand';ob.matrix_world=m;r['props']['basket']=[ob.name]
 for objects in r['props'].values():
  for label in objects:ob=bpy.data.objects[label];ob.hide_render=True;ob.hide_set(True)
 default=r['defaultProp'];bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);body.select_set(True)
 if default:
  for label in r['props'][default]:ob=bpy.data.objects[label];ob.hide_render=False;ob.hide_set(False);ob.select_set(True)
 bpy.context.view_layer.objects.active=rig
 for t in rig.animation_data.nla_tracks:t.mute=False
 bpy.ops.export_scene.gltf(filepath=str(d/(name+'-jogo.glb')),export_format='GLB',use_selection=True,export_animations=True,export_skins=True,export_force_sampling=True,export_animation_mode='NLA_TRACKS')
 pose('Idle',.2);S.cycles.max_bounces=2;S.cycles.diffuse_bounces=1;S.cycles.glossy_bounces=1
 (d/'build-report.json').write_text(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(d/(name+'-jogo.blend')));print('CORRECTED',name,r['correction'],flush=True)
