// Vida da aldeia 2: profissões, formações com vantagens, caravanas (escolta/emboscada) e vilas neutras.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
function fn(name){const start=html.indexOf('function '+name+'(');assert.ok(start>=0,name);const ends=['\nfunction ','\nconst ','\n//','\nlet '].map(k=>html.indexOf(k,start+1)).filter(i=>i>0);return html.slice(start,Math.min(...ends))}
const ctx={Math,hyp:Math.hypot,alive:e=>!!e&&!e.dead,isPasture:r=>!!r&&r.kind==='u'&&r.o===2&&r.type==='ovelha',ents:[],G:{time:0},byId:new Map(),centerOf:e=>e.kind==='u'?{x:e.x,y:e.y}:{x:e.tx+e.w/2,y:e.ty+e.h/2}};
for(const n of ['villJob','jobCounts','isSpear','isShooter','formTick','formArm','flankBonus','escorted','caravanLoot','tradeGain'])ctx[n]=vm.runInNewContext('('+fn(n)+'\n)',ctx);
// profissões
const V=(state,extra)=>({kind:'u',o:0,type:'aldeao',state,...extra});
assert.equal(ctx.villJob(V('gather',{gkind:'wood'})),'lenhador');assert.equal(ctx.villJob(V('return',{gkind:'gold'})),'mineiro');assert.equal(ctx.villJob(V('gather',{gkind:'stone'})),'pedreiro');
assert.equal(ctx.villJob(V('gather',{gkind:'food',gres:{kind:'b',d:{farm:1}}})),'agricultor');assert.equal(ctx.villJob(V('gather',{gkind:'food',gres:{kind:'r',carcass:true}})),'cacador');
assert.equal(ctx.villJob(V('herd')),'pastor');assert.equal(ctx.villJob(V('gather',{gkind:'food',gres:{kind:'u',o:2,type:'ovelha'}})),'pastor');
assert.equal(ctx.villJob(V('build')),'construtor');assert.equal(ctx.villJob(V('idle')),'ocioso');assert.equal(ctx.villJob({type:'guerreiro'}),null);
// formações
const U=(o,type,cls,x,y,d={})=>({kind:'u',o,type,x,y,state:'idle',d:{mil:1,cls,range:0,...d}});
const arch=U(0,'arqueiro','arch',10,10,{range:6}),spear=U(0,'lanceiro','inf',11,10,{bonus:{cav:4}}),lone=U(0,'arqueiro','arch',30,30,{range:6});
const line=[0,1,2].map(i=>U(0,'guerreiro','inf',10+i*.9,14)),foe=U(1,'lanceiro','inf',11,10.5,{bonus:{cav:4}});
ctx.ents=[arch,spear,lone,...line,foe];ctx.G.time=1;ctx.G.formQ=-1;ctx.formTick();
assert.equal(arch.fb&1,1,'archer protected by spearman');assert.equal(lone.fb,0);assert.ok(line.every(u=>u.fb&2),'three infantry in line');
assert.equal(ctx.formArm(arch,false),2);assert.equal(ctx.formArm(arch,true),0,'protection is against melee only');assert.equal(ctx.formArm(line[1],true),1);
const moving={...line[0],path:[{x:0,y:0}],pi:0,state:'move'};ctx.ents=[moving,line[1],line[2]];ctx.G.formQ=-1;ctx.formTick();assert.equal(moving.fb,0,'moving infantry gets no line bonus');
const cav=U(0,'cavaleiro','cav',0,0),busy={...U(1,'guerreiro','inf',1,0),state:'attack',target:line[0]};
assert.equal(ctx.flankBonus(cav,busy),3);assert.equal(ctx.flankBonus(cav,{...busy,target:cav}),0);assert.equal(ctx.flankBonus(spear,busy),0);
// caravanas
const cart={kind:'u',o:0,x:5,y:5,d:{trade:1},tradeA:1,tradeB:2};ctx.byId=new Map([[1,{kind:'b',tx:0,ty:0,w:3,h:3}],[2,{kind:'b',tx:40,ty:0,w:3,h:3}]]);
assert.equal(ctx.caravanLoot(cart),Math.max(40,Math.round(ctx.tradeGain(40)*.6)));
ctx.ents=[cart];assert.equal(ctx.escorted(cart),false);ctx.ents=[cart,U(0,'guerreiro','inf',6,6)];assert.equal(ctx.escorted(cart),true);
// vilas neutras: definição, regras e ligações no jogo
assert.ok(html.includes("vila:{name:'Vila neutra',icon:'🏘️',w:3,h:3,hp:600,cost:{},time:0,age:9,sight:5,garr:5,pop:5,neutral:1}"));assert.match(html,/const VILA_CLAIM=20,VILA_SWAP=30,VILA_R=4\.5;/);
assert.match(html,/relicTick\(dt\);natureTick\(dt\);formTick\(\);villageTick\(dt\);/,'ticks run inside the deterministic step');
assert.match(html,/formArm\(t,ranged\)/);assert.match(html,/dmg\+=flankBonus\(src,t\);/);assert.match(html,/spawnVillages\(\);/);
assert.match(html,/if\(escorted\(u\)\)\{g=Math\.round\(g\*1\.25\)/);assert.match(html,/const g=caravanLoot\(e\);P\[src\.o\]\.res\.gold\+=g;/);
assert.match(html,/e\.type==='vila'&&\(e\.o===o\|\|e\.o===2\)/,'carts can trade with neutral/allied villages');
for(const n of ['spawnVillages','villageTick','vilaSprite','vilaInfo','idleProducers'])assert.ok(html.includes('function '+n+'('),n);
assert.doesNotMatch(fn('villageTick')+fn('formTick')+fn('spawnVillages'),/Math\.random|performance\.now|Date\.now/,'gameplay ticks stay deterministic for online play');
console.log('PASS: professions, formation armour/flank bonuses, caravan escort/ambush and neutral villages');
