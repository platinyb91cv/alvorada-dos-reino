// Soldados HD: atlas h=128 renderizados a 512px a partir dos mesmos GLB dos armados (reduzidos, não ampliados);
// mesma ordem de quadros/estados que os armados; proveniência com o sha do GLB; carregados só com Resolução HD e memória suficiente.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const hd=JSON.parse(html.match(/const UNIT3D_HD_DATA=(\{[^\n]*\});/)[1]),armed=JSON.parse(html.match(/const UNIT3D_ARMED_DATA=(\{[^\n]+\});/)[1]);
let pixels=0;
for(const [u,m] of Object.entries(hd)){
  const folder=path.join(root,'www/assets/units3d-hd');assert.deepEqual(m,JSON.parse(fs.readFileSync(path.join(folder,u+'.json'))));
  const bytes=fs.readFileSync(path.join(folder,u+'.webp'));assert.equal(m.atlasSha256,crypto.createHash('sha256').update(bytes).digest('hex'));assert.ok(bytes.length<4.5*1024*1024,u+' atlas size');
  assert.equal(m.h,u==='aldeao'?96:128,'aldeão a 96 (576 quadros), soldados a 128');const a=armed[u];assert.ok(a,'HD only for armed units');assert.deepEqual(m.states,a.states);assert.equal(m.framesPerDirection,a.framesPerDirection);assert.deepEqual(m.directionLabels,a.directionLabels);assert.equal(m.f.length,m.framesPerDirection*8);
  const prov=JSON.parse(fs.readFileSync(path.join(root,'arte/unidades-hd',u+'.verification.json')));const proofA=JSON.parse(fs.readFileSync(path.join(root,'arte/unidades-armadas',u+'.verification.json')));
  assert.equal(prov.atlasSha256,m.atlasSha256);assert.equal(prov.glbSha256,proofA.sha256,'same GLB as armed');assert.equal(prov.additionalMeshyCredits,0);assert.ok(prov.downscaleFactor<1,'downscaled, not upscaled');assert.ok(prov.renderResolution>=512);
  const W=bytes.readUInt32LE(24)&0xffffff;let w,h;if(bytes.toString('ascii',12,16)==='VP8L'){const bits=bytes.readUInt32LE(21);w=(bits&16383)+1;h=((bits>>>14)&16383)+1}else{w=(W)+1;h=(bytes.readUIntLE(27,3))+1}
  assert.ok(w<=2048&&h<=4096);pixels+=w*h;for(const f of m.f){assert.equal(f.length,6);assert.ok(f[0]>=0&&f[1]>=0&&f[0]+f[2]<=w&&f[1]+f[3]<=h,'inside '+u)}}
assert.ok(pixels<26000000,'HD decoded budget');
assert.match(html,/function unit3dHdOn\(\)\{try\{return RES==='hd'&&\(navigator\.deviceMemory\|\|4\)>=4\}/,'HD gated by setting and memory');
assert.match(html,/image\.onerror=\(\)=>load\(preferred\|\|UNIT3D_DATA\[type\]/,'HD falls back to armed atlas');
console.log('PASS: HD soldiers ('+Object.keys(hd).length+' atlases, '+pixels+' pixels)');
