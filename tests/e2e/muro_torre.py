import asyncio, json, sys
from playwright.async_api import async_playwright
OUT=sys.argv[1]
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        r=await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=2;
          const ok=(x,y,w,h)=>{for(let j=-1;j<=h;j++)for(let i=-1;i<=w;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
          let q=null;for(let r=4;r<60&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(ok(x,y,14,10))q={x,y}}
          const W=(t,x,y)=>mkBld(ME,t,x,y,true);
          // linha em x: muro - portão - muro - torre - muro ; e uma linha em y com portão e canto
          for(let i=0;i<12;i++){const x=q.x+i,y=q.y+2;if(i===3)W('portaoPedra',x,y);else if(i===7||i===8){if(i===7)W('torre',x,y-1)}else W('muralhaPedra',x,y)}
          for(let j=3;j<10;j++){const x=q.x,y=q.y+j;if(j===6)W('portaoMadeira',x,y);else W('muralhaPedra',x,y)}
          for(let i=1;i<6;i++)W('muralhaMadeira',q.x+i,q.y+9);
          cam.z=2;centerCam(q.x+5,q.y+5);for(const k in BCACHE)delete BCACHE[k];return q}""")
        await pg.wait_for_timeout(2000); await pg.screenshot(path=OUT)
        print(json.dumps({'q':r,'errs':errs})); await br.close()
asyncio.run(main())
