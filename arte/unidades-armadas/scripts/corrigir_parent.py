import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
for unit in ['aldeao','guerreiro','lanceiro','arqueiro','besteiro']:
 D=R/unit;bpy.ops.wm.open_mainfile(filepath=str(D/(unit+'-jogo.blend')));r=json.loads((D/'build-report.json').read_text());rig=bpy.data.objects[r['rig']];rig.animation_data.action=None
 if unit=='aldeao':
  for t in list(rig.animation_data.nla_tracks):
   if t.name not in r['clips']:rig.animation_data.nla_tracks.remove(t)
 for t in rig.animation_data.nla_tracks:t.mute=t.name!='Idle'
 bpy.context.scene.frame_set(1);bpy.context.view_layer.update();fixed=[]
 for labels in r['props'].values():
  for n in labels:
   o=bpy.data.objects[n];world=o.matrix_world.copy();o.parent=rig;o.parent_type='OBJECT';o.matrix_world=world;fixed.append(n)
 bpy.context.view_layer.update();r['rigidPropsFollowDirectionPivot']=fixed
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
 for n in r['bodyMeshes']+fixed:bpy.data.objects[n].hide_set(False);bpy.data.objects[n].select_set(True)
 for t in rig.animation_data.nla_tracks:t.mute=False
 bpy.context.view_layer.objects.active=rig;bpy.ops.export_scene.gltf(filepath=str(D/(unit+'-jogo.glb')),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True)
 for t in rig.animation_data.nla_tracks:t.mute=t.name!='Idle'
 (D/'build-report.json').write_text(json.dumps(r,indent=2),encoding='utf-8');bpy.ops.wm.save_as_mainfile(filepath=str(D/(unit+'-jogo.blend')))
 if (D/'fixed-camera.json').exists():(D/'fixed-camera.json').unlink()
 print('RIG_PARENT_FIXED',unit,flush=True)
