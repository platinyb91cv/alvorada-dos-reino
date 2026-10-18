const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.join(__dirname,'..');
const cost=JSON.parse(fs.readFileSync(path.join(root,'arte/unidades3d/meshy-segunda-volta.json')));assert.equal(cost.authorizedMaximumCredits,39);assert.equal(cost.totalConsumedCredits,39);assert.equal(cost.automaticPaidRetries,false);assert.equal(cost.clips.length,3);
for(const name of ['aldeao','guerreiro']){
 const p=JSON.parse(fs.readFileSync(path.join(root,'arte/unidades3d',name+'.verification.json'))),s=p.secondPass;
 assert.ok(Math.abs(s.axeScaleVsOriginal-1.4)<1e-4);
 assert.ok(s.axeWedgeThicknessMeters[0]/s.axeWedgeThicknessMeters[1]<.25);
 assert.equal(s.toolCorrection.newCharacterGenerations,0);
 if(name==='aldeao'){
  assert.ok(s.hoe.bladeThicknessMeters<.025);assert.ok(s.hoe.workingBladeNormalZ>.99);
  assert.deepEqual(s.dedicatedWorkClips,['Mine','Build','Butcher']);assert.equal(s.workMotionCredits,39);
  for(const [state,clip]of Object.entries({mine:'Mine',build:'Build',butcher:'Butcher',farm:'Farm'}))assert.deepEqual(p.renderStateClips[state],[clip]);
  assert.equal(new Set(Object.values(p.workMotions).map(x=>x.sourceSha256)).size,3);
  assert.equal(new Set(s.dedicatedWorkClips.map(c=>p.reimportedClipPoseSha256[c])).size,3);
  assert.equal(Object.values(p.workMotions).reduce((n,x)=>n+x.motionCredits+x.retargetCredits,0),39);
  for(const c of cost.clips){const clip=c.state[0].toUpperCase()+c.state.slice(1);assert.equal(c.sourceGlbSha256,p.workMotions[clip].sourceSha256);assert.equal(c.motion.status,'SUCCEEDED');assert.equal(c.retarget.status,'SUCCEEDED');assert.equal(c.motion.consumedCredits,10);assert.equal(c.retarget.consumedCredits,3);}
  assert.equal(p.knifeVisibility.sourceModelSha256,p.optimizedGlbSha256);
  const visible=p.knifeVisibility.frames.filter(f=>['SE','S'].includes(f.direction));assert.equal(visible.length,12);assert.ok(visible.every(f=>f.visibleBladeAreaAt30px>0));
 }
}
console.log('PASS: wedge axes at 1.4x, flat ground-facing hoe, three distinct Prime clips, 39 credits and visible SE/S knife');
