// Máquinas de cerco Meshy (aríete, trebuchet): atlas de 8 direções, metadados embutidos e ligação ao renderer de unidades 3D.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const data=JSON.parse(html.match(/const UNIT3D_SIEGE_DATA=(\{[^\n]+\});/)[1]);assert.deepEqual(Object.keys(data),['ariete','trebuchet']);
const types=JSON.parse(html.match(/const UNIT3D_TYPES=(\[[^\]]+\]);/)[1].replace(/'/g,'"'));for(const t of ['ariete','trebuchet'])assert.ok(types.includes(t),'8-direction heading for '+t);
const proof=JSON.parse(fs.readFileSync(path.join(root,'arte/cerco-meshy/verification.json'),'utf8'));assert.equal(proof.creditosAdicionais,0);
let pixels=0;
for(const [type,meta] of Object.entries(data)){
 assert.equal(meta.directions,8);assert.equal(meta.f.length,8*meta.framesPerDirection);assert.deepEqual(meta.directionLabels,['SE','S','SW','W','NW','N','NE','E']);
 for(const [s,n] of [['idle',2],['walk',8],['attack',6],['hit',2],['death',4]])assert.equal(meta.states[s].length,n,type+' '+s);
 assert.deepEqual(meta,JSON.parse(fs.readFileSync(path.join(root,'www/assets/units3d',type+'.json'),'utf8')));
 const webp=fs.readFileSync(path.join(root,'www/assets/units3d',type+'.webp'));assert.equal(crypto.createHash('sha256').update(webp).digest('hex'),meta.atlasSha256);assert.equal(proof.atlas[type],meta.atlasSha256);
 assert.equal(webp.toString('ascii',8,16),'WEBPVP8L');const bits=webp.readUInt32LE(21),w=(bits&16383)+1,h=((bits>>>14)&16383)+1;pixels+=w*h;
 for(const [x,y,fw,fh] of meta.f)assert.ok(x>=0&&y>=0&&x+fw<=w&&y+fh<=h,'frame inside atlas');
 const L=meta.locomotion.walk;assert.ok(Math.abs(L.phaseScale*L.strideTiles-2*Math.PI/5)<1e-5,'wheel cadence matches movement');
 assert.ok(meta.h>40&&meta.h<64,'downscaled atlas keeps real on-screen size');
 const rig=fs.readFileSync(path.join(root,proof.riggados[type].ficheiro));assert.equal(crypto.createHash('sha256').update(rig).digest('hex'),proof.riggados[type].sha256);assert.ok(rig.length<20*1024*1024);
}
assert.ok(pixels<4e6,'siege atlases stay within a small memory budget');
assert.match(html,/for\(const type of Object\.keys\(UNIT3D_SIEGE_DATA\)\)\{const source=/);
console.log('PASS: ram and trebuchet 8-direction atlases, rigs and wheel cadence');
