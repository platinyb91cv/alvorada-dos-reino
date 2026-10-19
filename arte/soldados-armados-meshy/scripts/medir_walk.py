# Mede o clip Walk de um corpo Meshy: duração, fps, ciclos (passos pelos pés), avanço da raiz e passada.
# Uso: blender -b --python medir_walk.py -- corpo.glb saida.json
import bpy, sys, json, math
from mathutils import Vector
import os
src, out = os.environ['MW_SRC'], os.environ['MW_OUT']
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=src)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
acts = {a.name: a for a in bpy.data.actions}
def act(name): return next(a for n, a in acts.items() if n.split('|')[-1].lower() == name.lower() or n.lower() == name.lower())
for o in bpy.context.scene.objects:
    if o.animation_data:
        for t in list(o.animation_data.nla_tracks): o.animation_data.nla_tracks.remove(t)
res = {'bones': len(arm.data.bones), 'boneNames': [b.name for b in arm.data.bones], 'clips': {}}
fwd = Vector((0, -1, 0))
for clip in ['Idle', 'Walk', 'Attack', 'Hit', 'Death']:
    try: a = act(clip)
    except StopIteration: res['clips'][clip] = None; continue
    arm.animation_data_create(); arm.animation_data.action = a
    try:
        if a.slots: arm.animation_data.action_slot = a.slots[0]
    except AttributeError: pass
    f0, f1 = a.frame_range; n = int(round(f1 - f0)); hips = arm.pose.bones['Hips']
    lf, rf = arm.pose.bones['LeftFoot'], arm.pose.bones['RightFoot']
    rows = []
    for i in range(n + 1):
        bpy.context.scene.frame_set(int(f0) + i); bpy.context.view_layer.update()
        h = arm.matrix_world @ hips.head; l = arm.matrix_world @ lf.head; r = arm.matrix_world @ rf.head
        rows.append((h.x, h.y, h.z, (l - r).dot(fwd), l.z, r.z))
    d = [r[3] for r in rows]; sign = [1 if x > 0 else -1 for x in d]
    crossings = sum(1 for i in range(1, len(sign)) if sign[i] != sign[i - 1])
    root = Vector((rows[-1][0] - rows[0][0], rows[-1][1] - rows[0][1], 0))
    H = max(r[2] for r in rows)
    res['clips'][clip] = {'frames': n, 'seconds': round(n / fps, 4), 'fps': fps, 'footCrossings': crossings,
        'cycles': round(crossings / 2, 2), 'rootHorizontalMetres': round(root.length, 4),
        'rootHorizontalMaxMetres': round(max(math.hypot(r[0] - rows[0][0], r[1] - rows[0][1]) for r in rows), 4),
        'footSeparationRangeMetres': round(max(d) - min(d), 4), 'hipsHeightMetres': round(H, 4),
        'footSeparationSeries': [round(x,3) for x in d] if clip == 'Walk' else None, 'walkLoopRootClose': round(math.hypot(rows[-1][0] - rows[0][0], rows[-1][1] - rows[0][1]), 4)}
json.dump(res, open(out, 'w'), indent=1)
