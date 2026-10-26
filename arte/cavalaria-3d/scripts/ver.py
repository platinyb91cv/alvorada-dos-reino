import bpy, os, math
F = os.environ['F']; D = os.environ['D']; CL = os.environ.get('CL', 'Idle,Walk,Attack,Hit,Death').split(',')
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=F)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE' if False else 'CYCLES'; sc.cycles.samples = 8; sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = 360, 300
if not sc.world: sc.world = bpy.data.worlds.new('w')
sc.world.use_nodes = True; sc.world.node_tree.nodes['Background'].inputs[1].default_value = 1.6
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); cam.data.type = 'ORTHO'; cam.data.ortho_scale = float(os.environ.get('OS', '13'))
sc.collection.objects.link(cam); sc.camera = cam
v = os.environ.get('VIEW', 'side')
if v == 'side': cam.location = (30, -.5, 4.6); cam.rotation_euler = (math.radians(90), 0, math.radians(90))
else: cam.location = (22, -22, 21); cam.rotation_euler = (math.radians(60), 0, math.radians(45))
ad = arm.animation_data
for t in list(ad.nla_tracks): t.mute = True
for an in CL:
    a = next(x for x in bpy.data.actions if x.name.split('|')[-1].startswith(an)); ad.action = a
    try: ad.action_slot = a.slots[0]
    except Exception: pass
    f0, f1 = a.frame_range
    for k in range(4):
        sc.frame_set(int(f0 + (f1 - f0) * k / 3)); sc.render.filepath = f'{D}/v_{an}_{k}.png'; bpy.ops.render.render(write_still=True)
