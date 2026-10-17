const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const match=html.match(/const UNIT3D_DATA=(\{[^\n]+\});/);assert.ok(match,'Unit metadata missing');const data=JSON.parse(match[1]);
const types=['aldeao','guerreiro','lanceiro','espadachim','arqueiro','besteiro'];assert.deepEqual(Object.keys(data),types);
let pixels=0;
for(const type of types){const meta=data[type];assert.equal(meta.directions,8);assert.equal(meta.h,64);assert.equal(meta.f.length,8*meta.framesPerDirection);assert.equal(meta.states.walk.length,8);assert.equal(meta.states.attack.length,6);assert.equal(meta.states.death.length,4);
 assert.deepEqual(meta,JSON.parse(fs.readFileSync(path.join(root,'www/assets/units3d',type+'.json'),'utf8')));
 const webp=fs.readFileSync(path.join(root,'www/assets/units3d',type+'.webp'));assert.equal(meta.atlasSha256,crypto.createHash('sha256').update(webp).digest('hex'));assert.equal(webp.toString('ascii',0,4),'RIFF');assert.equal(webp.toString('ascii',8,16),'WEBPVP8L');assert.equal(webp[20],47);const bits=webp.readUInt32LE(21),width=(bits&16383)+1,height=((bits>>>14)&16383)+1;assert.ok(width<=4096&&height<=8192);pixels+=width*height;
 for(const f of meta.f){assert.equal(f.length,6);assert.ok(f.every(Number.isFinite));const[x,y,w,h,ax,ay]=f;assert.ok(x>=0&&y>=0&&w>0&&h>0&&x+w<=width&&y+h<=height);assert.ok(Math.abs(ax)<width&&Math.abs(ay)<height)}
 for(const ids of Object.values(meta.states))assert.ok(ids.length&&ids.every(i=>Number.isInteger(i)&&i>=0&&i<meta.framesPerDirection));
 const proof=JSON.parse(fs.readFileSync(path.join(root,'arte/unidades3d',type+'.verification.json'),'utf8'));assert.equal(proof.reimported,true);assert.equal(proof.reimportedClipsDistinct,true);assert.ok(Object.values(proof.reimportedRootDriftByClip).every(v=>v<1e-4));if(type==='arqueiro'||type==='besteiro')assert.ok(proof.forwardAimDot>.9);assert.ok(proof.triangles<8000&&proof.bones>=24&&proof.rootHorizontalDrift<1e-4);assert.ok(Object.values(proof.stanceVelocityY).every(v=>v>0));assert.ok(Object.values(proof.rigidProps).every(v=>v<1e-4));
}
assert.ok(pixels<10000000,'Atlas set exceeded decoded image budget');
function fn(name){const start=html.indexOf('function '+name+'(');assert.ok(start>=0,name);const end=html.indexOf('\nfunction ',start+1);return html.slice(start,end)}
const drawCalls=[],scaleCalls=[],sources=Object.fromEntries(types.map(type=>[type,{ready:true,img:{type},teams:new Map(),meta:data[type]}]));
sources.besteiroPesado=sources.besteiro;
const ctx={Math,Number,UNIT3D_HEIGHT:30,UNIT3D_TYPES:types,UNIT3D:sources,P:[{col:'#3366cc'}],performance:{now:()=>1000},atkPhase:()=>.5,distTo:(u,t)=>Math.hypot(t.x-u.x,t.y-u.y),rectOf:t=>t.kind==='u'?{x:t.x-.5,y:t.y-.5,w:1,h:1}:{x:t.tx,y:t.ty,w:t.w||1,h:t.h||1},recolorImg:(source,team)=>{if(!source.teams.has(team))source.teams.set(team,{...source.img,team});return source.teams.get(team)}};
for(const name of ['kingDirFromDelta','kingDirection','unit3dHeading','unit3dDeathDirection','unit3dState','unit3dFrame','unit3dTint','drawUnit3dFrame','drawUnit3D','drawUnit3DCorpse'])ctx[name]=vm.runInNewContext('('+fn(name)+'\n)',ctx);
const canvas={save(){},restore(){},translate(){},scale(...a){scaleCalls.push(a)},beginPath(){},ellipse(){},fill(){},drawImage(...a){drawCalls.push(a)}};
const vectors=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]];
for(const type of types)for(const [direction,[dx,dy]]of vectors.entries()){
 const u={type,o:0,id:1,x:0,y:0,anim:Math.PI,face:-1,kingDir:direction,path:[{x:dx,y:dy}],pi:0,d:{},state:'move',hitT:0};
 assert.equal(ctx.unit3dHeading(u),direction);assert.equal(ctx.unit3dState(u),'walk');assert.equal(ctx.drawUnit3D(canvas,u,10,20),true);assert.equal(drawCalls.at(-1)[0].type,type);
 const i=ctx.unit3dFrame(u,'walk',data[type]);assert.deepEqual(drawCalls.at(-1).slice(1,5),data[type].f[direction*data[type].framesPerDirection+i].slice(0,4));
 u.path=[];u.state='idle';assert.equal(ctx.unit3dHeading(u),direction);assert.equal(ctx.unit3dState(u),'idle');
 u.state='attack';u.target={kind:'u',x:dx*.3,y:dy*.3,o:1};assert.equal(ctx.unit3dHeading(u),direction);assert.equal(ctx.unit3dState(u),'attack');
 assert.equal(ctx.drawUnit3DCorpse(canvas,{ut:type,o:0,kingDir:direction,life:10,t:.5},{x:0,y:0}),true);
 const death=data[type].states.death[Math.min(3,Math.floor(.5/.7*4))];assert.deepEqual(drawCalls.at(-1).slice(1,5),data[type].f[direction*data[type].framesPerDirection+death].slice(0,4));
}
assert.equal(scaleCalls.length,0,'Never mirror directional weapons');
const vill={type:'aldeao',o:0,id:1,x:0,y:0,path:[],pi:0,d:{},anim:Math.PI,kingDir:5,hitT:0};
for(const [state,kind,resource,expected]of [['gather','wood',{kind:'r',tx:2,ty:2},'chop'],['gather','gold',{kind:'r',tx:2,ty:2},'mine'],['gather','stone',{kind:'r',tx:2,ty:2},'mine'],['gather','food',{kind:'b',tx:2,ty:2},'farm'],['gather','food',{kind:'r',tx:2,ty:2},'forage'],['gather','food',{kind:'r',carcass:true,tx:2,ty:2},'butcher'],['build',null,null,'build']]){
 const u={...vill,state,gkind:kind,gres:resource,bld:{tx:2,ty:2}};assert.equal(ctx.unit3dState(u),expected);assert.equal(ctx.unit3dHeading(u),1);assert.ok(data.aldeao.states[expected]);
}
assert.equal(ctx.unit3dState({...vill,state:'move',path:[{x:1,y:0}],carry:5}),'carry');assert.equal(ctx.unit3dState({...vill,state:'attack',target:{o:2}}),'hunt');
for(const type of types){sources[type].ready=false;assert.equal(ctx.drawUnit3D(canvas,{type},0,0),false);assert.equal(ctx.drawUnit3DCorpse(canvas,{ut:type},{x:0,y:0}),false);sources[type].ready=true;}
assert.equal(ctx.drawUnit3D(canvas,{type:'besteiroPesado',o:0,id:1,x:0,y:0,path:[],pi:0,kingDir:3,anim:0,state:'idle'},0,0),true);assert.equal(drawCalls.at(-1)[0].type,'besteiro');
assert.equal(ctx.drawUnit3D(canvas,{type:'cavaleiro'},0,0),false);assert.equal(ctx.drawUnit3DCorpse(canvas,{ut:'rei'},{x:0,y:0}),false);
console.log(JSON.stringify({units:types,directions:8,resourceJobs:true,deathHeading:true,loadingFallback:true,noMirroring:true,decodedAtlasPixels:pixels}));

// Orientation persists through the real final waypoint and save/continue functions.
ctx.UNIT3D_TYPES=[...types,'besteiroPesado'];ctx.hyp=Math.hypot;ctx.physSpeed=()=>1;ctx.stepOK=()=>true;ctx.spawnFx=()=>{};
ctx.faceTo=vm.runInNewContext('('+fn('faceTo')+'\n)',ctx);const follow=vm.runInNewContext('('+fn('follow')+'\n)',ctx);
for(const type of ctx.UNIT3D_TYPES)for(const [direction,[dx,dy]]of vectors.entries()){
 const u={type,x:0,y:0,d:{cls:'inf',speed:1},path:[{x:dx*.03,y:dy*.03}],pi:0,anim:0};assert.equal(follow(u,.1),true);assert.equal(u.kingDir,direction);
}
const saveCtx={JSON,Math,difficulty:0,nid:1,G:{seed:1,time:0,starts:[]},gExtra:()=>({}),P:[],W:0,terr:[],vis:[],byId:new Map(),AIs:[],cam:{},ents:[],UNIT3D_TYPES:ctx.UNIT3D_TYPES};const serialize=vm.runInNewContext('('+fn('serialize')+'\n)',saveCtx);
const ma=html.indexOf('const mkU=(q,push)=>'),mb=html.indexOf("  for(const q of d.ents.filter(x=>x.k==='u'))",ma),restoreCtx={Number,Math,nid:0,ents:[],byId:new Map(),pend:[],UNIT3D_TYPES:ctx.UNIT3D_TYPES,mkUnit:(o,type)=>({d:{},type,id:1})};const restore=vm.runInNewContext('(function(){'+html.slice(ma,mb)+';return mkU})()',restoreCtx);
for(const type of ctx.UNIT3D_TYPES)for(let direction=0;direction<8;direction++){saveCtx.ents=[{kind:'u',id:1,o:0,type,d:{},x:2,y:3,hp:30,state:'idle',kingDir:direction}];const q=JSON.parse(serialize()).ents[0];assert.equal(q.kd,direction);assert.equal(restore(q,true).kingDir,direction)}
console.log('PASS: all new units retain eight directions through movement and save/continue');

for(const team of ['#112233','#223344','#334455','#445566'])ctx.unit3dTint(sources.aldeao,team);assert.equal(sources.aldeao.teams.size,3);assert.ok(sources.aldeao.teams.has('#445566'));console.log('PASS: per-unit team texture cache bounded to three variants');

assert.equal(ctx.unit3dState({...vill,state:'idle',carry:5}),'carryIdle');assert.equal(data.aldeao.states.carryIdle.length,1);console.log('PASS: stopped villager retains resource crate');

assert.equal(ctx.unit3dState({type:'guerreiro',state:'attack',target:{x:5,y:0},x:0,y:0,d:{range:0},path:[]}), 'idle');assert.equal(ctx.unit3dState({type:'arqueiro',state:'attack',target:{x:5,y:0},x:0,y:0,d:{range:6},path:[]}), 'attack');console.log('PASS: melee/ranged attack visual conditions preserved');

// Capture the current work/attack facing, rather than a stale path heading.
for(const [direction,[dx,dy]]of vectors.entries()){
 const u={...vill,state:'gather',kingDir:(direction+4)%8,gres:{kind:'r',tx:dx-.5,ty:dy-.5,w:1,h:1}};
 assert.equal(ctx.unit3dDeathDirection(u),direction);
 ctx.drawUnit3DCorpse(canvas,{ut:'aldeao',o:0,kingDir:ctx.unit3dDeathDirection(u),life:10,t:.5},{x:0,y:0});
 const ids=data.aldeao.states.death,i=ids[Math.min(ids.length-1,Math.floor(.5/.7*ids.length))];assert.deepEqual(drawCalls.at(-1).slice(1,5),data.aldeao.f[direction*data.aldeao.framesPerDirection+i].slice(0,4));
}
assert.match(html,/kingDir:unit3dDeathDirection\(e\),ut:e.type/);console.log('PASS: death preserves the actual resource-facing direction');

// Exercise the actual world dispatchers, not only the new drawing helpers.
const delegated=[];const dispatchCtx={...ctx,UNIT_SCALE:Number(html.match(/const UNIT_SCALE=([\d.]+)/)[1]),drawUnit3D:(c,u,x,y)=>{delegated.push(u.type);return !!sources[u.type]&&sources[u.type].ready},uTier:()=>1,cavFrame:()=>({cv:{legacy:true},ax:0,ay:0,w:10,h:10}),darkOf:x=>x,UNITS:{cavaleiro:{cls:'cav'}},KART:{ready:true},drawKingCorpse(){},corpseUnit:f=>({type:f.ut,d:{cls:'cav'},face:1})};
const drawWorld=vm.runInNewContext('('+fn('drawUnit')+'\n)',dispatchCtx);
for(const type of ctx.UNIT3D_TYPES){drawWorld(canvas,{type,o:0},10,20);assert.equal(delegated.at(-1),type)}
drawWorld(canvas,{type:'cavaleiro',o:0,id:1,state:'idle',d:{cls:'cav'},face:1,path:[],pi:0,hitT:0},10,20);assert.equal(drawCalls.at(-1)[0].legacy,true);
const corpseDelegated=[];dispatchCtx.drawUnit3DCorpse=(c,f)=>{corpseDelegated.push(f.ut);return !!sources[f.ut]&&sources[f.ut].ready};const drawWorldCorpse=vm.runInNewContext('('+fn('drawCorpse')+'\n)',dispatchCtx);
for(const type of ctx.UNIT3D_TYPES){drawWorldCorpse(canvas,{ut:type,o:0},{x:0,y:0});assert.equal(corpseDelegated.at(-1),type)}
canvas.rotate=()=>{};drawWorldCorpse(canvas,{ut:'cavaleiro',o:0,life:10,t:.5},{x:0,y:0});assert.equal(drawCalls.at(-1)[0].legacy,true);
console.log('PASS: world living/death dispatchers select new units and retain legacy cavalry');
