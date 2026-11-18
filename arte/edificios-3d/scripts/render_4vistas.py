# Vistas da câmara rodada (botão ⟳ do jogo): renderiza um modelo GLB de um edifício dos 4 lados com a câmara do jogo
# (ortográfica, azimute 45°, elevação 30°, a mesma luz e contorno dos outros edifícios 3D).
# A vista k (0..3) é o modelo rodado −90°·k à volta do centro da pegada — igual a rodar a câmara do jogo k quartos de volta
# (no jogo, ROT=1 leva o +x do mapa para +y; no Blender o y do jogo é −Y, por isso o modelo roda −90°).
# Saída: <NOME>_r0.png … <NOME>_r3.png e anchors.json com a chave "<NOME>|rK" (canto de cima da pegada), no formato que o
# trocar_no_atlas.py lê. A r0 serve para comparar com a pintura atual; o jogo usa r1, r2 e r3 (e r0 só se se quiser trocar a pintura).
# Uso (Blender por linha de comando ou módulo bpy do Python):
#   GLB=/caminho/casa.glb NOME=casa_n2 W=2 H=2 OUT=/tmp/casa4 [ROT0=0] [SAMPLES=48] [GPU=1] python3 render_4vistas.py
#   (ou: blender -b --python render_4vistas.py com as mesmas variáveis)
# ROT0: graus a rodar o modelo antes de tudo, para a frente dele (porta) ficar virada como na pintura do jogo (vista r0).
import bpy, os, json, math
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
LIB = os.environ.get('LIB', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'portoes-3d', 'scripts', 'montar_portao2.py'))
lib = open(LIB, encoding='utf-8').read().replace('\r\n', '\n'); lib = lib[:lib.index('reset(); M = mats()')]
os.environ.setdefault('OUT', os.environ.get('OUT', '/tmp/vistas'))
g = {'__name__': 'lib'}; exec(compile(lib, 'montar_portao2.py', 'exec'), g)
R = math.radians; PXU = 2 * 64 / math.sqrt(2)
GLB, NOME, OUT = os.environ['GLB'], os.environ['NOME'], os.environ['OUT']; W, H = float(os.environ.get('W', 2)), float(os.environ.get('H', 2))
ROT0 = float(os.environ.get('ROT0', 0)); MARGIN = float(os.environ.get('MARGEM', .05)); g['SAMPLES'] = int(os.environ.get('SAMPLES', '48'))
VIEWS = [int(v) for v in os.environ.get('VISTAS', '0,1,2,3').split(',')]
os.makedirs(OUT, exist_ok=True)

def scene_for(w, h):  # igual ao montar_edificios.py
    sc = g['SCN'](); RX = int(((w + h) * 64 * 1.25 + 40)); RY = int(RX * 1.05)
    g['RES'] = (RX, RY); cam = g['scene']()
    cam.data.ortho_scale = RX / PXU
    c = Vector((w / 2, -h / 2, 0)); d = Vector((1, -1, 0)).normalized() * math.cos(R(30)) + Vector((0, 0, math.sin(R(30))))
    cam.location = c + d * 30; cam.data.shift_y = .16
    gobj = next(o for o in sc.objects if o.name == 'g'); gobj.scale = (w, h, 1); gobj.location = (w / 2 - .5, -(h / 2 - .5), 0)
    return sc, cam

def import_fit(w, h):
    """Importa o GLB e encaixa-o na pegada w×h (escala uniforme, centrado, assente em z=0). Devolve os objetos de topo."""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=GLB)
    objs = [o for o in bpy.data.objects if o not in before]; ms = [o for o in objs if o.type == 'MESH']
    sc = g['SCN']()
    for o in objs:  # o import vai para a cena ativa: passar para a cena "portoes"
        for col in list(o.users_collection): col.objects.unlink(o)
        sc.collection.objects.link(o)
    top = [o for o in objs if o.parent is None]
    rot = Matrix.Rotation(R(ROT0), 4, 'Z')
    for o in top: o.matrix_world = rot @ o.matrix_world
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in ms for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    s = min((w - 2 * MARGIN) / (hi.x - lo.x), (h - 2 * MARGIN) / (hi.y - lo.y)); c = (lo + hi) / 2
    T = Matrix.Translation((w / 2, -h / 2, 0)) @ Matrix.Scale(s, 4) @ Matrix.Translation((-c.x, -c.y, -lo.z))
    for o in top: o.matrix_world = T @ o.matrix_world
    for o in ms:
        for sl in o.material_slots:
            if sl.material and sl.material.use_nodes:  # mate como o resto do jogo
                b = sl.material.node_tree.nodes.get('Principled BSDF')
                if b: b.inputs['Roughness'].default_value = max(b.inputs['Roughness'].default_value, .6)
    print('GLB', NOME, 'altura', round((hi.z - lo.z) * s, 3), 'escala', round(s, 4), flush=True)
    return top, [o.matrix_world.copy() for o in top]

g['reset'](); g['G'].clear(); sc, cam = scene_for(W, H)
# sem sombra embutida: o jogo projeta a sua (como nos outros edifícios)
for o in sc.objects:
    if o.name == 'g': o.hide_render = True
top, base = import_fit(W, H)
af = os.path.join(OUT, 'anchors.json'); info = json.load(open(af)) if os.path.exists(af) else {}
for k in VIEWS:
    piv = Matrix.Translation((W / 2, -H / 2, 0)) @ Matrix.Rotation(R(-90 * k), 4, 'Z') @ Matrix.Translation((-W / 2, H / 2, 0))
    for o, m in zip(top, base): o.matrix_world = piv @ m
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(OUT, f'{NOME}_r{k}.png')
    with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]): bpy.ops.render.render(write_still=True)
    a = world_to_camera_view(sc, cam, Vector((0, 0, 0)))  # canto de cima da pegada no ecrã (o mesmo em todas as vistas: a pegada é a mesma)
    info[f'{NOME}|r{k}'] = [a.x * sc.render.resolution_x, (1 - a.y) * sc.render.resolution_y, W, H]
    print('REN', NOME, k, flush=True)
json.dump(info, open(af, 'w'), indent=1); print('FEITO')
