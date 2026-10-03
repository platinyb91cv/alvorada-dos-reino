import asyncio,json
from playwright.async_api import async_playwright
JS=r"""
async (args)=>{const [N,zoom]=args;startGame(7);const s=__S();s.AIs[1]=null;s.vis.fill(2);s.P[0].age=2;s.P[1].age=2;s.fx.length=0;
 const cx=40,cy=40;for(let y=cy-12;y<=cy+12;y++)for(let x=cx-14;x<=cx+14;x++){const r=s.resAt[idx(x,y)];if(r&&!r.fish)removeRes(r)}
 const T=['guerreiro','lanceiro','espadachim','arqueiro','besteiro','cavaleiro','cavPesada','cavArqueira','aldeao','sacerdote','catapulta','ariete'];
 const A=[],B=[];for(let i=0;i<N;i++){const side=i%2,k=(i>>1);const t=T[k%T.length];const u=mkUnit(side?1:0,t,cx+(side?4:-4)+(k%6)*.6,cy-6+Math.floor(k/6)*.6);(side?B:A).push(u)}
 for(const u of A)orderAttack(u,B[Math.floor(Math.random()*B.length)]);for(const u of B)orderAttack(u,A[Math.floor(Math.random()*A.length)]);
 paused=false;cam.z=zoom;centerCam(cx,cy);const ctx=document.querySelector('canvas').getContext('2d');
 for(let i=0;i<20;i++){step(1/30);render();ctx.getImageData(0,0,1,1)}
 const m0=UCMISS;const rs=[],ss=[];for(let i=0;i<150;i++){let t0=performance.now();step(1/30);ss.push(performance.now()-t0);t0=performance.now();render();ctx.getImageData(0,0,1,1);rs.push(performance.now()-t0)}
 const q=(a,p)=>{a=a.slice().sort((x,y)=>x-y);return a[Math.floor(a.length*p)]};const avg=a=>a.reduce((x,y)=>x+y,0)/a.length;
 const vis=s.ents.filter(e=>e.kind==='u'&&!e.dead).length;
 return {miss150:UCMISS-m0,cacheMB:+(UCBYTES/1e6).toFixed(1),N,zoom,alive:vis,render_avg:+avg(rs).toFixed(2),render_p95:+q(rs,.95).toFixed(2),step_avg:+avg(ss).toFixed(2),frame_avg:+(avg(rs)+avg(ss)).toFixed(2)}}
"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page(viewport={"width":900,"height":420},device_scale_factor=2)
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
    await pg.goto("file:///home/claude/alvorada/www/index.html");await pg.click("#lgPreview"); await pg.click("#bPlay");await pg.wait_for_timeout(300)
    for N in (50,100,200):
      for z in (1.0,2.2,.6):
        r=await pg.evaluate(JS,[N,z]);print(json.dumps(r))
    print("ERRS",errs);await b.close()
asyncio.run(main())
