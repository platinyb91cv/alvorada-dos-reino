// Reis de 8 direções: o quadro recolorido sozinho tem de ser igual ao mesmo quadro do atlas inteiro recolorido,
// e a cache de quadros tem de ficar limitada.
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(path.join(__dirname,'..','www/index.html'),'utf8');
function fn(name){const s=html.indexOf('function '+name+'('),e=html.indexOf('\nfunction ',s+1);assert.ok(s>=0,name);return html.slice(s,e).split('\n// ')[0]}
function mkCanvas(w,h){const cv={width:w,height:h,px:new Uint8ClampedArray(w*h*4)};cv.getContext=()=>({
  drawImage(src,...a){let sx=0,sy=0,sw=src.width,sh=src.height,dx=0,dy=0;if(a.length===2)[dx,dy]=a;else[sx,sy,sw,sh,dx,dy]=a;
    for(let y=0;y<sh;y++)for(let x=0;x<sw;x++){const si=((sy+y)*src.width+sx+x)*4,di=((dy+y)*w+dx+x)*4;for(let k=0;k<4;k++)cv.px[di+k]=src.px[si+k]}},
  getImageData(x,y,ww,hh){const d=new Uint8ClampedArray(ww*hh*4);for(let r=0;r<hh;r++)d.set(cv.px.subarray(((y+r)*w+x)*4,((y+r)*w+x+ww)*4),r*ww*4);return{data:d}},
  putImageData(img,x,y){cv.px.set(img.data)}});return cv}
// atlas sintético: píxeis variados, com azuis (equipa) e vermelhos (capa) garantidos
const W=96,H=64,img={width:W,height:H,px:new Uint8ClampedArray(W*H*4)};let seed=7;const rnd=()=>(seed=(seed*1103515245+12345)%2147483648)/2147483648;
for(let i=0;i<W*H;i++){const t=i%5;const p=t===0?[40,70,200]:t===1?[176,20,40]:[rnd()*255,rnd()*255,rnd()*255];img.px.set([...p.map(v=>v|0),t===4?0:255],i*4)}
const f=[];for(let d=0;d<8;d++)for(let s=0;s<24;s++){const x=(d*24+s)%12*8,y=((d*24+s)/12|0)%8*8;f.push([x,y,8,8,4,8])}
const source={key:'teste',wide:true,img,teams:new Map(),cape:new Map(),meta:{h:130,directions:8,framesPerDirection:24,f}};
const ctx={Math,parseInt,mkCanvas,KFRAME:new Map(),KFRAME_MAX:40,KART:source};
for(const n of ['capeHue','teamTintData','capeTintData','recolorImg','kingAtlas','kingFrameCanvas'])ctx[n]=vm.runInNewContext('('+fn(n)+')',ctx);
let compared=0;
for(const team of ['#d23a2a','#3f86e0','#2fa84a','#e0c040'])for(const cape of ['#aa2244','#2244aa','#888888'])for(const fr of [0,25,100,191]){
  const full=ctx.kingAtlas(team,cape,source),one=ctx.kingFrameCanvas(source,fr,team,cape),[x,y,w,h]=f[fr];
  const want=full.getContext().getImageData(x,y,w,h).data;assert.deepEqual(one.px,want,'frame '+fr+' '+team+' '+cape);compared++}
console.log('PASS: per-frame recolour identical to whole-atlas recolour ('+compared+' frames)');
ctx.KFRAME.clear();for(let i=0;i<192;i++)ctx.kingFrameCanvas(source,i,'#d23a2a','#aa2244');
assert.ok(ctx.KFRAME.size<=ctx.KFRAME_MAX,'cache unbounded');const keep=ctx.KFRAME.keys().next().value;ctx.kingFrameCanvas(source,+keep.split('|').pop(),'#d23a2a','#aa2244');
ctx.kingFrameCanvas(source,0,'#000001','#aa2244');assert.ok(ctx.KFRAME.has(keep),'recently used frame evicted');
const t2=ctx.kingFrameCanvas(source,3,'#d23a2a','#aa2244');assert.equal(ctx.kingFrameCanvas(source,3,'#d23a2a','#aa2244'),t2,'cache miss on repeat');
console.log('PASS: frame cache bounded ('+ctx.KFRAME.size+'/'+ctx.KFRAME_MAX+'), LRU keeps recent frames');
const tainted={...source,key:'t2',img:{width:W,height:H,px:img.px}};const bad=(w,h)=>{const c=mkCanvas(w,h);const g=c.getContext();c.getContext=()=>({...g,getImageData(){throw new Error('SecurityError')}});return c};
const ctx2={...ctx,mkCanvas:bad,KFRAME:new Map()};ctx2.kingFrameCanvas=vm.runInNewContext('('+fn('kingFrameCanvas')+')',ctx2);
assert.ok(ctx2.kingFrameCanvas(tainted,1,'#d23a2a','#aa2244'));console.log('PASS: no crash when pixels are unreadable (file://)');
assert.ok(Buffer.byteLength(html)<5*1048576,'index.html grew past 5 MB');console.log('PASS: index.html '+(Buffer.byteLength(html)/1048576).toFixed(2)+' MB');
