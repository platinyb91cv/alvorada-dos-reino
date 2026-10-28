# Muitas partidas rápidas em paralelo para apanhar exceções que matam o ciclo do jogo (o ecrã fica parado).
import asyncio, json, sys, time
from playwright.async_api import async_playwright
OUT=sys.argv[1]; MIN=float(sys.argv[2]); PAR=int(sys.argv[3]); SPEED=sys.argv[4] if len(sys.argv)>4 else '8'; BOTON=sys.argv[5] if len(sys.argv)>5 else 'true'
CFG=[]
for m in ['rios','continental','lagos','arquipelago']:
  for v in ['classico','total']: CFG.append(('jogo',m,v))
CFG += [('camp',i,None) for i in range(12)] + [('reino',0,None),('jogo','rios','sobrevivencia'),('build','rios','classico')]
async def run(br,k,cfg,res):
  ctx=await br.new_context(viewport={'width':915,'height':412}); pg=await ctx.new_page(); errs=[]
  pg.on('pageerror',lambda e: errs.append((getattr(e,'stack',None) or str(e))[:900]))
  try:
    await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(4000)
    kind,a,b=cfg
    if kind=='jogo': await pg.evaluate(f"()=>{{gameMode='normal';difficulty={k%3};startGame({1000+k},{{map:'{a}',vic:'{b}',civ:['planicies','montanha']}})}}")
    elif kind=='build': await pg.evaluate(f"()=>{{gameMode='build';startGame({1000+k},{{map:'{a}',vic:'{b}',civ:['mar','planicies']}})}}")
    elif kind=='camp': await pg.evaluate(f"()=>campStart({a})")
    else: await pg.evaluate("()=>reinoFound()")
    await pg.wait_for_timeout(2500)
    await pg.evaluate(f"()=>{{try{{if({BOTON}&&!BOT.on)botSet(true)}}catch(e){{}};speed={SPEED};}}")
    t0=time.time(); lastT=-1; stuck=0; rows=[]
    while time.time()-t0<MIN*60:
      await pg.wait_for_timeout(10000)
      r=await pg.evaluate("()=>({t:G.time|0,over:G.over,run:running,paused,u:ents.filter(e=>e.kind==='u').length})")
      rows.append(r)
      if r['over'] or not r['run']: break
      if r['t']==lastT and not r['paused']: stuck+=1
      if stuck>=2: break
      lastT=r['t']
    el=await pg.evaluate("()=>ERRLOG.slice()")
    res.append({'k':k,'cfg':cfg,'rows':rows[-3:],'parou':stuck>=2,'erros':errs,'errlog':el})
  except Exception as e: res.append({'k':k,'cfg':cfg,'harness':str(e)[:300],'erros':errs})
  print(json.dumps(res[-1])[:1500],flush=True); await ctx.close()
async def main():
  async with async_playwright() as p:
    br=await p.chromium.launch(); res=[]; sem=asyncio.Semaphore(PAR)
    async def one(k,c):
      async with sem: await run(br,k,c,res)
    await asyncio.gather(*[one(k,c) for k,c in enumerate(CFG)])
    json.dump(res,open(OUT+'/fuzz.json','w'),indent=1); await br.close()
asyncio.run(main())
