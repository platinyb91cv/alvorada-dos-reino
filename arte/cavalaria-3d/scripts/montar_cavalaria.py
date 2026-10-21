# Cavalaria 3D (0 créditos): cavalo CC0 do Quaternius (Farm Animals Pack) + cavaleiro Meshy já existente sentado na sela.
# Junta os dois esqueletos num só, coze clips combinados (cavalo + tronco do cavaleiro, pernas montadas fixas)
# e acrescenta uma manta azul (cor da equipa) presa ao tronco do cavalo. Exporta um GLB com clips NLA:
# Idle, Walk (galope), Attack, Hit, Death.  Uso: HORSE=Horse.blend RIDER=<soldado.glb> OUT=<saida.glb> blender -b --python
import bpy, os, math, bmesh
from mathutils import Vector, Matrix, Quaternion, Euler

HORSE, RIDER, OUT = os.environ['HORSE'], os.environ['RIDER'], os.environ['OUT']
M_PER_U = 2.25 / 6.92          # o cavalo (até ao topo da cabeça) mede 2,25 m
RIDER_H = float(os.environ.get('RIDER_H', '1.70'))
bpy.ops.wm.open_mainfile(filepath=HORSE)
H = bpy.data.objects['Armature']; HM = bpy.data.objects['Horse']; H.name = 'Cavalaria'
horse_acts = {a.name: a for a in bpy.data.actions}
for m in list(HM.data.materials):  # materiais do pack com vários nós de saída: um Principled simples (exporta para glTF)
    col = tuple(m.diffuse_color); nt = m.node_tree; nt.nodes.clear()
    bs = nt.nodes.new('ShaderNodeBsdfPrincipled'); out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(bs.outputs[0], out.inputs[0])
    bs.inputs['Base Color'].default_value = col; bs.inputs['Roughness'].default_value = .75
for a in horse_acts.values(): a.use_fake_user = True
# ---------- cavaleiro ----------
before = set(bpy.data.actions); bobjs = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=RIDER)
rider_acts = {a.name: a for a in bpy.data.actions if a not in before}
for a in rider_acts.values(): a.use_fake_user = True
new = [o for o in bpy.data.objects if o not in bobjs]
RA = next(o for o in new if o.type == 'ARMATURE')
for o in new:
    if o.type == 'MESH' and o.parent is None: bpy.data.objects.remove(o, do_unlink=True)  # icosfera de referência
RM = [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == RA]
RA.animation_data_clear() if RA.animation_data else None
bpy.context.view_layer.update()
def wpos(arm, b): return arm.matrix_world @ arm.data.bones[b].head_local
body = next(o for o in RM if o.name.startswith('char'))
zs = [(body.matrix_world @ v.co).z for v in body.data.vertices]; h_now = max(zs) - min(zs)
k = (RIDER_H / M_PER_U) / h_now
fwd = (wpos(RA, 'headfront') - wpos(RA, 'Head')); fwd.z = 0; fwd.normalize()
ang = math.atan2(fwd.x, fwd.y) - math.atan2(0, -1)  # rodar para olhar para −Y (frente do cavalo)
RA.matrix_world = Matrix.Rotation(-ang, 4, 'Z') @ Matrix.Scale(k, 4) @ RA.matrix_world
bpy.context.view_layer.update()
# sela: ponto mais alto do dorso do cavalo perto do centro
hv = [HM.matrix_world @ v.co for v in HM.data.vertices]
yc = (H.matrix_world @ H.data.bones['Torso'].head_local).y - .25
top = max(v.z for v in hv if abs(v.y - yc) < .35 and abs(v.x) < .3)
hips = wpos(RA, 'Hips'); seat = Vector((0, yc, top + .12 / M_PER_U))
RA.matrix_world = Matrix.Translation(seat - hips) @ RA.matrix_world
bpy.context.view_layer.update()
# ---------- manta (cor da equipa) moldada ao dorso por raycast ----------
import mathutils; dg = bpy.context.evaluated_depsgraph_get(); bvh = mathutils.bvhtree.BVHTree.FromObject(HM, dg)
bm = bmesh.new(); NT, NY = 14, 8; vs = {}
for i in range(NT + 1):
    th = math.radians(-105 + 210 * i / NT)
    for j in range(NY + 1):
        y = yc - 1.05 + 2.1 * j / NY; d = Vector((math.sin(th), 0, math.cos(th)))
        o = Vector((0, y, 3.75)) + d * 6; hit = bvh.ray_cast(o, -d)
        p = (hit[0] + d * .07) if hit[0] else Vector((0, y, 3.75)) + d * 1.4
        vs[i, j] = bm.verts.new(p)
for i in range(NT):
    for j in range(NY): bm.faces.new((vs[i, j], vs[i, j + 1], vs[i + 1, j + 1], vs[i + 1, j]))
for e in bm.edges:  # orla dourada nas bordas
    pass
me = bpy.data.meshes.new('manta'); bm.to_mesh(me); bm.free()
manta = bpy.data.objects.new('manta', me); bpy.context.scene.collection.objects.link(manta)
manta.modifiers.new('esp', 'SOLIDIFY').thickness = .05
mt = bpy.data.materials.new('manta'); mt.use_nodes = True; bs = mt.node_tree.nodes['Principled BSDF']
bs.inputs['Base Color'].default_value = (.02, .1, .58, 1); bs.inputs['Roughness'].default_value = .85; me.materials.append(mt)
for p in me.polygons: p.use_smooth = True
vg = manta.vertex_groups.new(name='Torso'); vg.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
manta.parent = H; am = manta.modifiers.new('Armature', 'ARMATURE'); am.object = H
# ---------- juntar esqueletos (ossos do cavaleiro com prefixo R_) ----------
rmap = {}
for b in RA.data.bones: rmap[b.name] = 'R_' + b.name
for o in RM:
    for g in o.vertex_groups:
        if g.name in rmap: g.name = rmap[g.name]
for b in list(RA.data.bones): b.name = rmap.get(b.name, b.name)
RW = {o.name: o.matrix_world.copy() for o in RM}  # posição real de cada malha do cavaleiro antes de juntar
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o.name.startswith('Icosphere'): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
RA.select_set(True); H.select_set(True); bpy.context.view_layer.objects.active = H
bpy.ops.object.join()
bpy.ops.object.mode_set(mode='EDIT')
H.data.edit_bones['R_Hips'].parent = H.data.edit_bones['Torso']; H.data.edit_bones['R_Hips'].use_connect = False
bpy.ops.object.mode_set(mode='OBJECT')
for o in bpy.data.objects:  # malhas do cavaleiro: coordenadas no espaço do esqueleto, sem transformações soltas
    if o.type == 'MESH' and o.name in RW:
        mw = RW[o.name]; o.parent = H; o.matrix_parent_inverse = Matrix(); o.matrix_basis = Matrix()
        o.data.transform(H.matrix_world.inverted() @ mw)
        if not any(md.type == 'ARMATURE' for md in o.modifiers): o.modifiers.new('Armature', 'ARMATURE')
        for md in o.modifiers:
            if md.type == 'ARMATURE': md.object = H
PB = H.pose.bones
for pb in PB: pb.rotation_mode = 'QUATERNION'
# ---------- pose montada das pernas (escolhe os sinais pela geometria) ----------
def wp(b): return H.matrix_world @ PB[b].head
def set_leg(side):
    up, lo, ft = f'R_{side}UpLeg', f'R_{side}Leg', f'R_{side}Foot'
    best = None
    for sx in (1, -1):
        PB[up].rotation_quaternion = Quaternion((1, 0, 0), math.radians(78 * sx)); bpy.context.view_layer.update()
        kn = wp(lo); sc = -kn.y + kn.z * .2
        if best is None or sc > best[0]: best = (sc, sx)
    q1 = Quaternion((1, 0, 0), math.radians(78 * best[1])); best2 = None
    for sz in (1, -1):
        PB[up].rotation_quaternion = q1 @ Quaternion((0, 0, 1), math.radians(18 * sz)); bpy.context.view_layer.update()
        sc = abs(wp(lo).x)
        if best2 is None or sc > best2[0]: best2 = (sc, sz)
    PB[up].rotation_quaternion = q1 @ Quaternion((0, 0, 1), math.radians(18 * best2[1])); best3 = None
    for sk in (1, -1):
        PB[lo].rotation_quaternion = Quaternion((1, 0, 0), math.radians(85 * sk)); bpy.context.view_layer.update()
        f = wp(ft); sc = f.y - f.z * .3
        if best3 is None or sc > best3[0]: best3 = (sc, sk)
    PB[lo].rotation_quaternion = Quaternion((1, 0, 0), math.radians(85 * best3[1]))
    return {up: PB[up].rotation_quaternion.copy(), lo: PB[lo].rotation_quaternion.copy()}
for pb in PB: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
H.animation_data_create(); H.animation_data.action = None; bpy.context.view_layer.update()
LEGS = {}; LEGS.update(set_leg('Left')); LEGS.update(set_leg('Right'))
print('PERNAS', {k: tuple(round(x, 3) for x in v) for k, v in LEGS.items()})
FIX = set(LEGS) | {'R_Hips', 'R_LeftFoot', 'R_RightFoot', 'R_LeftToeBase', 'R_RightToeBase'}
# ---------- clips combinados ----------
def fcurves_of(a):
    try: return list(a.fcurves)
    except AttributeError: pass
    out = []
    for L in a.layers:
        for s in L.strips:
            for cb in s.channelbags: out += list(cb.fcurves)
    return out
def rider_values(act, t):  # t em [0,1]: valores das rotações do cavaleiro (sem localizações)
    f0, f1 = act.frame_range; fr = f0 + (f1 - f0) * t; vals = {}
    for fc in fcurves_of(act):
        dp = fc.data_path
        if not dp.startswith('pose.bones["') or not dp.endswith('rotation_quaternion'): continue
        b = dp.split('"')[1]; b = rmap.get(b, b)
        vals.setdefault(b, [1, 0, 0, 0])[fc.array_index] = fc.evaluate(fr)
    return vals
def horse_capture(act, t):
    H.animation_data.action = act
    try: H.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = act.frame_range; bpy.context.scene.frame_set(int(round(f0 + (f1 - f0) * t)))
    return {pb.name: (pb.location.copy(), pb.rotation_quaternion.copy(), pb.scale.copy()) for pb in PB if not pb.name.startswith('R_')}
import re; ra = {re.sub(r'\.\d+$', '', n.split('|')[-1]): a for n, a in rider_acts.items()}; print('RIDER_ACTS', list(ra))
CLIPS = [('Idle', 'Idle', 'Idle', 40), ('Walk', 'Run', 'Idle', 20), ('Attack', 'Idle', 'Attack', 36), ('Hit', 'Idle', 'Hit', 24), ('Death', 'Death', 'Death', 40)]
for name, hn, rn, n in CLIPS:
    act = bpy.data.actions.new(name); frames = []
    for f in range(n + 1):
        t = f / n; cap = horse_capture(horse_acts[hn], t if hn != 'Idle' or name == 'Idle' else t * .25)
        rv = rider_values(ra[rn], t); frames.append((cap, rv))
    c0, c1 = frames[0][0]['Body'], frames[n // 2][0]['Body']; r0, r1 = frames[0][1].get('R_RightArm'), frames[n // 2][1].get('R_RightArm')
    print('DBG', name, tuple(round(x, 3) for x in c0[1]), tuple(round(x, 3) for x in c1[1]), r0 and [round(x, 3) for x in r0], r1 and [round(x, 3) for x in r1])
    H.animation_data.action = act
    for f, (cap, rv) in enumerate(frames):
        for pb in PB:
            if pb.name in cap: pb.location, pb.rotation_quaternion, pb.scale = cap[pb.name]
            elif pb.name in LEGS: pb.rotation_quaternion = LEGS[pb.name]; pb.location = (0, 0, 0)
            elif pb.name in FIX: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
            else: pb.rotation_quaternion = Quaternion(rv.get(pb.name, (1, 0, 0, 0))); pb.location = (0, 0, 0)
            pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_quaternion', frame=f); pb.keyframe_insert('scale', frame=f)
    vv = [fc for L in act.layers for st in L.strips for cb in st.channelbags for fc in cb.fcurves]
    print('KEYS', name, len(vv), sum(1 for fc in vv if max(k.co[1] for k in fc.keyframe_points) - min(k.co[1] for k in fc.keyframe_points) > 1e-3))
    tr = H.animation_data.nla_tracks.new(); tr.name = name; tr.strips.new(name, 0, act); H.animation_data.action = None
    print('CLIP', name, n)
for a in list(horse_acts.values()) + list(rider_acts.values()): a.use_fake_user = False; bpy.data.actions.remove(a)
for img in bpy.data.images:
    if img.size[0] > 1024: img.scale(1024, 1024)
bpy.context.scene.render.fps = 24
for pb in H.pose.bones: pb.custom_shape = None
for t in list(H.animation_data.nla_tracks):
    if t.name not in ('Idle', 'Walk', 'Attack', 'Hit', 'Death'): H.animation_data.nla_tracks.remove(t)
used = {st.action for t in H.animation_data.nla_tracks for st in t.strips}
for a_ in list(bpy.data.actions):
    if a_ not in used: bpy.data.actions.remove(a_)
for a_ in used: a_.name = a_.name.split('.')[0]
print('TRACKS', [t.name for t in H.animation_data.nla_tracks])
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o.name.startswith('Icosphere'): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT'); H.select_set(True)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.parent == H: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True)
print('OK', OUT, os.path.getsize(OUT), 'm/u', M_PER_U)
