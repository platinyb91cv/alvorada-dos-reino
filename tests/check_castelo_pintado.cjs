// Portão de pedra e torre de nível 3 pintados (arte/pintura-castelo): 2 direções x 3 estados, sha certo, ganchos no jogo,
// muros debaixo das torres escondidos (bit 256) e alturas dos soldados vindas da pintura.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const d=JSON.parse(html.match(/const PGATE_DATA=(\{[^\n]+\});/)[1]);
for(const dir of ['x','y'])for(const st of [0,1,2])assert.ok(d.frames['pedra_'+dir+'_'+st],'frame '+dir+st);
const webp=fs.readFileSync(path.join(root,'www/assets/edificios-extra',d.file));assert.equal(crypto.createHash('sha256').update(webp).digest('hex'),d.atlasSha256);
assert.ok(d.walk>1.2&&d.walk<1.6,'caminho de ronda à altura das muralhas');assert.ok(d.span>=1&&d.span<=2.5,'torres a 1-2,5 casas do portão');assert.ok(d.towerTop>d.walk,'torres mais altas');
assert.match(html,/if\(type==='portaoPedra'&&PGATE\.ready\)/);assert.match(html,/if\(e\.d\.wall&&PGATE\.ready&&\(bldVariant\(e\)&256\)\)\{c\.save\(\);if\(pgateWallClip\(c,e\)!=='skip'\)/,'muro da frente recortado na torre');assert.match(html,/if\(e\.type==='torre'\)towerWallStubs\(c,e,false,lit\)/,'muros entram na torre redonda');assert.match(html,/\[0,2\.22,2\.45,3\.3\]/,'varanda da torre redonda');assert.ok(d.rTorre>.2&&d.rTorre<.8);
assert.match(html,/if\(e\.type==='portaoPedra'\)return PGATE\.meta\.walk;if\(e\.d\.wall\)\{const v=bldVariant\(e\);if\(v&768\)/);
for(const f of ['fonte/portao_v2.png','fonte/torre_v2.png','scripts/portao_pintado.py','scripts/torre_pintada.py'])assert.ok(fs.existsSync(path.join(root,'arte/pintura-castelo',f)),f);
console.log('PASS: castelo pintado ('+Object.keys(d.frames).length+' quadros, '+(webp.length/1024|0)+' KB)');
