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

GB = 0  # portão vizinho do lado −x (4) / −y (8): o braço pára na face da casa do portão (que ocupa até 0,28 desta casa)
GCUT = .3
def arms(m):
    A = arms0(m)
    return [(ax, max(a0, GCUT) if (ax == 'x' and GB & 4 or ax == 'y' and GB & 8) else a0, a1) for ax, a0, a1 in A]
def arms0(m):  # braços: retas numa só peça; nos outros casos os braços sobrepõem-se no centro (sem juntas coplanares)
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

def madeira(m, M):  # paliçada: troncos grossos aguçados, de alturas irregulares, com travessas e escoras por dentro
    H = 1.05
    for axis, a0, a1 in arms(m):
        for k in range(-24, 36):  # espaçamento global de 0,085 (encaixa entre casas)
            t = (k + .5) * .085
            if not (a0 - .05 <= t <= a1 + .05) or (abs(t - .5) < .07 and not straight(m)): continue
            if (axis == 'x' and (m & 1 == 0 and t > .5 or m & 4 == 0 and t < .5)) or (axis == 'y' and (m & 2 == 0 and t > .5 or m & 8 == 0 and t < .5)): continue
            x, y = (t, .5) if axis == 'x' else (.5, t)
            hh = H - .1 + ((k * 7919) % 5) * .018
            cyl(x, y, 0, hh, .055, M['wood'], tip=.16, seg=8)
        for z in (.3, .7): seg(axis, a0, a1, -.075, -.045, z - .024, z + .024, M['wood_lt'], 'trav')  # travessas por dentro
    if not straight(m): cyl(.5, .5, 0, H + .04, .07, M['wood'], tip=.13, seg=9)

def pedra(m, M, fort=False):  # muralha alta e grossa (estilo Stronghold): adarve largo, ameias dos dois lados, pedra cinzenta
    T = .64 if fort else .56; H = 1.5 if fort else 1.3; hw = T / 2
    for axis, a0, a1 in arms(m):
        seg(axis, a0, a1, -hw - .04, hw + .04, 0, .14, M['stone_dk'], 'base')
        seg(axis, a0, a1, -hw, hw, .14, H, M['stone'])
        seg(axis, a0, a1, -hw + .07, hw - .07, H - .005, H + .005, M['stone_dk'], 'adarve')
        for k in range(-10, 16):  # ameias (global, 0,2) nos dois lados
            t = .1 + .2 * k
            if not (a0 - .06 <= t <= a1 + .06): continue
            for side in (-1, 1):
                w = (hw - .07, hw) if side > 0 else (-hw, -hw + .07)
                if axis == 'x': box(t - .055, t + .055, .5 + w[0], .5 + w[1], H, H + .15, M['stone'], 'merlon')
                else: box(.5 + w[0], .5 + w[1], t - .055, t + .055, H, H + .15, M['stone'], 'merlon')
            if axis == 'x': box(a0 if k == -10 else t - .1, t + .1, .5 + hw - .07, .5 + hw, H, H + .05, M['stone'], 'parapeito'); box(t - .1, t + .1, .5 - hw, .5 - hw + .07, H, H + .05, M['stone'], 'parapeito')
            else: box(.5 + hw - .07, .5 + hw, t - .1, t + .1, H, H + .05, M['stone'], 'parapeito'); box(.5 - hw, .5 - hw + .07, t - .1, t + .1, H, H + .05, M['stone'], 'parapeito')
        if fort:
            for k in range(-4, 7):
                t = .5 * k
                if not (a0 + .08 <= t <= a1 - .08): continue
                if axis == 'x': box(t - .012, t + .012, .5 + hw - .005, .5 + hw + .005, H * .5, H * .8, M['vao'], 'seteira')
                else: box(.5 + hw - .005, .5 + hw + .005, t - .012, t + .012, H * .5, H * .8, M['vao'], 'seteira')
    if not straight(m):  # torreão quadrado nas pontas, cantos e cruzamentos
        p = hw + .08; Hp = H + .4
        X0 = max(.5 - p, GCUT) if GB & 4 else .5 - p; Y0 = max(.5 - p, GCUT) if GB & 8 else .5 - p; X1 = Y1 = .5 + p  # o torreão não entra na casa do portão
        box(X0 - .03, X1 + .03, Y0 - .03, Y1 + .03, 0, .14, M['stone_dk'], 'base')
        box(X0, X1, Y0, Y1, .14, Hp, M['stone'], 'pilar')
        box(X0 - .02, X1 + .02, Y0 - .02, Y1 + .02, Hp, Hp + .04, M['stone_dk'], 'cornija')
        merlons(X0 - .02, X1 + .02, Y0 - .02, Y1 + .02, Hp + .04, M['stone'], 4, size=.09, h=.13)

def tons(M):  # pedra e madeira menos saturadas, como a arte pintada dos edifícios
    tm = g['tex_mat']
    M['stone'] = tm('t_stone_m', 'large_sandstone_blocks_01', 1.3, tint=(.93, .92, .89), sat=.14, val=1.04, normal=1.8) or M['stone']
    M['stone_dk'] = tm('t_stone_dk_m', 'medieval_blocks_02', 1.6, tint=(.86, .86, .84), sat=.1, val=.78, normal=1.8) or M['stone_dk']
    M['wood'] = tm('t_wood_m', 'bark_brown_02', 3.2, tint=(.92, .8, .66), sat=1.0, val=1.0) or M['wood']
    M['dirt'] = g['node_mat']('terra_m', (.26, .2, .13), noise=25, var=.2, bump=.3)

g['reset'](); sc = g['SCN'](); M = g['mats'](); tons(M); cam = g['scene']()
sc.view_layers[0].update()  # sem isto a câmara ainda não está rodada e a âncora saía no centro da casa (muro 16 px acima)
a = world_to_camera_view(sc, cam, Vector((0, 0, 0))); RX, RY = g['RES']; ax = a.x * RX
half = 16 * 2  # 16 px do jogo, a 2×
sc.render.use_border = True; sc.render.use_crop_to_border = False
sc.render.border_min_x = (ax - half - 10) / RX; sc.render.border_max_x = (ax + half + 10) / RX; sc.render.border_min_y = 0; sc.render.border_max_y = 1
info = {}
GATES = os.environ.get('GATES', '1') == '1'
for tp in TYPES:
  for m in MASKS:
    for gb in ([0] + ([4] if GATES and m & 4 else []) + ([8] if GATES and m & 8 else []) + ([12] if GATES and m & 12 == 12 else [])):
        GB = gb
        for o in list(G): bpy.data.objects.remove(o, do_unlink=True)
        G.clear()
        madeira(m, M) if tp == 'madeira' else pedra(m, M, fort=(tp == 'fort'))
        finish([o for o in G if o.name.split('.')[0] not in ('seg', 'base', 'cornija', 'centro', 'trav', 'contraforte', 'seteira', 'adarve', 'parapeito')])
        name = f'{tp}_{m}' + (f'_g{gb}' if gb else ''); sc.render.filepath = os.path.join(OUT, name + '.png')
        with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]): bpy.ops.render.render(write_still=True)
        info[name] = [ax, (1 - a.y) * RY]; print('REN', name, flush=True)
af = os.path.join(OUT, 'anchors.json'); old = json.load(open(af))['anchor'] if os.path.exists(af) else {}
old.update(info); json.dump({'anchor': old, 'clipHalfPx': half}, open(af, 'w'), indent=1)
print('FEITO')
