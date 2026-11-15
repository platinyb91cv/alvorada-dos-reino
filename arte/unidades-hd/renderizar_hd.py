# Render HD dos soldados armados a partir do GLB (mesma câmara/direções/fases do renderizar.py original)
import bpy,json,math,sys,hashlib,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
args=dict(a.split('=',1) for a in sys.argv[1:] if '=' in a)
name=args['unit'];RES=int(args.get('res',512));SAMPLES=int(args.get('samples',16));OUT=Path(args.get('out','/tmp/claude-0/sp/hd'))/name
only=args.get('only');OUT.mkdir(parents=True,exist_ok=True);(OUT/'frames').mkdir(exist_ok=True)
A=Path('/tmp/claude-0/wt/arte/unidades-armadas');build=json.loads((A/f'{name}.build.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(A/f'{name}.glb'))
S=bpy.context.scene;rig=bpy.data.objects[build['rig']];body=bpy.data.objects[build['body']];default=build['defaultProp']
rig.animation_data.action=None
frames=[];states={}
def seq(state,clip,phases,tool):
  states[state]=[]
  for ph in phases:states[state].append(len(frames));frames.append({'i':len(frames),'state':state,'clip':clip,'phase':ph,'tool':tool})
seq('idle','Idle',[.2,.7],default);seq('walk','Walk',[i/8 for i in range(8)],default);seq('attack','Attack',[0,.15,.3,.5,.7,.9],'hammer' if name=='aldeao' else default);seq('hit','Hit',[.2,.55],default);seq('death','Death',[.1,.35,.65,1],default)
if name=='aldeao':
  C=build['clips']
  for st,clip,tool in [('chop','Chop','axe'),('mine','Mine','pick'),('build','Build' if 'Build' in C else 'Mine','build_hammer' if 'build_hammer' in build['props'] else 'hammer'),('farm','Farm' if 'Farm' in C else 'Harvest','hoe'),('forage','Harvest','basket'),('hunt','Attack','spear'),('butcher','Butcher' if 'Butcher' in C else 'Mine','knife')]:seq(st,clip,[.05,.2,.35,.5,.65,.8],tool)
  seq('carry','Carry',[i/8 for i in range(8)],'cargo')
clipLen={}
for t in rig.animation_data.nla_tracks:
  st=t.strips[0];clipLen[t.name]=(st.frame_start,st.frame_end)
anchor=rig.matrix_world@rig.data.bones['Hips'].head_local;anchor.z=0
pivot=bpy.data.objects.new('Pivot',None);S.collection.objects.link(pivot);pivot.location=anchor;m=rig.matrix_world.copy();rig.parent=pivot;rig.matrix_world=m
for o in bpy.data.objects:
  if o.type=='MESH' and o.parent is None and o.name not in build.get('bodyMeshes',[]):o.parent=pivot  # malhas soltas rodam com a unidade
cam_d=bpy.data.cameras.new('Cam');cam_d.type='ORTHO';cam=bpy.data.objects.new('Cam',cam_d);S.collection.objects.link(cam);S.camera=cam
target=anchor+Vector((0,0,.9));cam.location=target+Vector((6,-6,math.sqrt(72)/math.sqrt(3)));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam_d.ortho_scale=4
# luz: sol do canto superior esquerdo do ecrã (como os edifícios) + céu suave
sun_d=bpy.data.lights.new('Sun','SUN');sun_d.energy=float(args.get('sun',3.2));sun_d.angle=math.radians(10);sun=bpy.data.objects.new('Sun',sun_d);S.collection.objects.link(sun)
sun.rotation_euler=(math.radians(float(args.get('sel',50))),0,math.radians(float(args.get('saz',-80))))
fill_d=bpy.data.lights.new('Fill','SUN');fill_d.energy=float(args.get('fill',.6));fill=bpy.data.objects.new('Fill',fill_d);S.collection.objects.link(fill);fill.rotation_euler=(math.radians(60),0,math.radians(120))
w=bpy.data.worlds.new('W');S.world=w;w.use_nodes=True;bg=w.node_tree.nodes['Background'];bg.inputs[0].default_value=(.62,.66,.75,1);bg.inputs[1].default_value=float(args.get('amb',.9))
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=SAMPLES;S.cycles.use_denoising=True
try:S.cycles.denoiser='OPENIMAGEDENOISE'
except Exception:pass
S.render.film_transparent=True;S.render.resolution_x=S.render.resolution_y=RES;S.render.resolution_percentage=100
S.view_settings.view_transform=args.get('vt','Standard');S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA'
S.cycles.max_bounces=4;S.render.threads=int(args.get('threads',0)) or 0
def pose(direction,fr):
  pivot.rotation_euler.z=math.pi/2-direction*math.pi/4
  for t in rig.animation_data.nla_tracks:t.mute=t.name!=fr['clip']
  for kind,objs in build['props'].items():
    for lab in objs:
      ob=bpy.data.objects.get(lab)
      if ob:ob.hide_render=kind!=fr['tool'];ob.hide_set(kind!=fr['tool'])
  a,b=clipLen[fr['clip']];f=a+(b-a)*fr['phase'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
def meshes(fr):
  L=[bpy.data.objects[n] for n in build.get('bodyMeshes',[build['body']])]
  return L+[bpy.data.objects[l] for l in build['props'].get(fr['tool'],[]) if l in bpy.data.objects]
camf=OUT/'camera.json'
if camf.exists():
  c=json.loads(camf.read_text());cam.location=c['loc'];cam.rotation_euler=c['rot'];cam_d.ortho_scale=c['ortho'];bodyRef=c['bodyRef']
else:
  pts=[]
  for d in range(8):
    for fr in frames:
      pose(d,fr);dg=bpy.context.evaluated_depsgraph_get()
      for ob in meshes(fr):
        ev=ob.evaluated_get(dg);pts.extend(world_to_camera_view(S,cam,ev.matrix_world@Vector(p)) for p in ev.bound_box)
  x0,x1=min(p.x for p in pts),max(p.x for p in pts);y0,y1=min(p.y for p in pts),max(p.y for p in pts);sz=cam_d.ortho_scale
  cam.location+=cam.matrix_world.to_quaternion()@Vector((((x0+x1)/2-.5)*sz,((y0+y1)/2-.5)*sz,0));cam_d.ortho_scale*=max(x1-x0,y1-y0)*1.15;bpy.context.view_layer.update()
  pose(1,frames[0]);ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();import numpy as np
  co=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',co.ravel());mm=cam.matrix_world.inverted()@ev.matrix_world;hts=co@np.array(mm[1][:3])+mm[1][3];bodyRef=float(np.ptp(hts))/cam_d.ortho_scale;ev.to_mesh_clear()
  camf.write_text(json.dumps({'loc':list(cam.location),'rot':list(cam.rotation_euler),'ortho':cam_d.ortho_scale,'bodyRef':bodyRef}))
rep={'unit':name,'res':RES,'samples':SAMPLES,'bodyReferencePixels':bodyRef*RES,'framesPerDirection':len(frames),'states':states,'labels':['SE','S','SW','W','NW','N','NE','E'],'frames':[],'glbSha256':hashlib.sha256((A/f'{name}.glb').read_bytes()).hexdigest()}
sel=None
if only:sel=[tuple(map(int,x.split(':'))) for x in only.split(',')]
t0=time.time()
for d in range(8):
  for fr in frames:
    if sel and (d,fr['i']) not in sel:continue
    pose(d,fr);p=world_to_camera_view(S,cam,anchor);rep['frames'].append({**fr,'direction':d,'anchor':[p.x*RES,(1-p.y)*RES]})
    f=OUT/'frames'/f'{d:02d}-{fr["i"]:02d}.png'
    if not f.exists() or args.get('force'):S.render.filepath=str(f);bpy.ops.render.render(write_still=True)
  print('DIR',name,d,round(time.time()-t0,1),flush=True)
(OUT/('render-report.json' if not sel else 'test-report.json')).write_text(json.dumps(rep,indent=1));print('DONE',name,round(time.time()-t0,1))
