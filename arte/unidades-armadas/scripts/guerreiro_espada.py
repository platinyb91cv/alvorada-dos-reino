# Guerreiro com espada: tira o machado e põe a espada do espadachim presa ao osso da mão direita, na mesma posição relativa
import bpy,json
from mathutils import Vector
A='/tmp/claude-0/wt/arte/unidades-armadas/'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=A+'guerreiro.glb');G=set(bpy.data.objects)
rig=next(o for o in G if o.type=='ARMATURE');axe=bpy.data.objects['Meshy_axe'];body=bpy.data.objects['char1']
bpy.ops.import_scene.gltf(filepath=A+'espadachim.glb');E=[o for o in bpy.data.objects if o not in G]
erig=next(o for o in E if o.type=='ARMATURE');sw=next(o for o in E if o.name.startswith('Espada'));ebody=next(o for o in E if o.name.startswith('char1'))
def dom(o):
  vg={g.index:g.name for g in o.vertex_groups};acc={}
  for v in o.data.vertices:
    for g in v.groups:acc[vg[g.group]]=acc.get(vg[g.group],0)+g.weight
  return max(acc,key=acc.get)
b_sw,b_ax=dom(sw),dom(axe);print('BONES',b_sw,b_ax)
for o in (rig,erig):
  for t in o.animation_data.nla_tracks:t.mute=True
  o.animation_data.action=None
bpy.context.view_layer.update()
Be=erig.matrix_world@erig.data.bones[b_sw].matrix_local;Bg=rig.matrix_world@rig.data.bones[b_sw].matrix_local
# escala pela altura dos corpos em pose de repouso
he=ebody.dimensions.z*ebody.matrix_world.to_scale().z;hg=body.dimensions.z*body.matrix_world.to_scale().z;k=hg/he
from mathutils import Matrix
M=Bg@Matrix.Scale(k*.8,4)@Be.inverted()  # espada de uma mão, mais curta que a do espadachim
me=sw.data.copy();me.transform(sw.matrix_world);me.transform(M)
new=bpy.data.objects.new('Espada_guerreiro',me);bpy.context.scene.collection.objects.link(new)
new.vertex_groups.clear();g=new.vertex_groups.new(name=b_sw);g.add(list(range(len(me.vertices))),1.0,'REPLACE')
new.parent=rig;new.matrix_parent_inverse=rig.matrix_world.inverted();m=new.modifiers.new('Armature','ARMATURE');m.object=rig
for o in E:bpy.data.objects.remove(o,do_unlink=True)
bpy.data.objects.remove(axe,do_unlink=True)
for a in list(bpy.data.actions):
  if a.users==0:bpy.data.actions.remove(a)
print('K',round(k,3),len(me.vertices))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:o.select_set(True)
bpy.context.view_layer.objects.active=rig
for t in rig.animation_data.nla_tracks:t.mute=False
bpy.ops.export_scene.gltf(filepath='/tmp/claude-0/sp/hd/guerreiro-espada.glb',export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_skins=True)
print('OK')
