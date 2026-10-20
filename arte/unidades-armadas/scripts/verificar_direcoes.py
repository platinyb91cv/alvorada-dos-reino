import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;out=[]
for unit in ['aldeao','guerreiro','lanceiro','espadachim','arqueiro','besteiro']:
 D=R/unit;bpy.ops.wm.open_mainfile(filepath=str(D/(unit+'-jogo.blend')));r=json.loads((D/'build-report.json').read_text());rig=bpy.data.objects[r['rig']];body=bpy.data.objects[r['body']];rig.animation_data.action=None;bone='LeftHand' if unit=='arqueiro' else 'RightHand';g=body.vertex_groups[bone];ids=[v.index for v in body.data.vertices if any(x.group==g.index and x.weight>.85 for x in v.groups)];kind=r['defaultProp'] or 'axe';tool=bpy.data.objects[r['props'][kind][0]]
 pivot=bpy.data.objects.new('QA_Direction_Pivot',None);bpy.context.scene.collection.objects.link(pivot);mw=rig.matrix_world.copy();rig.parent=pivot;rig.matrix_world=mw;checks=[]
 for clip in ['Chop' if unit=='aldeao' else 'Idle','Attack']:
  for t in rig.animation_data.nla_tracks:t.mute=t.name!=clip
  tr=next(t for t in rig.animation_data.nla_tracks if t.name==clip);st=tr.strips[0];frame=(st.frame_start+st.frame_end)/2
  for direction in range(8):
   pivot.rotation_euler.z=direction*math.pi/4;bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(deps);me=ev.to_mesh();hand=sum((ev.matrix_world@me.vertices[i].co for i in ids),Vector())/len(ids);ev.to_mesh_clear();ev=tool.evaluated_get(deps);me=ev.to_mesh();distance=min((ev.matrix_world@v.co-hand).length for v in me.vertices);ev.to_mesh_clear();checks.append({'clip':clip,'direction':direction,'closestHandWeaponSurfaceMetres':distance})
  vals=[x['closestHandWeaponSurfaceMetres'] for x in checks if x['clip']==clip];assert max(vals)-min(vals)<.002,(unit,clip,vals);assert max(vals)<.09,(unit,clip,vals)
 out.append({'unit':unit,'passed':True,'rigidHandAndDirectionPivotVerified':True,'checks':checks});print('EIGHT_DIRECTION_GRIP_OK',unit,flush=True)
(R/'grip-directions.verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
