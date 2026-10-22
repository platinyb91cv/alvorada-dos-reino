# Edifícios 3D do Alvorada dos Reinos: mesmas primitivas, materiais (texturas Poly Haven se TEX_DIR existir), câmara,
# luz e contorno dos portões/muralhas. Um render por tipo e idade (torre: por nível). Âncora = canto de cima da casa (tx,ty).
import bpy, bmesh, os, json, math
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
LIB = os.environ.get('LIB', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'portoes-3d', 'scripts', 'montar_portao2.py'))
lib = open(LIB, encoding='utf-8').read().replace('\r\n', '\n'); lib = lib[:lib.index('reset(); M = mats()')]
g = {'__name__': 'lib'}; exec(compile(lib, 'montar_portao2.py', 'exec'), g)
box, cyl, hlog, pyramid, gable, cone, banner, flag, merlons, finish, G = (g[k] for k in ('box', 'cyl', 'hlog', 'pyramid', 'gable', 'cone', 'banner', 'flag', 'merlons', 'finish', 'G'))
mesh_obj = g['mesh_obj']; R = math.radians
OUT = os.environ['ED_OUT']; os.makedirs(OUT, exist_ok=True); SAMPLES = int(os.environ.get('SAMPLES', '48'))
PXU = 2 * 64 / math.sqrt(2)
def gableY(x0, x1, y0, y1, z0, h, mat, over=.05):  # duas águas com cumeeira ao longo de y
    bm = bmesh.new(); xm = (x0 + x1) / 2
    p = [bm.verts.new(v) for v in ((x0 - over, -(y0 - over), z0), (x0 - over, -(y1 + over), z0), (xm, -(y1 + over), z0 + h), (xm, -(y0 - over), z0 + h),
                                    (x1 + over, -(y0 - over), z0), (x1 + over, -(y1 + over), z0))]
    bm.faces.new((p[1], p[0], p[3], p[2])); bm.faces.new((p[3], p[4], p[5], p[2])); bm.faces.new((p[0], p[4], p[3])); bm.faces.new((p[1], p[2], p[5]))
    return mesh_obj('gable', bm, mat)
def gable_end(x0, x1, y, z0, h, mat, axis='x'):  # empena triangular (fecha o telhado) — cumeeira ao longo de x: empenas nas pontas x
    bm = bmesh.new()
    if axis == 'x':  # empena no plano x=const, triângulo em y
        pass
    return None
def walls(x0, x1, y0, y1, h, age, M, frame=True):
    """Paredes por idade: 0 tábuas/pau-a-pique, 1 base de pedra + madeira, 2 pedra; com cunhais de madeira nas 0/1."""
    FRONT['y'] = y1; FRONT['x'] = x1
    box(x0 - .03, x1 + .03, y0 - .03, y1 + .03, 0, .08, M['stone_dk'], 'base')
    if age == 0: box(x0, x1, y0, y1, .08, h, M['plank'], 'parede')
    elif age == 1: box(x0, x1, y0, y1, .08, h * .42, M['stone'], 'parede'); box(x0 + .01, x1 - .01, y0 + .01, y1 - .01, h * .42, h, M['plank'], 'parede')
    else: box(x0, x1, y0, y1, .08, h, M['stone'], 'parede')
    if frame and age < 2:
        for x in (x0, x1):
            for y in (y0, y1): box(x - .03, x + .03, y - .03, y + .03, .08, h, M['wood'], 'cunhal')
        box(x0 - .02, x1 + .02, y1 - .01, y1 + .02, h - .05, h, M['wood'], 'viga'); box(x1 - .01, x1 + .02, y0 - .02, y1 + .02, h - .05, h, M['wood'], 'viga')
def roof(x0, x1, y0, y1, z, h, age, M, ridge='x', over=.08):
    mat = [M['thatch'], M['shingle'], M['slate']][age]
    (gable if ridge == 'x' else gableY)(x0, x1, y0, y1, z, h, mat, over=over)
    # empenas (triângulos de parede nas pontas)
    bm = bmesh.new()
    if ridge == 'x':
        ym = (y0 + y1) / 2
        for x in (x0, x1): bm.faces.new((bm.verts.new((x, -y0, z)), bm.verts.new((x, -y1, z)), bm.verts.new((x, -ym, z + h))))
    else:
        xm = (x0 + x1) / 2
        for y in (y0, y1): bm.faces.new((bm.verts.new((x0, -y, z)), bm.verts.new((x1, -y, z)), bm.verts.new((xm, -y, z + h))))
    o = mesh_obj('empena', bm, M['plank'] if age < 2 else M['stone']); o.modifiers.new('s', 'SOLIDIFY').thickness = .02
def door(x0, x1, y, h, M, face='y'):  # porta na face +y (ou +x)
    if face == 'y': box(x0 - .03, x1 + .03, y - .005, y + .02, .08, h + .04, M['wood'], 'aro'); box(x0, x1, y, y + .025, .08, h, M['plank'], 'porta')
    else: box(y - .005, y + .02, x0 - .03, x1 + .03, .08, h + .04, M['wood'], 'aro'); box(y, y + .025, x0, x1, .08, h, M['plank'], 'porta')
FRONT = {'x': 0, 'y': 0}
def window(c, z, M, face='y', w=.12, h=.12, at=None):
    if at is None: at = FRONT[face]
    if face == 'y': box(c - w / 2 - .02, c + w / 2 + .02, at - .005, at + .015, z - .02, z + h + .02, M['wood'], 'moldura'); box(c - w / 2, c + w / 2, at, at + .02, z, z + h, M['vao'], 'janela')
    else: box(at - .005, at + .015, c - w / 2 - .02, c + w / 2 + .02, z - .02, z + h + .02, M['wood'], 'moldura'); box(at, at + .02, c - w / 2, c + w / 2, z, z + h, M['vao'], 'janela')
def barrel(x, y, M, s=1.0): cyl(x, y, 0, .16 * s, .07 * s, M['wood_lt'], seg=10); cyl(x, y, .05 * s, .07 * s, .073 * s, M['iron'], seg=10)
def crate(x, y, M, s=.14, z=0): box(x - s / 2, x + s / 2, y - s / 2, y + s / 2, z, z + s, M['plank'], 'caixa')
def sack(x, y, M): cyl(x, y, 0, .12, .06, M['cloth'], seg=8)
def fence(pts, M, h=.18):
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(2, int(math.hypot(bx - ax, by - ay) / .22))
        for k in range(n + 1): t = k / n; cyl(ax + (bx - ax) * t, ay + (by - ay) * t, 0, h, .018, M['wood'], seg=6)
        for zz in (h * .45, h * .8): box(min(ax, bx) - .01, max(ax, bx) + .01, min(ay, by) - .01, max(ay, by) + .01, zz - .012, zz + .012, M['wood_lt'], 'travessa')
def chimney(x, y, z0, z1, M): box(x - .06, x + .06, y - .06, y + .06, z0, z1, M['stone_dk'], 'chamine')
# ---------------- edifícios ----------------
def casa(age, M):
    h = (.5, .55, .62)[age]; x0, x1, y0, y1 = .35, 1.65, .45, 1.55
    walls(x0, x1, y0, y1, h, age, M); roof(x0, x1, y0, y1, h, (.42, .4, .45)[age], age, M, 'x')
    door(.75, .97, y1, .3, M); window(1.35, .25, M); window(.95, .27, M, 'x', at=x1)
    if age >= 1: chimney(1.35, .8, h, h + .55, M)
    if age == 0: barrel(1.8, 1.75, M, .8); sack(.25, 1.75, M)
    else: box(.3, 1.7, 1.62, 1.66, .08, .08 + .14, M['wood'], 'banco')
    if age == 2: banner(1.65 + .02, 1.0, h - .05, .16, .26, M['banner'], face='x')
def armazem(age, M):
    h = (.55, .6, .68)[age]; x0, x1, y0, y1 = .25, 1.75, .25, 1.05
    walls(x0, x1, y0, y1, h, age, M); roof(x0, x1, y0, y1, h, .35, age, M, 'x')
    for x in (.3, 1.0, 1.7): cyl(x, 1.6, .0, h * .78, .03, M['wood'], seg=6)  # alpendre
    box(.2, 1.8, 1.05, 1.68, h * .78, h * .78 + .04, [M['thatch'], M['shingle'], M['slate']][age], 'alpendre')
    for x, y in ((.45, 1.3), (.62, 1.38), (.5, 1.48)): barrel(x, y, M)
    for x, y, z in ((1.2, 1.3, 0), (1.36, 1.3, 0), (1.28, 1.3, .14), (1.5, 1.45, 0)): crate(x, y, M, z=z)
    for k in range(3): hlog(.9, 1.15, 1.55 + k * .05, .04 + (k % 2) * .05, .03, M['wood'], 'x')
    if age == 2: banner(1.0, 1.06, h - .05, .2, .28, M['banner'])
def quartel(age, M):
    h = (.6, .68, .8)[age]; x0, x1, y0, y1 = .25, 2.75, .25, 1.35
    walls(x0, x1, y0, y1, h, age, M); roof(x0, x1, y0, y1, h, .48, age, M, 'x')
    door(1.3, 1.7, y1, .38, M); window(.65, .32, M); window(2.3, .32, M); window(.8, .32, M, 'x', at=x1)
    fence([(.25, 1.6), (.25, 2.75), (2.75, 2.75), (2.75, 1.6)], M)
    for k in range(3):  # bonecos de treino
        x = .8 + k * .6; cyl(x, 2.2, 0, .32, .025, M['wood'], seg=6); cyl(x, 2.2, .2, .34, .07, M['cloth'], seg=8)
    box(2.1, 2.5, 1.7, 1.78, 0, .3, M['wood'], 'armeiro')
    for k in range(4): cyl(2.15 + k * .1, 1.75, .02, .42, .01, M['iron'], seg=5)
    if age == 2:
        box(2.25, 2.85, .2, .8, 0, 1.3, M['stone'], 'torre'); merlons(2.25, 2.85, .2, .8, 1.3, M['stone'], 3, size=.09, h=.1)
        flag(2.55, .5, 1.4, .35, M['banner'], M)
    banner(1.5, y1 + .03, h - .04, .22, .3, M['banner'])
def arquearia(age, M):
    h = (.55, .62, .75)[age]; x0, x1, y0, y1 = .25, 1.45, .25, 2.75
    walls(x0, x1, y0, y1, h, age, M); roof(x0, x1, y0, y1, h, .45, age, M, 'y')
    door(1.3, 1.7, x1, .34, M, face='x'); window(.7, .3, M, 'x', at=x1); window(2.3, .3, M, 'x', at=x1)
    for k, y in enumerate((.8, 1.6, 2.4)):  # alvos
        x = 2.5; cyl(x - .08, y, 0, .3, .02, M['wood'], seg=5)
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=.15, radius2=.15, depth=.04)
        bmesh.ops.transform(bm, matrix=Matrix.Translation((x, -y, .32)) @ Matrix.Rotation(R(90), 4, 'Y') @ Matrix.Rotation(R(15), 4, 'X'), verts=bm.verts)
        mesh_obj('alvo', bm, M['cloth'])
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=.07, radius2=.07, depth=.045)
        bmesh.ops.transform(bm, matrix=Matrix.Translation((x - .005, -y, .32)) @ Matrix.Rotation(R(90), 4, 'Y'), verts=bm.verts); mesh_obj('centro_alvo', bm, M['banner'])
    for x, y in ((1.8, .6), (1.95, .55)): cyl(x, y, 0, .22, .09, M['thatch'], seg=10)
    if age == 2: banner(x1 + .03, 1.5, h - .05, .2, .28, M['banner'], face='x')
def estabulo(age, M):
    h = (.6, .66, .74)[age]; x0, x1, y0, y1 = .25, 2.75, .25, 1.3
    walls(x0, x1, y0, y1, h, age, M); roof(x0, x1, y0, y1, h, .5, age, M, 'x')
    for k in range(4): door(.45 + k * .58, .75 + k * .58, y1, .36, M)
    if age >= 1: box(1.35, 1.65, y1, y1 + .02, h + .08, h + .26, M['vao'], 'palheiro')
    fence([(.25, 1.55), (.25, 2.75), (2.75, 2.75), (2.75, 1.55)], M, .2)
    for x, y in ((1.0, 2.2), (1.25, 2.3)): box(x - .14, x + .14, y - .08, y + .08, 0, .14, M['thatch'], 'feno')
    box(2.0, 2.5, 2.0, 2.12, 0, .1, M['wood'], 'bebedouro'); box(2.03, 2.47, 2.02, 2.1, .06, .1, M['vao'], 'agua')
    if age == 2: banner(1.5, y1 + .03, h + .02, .2, .26, M['banner'])
def doca(age, M):
    box(.1, 1.9, .5, 1.9, .06, .12, M['plank'], 'cais')
    for x in (.15, .7, 1.3, 1.85):
        for y in (.55, 1.2, 1.85): cyl(x, y, -.05, .12, .04, M['wood'], seg=6)
    if age >= 1:
        walls(.15, .9, .1, .6, .45, age, M); roof(.15, .9, .1, .6, .45, .3, age, M, 'x')
    else: box(.2, .6, .15, .45, .12, .3, M['plank'], 'abrigo')
    cyl(1.6, .8, .12, .9, .035, M['wood'], seg=6); hlog(1.0, 1.6, .8, .88, .02, M['wood'], 'x'); cyl(1.05, .8, .5, .88, .006, M['corda'] if 'corda' in M else M['cloth'], seg=4)
    for x, y in ((.4, 1.6), (.55, 1.65)): barrel(x, y, M, .8)
    crate(1.2, 1.6, M, z=.12)
    if age == 2: flag(1.85, 1.85, .12, .4, M['banner'], M)
def torre(lvl, M):
    if lvl == 1:
        for x in (.6, 1.4):
            for y in (.6, 1.4): cyl(x, y, 0, 1.3, .045, M['wood'], seg=7)
        box(.5, 1.5, .5, 1.5, 1.05, 1.12, M['plank'], 'plataforma')
        for k in range(8): t = k / 8; cyl(.5 + t, .5, 1.12, 1.3, .015, M['wood'], seg=5); cyl(.5, .5 + t, 1.12, 1.3, .015, M['wood'], seg=5)
        pyramid(.5, 1.5, .5, 1.5, 1.42, .35, M['thatch'], over=.08)
        for x in (.6, 1.4):
            for y in (.6, 1.4): cyl(x, y, 1.12, 1.44, .025, M['wood'], seg=6)
        box(.6, 1.4, 1.38, 1.42, .48, .52, M['wood'], 'trav'); box(1.38, 1.42, .6, 1.4, .78, .82, M['wood'], 'trav')
    else:
        H = 1.45 if lvl == 2 else 1.75
        box(.45, 1.55, .45, 1.55, 0, .12, M['stone_dk'], 'base'); box(.5, 1.5, .5, 1.5, .12, H, M['stone'], 'torre')
        for zz in (.6, 1.05): window(1.0, zz, M, 'y', w=.06, h=.18, at=1.5); window(1.0, zz, M, 'x', w=.06, h=.18, at=1.5)
        door(.85, 1.15, 1.5, .32, M)
        if lvl == 2:
            box(.44, 1.56, .44, 1.56, H, H + .1, M['plank'], 'balcao'); pyramid(.44, 1.56, .44, 1.56, H + .35, .4, M['shingle'], over=.06)
            for x in (.48, 1.52):
                for y in (.48, 1.52): cyl(x, y, H + .1, H + .36, .025, M['wood'], seg=6)
        else:
            box(.44, 1.56, .44, 1.56, H, H + .06, M['stone_dk'], 'cornija'); merlons(.44, 1.56, .44, 1.56, H + .06, M['stone'], 4, size=.1, h=.12)
            cone(1.0, 1.0, H + .06, .55, .38, M['slate'], seg=16); flag(1.0, 1.0, H + .58, .3, M['banner'], M)
def ferreiro(age, M):
    h = (.55, .6, .7)[age]; x0, x1, y0, y1 = .3, 1.7, .3, 1.15
    walls(x0, x1, y0, y1, h, age, M); roof(x0, x1, y0, y1, h, .35, age, M, 'x')
    for x in (.35, 1.65): cyl(x, 1.65, 0, h * .75, .03, M['wood'], seg=6)
    box(.25, 1.75, 1.15, 1.72, h * .75, h * .75 + .04, [M['thatch'], M['shingle'], M['slate']][age], 'alpendre')
    box(.4, .75, 1.2, 1.5, 0, .3, M['stone_dk'], 'forja'); box(.47, .68, 1.38, 1.52, .1, .25, M['fire'], 'brasa')
    chimney(.57, 1.3, .3, h + .65, M)
    box(1.1, 1.28, 1.35, 1.45, 0, .14, M['wood'], 'cepo'); box(1.06, 1.32, 1.36, 1.44, .14, .2, M['iron'], 'bigorna')
    cyl(1.55, 1.45, .0, .22, .1, M['stone'], seg=12)  # mó
    for k in range(3): cyl(.9 + k * .08, 1.25, 0, .28, .008, M['iron'], seg=4)
    if age == 2: banner(1.7 + .02, .75, h - .05, .16, .24, M['banner'], face='x')
def templo(age, M):
    h = (0, .85, 1.0)[age]; x0, x1, y0, y1 = .35, 2.65, .9, 2.2
    walls(x0, x1, y0, y1, h, 2 if age == 2 else 1, M, frame=False); roof(x0, x1, y0, y1, h, .6, 2 if age == 2 else 1, M, 'x', over=.06)
    for k in range(4): window(.8 + k * .5, .4, M, 'y', w=.08, h=.28, at=y1)
    door(.4, .65, x1, .45, M, face='x')
    th = h + (.9 if age == 1 else 1.3); box(.3, .9, .3, .9, 0, th, M['stone'], 'torre_sino'); window(.6, th - .35, M, 'y', w=.16, h=.22, at=.9); window(.6, th - .35, M, 'x', w=.16, h=.22, at=.9)
    if age == 1: pyramid(.3, .9, .3, .9, th, .45, M['shingle'], over=.05)
    else: cone(.6, .6, th, .75, .42, M['slate'], seg=16); cyl(.6, .6, th + .75, th + .9, .015, M['gold'], seg=6)
    if age == 2:
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=.2, radius2=.2, depth=.03)
        bmesh.ops.transform(bm, matrix=Matrix.Translation((x1 + .01, -1.55, h * .72)) @ Matrix.Rotation(R(90), 4, 'Y'), verts=bm.verts); mesh_obj('rosacea', bm, M['gold'])
        for y in (1.1, 2.0): banner(x1 + .03, y, h - .05, .18, .4, M['banner'], face='x')
def mercado(age, M):
    box(.1, 2.9, .1, 2.9, 0, .02, M['dirt'], 'praca')
    def stall(x0, y0, w, d, col):
        box(x0, x0 + w, y0, y0 + d, 0, .2, M['plank'], 'banca')
        for x, y in ((x0, y0), (x0 + w, y0), (x0, y0 + d), (x0 + w, y0 + d)): cyl(x, y, 0, .5, .015, M['wood'], seg=5)
        n = 5
        for k in range(n):  # toldo às riscas (azul = cor da equipa)
            a = x0 - .05 + (w + .1) * k / n; b = x0 - .05 + (w + .1) * (k + 1) / n
            bm = bmesh.new(); vs = [bm.verts.new(v) for v in ((a, -(y0 - .05), .55), (b, -(y0 - .05), .55), (b, -(y0 + d + .12), .43), (a, -(y0 + d + .12), .43))]
            bm.faces.new(vs); o = mesh_obj('toldo', bm, M['banner'] if k % 2 else M['cloth']); o.modifiers.new('s', 'SOLIDIFY').thickness = .01
        for k in range(4): cyl(x0 + .1 + k * (w - .2) / 3, y0 + d / 2, .2, .26, .04, [M['fire'], M['gold'], M['thatch'], M['cloth']][k % 4], seg=8)
    stall(.25, .3, .9, .5, 0); stall(1.65, .3, .9, .5, 1); stall(.25, 1.9, .9, .5, 2)
    cyl(2.0, 2.1, 0, .2, .26, M['stone'], seg=16); cyl(2.0, 2.1, .15, .21, .22, M['vao'], seg=16); cyl(2.0, 2.1, .2, .7, .02, M['wood'], seg=5)
    for x, y in ((1.3, 1.4), (1.45, 1.5)): barrel(x, y, M)
    if age == 2: flag(2.0, 2.1, .7, .35, M['banner'], M)
def oficina(age, M):
    h = (0, .75, .85)[age]; x0, x1, y0, y1 = .25, 2.75, .25, 1.6
    for x in (x0, 1.5, x1):
        for y in (y0, y1): cyl(x, y, 0, h, .05, M['wood'], seg=7)
    box(x0, x1, y0, y0 + .08, .08, h, M['plank'] if age == 1 else M['stone'], 'parede_fundo')
    roof(x0, x1, y0, y1, h, .5, age, M, 'x')
    for x in (.75, 1.35):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=.2, radius2=.2, depth=.06)
        bmesh.ops.transform(bm, matrix=Matrix.Translation((x, -2.25, .2)) @ Matrix.Rotation(R(90), 4, 'X'), verts=bm.verts); mesh_obj('roda', bm, M['wood'])
    box(1.6, 2.6, .7, 1.0, .25, .35, M['plank'], 'chassis'); box(1.7, 2.5, .76, .94, .35, .42, M['wood'], 'braco')
    for k in range(4): hlog(1.8, 2.6, 2.2 + k * .06, .04 + (k % 2) * .06, .035, M['wood'], 'x')
    if age == 2: banner(1.5, y1 + .03, h - .03, .2, .3, M['banner'])
def centro(age, M):
    if age == 0:
        walls(.3, 2.7, .5, 2.3, .62, 0, M); roof(.3, 2.7, .5, 2.3, .62, .75, 0, M, 'x', over=.12)
        door(1.3, 1.7, 2.3, .4, M); window(.7, .35, M); window(2.3, .35, M); window(1.4, .35, M, 'x', at=2.7)
        for x in (.15, 2.85): cyl(x, 2.5, 0, .9, .04, M['wood'], tip=.1, seg=7)
        banner(1.5, 2.33, .6, .3, .36, M['banner']); flag(.3, .5, 1.3, .4, M['banner'], M)
        for x, y in ((2.6, 2.6), (2.75, 2.55)): barrel(x, y, M)
    elif age == 1:
        walls(.3, 2.7, .6, 2.4, .8, 1, M); roof(.3, 2.7, .6, 2.4, .8, .65, 1, M, 'x')
        box(.2, 1.0, .2, 1.0, 0, 1.75, M['stone'], 'torre'); pyramid(.2, 1.0, .2, 1.0, 1.75, .55, M['shingle'], over=.06)
        window(.6, 1.3, M, 'y', w=.12, h=.2, at=1.0); window(.6, 1.3, M, 'x', w=.12, h=.2, at=1.0)
        door(1.3, 1.7, 2.4, .45, M); window(.8, .45, M); window(2.2, .45, M); window(1.5, .45, M, 'x', at=2.7)
        banner(1.5, 2.43, .78, .32, .42, M['banner']); flag(.6, .6, 2.3, .45, M['banner'], M)
    else:
        walls(.3, 2.7, .5, 2.5, 1.0, 2, M); merlons(.3, 2.7, .5, 2.5, 1.0, M['stone'], 8, size=.1, h=.12)
        box(.4, 2.6, .6, 2.4, 1.0, 1.04, M['stone_dk'], 'adarve'); roof(.6, 2.4, .9, 2.1, 1.04, .55, 2, M, 'x')
        for x, y in ((.3, .5), (2.7, .5), (.3, 2.5), (2.7, 2.5)):
            cyl(x, y, 0, 1.45, .26, M['stone'], seg=16); cone(x, y, 1.45, .6, .32, M['slate'], seg=16)
        cyl(.3, .5, 2.05, 2.2, .015, M['gold'], seg=6); flag(2.7, 2.5, 2.05, .4, M['banner'], M)
        door(1.3, 1.7, 2.5, .55, M); box(1.25, 1.75, 2.5, 2.53, .63, .7, M['stone_dk'], 'verga')
        for y in (1.2, 1.9): banner(2.73, y, .95, .22, .5, M['banner'], face='x')
        banner(1.5, 2.53, .98, .3, .5, M['banner'])
def maravilha(age, M):
    box(.2, 3.8, .2, 3.8, 0, .12, M['stone_dk'], 'plinto'); box(.35, 3.65, .35, 3.65, .12, .24, M['stone'], 'degrau')
    walls(.7, 3.3, .7, 3.3, 1.3, 2, M, frame=False); merlons(.7, 3.3, .7, 3.3, 1.3, M['stone'], 9, size=.1, h=.12)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0)
    for v in bm.verts: v.co.z = max(v.co.z, 0)
    bmesh.ops.transform(bm, matrix=Matrix.Translation((2.0, -2.0, 1.3)), verts=bm.verts); mesh_obj('cupula', bm, M['gold'])
    cyl(2.0, 2.0, 2.3, 2.75, .04, M['gold'], seg=8)
    for x, y in ((.55, .55), (3.45, .55), (.55, 3.45), (3.45, 3.45)):
        cyl(x, y, 0, 2.1, .3, M['stone'], seg=16); cone(x, y, 2.1, .8, .36, M['slate'], seg=16); flag(x, y, 2.85, .4, M['banner'], M)
        for zz in (.7, 1.4): window(x, zz, M, 'y', w=.08, h=.2, at=y + .3) if y > 2 else None
    for k in range(5): box(1.2 + k * .4 - .07, 1.2 + k * .4 + .07, 3.3, 3.42, .24, 1.15, M['stone'], 'coluna')
    door(1.75, 2.25, 3.3, .7, M); for_y = [banner(3.33, y, 1.2, .25, .7, M['banner'], face='x') for y in (1.4, 2.6)]
    banner(2.0, 3.43, 1.25, .35, .7, M['banner'])
B = {'casa': ((2, 2), (0, 1, 2), casa), 'armazem': ((2, 2), (0, 1, 2), armazem), 'quartel': ((3, 3), (0, 1, 2), quartel), 'arquearia': ((3, 3), (0, 1, 2), arquearia),
     'estabulo': ((3, 3), (0, 1, 2), estabulo), 'doca': ((2, 2), (0, 1, 2), doca), 'torre': ((2, 2), (1, 2, 3), torre), 'ferreiro': ((2, 2), (0, 1, 2), ferreiro),
     'templo': ((3, 3), (1, 2), templo), 'mercado': ((3, 3), (1, 2), mercado), 'oficina': ((3, 3), (1, 2), oficina), 'centro': ((3, 3), (0, 1, 2), centro), 'maravilha': ((4, 4), (2,), maravilha)}
def scene_for(w, h):
    sc = g['SCN'](); RX = int((w + h) * 64 * 1.25 + 40); RY = int(RX * 1.05)
    g['RES'] = (RX, RY); cam = g['scene']()
    cam.data.ortho_scale = RX / PXU
    c = Vector((w / 2, -h / 2, 0)); d = Vector((1, -1, 0)).normalized() * math.cos(R(30)) + Vector((0, 0, math.sin(R(30))))
    cam.location = c + d * 30; cam.data.shift_y = .16
    gobj = next(o for o in sc.objects if o.name == 'g'); gobj.scale = (w, h, 1); gobj.location = (w / 2 - .5, -(h / 2 - .5), 0)
    return sc, cam
info = {}
only = os.environ.get('ONLY', '')
for name, ((w, h), ages, fn) in B.items():
    if only and name not in only.split(','): continue
    for age in ages:
        g['reset'](); G.clear(); M = g['mats'](); sc, cam = scene_for(w, h)
        fn(age, M); finish(list(G))
        key = f'{name}|{age}'; sc.render.filepath = os.path.join(OUT, f'{name}_{age}.png')
        with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]): bpy.ops.render.render(write_still=True)
        a = world_to_camera_view(sc, cam, Vector((0, 0, 0))); info[key] = [a.x * sc.render.resolution_x, (1 - a.y) * sc.render.resolution_y, w, h]
        print('REN', key, flush=True)
af = os.path.join(OUT, 'anchors.json'); old = json.load(open(af)) if os.path.exists(af) else {}
old.update(info); json.dump(old, open(af, 'w'), indent=1); print('FEITO')
