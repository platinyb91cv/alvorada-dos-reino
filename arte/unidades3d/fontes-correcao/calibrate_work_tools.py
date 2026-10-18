import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent.parent;d=O/'aldeao';bpy.ops.wm.open_mainfile(filepath=str(d/'aldeao-jogo.blend'));S=bpy.context.scene;r=json.loads((d/'build-report.json').read_text());rig=bpy.data.objects[r['rig']];body=bpy.data.objects[r['body']];rig.animation_data.action=None
if 'build_hammer'not in r['props']:
 labels=[]
 for label in r['props']['hammer']:
  source=bpy.data.objects[label];copy=source.copy();copy.data=source.data.copy();copy.name='build_'+label;S.collection.objects.link(copy);labels.append(copy.name)
 r['props']['build_hammer']=labels
for kind,clip,phase,target in [('pick','Mine',13/31,(0,-.72,-.694)),('build_hammer','Build',.5,(0,-.98,-.2)),('knife','Butcher',.5,(0,-1,0))]:
 for tr in rig.animation_data.nla_tracks:tr.mute=tr.name!=clip
 f=1+31*phase;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();hand=rig.matrix_world@rig.pose.bones['RightHand'].head;shaft=bpy.data.objects[r['props'][kind][0]];v=list(shaft.data.vertices);axis=shaft.matrix_world.to_3x3()@(sum((p.co for p in v[10:]),Vector())/10-sum((p.co for p in v[:10]),Vector())/10);target=Vector(target).normalized();q=axis.normalized().rotation_difference(target)
 if kind=='knife':
  blade=bpy.data.objects[r['props'][kind][1]];width=blade.matrix_world.to_3x3()@(blade.data.vertices[1].co-blade.data.vertices[0].co);width=q@width;width=(width-target*width.dot(target)).normalized();desired=Vector((1,0,0));angle=math.atan2(target.dot(width.cross(desired)),width.dot(desired));q=Matrix.Rotation(angle,4,target).to_quaternion()@q
 rotation=Matrix.Translation(hand)@q.to_matrix().to_4x4()@Matrix.Translation(-hand)
 for label in r['props'][kind]:
  ob=bpy.data.objects[label];ob.matrix_world=rotation@ob.matrix_world
 bpy.context.view_layer.update()
blade=bpy.data.objects[r['props']['knife'][1]]
if not r['toolCorrection2'].get('knifeReadability'):
 width=(blade.data.vertices[1].co-blade.data.vertices[0].co).normalized();center=sum((v.co for v in blade.data.vertices),Vector())/len(blade.data.vertices)
 for v in blade.data.vertices:v.co+=width*((v.co-center).dot(width)*.25)
 blade.data.update()
steel=bpy.data.materials.get('ButcherKnifeSteel')or bpy.data.materials.new('ButcherKnifeSteel');steel.use_nodes=True;node=steel.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.72,.77,.85,1);node.inputs['Metallic'].default_value=.45;node.inputs['Roughness'].default_value=.3;blade.data.materials.clear();blade.data.materials.append(steel);r['toolCorrection2']['knifeReadability']='100mm broadside blade, cold steel contrast, horizontal grip'
r['toolCorrection2']['workToolBinding']='Rigid hand-space calibration for dedicated Meshy clips; pick downward strike, hammer at waist, knife horizontal and broadside.'
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);body.select_set(True);bpy.context.view_layer.objects.active=rig
for tr in rig.animation_data.nla_tracks:tr.mute=False
bpy.ops.export_scene.gltf(filepath=str(d/'aldeao-jogo.glb'),export_format='GLB',use_selection=True,export_animations=True,export_skins=True,export_force_sampling=True,export_animation_mode='NLA_TRACKS')
for tr in rig.animation_data.nla_tracks:tr.mute=tr.name!='Idle'
S.frame_set(10);(d/'build-report.json').write_text(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(d/'aldeao-jogo.blend'));print('WORK_TOOLS_CALIBRATED',flush=True)
