// Cavalaria 3D: atlas de 8 direções para cavaleiro, cavPesada e cavArqueira, metadados embutidos e cadência do galope.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const data=JSON.parse(html.match(/const UNIT3D_CAV_DATA=(\{[^\n]+\});/)[1]);
const proof=JSON.parse(fs.readFileSync(path.join(root,'arte/cavalaria-3d/verification.json'),'utf8'));assert.equal(proof.creditosAdicionais,0);
assert.match(fs.readFileSync(path.join(root,'arte/cavalaria-3d/fontes/Quaternius-License.txt'),'utf8'),/CC0/);
const types=JSON.parse(html.match(/const UNIT3D_TYPES=(\[[^\]]+\]);/)[1].replace(/'/g,'"'));
for(const t of ['cavaleiro','cavPesada','cavArqueira']){
 assert.ok(types.includes(t),'8-direction heading for '+t);const meta=data[t];assert.ok(meta,t);
 assert.equal(meta.directions,8);assert.equal(meta.f.length,8*meta.framesPerDirection);assert.deepEqual(meta.directionLabels,['SE','S','SW','W','NW','N','NE','E']);
 for(const [s,n] of [['idle',2],['walk',8],['attack',6],['hit',2],['death',4]])assert.equal(meta.states[s].length,n,t+' '+s);
 assert.deepEqual(meta,JSON.parse(fs.readFileSync(path.join(root,'www/assets/units3d',t+'.json'),'utf8')));
 const webp=fs.readFileSync(path.join(root,'www/assets/units3d',t+'.webp'));const sha=crypto.createHash('sha256').update(webp).digest('hex');
 assert.equal(sha,meta.atlasSha256);assert.equal(proof.atlas[t],sha);assert.equal(webp.toString('ascii',8,16),'WEBPVP8L');
 const bits=webp.readUInt32LE(21),w=(bits&16383)+1,h=((bits>>>14)&16383)+1;assert.ok(w*h<4.5e6,'atlas memory budget');
 for(const [x,y,fw,fh] of meta.f)assert.ok(x>=0&&y>=0&&x+fw<=w&&y+fh<=h,'frame inside atlas');
 const L=meta.locomotion.walk;assert.ok(Math.abs(L.phaseScale*L.strideTiles-2*Math.PI/5)<1e-5,'gallop cadence matches movement');
}
assert.match(html,/for\(const type of Object\.keys\(UNIT3D_CAV_DATA\)\)\{const source=\{ready:false,img:null,wide:true/);
console.log('PASS: 3D cavalry atlases (cavaleiro, cavPesada, cavArqueira)');
