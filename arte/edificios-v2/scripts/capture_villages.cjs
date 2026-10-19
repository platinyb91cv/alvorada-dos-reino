const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright');
const repo=path.resolve(__dirname,'../../..'),out=path.resolve(__dirname,'../publicacao');
const entries=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'),'utf8')).entries;
const errors=[];const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript','.json':'application/json','.webp':'image/webp','.png':'image/png','.mp3':'audio/mpeg','.wav':'audio/wav','.ogg':'audio/ogg'};
const server=http.createServer((req,res)=>{const url=new URL(req.url,'http://localhost');let name=decodeURIComponent(url.pathname);if(name==='/')name='/index.html';const p=path.resolve(repo,'www','.'+name);if(!p.startsWith(path.resolve(repo,'www')+path.sep)){res.writeHead(403);return res.end();}fs.readFile(p,(err,b)=>{if(err){res.writeHead(404);return res.end();}res.setHeader('Content-Type',mime[path.extname(p)]||'application/octet-stream');res.setHeader('Cache-Control','no-store');res.end(b);});});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const port=server.address().port;
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1600,height:1050},deviceScaleFactor:1});
 page.on('pageerror',e=>errors.push(String(e).slice(0,400)));
 await page.goto('http://127.0.0.1:'+port+'/',{waitUntil:'load',timeout:60000});
 await page.waitForFunction(()=>window.__alv&&BLDART.ready&&FLORA.ready,{timeout:60000});
 console.log('GAME_LOADED',await page.evaluate(()=>({atlas:[BLDART.img.width,BLDART.img.height],keys:Object.keys(BLDART.meta).length,ready:BLDART.ready})));
 const results=[];
 for(const age of [0,1,2]){
  const result=await page.evaluate(async({age,entries})=>{
   gameMode='build';soundOn=false;startGame(48172,{map:'rios',vic:'classico',civ:['mar','planicies']});paused=true;
   // Deterministic QA village, using the real map, real entities and renderer.
   P[ME].age=age;P[ME].col='#3f86e0';sel=[];placing=null;ents=[];byId.clear();bldAt.fill(0);resAt.fill(null);blk.fill(0);terr.fill(0);nid=1;
   const rows=[['centro','casa','casa','armazem'],['quartel','arquearia','estabulo','ferreiro'],['quinta','templo','oficina','torre'],['doca','maravilha','torre','casa']];
   const made=[];
   for(let row=0;row<rows.length;row++)for(let col=0;col<rows[row].length;col++){
    const type=rows[row][col];if(age===0&&['templo','oficina','torre','maravilha'].includes(type))continue;if(age===1&&type==='maravilha')continue;
    let tx=20+col*6,ty=20+row*6;const b=mkBld(ME,type,tx,ty,true);if(type==='torre')b.lvl=age===2?(row===3?3:2):1;b.seen=true;made.push(b);
   }
   // Wall and gate modules in both diagonals, away from building footprints.
   for(const [type,tx,ty] of [['muralhaMadeira',16,22],['muralhaMadeira',17,22],['portaoMadeira',18,22],['muralhaMadeira',19,22],['muralhaPedra',23,16],['muralhaPedra',23,17],['portaoPedra',23,18],['muralhaPedra',23,19]]){const b=mkBld(ME,type,tx,ty,true);b.seen=true;made.push(b);}
   // A small shore at the dock, with terrain rendered by the unchanged engine.
   for(let y=40;y<50;y++)for(let x=16;x<27;x++){terr[idx(x,y)]=1;blk[idx(x,y)]=1;}
   for(const b of made)for(let y=b.ty;y<b.ty+b.h;y++)for(let x=b.tx;x<b.tx+b.w;x++){terr[idx(x,y)]=0;}
   G.time=0;G.hero=null;fx=[{type:'rubble',x:42,y:33,w:age?3:2,h:age?3:2,t:0,life:16}];projs=[];
   vis.fill(2);fogCtx.clearRect(0,0,fogCanvas.width,fogCanvas.height);G.relics=[];
   // Isolated offline QA: hide the account/menu overlay without changing auth code.
   for(const screen of document.querySelectorAll('.screen'))screen.style.display='none';
   MBG.on=false;MBG.still=true;cancelAnimationFrame(MBG.raf);$('menuBg').style.display='none';
   for(const [x,y] of [[24,24],[25,25],[26,25],[31,24],[32,25],[25,31],[31,31],[37,31]])mkUnit(ME,'aldeao',x+.5,y+.5);
   buildTerrain();CHUNKS.clear();for(const key in BCACHE)delete BCACHE[key];
   const boxes=made.map(b=>{const p=proj(b.tx,b.ty),s=bldSprite(b.type,age,ME,bldVariant(b));return {key:bldArtKey(b.type,age,bldVariant(b)),x:p.x-s.ox,y:p.y-s.oy,w:s.CW,h:s.CH};});
   const minX=Math.min(...boxes.map(b=>b.x))-70,maxX=Math.max(...boxes.map(b=>b.x+b.w))+70;
   const minY=Math.min(...boxes.map(b=>b.y))-50,maxY=Math.max(...boxes.map(b=>b.y+b.h))+70;
   cam.z=Math.min(1.25,(vw-70)/(maxX-minX),(vh-170)/(maxY-minY));cam.x=(minX+maxX)/2-vw/cam.z/2;cam.y=(minY+maxY)/2-vh/cam.z/2-35/cam.z;
   uiDirty=true;resDirty=true;updateTop();updateUI();render();
   return {age,seed:G.seed,buildings:made.length,keys:[...new Set([...boxes.map(b=>b.key).filter(Boolean),age?'ruina|1':'ruina|0'])],camera:{...cam},size:{vw,vh},boxes};
  },{age,entries});
  await page.waitForTimeout(1000);await page.screenshot({path:path.join(out,'capturas','vila-idade-'+age+'.png')});results.push(result);console.log('CAPTURED',age,result.buildings);
 }
 const calibration=await page.evaluate(({entries})=>{
  const rs=2,w=1600,rowH=330,cols=5,top=60;const canvas=document.createElement('canvas');canvas.width=w;canvas.height=top+Math.ceil(entries.length/cols)*rowH;const c=canvas.getContext('2d');c.fillStyle='#292d28';c.fillRect(0,0,canvas.width,canvas.height);c.fillStyle='#eee2c9';c.font='24px sans-serif';c.fillText('37 PEÇAS — DESENHO REAL DO JOGO / ÂNCORA E LOTE',20,35);const checks=[];
  for(let i=0;i<entries.length;i++){
   const e=entries[i];const x=i%cols*320,y=top+Math.floor(i/cols)*rowH;const [type,variant]=e.key.split('|');const age=+variant;let s;
   if(type==='ruina'){
    const m=BLDART.meta[e.key],[sx,sy,iw,ih]=m.f,k=2*e.tiles[0]*HW*1.03/(m.xr-m.xl);const cc=document.createElement('canvas');cc.width=Math.ceil(iw*k*2)+4;cc.height=Math.ceil(ih*k*2)+4;cc.getContext('2d').drawImage(BLDART.img,sx,sy,iw,ih,2,2,iw*k*2,ih*k*2);s={cv:cc,CW:cc.width/2,CH:cc.height/2,ox:(m.xl+m.xr)/2*k+1,oy:m.yb*k+1-e.tiles[0]*HH*2};
   }else{s=bldSprite(type,Math.min(2,age),ME,type==='torre'?age:0);}
   const n=e.tiles[0],originX=x+160,originY=y+rowH-100;
   c.strokeStyle='#8aab75';c.beginPath();c.moveTo(originX,originY);c.lineTo(originX+n*32,originY+n*16);c.lineTo(originX,originY+n*32);c.lineTo(originX-n*32,originY+n*16);c.closePath();c.stroke();
   c.drawImage(s.cv,originX-s.ox,originY-s.oy,s.CW,s.CH);c.fillStyle='#f8edd6';c.font='17px sans-serif';c.fillText(e.key+'  '+e.tiles.join('×'),x+12,y+24);
   const m=BLDART.meta[e.key];const k=2*n*HW*1.03/(m.xr-m.xl)*(e.artFactor||1);
   const check={key:e.key,CW:s.CW,CH:s.CH,ox:s.ox,oy:s.oy,finite:[s.CW,s.CH,s.ox,s.oy].every(Number.isFinite),positive:s.CW>0&&s.CH>0};
   if(!e.thin&&type!=='ruina'){check.footprintWidth=(m.xr-m.xl)*k;check.expectedFootprintWidth=2*n*HW*1.03*(e.artFactor||1);check.bottomY=m.yb*k+2-s.oy;check.expectedBottomY=n*HH*(1+(e.artFactor||1));check.anchorError=Math.abs(check.bottomY-check.expectedBottomY);}
   checks.push(check);
  }
  return {png:canvas.toDataURL('image/png').split(',')[1],checks};
 },{entries});
 fs.writeFileSync(path.join(out,'capturas','calibracao-37-pecas.png'),Buffer.from(calibration.png,'base64'));
 const covered=[...new Set(results.flatMap(r=>r.keys))];if(entries.some(e=>!covered.includes(e.key)))throw Error('Village screenshots omit approved keys');
 const report={browser:'Chrome headless, real game renderer',viewport:{width:1600,height:1050},deviceTested:false,errors,coveredApprovedKeys:entries.map(e=>e.key),ages:results,checks:calibration.checks};
 fs.writeFileSync(path.join(out,'jogo.verification.json'),JSON.stringify(report,null,2));
 await browser.close();server.close();if(errors.length||calibration.checks.some(c=>!c.finite||!c.positive||c.anchorError>.51))throw Error('Game errors or anchor mismatch: '+JSON.stringify(errors));
})().catch(e=>{console.error(e.stack);server.close();process.exit(1);});
