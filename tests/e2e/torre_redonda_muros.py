# Torre redonda (nível 3) com muros dos 4 lados: os de trás passam por trás, os da frente param na parede da torre. Uso: python3 torre_redonda_muros.py <imagem.png>
import asyncio, json, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=2;
          const ok=(x,y,w,h)=>{for(let j=-1;j<=h;j++)for(let i=-1;i<=w;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
          let q=null;for(let r=4;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(ok(x,y,10,10))q={x,y}}
          const W=(t,x,y)=>mkBld(ME,t,x,y,true);const t=W('torre',q.x+4,q.y+4);t.lvl=3;
          for(let i=0;i<4;i++){W('muralhaPedra',q.x+i,q.y+4);W('muralhaPedra',q.x+6+i,q.y+5)}
          for(let j=0;j<4;j++){W('muralhaFort',q.x+5,q.y+j);W('muralhaPedra',q.x+4,q.y+6+j)}
          window.__q=q;for(const k in BCACHE)delete BCACHE[k];cam.z=2.4;centerCam(q.x+5,q.y+5)}""")
        await pg.wait_for_timeout(1500); await pg.screenshot(path=sys.argv[1]); print(errs); await br.close()
asyncio.run(main())
