# Zoom com gestos reais (roda do rato no PC; pinça com dois dedos em modo telemóvel): ms por frame e tarefas longas (>50 ms).
# Uso: python3 tests/e2e/zoom_toque.py <abrandamento CPU> <pc|mob>
import asyncio,sys,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();mob=sys.argv[2]=='mob'
        ctx=await b.new_context(viewport={'width':900,'height':420},device_scale_factor=2 if mob else 1,is_mobile=mob,has_touch=mob);pg=await ctx.new_page();err=[]
        pg.on('pageerror',lambda e:err.append(str(e)[:200]));pg.on('console',lambda m:err.append(m.text[:200]) if m.type=='error' else None)
        cdp=await ctx.new_cdp_session(pg);await cdp.send('Emulation.setCPUThrottlingRate',{'rate':float(sys.argv[1])})
        await pg.goto('http://localhost:8777/index.html?bot=teste');await pg.wait_for_timeout(3500)
        await pg.evaluate("()=>{startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']});try{tutEnd(true)}catch(e){};document.querySelectorAll('#sMenu,#sLogin').forEach(x=>x.hidden=true);const q=centerOf(ents.find(e=>e.type==='centro'&&e.o===ME));centerCam(q.x+1,q.y+4);cam.z=1;window.__lt=[];new PerformanceObserver(l=>{for(const e of l.getEntries())__lt.push([Math.round(e.startTime),Math.round(e.duration)])}).observe({entryTypes:['longtask']});window.__fr=[];let last=performance.now();(function f(n){__fr.push([Math.round(n),Math.round(n-last)]);last=n;requestAnimationFrame(f)})(last)}")
        await pg.wait_for_timeout(3000);t0=await pg.evaluate('performance.now()')
        if mob:
            cx,cy=450,210
            for rep in range(3):
                for d0,d1 in ((60,200),(200,60)):
                    await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':cx-d0,'y':cy},{'x':cx+d0,'y':cy}]})
                    for s in range(25):
                        d=d0+(d1-d0)*(s+1)/25
                        await cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':cx-d,'y':cy},{'x':cx+d,'y':cy}]});await pg.wait_for_timeout(16)
                    await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});await pg.wait_for_timeout(300)
        else:
            await pg.mouse.move(450,210)
            for rep in range(3):
                for dy in (-100,100):
                    for s in range(10):await pg.mouse.wheel(0,dy);await pg.wait_for_timeout(40)
                    await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(3000)
        r=await pg.evaluate("(t0)=>{const fr=__fr.filter(x=>x[0]>t0).map(x=>x[1]).sort((a,b)=>a-b);return {z:cam.z,frames:fr.length,avg:+(fr.reduce((s,x)=>s+x,0)/fr.length).toFixed(1),p95:fr[Math.floor(fr.length*.95)],max:fr[fr.length-1],longtasks:__lt.filter(x=>x[0]>t0).sort((a,b)=>b[1]-a[1]).slice(0,8),dpr:DPR,chunks:CHUNKS.size,u3p:U3P.size}}",t0)
        print(json.dumps(r));print('ERR',err[:5]);await b.close()
asyncio.run(main())
