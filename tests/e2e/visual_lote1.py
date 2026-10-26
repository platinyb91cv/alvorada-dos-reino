import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(3000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        r=await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);const clear=(x,y)=>{for(let j=-4;j<=10;j++)for(let i=-4;i<=12;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
          let q=null;for(let r=5;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(clear(x,y))q={x,y}}
          P[ME].age=2;const cat=mkUnit(ME,'catapulta',q.x+1,q.y+1),car=mkUnit(ME,'carroca',q.x+4,q.y+1),cg=mkUnit(ME,'carrocaCarga',q.x+7,q.y+1),cp=mkUnit(ME,'cavPesada',q.x+2,q.y+4),cv=mkUnit(ME,'cavaleiro',q.x+5,q.y+4);
          let h=null;for(let r=5;r<10&&!h;r++)for(let a=0;a<24&&!h;a++){const tx=Math.round(q.x+1+Math.cos(a/24*6.283)*r),ty=Math.round(q.y+1+Math.sin(a/24*6.283)*r);if(canPlace('casa',tx,ty,1,0,true))h=mkBld(1,'casa',tx,ty,true)}
          orderAttack(cat,h);moveTo(car,q.x+12,q.y+2);moveTo(cg,q.x+12,q.y+5);window.__U={cp,cv};cam.z=1.9;centerCam(q.x+4,q.y+3);
          return{ready:['catapulta','carroca','carrocaCarga','cavPesada'].map(t=>UNIT3D[t]&&UNIT3D[t].ready)}}""")
        await pg.wait_for_timeout(1200)
        # cavalaria: trote ao arrancar
        await pg.evaluate("()=>{const {cp,cv}=window.__U;moveTo(cp,cp.x+8,cp.y+3);moveTo(cv,cv.x+8,cv.y+3)}")
        await pg.wait_for_timeout(250); g1=await pg.evaluate("()=>[window.__U.cp.gait,unit3dState(window.__U.cp),+(window.__U.cp.v||0).toFixed(2)]")
        await pg.screenshot(path='/tmp/claude-0/cerco2/jogo1.png', clip={'x':300,'y':130,'width':680,'height':440})
        await pg.wait_for_timeout(1600); g2=await pg.evaluate("()=>[window.__U.cp.gait,unit3dState(window.__U.cp),+(window.__U.cp.v||0).toFixed(2)]")
        await pg.screenshot(path='/tmp/claude-0/cerco2/jogo2.png', clip={'x':300,'y':130,'width':680,'height':440})
        print(json.dumps({'r':r,'arranque':g1,'emCorrida':g2,'errs':errs})); await br.close()
asyncio.run(main())
