# Prova visual do mercado (modelo GLB): mercado do jogador e de outra equipa, lado a lado e de perto, sem erros de página.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/mercado3d'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(3000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        r = await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=1;const foe=P.findIndex((p,i)=>i!==ME&&p);
          const put=(o,t)=>{for(let r=4;r<30;r++)for(let a=0;a<48;a++){const tx=Math.round(q0.x+Math.cos(a/48*6.283)*r),ty=Math.round(q0.y+Math.sin(a/48*6.283)*r);if(canPlace(t,tx,ty,ME,0,true))return mkBld(o,t,tx,ty,true)}return null};
          const m1=put(ME,'mercado'),m2=put(foe,'mercado'),h=put(ME,'casa');
          for(const e of ents)if(e.kind==='u')e.hp=e.hp; // nada a fazer: só a prova visual
          const m=centerOf(m1);cam.z=1.6;centerCam(m.x,m.y);for(const k in BCACHE)delete BCACHE[k];
          return{ready:BLD3D.ready,key1:bld3dKey('mercado',1,0),key2:bld3dKey('mercado',2,0),usa3d:!!bld3dSprite('mercado',1,ME,0),cores:[P[ME].col,P[foe].col],
            pos:[[m1.tx,m1.ty],[m2.tx,m2.ty]],casa:!!h}}""")
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{OUT}/mercado_perto.png')
        await pg.evaluate("()=>{cam.z=1.0;const m=ents.find(e=>e.type==='mercado'&&e.o===ME);const q=centerOf(m);centerCam(q.x,q.y)}")
        await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{OUT}/mercado_aldeia.png')
        print(json.dumps({'r': r, 'errs': errs})); await br.close()
asyncio.run(main())
