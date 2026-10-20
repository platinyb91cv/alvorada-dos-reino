# Monta um GLB riggado e animado a partir de um modelo Meshy estático de máquina de cerco (0 créditos).
# Partes rígidas por região (o modelo low-poly do Meshy vem em "sopa" de faces): corpo, eixos das rodas,
# tronco do aríete ou braço + contrapeso do trebuchet. Clips: Idle, Walk, Attack, Hit, Death (24 fps).
# Uso: MN=<entrada sem .glb> KIND=ram|treb SCALE=<fator> OUT=<saida.glb> blender -b --python montar_cerco.py
import bpy, bmesh, os, math, json
from mathutils import Vector, Matrix, Euler
D = os.path.dirname(os.path.abspath(os.environ.get('OUT')))
SRC, KIND, SCALE, OUT = os.environ['SRC'], os.environ['KIND'], float(os.environ['SCALE']), os.environ['OUT']
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions): bpy.data.actions.remove(a)
bpy.ops.import_scene.gltf(filepath=SRC)
mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
for o in list(bpy.context.scene.objects):
    if o is not mesh and o.type != 'MESH': bpy.data.objects.remove(o, do_unlink=True)
mesh.parent = None
# aplica a transformação de importação e a escala real; pousa no chão (z mínimo = 0)
mesh.data.transform(mesh.matrix_world); mesh.matrix_world = Matrix()
mesh.data.transform(Matrix.Scale(SCALE, 4))
zmin = min(v.co.z for v in mesh.data.vertices); mesh.data.transform(Matrix.Translation((0, 0, -zmin)))
S = SCALE; dz = -zmin  # converte coordenadas do modelo original (unidades Meshy) para metros pousados
def P(x, y, z): return Vector((x * S, y * S, z * S + dz))

if KIND == 'ram':
    wheels = {'eixoF': [(-0.50, -0.40)], 'eixoT': [(0.60, -0.40)]}; wr, wy = 0.17, 0.27
    parts = {'tronco': lambda c: abs(c.y) < 0.13 * S and -0.21 * S + dz < c.z < 0.02 * S + dz}
else:
    wheels = {'eixoF': [(-0.44, -0.40)], 'eixoT': [(0.66, -0.40)]}; wr, wy = 0.17, 0.29
    PIV = P(0.30, 0, 0.36); END = P(0.75, 0, 0.36)
    parts = {
        'contrapeso': lambda c: c.x > 0.52 * S and -0.22 * S + dz < c.z < 0.30 * S + dz and abs(c.y) < 0.27 * S,
        'braco': lambda c: (0.27 * S + dz < c.z < 0.46 * S + dz and c.x < 0.82 * S and abs(c.y) < 0.12 * S and not (0.12 * S < c.x < 0.48 * S))
                           or (c.x < -0.62 * S and 0.12 * S + dz < c.z < 0.46 * S + dz),
    }
centers = {k: P(x, 0, z) for k, v in wheels.items() for (x, z) in v}
groups = {k: [] for k in ['corpo', *wheels, *parts]}
bm = bmesh.new(); bm.from_mesh(mesh.data); bm.faces.ensure_lookup_table()
face_group = {}
for f in bm.faces:
    c = f.calc_center_median(); g = 'corpo'
    for k, w in centers.items():
        if all(abs(v.co.y) > wy * S and math.hypot(v.co.x - w.x, v.co.z - w.z) < wr * S for v in f.verts): g = k; break
    if g == 'corpo':
        for k, test in parts.items():
            if test(c): g = k; break
    face_group[f.index] = g
vg = {k: mesh.vertex_groups.new(name=k) for k in groups}
vert_group = {}
for f in bm.faces:
    for v in f.verts: vert_group.setdefault(v.index, face_group[f.index])
bm.free()
counts = {}
for vi, g in vert_group.items(): vg[g].add([vi], 1.0, 'REPLACE'); counts[g] = counts.get(g, 0) + 1
print('GRUPOS', json.dumps(counts))

# esqueleto: ossos ao longo de +Y (rodar no Y local = rodar em torno do eixo das rodas/pivô)
arm_data = bpy.data.armatures.new('Cerco'); arm = bpy.data.objects.new('Cerco', arm_data); bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
def bone(name, head, parent=None):
    b = arm_data.edit_bones.new(name); b.head = head; b.tail = head + Vector((0, 0.3, 0)); b.roll = 0
    if parent: b.parent = arm_data.edit_bones[parent]
    return b
bone('corpo', Vector((0, 0, 0)))
for k, c in centers.items(): bone(k, c, 'corpo')
if KIND == 'ram': bone('tronco', P(0, 0, -0.1), 'corpo')
else: bone('braco', PIV, 'corpo'); bone('contrapeso', END, 'corpo')
bpy.ops.object.mode_set(mode='OBJECT')
mesh.parent = arm; mod = mesh.modifiers.new('Armature', 'ARMATURE'); mod.object = arm
# o pipeline procura a anca/raiz: o osso "corpo" é a raiz
FPS = 24; bpy.context.scene.render.fps = FPS
wheel_r = wr * S * 0.95

def act(name, n, fn):
    a = bpy.data.actions.new(name); arm.animation_data_create(); arm.animation_data.action = a
    for pb in arm.pose.bones: pb.rotation_mode = 'XYZ'
    for f in range(n + 1):
        t = f / n
        for pb in arm.pose.bones: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
        fn(t)
        for pb in arm.pose.bones:
            pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_euler', frame=f)
    tr = arm.animation_data.nla_tracks.new(); tr.name = name; st = tr.strips.new(name, 0, a); arm.animation_data.action = None
    return a
PB = arm.pose.bones
def wheels_spin(ang):
    for k in centers: PB[k].rotation_euler = (0, ang, 0)

# Idle: parado, só um leve assentar das tábuas
act('Idle', 40, lambda t: None)
# Walk: uma volta completa das rodas (avanço = perímetro da roda); balanço muito leve do corpo
def walk(t):
    wheels_spin(-2 * math.pi * t)
    PB['corpo'].location = (0, 0, 0.012 * math.sin(4 * math.pi * t))
act('Walk', 32, walk)
if KIND == 'ram':
    # Attack: recua o tronco e investe (frente = -X)
    def attack(t):
        k = math.sin(math.pi * t / 0.7) if t < 0.7 else 0
        d = (0.35 * S * k) if t < 0.45 else (-0.22 * S * math.sin(math.pi * (t - 0.45) / 0.55))
        PB['tronco'].location = (d, 0, 0)  # eixo X do osso = X do mundo
    act('Attack', 36, attack)
else:
    # Attack: o contrapeso cai, o braço longo sobe e passa por cima (larga a pedra), depois volta
    def ang(t): return math.radians(140) * (math.sin(math.pi * min(1, t / 0.45) / 2) if t < 0.45 else max(0, 1 - (t - 0.45) / 0.55) ** 1.5)
    def attack(t):
        a = ang(t); PB['braco'].rotation_euler = (0, a, 0)
        r = END - PIV; rr = Matrix.Rotation(a, 3, 'Y') @ r; dv = (PIV + rr) - END
        PB['contrapeso'].location = (dv.x, dv.y, dv.z)
    act('Attack', 48, attack)
# Hit: estremece
act('Hit', 30, lambda t: setattr(PB['corpo'], 'rotation_euler', (math.radians(3) * math.sin(6 * math.pi * t) * (1 - t), 0, 0)))
# Death: tomba para o lado e abate
def death(t):
    e = min(1, t / 0.8) ** 2
    PB['corpo'].rotation_euler = (math.radians(-28) * e, 0, 0); PB['corpo'].location = (0, -0.25 * e, -0.12 * e)
act('Death', 52, death)

for img in bpy.data.images:
    if img.size[0] > 1024: img.scale(1024, 1024)
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); mesh.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True, export_apply=False)
print('OK', OUT, os.path.getsize(OUT))
