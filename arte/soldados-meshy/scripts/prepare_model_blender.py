import bpy,json,sys
from pathlib import Path
O=Path(__file__).resolve().parent.parent/sys.argv[sys.argv.index('--unit')+1]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'model.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons)for o in meshes);assert triangles>1000
for o in meshes:
 bpy.context.view_layer.objects.active=o
 if triangles>100000:
  mod=o.modifiers.new('TechnicalRigInputBudget','DECIMATE');mod.ratio=100000/triangles;bpy.ops.object.modifier_apply(modifier=mod.name)
after=sum(sum(len(p.vertices)-2 for p in o.data.polygons)for o in meshes);assert after<300000
bpy.ops.export_scene.gltf(filepath=str(O/'model-rig-input.glb'),export_format='GLB',export_animations=False)
(O/'technical-preparation.json').write_text(json.dumps({'sourceTriangles':triangles,'rigInputTriangles':after,'animationEdits':False,'method':'local mesh decimation only; materials, UVs and global axes preserved; no paid Meshy remesh'},indent=2));print('MODEL_PREPARED',triangles,after,flush=True)
