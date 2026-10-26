# Torre de nível 2 = torre quadrada pintada com catapulta no terraço: imagem de perto, a catapulta dispara pedras contra inimigos
# (a 2-9 casas), os arqueiros abrigados ficam no terraço; sem erros de página.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}#top,#bottom,#side,#grp,#toast{display:none!important}')
        R = {}
        R['montar'] = await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=2;for(let i=0;i<vis.length;i++)vis[i]=2;
          let t=null;for(let r=6;r<40&&!t;r++)for(let a=0;a<48&&!t;a++){const tx=Math.round(q0.x+Math.cos(a/48*6.283)*r),ty=Math.round(q0.y+Math.sin(a/48*6.283)*r);if(canPlace('torre',tx,ty,ME,0,true))t=mkBld(ME,'torre',tx,ty,true)}
          t.lvl=2;window.__t=t;const us=[0,1,2].map(k=>mkUnit(ME,'arqueiro',t.tx+k*.4,t.ty+2.6));act('garrison',{b:t.id,u:us.map(u=>u.id)});
          for(const k in BCACHE)delete BCACHE[k];CHUNKS.clear();return{nome:TOWER[2].name,key:bld3dKey('torre',2,2),topo:TOPZ(t)}}""")
        await pg.wait_for_timeout(4000)
        await pg.evaluate("()=>{cam.z=2.2;centerCam(__t.tx-2,__t.ty-2)}"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{OUT}/torre2_perto.png')
        R['ataque'] = await pg.evaluate("""()=>{window.__F=[];for(let k=0;k<6;k++){const f=mkUnit(1,'espadachim',__t.tx+6+(k%3)*.6,__t.ty+1+(k>>1)*.5);__F.push(f)}const n0=projs.length;window.__s0=0;return __F.length}""")
        await pg.wait_for_timeout(3000)
        await pg.evaluate("()=>{cam.z=1.6;centerCam(__t.tx,__t.ty-2)}"); await pg.wait_for_timeout(400); await pg.screenshot(path=f'{OUT}/torre2_dispara.png')
        await pg.wait_for_timeout(12000)
        R['fim'] = await pg.evaluate("()=>({inimigos_mortos:__F.filter(f=>!alive(f)).length,de:__F.length,catapulta_disparou:__t.cfire!=null,em_cima:__t.garr.length})")
        R['erros'] = errs; print(json.dumps(R, ensure_ascii=False)); await br.close()
asyncio.run(main())
