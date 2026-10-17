const fs = require('node:fs');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'www/index.html'), 'utf8');
const block = html.slice(html.indexOf('const BART='), html.indexOf('function kingAtlasForAge'));
const meta = JSON.parse(block.split('\n')[0].split('meta:')[1].replace(/};\s*$/, ''));
const stored = JSON.parse(fs.readFileSync(path.join(root, 'arte/rei/rei.json'), 'utf8'));
assert.deepEqual(meta, stored, 'Embedded metadata differs from source atlas');
assert.equal(meta.h, 130);
assert.equal(meta.f.length, 24);
const payload = block.match(/im\.src='data:image\/webp;base64,([^']+)'/);
assert.ok(payload, 'Embedded WebP missing');
const webp = Buffer.from(payload[1], 'base64');
assert.deepEqual(webp, fs.readFileSync(path.join(root, 'arte/rei/rei.webp')), 'Embedded atlas is stale');
assert.equal(webp.toString('ascii', 0, 4), 'RIFF');
assert.equal(webp.toString('ascii', 8, 12), 'WEBP');
const png = fs.readFileSync(path.join(root, 'arte/rei/rei_atlas.png'));
assert.equal(png.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
const width = png.readUInt32BE(16), height = png.readUInt32BE(20);
for (const [i, frame] of meta.f.entries()) {
  assert.equal(frame.length, 6);
  assert.ok(frame.every(Number.isFinite), `Invalid frame ${i}`);
  const [x, y, w, h, ax, ay] = frame;
  assert.ok(x >= 0 && y >= 0 && w > 0 && h > 0 && x+w <= width && y+h <= height, `Frame ${i} outside atlas`);
  assert.ok(Math.abs(ax) < width && Math.abs(ay) < height*2, `Invalid anchor ${i}`);
}
assert.match(html, /const KING_H=34/);
assert.match(html, /return 16\+Math\.min\(7/);
// Exercise the real age selector and draw dispatcher outside browser/auth code.
const vm = require('node:vm');
const selector = html.match(/function kingAtlasForAge\(age\)\{[^\n]+\}/)[0];
const start = html.indexOf('function drawKing(c,e,v,px,py)');
const end = html.indexOf('\nfunction ', start+1);
const knight = {ready:true}, stone = {ready:true};
const calls = [];
const context = {BART:stone,KART:knight,KING_H:34,P:[{age:0,col:'#3366cc'}],G:{hero:{}},ME:0,cam:{z:.5},performance:{now:()=>1000},Math,
  kingLook:()=>({cape:'#aa2244'}),heroWC:()=>false,kingFrameIdx:()=>8,drawKingArt:(...args)=>calls.push(args.at(-1))};
context.kingAtlasForAge = vm.runInNewContext('('+selector+')',context);
const draw = vm.runInNewContext('('+html.slice(start,end)+')',context);
const canvas = {beginPath(){},ellipse(){},fill(){}};
for (const age of [0,1,2]) {
  context.P[0].age=age;
  draw(canvas,{o:0,id:1,state:'idle',face:1,path:[],pi:0},null,0,0);
  assert.equal(calls.at(-1),age===0?stone:knight,`Wrong king atlas in age ${age}`);
}
stone.ready=false;
assert.equal(context.kingAtlasForAge(0),knight,'Missing loading fallback');
assert.match(html, /f\.t>1\.2,kingAtlasForAge\(P\[f\.o\]\.age\)/);
console.log(JSON.stringify({kingAtlasVerified:true,frames:24,width,height,webpBytes:webp.length,embeddedPayloadMatches:true,stoneAgeRouting:true,bronzeAndIronKnightPreserved:true,corpseRouting:true}));
