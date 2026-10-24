# Carroça (0 créditos): cavalo CC0 do Quaternius a puxar uma carroça modelada por código, com toldo azul (cor da equipa).
# A carroça fica presa ao osso 'root' (não abana com o galope); as rodas têm osso próprio. Clips: Idle, Walk (passo), Hit, Death.
import bpy, bmesh, math, os, re
from mathutils import Vector, Matrix
OUT = os.environ['CAR_OUT']; M_PER_U = 2.25 / 6.92; U = 1 / M_PER_U  # unidades do cavalo por metro
bpy.ops.wm.open_mainfile(filepath='/tmp/claude-0/cav/Horse.blend')
H = bpy.data.objects['Armature']; HM = bpy.data.objects['Horse']; H.name = 'Carroca'
acts = {a.name: a for a in bpy.data.actions}
for m in list(HM.data.materials):
    col = tuple(m.diffuse_color); nt = m.node_tree; nt.nodes.clear(); b = nt.nodes.new('ShaderNodeBsdfPrincipled'); o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(b.outputs[0], o.inputs[0]); b.inputs['Base Color'].default_value = col; b.inputs['Roughness'].default_value = .75
def flat(name, col, rough=.8, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal; return m
WD, WL, IR, TOLDO, SACO, OURO = flat('madeira', (.25, .12, .05)), flat('tabuas', (.4, .22, .1)), flat('ferro', (.13, .13, .14), .45, .8), flat('toldo', (.02, .1, .58), .85), flat('saco', (.62, .5, .32), .95), flat('ouro', (.8, .58, .15), .35, .9)
parts = []
def bx(c, s, mat, bone, name='p', rot=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c * U) @ (rot.to_4x4() if rot else Matrix()) @ Matrix.Diagonal((s[0] * U, s[1] * U, s[2] * U, 1)), verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); me.materials.append(mat); bpy.context.scene.collection.objects.link(o); o['bone'] = bone; parts.append(o); return o
def cyl(c, r, depth, mat, bone, axis='X', seg=16, name='c'):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r * U, radius2=r * U, depth=depth * U)
    rot = Matrix.Rotation(math.radians(90), 4, 'Y') if axis == 'X' else (Matrix.Rotation(math.radians(90), 4, 'X') if axis == 'Y' else Matrix())
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c * U) @ rot, verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); me.materials.append(mat)
    for p in me.polygons: p.use_smooth = True
    bpy.context.scene.collection.objects.link(o); o['bone'] = bone; parts.append(o); return o
# o cavalo olha para −Y; a carroça vai atrás (+Y). Medidas em metros.
y0 = 4.12 * M_PER_U + .25          # início da carroça logo atrás da garupa
L, Wd, zb = 2.0, 1.25, .78         # comprimento, largura, altura do estrado
yc = y0 + L / 2; R_ = .5            # raio das rodas
bx(Vector((0, yc, zb)), (Wd, L, .08), WL, 'root', 'estrado')
for x in (-Wd / 2, Wd / 2): bx(Vector((x, yc, zb + .22)), (.06, L, .38), WL, 'root', 'lado')
for y in (y0, y0 + L): bx(Vector((0, y, zb + .22)), (Wd, .06, .38), WL, 'root', 'topo')
for x in (-.42, .42): bx(Vector((x, (y0 - .9 + y0) / 2 - .2, zb + .1)), (.07, 1.9, .07), WD, 'root', 'varal', rot=Matrix.Rotation(math.radians(6), 3, 'X'))  # varais até ao cavalo
# toldo em arco (cor da equipa) com arcos de madeira
bm = bmesh.new(); NA, NY = 10, 6; vs = {}
for i in range(NA + 1):
    a = math.pi * i / NA
    for j in range(NY + 1):
        y = y0 + .1 + (L - .2) * j / NY; vs[i, j] = bm.verts.new((math.cos(a) * Wd * .52 * U, y * U, (zb + .4 + math.sin(a) * .62) * U))
for i in range(NA):
    for j in range(NY): bm.faces.new((vs[i, j], vs[i + 1, j], vs[i + 1, j + 1], vs[i, j + 1]))
me = bpy.data.meshes.new('toldo'); bm.to_mesh(me); bm.free(); t = bpy.data.objects.new('toldo', me); me.materials.append(TOLDO); bpy.context.scene.collection.objects.link(t)
t.modifiers.new('s', 'SOLIDIFY').thickness = .03 * U; t['bone'] = 'root'; parts.append(t)
for p in me.polygons: p.use_smooth = True
# carga visível atrás: sacos e um baú de ouro
for k, (dx, dy) in enumerate(((-.3, .25), (.25, .3), (0, .55))):
    o = cyl(Vector((dx, y0 + L - dy, zb + .28)), .2, .42, SACO, 'root', axis='Z', seg=10)
bx(Vector((0, y0 + L - .15, zb + .62)), (.45, .3, .28), WD, 'root', 'bau'); bx(Vector((0, y0 + L - .15, zb + .62)), (.47, .32, .05), OURO, 'root', 'aro')
# rodas (osso próprio)
for x in (-Wd / 2 - .1, Wd / 2 + .1):
    cyl(Vector((x, yc + .15, R_)), R_, .09, WD, 'rodas', seg=20)
    cyl(Vector((x, yc + .15, R_)), R_ * .98, .1, IR, 'rodas', seg=20).scale = (1, 1, 1)
    cyl(Vector((x * 1.04, yc + .15, R_)), .1, .14, IR, 'rodas', seg=10)
    for k in range(5): bx(Vector((x, yc + .15, R_)), (.05, .05, R_ * 1.9), WL, 'rodas', 'raio', rot=Matrix.Rotation(math.radians(36 * k), 3, 'X'))
cyl(Vector((0, yc + .15, R_)), .06, Wd + .3, WD, 'rodas', seg=8)
# osso das rodas no esqueleto do cavalo
bpy.context.view_layer.objects.active = H; bpy.ops.object.mode_set(mode='EDIT')
rb = H.data.edit_bones.new('rodas'); rb.head = Vector((0, (yc + .15) * U, R_ * U)); rb.tail = rb.head + Vector((.6 * U, 0, 0)); rb.parent = H.data.edit_bones['root']
bpy.ops.object.mode_set(mode='OBJECT')
for o in parts:
    vg = o.vertex_groups.new(name=o['bone']); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE'); o.parent = H; md = o.modifiers.new('Armature', 'ARMATURE'); md.object = H
PB = H.pose.bones
for pb in PB: pb.rotation_mode = 'QUATERNION'
def capture(act, t):
    H.animation_data.action = act
    try: H.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = act.frame_range; bpy.context.scene.frame_set(int(round(f0 + (f1 - f0) * t)))
    return {pb.name: (pb.location.copy(), pb.rotation_quaternion.copy()) for pb in PB if pb.name != 'rodas'}
H.animation_data_create()
CLIPS = [('Idle', 'Idle', 40, .3, 0), ('Walk', 'Walk', 32, 1, 1), ('Hit', 'Idle', 20, .1, 0), ('Death', 'Death', 40, 1, 0)]
for name, hn, n, span, roll in CLIPS:
    frames = [capture(acts[hn], (f / n) * span) for f in range(n + 1)]
    act = bpy.data.actions.new(name + '_c'); H.animation_data.action = act
    for f, cap in enumerate(frames):
        for pb in PB:
            if pb.name == 'rodas':
                ang = -2 * math.pi * (f / n) * roll  # uma volta das rodas por ciclo de passo
                pb.rotation_quaternion = Matrix.Rotation(ang, 3, 'Y').to_quaternion(); pb.location = (0, 0, 0)
                if name == 'Death': pb.rotation_quaternion = (1, 0, 0, 0)
            else: pb.location, pb.rotation_quaternion = cap[pb.name]
            if name == 'Death' and pb.name == 'root':  # a carroça tomba com o cavalo, para o lado
                e = min(1, f / n / .8) ** 2; pb.rotation_quaternion = Matrix.Rotation(math.radians(-14 * e), 3, 'Y').to_quaternion()
            pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_quaternion', frame=f)
    tr = H.animation_data.nla_tracks.new(); tr.name = name; tr.strips.new(name, 0, act); H.animation_data.action = None; print('CLIP', name, n)
for t_ in list(H.animation_data.nla_tracks):
    if t_.name not in ('Idle', 'Walk', 'Hit', 'Death'): H.animation_data.nla_tracks.remove(t_)
used = {st.action for t_ in H.animation_data.nla_tracks for st in t_.strips}
for a in list(bpy.data.actions):
    if a not in used: bpy.data.actions.remove(a)
for a in used: a.name = re.sub(r'_c$', '', a.name)
bpy.ops.object.select_all(action='DESELECT'); H.select_set(True)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.parent == H: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True)
print('OK', OUT, os.path.getsize(OUT))
