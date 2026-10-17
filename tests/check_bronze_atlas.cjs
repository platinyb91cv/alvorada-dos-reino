const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'www/index.html'), 'utf8');
function verifyAtlas(marker, endMarker, folder) {
  const start = html.indexOf('const '+marker+'=');
  assert.ok(start>=0, marker+' missing');
  const block = html.slice(start,html.indexOf(endMarker,start+1));
  const meta = JSON.parse(block.split('\n')[0].split('meta:')[1].replace(/};\s*$/, ''));
  const stored = JSON.parse(fs.readFileSync(path.join(root,folder,'rei.json'),'utf8'));
  assert.deepEqual(meta,stored,marker+': embedded metadata differs');
  assert.equal(meta.h,130);assert.equal(meta.f.length,192);assert.equal(meta.directions,8);assert.equal(meta.framesPerDirection,24);
  const payload=block.match(/im\.src='(assets\/kings\/[a-z]+\.webp)\?v=([0-9a-f]{12})'/);
  assert.ok(payload,marker+': atlas file reference missing');
  assert.ok(!/base64,/.test(block),marker+': atlas must not be embedded in index.html');
  const webp=fs.readFileSync(path.join(root,'www',payload[1]));
  assert.deepEqual(webp,fs.readFileSync(path.join(root,folder,'rei.webp')),marker+': shipped atlas stale');
  assert.equal(require('node:crypto').createHash('sha256').update(webp).digest('hex').slice(0,12),payload[2],marker+': cache-busting hash stale');
  assert.equal(webp.toString('ascii',0,4),'RIFF');assert.equal(webp.toString('ascii',8,12),'WEBP');
  const png=fs.readFileSync(path.join(root,folder,'rei_atlas.png'));
  assert.equal(png.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
  const width=png.readUInt32BE(16),height=png.readUInt32BE(20);
  for(const [i,frame]of meta.f.entries()){
    assert.equal(frame.length,6);assert.ok(frame.every(Number.isFinite));
    const[x,y,w,h,ax,ay]=frame;
    assert.ok(x>=0&&y>=0&&w>0&&h>0&&x+w<=width&&y+h<=height,marker+': frame outside atlas '+i);
    assert.ok(Math.abs(ax)<width&&Math.abs(ay)<height*2,marker+': invalid anchor '+i);
  }
  return{frames:192,width,height,webpBytes:webp.length};
}
const stoneResult=verifyAtlas('BART','const BRONZE_ART=','arte/rei');
const bronzeResult=verifyAtlas('BRONZE_ART','function kingAtlasForAge','arte/rei-bronze');
assert.match(html,/const KING_H=34/);assert.match(html,/return 16\+Math\.min\(7/);
const selector=html.match(/function kingAtlasForAge\(age\)\{[^\n]+\}/)[0];
const start=html.indexOf('function drawKing(c,e,v,px,py)'),end=html.indexOf('\nfunction ',start+1);
const knight={ready:true},stone={ready:true},bronze={ready:true},calls=[];
const context={BART:stone,BRONZE_ART:bronze,KART:knight,KING_H:34,P:[{age:0,col:'#3366cc'}],G:{hero:{}},ME:0,cam:{z:.5},performance:{now:()=>1000},Math,
  kingDirection:()=>0,kingLook:()=>({cape:'#aa2244'}),heroWC:()=>false,kingFrameIdx:()=>8,drawKingArt:(...args)=>calls.push(args[9])};
context.kingAtlasForAge=vm.runInNewContext('('+selector+'\n)',context);
const draw=vm.runInNewContext('('+html.slice(start,end)+'\n)',context);
const cs=html.indexOf('function drawKingCorpse'),ce=html.indexOf('\n//',cs);
const drawCorpse=vm.runInNewContext('('+html.slice(cs,ce)+'\n)',context);
const canvas={beginPath(){},ellipse(){},fill(){}};
for(const[age,expected]of[[0,stone],[1,bronze],[2,knight]]){
  context.P[0].age=age;draw(canvas,{o:0,id:1,state:'idle',face:1,path:[],pi:0},null,0,0);
  assert.equal(calls.at(-1),expected,'Wrong living king atlas in age '+age);
  drawCorpse(canvas,{o:0,life:10,t:.5,face:1},{x:0,y:0});
  assert.equal(calls.at(-1),expected,'Wrong corpse atlas in age '+age);
}
stone.ready=false;bronze.ready=false;
assert.equal(context.kingAtlasForAge(0),knight);assert.equal(context.kingAtlasForAge(1),knight);
console.log(JSON.stringify({kingAtlasesVerified:true,stone:stoneResult,bronze:bronzeResult,threeAgeRouting:true,livingAndCorpseRouting:true,loadingFallback:true}));

// Exercise the actual heading and rendering functions, including weapons that must not mirror.
function fn(name){const start=html.indexOf('function '+name+'('),end=html.indexOf('\nfunction ',start+1);return html.slice(start,end)}
const directionContext={Math,Number,rectOf:e=>e.kind==='u'?{x:Math.floor(e.x),y:Math.floor(e.y),w:1,h:1}:{x:e.tx,y:e.ty,w:e.w,h:e.h}};
const fromDelta=directionContext.kingDirFromDelta=vm.runInNewContext('('+fn('kingDirFromDelta')+'\n)',directionContext);
const direction=vm.runInNewContext('('+fn('kingDirection')+'\n)',directionContext);
const vectors=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]];
for(const [i,[x,y]]of vectors.entries()){
 assert.equal(fromDelta(x,y),i);assert.equal(fromDelta(x*10,y*10),i);
 assert.equal(direction({x:0,y:0,path:[{x,y}],pi:0,kingDir:4}),i);
 assert.equal(direction({x:0,y:0,state:'attack',target:{kind:'u',x,y},kingDir:4}),i);
 assert.equal(direction({x:0,y:0,state:'attack',target:{tx:x-.5,ty:y-.5,w:1,h:1},kingDir:4}),i);
 assert.equal(direction({state:'idle',kingDir:i}),i);
 assert.equal(fromDelta(0,0,i),i);
}
const drawLog=[],scaleLog=[];
const renderContext={KART:knight,KING_H:34,kingAtlas:()=>({}),kingFrameCanvas:(s,f)=>({frame:f})};
const render=vm.runInNewContext('('+fn('drawKingArt')+'\n)',renderContext);
const cc={save(){},restore(){},translate(){},scale(...a){scaleLog.push(a)},drawImage(...a){drawLog.push(a)}};
const meta=JSON.parse(fs.readFileSync(path.join(root,'arte/rei-bronze/rei.json'),'utf8'));
for(let d=0;d<8;d++)for(const i of [4,8,12,15,16,23]){
 render(cc,i,'blue','red',0,0,-1,null,false,{meta},d);
 const call=drawLog.at(-1),fr=meta.f[d*24+i];assert.equal(call[0].frame,d*24+i);assert.deepEqual(call.slice(1,5),[0,0,fr[2],fr[3]]);
}
assert.equal(scaleLog.length,0,'Directional sprites must not mirror the spear');
render(cc,8,'blue','red',0,0,-1,null,false,{meta:{h:130,f:meta.f.slice(0,24)}},0);
assert.deepEqual(scaleLog.at(-1),[-1,1],'Legacy knight keeps its original rendering');
// Dead kings retain their death heading and age even if their owner advances.
const corpseCalls=[];context.drawKingArt=(...a)=>corpseCalls.push(a);stone.ready=true;bronze.ready=true;context.P[0].age=2;
for(let d=0;d<8;d++){
 drawCorpse(canvas,{o:0,age:1,kingDir:d,life:10,t:.5,face:-1},{x:0,y:0});
 assert.equal(corpseCalls.at(-1)[9],bronze);assert.equal(corpseCalls.at(-1)[10],d);
}
console.log('PASS: eight movement/attack headings, idle/death retention, correct atlas frames, no mirrored spear, legacy fallback');
// Follow a real short waypoint through the arrival branch, where orientation previously stayed stale.
const followContext={Math,hyp:Math.hypot,physSpeed:()=>1,stepOK:()=>true,kingDirFromDelta:fromDelta,spawnFx(){}};
followContext.faceTo=vm.runInNewContext('('+fn('faceTo')+'\n)',followContext);
const follow=vm.runInNewContext('('+fn('follow')+'\n)',followContext);
for(const [i,[dx,dy]]of vectors.entries()){
 const u={x:0,y:0,d:{king:1,cls:'inf',speed:1},path:[{x:dx*.03,y:dy*.03}],pi:0,kingDir:(i+4)%8,anim:0};
 assert.equal(follow(u,.1),true);assert.equal(u.kingDir,i);assert.equal(u.pi,1);
 assert.equal(u.x,dx*.03);assert.equal(u.y,dy*.03);
 followContext.faceTo(u,u.x+dx,u.y+dy,.35);assert.equal(u.kingDir,i);
}
console.log('PASS: actual movement and faceTo preserve eight headings, including final short waypoint');
// A saved idle king must not turn back to the default view after Continue.
const saveContext={JSON,Math,difficulty:0,nid:1,G:{seed:1,time:0,starts:[]},gExtra:()=>({}),P:[],W:0,terr:[],vis:[],byId:new Map(),AIs:[],cam:{},ents:[]};
const serialize=vm.runInNewContext('('+fn('serialize')+'\n)',saveContext);
const ma=html.indexOf('const mkU=(q,push)=>'),mb=html.indexOf("  for(const q of d.ents.filter(x=>x.k==='u'))",ma);
const loadContext={Number,Math,nid:0,ents:[],byId:new Map(),pend:[],mkUnit:()=>({d:{king:1},id:1})};
const restore=vm.runInNewContext('(function(){'+html.slice(ma,mb)+';return mkU})()',loadContext);
for(let d=0;d<8;d++){
 saveContext.ents=[{kind:'u',id:1,o:0,type:'rei',d:{king:1},x:2,y:3,hp:160,state:'idle',kingDir:d}];
 const q=JSON.parse(serialize()).ents[0];assert.equal(q.kd,d);assert.equal(restore(q,true).kingDir,d);
}
assert.equal(restore({id:1,kd:99},true).kingDir,undefined);assert.equal(restore({id:1},true).kingDir,undefined);
console.log('PASS: save/continue retains all eight headings; old saves still load');
// Parse the complete shipped inline JavaScript, beyond the extracted render functions.
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))if(m[1].trim())new vm.Script(m[1]);
console.log('PASS: complete inline game JavaScript parses');
