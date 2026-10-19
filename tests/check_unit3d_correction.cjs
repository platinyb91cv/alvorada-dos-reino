const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.join(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const start=html.indexOf('function unit3dFrame('),end=html.indexOf('\nfunction ',start+1);
const frame=vm.runInNewContext('('+html.slice(start,end)+')',{Math,performance:{now:()=>0},atkPhase:()=>.5});
// O guerreiro antigo foi substituído pelo soldado v2 (arte/soldados-meshy/atlas); a correção de pose fica validada só no aldeão.
for(const name of ['aldeao']){
 const meta=JSON.parse(fs.readFileSync(path.join(root,'www/assets/units3d',name+'.json'))),proof=JSON.parse(fs.readFileSync(path.join(root,'arte/unidades3d',name+'.verification.json')));
 assert.equal(proof.atlasSha256,meta.atlasSha256);assert.equal(proof.correctionChecks.newMeshyCredits,0);
 assert.ok(proof.correctionChecks.maxArmLateralFraction<.2);assert.ok(Object.values(proof.correctionChecks.boneAttachmentMatrixErrors).every(x=>x<1e-3));
 assert.ok(Object.values(proof.correctionChecks.armLegCorrelation).every(x=>x<-.9),'arms must swing opposite the legs');
 assert.ok(Object.values(proof.correctionChecks.cyclicPoseMatrixError).every(x=>x<1e-4));
 for(const [state,locomotion]of Object.entries(meta.locomotion)){
  assert.ok(Math.abs(locomotion.phaseScale*locomotion.strideTiles-2*Math.PI/5)<1e-8,'stride must match game distance');
  assert.ok(Math.abs(locomotion.animFactor-5*locomotion.phaseScale)<1e-8);
  for(let i=0;i<8;i++)assert.equal(frame({anim:5*locomotion.strideTiles*(i+.5)/8,id:0},state,meta),meta.states[state][i]);
 }
 if(name==='aldeao'){
  assert.ok(proof.correctionChecks.maxAxeGripErrorMeters<1e-4);assert.equal(proof.correctionChecks.chopFrames.length,6);
  assert.ok(proof.correctionChecks.chopFrames.every(f=>f.handHeightMeters>.65&&f.hipsHeightMeters>.85&&f.tool.length===2));
  assert.ok('forage_basket'in proof.rigidProps);
  assert.equal(proof.axeVisibility.sourceModelSha256,proof.optimizedGlbSha256);assert.equal(proof.axeVisibility.frames.length,48);assert.ok(proof.axeVisibility.frames.every(f=>f.visibleBladeAreaAt30px>0));
 }else assert.ok(proof.correctionChecks.maxTorsoLeanDegrees<5);
}
console.log('PASS: corrected arm/torso poses, rigid hand attachments, six held-axe phases, basket and measured walk/carry cadence');
