const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../www/index.html'),'utf8');
function source(name){const a=html.indexOf('function '+name+'('),b=html.indexOf('\nfunction ',a+1);assert.ok(a>=0&&b>a,name);return html.slice(a,b)}
function def(name){const match=html.match(new RegExp('\\n  '+name+':(\\{[^\\n]+\\}),'));assert.ok(match,name);return vm.runInNewContext('('+match[1]+')')}
const N=32,ctx=vm.createContext({Math,Number,Map,Float32Array,Int32Array,Array,DataView,ArrayBuffer,
 W:N,H:N,idx:(x,y)=>y*N+x,inb:(x,y)=>x>=0&&y>=0&&x<N&&y<N,hyp:Math.hypot,clamp:(v,a,b)=>Math.max(a,Math.min(b,v)),
 terr:new Uint8Array(N*N),blk:new Uint8Array(N*N),bldAt:new Int32Array(N*N),resAt:new Array(N*N).fill(null),vis:new Uint8Array(N*N).fill(2),
 BLDS:{estrada:def('estrada'),curral:def('curral')},UNITS:{aldeao:def('aldeao'),ovelha:def('ovelha')},G:{time:0},P:[0,1,2].map(()=>({age:0,techs:{},res:{stone:100}})),
 ents:[],byId:new Map(),ME:0,resDirty:false,MV:{nav:0,o:0},gS:new Float32Array(N*N),stamp:new Int32Array(N*N),came:new Int32Array(N*N),closedS:new Int32Array(N*N),gen:0,heap:[],PF_REACHED:true,
 civOf:()=>null,heroSpd:(_u,s)=>s,toast(){},chunkDirtyAt(){},
 approach:()=>true,moveTo:(u,x,y)=>{u.state='move';u.path=[{x,y}];u.pi=0;},sel:[],setSel(l){ctx.sel=l},centerCam(){},
});
for(const name of ['alive','setMover','okTile','okXY','stepOK','hpush','hpop','rdist','los','smooth','findPath','canPlace','canAfford','pay','placeRoad','spd','pasturePen','pastureAllowed','penSheep','penPoint','insidePen','orderHerd','herdTick','isPasture','resKind','orderGather','stopUnit','watchWorker','workerBlocked','locateBlocked'])vm.runInContext(source(name),ctx);
const index=(x,y)=>y*N+x,unit=(id,type='aldeao',o=0)=>({id,kind:'u',type,o,d:ctx.UNITS[type],x:3.5,y:3.5,state:'idle',pi:0,path:null,carry:0});
const worker=unit(1);
assert.equal(ctx.placeRoad(0,3,3),true);assert.equal(ctx.P[0].res.stone,98);
assert.equal(ctx.bldAt[index(3,3)],0,'Road must not occupy a building slot');
assert.equal(ctx.blk[index(3,3)],0,'Road must stay passable');
assert.equal(ctx.placeRoad(0,3,3),false);assert.equal(ctx.P[0].res.stone,98,'Duplicate road must not charge twice');
ctx.blk[index(4,3)]=1;ctx.terr[index(4,3)]=1;assert.equal(ctx.placeRoad(0,4,3),false);
ctx.resAt[index(5,3)]={rk:'wood'};assert.equal(ctx.placeRoad(0,5,3),false);
assert.equal(ctx.placeRoad(0,-1,3),false);
const onRoad=ctx.spd(worker);delete ctx.G.roads[index(3,3)];const onGrass=ctx.spd(worker);assert.ok(Math.abs(onRoad/onGrass-1.2)<1e-10);
// The real pathfinder chooses a slightly longer paved route instead of smoothing it away.
ctx.G.roads={};for(let x=2;x<=14;x++)ctx.G.roads[index(x,10)]=1;
const route=ctx.findPath(2.5,11.5,{x:14,y:11,w:1,h:1},true,worker);
assert.ok(route.filter(p=>Math.floor(p.y)===10).length>=7,'Route must actually use the faster road');

const pen={id:20,kind:'b',type:'curral',o:0,d:ctx.BLDS.curral,tx:10,ty:10,w:3,h:3,done:true};
const sheep=unit(30,'ovelha',2);ctx.ents=[worker,pen,sheep];ctx.byId.set(pen.id,pen);
assert.equal(ctx.orderHerd(worker,pen),true);assert.equal(worker.state,'herd');assert.equal(worker.target,sheep);
ctx.herdTick(worker,1/30);assert.equal(sheep.penId,pen.id);assert.equal(sheep.state,'move');
Object.assign(sheep,ctx.penPoint(pen,sheep));sheep.path=null;sheep.state='idle';ctx.herdTick(worker,1/30);
assert.equal(ctx.stepOK(sheep,pen.tx-.1,sheep.y),false,'Collisions and movement must not push a penned sheep through the fence');
assert.equal(ctx.stepOK(sheep,sheep.x+.05,sheep.y),true);
assert.equal(worker.state,'gather');assert.equal(worker.gres,sheep);
assert.equal(ctx.pastureAllowed(sheep,1),false,'Enemy must not milk another player’s penned flock');
const before=worker.state;ctx.orderGather(worker,{...sheep,penId:21}); // Invalid old pen IDs remain harmless.
assert.equal(worker.state,before);
const extra=Array.from({length:7},(_,i)=>({...unit(40+i,'ovelha',2),penId:pen.id}));ctx.ents.push(...extra);
const ninth=unit(60,'ovelha',2),second=unit(2);ctx.ents.push(ninth,second);
assert.equal(ctx.penSheep(pen).length,8);
ctx.orderHerd(second,pen);assert.notEqual(second.target,ninth,'A full pen must not accept a ninth incoming sheep');
const deadPen={...pen,dead:true};ctx.byId.set(pen.id,deadPen);assert.equal(ctx.pasturePen(sheep),null);assert.equal(ctx.pastureAllowed(sheep,1),true);

const stuck=unit(70);stuck.state='move';stuck.path=[{x:25,y:25}];ctx.watchWorker(stuck,.1);
for(let i=0;i<45;i++)ctx.watchWorker(stuck,.1);assert.equal(ctx.workerBlocked(stuck),true);
stuck.x+=.3;ctx.watchWorker(stuck,.1);assert.equal(ctx.workerBlocked(stuck),false,'Progress must clear the blocked alert');
stuck.state='gather';stuck.path=null;for(let i=0;i<60;i++)ctx.watchWorker(stuck,.1);assert.equal(ctx.workerBlocked(stuck),false,'Stationary productive workers must not be reported as blocked');
stuck.state='move';stuck.fails=2;ctx.ents=[stuck];ctx.locateBlocked();assert.equal(ctx.sel[0],stuck);
assert.match(html,/'roads'/);assert.match(html,/pn:e\.penId\|\|null/);assert.match(html,/penId:q\.pn\|\|null/);
assert.match(html,/line:!!\(d\.wall\|\|d\.road\)/);
console.log('PASS: road cost/passability/speed and real A* route, pen escort/capacity/ownership, productive workers vs blocked workers');
