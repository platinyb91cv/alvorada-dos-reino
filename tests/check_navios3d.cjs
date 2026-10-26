// Navios 3D: 6 atlas de 8 direções, desenho na água (esteira/balanço) e afundar com a animação 3D.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const data=JSON.parse(html.match(/const UNIT3D_NAVAL_DATA=(\{[^\n]+\});/)[1]);const proof=JSON.parse(fs.readFileSync(path.join(root,'arte/navios-3d/verification.json'),'utf8'));
const T=['barcoPesca','transporte','gale','incendiario','navioPesado','corsario'];assert.deepEqual(Object.keys(data).sort(),[...T].sort());
const types=JSON.parse(html.match(/const UNIT3D_TYPES=(\[[^\]]+\]);/)[1].replace(/'/g,'"'));let px=0;
for(const t of T){assert.ok(types.includes(t),t);const m=data[t];assert.equal(m.directions,8);assert.equal(m.f.length,8*m.framesPerDirection);
 for(const [s,n] of [['idle',2],['walk',8],['attack',6],['hit',2],['death',4]])assert.equal(m.states[s].length,n,t+' '+s);
 const webp=fs.readFileSync(path.join(root,'www/assets/units3d',t+'.webp'));const sha=crypto.createHash('sha256').update(webp).digest('hex');assert.equal(sha,m.atlasSha256);assert.equal(proof.atlas[t],sha);
 const bits=webp.readUInt32LE(21),w=(bits&16383)+1,h=((bits>>>14)&16383)+1;px+=w*h;for(const [x,y,fw,fh] of m.f)assert.ok(x>=0&&y>=0&&x+fw<=w&&y+fh<=h);
 const rig=fs.readFileSync(path.join(root,'arte/navios-3d/modelos',t+'-rig.glb'));assert.equal(crypto.createHash('sha256').update(rig).digest('hex'),proof.riggados[t])}
assert.ok(px<6e6,'naval atlas memory budget');
assert.match(html,/else if\(e\.d\.naval\)\{if\(!drawShip3D\(c,v,p\.x,p\.y\)\)drawShip\(c,v,p\.x,p\.y\)\}/);
assert.match(html,/if\(e\.d\.trade\)\{if\(!drawUnit3D\(c,e,p\.x,p\.y\)\)drawCart\(c,e,p\.x,p\.y\)\}/);
assert.match(html,/else if\(f\.type==='sink'\)\{\{const src=UNIT3D\[f\.ut\];/);
console.log('PASS: 3D ships (6 types, water drawing, sinking)');
