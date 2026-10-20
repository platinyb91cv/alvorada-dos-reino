
import bpy, os, math, bmesh
from mathutils import Vector, Matrix, Euler
work = r'C:\Users\plati\Documents\alvorada-portoes'
src = open(os.path.join(work, 'montar_portao2.py'), encoding='utf-8').read(); src = src[:src.index('reset(); M = mats()')]
os.environ['TEX_DIR'] = os.path.join(work, 'texturas')
for m in list(bpy.data.materials):
    if m.name.startswith(('t_', 'wood', 'plank', 'stone', 'thatch', 'shingle', 'slate', 'iron', 'gold', 'banner', 'cloth', 'dirt', 'fire', 'vao', 'relva')): bpy.data.materials.remove(m)
g = {'__name__': 'portoes_lib'}; exec(compile(src, 'montar_portao2.py', 'exec'), g)
g['reset'](); sc = bpy.data.scenes['portoes']; M = g['mats']()
sc.render.engine = 'CYCLES'; sc.cycles.device = 'GPU'
sc.world = bpy.data.worlds.new('ceu'); sc.world.use_nodes = True; nt = sc.world.node_tree
env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(work, 'texturas', 'ceu.hdr'), check_existing=True)
nt.links.new(env.outputs['Color'], nt.nodes['Background'].inputs['Color'])
sun = bpy.data.objects.new('sol', bpy.data.lights.new('sol', 'SUN')); sun.data.energy = 3.5; sun.data.angle = math.radians(2); sun.data.color = (1, .93, .82)
sun.rotation_euler = (math.radians(50), math.radians(-25), math.radians(-35)); sc.collection.objects.link(sun)
OPEN = float(os.environ.get('VIT_OPEN', '0'))
nomes = [('madeira', 0, 'Madeira - Idade da Pedra'), ('madeira', 1, 'Madeira - Bronze'), ('madeira', 2, 'Madeira - Ferro'), ('pedra', 1, 'Pedra - Bronze'), ('pedra', 2, 'Pedra - Ferro')]
for i, (fn, age, nome) in enumerate(nomes):
    g['G'].clear(); g[fn](age, M, OPEN); g['finish'](g['G'])
    col = bpy.data.collections.new(nome); sc.collection.children.link(col)
    off = Matrix.Translation((i * 1.8 - 3.6, 0, 0))
    for o in list(g['G']):
        o.matrix_world = off @ o.matrix_world
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=8)
me = bpy.data.meshes.new('relva'); bm.to_mesh(me); bm.free(); pl = bpy.data.objects.new('relva', me); pl.location = (0, -.5, -.002); sc.collection.objects.link(pl)
mt = bpy.data.materials.new('relva'); mt.use_nodes = True; mt.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.08, .16, .04, 1); mt.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .95; me.materials.append(mt)
cam = bpy.data.objects.new('vista', bpy.data.cameras.new('vista')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 34; cam.location = (0, -10.2, 3.6); cam.rotation_euler = (math.radians(74), 0, 0)
sc.render.resolution_x, sc.render.resolution_y = 1500, 640; sc.cycles.samples = 64; sc.cycles.use_denoising = True; sc.render.film_transparent = False; sc.render.use_freestyle = False
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
out = os.path.join(work, os.environ.get('VIT_OUT', 'vitrine.png')); sc.render.filepath = out
with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]): bpy.ops.render.render(write_still=True)
for w in bpy.context.window_manager.windows:
    w.scene = sc
    for a in w.screen.areas:
        if a.type == 'VIEW_3D': a.spaces[0].shading.type = 'MATERIAL'
