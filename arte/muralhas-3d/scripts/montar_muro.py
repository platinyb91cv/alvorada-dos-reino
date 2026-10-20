# Muralhas 3D (paliçada, pedra, fortificada) para o Alvorada dos Reinos: mesma câmara, texturas e acabamento dos portões.
# 16 máscaras de vizinhos (1=+x, 2=+y, 4=−x, 8=−y, como bldVariant). Cada braço é modelado prolongado para lá da casa
# e o render é recortado (render border) à coluna de ecrã da casa: |x_ecrã| ≤ 16 px do jogo. Assim casas vizinhas
# encaixam sem costura (a geometria é a mesma dos dois lados do corte).
import bpy, os, json, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
work = os.environ['WORK']
lib = open(os.path.join(work, 'montar_portao2.py'), encoding='utf-8').read(); lib = lib[:lib.index('reset(); M = mats()')]
g = {'__name__': 'lib'}; exec(compile(lib, 'montar_portao2.py', 'exec'), g)
box, cyl, merlons, flag, finish, G = g['box'], g['cyl'], g['merlons'], g['flag'], g['finish'], g['G']
OUT = os.environ['OUT']; os.makedirs(OUT, exist_ok=True)
TYPES = os.environ.get('TYPES', 'madeira,pedra,fort').split(',')
MASKS = [int(v) for v in os.environ.get('MASKS', ','.join(map(str, range(16)))).split(',')]
EXT = 1.4  # quanto o braço se prolonga para lá do centro (corta-se no ecrã)

def arms(m):  # braços: retas numa só peça; nos outros casos os braços sobrepõem-se no centro (sem juntas coplanares)
    if m == 5: return [('x', .5 - EXT, .5 + EXT)]
    if m == 10: return [('y', .5 - EXT, .5 + EXT)]
    A = []; ov = .2
    if m & 1: A.append(('x', .5 - ov, .5 + EXT))
    if m & 4: A.append(('x', .5 - EXT, .5 + ov))
    if m & 2: A.append(('y', .5 - ov, .5 + EXT))
    if m & 8: A.append(('y', .5 - EXT, .5 + ov))
    return A
def seg(axis, a0, a1, w0, w1, z0, z1, mat, name='seg'):  # caixa ao longo de um eixo; w0..w1 = largura em torno de 0,5
    return box(a0, a1, .5 + w0, .5 + w1, z0, z1, mat, name) if axis == 'x' else box(.5 + w0, .5 + w1, a0, a1, z0, z1, mat, name)
def straight(m): return m in (5, 10)

def madeira(m, M):
    H = .62
    for axis, a0, a1 in arms(m):
        for k in range(-20, 30):  # troncos com espaçamento global de 0,1 (alternam a altura pela paridade global)
            t = (k + .5) / 10
            if not (a0 - .05 <= t <= a1 + .05) or (abs(t - .5) < .06 and not straight(m)): continue
            if (axis == 'x' and (m & 1 == 0 and t > .5 or m & 4 == 0 and t < .5)) or (axis == 'y' and (m & 2 == 0 and t > .5 or m & 8 == 0 and t < .5)): continue
            x, y = (t, .5) if axis == 'x' else (.5, t)
            cyl(x, y, 0, H + (.05 if k % 2 else 0) - .1, .047, M['wood'], tip=.11, seg=7)
        for z in (.17, .44):  # travessas atadas pela frente
            seg(axis, a0, a1, .045, .075, z - .022, z + .022, M['wood_lt'], 'trav')
    if not straight(m):  # poste central mais grosso nas pontas, cantos e cruzamentos
        cyl(.5, .5, 0, H + .02, .07, M['wood'], tip=.13, seg=9)
        if m == 0:
            for dx, dy in ((-.1, .02), (.08, -.08)): cyl(.5 + dx, .5 + dy, 0, H - .08, .05, M['wood'], tip=.1, seg=7)
        if bin(m).count('1') <= 1: flag(.5, .5, H + .1, .22, M['banner'], M)

def pedra(m, M, fort=False):
    T = .34 if fort else .26; H = .9 if fort else .72; hw = T / 2
    for axis, a0, a1 in arms(m):
        seg(axis, a0, a1, -hw - .035, hw + .035, 0, .1, M['stone_dk'], 'base')
        seg(axis, a0, a1, -hw, hw, .1, H, M['stone'])
        if fort:  # ameias dos dois lados, espaçamento global de 0,25
            seg(axis, a0, a1, -hw - .02, hw + .02, H, H + .04, M['stone'], 'cornija')
            for k in range(-8, 12):
                t = .125 + .25 * k
                if not (a0 <= t <= a1): continue
                for side in (-1, 1):
                    w = (hw - .035, hw + .02) if side > 0 else (-hw - .02, -hw + .035)
                    if axis == 'x': box(t - .055, t + .055, .5 + w[0], .5 + w[1], H + .04, H + .14, M['stone'], 'merlon')
                    else: box(.5 + w[0], .5 + w[1], t - .055, t + .055, H + .04, H + .14, M['stone'], 'merlon')
        else:
            seg(axis, a0, a1, -hw - .02, hw + .02, H, H + .045, M['stone'], 'cornija')
    # bloco do centro (enche a junção) e pilar nas pontas/cantos
    if not straight(m): box(.5 - hw, .5 + hw, .5 - hw, .5 + hw, .1, H, M['stone'], 'centro')
    if not straight(m): box(.5 - hw - .035, .5 + hw + .035, .5 - hw - .035, .5 + hw + .035, 0, .1, M['stone_dk'], 'base')
    if not straight(m):
        p = hw + .04; Hp = H + (.28 if fort else .12)
        box(.5 - p, .5 + p, .5 - p, .5 + p, 0, Hp, M['stone'], 'pilar')
        box(.5 - p - .02, .5 + p + .02, .5 - p - .02, .5 + p + .02, Hp, Hp + .05, M['stone'], 'cornija')
        if fort:
            merlons(.5 - p - .02, .5 + p + .02, .5 - p - .02, .5 + p + .02, Hp + .05, M['stone'], 2, size=.08, h=.1)
            if bin(m).count('1') <= 1: flag(.5, .5, Hp + .15, .26, M['banner'], M)
        elif bin(m).count('1') <= 1: flag(.5, .5, Hp + .05, .22, M['banner'], M)
    elif not fort:
        pass

g['reset'](); sc = g['SCN'](); M = g['mats'](); cam = g['scene']()
a = world_to_camera_view(sc, cam, Vector((0, 0, 0))); RX, RY = g['RES']; ax = a.x * RX
half = 16 * 2  # 16 px do jogo, a 2×
sc.render.use_border = True; sc.render.use_crop_to_border = False
sc.render.border_min_x = (ax - half - 10) / RX; sc.render.border_max_x = (ax + half + 10) / RX; sc.render.border_min_y = 0; sc.render.border_max_y = 1
info = {}
for tp in TYPES:
    for m in MASKS:
        for o in list(G): bpy.data.objects.remove(o, do_unlink=True)
        G.clear()
        madeira(m, M) if tp == 'madeira' else pedra(m, M, fort=(tp == 'fort'))
        finish([o for o in G if o.name.split('.')[0] not in ('seg', 'base', 'cornija', 'centro', 'trav')])
        name = f'{tp}_{m}'; sc.render.filepath = os.path.join(OUT, name + '.png')
        with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]): bpy.ops.render.render(write_still=True)
        info[name] = [ax, (1 - a.y) * RY]; print('REN', name, flush=True)
af = os.path.join(OUT, 'anchors.json'); old = json.load(open(af))['anchor'] if os.path.exists(af) else {}
old.update(info); json.dump({'anchor': old, 'clipHalfPx': half}, open(af, 'w'), indent=1)
print('FEITO')
