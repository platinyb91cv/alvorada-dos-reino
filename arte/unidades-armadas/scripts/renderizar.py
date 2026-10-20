import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
O=Path(sys.argv[sys.argv.index('--sources')+1]).resolve()if '--sources'in sys.argv else Path(__file__).resolve().parent.parent
names=[u['id']for u in json.loads((O/'manifest.json').read_text())['units']]
if '--unit'in sys.argv:names=[sys.argv[sys.argv.index('--unit')+1]]
labels=['SE','S','SW','W','NW','N','NE','E']
for name in names:
 d=O/name;(d/'frames').mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(d/(name+'-jogo.blend')));S=bpy.context.scene;report=json.loads((d/'build-report.json').read_text());rig=bpy.data.objects[report['rig']];rig.animation_data.action=None;body=bpy.data.objects[report['body']];default=report['defaultProp'];states={};frames=[]
 def sequence(state,clip,phases,tool):
  states[state]=[]
  for phase in phases:states[state].append(len(frames));frames.append({'i':len(frames),'state':state,'clip':clip,'phase':phase,'tool':tool})
 sequence('idle','Idle',[.2,.7],default);sequence('walk','Walk',[i/8 for i in range(8)],default);sequence('attack','Attack',[0,.15,.3,.5,.7,.9],'hammer'if name=='aldeao'else default);sequence('hit','Hit',[.2,.55],default);sequence('death','Death',[.1,.35,.65,1],default)
 if name=='aldeao':
  for state,clip,tool in [('chop','Chop','axe'),('mine','Mine','pick'),('build','Build'if 'Build'in report['clips']else 'Mine','build_hammer'if 'build_hammer'in report['props']else 'hammer'),('farm','Farm'if 'Farm'in report['clips']else 'Harvest','hoe'),('forage','Harvest','basket'),('hunt','Attack','spear'),('butcher','Butcher'if 'Butcher'in report['clips']else 'Mine','knife')]:sequence(state,clip,[.05,.2,.35,.5,.65,.8],tool)
  sequence('carry','Carry',[i/8 for i in range(8)],'cargo')
 anchor=rig.matrix_world@rig.data.bones['Hips'].head_local;anchor.z=0;pivot=bpy.data.objects.new('EightDirectionPivot',None);S.collection.objects.link(pivot);pivot.location=anchor;matrix=rig.matrix_world.copy();rig.parent=pivot;rig.matrix_world=matrix
 camera=S.camera;target=anchor+Vector((0,0,.9));camera.location=target+Vector((6,-6,math.sqrt(72)/math.sqrt(3)));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=4
 S.render.resolution_x=S.render.resolution_y=128;S.render.resolution_percentage=100
 if '--only-state'in sys.argv:S.render.threads=1
 S.cycles.samples=2;S.render.use_persistent_data=True
 if '--eevee' in sys.argv:S.render.engine='BLENDER_EEVEE'
 rendering=False
 def pose(direction,frame):
  pivot.rotation_euler.z=math.pi/2-direction*math.pi/4
  for tr in rig.animation_data.nla_tracks:tr.mute=tr.name!=frame['clip']
  for kind,objects in report['props'].items():
   for label in objects:
    ob=bpy.data.objects[label];ob.hide_render=kind!=frame['tool'];ob.hide_set(kind!=frame['tool'])
  length=report['clips'][frame['clip']]['frames'];f=1+(length-1)*frame['phase'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
  if False and rendering and frame['tool']=='cargo':
   left=rig.matrix_world@rig.pose.bones['LeftHand'].head;right=rig.matrix_world@rig.pose.bones['RightHand'].head;rotation=pivot.rotation_euler.to_matrix().to_4x4();center=(left+right)/2+rotation.to_3x3()@Vector((0,-.035,-.025))
   for label in report['props']['cargo']:
    ob=bpy.data.objects[label];local_center=sum((Vector(p)for p in ob.bound_box),Vector())/8;crate_width=.28 if report.get('correction')else .72;ob.matrix_world=Matrix.Translation(center)@rotation@Matrix.Diagonal(Vector((crate_width/.42,1,1,1)))@Matrix.Translation(-local_center)
   bpy.context.view_layer.update()
 def active_meshes(frame):return [bpy.data.objects[n] for n in report.get('bodyMeshes',[report['body']])]+[bpy.data.objects[label]for label in report['props'].get(frame['tool'],[])]
 points=[]
 for direction in range(8):
  for frame in frames:
   pose(direction,frame);deps=bpy.context.evaluated_depsgraph_get()
   for ob in active_meshes(frame):
    ev=ob.evaluated_get(deps);points.extend(world_to_camera_view(S,camera,ev.matrix_world@Vector(p))for p in ev.bound_box)
 x0,x1=min(p.x for p in points),max(p.x for p in points);y0,y1=min(p.y for p in points),max(p.y for p in points);size=camera.data.ortho_scale;camera.location+=camera.matrix_world.to_quaternion()@Vector((((x0+x1)/2-.5)*size,((y0+y1)/2-.5)*size,0));camera.data.ortho_scale*=max(x1-x0,y1-y0)*1.15
 pose(1,frames[0]);ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();import numpy as np; coords=np.empty((len(me.vertices),3),dtype=np.float32);me.vertices.foreach_get('co',coords.ravel());m=camera.matrix_world.inverted()@ev.matrix_world;heights=coords@np.array(m[1][:3])+m[1][3];body_pixels=float(np.ptp(heights))*128/camera.data.ortho_scale;ev.to_mesh_clear()
 if '--capture-camera'in sys.argv:
  (d/'fixed-camera.json').write_text(json.dumps({'location':list(camera.location),'rotation':list(camera.rotation_euler),'orthoScale':camera.data.ortho_scale,'bodyReferencePixels':body_pixels,'anchor':list(anchor)},indent=2));continue
 if (d/'fixed-camera.json').exists():
  fixed=json.loads((d/'fixed-camera.json').read_text());camera.location=fixed['location'];camera.rotation_euler=fixed['rotation'];camera.data.ortho_scale=fixed['orthoScale'];body_pixels=fixed['bodyReferencePixels'];bpy.context.view_layer.update()
 output={'sourceModelSha256':hashlib.sha256((d/(name+'-jogo.glb')).read_bytes()).hexdigest(),'bodyReferencePixels':body_pixels,'unit':name,'directions':8,'framesPerDirection':len(frames),'states':states,'labels':labels,'frames':[],'resolution':128,'cpuSamples':2}
 rendering=True
 if '--verify-axe-visibility'in sys.argv or '--verify-knife-visibility'in sys.argv:
  from mathutils.bvhtree import BVHTree
  knife_mode='--verify-knife-visibility'in sys.argv;kind='knife'if knife_mode else 'axe';state='butcher'if knife_mode else 'chop';checks=[];native=128*30/body_pixels;rotation=camera.matrix_world.to_quaternion();right=rotation@Vector((1,0,0));up=rotation@Vector((0,1,0));ray=rotation@Vector((0,0,-1));size=camera.data.ortho_scale
  def tree(ob):
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vertices=[ev.matrix_world@v.co for v in me.vertices];faces=[tuple(p.vertices)for p in me.polygons];result=BVHTree.FromPolygons(vertices,faces);ev.to_mesh_clear();return result,vertices
  for direction in range(8):
   for frame in frames:
    if frame['state']!=state:continue
    pose(direction,frame);occluder,_=tree(body);blade=bpy.data.objects[report['props'][kind][1]];target,vertices=tree(blade);projected=[world_to_camera_view(S,camera,p)for p in vertices];x0=max(0,int(min(p.x for p in projected)*native)-1);x1=min(math.ceil(native),math.ceil(max(p.x for p in projected)*native)+1);y0=max(0,int(min(p.y for p in projected)*native)-1);y1=min(math.ceil(native),math.ceil(max(p.y for p in projected)*native)+1);area=0
    for x in range(x0,x1):
     for y in range(y0,y1):
      for sx,sy in [(.25,.25),(.75,.25),(.25,.75),(.75,.75)]:
       origin=camera.location+right*((x+sx)/native-.5)*size+up*((y+sy)/native-.5)*size;hit=target.ray_cast(origin,ray);block=occluder.ray_cast(origin,ray)
       if hit[0]is not None and (block[0]is None or hit[3]<block[3]+1e-4):area+=.25
    checks.append({'direction':labels[direction],'frame':frame['i'],'phase':frame['phase'],'visibleBladeAreaAt30px':area})
  (d/(kind+'-visibility.json')).write_text(json.dumps({'sourceModelSha256':hashlib.sha256((d/(name+'-jogo.glb')).read_bytes()).hexdigest(),'method':'4 subpixel orthographic rays per native 30px pixel; evaluated body BVH occlusion against the '+kind+' blade mesh','frames':checks},indent=2));print(kind.upper()+'_VISIBILITY',name,min(c['visibleBladeAreaAt30px']for c in checks),flush=True);continue
 for direction in range(8):
  if '--preview'in sys.argv and direction>1:continue
  subset=[frames[0]]if '--calibrate'in sys.argv else frames
  for frame in subset:
   if '--preview'in sys.argv and frame['i']not in [0,2,4,6,8,22,24,25,27,28,30,32,34,36,38,40,41,42,44,46,58,60,62,64]:continue
   pose(direction,frame);p=world_to_camera_view(S,camera,anchor);row={**frame,'direction':direction,'anchor':[p.x*128,(1-p.y)*128]};output['frames'].append(row);file=d/'frames'/f"{direction:02d}-{frame['i']:02d}.png";S.render.filepath=str(file)
   force_state=sys.argv[sys.argv.index('--only-state')+1]if '--only-state'in sys.argv else None
   force_states=sys.argv[sys.argv.index('--only-states')+1].split(',')if '--only-states'in sys.argv else None
   if force_state and frame['state']!=force_state:continue
   if force_states and frame['state']not in force_states:continue
   if '--force-all'in sys.argv or force_state or force_states or not file.exists()or int.from_bytes(file.read_bytes()[16:20],'big')!=128 or '--calibrate'in sys.argv:bpy.ops.render.render(write_still=True)
  print('UNIT_DIRECTION_COMPLETE',name,direction,flush=True)
 (d/('preview-report.json'if '--preview'in sys.argv else 'calibration.json'if '--calibrate'in sys.argv else 'render-report.json')).write_text(json.dumps(output,indent=2));print('UNIT_SPRITES_COMPLETE',name,flush=True)
