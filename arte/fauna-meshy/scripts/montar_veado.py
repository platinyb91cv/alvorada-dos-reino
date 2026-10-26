# Veado Meshy (estático) -> GLB riggado e animado no Blender (0 créditos): esqueleto de quadrúpede,
# pesos automáticos, clips Idle, Walk (trote no lugar), Attack (investida com as hastes), Hit, Death.
import bpy, math, os
from mathutils import Vector, Matrix, Euler
SRC, OUT, SCALE = os.environ['SRC'], os.environ['OUT'], float(os.environ.get('SCALE', '1.05'))
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions): bpy.data.actions.remove(a)
bpy.ops.import_scene.gltf(filepath=SRC)
m = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
for o in list(bpy.context.scene.objects):
    if o is not m: bpy.data.objects.remove(o, do_unlink=True)
m.data.transform(m.matrix_world); m.matrix_world = Matrix(); m.parent = None
zmin = min(v.co.z for v in m.data.vertices); S = SCALE
m.data.transform(Matrix.Scale(S, 4)); m.data.transform(Matrix.Translation((0, 0, -zmin * S)))
dz = -zmin * S
def P(x, y, z): return Vector((x * S, y * S, z * S + dz))
arm_d = bpy.data.armatures.new('Veado'); arm = bpy.data.objects.new('Veado', arm_d); bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
def B(n, h, t, par=None, conn=False):
    b = arm_d.edit_bones.new(n); b.head = h; b.tail = t
    if par: b.parent = arm_d.edit_bones[par]; b.use_connect = conn
    return b
B('Root', Vector((0, 0, 0)), Vector((0, 0, 0.3)))
B('Hips', P(0, 0.40, -0.15), P(0, 0.10, -0.12), 'Root')
B('Spine', P(0, 0.10, -0.12), P(0, -0.30, -0.10), 'Hips', True)
B('Neck', P(0, -0.32, -0.08), P(0, -0.45, 0.18), 'Spine')
B('Head', P(0, -0.45, 0.18), P(0, -0.66, 0.22), 'Neck', True)
B('Antlers', P(0, -0.42, 0.40), P(0, -0.35, 0.85), 'Head')
for side, x in (('L', 0.10), ('R', -0.10)):
    B(f'FrontUpper.{side}', P(x, -0.28, -0.30), P(x, -0.27, -0.62), 'Spine')
    B(f'FrontLower.{side}', P(x, -0.27, -0.62), P(x, -0.27, -0.93), f'FrontUpper.{side}', True)
    B(f'HindUpper.{side}', P(x, 0.45, -0.22), P(x, 0.60, -0.57), 'Hips')
    B(f'HindLower.{side}', P(x, 0.60, -0.57), P(x, 0.47, -0.93), f'HindUpper.{side}', True)
bpy.ops.object.mode_set(mode='OBJECT')
# pesos suaves próprios (o heat map do Blender falha na malha aberta do Meshy): inverso da distância aos ossos, 3 mais próximos
m.parent = arm; mod = m.modifiers.new('Armature', 'ARMATURE'); mod.object = arm
bones = [(b.name, arm.matrix_world @ b.head_local, arm.matrix_world @ b.tail_local) for b in arm.data.bones if b.name != 'Root']
def dseg(p, a, b):
    ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared)); return (a + ab * t - p).length
G = {n: m.vertex_groups.new(name=n) for n, _, _ in bones}
for v in m.data.vertices:
    co = v.co; ds = sorted((dseg(co, h, t), n) for n, h, t in bones)
    # pernas: só se a perna for claramente a mais próxima (evita colar a barriga às pernas)
    top = ds[:3]; w = [(1 / max(d, 0.02 * S) ** 4, n) for d, n in top]; tot = sum(x for x, _ in w)
    for x, n in w:
        if x / tot > 0.03: G[n].add([v.index], x / tot, 'REPLACE')
print('PESOS proprios', len(m.data.vertices))
bpy.context.scene.render.fps = 24
PB = arm.pose.bones
for pb in PB: pb.rotation_mode = 'XYZ'
def act(name, n, fn):
    a = bpy.data.actions.new(name); arm.animation_data_create(); arm.animation_data.action = a
    for f in range(n + 1):
        t = f / n
        for pb in PB: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
        fn(t)
        for pb in PB: pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_euler', frame=f)
    tr = arm.animation_data.nla_tracks.new(); tr.name = name; tr.strips.new(name, 0, a); arm.animation_data.action = None
R = math.radians
# Os ossos das pernas apontam para baixo: rodar em X local balança a perna para a frente/trás.
def gait(t, amp, bend, ph):
    for name, p in ph.items():
        u, lo = name.split('|'); a = 2 * math.pi * (t + p)
        PB[u].rotation_euler = (R(amp) * math.sin(a), 0, 0)
        PB[lo].rotation_euler = (R(bend) * max(0, math.cos(a)), 0, 0)
TROT = {'FrontUpper.L|FrontLower.L': 0, 'HindUpper.R|HindLower.R': 0, 'FrontUpper.R|FrontLower.R': .5, 'HindUpper.L|HindLower.L': .5}
def idle(t):
    PB['Neck'].rotation_euler = (R(4) * math.sin(2 * math.pi * t), 0, R(6) * math.sin(2 * math.pi * t))
    PB['Hips'].location = (0, 0.004 * math.sin(4 * math.pi * t), 0)
act('Idle', 48, idle)
def graze(t):  # pasta: cabeça ao chão e mastiga
    k = min(1, math.sin(math.pi * min(1, t / 0.25) / 2) if t < .75 else 1 - (t - .75) / .25)
    PB['Neck'].rotation_euler = (R(92) * k, 0, 0); PB['Spine'].rotation_euler = (R(6) * k, 0, 0); PB['Head'].rotation_euler = (R(30) * k + R(4) * math.sin(6 * math.pi * t) * k, 0, 0)
    for leg in ('FrontUpper.L', 'FrontUpper.R'): PB[leg].rotation_euler = (R(-6) * k, 0, 0)
act('Graze', 48, graze)
def walk(t):
    gait(t, 26, 38, TROT); PB['Hips'].location = (0, 0.03 * abs(math.sin(2 * math.pi * t)), 0)
    PB['Neck'].rotation_euler = (R(5) * math.sin(4 * math.pi * t), 0, 0)
act('Walk', 24, walk)
def attack(t):  # baixa a cabeça e investe com as hastes
    k = math.sin(math.pi * t)
    PB['Neck'].rotation_euler = (R(45) * k, 0, 0); PB['Head'].rotation_euler = (R(20) * k, 0, 0)
    PB['Hips'].location = (0, 0, -0.10 * k * (1 if t > .5 else -0.5))
act('Attack', 30, attack)
def hit(t):
    k = math.sin(math.pi * t) * (1 - t); PB['Spine'].rotation_euler = (0, R(8) * k, 0); PB['Neck'].rotation_euler = (R(15) * k, 0, 0)
act('Hit', 20, hit)
def death(t):  # dobra as pernas e tomba de lado
    e = min(1, t / .8) ** 2
    PB['Root'].rotation_euler = (0, 0, R(84) * e); PB['Root'].location = (0, 0.06 * S * e, 0)
    for leg in ('FrontUpper.L', 'FrontUpper.R', 'HindUpper.L', 'HindUpper.R'): PB[leg].rotation_euler = (R(25) * e, 0, 0)
    PB['Neck'].rotation_euler = (R(-20) * e, 0, R(20) * e)
act('Death', 40, death)
for img in bpy.data.images:
    if img.size[0] > 1024: img.scale(1024, 1024)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); m.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True)
print('OK', OUT, os.path.getsize(OUT))
