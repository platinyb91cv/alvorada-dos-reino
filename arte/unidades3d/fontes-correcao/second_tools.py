"""Second review: wedge axe, flat hoe, visible knife. Uses first-review backup."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent.parent;B=O.parent/'correcao-aldeao-guerreiro/segunda-volta/antes'
for name in ['aldeao','guerreiro']:
 d=O/name;bpy.ops.wm.open_mainfile(filepath=str(B/name/(name+'-jogo.blend')));S=bpy.context.scene;r=json.loads((B/name/'build-report.json').read_text());rig=bpy.data.objects[r['rig']];body=bpy.data.objects[r['body']];rig.animation_data.action=None
 def pose(clip,t):
  for tr in rig.animation_data.nla_tracks:tr.mute=tr.name!=clip
  f=1+(r['clips'][clip]['frames']-1)*t;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 def shaft_axis(ob):
  v=list(ob.data.vertices);return (ob.matrix_world.to_3x3()@(sum((p.co for p in v[10:]),Vector())/10-sum((p.co for p in v[:10]),Vector())/10)).normalized()
 def geometry(ob,verts,faces):
  material=list(ob.data.materials);me=bpy.data.meshes.new(ob.name+'_review2');inv=ob.matrix_world.inverted();me.from_pydata([inv@Vector(v)for v in verts],[],faces);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();ob.data=me
  for mat in material:me.materials.append(mat)
 def cylinder(ob,hand,z,length,radius):
  x=z.cross(Vector((0,1,0))).normalized();y=z.cross(x);verts=[hand+z*t+radius*(math.cos(i*math.pi/5)*x+math.sin(i*math.pi/5)*y)for t in [-.3*length,.7*length]for i in range(10)];faces=[tuple(range(9,-1,-1)),tuple(range(10,20))]+[(i,(i+1)%10,(i+1)%10+10,i+10)for i in range(10)];geometry(ob,verts,faces)
 pose('Chop'if name=='aldeao'else 'Attack',.2);hand=rig.matrix_world@rig.pose.bones['RightHand'].head;shaft=bpy.data.objects[r['props']['axe'][0]];blade=bpy.data.objects[r['props']['axe'][1]];z=shaft_axis(shaft);x=shaft.matrix_world.to_3x3()@Vector((1,0,0));x=(x-z*x.dot(z)).normalized();y=z.cross(x);length=.65*1.4
 cylinder(shaft,hand,z,length,.032)
 # Flared, bearded cutting edge; thickness tapers towards the cutting edge.
 profile=[(-.025,-.05),(.065,-.07),(.235,-.115),(.285,-.065),(.285,.055),(.235,.11),(.065,.075),(-.025,.05)]
 verts=[hand+z*(length*.65+pz)+x*px+y*sign*(.030 if px<.08 else .006)for sign in [-1,1]for px,pz in profile];N=len(profile);faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)];geometry(blade,verts,faces)
 if name=='aldeao':
  # Clone Harvest, retaining its body motion, and steer only the hoe wrist.
  length=1.35;pose('Harvest',.5);shaft=bpy.data.objects[r['props']['hoe'][0]];handbone=rig.pose.bones['RightHand'];hand=rig.matrix_world@handbone.head;axis=shaft_axis(shaft)
  def down_axis(height):
   down=max(.15,min(.96,(height-.08)/(.7*length)));return Vector((0,-math.sqrt(1-down*down),-down))
  reference_axis=down_axis(hand.z);q=axis.rotation_difference(reference_axis);reference=rig.matrix_world@handbone.matrix;reference_rotation=q.to_matrix().to_4x4()@reference;reference_rotation.translation=Vector()
  samples=[]
  for i in range(40):
   t=i/39;pose('Harvest',t);hand=rig.matrix_world@handbone.head;axis=down_axis(hand.z);rotation=reference_axis.rotation_difference(axis).to_matrix().to_4x4();m=rotation@reference_rotation;m.translation=hand;handbone.matrix=rig.matrix_world.inverted()@m;bpy.context.view_layer.update();samples.append({p.name:(p.location.copy(),p.rotation_quaternion.copy(),p.scale.copy())for p in rig.pose.bones})
  for tr in rig.animation_data.nla_tracks:tr.mute=True
  action=bpy.data.actions.new('Farm_Hoe_WristLayer');rig.animation_data.action=action
  for f,row in enumerate(samples,1):
   for p in rig.pose.bones:
    p.location,p.rotation_quaternion,p.scale=row[p.name]
    for channel in ['location','rotation_quaternion','scale']:p.keyframe_insert(data_path=channel,frame=f)
  rig.animation_data.action=None;track=rig.animation_data.nla_tracks.new();track.name='Farm';track.strips.new('Farm',1,action);r['clips']['Farm']={'source':'Harvest + local hoe wrist orientation layer','frames':40}
  pose('Farm',.5);hand=rig.matrix_world@handbone.head;axis=down_axis(hand.z);cylinder(shaft,hand,axis,length,.028)
  # Flat trapezoid blade faces the ground in the working pose, not a hammer block.
  blade=bpy.data.objects[r['props']['hoe'][1]];center=hand+axis*(.7*length);profile=[(-.11,.015),(.11,.015),(.15,-.19),(-.15,-.19)];verts=[center+Vector((x,y,z))for z in [-.009,.009]for x,y in profile];geometry(blade,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
  pose('Mine',.3);hand=rig.matrix_world@handbone.head;shaft=bpy.data.objects[r['props']['knife'][0]];axis=shaft_axis(shaft);x=shaft.matrix_world.to_3x3()@Vector((1,0,0));x=(x-axis*x.dot(axis)).normalized();y=axis.cross(x);cylinder(shaft,hand,axis,.24,.023)
  blade=bpy.data.objects[r['props']['knife'][1]];profile=[(-.035,.08),(.035,.08),(.04,.26),(-.025,.36),(-.035,.28)];verts=[hand+axis*z+x*xx+y*sign*.0075 for sign in [-1,1]for xx,z in profile];N=5;geometry(blade,verts,[tuple(range(4,-1,-1)),tuple(range(5,10))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)])
 r['toolCorrection2']={'axeScaleVsOriginal':1.4,'axeHead':'tapered flared wedge, 60mm socket to 12mm edge','hoeBlade':'flat 18mm trapezoid, ground-facing wrist layer'if name=='aldeao'else None,'newCharacterGenerations':0}
 for kinds in r['props'].values():
  for label in kinds:ob=bpy.data.objects[label];ob.hide_set(True);ob.hide_render=True
 if r['defaultProp']:
  for label in r['props'][r['defaultProp']]:ob=bpy.data.objects[label];ob.hide_set(False);ob.hide_render=False
 pose('Idle',.2);(d/'build-report.json').write_text(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(d/(name+'-jogo.blend')));print('SECOND_TOOLS_READY',name,flush=True)
