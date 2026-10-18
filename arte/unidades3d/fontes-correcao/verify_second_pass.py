import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent.parent
for name in ['aldeao','guerreiro']:
 d=O/name;bpy.ops.wm.open_mainfile(filepath=str(d/(name+'-jogo.blend')));S=bpy.context.scene;r=json.loads((d/'build-report.json').read_text());rig=bpy.data.objects[r['rig']];rig.animation_data.action=None
 def pose(clip,t):
  for tr in rig.animation_data.nla_tracks:tr.mute=tr.name!=clip
  f=1+(r['clips'][clip]['frames']-1)*t;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 def points(label):
  ob=bpy.data.objects[label];return [ob.matrix_world@v.co for v in ob.data.vertices]
 pose('Idle',.2);p=points(r['props']['axe'][0]);length=(sum(p[10:],Vector())/10-sum(p[:10],Vector())/10).length;assert abs(length-.91)<1e-4;v=points(r['props']['axe'][1]);thickness=[(v[i+8]-v[i]).length for i in range(8)];assert min(thickness)/max(thickness)<.25
 result={'unit':name,'axeHandleLengthMeters':length,'axeScaleVsOriginal':length/.65,'axeWedgeThicknessMeters':[min(thickness),max(thickness)],'axeHeadVertexCount':len(v),'toolCorrection':r['toolCorrection2']}
 if name=='aldeao':
  pose('Farm',.5);v=points(r['props']['hoe'][1]);thickness=[(v[i+4]-v[i]).length for i in range(4)];normal=(v[1]-v[0]).cross(v[3]-v[0]).normalized();assert max(thickness)<.025;assert abs(normal.z)>.99;result['hoe']={'bladeThicknessMeters':max(thickness),'workingBladeNormalZ':abs(normal.z),'clip':'Farm','baseClip':'Harvest'}
  provenance=json.loads((d/'work-motion-provenance.json').read_text());assert set(provenance)=={'Mine','Build','Butcher'};assert len({v['sourceSha256']for v in provenance.values()})==3;credits=sum(v['motionCredits']+v['retargetCredits']for v in provenance.values());assert credits==39;result['workMotionCredits']=credits;result['dedicatedWorkClips']=list(provenance)
 (d/'second-pass-verification.json').write_text(json.dumps(result,indent=2));print('SECOND_PASS_VERIFIED',json.dumps(result),flush=True)
