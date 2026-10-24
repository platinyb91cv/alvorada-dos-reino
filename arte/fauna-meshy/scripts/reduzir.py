import bpy, os
SRC, OUT, N = os.environ['SRC'], os.environ['OUT'], int(os.environ.get('TRIS', '40000'))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=SRC)
m = next(o for o in bpy.context.scene.objects if o.type == 'MESH'); bpy.context.view_layer.objects.active = m
tris = sum(len(p.vertices) - 2 for p in m.data.polygons)
mod = m.modifiers.new('d', 'DECIMATE'); mod.ratio = min(1, N / tris); bpy.ops.object.modifier_apply(modifier='d')
for img in bpy.data.images:
    if img.size[0] > 2048: img.scale(2048, 2048)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True)
print('RED', tris, '->', sum(len(p.vertices) - 2 for p in m.data.polygons), os.path.getsize(OUT))
