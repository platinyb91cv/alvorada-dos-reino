// Portões 3D: 5 variantes × 2 direções × 3 estados de porta, atlas verificado e ganchos de desenho.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(root,'arte/leve/fonte/GATE3D_DATA.json'),'utf8')); // atlas completo (fonte); o jogo carrega a versão leve: tests/check_atlas_leve.cjs
const proof=JSON.parse(fs.readFileSync(path.join(root,'arte/portoes-3d/verification.json'),'utf8'));
assert.equal(proof.creditosAdicionais,0);
const webp=fs.readFileSync(path.join(root,'www/assets/edificios-extra',data.file));const sha=crypto.createHash('sha256').update(webp).digest('hex');
assert.equal(sha,data.atlasSha256);assert.equal(sha,proof.atlas.sha256);
assert.equal(webp.toString('ascii',8,16),'WEBPVP8L');const bits=webp.readUInt32LE(21),w=(bits&16383)+1,h=((bits>>>14)&16383)+1;
assert.ok(w<=2048&&h<=2048,'atlas within 2048');assert.ok(webp.length<1.6e6,'atlas size budget');
let n=0;for(const v of ['madeira0','madeira1','madeira2','pedra1','pedra2'])for(const d of ['x','y'])for(const o of [0,1,2]){
 const f=data.frames[`${v}_${d}_${o}`];assert.ok(f,`frame ${v}_${d}_${o}`);const [x,y,fw,fh,ax,ay]=f;n++;
 assert.ok(x>=0&&y>=0&&x+fw<=w&&y+fh<=h,'frame inside atlas');assert.ok(ax>0&&ax<fw&&ay>0&&ay<fh,'anchor inside frame')}
assert.equal(n,30);assert.equal(Object.keys(data.frames).length,30);
assert.match(html,/function gate3dSprite\(type,age,o,vr,op\)/);
assert.match(html,/e\.d\.gate&&e\.done&&gate3dSprite\(e\.type,P\[e\.o\]\.age,e\.o,bldVariant\(e\),Math\.round\(\(e\.open\|\|0\)\*2\)\)/,'door state follows e.open');
assert.match(html,/if\(BLDS\[type\]\.gate\)\{const g3=gate3dSprite\(type,age,o,vr,0\);if\(g3\)return g3\}/);
assert.match(html,/if\(e\.d\.gate&&!BLDART\.ready&&!GATE3D\.ready\)drawGateDoor/);
assert.match(html,/portaoMadeira:66,portaoPedra:80,/,'taller gates');
console.log('PASS: 3D gates (5 variants, 2 directions, 3 door states)');
