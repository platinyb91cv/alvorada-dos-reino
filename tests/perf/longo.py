# Partida longa num "telemóvel" simulado: CPU 4x mais lenta, ecrã 915x412 a DPR 2,6, bot a jogar a 3x.
# Amostra a cada 15 s: tempo por imagem (média, p95, máx), bloqueios >200 ms, memória JS, memória das telas (canvas), caches, entidades.
import asyncio, json, sys, time
from playwright.async_api import async_playwright
OUT = sys.argv[1]; MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 8; THR = float(sys.argv[3]) if len(sys.argv) > 3 else 4; SPEED = sys.argv[4] if len(sys.argv) > 4 else '3'
INIT = r"""
(()=>{const live=[];const oc=document.createElement.bind(document);
 document.createElement=function(t,...a){const e=oc(t,...a);if(String(t).toLowerCase()==='canvas')live.push(new WeakRef(e));return e};
 window.__cv=()=>{let px=0,n=0,big=0;for(let i=live.length-1;i>=0;i--){const c=live[i].deref();if(!c){live.splice(i,1);continue}n++;const p=c.width*c.height;px+=p;if(p>=1024*1024)big++}return{n,mb:Math.round(px*4/1048576),big}};
 window.__ft=[];window.__lt=[];let last=performance.now();
 const loop=t=>{window.__ft.push(t-last);last=t;requestAnimationFrame(loop)};requestAnimationFrame(loop);
 try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__lt.push([Math.round(e.startTime),Math.round(e.duration)])}).observe({type:'longtask',buffered:true})}catch(e){}
})();"""
SAMPLE = r"""()=>{const f=window.__ft.splice(0);f.sort((a,b)=>a-b);const n=f.length||1;const lt=window.__lt.splice(0);
 const m=performance.memory||{};const cv=window.__cv();
 let bc=0;try{bc=Object.keys(BCACHE).length}catch(e){}
 return{t:Math.round(G?G.time:0),fps:Math.round(n/15),avg:+(f.reduce((a,b)=>a+b,0)/n).toFixed(1),p95:Math.round(f[Math.floor(n*.95)]||0),max:Math.round(f[n-1]||0),
  longos:lt.filter(x=>x[1]>=200).length,pior_bloqueio:lt.reduce((a,x)=>Math.max(a,x[1]),0),
  heap_mb:Math.round((m.usedJSHeapSize||0)/1048576),canvas_mb:cv.mb,canvas_n:cv.n,canvas_grandes:cv.big,
  bcache:bc,ucache:UCACHE.size,ucbytes_mb:Math.round(UCBYTES/1048576),chunks:CHUNKS.size,
  ents:ents.length,unidades:ents.filter(e=>e.kind==='u').length,projs:projs.length,fx:fx.length,dpr:DPR,running:running}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--enable-precise-memory-info','--js-flags=--expose-gc'])
        ctx = await br.new_context(viewport={'width': 915, 'height': 412}, device_scale_factor=2.6, is_mobile=True, has_touch=True)
        await ctx.add_init_script(INIT); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setCPUThrottlingRate', {'rate': THR})
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(6000)
        await pg.evaluate("startGame(4242,{map:'continental',vic:'total',civ:['planicies','mar']})"); await pg.wait_for_timeout(3000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        await pg.evaluate(f"()=>{{botSet(true);speed={SPEED};window.__ft=[];window.__lt=[]}}")
        rows = []; t0 = time.time()
        while time.time() - t0 < MIN * 60:
            await pg.wait_for_timeout(15000)
            r = await pg.evaluate(SAMPLE); rows.append(r); print(json.dumps(r), flush=True)
            if not r['running']: break
        await pg.screenshot(path=f'{OUT}/fim.png')
        json.dump({'rows': rows, 'erros': errs, 'thr': THR, 'speed': SPEED}, open(f'{OUT}/longo.json', 'w'), indent=1)
        print('erros', errs); await br.close()
asyncio.run(main())
