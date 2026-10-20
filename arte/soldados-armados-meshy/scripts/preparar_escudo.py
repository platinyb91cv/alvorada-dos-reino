# Escudo Meshy -> prop do Forge3D: centro na origem, face para +Y, Ø 0,62 m, ~1500 triângulos, texturas 512 px.
import bpy, bmesh, os, math
from mathutils import Vector, Matrix
SRC, OUT = os.environ['SRC'], os.environ['OUT']
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=SRC)
ms=[o for o in bpy.context.scene.objects if o.type=='MESH'];m=ms[0]
for o in list(bpy.context.scene.objects):
    if o is not m: bpy.data.objects.remove(o, do_unlink=True)
m.data.transform(m.matrix_world); m.matrix_world=Matrix(); m.parent=None
vs=[v.co.copy() for v in m.data.vertices]; c=sum(vs,Vector())/len(vs)
mn=Vector([min(v[i] for v in vs) for i in range(3)]); mx=Vector([max(v[i] for v in vs) for i in range(3)]); ctr=(mn+mx)/2
m.data.transform(Matrix.Translation(-ctr))
# eixo fino = normal da face; o lado com o umbo (vértices perto do centro mais salientes) é a frente
dims=mx-mn; thin=min(range(3),key=lambda i:dims[i]); R=max(dims)/2
near=[v.co for v in m.data.vertices if (v.co-v.co.project(Vector([1 if i==thin else 0 for i in range(3)]))).length<R*0.2]
sgn=1 if max(v[thin] for v in near)>-min(v[thin] for v in near) else -1
ax=Vector([1 if i==thin else 0 for i in range(3)])*sgn
rot=ax.rotation_difference(Vector((0,1,0))).to_matrix().to_4x4(); m.data.transform(rot)
m.data.transform(Matrix.Scale(0.62/(2*R),4))
bpy.context.view_layer.objects.active=m; mod=m.modifiers.new('dec','DECIMATE'); mod.ratio=1500/len(m.data.polygons); bpy.ops.object.modifier_apply(modifier='dec')
for img in bpy.data.images:
    if img.size[0]>512: img.scale(512,512)
m.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',use_selection=True)
print('ESCUDO', len(m.data.polygons), [round(x,3) for x in m.dimensions], 'frente', 'XYZ'[thin], sgn, os.path.getsize(OUT))
