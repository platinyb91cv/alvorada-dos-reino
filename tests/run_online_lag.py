# Modo online sob latência (FAKE_LAG ms em cada sentido) e batalha grande
import asyncio,os,subprocess,time
from playwright.async_api import async_playwright
PORT=8792;LAG=int(os.environ.get('LAG','150'))
URL=f"http://127.0.0.1:{PORT}/"
SPAWN="""()=>{EXEC.spawn=(o,d)=>{const c=__S().G.starts[o];const T=['guerreiro','arqueiro','cavaleiro','lanceiro','espadachim','besteiro','catapulta','sacerdote'];for(let i=0;i<d.n;i++)__alv.mkUnit(o,T[i%T.length],c.x+3+(i%8)*.7,c.y+4+Math.floor(i/8)*.7)};}"""
ORD=r"""()=>{const s=__S();const mine=s.ents.filter(e=>e.kind==='u'&&e.o===ME&&e.d.mil);const en=s.ents.filter(e=>e.kind==='u'&&e.o!==ME&&e.o!==2);
  if(mine.length&&en.length){const t=en[Math.floor(Math.random()*en.length)];G.cmdMode='amove';issueCmd(mine.filter(()=>Math.random()<.7),null,{x:t.x,y:t.y})}return [mine.length,en.length]}"""
async def main():
  srv=subprocess.Popen(['node','../server/server.js'],env=dict(os.environ,PORT=str(PORT),FAKE_LAG=str(LAG)),stdout=subprocess.DEVNULL)
  time.sleep(.8)
  try:
   async with async_playwright() as p:
    b=await p.chromium.launch()
    A=await (await b.new_context(viewport={"width":900,"height":420})).new_page();B=await (await b.new_context(viewport={"width":900,"height":420})).new_page()
    errs=[];A.on("pageerror",lambda e:errs.append(str(e)));B.on("pageerror",lambda e:errs.append(str(e)))
    for pg,n in ((A,'Ana'),(B,'Rui')):
      await pg.goto(URL);await pg.wait_for_timeout(300);await pg.evaluate(SPAWN);await pg.evaluate("(u)=>{localStorage.setItem('alv_net',JSON.stringify({url:u}));accPreview();ACC.profile.username='"+n+"'}",f'ws://127.0.0.1:{PORT}/ws');await pg.click('#bOnline');await pg.wait_for_timeout(800)
    await A.click('#olCreate');await A.wait_for_timeout(800);code=await A.evaluate("()=>NET.room");await B.fill('#olJoin',code);await B.click('#olJoinB')
    await A.wait_for_timeout(3000);await A.click('#olStart');await A.wait_for_timeout(1500)
    rtt=await A.evaluate("()=>NET.rtt");d=await A.evaluate("()=>NET.delay")
    await A.evaluate("()=>act('spawn',{n:50})");await B.evaluate("()=>act('spawn',{n:50})");await asyncio.sleep(2)
    t0=time.time();T0=await A.evaluate("()=>NET.turn")
    for k in range(12):
      await asyncio.gather(A.evaluate(ORD),B.evaluate(ORD));await asyncio.sleep(3)
    hs=await asyncio.gather(*[pg.evaluate("()=>({my:[...NET.myHash],d:NET.desync,t:NET.turn,n:__S().ents.filter(e=>e.kind==='u').length,w:NET.stats})") for pg in (A,B)])
    com=[t for t in dict(hs[0]['my']) if t in dict(hs[1]['my'])];eq=all(dict(hs[0]['my'])[t]==dict(hs[1]['my'])[t] for t in com)
    rate=(hs[0]['t']-T0)/(time.time()-t0)
    print(('PASS' if eq and hs[0]['d']==0 and rate>8.5 else 'FAIL').ljust(10)+f"Latência {LAG} ms por sentido (ping medido {rtt} ms, atraso {d} turnos = {d*100} ms): batalha com {hs[0]['n']} unidades vivas no fim, {len(com)} verificações iguais, dessincronizações {hs[0]['d']}/{hs[1]['d']}, ritmo {rate:.1f} turnos/s; dados enviados {hs[0]['w']['bytes']//1024} KB")
    print('ERRS',errs[:3]);await b.close()
  finally:srv.terminate()
asyncio.run(main())
