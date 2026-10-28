# Leva uma partida com o bot até ao fim do jogo (rápido, sem limitar o CPU) e depois grava um perfil de CPU de 40 s num "telemóvel" (CPU 4x).
import asyncio, json, sys, collections
from playwright.async_api import async_playwright
OUT=sys.argv[1]; TGT=int(sys.argv[2]) if len(sys.argv)>2 else 600
INIT=r"""(()=>{window.__lt=[];try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lt.push([Math.round(e.startTime),Math.round(e.duration)])}).observe({type:'longtask',buffered:true})}catch(e){}})();"""
async def main():
  async with async_playwright() as p:
    br=await p.chromium.launch(); ctx=await br.new_context(viewport={'width':915,'height':412},device_scale_factor=2.6,is_mobile=True,has_touch=True)
    await ctx.add_init_script(INIT); pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)[:300]))
    await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(5000)
    await pg.evaluate("startGame(4242,{map:'continental',vic:'total',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
    await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
    await pg.evaluate("()=>{botSet(true);speed=8}")
    while (await pg.evaluate("G.time"))<TGT: await pg.wait_for_timeout(5000)
    await pg.evaluate("()=>{speed=3;window.__lt=[]}")
    cdp=await ctx.new_cdp_session(pg); await cdp.send('Emulation.setCPUThrottlingRate',{'rate':4})
    await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval',{'interval':500}); await cdp.send('Profiler.start')
    await pg.wait_for_timeout(40000)
    prof=(await cdp.send('Profiler.stop'))['profile']; lt=await pg.evaluate("window.__lt")
    json.dump(prof,open(OUT+'/cpu.cpuprofile','w'))
    nodes={n['id']:n for n in prof['nodes']}; self_=collections.Counter()
    dts=prof['timeDeltas']; 
    for s,dt in zip(prof['samples'],dts): n=nodes[s]['callFrame']; self_[(n['functionName'] or '(anon)')+':'+str(n['lineNumber'])]+=dt
    tot=sum(self_.values()); print('total ms',tot/1000)
    for k,v in self_.most_common(45): print(f'{v/tot*100:5.1f}%  {v/1000:8.0f}ms  {k}')
    # tempo inclusivo por função
    par={}; 
    for n in prof['nodes']:
      for c in n.get('children',[]): par[c]=n['id']
    inc=collections.Counter()
    for s,dt in zip(prof['samples'],dts):
      seen=set(); x=s
      while x in nodes:
        f=nodes[x]['callFrame']; k=(f['functionName'] or '(anon)')+':'+str(f['lineNumber'])
        if k not in seen: inc[k]+=dt; seen.add(k)
        x=par.get(x)
    print('--- inclusivo'); 
    for k,v in inc.most_common(60): print(f'{v/tot*100:5.1f}%  {k}')
    print('longos', sorted(lt,key=lambda x:-x[1])[:15], 'n>=200:',sum(1 for x in lt if x[1]>=200)); print('erros',errs)
    await br.close()
asyncio.run(main())
