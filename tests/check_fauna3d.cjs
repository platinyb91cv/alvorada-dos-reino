// Veado Meshy (tipo "gazela"): atlas de 8 direções, metadados embutidos, pastar, sem cor de equipa e carcaça 3D.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const data=JSON.parse(html.match(/const UNIT3D_FAUNA_DATA=(\{[^\n]+\});/)[1]);assert.deepEqual(Object.keys(data),['gazela']);
const types=JSON.parse(html.match(/const UNIT3D_TYPES=(\[[^\]]+\]);/)[1].replace(/'/g,'"'));assert.ok(types.includes('gazela'),'8-direction heading for the deer');
const proof=JSON.parse(fs.readFileSync(path.join(root,'arte/fauna-meshy/verification.json'),'utf8'));assert.equal(proof.creditosAdicionais,0);
const meta=data.gazela;
assert.equal(meta.directions,8);assert.equal(meta.f.length,8*meta.framesPerDirection);assert.deepEqual(meta.directionLabels,['SE','S','SW','W','NW','N','NE','E']);
for(const [s,n] of [['idle',2],['graze',4],['walk',8],['attack',4],['hit',2],['death',4]])assert.equal(meta.states[s].length,n,'gazela '+s);
assert.deepEqual(meta,JSON.parse(fs.readFileSync(path.join(root,'www/assets/units3d/gazela.json'),'utf8')));
const webp=fs.readFileSync(path.join(root,'www/assets/units3d/gazela.webp'));const sha=crypto.createHash('sha256').update(webp).digest('hex');
assert.equal(sha,meta.atlasSha256);assert.equal(proof.atlas.gazela,sha);
assert.equal(webp.toString('ascii',8,16),'WEBPVP8L');const bits=webp.readUInt32LE(21),w=(bits&16383)+1,h=((bits>>>14)&16383)+1;
for(const [x,y,fw,fh] of meta.f)assert.ok(x>=0&&y>=0&&x+fw<=w&&y+fh<=h,'frame inside atlas');
assert.ok(w*h<2.5e6,'deer atlas stays within a small memory budget');
const L=meta.locomotion.walk;assert.ok(Math.abs(L.phaseScale*L.strideTiles-2*Math.PI/5)<1e-5,'trot cadence matches movement');
const rig=fs.readFileSync(path.join(root,proof.riggado.ficheiro));assert.equal(crypto.createHash('sha256').update(rig).digest('hex'),proof.riggado.sha256);assert.ok(rig.length<20*1024*1024);
assert.match(html,/for\(const type of Object\.keys\(UNIT3D_FAUNA_DATA\)\)\{const source=\{ready:false,img:null,fauna:true/);
assert.match(html,/source\.fauna\?source\.img:unit3dTint\(source,team\)/,'no team recolor on wild animals');
assert.match(html,/if\(u\.o===2&&u\.state!=='attack'\)return [^\n]+'graze':'idle'/,'animals graze when idle');
assert.match(html,/carcass:true,walk:true,dir:e\.kingDir\?\?0\}/,'carcass keeps the death direction');
assert.match(html,/function carcass3D\(r,t\)/);assert.match(html,/if\(s3\)return s3\}if\(!FAUNA\.ready\)return null;/);
// a lógica de jogo continua determinística: o veado usa performance.now só no desenho
const step=html.slice(html.indexOf('function step('),html.indexOf('\n}',html.indexOf('function step(')));assert.ok(!/carcass3D|UNIT3D_FAUNA/.test(step));
console.log('PASS: Meshy deer atlas (8 directions, graze, trot cadence, 3D carcass)');
