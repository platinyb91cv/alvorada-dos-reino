// Regressão das defesas: alturas coerentes entre os modelos do Blender e o jogo, câmara à escala certa, âncora dos muros
// calculada com a câmara já rodada, peças de muro que param na face do portão, e soldados em cima à altura do adarve.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const rd=p=>fs.readFileSync(path.join(root,p),'utf8').replace(/\r\n/g,'\n');
const muro=rd('arte/muralhas-3d/scripts/montar_muro.py'),port=rd('arte/portoes-3d/scripts/montar_portao2.py'),edif=rd('arte/edificios-3d/scripts/montar_edificios.py');
// 1) câmara: a escala ortográfica aplica-se à largura (com 'AUTO' aplicava-se à altura e tudo saía 5-11% maior que as casas)
assert.match(port,/cam\.data\.sensor_fit = 'HORIZONTAL'; cam\.data\.ortho_scale = RES\[0\] \/ PXU/);
// 2) âncora dos muros projetada depois de atualizar a cena (antes ficava no centro da casa: muro 16 px acima do chão)
assert.ok(muro.indexOf('sc.view_layers[0].update()')>=0&&muro.indexOf('sc.view_layers[0].update()')<muro.indexOf('a = world_to_camera_view(sc, cam, Vector((0, 0, 0)))'));
// 3) alturas de referência iguais nos modelos e no jogo (TOPZ = altura do adarve onde ficam os soldados)
const H=muro.match(/T = \.64 if fort else \.56; H = ([\d.]+) if fort else ([\d.]+)/);assert.deepEqual([+H[1],+H[2]],[1.5,1.3]);
const gp=port.match(/Hb = \(0, ([\d.]+), ([\d.]+)\)\[age\]; dz = \.82; x0, x1, y0, y1 = -\.28, 1\.28, \.04, \.96/);assert.deepEqual([+gp[1],+gp[2]],[1.8,2.0]);
const gm=port.match(/Hb = \(([\d.]+), ([\d.]+), ([\d.]+)\)\[age\]; dz = \.82; x0, x1, y0, y1 = -\.28, 1\.28, \.06, \.94/);assert.deepEqual([+gm[1],+gm[2],+gm[3]],[1.35,1.65,1.8]);
assert.match(edif,/        H = 2\.45\n/);assert.match(edif,/        Hb = 1\.3; H = 2\.85\n/,'round tower base at wall height');
assert.match(html,/return \(e\.type==='muralhaFort'\?1\.5:1\.3\)\+\(tw\?\.44:0\)/);
assert.match(html,/if\(e\.type==='portaoPedra'\)return \(P\[e\.o\]&&P\[e\.o\]\.age>=2\)\?2\.0:1\.8;/);
assert.match(html,/if\(e\.type==='portaoMadeira'\)return \[1\.28,1\.65,1\.8\]/);
assert.match(html,/if\(e\.type==='torre'\)return \[0,2\.22,2\.45,2\.98\]\[e\.lvl\|\|1\]/);
assert.match(html,/const ZP=HW\*2\/Math\.SQRT2\*Math\.cos\(Math\.PI\/6\); \/\/ píxeis/,'no leftover render-scale fudge factor');
// 4) muro ao lado da casa do portão: variantes renderizadas e escolhidas no jogo
const W=JSON.parse(html.match(/const WALL3D_DATA=(\{[^\n]+\});/)[1]).frames;
for(const t of ['pedra','fort','madeira'])for(let m=0;m<16;m++){assert.ok(W[t+'_'+m],t+'_'+m);if(m&4)assert.ok(W[t+'_'+m+'_g4'],t+'_'+m+'_g4');if(m&8)assert.ok(W[t+'_'+m+'_g8'],t+'_'+m+'_g8')}
assert.match(html,/if\(\(m&4\)&&gAt\(e\.tx-1,e\.ty,'x'\)\)m\|=64;if\(\(m&8\)&&gAt\(e\.tx,e\.ty-1,'y'\)\)m\|=128;/);
assert.match(html,/fk=gb&&F\[base\+'_g'\+gb\]\?base\+'_g'\+gb:base/);
// 5) soldados em cima desenhados com o próprio edifício (as torres da frente tapam-nos)
assert.match(html,/if\(lit&&e\.garr&&e\.garr\.length\)drawGarrTop\(c,e,performance\.now\(\)\/1000\);/);
assert.match(html,/    if\(top3\)continue; \/\/ desenhados com o próprio edifício/);
console.log('PASS: defesas (escala da câmara, âncoras, alturas modelo=jogo, muros que param no portão, soldados no adarve)');
