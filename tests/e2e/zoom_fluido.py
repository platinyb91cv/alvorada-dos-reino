# Fluidez do zoom: ms por frame parado e a fazer zoom contínuo (120 unidades). Uso: python3 tests/e2e/zoom_fluido.py <abrandamento CPU, ex. 1 ou 4>
import asyncio,sys,json
from playwright.async_api import async_playwright
SETUP=sys.argv[2] if len(sys.argv)>2 else '0'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--enable-gpu-rasterization']);ctx=await b.new_context(viewport={'width':900,'height':420},device_scale_factor=2,is_mobile=True,has_touch=True);pg=await ctx.new_page()
        cdp=await ctx.new_cdp_session(pg);await cdp.send('Emulation.setCPUThrottlingRate',{'rate':float(sys.argv[1])})
        await pg.goto('http://localhost:8777/index.html?bot=teste');await pg.wait_for_timeout(3500)
        await pg.evaluate("()=>{startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']});try{tutEnd(true)}catch(e){};document.querySelectorAll('#sMenu,#sLogin').forEach(x=>x.hidden=true);const q=centerOf(ents.find(e=>e.type==='centro'&&e.o===ME));vis.fill(2);const T=['guerreiro','espadachim','lanceiro','arqueiro','cavaleiro','aldeao'];for(let i=0;i<120;i++)mkUnit(i%2?1:ME,T[i%6],q.x-4+(i%12)*.8,q.y+3+(i/12|0)*.8);centerCam(q.x+1,q.y+4);cam.z=1}")
        await pg.evaluate(SETUP);await pg.wait_for_timeout(4000)
        js="""(zoom)=>new Promise(res=>{const T=[];let last=performance.now(),t0=last;const c=centerOf(ents.find(e=>e.type==='centro'&&e.o===ME));
          function f(now){T.push(now-last);last=now;if(zoom){const k=(now-t0)/1000;const z=1+.6*Math.sin(k*2.2);const w={x:innerWidth/2,y:innerHeight/2};const a=s2p(w.x,w.y);cam.z=clamp(z,.45,2.2);const b=s2p(w.x,w.y);cam.x+=(a.x-b.x)*cam.z;cam.y+=(a.y-b.y)*cam.z}
            if(now-t0<6000)requestAnimationFrame(f);else{T.sort((a,b)=>a-b);res({n:T.length,avg:+(T.reduce((s,x)=>s+x,0)/T.length).toFixed(1),p95:+T[Math.floor(T.length*.95)].toFixed(1),max:+T[T.length-1].toFixed(1),u3p:typeof U3P!=='undefined'?U3P.size:null,dpr:DPR})}}requestAnimationFrame(f)})"""
        st=await pg.evaluate(js,False);zm=await pg.evaluate(js,True)
        print('PARADO',json.dumps(st));print('ZOOM  ',json.dumps(zm));await b.close()
asyncio.run(main())
