import bpy,json,math,statistics,sys
from pathlib import Path
O=Path(sys.argv[sys.argv.index('--sources')+1]).resolve()if '--sources'in sys.argv else Path(__file__).resolve().parent.parent
for name in ['aldeao','guerreiro']:
 d=O/name;bpy.ops.wm.open_mainfile(filepath=str(d/(name+'-jogo.blend')));r=json.loads((d/'build-report.json').read_text());rig=bpy.data.objects[r['rig']];rig.animation_data.action=None
 camera=json.loads((d/'fixed-camera.json').read_text());s=192/camera['orthoScale']*30/camera['bodyReferencePixels'];meters_per_tile=32/(s*math.sqrt(.5))
 def measure(clip):
  for t in rig.animation_data.nla_tracks:t.mute=t.name!=clip
  rows=[];N=240
  for i in range(N+1):
   f=1+23*i/N;bpy.context.scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();rows.append({n:list(rig.matrix_world@rig.pose.bones[n].head)for n in ['LeftFoot','RightFoot','LeftHand','RightHand','Hips','Head']})
  foot={}
  for side in ['LeftFoot','RightFoot']:
   low=min(x[side][2]for x in rows);high=max(x[side][2]for x in rows);vel=[]
   for i in range(1,N):
    speed=(rows[i+1][side][1]-rows[i-1][side][1])*N/2
    if rows[i][side][2]<low+.30*(high-low)and speed>0:vel.append(speed)
   foot[side]={'stanceTravelPerCycleMeters':statistics.median(vel),'stanceSampleCount':len(vel),'stanceSpeedRangeMeters':[min(vel),max(vel)],'swingRangeMeters':max(x[side][1]for x in rows)-min(x[side][1]for x in rows)}
  stride=statistics.mean(x['stanceTravelPerCycleMeters']for x in foot.values());factor=2*math.pi*meters_per_tile/stride
  return {'foot':foot,'strideMeters':stride,'strideTiles':stride/meters_per_tile,'recommendedAnimFactor':factor,'visualPhaseMultiplier':factor/5,'rows':rows}
 result={'unit':name,'method':'Median ground-level backward foot speed over one normalized cycle; average of both feet. Camera projection converted at 30px display height. No mesh or world scaling changed.','screenPixelsPerMeter':s,'metersPerTile':meters_per_tile,'gameCycleTilesAtFactor5':2*math.pi/5,'animationFrames':8,**measure('Walk')}
 if name=='aldeao':result['carry']=measure('Carry')
 (d/'stride-verification.json').write_text(json.dumps(result,indent=2));print('MEASURED_STRIDE',name,result['recommendedAnimFactor'],result.get('carry',{}).get('recommendedAnimFactor'),flush=True)
