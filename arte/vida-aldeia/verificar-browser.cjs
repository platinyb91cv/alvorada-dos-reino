const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict');
const {chromium}=require('playwright');
const out=__dirname,web=path.resolve(out,'../../www');
const server=http.createServer((req,res)=>{const name=decodeURIComponent(new URL(req.url,'http://localhost').pathname),file=path.resolve(web,'.'+(name==='/'?'/index.html':name));if(!file.startsWith(web+path.sep)){res.writeHead(403);return res.end()}fs.readFile(file,(e,b)=>{if(e){res.writeHead(404);return res.end()}res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript','.webp':'image/webp','.png':'image/png','.json':'application/json'})[path.extname(file)]||'application/octet-stream');res.end(b)})});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:850}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:'+server.address().port+'/index.html');await page.waitForFunction(()=>window.__alv&&BLDART.ready&&FLORA.ready&&FAUNA.ready&&UNIT3D.aldeao.ready,{timeout:120000});
  const report=await page.evaluate(()=>{
   gameMode='build';soundOn=false;startGame(48172,{map:'continental',vic:'classico',civ:['mar','planicies']});paused=true;AIs=[null,null,null];MBG.on=false;cancelAnimationFrame(MBG.raf);
   for(const e of document.querySelectorAll('.screen'))e.style.display='none';$('menuBg').style.display='none';
   ents=[];byId.clear();bldAt.fill(0);resAt.fill(null);blk.fill(0);terr.fill(0);vis.fill(2);fx=[];projs=[];G.relics=[];P[0].age=0;P[0].techs={};for(const k of KINDS)P[0].res[k]=1000;
   mkBld(0,'centro',10,10,true);mkBld(0,'quinta',16,19,true);mkBld(0,'casa',23,12,true);mkBld(0,'armazem',23,19,true);
   const penId=mkBld(0,'curral',16,12,true).id,workerId=mkUnit(0,'aldeao',20,13).id;
   const sheepIds=[[21.5,14.5],[22.5,15.5],[20.5,15.5]].map(([x,y])=>mkUnit(2,'ovelha',x,y).id);
   doCommand(0,[byId.get(workerId)],byId.get(penId),{x:17.5,y:13.5},null,'livre');
   localStorage.setItem('qa-vida-aldeia',serialize());loadGame('qa-vida-aldeia');paused=true;AIs=[null,null,null];
   const midHerdRestored=byId.get(workerId).state==='herd'&&byId.get(workerId).bld===byId.get(penId)&&!!byId.get(workerId).target;
   for(let i=0;i<240*30;i++){G.time+=1/30;for(const u of ents.slice())if(u.kind==='u')updUnit(u,1/30);separate(1/30)}
   const pen=byId.get(penId),flock=sheepIds.map(id=>byId.get(id)),herd={midHerdRestored,inside:flock.map(s=>insidePen(s,pen)),allAssigned:flock.every(s=>s.penId===penId),hp:flock.map(s=>s.hp),workerState:byId.get(workerId).state,food:P[0].res.food};
   const builderId=mkUnit(0,'aldeao',12,15).id,before=P[0].res.stone;
   EXEC.wall(0,{t:'estrada',a:{x:10,y:16},b:{x:24,y:16},u:[builderId]});
   const roadCount=Object.keys(G.roads||{}).length,roadCost=before-P[0].res.stone;
   const builder=byId.get(builderId);builder.x=12.5;builder.y=16.5;const pavedSpeed=spd(builder);builder.y=17.5;const grassSpeed=spd(builder);
   const path=findPath(10.5,17.5,{x:24,y:17,w:1,h:1},true,builder),pavedWaypoints=path.filter(p=>G.roads[idx(Math.floor(p.x),Math.floor(p.y))]).length;
   const oldRoads=JSON.stringify(G.roads);localStorage.setItem('qa-vida-aldeia',serialize());loadGame('qa-vida-aldeia');paused=true;AIs=[null,null,null];
   const restored=JSON.stringify(G.roads)===oldRoads&&sheepIds.every(id=>byId.get(id).penId===penId)&&byId.get(workerId).gres?.penId===penId;
   recount();const hashBefore=stateHash(),snapshot=snapState();applySnap(snapshot,false);const exactSnapshot=stateHash()===hashBefore;const flipped=swapSnap(JSON.parse(JSON.stringify(snapshot)));const flippedOwner=Object.values(flipped.G.roads).every(o=>o===2);swapSnap(flipped);const swapRoundTrip=JSON.stringify(flipped.G.roads)===oldRoads;
   const stuck=mkUnit(0,'aldeao',21,17);stuck.state='move';stuck.path=[{x:25,y:25}];watchWorker(stuck,.1);for(let i=0;i<45;i++)watchWorker(stuck,.1);
   updateTop();window.qaIds={penId,workerId,builderId,stuckId:stuck.id};
   const issueButton={visible:!$('bStuck').hidden,count:$('stuckN').textContent};
   buildTerrain();CHUNKS.clear();const p=proj(18,16);cam.z=1.9;cam.x=p.x-vw/(2*cam.z);cam.y=p.y-vh/(2*cam.z);fogCtx.clearRect(0,0,W,H);
   for(const e of document.querySelectorAll('.screen'))e.style.display='none';$('menuBg').style.display='none';sel=[byId.get(penId)];uiDirty=true;updateTop();updateUI();render();
   return {herd,roads:{count:roadCount,cost:roadCost,pavedSpeed,grassSpeed,pavedWaypoints},saveLoad:restored,snapshot:{exactSnapshot,flippedOwner,swapRoundTrip},issueButton,indexBytes:new TextEncoder().encode(document.documentElement.outerHTML).length};
  });
  assert.ok(report.herd.midHerdRestored&&report.herd.allAssigned&&report.herd.inside.every(Boolean),JSON.stringify(report.herd));assert.ok(report.herd.hp.every(h=>h===12));assert.equal(report.herd.workerState,'gather');assert.ok(report.herd.food>1000);
  assert.equal(report.roads.count,15);assert.equal(report.roads.cost,30);assert.ok(Math.abs(report.roads.pavedSpeed/report.roads.grassSpeed-1.2)<1e-8);assert.ok(report.roads.pavedWaypoints>=8);assert.ok(report.saveLoad);assert.ok(Object.values(report.snapshot).every(Boolean),JSON.stringify(report.snapshot));assert.deepEqual(report.issueButton,{visible:true,count:'1'});
  await page.screenshot({path:path.join(out,'curral-estradas-desktop.png')});
  await page.locator('#bStuck').click();assert.equal(await page.evaluate(()=>sel[0].id),await page.evaluate(()=>qaIds.stuckId));
  await page.evaluate(()=>{setSel([byId.get(qaIds.builderId)]);menuMode='build';uiDirty=true;updateUI()});
  await page.getByTitle('Curral',{exact:true}).click();await page.evaluate(()=>updateUI());assert.equal(await page.evaluate(()=>placing.type),'curral');await page.locator('#cmds').getByText('Cancelar',{exact:true}).click();
  await page.evaluate(()=>{menuMode='build';uiDirty=true;updateUI()});await page.getByTitle('Estrada',{exact:true}).click();await page.evaluate(()=>updateUI());assert.equal(await page.evaluate(()=>placing.line),true);await page.locator('#cmds').getByText('Cancelar',{exact:true}).click();
  await page.setViewportSize({width:844,height:390});await page.waitForFunction(()=>vw===844&&vh===390);await page.evaluate(()=>{$('toast').replaceChildren();cam.z=1.25;centerCam(18,15);setSel([byId.get(qaIds.penId)]);updateTop();updateUI();render()});await page.screenshot({path:path.join(out,'curral-estradas-mobile.png')});
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'browser.verification.json'),JSON.stringify({passed:true,...report,menuButtons:true,blockedButtonSelectsUnit:true,errors},null,2));console.log(JSON.stringify({passed:true,...report}));
 }finally{await browser.close();server.close()}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
