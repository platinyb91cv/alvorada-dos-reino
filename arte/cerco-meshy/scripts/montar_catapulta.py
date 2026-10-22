# Catapulta 3D (0 créditos): modelada por código, peças rígidas presas a ossos. Clips Idle, Walk (uma volta das rodas),
# Attack (o braço dispara e a pedra sai), Hit, Death. Frente = +X (para onde a pedra voa). Metros reais.
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
OUT = os.environ['CAT_OUT']
lib = open('/tmp/claude-0/portao/montar_portao.py').read(); lib = lib[:lib.index('reset(); M = mats()')]
g = {'__name__': 'lib'}; exec(compile(lib, 'montar_portao.py', 'exec'), g)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
def flat(name, col, rough=.8, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal; return m
M = dict(wood=flat('madeira', (.23, .11, .045)), plank=flat('tabuas', (.36, .19, .08)), wood_lt=flat('madeira_clara', (.42, .25, .11)),
         iron=flat('ferro', (.13, .13, .14), .45, .8), cloth=flat('couro', (.3, .16, .07), .7), dirt=flat('corda', (.55, .42, .25), .9),
         stone=flat('pedra', (.42, .4, .37), .9), stone_dk=flat('pedra_esc', (.32, .3, .28), .9), banner=flat('estandarte', (.02, .1, .58), .85))
def part(obj, bone): obj['bone'] = bone; return obj
def bx(c, s, mat, bone, rot=None, name='p'):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    m = Matrix.Translation(c) @ (rot.to_4x4() if rot else Matrix()) @ Matrix.Diagonal((*s, 1))
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); me.materials.append(mat)
    bpy.context.scene.collection.objects.link(o); return part(o, bone)
def cyl(c, r, depth, mat, bone, axis='Y', seg=16, name='c'):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=depth)
    rot = Matrix.Rotation(math.radians(90), 4, 'X') if axis == 'Y' else (Matrix.Rotation(math.radians(90), 4, 'Y') if axis == 'X' else Matrix())
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ rot, verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); me.materials.append(mat)
    for p in me.polygons: p.use_smooth = True
    bpy.context.scene.collection.objects.link(o); return part(o, bone)
W, WD = M['wood'], M['plank']
# chassis
for y in (-.55, .55): bx(Vector((0, y, .62)), (3.3, .2, .24), WD, 'corpo')
for x in (-1.35, -.2, 1.0, 1.45): bx(Vector((x, 0, .62)), (.2, 1.3, .18), WD, 'corpo')
bx(Vector((.15, 0, .78)), (1.5, 1.0, .06), WD, 'corpo')  # estrado
# rodas (4) com raios
wheels = {'eixoF': 1.1, 'eixoT': -1.1}
for b, x in wheels.items():
    for y in (-.78, .78):
        cyl(Vector((x, y, .4)), .4, .12, W, b, seg=18)
        cyl(Vector((x, y * 1.06, .4)), .11, .1, M['iron'], b, seg=10)
        for k in range(4): bx(Vector((x, y * .97, .4)), (.06, .05, .74), M['wood_lt'], b, rot=Matrix.Rotation(math.radians(45 * k), 3, 'Y'))
    cyl(Vector((x, 0, .4)), .06, 1.5, W, b, seg=8)
# montantes em A e travessa de paragem
for y in (-.48, .48):
    bx(Vector((.55, y, 1.25)), (.16, .16, 1.35), W, 'corpo', rot=Matrix.Rotation(math.radians(-14), 3, 'Y'))
    bx(Vector((1.05, y, 1.15)), (.14, .14, 1.2), W, 'corpo', rot=Matrix.Rotation(math.radians(24), 3, 'Y'))
bx(Vector((.75, 0, 1.88)), (.24, 1.15, .22), W, 'corpo')
bx(Vector((.75, 0, 1.75)), (.3, .5, .08), M['cloth'], 'corpo')  # almofada de couro
# feixe de torção (corda)
PIV = Vector((.35, 0, .9))
cyl(PIV, .2, 1.05, M['dirt'], 'corpo', seg=14)
for y in (-.55, .55): cyl(Vector((PIV.x, y, PIV.z)), .26, .1, M['iron'], 'corpo', seg=14)
# braço (deitado para trás) com colher e pedra
L = 2.15
bx(PIV + Vector((-L / 2, 0, .05)), (L, .16, .16), W, 'braco')
cup = PIV + Vector((-L, 0, .14)); cyl(cup, .26, .14, WD, 'braco', axis='Z', seg=12)
for k in range(6): bx(cup + Vector((.24 * math.cos(k), .24 * math.sin(k), .1)), (.05, .05, .16), WD, 'braco')
ico = bmesh.new(); bmesh.ops.create_icosphere(ico, subdivisions=2, radius=.2); bmesh.ops.transform(ico, matrix=Matrix.Translation(cup + Vector((0, 0, .2))), verts=ico.verts)
me = bpy.data.meshes.new('pedra'); ico.to_mesh(me); ico.free(); pedra = bpy.data.objects.new('pedra', me); me.materials.append(M['stone_dk'] if 'stone_dk' in M else M['stone']); bpy.context.scene.collection.objects.link(pedra); part(pedra, 'pedra')
for p in me.polygons: p.use_smooth = True
# esqueleto
arm_d = bpy.data.armatures.new('Catapulta'); arm = bpy.data.objects.new('Catapulta', arm_d); bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
def bone(n, h, par=None):
    b = arm_d.edit_bones.new(n); b.head = h; b.tail = h + Vector((0, .3, 0)); b.roll = 0
    if par: b.parent = arm_d.edit_bones[par]
bone('corpo', Vector((0, 0, 0)))
for b, x in wheels.items(): bone(b, Vector((x, 0, .4)), 'corpo')
bone('braco', PIV, 'corpo'); bone('pedra', cup + Vector((0, 0, .2)), 'braco')
bpy.ops.object.mode_set(mode='OBJECT')
for o in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
    vg = o.vertex_groups.new(name=o['bone']); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    o.parent = arm; md = o.modifiers.new('Armature', 'ARMATURE'); md.object = arm
PB = arm.pose.bones
for pb in PB: pb.rotation_mode = 'XYZ'
bpy.context.scene.render.fps = 24
def act(name, n, fn):
    a = bpy.data.actions.new(name); arm.animation_data_create(); arm.animation_data.action = a
    for f in range(n + 1):
        t = f / n
        for pb in PB: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)
        fn(t)
        for pb in PB: pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_euler', frame=f); pb.keyframe_insert('scale', frame=f)
    tr = arm.animation_data.nla_tracks.new(); tr.name = name; tr.strips.new(name, 0, a); arm.animation_data.action = None
R = math.radians
act('Idle', 30, lambda t: None)
def walk(t):
    for b in wheels: PB[b].rotation_euler = (0, 2 * math.pi * t, 0)
    PB['corpo'].location = (0, 0, .012 * math.sin(4 * math.pi * t))
act('Walk', 32, walk)
def attack(t):  # dispara (0,25 do clip), bate na travessa, a pedra voa, o braço volta a baixar devagar
    if t < .22: a = R(98) * (t / .22) ** 2
    elif t < .32: a = R(98) - R(6) * math.sin(math.pi * (t - .22) / .1)
    else: a = R(98) * max(0, 1 - (t - .32) / .6) ** 1.4
    PB['braco'].rotation_euler = (0, a, 0)
    if t >= .2: PB['pedra'].scale = (0, 0, 0)  # a pedra saiu (o projétil do jogo continua o voo)
    elif t > .9: PB['pedra'].scale = (1, 1, 1)
    PB['corpo'].rotation_euler = (0, R(-2.5) * math.sin(math.pi * min(1, max(0, (t - .2) / .2))), 0)
act('Attack', 44, attack)
act('Hit', 24, lambda t: setattr(PB['corpo'], 'rotation_euler', (R(3) * math.sin(6 * math.pi * t) * (1 - t), 0, 0)))
def death(t):
    e = min(1, t / .8) ** 2
    PB['corpo'].rotation_euler = (R(-24) * e, 0, R(6) * e); PB['corpo'].location = (0, -.3 * e, -.18 * e)
    PB['braco'].rotation_euler = (0, R(-25) * e, R(10) * e); PB['pedra'].scale = (1 - e, 1 - e, 1 - e)
act('Death', 48, death)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True)
for o in bpy.context.scene.objects:
    if o.type == 'MESH': o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True)
print('OK', OUT, os.path.getsize(OUT))
