import bpy,json,sys,math,statistics,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;units=['aldeao','guerreiro','lanceiro','espadachim','arqueiro','besteiro']
for unit in units:
 D=R/unit;bpy.ops.wm.open_mainfile(filepath=str(D/(unit+'-jogo.blend')));report=json.loads((D/'build-report.json').read_text());rig=bpy.data.objects[report['rig']];rig.animation_data.action=None;camera=json.loads((D/'fixed-camera.json').read_text());pixels_per_metre=128/camera['orthoScale']*30/camera['bodyReferencePixels'];metres_per_tile=32/(pixels_per_metre*math.sqrt(.5));result={}
 for clip in ['Walk']+(['Carry'] if unit=='aldeao' else []):
  for t in rig.animation_data.nla_tracks:t.mute=t.name!=clip
  tr=next(t for t in rig.animation_data.nla_tracks if t.name==clip);st=tr.strips[0];rows=[];N=120
  for i in range(N+1):
   f=st.frame_start+(st.frame_end-st.frame_start)*i/N;bpy.context.scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();rows.append({n:list(rig.matrix_world@rig.pose.bones[n].head) for n in ['LeftFoot','RightFoot','Hips']})
  feet={}
  for side in ['LeftFoot','RightFoot']:
   low=min(r[side][2] for r in rows);high=max(r[side][2] for r in rows);speeds=[]
   for i in range(1,N):
    speed=(rows[i+1][side][1]-rows[i-1][side][1])*N/2
    if rows[i][side][2]<low+.35*(high-low) and speed>1e-5:speeds.append(speed)
   if not speeds:raise RuntimeError('No forward ground stance samples: '+unit+'/'+clip+'/'+side)
   feet[side]={'stanceTravelPerCycleMeters':statistics.median(speeds),'stanceSampleCount':len(speeds),'swingRangeMeters':max(r[side][1] for r in rows)-min(r[side][1] for r in rows)}
  stride=statistics.mean(v['stanceTravelPerCycleMeters'] for v in feet.values());tiles=stride/metres_per_tile;factor=2*math.pi/tiles;result[clip]={'foot':feet,'strideMeters':stride,'strideTiles':tiles,'recommendedAnimFactor':factor,'visualPhaseMultiplier':factor/5,'durationSeconds':(st.frame_end-st.frame_start)/24}
 primary=result['Walk'];out={'unit':unit,'method':'Median backwards foot velocity during low ground stance, per normalized clip cycle; both feet; orthographic game projection at 30px.','screenPixelsPerMeter':pixels_per_metre,'metersPerTile':metres_per_tile,**primary}
 if 'Carry' in result:out['carry']=result['Carry']
 (D/'stride-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('STRIDE',unit,primary['recommendedAnimFactor'],flush=True)
