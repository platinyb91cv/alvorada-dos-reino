// Muralhas 3D: 3 tipos × 16 máscaras, atlas verificado e gancho em bldSprite.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(root,'arte/leve/fonte/WALL3D_DATA.json'),'utf8')); // atlas completo (fonte); o jogo carrega a versão leve: tests/check_atlas_leve.cjs
const proof=JSON.parse(fs.readFileSync(path.join(root,'arte/muralhas-3d/verification.json'),'utf8'));assert.equal(proof.creditosAdicionais,0);
const webp=fs.readFileSync(path.join(root,'www/assets/edificios-extra',data.file));const sha=crypto.createHash('sha256').update(webp).digest('hex');
assert.equal(sha,data.atlasSha256);assert.equal(sha,proof.atlas.sha256);assert.equal(webp.toString('ascii',8,16),'WEBPVP8L');
const bits=webp.readUInt32LE(21),w=(bits&16383)+1,h=((bits>>>14)&16383)+1;assert.ok(w*h<=2048*2048);assert.ok(webp.length<2e6,'atlas size budget (108 pieces: 48 + variants that stop at the gatehouse)');
let n=0;for(const t of ['madeira','pedra','fort'])for(let m=0;m<16;m++){const f=data.frames[`${t}_${m}`];assert.ok(f,`${t}_${m}`);const [x,y,fw,fh,ax,ay]=f;n++;
 assert.ok(x>=0&&y>=0&&x+fw<=w&&y+fh<=h);assert.ok(fw<=72,'piece stays inside its screen column (+3 px of overlap each side)');assert.ok(ax>=0&&ax<=fw&&ay>0&&ay<=fh+40)}
assert.equal(n,48);
assert.match(html,/const WALL3D_KIND=\{muralhaMadeira:'madeira',muralhaPedra:'pedra',muralhaFort:'fort'\};/);
assert.match(html,/if\(BLDS\[type\]\.wall\)\{const w3=wall3dSprite\(type,o,vr\);if\(w3\)return w3\}/);
console.log('PASS: 3D walls (3 types × 16 joins)');
