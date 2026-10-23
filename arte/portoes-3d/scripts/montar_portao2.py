# Portões 3D para o Alvorada dos Reinos (0 créditos): modelados por código no Blender e renderizados na câmara
# isométrica do jogo (2:1, ortográfica). Variantes: madeira idade 0/1/2, pedra idade 1/2; direções x/y; portas 0/½/aberta.
# Coordenadas: 1 casa = 1 unidade; Blender X = x do jogo, Blender Y = −y do jogo (a câmara fica do lado de +x,+y do jogo).
import bpy, bmesh, math, os, json, random
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
OUT = os.environ.get('OUT', '/tmp/claude-0/portao/render'); os.makedirs(OUT, exist_ok=True)
VARS = os.environ.get('VARS', 'madeira0,madeira1,madeira2,pedra1,pedra2').split(',')
PXU = 2 * 64 / math.sqrt(2)  # px por unidade a 2× (o atlas guarda a 2× do ecrã, como os edifícios)
RES = (360, 400); SAMPLES = int(os.environ.get('SAMPLES', '96'))
R = math.radians

def SCN(): return bpy.data.scenes['portoes']
def reset():  # cena própria "portoes" (não mexe no resto do ficheiro do utilizador)
    old = bpy.data.scenes.get('portoes')
    if old:
        for o in list(old.objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.scenes.remove(old)
    for c in list(bpy.data.collections):
        if c.name.startswith('chao'): bpy.data.collections.remove(c)
    sc = bpy.data.scenes.new('portoes')
    for w in bpy.context.window_manager.windows: w.scene = sc
    for m in list(bpy.data.meshes):
        if m.users == 0: bpy.data.meshes.remove(m)
    for m in list(bpy.data.materials):
        if m.users == 0: bpy.data.materials.remove(m)

# ---------- materiais ----------
def node_mat(name, base, rough=.8, metal=0, bump=.3, noise=8, var=.25, brick=None, emit=None):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    bs = N['Principled BSDF']; bs.inputs['Roughness'].default_value = rough; bs.inputs['Metallic'].default_value = metal
    tc = N.new('ShaderNodeTexCoord'); oi = N.new('ShaderNodeObjectInfo')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = noise; nz.inputs['Detail'].default_value = 6
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (*[c * (1 - var) for c in base], 1); ramp.color_ramp.elements[1].color = (*[min(1, c * (1 + var)) for c in base], 1)
    mix = N.new('ShaderNodeMath'); mix.operation = 'ADD'; L.new(nz.outputs['Fac'], mix.inputs[0]); L.new(oi.outputs['Random'], mix.inputs[1]); mix.inputs[1].default_value = 0
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY_ADD'; L.new(oi.outputs['Random'], mul.inputs[0]); mul.inputs[1].default_value = .35; L.new(nz.outputs['Fac'], mul.inputs[2])
    L.new(mul.outputs[0], ramp.inputs['Fac']); col = ramp.outputs['Color']; height = nz.outputs['Fac']
    if brick:  # blocos de pedra/telha: coordenada horizontal = x + y (serve as duas faces visíveis de caixas alinhadas)
        sx = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sx.inputs[0])
        ad = N.new('ShaderNodeMath'); ad.operation = 'ADD'; L.new(sx.outputs[0], ad.inputs[0]); L.new(sx.outputs[1], ad.inputs[1])
        cb = N.new('ShaderNodeCombineXYZ'); L.new(ad.outputs[0], cb.inputs[0]); L.new(sx.outputs[2], cb.inputs[1])
        br = N.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = brick[0]; br.inputs['Mortar Size'].default_value = brick[1]
        br.inputs['Brick Width'].default_value = brick[2]; br.inputs['Row Height'].default_value = brick[3]; br.offset = .5
        L.new(cb.outputs[0], br.inputs['Vector']); L.new(col, br.inputs['Color1'])
        dk = N.new('ShaderNodeMixRGB'); dk.blend_type = 'MULTIPLY'; dk.inputs['Fac'].default_value = 1; L.new(col, dk.inputs[1]); dk.inputs[2].default_value = (.82, .78, .72, 1)
        L.new(dk.outputs[0], br.inputs['Color2']); br.inputs['Mortar'].default_value = (*[c * .55 for c in base], 1)
        col = br.outputs['Color']; height = br.outputs['Fac']
    L.new(col, bs.inputs['Base Color'])
    if bump:
        b = N.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump; L.new(height, b.inputs['Height']); L.new(b.outputs['Normal'], bs.inputs['Normal'])
    if emit:
        bs.inputs['Emission Color'].default_value = (*emit, 1); bs.inputs['Emission Strength'].default_value = 6
    return m
TEX = os.environ.get('TEX_DIR', '')
def tex_mat(name, tid, scale, tint=(1, 1, 1), sat=1.25, val=1.0, rough_k=1.0, normal=1.0):
    p = lambda k: os.path.join(TEX, f'{tid}_{k}.jpg')
    if not TEX or not os.path.exists(p('diff')): return None
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links; bs = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale); L.new(tc.outputs['Object'], mp.inputs['Vector'])
    oi = N.new('ShaderNodeObjectInfo'); off = N.new('ShaderNodeVectorMath'); off.operation = 'MULTIPLY_ADD'; L.new(oi.outputs['Random'], off.inputs[0]); off.inputs[1].default_value = (7.3, 3.1, 0); L.new(mp.outputs['Vector'], off.inputs[2])
    def img(k, color):
        t = N.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(p(k), check_existing=True); t.projection = 'BOX'; t.projection_blend = .25
        if not color: t.image.colorspace_settings.name = 'Non-Color'
        L.new(off.outputs['Vector'], t.inputs['Vector']); return t
    d = img('diff', True); hs = N.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = sat; hs.inputs['Value'].default_value = val; L.new(d.outputs['Color'], hs.inputs['Color'])
    mu = N.new('ShaderNodeMixRGB'); mu.blend_type = 'MULTIPLY'; mu.inputs['Fac'].default_value = 1; L.new(hs.outputs['Color'], mu.inputs[1]); mu.inputs[2].default_value = (*tint, 1)
    sz = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sz.inputs[0])
    mr = N.new('ShaderNodeMapRange'); L.new(sz.outputs[2], mr.inputs['Value']); mr.inputs['From Min'].default_value = 0; mr.inputs['From Max'].default_value = .32; mr.inputs['To Min'].default_value = .5; mr.inputs['To Max'].default_value = 1
    gn = N.new('ShaderNodeTexNoise'); gn.inputs['Scale'].default_value = 9; L.new(tc.outputs['Object'], gn.inputs['Vector'])
    gm = N.new('ShaderNodeMath'); gm.operation = 'MULTIPLY_ADD'; L.new(gn.outputs['Fac'], gm.inputs[0]); gm.inputs[1].default_value = .25; L.new(mr.outputs[0], gm.inputs[2])
    gc = N.new('ShaderNodeMath'); gc.operation = 'MINIMUM'; L.new(gm.outputs[0], gc.inputs[0]); gc.inputs[1].default_value = 1
    dm = N.new('ShaderNodeMixRGB'); dm.blend_type = 'MULTIPLY'; dm.inputs['Fac'].default_value = 1; L.new(mu.outputs[0], dm.inputs[1])
    cc = N.new('ShaderNodeCombineColor'); [L.new(gc.outputs[0], cc.inputs[i]) for i in range(3)]; L.new(cc.outputs[0], dm.inputs[2])
    L.new(dm.outputs[0], bs.inputs['Base Color'])
    if os.path.exists(p('rough')):
        r = img('rough', False); rm = N.new('ShaderNodeMath'); rm.operation = 'MULTIPLY'; rm.inputs[1].default_value = rough_k; L.new(r.outputs['Color'], rm.inputs[0]); L.new(rm.outputs[0], bs.inputs['Roughness'])
    if os.path.exists(p('nor')):
        n = img('nor', False); nm = N.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = normal; L.new(n.outputs['Color'], nm.inputs['Color']); L.new(nm.outputs['Normal'], bs.inputs['Normal'])
    return m
def mats():
    M = dict(
        vao=node_mat('vao', (.012, .01, .008), bump=0, var=0, rough=1),
        wood=node_mat('wood', (.2, .09, .03), noise=14, var=.3),
        wood_lt=node_mat('wood_lt', (.3, .15, .05), noise=14, var=.25),
        plank=node_mat('plank', (.27, .12, .04), noise=22, var=.3, brick=(9, .01, .9, .12)),
        stone=node_mat('stone', (.5, .33, .15), noise=6, var=.22, brick=(5, .03, .6, .22), bump=.6),
        stone_dk=node_mat('stone_dk', (.33, .21, .1), noise=6, var=.2, brick=(6, .03, .5, .2), bump=.6),
        thatch=node_mat('thatch', (.5, .26, .06), noise=40, var=.35, bump=.8),
        shingle=node_mat('shingle', (.24, .05, .02), noise=10, var=.2, brick=(16, .02, .5, .25), bump=.5),
        slate=node_mat('slate', (.12, .1, .085), noise=10, var=.2, brick=(18, .02, .5, .25), bump=.5),
        iron=node_mat('iron', (.16, .15, .14), rough=.45, metal=.7, bump=.1, var=.1),
        gold=node_mat('gold', (.75, .55, .2), rough=.35, metal=.9, bump=0, var=.05),
        banner=node_mat('banner', (.02, .1, .58), rough=.9, bump=.05, var=.08),  # azul da equipa (recolorido no jogo)
        cloth=node_mat('cloth', (.75, .68, .5), rough=.9, bump=.05, var=.08),
        dirt=node_mat('dirt', (.3, .17, .07), noise=20, var=.25, bump=.2),
        fire=node_mat('fire', (1, .5, .15), emit=(1, .45, .1), bump=0, var=0))
    real = dict(  # texturas reais Poly Haven (CC0); cores puxadas para o estilo pintado do jogo
        wood=tex_mat('t_wood', 'bark_brown_02', 3.2, tint=(1, .78, .55), sat=1.5, val=1.2),
        wood_lt=tex_mat('t_wood_lt', 'brown_planks_05', 1.6, tint=(1, .85, .65), sat=1.2, val=1.1),
        plank=tex_mat('t_plank', 'weathered_brown_planks', 1.6, tint=(1, .76, .52), sat=1.55, val=1.12),
        stone=tex_mat('t_stone', 'large_sandstone_blocks_01', 1.1, tint=(1.05, .86, .62), sat=1.45, val=1.18, normal=1.4),
        stone_dk=tex_mat('t_stone_dk', 'medieval_blocks_02', 1.4, tint=(.95, .8, .62), sat=1.2, val=.95, normal=1.4),
        thatch=tex_mat('t_thatch', 'thatch_roof_angled', 1.6, tint=(1.15, .86, .42), sat=1.8, val=1.45),
        shingle=tex_mat('t_shingle', 'clay_roof_tiles_02', 2.4, tint=(1, .8, .7), sat=1.15, val=.95),
        slate=tex_mat('t_slate', 'roof_slates_02', 2.4, tint=(.75, .7, .66), sat=.3, val=.9))
    for k, v in real.items():
        if v: M[k] = v
    return M

# ---------- primitivas (em coordenadas do jogo: x, y, z) ----------
G = []  # objetos do portão (para rodar em bloco)
def link(o): SCN().collection.objects.link(o); G.append(o); return o
def mesh_obj(name, bm, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); me.materials.append(mat)
    for p in me.polygons: p.use_smooth = False
    return link(o)
def box(x0, x1, y0, y1, z0, z1, mat, name='box'):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), -((y0 + y1) / 2 + v.co.y * (y1 - y0)), (z0 + z1) / 2 + v.co.z * (z1 - z0)))
    return mesh_obj(name, bm, mat)
def cyl(x, y, z0, z1, r, mat, tip=0, seg=10, name='log'):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
    for v in bm.verts: v.co += Vector((x, -y, (z0 + z1) / 2))
    o = mesh_obj(name, bm, mat)
    for p in o.data.polygons: p.use_smooth = True
    if tip:
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=0, depth=tip)
        for v in bm.verts: v.co += Vector((x, -y, z1 + tip / 2))
        mesh_obj(name + 'tip', bm, mat)
    return o
def hlog(x0, x1, y, z, r, mat, axis='x'):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r, radius2=r, depth=abs(x1 - x0))
    rot = Matrix.Rotation(R(90), 4, 'Y' if axis == 'x' else 'X'); bmesh.ops.transform(bm, matrix=rot, verts=bm.verts)
    c = Vector(((x0 + x1) / 2, -y, z)) if axis == 'x' else Vector((x, -(x0 + x1) / 2, z))
    for v in bm.verts: v.co += c
    o = mesh_obj('hlog', bm, mat)
    for p in o.data.polygons: p.use_smooth = True
    return o
def pyramid(x0, x1, y0, y1, z0, h, mat, over=.05, name='roof'):  # telhado de 4 águas
    bm = bmesh.new(); a = [bm.verts.new((x, -y, z0)) for x, y in ((x0 - over, y0 - over), (x1 + over, y0 - over), (x1 + over, y1 + over), (x0 - over, y1 + over))]
    t = bm.verts.new(((x0 + x1) / 2, -(y0 + y1) / 2, z0 + h))
    for i in range(4): bm.faces.new((a[i], a[(i + 1) % 4], t))
    bm.faces.new(a[::-1]); return mesh_obj(name, bm, mat)
def gable(x0, x1, y0, y1, z0, h, mat, over=.05):  # telhado de duas águas com cumeeira ao longo de x
    bm = bmesh.new(); ym = (y0 + y1) / 2
    p = [bm.verts.new(v) for v in ((x0 - over, -(y0 - over), z0), (x1 + over, -(y0 - over), z0), (x1 + over, -ym, z0 + h), (x0 - over, -ym, z0 + h),
                                    (x0 - over, -(y1 + over), z0), (x1 + over, -(y1 + over), z0))]
    bm.faces.new((p[0], p[1], p[2], p[3])); bm.faces.new((p[3], p[2], p[5], p[4])); bm.faces.new((p[0], p[3], p[4])); bm.faces.new((p[1], p[5], p[2]))
    return mesh_obj('gable', bm, mat)
def cone(x, y, z0, h, r, mat, seg=12):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=0, depth=h)
    for v in bm.verts: v.co += Vector((x, -y, z0 + h / 2))
    o = mesh_obj('cone', bm, mat)
    for p in o.data.polygons: p.use_smooth = True
    return o
def banner(x, y, z_top, w, h, mat, face='y', wave=.02):  # estandarte pendurado, com cauda em V
    bm = bmesh.new(); nx, nz = 6, 8; vs = {}
    for i in range(nx + 1):
        for j in range(nz + 1):
            u = i / nx - .5; t = j / nz; zz = z_top - t * h
            if j == nz: zz += abs(u) * h * .35 - h * .12  # recorte em V
            d = wave * math.sin(u * 6 + t * 3)
            co = (x + u * w, -(y + .001 + d), zz) if face == 'y' else (x + .001 + d, -(y + u * w), zz)
            vs[i, j] = bm.verts.new(co)
    for i in range(nx):
        for j in range(nz): bm.faces.new((vs[i, j], vs[i + 1, j], vs[i + 1, j + 1], vs[i, j + 1]))
    o = mesh_obj('banner', bm, mat); s = o.modifiers.new('s', 'SOLIDIFY'); s.thickness = .008; return o
def flag(x, y, z0, h, mat, M):  # mastro com bandeira
    cyl(x, y, z0, z0 + h, .012, M['wood'], seg=6)
    bm = bmesh.new(); vs = {}
    for i in range(5):
        for j in range(3):
            u = i / 4; vs[i, j] = bm.verts.new((x + u * .2, -(y + .02 * math.sin(u * 5)), z0 + h - .02 - j * .06 - u * .01))
    for i in range(4):
        for j in range(2): bm.faces.new((vs[i, j], vs[i + 1, j], vs[i + 1, j + 1], vs[i, j + 1]))
    o = mesh_obj('flag', bm, M['banner']); o.modifiers.new('s', 'SOLIDIFY').thickness = .006
def merlons(x0, x1, y0, y1, z, mat, n, size=.07, h=.08, sides='all'):
    for k in range(n):
        t = (k + .5) / n
        if sides in ('all', 'front'):
            xx = x0 + (x1 - x0) * t; box(xx - size / 2, xx + size / 2, y1 - .05, y1, z, z + h, mat, 'merlon'); box(xx - size / 2, xx + size / 2, y0, y0 + .05, z, z + h, mat, 'merlon')
        if sides == 'all':
            yy = y0 + (y1 - y0) * t; box(x0, x0 + .05, yy - size / 2, yy + size / 2, z, z + h, mat, 'merlon'); box(x1 - .05, x1, yy - size / 2, yy + size / 2, z, z + h, mat, 'merlon')
def arch_cut(o, x0, x1, z_spring, y0, y1, only_round=False):  # recorta uma porta em arco num bloco (boolean)
    w = x1 - x0; cut = box(x0, x1, y0 - .1, y1 + .1, -.05, z_spring, o.data.materials[0], 'cut')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=w / 2, radius2=w / 2, depth=(y1 - y0) + .2)
    bmesh.ops.transform(bm, matrix=Matrix.Rotation(R(90), 4, 'X'), verts=bm.verts)
    for v in bm.verts: v.co += Vector(((x0 + x1) / 2, -(y0 + y1) / 2, z_spring))
    me = bpy.data.meshes.new('c2'); bm.to_mesh(me); bm.free(); c2 = bpy.data.objects.new('c2', me); SCN().collection.objects.link(c2)
    for c in ((c2,) if only_round else (cut, c2)):
        b = o.modifiers.new('b', 'BOOLEAN'); b.operation = 'DIFFERENCE'; b.object = c; c.hide_render = True
    dg = SCN().view_layers[0].depsgraph; dg.update()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); old = o.data; o.modifiers.clear(); o.data = me; bpy.data.meshes.remove(old)
    G.remove(cut); bpy.data.objects.remove(cut, do_unlink=True); bpy.data.objects.remove(c2, do_unlink=True)

# ---------- portas (folhas com dobradiças nas pontas da abertura; abrem para trás, −y) ----------
def doors(x0, x1, y, h, M, iron=False, arch=False, open_=0):
    w = (x1 - x0) / 2; ang = R(118) * open_  # bem aberto (118°), as folhas encostam às torres
    for side in (0, 1):
        pivot = Vector((x0 if side == 0 else x1, -y, 0))
        parts = []
        nb = 4
        for k in range(nb):  # tábuas verticais
            a = k * w / nb; b = (k + 1) * w / nb - .004
            xa, xb = (x0 + a, x0 + b) if side == 0 else (x1 - b, x1 - a)
            hh = h if not arch else h + (w * .55) * math.sqrt(max(0, 1 - ((((xa + xb) / 2) - (x0 + x1) / 2) / (w * 1.02)) ** 2)) - w * .1
            parts.append(box(xa, xb, y - .02, y + .02, 0, hh, M['plank'], 'door'))
        for zz in (.18 * h, .82 * h):  # travessas
            xa, xb = (x0, x0 + w) if side == 0 else (x1 - w, x1)
            parts.append(box(xa + .01, xb - .01, y + .02, y + .035, zz - .035, zz + .035, M['iron'] if iron else M['wood'], 'trav'))
        if not iron:  # travessa diagonal
            xa, xb = (x0, x0 + w) if side == 0 else (x1 - w, x1)
            d = box(xa + .02, xb - .02, y + .02, y + .033, .45 * h - .03, .45 * h + .03, M['wood'], 'diag')
            d.rotation_euler = (0, R(-38 if side == 0 else 38), 0); d.location = Vector(((xa + xb) / 2, -(y + .026), .45 * h)) - Vector(((xa + xb) / 2, -(y + .026), .45 * h)); parts.append(d)
            # (a rotação faz-se no centro da peça: origem no centro do cubo)
        else:
            for zz in (.18 * h, .5 * h, .82 * h):
                for k in range(3):
                    xx = (x0 + .03 + k * w / 3) if side == 0 else (x1 - .03 - k * w / 3)
                    parts.append(cyl(xx, y + .04, zz - .012, zz + .012, .012, M['iron'], seg=6))
        for p in parts:  # roda em torno da dobradiça
            mw = Matrix.Translation(pivot) @ Matrix.Rotation(ang if side == 0 else -ang, 4, 'Z') @ Matrix.Translation(-pivot)
            p.matrix_world = mw @ p.matrix_world

def set_origins_center():
    for o in G:
        if o.type == 'MESH' and o.name.startswith('diag'):
            pass

# ---------- variantes ----------
def path(M, y0=.2, y1=.8):  # chão de terra batida sob a passagem
    bm = bmesh.new(); n = 16
    vs = []
    for k in range(n):
        a = 2 * math.pi * k / n; vs.append(bm.verts.new((.5 + .3 * math.cos(a), -(.5 + .22 * math.sin(a)), .004)))
    bm.faces.new(vs); mesh_obj('path', bm, M['dirt'])

def madeira(age, M, open_):  # casa do portão de madeira (estilo Stronghold): bloco largo, arco/porta ao meio, parapeito com ameias de tábuas
    Hb = (1.35, 1.65, 1.8)[age]; dz = .82; x0, x1, y0, y1 = -.28, 1.28, .06, .94
    path(M)
    if age == 0:  # paredes de troncos aguçados à volta de um núcleo de tábuas
        box(x0 + .05, .25, y0 + .05, y1 - .05, 0, Hb - .15, M['plank'], 'torre'); box(.75, x1 - .05, y0 + .05, y1 - .05, 0, Hb - .15, M['plank'], 'torre')
        for (a, b) in ((x0, .25), (.75, x1)):
            n = 5
            for k in range(n):
                t = a + (k + .5) * (b - a) / n
                for yy in (y0, y1): cyl(t, yy, 0, Hb + (.06 if k % 2 else 0), .055, M['wood'], tip=.13, seg=8)
            for yy in (y0 + .2, y0 + .45, y0 + .7):
                for xx in (a, b): cyl(xx, yy, 0, Hb + (.04 if int(yy * 10) % 2 else 0), .055, M['wood'], tip=.13, seg=8)
        box(.22, .78, y0 + .05, y1 - .05, dz, dz + .1, M['wood'], 'verga')
        for k in range(7):
            t = .27 + k * .46 / 6
            for yy in (y0 + .02, y1 - .02): cyl(t, yy, dz + .1, Hb + (.05 if k % 2 else 0), .045, M['wood'], tip=.11, seg=8)
        box(x0 + .05, .25, y0 + .05, y1 - .05, Hb - .12, Hb - .07, M['plank'], 'adarve'); box(.75, x1 - .05, y0 + .05, y1 - .05, Hb - .12, Hb - .07, M['plank'], 'adarve'); box(.25, .75, y0 + .05, y1 - .05, Hb - .12, Hb - .07, M['plank'], 'adarve')
    else:  # base de pedra cinzenta + andar de madeira com parapeito e ameias de tábuas
        Hs = .55
        for (a, b) in ((x0, .25), (.75, x1)):
            box(a - .03, b + .03, y0 - .03, y1 + .03, 0, .14, M['stone_dk'], 'sapata'); box(a, b, y0, y1, .14, Hs, M['stone'], 'torre')
        box(x0 - .02, x1 + .02, y0 - .02, y1 + .02, Hs, Hs + .05, M['wood'], 'viga')
        box(x0, .25, y0, y1, Hs + .05, Hb, M['plank'], 'torre'); box(.75, x1, y0, y1, Hs + .05, Hb, M['plank'], 'torre')
        top = box(.25, .75, y0, y1, dz, Hb, M['plank'], 'meio')
        for a in (x0, .25, .75, x1):
            for b in (y0, y1): box(a - .03, a + .03, b - .03, b + .03, Hs, Hb + .02, M['wood'], 'canto')
        for k in range(8):  # ameias de tábuas
            t = x0 + (k + .5) * (x1 - x0) / 8
            for b in (y0, y1): box(t - .06, t + .06, b - .02, b + .02, Hb, Hb + .14, M['plank'], 'merlon')
        for xc in (0.0, 1.0): box(xc - .05, xc + .05, y1 - .005, y1 + .005, Hs + .25, Hs + .45, M['vao'], 'seteira')
        if age == 2:  # telhado de duas águas sobre a passagem e lanternas
            gable(.2, .8, y0 - .02, y1 + .02, Hb + .02, .25, M['shingle'], over=.05)
            for x in (.2, .8): cyl(x, y1 + .08, .55, .61, .025, M['fire']); cyl(x, y1 + .06, .45, .55, .012, M['iron'], seg=6)
    doors(.25, .75, .5, dz, M, iron=age == 2, open_=open_)
    banner(.5, y1 + .02, dz + (.0 if age == 0 else .3), .2, .3, M['banner'])
    flag(x1 - .12, y0 + .12, Hb + .14, .32, M['banner'], M)

def pedra(age, M, open_):  # casa do portão (estilo Stronghold): um bloco largo de pedra cinzenta, arco no meio, ameias e terraço
    Hb = (0, 1.8, 2.0)[age]; dz = .82; x0, x1, y0, y1 = -.28, 1.28, .04, .96
    path(M)
    box(x0 - .03, x1 + .03, y0 - .03, y1 + .03, 0, .14, M['stone_dk'], 'sapata')
    for a, b in ((x0, .25), (.75, x1)): box(a, b, y0, y1, .14, Hb, M['stone'], 'torre')
    top = box(.25, .75, y0, y1, dz, Hb, M['stone'], 'meio'); arch_cut(top, .25, .75, dz, y0, y1, only_round=True)
    box(x0 - .03, x1 + .03, y0 - .03, y1 + .03, Hb, Hb + .05, M['stone_dk'], 'cornija')
    merlons(x0 - .03, x1 + .03, y0 - .03, y1 + .03, Hb + .05, M['stone'], 7, size=.1, h=.15)
    for k in range(9):  # aduelas
        a = math.pi * k / 8; x = .5 + .25 * math.cos(a); z = dz + .25 * math.sin(a)
        box(x - .035, x + .035, y1 - .005, y1 + .015, z - .035, z + .035, M['stone_dk'], 'aduela')
    for xc in (-.02, 1.02):
        for zz in (.5, .95): box(xc - .015, xc + .015, y1 - .005, y1 + .005, zz, zz + .22, M['vao'], 'seteira')
    if age == 2:  # mata-cães sobre o arco e grade levadiça
        for k in range(6):
            t = .2 + k * .12; box(t - .03, t + .03, y1, y1 + .06, Hb - .14, Hb - .03, M['stone_dk'], 'corbel')
        for k in range(6):
            x = .3 + k * .4 / 5; cyl(x, y1 - .1, dz - .05, dz + .2, .01, M['iron'], seg=6)
    doors(.25, .75, .5, dz, M, iron=True, arch=True, open_=open_)
    flag(x1 - .12, y0 + .12, Hb + .2, .35, M['banner'], M)
    banner(.5, y1 + .02, Hb - .05, .22, .32, M['banner'])

def tons(M):  # mesma pedra/madeira (menos saturadas) das muralhas
    tm = tex_mat
    M['stone'] = tm('t_stone_m', 'large_sandstone_blocks_01', 1.3, tint=(.93, .92, .89), sat=.14, val=1.04, normal=1.8) or M['stone']
    M['stone_dk'] = tm('t_stone_dk_m', 'medieval_blocks_02', 1.6, tint=(.86, .86, .84), sat=.1, val=.78, normal=1.8) or M['stone_dk']
    M['wood'] = tm('t_wood_m', 'bark_brown_02', 3.2, tint=(.92, .8, .66), sat=1.0, val=1.0) or M['wood']

# ---------- cena: câmara isométrica e luz ----------
def scene():
    sc = SCN(); sc.render.engine = 'CYCLES'; sc.cycles.device = 'GPU' if os.environ.get('GPU') else 'CPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
    sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = RES; sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    if not sc.world: sc.world = bpy.data.worlds.new('w')
    sc.world.use_nodes = True; bg = sc.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.95, .9, .82, 1); bg.inputs[1].default_value = .4
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); cam.data.type = 'ORTHO'; cam.data.sensor_fit = 'HORIZONTAL'; cam.data.ortho_scale = RES[0] / PXU  # 'AUTO' aplicava a escala à altura (maior): tudo saía 5-11% maior que as casas
    sc.collection.objects.link(cam); sc.camera = cam
    c = Vector((.5, -.5, 0)); d = Vector((1, -1, 0)).normalized() * math.cos(R(30)) + Vector((0, 0, math.sin(R(30))))
    cam.rotation_euler = (R(60), 0, R(45)); cam.location = c + d * 20
    # a vista sobe um pouco: o portão é alto (centro de enquadramento a 0,75 de altura)
    up = cam.matrix_world.to_3x3() @ Vector((0, 1, 0)); cam.location += up * 0.0
    cam.data.shift_y = .18
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 4.2; sun.data.angle = R(4); sun.data.color = (1, .95, .85)
    sun.rotation_euler = Vector((0, 0, -1)).rotation_difference(-Vector((-.5, -1, 2.1)).normalized()).to_euler(); sc.collection.objects.link(sun)
    # apanha-sombras no chão (sombra neutra e semitransparente)
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=2.5)
    for v in bm.verts: v.co += Vector((.5, -.5, 0))
    me = bpy.data.meshes.new('g'); bm.to_mesh(me); bm.free(); g = bpy.data.objects.new('g', me); chao = bpy.data.collections.new('chao'); sc.collection.children.link(chao); chao.objects.link(g); g.is_shadow_catcher = True
    # contorno escuro fino (estilo pintado dos edifícios do jogo)
    sc.render.use_freestyle = True; sc.render.line_thickness_mode = 'ABSOLUTE'; sc.render.line_thickness = 1.1
    ls = sc.view_layers[0].freestyle_settings.linesets[0] if sc.view_layers[0].freestyle_settings.linesets else sc.view_layers[0].freestyle_settings.linesets.new('l')
    ls.linestyle.color = (.09, .05, .025); ls.linestyle.alpha = .75; ls.select_by_visibility = True; ls.select_by_collection = True; ls.collection = bpy.data.collections['chao']; ls.collection_negation = 'EXCLUSIVE'; ls.select_crease = False; ls.select_border = True; ls.select_silhouette = True
    sc.view_layers[0].freestyle_settings.crease_angle = R(120)
    return cam

def finish(objs):
    for o in objs:
        if o.type != 'MESH': continue
        n = o.name.split('.')[0]
        if n in ('banner', 'flag', 'path'): continue
        if n in ('roof', 'gable', 'cone'):
            sm = o.modifiers.new('esp', 'SOLIDIFY'); sm.thickness = .022; sm.offset = 1
            continue
        if n in ('log', 'logtip', 'hlog'): continue
        b = o.modifiers.new('bisel', 'BEVEL'); b.width = .009 if n not in ('merlon', 'aduela', 'corbel') else .006; b.segments = 2; b.limit_method = 'ANGLE'
def build(var, M, dirn, open_):
    global G
    for o in G: bpy.data.objects.remove(o, do_unlink=True)
    G = []
    kind, age = var[:-1], int(var[-1])
    (madeira if kind == 'madeira' else pedra)(age, M, open_)
    finish(G)
    if dirn == 'y':  # roda 90° em torno do centro da casa: a frente (+y do jogo) passa a olhar para +x
        rot = Matrix.Translation((.5, -.5, 0)) @ Matrix.Rotation(R(90), 4, 'Z') @ Matrix.Translation((-.5, .5, 0))
        for o in G: o.matrix_world = rot @ o.matrix_world

reset(); M = mats(); tons(M); cam = scene()
info = {}
sc = SCN()
for var in VARS:
    for dirn in ('x', 'y'):
        for k, op in enumerate((0, .5, 1)):
            build(var, M, dirn, op)
            name = f'{var}_{dirn}_{k}'; sc.render.filepath = f'{OUT}/{name}.png'
            with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]): bpy.ops.render.render(write_still=True)
            a = world_to_camera_view(sc, cam, Vector((0, 0, 0)))  # canto de cima da casa (tx,ty) no ecrã
            info[name] = [a.x * RES[0], (1 - a.y) * RES[1]]
            print('REN', name, flush=True)
af = f'{OUT}/anchors.json'; old = json.load(open(af))['anchor'] if os.path.exists(af) else {}
old.update(info); json.dump({'pxPerUnit': PXU, 'res': RES, 'anchor': old}, open(af, 'w'), indent=1)
print('FEITO')
