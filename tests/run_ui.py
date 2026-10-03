import asyncio, json, time
from playwright.async_api import async_playwright
GAME="file:///home/claude/alvorada/www/index.html"
OUT="/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width":844,"height":390}, device_scale_factor=2, has_touch=True, is_mobile=True)
        pg = await ctx.new_page()
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
        await pg.goto(GAME); await pg.wait_for_timeout(400)
        R=[]
        # pausa e regresso
        await pg.evaluate("localStorage.clear()")
        await pg.click("#lgPreview"); await pg.click("#bPlay"); await pg.wait_for_timeout(500)
        t0=await pg.evaluate("__S().G.time")
        await pg.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))")
        paused=await pg.evaluate("({p:__S().paused,shown:!document.getElementById('sPause').hidden,title:document.querySelector('#sPause h2').textContent,save:!!localStorage.getItem('alv_save_v1')})")
        await pg.wait_for_timeout(1500)
        await pg.evaluate("Object.defineProperty(document,'hidden',{value:false,configurable:true});document.dispatchEvent(new Event('visibilitychange'))")
        await pg.wait_for_timeout(1500)
        after=await pg.evaluate("({p:__S().paused,t:__S().G.time,ai:__S().AIs[1]&&__S().AIs[1].t})")
        R.append(("Pausa", paused['p'] and paused['shown'] and paused['save'], f"pausou={paused['p']} ecrã '{paused['title']}' visível={paused['shown']} gravou={paused['save']}"))
        R.append(("Retorno da aplicação", after['p'] and abs(after['t']-t0)<0.6, f"continua pausado={after['p']}; tempo de jogo {t0:.2f}→{after['t']:.2f} (IA parada)"))
        await pg.click("#bResume"); await pg.wait_for_timeout(300)
        # auto-save em tempo real (45 s)
        await pg.evaluate("localStorage.removeItem('alv_save_v1')")
        st=time.time();ok=False
        while time.time()-st<52:
            await pg.wait_for_timeout(2000)
            if await pg.evaluate("!!localStorage.getItem('alv_save_v1')"): ok=True;break
        R.append(("Auto-save", ok, f"guardou sozinho após {time.time()-st:.0f} s de jogo real"))
        # continuar a partir do menu
        await pg.evaluate("document.getElementById('bQuit').click()")
        await pg.wait_for_timeout(300)
        cont=await pg.evaluate("!document.getElementById('bCont').hidden")
        await pg.click("#bCont"); await pg.wait_for_timeout(500)
        running=await pg.evaluate("__S().running")
        R.append(("Continuar partida", cont and running, f"botão visível={cont}; jogo retomado={running}"))
        # toque longo → atacar-mover
        lp=await pg.evaluate("""()=>{const s=__S();s.AIs[1]=null;const h=s.G.starts[0];const u=mkUnit(0,'guerreiro',h.x+3.5,h.y+3.5);setSel([u]);centerCam(h.x+3,h.y+3);const p=w2s(h.x+6,h.y+6);return {x:p.x,y:p.y,id:u.id}}""")
        await pg.touchscreen.tap(10,10)
        cdp=await ctx.new_cdp_session(pg)
        await cdp.send("Input.dispatchTouchEvent",{"type":"touchStart","touchPoints":[{"x":lp['x'],"y":lp['y']}]})
        await pg.wait_for_timeout(700)
        await cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[]})
        await pg.wait_for_timeout(200)
        lpr=await pg.evaluate(f"(()=>{{const u=__S().byId.get({lp['id']});return u?{{st:u.state,am:u.amove}}:null}})()")
        R.append(("Toque longo (comandos adicionais)", bool(lpr) and lpr['am'], f"unidade: {lpr}"))
        # capturas: painel de grupo, menu de defesas, muralhas, navios, formação
        await pg.evaluate("""()=>{startGame(404);const s=__S();s.AIs[1]=null;s.P[0].age=2;for(const k in s.P[0].res)s.P[0].res[k]=9999;s.vis.fill(2);
          const h=s.G.starts[0];const dx=Math.sign(40-h.x),dy=Math.sign(40-h.y);const us=[];
          for(let i=0;i<5;i++)us.push(mkUnit(0,'espadachim',h.x+dx*6+i*.5,h.y+dy*6));for(let i=0;i<4;i++)us.push(mkUnit(0,'besteiro',h.x+dx*6+i*.5,h.y+dy*6.8));us.push(mkUnit(0,'trebuchet',h.x+dx*7,h.y+dy*7.6));us.push(mkUnit(0,'cavPesada',h.x+dx*5,h.y+dy*5));us.push(mkUnit(0,'cavArqueira',h.x+dx*5.6,h.y+dy*5));us.push(mkUnit(0,'ariete',h.x+dx*7.6,h.y+dy*7.6));
          for(let k=0;k<7;k++){const x=h.x+dx*9+k,y=h.y+dy*3;if(canPlace('muralhaPedra',x,y,0,0,true))mkBld(0,k===3?'portaoPedra':'muralhaPedra',x,y,true)}
          for(let k=0;k<5;k++){const x=h.x+dx*3+k,y=h.y+dy*9;if(canPlace('muralhaMadeira',x,y,0,0,true))mkBld(0,'muralhaMadeira',x,y,true)}
          const tw=mkBld(0,'torre',h.x+dx*9,h.y+dy*6,true);tw.lvl=3;
          setSel(us);centerCam(h.x+dx*7,h.y+dy*6);}""")
        await pg.wait_for_timeout(600); await pg.screenshot(path=OUT+"ui_group.png")
        await pg.evaluate("document.querySelectorAll('#cmds .cmd').forEach(b=>{if(b.textContent.includes('Formação'))b.click()})"); await pg.wait_for_timeout(300); await pg.screenshot(path=OUT+"ui_form.png")
        await pg.evaluate("""()=>{const s=__S();const v=mkUnit(0,'aldeao',s.G.starts[0].x+2,s.G.starts[0].y+3);setSel([v]);menuMode='def';uiDirty=true}""");await pg.wait_for_timeout(400); await pg.screenshot(path=OUT+"ui_def.png")
        # navios no lago
        await pg.evaluate("""()=>{const s=__S();const L=s.G.lake;const pts=[];for(let y=Math.floor(L.y-3);y<=L.y+3;y++)for(let x=Math.floor(L.x-3);x<=L.x+3;x++)if(s.blk[idx(x,y)]===1)pts.push([x,y]);
          ['barcoPesca','transporte','gale','incendiario','navioPesado'].forEach((t,i)=>{const p=pts[(i*7)%pts.length];mkUnit(0,t,p[0]+.5,p[1]+.5)});
          mkUnit(1,'gale',pts[pts.length-1][0]+.5,pts[pts.length-1][1]+.5);setSel([]);centerCam(L.x,L.y);cam.z=1.1;}""")
        await pg.wait_for_timeout(600); await pg.screenshot(path=OUT+"ui_ships.png")
        # desempenho: frame com ~250 entidades
        perf=await pg.evaluate("""()=>{const s=__S();startGame(101);const S2=__S();S2.AIs[0]=mkAI(0,DIFF[1]);for(let t=0;t<15*60*30;t++)step(1/30);
          const n=__S().ents.length;const t0=performance.now();for(let i=0;i<60;i++)step(1/30);const simMs=(performance.now()-t0)/60;
          const c=document.getElementById('game').getContext('2d');render();render();c.getImageData(0,0,1,1);const r0=performance.now();for(let i=0;i<30;i++){render();c.getImageData(0,0,1,1)}const renMs=(performance.now()-r0)/30;cam.z=.55;clampCam();render();render();c.getImageData(0,0,1,1);const r1=performance.now();for(let i=0;i<30;i++){render();c.getImageData(0,0,1,1)}const farMs=(performance.now()-r1)/30;return {n,simMs:+simMs.toFixed(2),renMs:+renMs.toFixed(2),farMs:+farMs.toFixed(2)}}""")
        R.append(("Desempenho (Chromium headless sem GPU, DPR 2)", perf['simMs']+perf['renMs']<16, f"{perf['n']} entidades: simulação {perf['simMs']} ms + desenho {perf['renMs']} ms por frame (zoom afastado: {perf['farMs']} ms)"))
        for n,ok,d in R: print(f"{'PASS' if ok else 'FAIL':10} {n}: {d}")
        print("ERRS",errs)
        await b.close()
asyncio.run(main())
