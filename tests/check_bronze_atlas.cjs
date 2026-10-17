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
  assert.equal(meta.h,130);assert.equal(meta.f.length,24);
  const payload=block.match(/im\.src='data:image\/webp;base64,([^']+)'/);
  assert.ok(payload,marker+': embedded WebP missing');
  const webp=Buffer.from(payload[1],'base64');
  assert.deepEqual(webp,fs.readFileSync(path.join(root,folder,'rei.webp')),marker+': embedded atlas stale');
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
  return{frames:24,width,height,webpBytes:webp.length};
}
const stoneResult=verifyAtlas('BART','const BRONZE_ART=','arte/rei');
const bronzeResult=verifyAtlas('BRONZE_ART','function kingAtlasForAge','arte/rei-bronze');
assert.match(html,/const KING_H=34/);assert.match(html,/return 16\+Math\.min\(7/);
const selector=html.match(/function kingAtlasForAge\(age\)\{[^\n]+\}/)[0];
const start=html.indexOf('function drawKing(c,e,v,px,py)'),end=html.indexOf('\nfunction ',start+1);
const knight={ready:true},stone={ready:true},bronze={ready:true},calls=[];
const context={BART:stone,BRONZE_ART:bronze,KART:knight,KING_H:34,P:[{age:0,col:'#3366cc'}],G:{hero:{}},ME:0,cam:{z:.5},performance:{now:()=>1000},Math,
  kingLook:()=>({cape:'#aa2244'}),heroWC:()=>false,kingFrameIdx:()=>8,drawKingArt:(...args)=>calls.push(args.at(-1))};
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
