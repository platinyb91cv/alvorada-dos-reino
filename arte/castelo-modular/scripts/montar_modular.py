# Conjunto modular de muralhas + torre redonda do Alvorada dos Reinos, numa única cena do Blender.
# - Câmara ortográfica, azimute 45°, elevação 30° (eixos do chão 2:1), PXU = 90,5 px por casa a 2x (a mesma em todas as peças).
# - Uma luz, um material de pedra com textura presa ao MUNDO e período de 1 casa (peças vizinhas emendam sem costura).
# - Sem apanha-sombras: fundo transparente e nenhuma sombra de chão embutida (o jogo projeta a sua).
# - Muros: módulos de 1 casa, espessura T, caminho de ronda a H. Cada peça é a união (sem faces internas) dos braços que tem
#   (16 máscaras: 1=+x 2=+y 4=−x 8=−y). Nas junções, parapeito e ameias só nos lados sem braço (o caminho de ronda fica livre).
#   O braço para um vizinho continua para lá da casa e o integrador corta a coluna de ecrã da casa nesse lado.
# - Torre: cilindro de diâmetro 1,7 casas numa pegada 2x2, piso superior a 3,3. Objeto à parte.
#   Os 8 pedaços de muro que entram na torre (2 por lado) são renderizados com a torre como HOLDOUT: só fica o que está à
#   frente da torre (recorte exato por profundidade, sem cortes retos), e com a mesma câmara da torre (mesma âncora).
# Coordenadas do jogo: x, y no chão (1 casa = 1), z para cima; no Blender Y = −y.
# Uso: WORK=<pasta com montar_portao2.py> OUT=<saída> [BLOCK=1] [ONLY=testes] blender -b --python montar_modular.py
import bpy, bmesh, os, json, math
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
work = os.environ['WORK']; OUT = os.environ['OUT']; os.makedirs(OUT, exist_ok=True)
lib = open(os.path.join(work, 'montar_portao2.py'), encoding='utf-8').read().replace('\r\n', '\n'); lib = lib[:lib.index('reset(); M = mats()')]
g = {'__name__': 'lib'}; exec(compile(lib, 'montar_portao2.py', 'exec'), g)
G, finish, flag, mesh_obj = g['G'], g['finish'], g['flag'], g['mesh_obj']
BLOCK = os.environ.get('BLOCK') == '1'; ONLY = os.environ.get('ONLY', '')
PXU = g['PXU']; R = math.radians
T = .62; hw = T / 2                                  # espessura comum
H = {'pedra': 1.3, 'fort': 1.5}                      # caminho de ronda
TOWER_R, TOWER_FLOOR = .85, 3.3
EXT = 1.4                                            # braço para lá da casa (o integrador corta)
GCUT = .27                                           # casa do portão vizinha ocupa até 0,28 desta casa
def gv(x, y, z=0.0): return (x, -y, z)               # jogo -> Blender

# ---------- materiais: textura presa ao mundo, período 1 casa, mesma em todas as peças ----------
TEX = os.environ.get('TEX_DIR', '')
def pedra_mat(name, tid, per, tint, sat, val, normal=1.6):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links; bs = N['Principled BSDF']
    p = lambda k: os.path.join(TEX, f'{tid}_{k}.jpg')
    if BLOCK or not TEX or not os.path.exists(p('diff')):
        bs.inputs['Base Color'].default_value = (*[v * val for v in tint], 1); bs.inputs['Roughness'].default_value = .9; return m
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (per, per, per)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])  # todos os objetos têm origem no mundo: Object = mundo (sem desvio aleatório)
    def img(k, color):
        t = N.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(p(k), check_existing=True); t.projection = 'BOX'; t.projection_blend = .2
        if not color: t.image.colorspace_settings.name = 'Non-Color'
        L.new(mp.outputs['Vector'], t.inputs['Vector']); return t
    d = img('diff', True); hs = N.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = sat; hs.inputs['Value'].default_value = val; L.new(d.outputs['Color'], hs.inputs['Color'])
    mu = N.new('ShaderNodeMixRGB'); mu.blend_type = 'MULTIPLY'; mu.inputs['Fac'].default_value = 1; L.new(hs.outputs['Color'], mu.inputs[1]); mu.inputs[2].default_value = (*tint, 1)
    L.new(mu.outputs[0], bs.inputs['Base Color'])
    if os.path.exists(p('rough')): r = img('rough', False); L.new(r.outputs['Color'], bs.inputs['Roughness'])
    if os.path.exists(p('nor')): n = img('nor', False); nm = N.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = normal; L.new(n.outputs['Color'], nm.inputs['Color']); L.new(nm.outputs['Normal'], bs.inputs['Normal'])
    return m
def plain(name, col, rough=.8, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True; bs = m.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (*col, 1); bs.inputs['Roughness'].default_value = rough; bs.inputs['Metallic'].default_value = metal; return m
def mats():
    M = {}
    M['stone'] = pedra_mat('mod_pedra', 'large_sandstone_blocks_01', 1.0, (.9, .9, .88), .12, 1.0)
    M['stone_dk'] = pedra_mat('mod_pedra_esc', 'medieval_blocks_02', 2.0, (.82, .82, .8), .1, .72)
    M['walk'] = pedra_mat('mod_adarve', 'medieval_blocks_02', 2.0, (.78, .76, .72), .12, .8)
    M['wood'] = pedra_mat('mod_madeira', 'brown_planks_05', 2.0, (.9, .78, .62), .9, .9) if not BLOCK else plain('mod_madeira', (.35, .24, .14))
    M['vao'] = plain('mod_vao', (.03, .025, .02), .95); M['iron'] = plain('mod_ferro', (.12, .12, .13), .5, .8)
    M['banner'] = plain('mod_bandeira', (.11, .2, .78), .7); M['gold'] = plain('mod_ouro', (.75, .55, .2), .35, .9)
    if BLOCK:
        for k, c in (('stone', (.62, .62, .6)), ('stone_dk', (.45, .45, .44)), ('walk', (.5, .48, .45))): M[k] = plain('blk_' + k, c)
    return M

# ---------- geometria: união retilínea sem faces internas ----------
def union_prism(rects, z0, z1, mat, name, top_mat=None):
    """rects = [(x0,x1,y0,y1)] em coordenadas do jogo. Constrói UMA malha fechada: só as faces de fronteira (sem faces internas)."""
    rects = [tuple(round(v, 6) for v in r) for r in rects]
    xs = sorted({v for r in rects for v in r[:2]}); ys = sorted({v for r in rects for v in r[2:]})
    cov = {(i, j) for i in range(len(xs) - 1) for j in range(len(ys) - 1)
           if any(r[0] <= (xs[i] + xs[i + 1]) / 2 <= r[1] and r[2] <= (ys[j] + ys[j + 1]) / 2 <= r[3] for r in rects)}
    bm = bmesh.new(); V = {}
    def v(x, y, z):
        k = (round(x, 6), round(y, 6), round(z, 6))
        if k not in V: V[k] = bm.verts.new(gv(x, y, z))
        return V[k]
    tops = []
    for (i, j) in cov:
        a, b, c, d = xs[i], xs[i + 1], ys[j], ys[j + 1]
        tops.append(bm.faces.new((v(a, c, z1), v(b, c, z1), v(b, d, z1), v(a, d, z1)))); bm.faces.new((v(a, c, z0), v(a, d, z0), v(b, d, z0), v(b, c, z0)))
        if (i + 1, j) not in cov: bm.faces.new((v(b, c, z0), v(b, d, z0), v(b, d, z1), v(b, c, z1)))
        if (i - 1, j) not in cov: bm.faces.new((v(a, c, z0), v(a, c, z1), v(a, d, z1), v(a, d, z0)))
        if (i, j + 1) not in cov: bm.faces.new((v(a, d, z0), v(a, d, z1), v(b, d, z1), v(b, d, z0)))
        if (i, j - 1) not in cov: bm.faces.new((v(a, c, z0), v(b, c, z0), v(b, c, z1), v(a, c, z1)))
    if top_mat is not None:
        for f in tops: f.material_index = 1
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.dissolve_limit(bm, angle_limit=R(1), verts=bm.verts, edges=bm.edges, delimit={'MATERIAL'})
    o = mesh_obj(name, bm, mat)
    if top_mat is not None: o.data.materials.append(top_mat)
    return o
def box(x0, x1, y0, y1, z0, z1, mat, name='box'): return union_prism([(x0, x1, y0, y1)], z0, z1, mat, name)
def rbox(cx, cy, ang, ln, wd, z0, z1, mat, name='rbox'):  # caixa rodada (ang em graus, no plano do jogo; eixo 'ln' na direção ang)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=(ln, wd, z1 - z0), verts=bm.verts)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(gv(cx, cy, (z0 + z1) / 2)) @ Matrix.Rotation(-R(ang), 4, 'Z'), verts=bm.verts)
    return mesh_obj(name, bm, mat)
def cylz(cx, cy, r, z0, z1, mat, seg=48, name='cil'):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
    bmesh.ops.translate(bm, vec=gv(cx, cy, (z0 + z1) / 2), verts=bm.verts)
    for f in bm.faces: f.smooth = True
    o = mesh_obj(name, bm, mat); [setattr(p, 'use_smooth', True) for p in o.data.polygons]; return o

# ---------- muralha de 1 casa ----------
def arms(m, gb):
    """Braços (eixo, a0, a1) ao longo do eixo, na casa 0..1 (linha do meio a 0,5). Ligados: prolongam EXT; portão vizinho: param em GCUT."""
    if m == 0: return [('x', .06, .94)]
    A = []
    def a(axis, plus):
        if plus: return (axis, .5 - hw, .5 + EXT)
        lo = GCUT if (axis == 'x' and gb & 4 or axis == 'y' and gb & 8) else .5 - EXT
        return (axis, lo, .5 + hw)
    if m & 5 == 5: A.append(('x', (GCUT if gb & 4 else .5 - EXT), .5 + EXT))
    elif m & 1: A.append(a('x', True))
    elif m & 4: A.append(a('x', False))
    if m & 10 == 10: A.append(('y', (GCUT if gb & 8 else .5 - EXT), .5 + EXT))
    elif m & 2: A.append(a('y', True))
    elif m & 8: A.append(a('y', False))
    return A
def rect(axis, a0, a1, w0, w1): return (a0, a1, .5 + w0, .5 + w1) if axis == 'x' else (.5 + w0, .5 + w1, a0, a1)
def parapets(m, gb, A):
    """Faixas de parapeito: dos dois lados de cada braço (do lado de fora da junção até à ponta) e, na junção, nos lados sem braço."""
    pw = .075; S = []
    jun = not (m in (5, 10) or m == 0)
    for axis, a0, a1 in A:
        for side in (-1, 1):
            w = (hw - pw, hw) if side > 0 else (-hw, -hw + pw)
            if jun:  # na junção os lados dos braços começam na face da junção (o canto exterior é fechado pela faixa da junção)
                plus = a1 > .5 + hw + 1e-6; lo, hi = (.5 - hw, a1) if plus else (a0, .5 + hw)
                S.append(rect(axis, lo, hi, *w))
            else: S.append(rect(axis, a0, a1, *w))
    if jun:  # lados da junção sem braço
        for bit, axis, side in ((1, 'y', 1), (4, 'y', -1), (2, 'x', 1), (8, 'x', -1)):
            if not m & bit:
                # faixa perpendicular ao lado: no lado +x (bit 1) é uma faixa ao longo de y em x = .5+hw
                c = (.5 + hw - pw, .5 + hw) if side > 0 else (.5 - hw, .5 - hw + pw)
                S.append((c[0], c[1], .5 - hw, .5 + hw) if axis == 'y' else (.5 - hw, .5 + hw, c[0], c[1]))
    if m == 0:  # muro sozinho: fecha as duas pontas
        S += [(.06, .06 + pw, .5 - hw, .5 + hw), (.94 - pw, .94, .5 - hw, .5 + hw)]
    return S
def merlon_list(S):
    """Ameias sobre as faixas: período 0,25 casa presas ao mundo (t = 0,125 + 0,25 k), para emendarem entre casas."""
    out = []
    for (x0, x1, y0, y1) in S:
        along_x = (x1 - x0) >= (y1 - y0)
        a0, a1 = (x0, x1) if along_x else (y0, y1)
        for k in range(-12, 20):
            t = .125 + .25 * k
            if a0 + .02 <= t - .065 and t + .065 <= a1 - .02 or (a1 - a0 < .3 and a0 <= t <= a1):
                r = (t - .065, t + .065, y0, y1) if along_x else (x0, x1, t - .065, t + .065)
                # sem ameias repetidas ou sobrepostas (faixas da junção e dos braços coincidem): superfícies coincidentes saem pretas
                if not any(r[0] < q[1] - 1e-4 and q[0] < r[1] - 1e-4 and r[2] < q[3] - 1e-4 and q[2] < r[3] - 1e-4 for q in out): out.append(r)
    return out
def muro(tp, m, gb, M):
    Hh = H[tp]; A = arms(m, gb)
    core = [rect(ax, a0, a1, -hw, hw) for ax, a0, a1 in A] + ([] if m in (0, 5, 10) else [(.5 - hw, .5 + hw, .5 - hw, .5 + hw)])
    base = [rect(ax, a0, a1, -hw - .04, hw + .04) for ax, a0, a1 in A] + ([] if m in (0, 5, 10) else [(.5 - hw - .04, .5 + hw + .04, .5 - hw - .04, .5 + hw + .04)])
    union_prism(base, 0, .14, M['stone_dk'], 'base')
    union_prism(core, .14, Hh, M['stone'], 'nucleo', top_mat=M['walk'])
    if BLOCK: return
    S = parapets(m, gb, A); union_prism(S, Hh, Hh + .1, M['stone'], 'parapeito')
    for r in merlon_list(S): box(*r, Hh + .1, Hh + .3, M['stone'], 'merlon')
    union_prism([rect(ax, a0, a1, -hw - .012, hw + .012) for ax, a0, a1 in A], Hh - .1, Hh - .06, M['stone_dk'], 'cornija')
    if tp == 'fort':  # seteiras nas faces de fora, período 0,5
        for ax, a0, a1 in A:
            for k in range(-4, 6):
                t = .25 + .5 * k
                if a0 + .08 < t < a1 - .08 and not (abs(t - .5) < hw + .05 and m not in (5, 10)):
                    for s in (-1, 1):
                        w = hw + .006
                        if ax == 'x': box(t - .014, t + .014, .5 + s * w - .006, .5 + s * w + .006, Hh * .45, Hh * .75, M['vao'], 'seteira')
                        else: box(.5 + s * w - .006, .5 + s * w + .006, t - .014, t + .014, Hh * .45, Hh * .75, M['vao'], 'seteira')

# ---------- torre redonda 2x2 ----------
def torre(M):
    cx = cy = 1.0; F = TOWER_FLOOR; objs = []
    objs.append(cylz(cx, cy, TOWER_R + .04, 0, .16, M['stone_dk'], name='base_torre'))
    objs.append(cylz(cx, cy, TOWER_R, .16, F - .32, M['stone'], name='corpo'))
    if not BLOCK:
        for k in range(24):  # mísulas (machicolagem)
            a = k * 15; ca, sa = math.cos(R(a)), math.sin(R(a))
            objs.append(rbox(cx + ca * (TOWER_R + .03), cy + sa * (TOWER_R + .03), a, .1, .09, F - .5, F - .32, M['stone'], 'misula'))
    objs.append(cylz(cx, cy, TOWER_R + .07, F - .32, F, M['stone'], name='coroa'))
    objs.append(cylz(cx, cy, TOWER_R - .02, F - .04, F + .005, M['wood'], name='piso'))
    if not BLOCK:
        n = 40
        for k in range(n):  # parapeito do topo (anel) e ameias
            a = k * 360 / n; ca, sa = math.cos(R(a)), math.sin(R(a)); rr = TOWER_R + .03
            objs.append(rbox(cx + ca * rr, cy + sa * rr, a + 90, 2 * math.pi * rr / n * 1.08, .09, F, F + .14, M['stone'], 'anel'))
        for k in range(14):
            a = k * 360 / 14 + 6; ca, sa = math.cos(R(a)), math.sin(R(a)); rr = TOWER_R + .03
            objs.append(rbox(cx + ca * rr, cy + sa * rr, a + 90, .2, .11, F + .14, F + .36, M['stone'], 'merlon'))
        dang = 45  # porta virada para o jogador (+x,+y)
        ca, sa = math.cos(R(dang)), math.sin(R(dang))
        objs.append(rbox(cx + ca * (TOWER_R + .005), cy + sa * (TOWER_R + .005), dang + 90, .2, .02, .16, .52, M['wood'], 'porta'))
        objs.append(rbox(cx + ca * (TOWER_R + .012), cy + sa * (TOWER_R + .012), dang + 90, .26, .02, .5, .56, M['stone_dk'], 'verga'))
        for a, z in ((15, 1.5), (75, 1.5), (45, 2.25), (5, 2.4), (85, 2.4), (45, 1.1)):
            ca, sa = math.cos(R(a)), math.sin(R(a))
            objs.append(rbox(cx + ca * (TOWER_R + .004), cy + sa * (TOWER_R + .004), a + 90, .035, .01, z, z + .26, M['vao'], 'seteira'))
        flag(cx + .45, cy - .45, F + .3, 1.0, M['banner'], {**M, 'wood': M['wood'], 'gold': M['gold']})
    return [o for o in G]

# ---------- pedaços de muro que entram na torre (ranhuras): lado (+x,−x,+y,−y) x fila (0,1) ----------
SLOTS = [('px', 0), ('px', 1), ('mx', 0), ('mx', 1), ('py', 0), ('py', 1), ('my', 0), ('my', 1)]
def slot_geom(side, row):
    """Casa da pegada onde o pedaço fica (i,j), eixo e braço: do centro da torre até à borda da pegada (+EXT para o corte)."""
    if side in ('px', 'mx'):
        j = row; i = 1 if side == 'px' else 0
        return (i, j), 'x', ((1.0, 2.0 + EXT) if side == 'px' else (-EXT, 1.0)), j + .5
    i = row; j = 1 if side == 'py' else 0
    return (i, j), 'y', ((1.0, 2.0 + EXT) if side == 'py' else (-EXT, 1.0)), i + .5
def pedaco(tp, side, row, M):
    (i, j), ax, (a0, a1), c = slot_geom(side, row); Hh = H[tp]
    rr = lambda w0, w1: (a0, a1, c + w0, c + w1) if ax == 'x' else (c + w0, c + w1, a0, a1)
    union_prism([rr(-hw - .04, hw + .04)], 0, .14, M['stone_dk'], 'base'); union_prism([rr(-hw, hw)], .14, Hh, M['stone'], 'nucleo', top_mat=M['walk'])
    if BLOCK: return (i, j)
    pw = .075; S = [rr(hw - pw, hw), rr(-hw, -hw + pw)]
    union_prism(S, Hh, Hh + .1, M['stone'], 'parapeito')
    # ameias: mesmo período global (a casa da pegada é inteira, logo o período de 0,25 bate com as casas de fora)
    for r in merlon_list(S): box(*r, Hh + .1, Hh + .3, M['stone'], 'merlon')
    union_prism([rr(-hw - .012, hw + .012)], Hh - .1, Hh - .06, M['stone_dk'], 'cornija')
    return (i, j)

# ---------- cena ----------
g['reset'](); sc = g['SCN'](); M = mats(); cam = g['scene']()
for o in list(sc.objects):
    if o.name.startswith('g') and o.type == 'MESH' and getattr(o, 'is_shadow_catcher', False): bpy.data.objects.remove(o, do_unlink=True)  # sem sombra de chão
if BLOCK: sc.cycles.samples = 8
HOLD = bpy.data.materials.new('recorte_torre'); HOLD.use_nodes = True; _n = HOLD.node_tree.nodes; _o = _n['Material Output']
_h = _n.new('ShaderNodeHoldout'); HOLD.node_tree.links.new(_h.outputs[0], _o.inputs['Surface'])
def frame(target, res):  # câmara (mesma orientação e PXU) apontada a um ponto do jogo
    sc.render.resolution_x, sc.render.resolution_y = res; cam.data.ortho_scale = res[0] / PXU; cam.data.shift_y = 0
    d = Vector((1, -1, 0)).normalized() * math.cos(R(30)) + Vector((0, 0, math.sin(R(30))))
    cam.location = Vector(gv(*target)) + d * 30; sc.view_layers[0].update()
def anchor():
    a = world_to_camera_view(sc, cam, Vector((0, 0, 0))); return [a.x * sc.render.resolution_x, (1 - a.y) * sc.render.resolution_y]
def scr(x, y, z):
    a = world_to_camera_view(sc, cam, Vector(gv(x, y, z))); return [round(a.x * sc.render.resolution_x, 2), round((1 - a.y) * sc.render.resolution_y, 2)]
def clear():
    for o in list(G): bpy.data.objects.remove(o, do_unlink=True)
    G.clear()
def render(name):
    finish([o for o in G if o.name.split('.')[0] in ('merlon', 'parapeito', 'misula', 'porta', 'verga')])
    sc.render.filepath = os.path.join(OUT, name + '.png')
    with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]): bpy.ops.render.render(write_still=True)
    print('REN', name, flush=True)
info = {}
TYPES = os.environ.get('TYPES', 'pedra,fort').split(',')
MASKS = list(range(16)) if ONLY != 'testes' else [1, 2, 4, 8, 5, 10, 3, 6, 9, 12, 15]
WRES = (400, 420); TRES = (460, 720)
for tp in TYPES:
    frame((.5, .5, .7), WRES)
    for m in MASKS:
        for gb in [0] + ([4] if m & 4 and ONLY != 'testes' else []) + ([8] if m & 8 and ONLY != 'testes' else []) + ([12] if m & 12 == 12 and ONLY != 'testes' else []):
            clear(); muro(tp, m, gb, M); name = f'{tp}_{m}' + (f'_g{gb}' if gb else ''); render(name)
            # lados cortados (coluna da casa): direita se o braço continua para +x ou −y; esquerda se para −x ou +y
            cutR = bool(m & 1 or (m & 8 and not gb & 8)); cutL = bool((m & 4 and not gb & 4) or m & 2)
            links = {k: scr(*p, H[tp]) for k, p, b in (('px', (1, .5), 1), ('py', (.5, 1), 2), ('mx', (0, .5), 4), ('my', (.5, 0), 8)) if m & b}
            info[name] = {'anchor': anchor(), 'cut': [cutL, cutR], 'col': [0, 0], 'links': links, 'walk': H[tp]}
    # pedaços que entram na torre: mesma câmara da torre, torre como holdout e sem projetar sombra neles
    frame((1, 1, 1.9), TRES)
    for side, row in SLOTS:
        clear(); tw = torre(M)
        for o in tw:  # torre = recorte: material holdout (tapa também os contornos), fora dos contornos, sem sombra
            if o.type == 'MESH':
                o.data.materials.clear(); o.data.materials.append(HOLD)
                for p in o.data.polygons: p.material_index = 0
            for k in ('visible_shadow', 'visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'): setattr(o, k, False)  # só a câmara a vê: luz igual à das casas de muro
            for cl in list(o.users_collection): cl.objects.unlink(o)
            bpy.data.collections['chao'].objects.link(o)
        nb = len(G); ij = pedaco(tp, side, row, M); name = f'tw_{tp}_{side}{row}'; render(name)
        info[name] = {'anchor': anchor(), 'cut': [True, True], 'col': list(ij), 'links': {}, 'walk': H[tp]}
frame((1, 1, 1.9), TRES); clear(); torre(M); render('torre3')
info['torre3'] = {'anchor': anchor(), 'cut': [False, False], 'col': [0, 0], 'walk': TOWER_FLOOR,
                  'links': {f'{s}{r}': scr(*(lambda ij, ax, a, c: ((2.0 if s == 'px' else 0.0), c) if ax == 'x' else (c, (2.0 if s == 'py' else 0.0)))(*slot_geom(s, r)), 1.3) for s, r in SLOTS}}
json.dump({'pxPerUnit': PXU, 'T': T, 'H': H, 'towerR': TOWER_R, 'towerFloor': TOWER_FLOOR, 'block': BLOCK, 'pieces': info}, open(os.path.join(OUT, 'anchors.json'), 'w'), indent=1)
print('FEITO', len(info))
