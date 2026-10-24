# Navios 3D (0 créditos), modelados por código no Blender: casco só acima da linha de água (flutuam no jogo),
# velas às riscas azuis e friso azul (cor da equipa), remos animados nas galés. Frente = +X. Escala "de jogo"
# (comprimentos de 1,5 a 3,4 m, como os desenhos antigos). Clips: Idle, Walk (navegar), Attack, Hit, Death (afunda).
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
R = math.radians
def flat(name, col, rough=.8, metal=0, emit=None):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = 4
    return m
def mats():
    return dict(casco=flat('casco', (.2, .1, .045)), casco_esc=flat('casco_esc', (.09, .07, .06)), deck=flat('convés', (.42, .26, .12)), madeira=flat('madeira', (.27, .14, .06)),
                vela=flat('vela', (.85, .8, .68), .9), azul=flat('azul', (.02, .1, .58), .85), bronze=flat('bronze', (.55, .35, .12), .35, .9),
                ferro=flat('ferro', (.13, .13, .14), .45, .8), rede=flat('rede', (.3, .27, .2), .95), fogo=flat('fogo', (1, .45, .1), .5, 0, (1, .4, .05)),
                corda=flat('corda', (.55, .42, .25), .9), barril=flat('barril', (.33, .18, .07)), escudo=flat('escudo_azul', (.04, .14, .62), .6))
PARTS = []
def obj(bm, mat, bone, name='p', smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me)
    if isinstance(mat, list):
        for m in mat: me.materials.append(m)
    else: me.materials.append(mat)
    for p in me.polygons: p.use_smooth = smooth
    bpy.context.scene.collection.objects.link(o); o['bone'] = bone; PARTS.append(o); return o
def box(c, s, mat, bone='raiz', rot=None, name='b'):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ (rot.to_4x4() if rot else Matrix()) @ Matrix.Diagonal((*s, 1)), verts=bm.verts); return obj(bm, mat, bone, name)
def cyl(c, r, h, mat, bone='raiz', axis='Z', seg=10, r2=None, name='c'):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    rot = {'Z': Matrix(), 'X': Matrix.Rotation(R(90), 4, 'Y'), 'Y': Matrix.Rotation(R(90), 4, 'X')}[axis]
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ rot, verts=bm.verts); return obj(bm, mat, bone, name, smooth=True)
def hull(L, B, F, M, sheer=.35, bow=.42, stern=.25, stripe=True):
    """Casco acima da água: secções de popa (x=-L/2) a proa (x=+L/2); costado com leve abertura; convés; friso azul."""
    N = 22; secs = []
    for i in range(N + 1):
        s = i / N; x = -L / 2 + L * s
        if s > 1 - bow: w = B / 2 * (1 - ((s - (1 - bow)) / bow) ** 1.7)
        elif s < stern: w = B / 2 * (.55 + .45 * (s / stern) ** .6)
        else: w = B / 2
        w = max(w, .015); top = F + sheer * F * ((2 * s - 1) ** 2) * (1.3 if s > .5 else 1)
        secs.append((x, w, top))
    bm = bmesh.new(); rows = []
    for x, w, top in secs:  # bombordo(+y) e estibordo(-y): base (água), meio, borda
        rows.append([bm.verts.new((x, -w * .82, 0)), bm.verts.new((x, -w, top * .6)), bm.verts.new((x, -w * 1.02, top)),
                     bm.verts.new((x, w * 1.02, top)), bm.verts.new((x, w, top * .6)), bm.verts.new((x, w * .82, 0))])
    for i in range(N):
        a, b = rows[i], rows[i + 1]
        for k in range(5):
            if k == 2: continue  # o convés é outra malha
            bm.faces.new((a[k], b[k], b[k + 1], a[k + 1]))
        bm.faces.new((a[5], b[5], b[0], a[0]))  # fundo (fica na água)
    bm.faces.new(rows[0][::-1]); bm.faces.new(rows[-1])
    obj(bm, M['casco'], 'raiz', 'casco')
    # convés ligeiramente abaixo da borda
    bm = bmesh.new(); prev = None
    for x, w, top in secs:
        cur = (bm.verts.new((x, -w * .96, top - .04 * F)), bm.verts.new((x, w * .96, top - .04 * F)))
        if prev: bm.faces.new((prev[0], cur[0], cur[1], prev[1]))
        prev = cur
    obj(bm, M['deck'], 'raiz', 'conves')
    if stripe:  # friso azul (cor da equipa) ao longo da borda
        for side in (-1, 1):
            bm = bmesh.new(); prev = None
            for x, w, top in secs:
                cur = (bm.verts.new((x, side * w * 1.035, top * .78)), bm.verts.new((x, side * w * 1.045, top * .93)))
                if prev: bm.faces.new((prev[0], cur[0], cur[1], prev[1]) if side > 0 else (prev[1], cur[1], cur[0], prev[0]))
                prev = cur
            obj(bm, M['azul'], 'raiz', 'friso')
    return secs
def topat(secs, x):
    best = min(secs, key=lambda t: abs(t[0] - x)); return best[2], best[1]
def mast(x, h, z0, M, r=.035):
    cyl((x, 0, z0 + h / 2), r, h, M['madeira'], seg=8); return z0 + h
def square_sail(x, zb, zt, w, M, bone='raiz', stripes=3):
    """Vela redonda com riscas verticais azuis (alternadas com pano cru), ligeiramente cheia de vento para a frente."""
    nx, nz = 8, 6; bm = bmesh.new(); vs = {}
    for i in range(nx + 1):
        for j in range(nz + 1):
            u, v = i / nx, j / nz; y = -w / 2 + w * u; z = zb + (zt - zb) * v; bulge = .18 * w * math.sin(math.pi * u) * math.sin(math.pi * v)
            vs[i, j] = bm.verts.new((x + .04 + bulge, y, z))
    fi = []
    for i in range(nx):
        for j in range(nz): f = bm.faces.new((vs[i, j], vs[i + 1, j], vs[i + 1, j + 1], vs[i, j + 1])); fi.append((f, 1 if (i * stripes // nx) % 2 else 0))
    for f, mi in fi: f.material_index = mi
    o = obj(bm, [M['vela'], M['azul']], bone, 'vela', smooth=True); o.modifiers.new('s', 'SOLIDIFY').thickness = .012
    cyl((x + .02, 0, zt + .01), .022, w * 1.08, M['madeira'], 'raiz', axis='Y', seg=6)  # verga
    return o
def lateen_sail(x, z0, h, L, M, bone='raiz'):
    """Vela latina triangular, com uma risca azul."""
    bm = bmesh.new(); a = bm.verts.new((x - L * .55, 0, z0 + h * .15)); b = bm.verts.new((x + L * .45, 0, z0 + h)); c = bm.verts.new((x + .02, 0, z0))
    m1 = bm.verts.new(((a.co.x + b.co.x) / 2, .06, (a.co.z + b.co.z) / 2)); m2 = bm.verts.new(((a.co.x + c.co.x) / 2 + .02, .04, (a.co.z + c.co.z) / 2))
    f1 = bm.faces.new((a, m2, m1)); f2 = bm.faces.new((m2, c, b, m1)); f1.material_index = 1; f2.material_index = 0
    pa, pb_ = a.co.copy(), b.co.copy()
    o = obj(bm, [M['vela'], M['azul']], bone, 'latina', smooth=True); o.modifiers.new('s', 'SOLIDIFY').thickness = .012
    # verga inclinada: cilindro ao longo de Z rodado para a direção a→b (transformação aplicada à malha, por causa do skin)
    bm2 = bmesh.new(); bmesh.ops.create_cone(bm2, cap_ends=True, segments=6, radius1=.018, radius2=.018, depth=(pb_ - pa).length)
    ang = math.atan2(pb_.x - pa.x, pb_.z - pa.z); bmesh.ops.transform(bm2, matrix=Matrix.Translation((pa + pb_) / 2) @ Matrix.Rotation(ang, 4, 'Y'), verts=bm2.verts)
    obj(bm2, M['madeira'], 'raiz', 'verga', smooth=True)
    return o
def oars(secs, n, x0, x1, M, F):
    for side, bone in ((-1, 'remosE'), (1, 'remosD')):
        for k in range(n):
            x = x0 + (x1 - x0) * k / max(1, n - 1); top, w = topat(secs, x)
            rot = Matrix.Rotation(R(-32) * side, 3, 'X')
            box((x, side * (w + .22), top * .55), (.025, .5, .025), M['madeira'], bone, rot=rot, name='remo')
def flag(x, z, M, s=.18):
    cyl((x, 0, z + s * .6), .01, s * 1.2, M['madeira'], seg=6); box((x - s * .38, 0, z + s * .95), (s * .7, .01, s * .42), M['azul'], name='bandeira')
def build(kind, M):
    PARTS.clear(); info = {}
    if kind == 'barcoPesca':
        L, B, F = 1.5, .55, .2; secs = hull(L, B, F, M, sheer=.6, bow=.45, stern=.35)
        z = mast(.08, .78, F * .9, M, .022); square_sail(.08, F + .28, z - .04, .42, M, stripes=2)
        box((-.35, .18, F + .06), (.35, .12, .08), M['rede'], name='rede'); box((.35, 0, F + .05), (.18, .2, .08), M['barril'], name='cesto')
        info = dict(oars=0, H=z + .05)
    elif kind == 'transporte':
        L, B, F = 2.4, .95, .34; secs = hull(L, B, F, M, sheer=.45, bow=.35, stern=.3)
        box((-.95, 0, F + .14), (.5, .82, .3), M['casco'], name='castelo'); box((-.95, 0, F + .3), (.54, .86, .04), M['azul'], name='ameia')
        z = mast(.15, 1.45, F, M, .04); square_sail(.15, F + .55, z - .06, .95, M, stripes=4); flag(.15, z, M)
        for dx, dy in ((.55, .2), (.6, -.18), (.85, 0)): box((dx, dy, F + .09), (.16, .16, .16), M['barril'], name='carga')
        info = dict(oars=0, H=z + .25)
    elif kind == 'gale':
        L, B, F = 2.8, .62, .22; secs = hull(L, B, F, M, sheer=.55, bow=.3, stern=.25)
        cyl((L / 2 + .12, 0, .07), .05, .3, M['bronze'], axis='X', r2=.01, seg=8)  # esporão de bronze
        z = mast(.1, 1.15, F, M, .03); lateen_sail(.1, F + .2, 1.05, 1.5, M); flag(-1.2, F + .1, M, .16)
        for k in range(7):  # escudos azuis ao longo da borda
            x = -.9 + 1.8 * k / 6
            for side in (-1, 1): top, w = topat(secs, x); cyl((x, side * (w + .02), top * .93), .07, .02, M['escudo'], axis='Y', seg=10)
        oars(secs, 7, -.9, .95, M, F); info = dict(oars=1, H=z + .1)
    elif kind == 'incendiario':
        L, B, F = 2.0, .58, .22; secs = hull(L, B, F, M, sheer=.5, bow=.35, stern=.3)
        z = mast(-.05, .9, F, M, .025); square_sail(-.05, F + .3, z - .05, .6, M, stripes=2)
        for dx in (.45, .65): box((dx, 0, F + .1), (.16, .16, .2), M['barril'], name='barril')
        cyl((.78, 0, F + .12), .1, .14, M['ferro'], seg=8, name='braseiro'); cyl((.78, 0, F + .24), .09, .16, M['fogo'], r2=.01, seg=8, name='chama')
        oars(secs, 4, -.55, .35, M, F); info = dict(oars=1, H=z + .05)
    elif kind == 'navioPesado':
        L, B, F = 3.3, 1.15, .42; secs = hull(L, B, F, M, sheer=.4, bow=.3, stern=.25)
        box((-1.25, 0, F + .2), (.7, 1.0, .4), M['casco'], name='castelo_popa'); box((1.2, 0, F + .14), (.5, .7, .28), M['casco'], name='castelo_proa')
        for x0, xx in ((-1.25, .7), (1.2, .5)):
            for k in range(5): box((x0 - xx / 2 + xx * (k + .5) / 5, .47 if x0 < 0 else .33, F + (.43 if x0 < 0 else .31)), (.07, .06, .07), M['azul'], name='ameia')
        z1 = mast(.35, 1.9, F, M, .05); square_sail(.35, F + .75, z1 - .08, 1.15, M, stripes=4); flag(.35, z1, M, .22)
        z2 = mast(-.55, 1.5, F, M, .04); square_sail(-.55, F + .65, z2 - .06, .9, M, stripes=4)
        box((.55, 0, F + .12), (.35, .3, .1), M['madeira'], name='balista'); cyl((.62, 0, F + .22), .02, .45, M['madeira'], axis='X', seg=6)
        info = dict(oars=0, H=z1 + .3)
    elif kind == 'corsario':
        L, B, F = 2.5, .72, .3; secs = hull(L, B, F, M, sheer=.5, bow=.38, stern=.28)
        for o in [o for o in PARTS if o.name.startswith('casco')]: o.data.materials[0] = M['casco_esc']
        z1 = mast(.35, 1.45, F, M, .035); lateen_sail(.35, F + .2, 1.3, 1.45, M); flag(.35, z1, M, .2)
        z2 = mast(-.5, 1.1, F, M, .03); lateen_sail(-.5, F + .16, .95, 1.1, M)
        for k in range(3): cyl((-.2 + .3 * k, .3, F + .06), .035, .2, M['ferro'], axis='Y', seg=8, name='canhao')
        info = dict(oars=0, H=z1 + .3)
    return info
def rig_and_animate(kind, info, out):
    arm_d = bpy.data.armatures.new(kind); arm = bpy.data.objects.new(kind, arm_d); bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
    def bone(n, h, par=None):
        b = arm_d.edit_bones.new(n); b.head = Vector(h); b.tail = Vector(h) + Vector((0, .2, 0)); b.roll = 0
        if par: b.parent = arm_d.edit_bones[par]
    bone('raiz', (0, 0, 0))
    if info['oars']:
        bone('remosE', (0, -.3, .15), 'raiz'); bone('remosD', (0, .3, .15), 'raiz')
    bpy.ops.object.mode_set(mode='OBJECT')
    for o in PARTS:
        vg = o.vertex_groups.new(name=o['bone']); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE'); o.parent = arm; md = o.modifiers.new('Armature', 'ARMATURE'); md.object = arm
    PB = arm.pose.bones
    for pb in PB: pb.rotation_mode = 'XYZ'
    def act(name, n, fn):
        a = bpy.data.actions.new(name); arm.animation_data_create(); arm.animation_data.action = a
        for f in range(n + 1):
            t = f / n
            for pb in PB: pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)
            fn(t)
            for pb in PB: pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_euler', frame=f); pb.keyframe_insert('scale', frame=f)
        tr = arm.animation_data.nla_tracks.new(); tr.name = name; tr.strips.new(name, 0, a); arm.animation_data.action = None
    def sway(t, k=1):
        PB['raiz'].rotation_euler = (R(2.2 * k) * math.sin(2 * math.pi * t), R(1.0 * k) * math.sin(2 * math.pi * t + 1.3), 0)
    def row(t):
        if not info['oars']: return
        a = 2 * math.pi * t * 2
        for b, sd in (('remosE', -1), ('remosD', 1)):
            PB[b].rotation_euler = (R(9) * math.sin(a) * sd, 0, 0); PB[b].location = (.06 * math.cos(a), 0, 0)
    act('Idle', 40, lambda t: sway(t))
    act('Walk', 32, lambda t: (sway(t, 1.4), row(t)))
    act('Attack', 24, lambda t: (setattr(PB['raiz'], 'rotation_euler', (R(4) * math.sin(math.pi * min(1, t / .3)) * (1 - t), R(-3) * math.sin(math.pi * min(1, t / .3)) * (1 - t), 0)), row(t * .5)))
    act('Hit', 20, lambda t: setattr(PB['raiz'], 'rotation_euler', (R(5) * math.sin(5 * math.pi * t) * (1 - t), 0, 0)))
    def death(t):  # inclina e afunda: achata para a linha de água (o casco nunca passa abaixo de z=0)
        e = min(1, t / .9) ** 1.6; PB['raiz'].rotation_euler = (R(18) * e, R(-10) * e, 0); PB['raiz'].scale = (1, 1, max(.02, 1 - e))
    act('Death', 48, death)
    bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True)
    for o in PARTS: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True)
    return arm
OUTD = os.environ['NAV_OUT']; os.makedirs(OUTD, exist_ok=True)
for kind in os.environ.get('KINDS', 'barcoPesca,transporte,gale,incendiario,navioPesado,corsario').split(','):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.actions): bpy.data.actions.remove(a)
    M = mats(); info = build(kind, M); rig_and_animate(kind, info, f'{OUTD}/{kind}-rig.glb')
    print('OK', kind, round(info['H'], 2), os.path.getsize(f'{OUTD}/{kind}-rig.glb'), flush=True)
