import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
O=Path(sys.argv[sys.argv.index('--sources')+1]).resolve()if '--sources'in sys.argv else Path(__file__).resolve().parent.parent
for name in ['aldeao','guerreiro']:
 d=O/name;bpy.ops.wm.open_mainfile(filepath=str(d/(name+'-jogo.blend')));S=bpy.context.scene;r=json.loads((d/'build-report.json').read_text());rig=bpy.data.objects[r['rig']];rig.animation_data.action=None
 def pose(clip,t):
  for tr in rig.animation_data.nla_tracks:tr.mute=tr.name!=clip
  f=1+(r['clips'][clip]['frames']-1)*t;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 arm=[];torso=[];grip=[];chop=[];loop={};opposition={side:[]for side in ['Left','Right']}
 for clip in ['Walk','Idle']+(['Carry']if name=='aldeao'else []):
  for t in [i/32 for i in range(33)]:
   pose(clip,t)
   for side in ['Left','Right']:
    p=rig.pose.bones[side+'Arm'];v=rig.matrix_world.to_3x3()@(p.tail-p.head);arm.append(abs(v.x)/v.length)
    if clip=='Walk':
     foot=rig.matrix_world@rig.pose.bones[side+'Foot'].head;hip=rig.matrix_world@rig.pose.bones['Hips'].head;opposition[side].append((foot.y-hip.y,v.y))
   if name=='guerreiro':
    v=rig.pose.bones['neck'].head-rig.pose.bones['Spine02'].head;torso.append(math.degrees(math.atan2(math.hypot(v.x,v.y),v.z)))
  if clip in ['Walk','Carry']:
   pose(clip,0);first={p.name:p.matrix.copy()for p in rig.pose.bones};pose(clip,1);loop[clip]=max(abs(p.matrix[i][j]-first[p.name][i][j])for p in rig.pose.bones for i in range(4)for j in range(4));assert loop[clip]<1e-4
 assert max(arm)<.2,(name,'arms still abducted',max(arm))
 if torso:assert max(torso)<5,(name,'torso leans',max(torso))
 attachment={}
 for kind,labels in r['props'].items():
  for label in labels:
   ob=bpy.data.objects[label];base=None;error=0
   assert ob.parent==rig and ob.parent_type=='BONE'
   for clip in r['clips']:
    for t in [0,.2,.5,.8,1]:
     pose(clip,t);relative=(rig.matrix_world@rig.pose.bones[ob.parent_bone].matrix).inverted()@ob.matrix_world
     if base is None:base=relative.copy()
     error=max(error,max(abs(relative[i][j]-base[i][j])for i in range(4)for j in range(4)))
   assert error<1e-3,(name,label,'detached from hand',error);attachment[label]=error
 if name=='aldeao':
  for phase in [.05,.2,.35,.5,.65,.8]:
   pose('Chop',phase);shaft=bpy.data.objects[r['props']['axe'][0]];v=list(shaft.data.vertices);a=shaft.matrix_world@(sum((x.co for x in v[:10]),Vector())/10);b=shaft.matrix_world@(sum((x.co for x in v[10:]),Vector())/10);hand=rig.matrix_world@rig.pose.bones['RightHand'].head;err=(a+(b-a)*.3-hand).length;grip.append(err);assert err<1e-4
   hip=rig.matrix_world@rig.pose.bones['Hips'].head;assert hip.z>.85;assert hand.z>.65
   chop.append({'phase':phase,'handHeightMeters':hand.z,'hipsHeightMeters':hip.z,'shaftGripErrorMeters':err,'tool':r['props']['axe']})
  assert 'basket'in r['props']
 correlations={}
 for side,pairs in opposition.items():
  ax=sum(a for a,b in pairs)/len(pairs);ay=sum(b for a,b in pairs)/len(pairs);corr=sum((a-ax)*(b-ay)for a,b in pairs)/math.sqrt(sum((a-ax)**2 for a,b in pairs)*sum((b-ay)**2 for a,b in pairs));assert corr<-.9,(name,side,'arm must oppose leg',corr);correlations[side]=corr
 result={'unit':name,'armLegCorrelation':correlations,'maxArmLateralFraction':max(arm),'maxTorsoLeanDegrees':max(torso)if torso else None,'cyclicPoseMatrixError':loop,'maxAxeGripErrorMeters':max(grip)if grip else None,'chopFrames':chop,'boneAttachmentMatrixErrors':attachment,'newMeshyCredits':0}
 (d/'correction-verification.json').write_text(json.dumps(result,indent=2));print('CORRECTION_VERIFIED',name,json.dumps(result),flush=True)
