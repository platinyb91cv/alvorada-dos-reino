# Centro da Vila na Idade do Ferro = castelo pintado: vista de perto (com e sem grelha ?iso=1), cores de 2 equipas, menu; sem erros.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); R = {}
        for dbg in ('', '?iso=1'):
            pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8777/index.html' + dbg); await pg.wait_for_timeout(3500)
            n = 'dbg' if dbg else 'normal'
            if not dbg: await pg.screenshot(path=f'{OUT}/menu.png')
            await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
            await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}#top,#bottom,#side,#grp,#toast{display:none!important}')
            R['r'] = await pg.evaluate("""()=>{for(const p of P)if(p)p.age=2;for(let i=0;i<vis.length;i++)vis[i]=2;for(const k in BCACHE)delete BCACHE[k];CHUNKS.clear();
              const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q=centerOf(c);cam.z=2.2;centerCam(q.x,q.y-.6);return{tx:c.tx,ty:c.ty,key:bld3dKey('centro',2,0)}}""")
            await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{OUT}/centro_{n}.png')
            if not dbg:
                await pg.evaluate("""()=>{const cv=document.createElement('canvas');cv.width=1280;cv.height=420;cv.style.cssText='position:fixed;left:0;top:0;z-index:999';document.body.appendChild(cv);
                  const c=cv.getContext('2d');c.fillStyle='#3d6a2c';c.fillRect(0,0,1280,420);let x=20;
                  for(let o=0;o<P.length;o++){if(!P[o])continue;const s=bldSprite('centro',2,o,0);c.drawImage(s.cv,x,10,s.CW*1.7,s.CH*1.7);x+=s.CW*1.7+20}}"""); await pg.wait_for_timeout(500)
                await pg.screenshot(path=f'{OUT}/centro_equipas.png', clip={'x': 0, 'y': 0, 'width': 1280, 'height': 420})
            R['erros_' + n] = errs; await pg.close()
        print(json.dumps(R)); await br.close()
asyncio.run(main())
