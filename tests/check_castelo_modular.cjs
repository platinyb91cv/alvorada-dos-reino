// Conjunto modular (arte/castelo-modular): uma cena do Blender, mesma escala por casa, sem sombra de chão.
// Verifica peças (16 máscaras x pedra/fortificada + variantes junto a portões), torre e pedaços de muro dentro da torre,
// sha do atlas, medidas comuns, âncoras dentro das peças, pontos de ligação e os ganchos no jogo.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const d=JSON.parse(html.match(/const CMOD_DATA=(\{[^\n]+\});/)[1]);
assert.equal(d.block,false,'atlas final (não a montagem de teste)');
for(const tp of ['pedra','fort'])for(let m=0;m<16;m++){assert.ok(d.frames[tp+'_'+m],'peça '+tp+'_'+m);if(m&4)assert.ok(d.frames[tp+'_'+m+'_g4']);if(m&8)assert.ok(d.frames[tp+'_'+m+'_g8'])}
assert.ok(d.frames.torre3,'torre');const tw=Object.keys(d.frames).filter(k=>k.startsWith('tw_'));assert.ok(tw.length>=8,'pedaços dentro da torre: '+tw.length);
assert.equal(d.H.pedra,1.3);assert.equal(d.towerFloor,3.3);assert.equal(d.towerR*2,1.7);
const webp=fs.readFileSync(path.join(root,'www/assets/edificios-extra',d.file));assert.equal(crypto.createHash('sha256').update(webp).digest('hex'),d.atlasSha256);
const bits=webp.readUInt32LE(21),w=(bits&16383)+1,h=((bits>>>14)&16383)+1;assert.ok(w<=2048&&h<=2048);
for(const [k,[x,y,fw,fh,ax,ay]] of Object.entries(d.frames)){assert.ok(x>=0&&y>=0&&x+fw<=w&&y+fh<=h,'dentro '+k);if(!k.startsWith('tw_')&&k!=='torre3')assert.ok(ax>0&&ax<fw,'âncora '+k)}
assert.ok(d.links.pedra_15&&['px','py','mx','my'].every(s=>d.links.pedra_15[s]),'ligações da cruz');
const v=JSON.parse(fs.readFileSync(path.join(root,'arte/castelo-modular/verification.json'),'utf8'));assert.equal(v.atlasSha256,d.atlasSha256);assert.equal(v.sombraDeChao,false);
const sc=fs.readFileSync(path.join(root,'arte/castelo-modular/scripts/montar_modular.py'),'utf8');
assert.match(sc,/is_shadow_catcher/,'apanha-sombras retirado');assert.match(sc,/ShaderNodeHoldout/,'torre como recorte');assert.match(sc,/R\(30\)/);
assert.match(html,/if\(CMOD\.ready&&CMOD_KIND\[type\]\)/,'muros usam o conjunto modular');assert.match(html,/cmodSprite\('tw_'\+CMOD_KIND\[n\.type\]\+'_'\+k/,'pedaços da torre');
assert.match(html,/return\[0,2\.22,2\.45,3\.3\]|\[0,2\.22,2\.45,3\.3\]/);
console.log('PASS: castelo modular ('+Object.keys(d.frames).length+' peças, '+w+'x'+h+', '+(webp.length/1024|0)+' KB)');
