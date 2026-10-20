import bpy, os, math
D='/tmp/claude-0/meshy-site';name=os.environ['MN']
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=f'{D}/{name}.glb')
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');print('ACTIONS',[a.name for a in bpy.data.actions])
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=6;sc.render.film_transparent=True;sc.render.resolution_x=420;sc.render.resolution_y=320
if not sc.world: sc.world=bpy.data.worlds.new('w')
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[1].default_value=1.5
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam'));cam.data.type='ORTHO';cam.data.ortho_scale=float(os.environ.get('OS','6'));sc.collection.objects.link(cam);sc.camera=cam
cam.location=(0,-20,1.4);cam.rotation_euler=(math.radians(90),0,0)
ad=arm.animation_data
for t in list(ad.nla_tracks): t.mute=True
for an in ['Attack','Walk','Death']:
    a=next(x for x in bpy.data.actions if x.name.split('|')[-1]==an or x.name.startswith(an));ad.action=a
    for t in list(ad.nla_tracks): ad.nla_tracks.remove(t)
    f0,f1=a.frame_range
    for k in range(4):
        sc.frame_set(int(f0+(f1-f0)*k/4));sc.render.filepath=f'{D}/ck_{name}_{an}_{k}.png';bpy.ops.render.render(write_still=True)
