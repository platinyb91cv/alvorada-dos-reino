// Atlas leves: o jogo carrega só as peças que ainda desenha (portões de madeira, paliçada, quinta e ruínas).
// Verifica: ficheiros e hashes, as mesmas medidas e âncoras do atlas completo, píxeis iguais (medidos ao gerar),
// e que tudo o que saiu é desenhado por arte mais nova (castelo modular e portões pintados).
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const proof=JSON.parse(fs.readFileSync(path.join(root,'arte/leve/verification.json'),'utf8')),src=n=>JSON.parse(fs.readFileSync(path.join(root,'arte/leve/fonte',n+'.json'),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),J=n=>JSON.parse(html.match(new RegExp('const '+n+'=(\\{[^\\n]+\\});'))[1]);
for(const n of ['GATE3D_DATA','WALL3D_DATA']){const d=J(n),full=src(n),p=proof[n];
 assert.equal(d.file,p.leve);assert.equal(d.atlasSha256,sha(path.join(root,'www/assets/edificios-extra',d.file)));assert.equal(p.leveSha256,d.atlasSha256);assert.equal(p.fonteSha256,full.atlasSha256);assert.equal(p.pixeisIguais,true);
 const kept=Object.keys(full.frames).filter(k=>k.startsWith('madeira'));assert.deepEqual(Object.keys(d.frames).sort(),kept.sort(),n+': só madeira, toda');
 for(const k of kept){assert.deepEqual(d.frames[k].slice(2),full.frames[k].slice(2),n+' '+k+': medidas/âncora');assert.deepEqual(p.mapa[k][0],full.frames[k].slice(0,4))}}
const C=J('CMOD_DATA').frames,PG=J('PGATE_DATA').frames;
for(const k of Object.keys(src('WALL3D_DATA').frames).filter(k=>!k.startsWith('madeira')))assert.ok(C[k],'muro de pedra/fortificado coberto pelo castelo modular: '+k);
for(const d of ['x','y'])for(const o of [0,1,2])assert.ok(PG[`pedra_${d}_${o}`],'portão de pedra coberto pelos portões pintados');
const m=JSON.parse(html.match(/const BLDART=\{wide:true,ready:false,img:null,meta:(\{[^\r\n]*\}),teams:new Map/)[1]),full=src('BLDART');
assert.deepEqual(Object.keys(m).sort(),['quinta|0','quinta|1','ruina|0','ruina|1']);for(const k in m){const {f,...r}=m[k],{f:f0,...r0}=full[k];assert.deepEqual(r,r0);assert.deepEqual(f.slice(2),f0.slice(2))}
const url=html.match(/im\.src='assets\/edificios-v2\/(bld-atlas-leve\.webp)\?v=([0-9a-f]{12})'/);assert.ok(url);assert.equal(sha(path.join(root,'www/assets/edificios-v2',url[1])).slice(0,12),url[2]);assert.equal(proof.BLDART.pixeisIguais,true);
assert.match(html,/const m=BLDART\.meta\[key\];if\(!m\)return null;/,'peças que saíram do atlas antigo não rebentam bldArt');
// memória: soma descodificada dos três
const mb=Object.values(proof).reduce((a,p)=>[a[0]+p.mbDescodificado[0],a[1]+p.mbDescodificado[1]],[0,0]);assert.ok(mb[1]<mb[0]*.4);
// reis e unidades raras: carregados quando são precisos e libertados quando deixam de aparecer
assert.match(html,/function kingAtlasForAge\(age\)\{return age===0&&u3ready\(BART\)\?BART:age===1&&u3ready\(BRONZE_ART\)/);
assert.match(html,/function atlasGC\(\)/);assert.match(html,/villageTick\(dt\);cartTick\(dt\);atlasGC\(\);/);
console.log('PASS atlas leves: '+mb[0].toFixed(1)+' MB -> '+mb[1].toFixed(1)+' MB descodificados, mesmas peças e âncoras, píxeis iguais; reis e unidades raras carregados/libertados conforme o uso');
