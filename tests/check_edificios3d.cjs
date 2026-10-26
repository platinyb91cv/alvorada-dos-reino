// Edifícios 3D (Blender): atlas BLD3D por tipo e idade (torre por nível), quadros dentro do atlas, sha igual, gancho no bldSprite.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const data=JSON.parse(html.match(/const BLD3D_DATA=(\{[^\n]+\});/)[1]);
const want={casa:[0,1,2],armazem:[0,1,2],quartel:[0,1,2],arquearia:[0,1,2],estabulo:[0,1,2],doca:[0,1,2],torre:[1,2,3],ferreiro:[0,1,2],templo:[1,2],mercado:[1,2],oficina:[1,2],centro:[0,1,2],maravilha:[2]};
let n=0;for(const [t,ages] of Object.entries(want))for(const a of ages){assert.ok(data.frames[t+'_'+a],'frame '+t+'_'+a);n++}
assert.equal(Object.keys(data.frames).length,n);
const webp=fs.readFileSync(path.join(root,'www/assets/edificios-extra',data.file));assert.equal(crypto.createHash('sha256').update(webp).digest('hex'),data.atlasSha256);
assert.equal(webp.toString('ascii',8,16),'WEBPVP8L');const bits=webp.readUInt32LE(21),w=(bits&16383)+1,h=((bits>>>14)&16383)+1;
assert.ok(w<=2048&&h<=2048,'atlas within 2048');assert.ok(webp.length<4*1024*1024,'atlas size budget');
for(const [k,[x,y,fw,fh,ax,ay]] of Object.entries(data.frames)){assert.ok(x>=0&&y>=0&&x+fw<=w&&y+fh<=h,'inside '+k);assert.ok(ax>0&&ax<fw&&ay>0&&ay<fh,'anchor inside '+k)}
const proof=JSON.parse(fs.readFileSync(path.join(root,'arte/edificios-3d/verification.json'),'utf8'));assert.equal(proof.atlasSha256,data.atlasSha256);assert.equal(proof.creditosMeshy,0);
assert.match(html,/if\(BLDS\[type\]\.wall\)\{const w3=wall3dSprite\(type,o,vr\);if\(w3\)return w3\}\n  if\(type==='torre'&&\(vr\|0\)===3&&CMOD\.ready\)\{const t3=cmodSprite\('torre3',o\);if\(t3\)return t3\}\n  \{const b3=bld3dSprite\(type,age,o,vr\);if\(b3\)return b3\}/,'3D building hook before painted art');
assert.match(html,/if\(type==='torre'\)\{const l=Math\.max\(1,Math\.min\(3,vr\|0\|\|1\)\)/,'tower picks level');
const step=html.slice(html.indexOf('function step('),html.indexOf('\n}',html.indexOf('function step(')));assert.ok(!/bld3d|BLD3D/.test(step),'drawing only');
console.log('PASS: 3D buildings atlas ('+n+' frames, '+w+'x'+h+', '+(webp.length/1024|0)+' KB)');
