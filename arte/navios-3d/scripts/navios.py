import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'arquipelago',vic:'classico',civ:['mar','planicies']})"); await pg.wait_for_timeout(3000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        r=await pg.evaluate("""()=>{const h=G.starts[0];let q=null;
          for(let r=6;r<60&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(h.x+Math.cos(a/64*6.283)*r),y=Math.round(h.y+Math.sin(a/64*6.283)*r);let ok=true;for(let j=-3;j<=6;j++)for(let i=-3;i<=10;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||terr[idx(tx,ty)]!==1)ok=false}if(ok)q={x,y}}
          if(!q)return 'sem água';P[ME].age=2;const T=['barcoPesca','transporte','gale','incendiario','navioPesado','corsario'];window.__S=T.map((t,i)=>mkUnit(ME,t,q.x+.5+(i%3)*3.2,q.y+.5+Math.floor(i/3)*3));
          window.__q=q;cam.z=1.6;centerCam(q.x+3,q.y+1.5);for(let i=0;i<W*H;i++)vis[i]=2;return{q,ready:T.map(t=>UNIT3D[t]&&UNIT3D[t].ready)}}""")
        await pg.wait_for_timeout(1500); await pg.screenshot(path='/tmp/claude-0/navios/jogo1.png', clip={'x':280,'y':140,'width':720,'height':440})
        await pg.evaluate("()=>{for(const u of window.__S)moveTo(u,u.x+2,u.y+1)}"); await pg.wait_for_timeout(700)
        st=await pg.evaluate("()=>window.__S.map(u=>[u.type,unit3dState(u),unit3dHeading(u)])")
        await pg.screenshot(path='/tmp/claude-0/navios/jogo2.png', clip={'x':280,'y':140,'width':720,'height':440})
        await pg.evaluate("()=>{for(const u of window.__S.slice(2))applyDmg(u,1e6,null,false)}"); await pg.wait_for_timeout(900)
        await pg.screenshot(path='/tmp/claude-0/navios/jogo3.png', clip={'x':280,'y':140,'width':720,'height':440})
        print(json.dumps({'r':r,'st':st,'errs':errs})); await br.close()
asyncio.run(main())
