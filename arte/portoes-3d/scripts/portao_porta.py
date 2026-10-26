import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(3000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        R=await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);const clear=(x,y)=>{for(let j=-3;j<=4;j++)for(let i=-2;i<=9;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
          let q=null;for(let r=6;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(clear(x,y))q={x,y}}
          P[ME].age=2;P[ME].col='#d23c3c';for(const k in BCACHE)delete BCACHE[k];
          const G=[];for(let i=0;i<7;i++){const b=mkBld(ME,i===3?'portaoPedra':'muralhaPedra',q.x+i,q.y,true);if(i===3)G.push(b)}
          const s=mkUnit(ME,'guerreiro',q.x+3.5,q.y-1.6);window.__s=s;window.__g=G[0];cam.z=2.2;centerCam(q.x+3.5,q.y);return q}""")
        await pg.wait_for_timeout(1200); await pg.screenshot(path='/tmp/claude-0/portao/porta_fechada.png', clip={'x':440,'y':230,'width':400,'height':300})
        await pg.evaluate("()=>{const q=window.__g;moveTo(window.__s,q.tx+.5,q.ty+2.5)}")
        await pg.wait_for_timeout(900); o=await pg.evaluate("()=>window.__g.open"); await pg.screenshot(path='/tmp/claude-0/portao/porta_aberta.png', clip={'x':440,'y':230,'width':400,'height':300})
        print(json.dumps({'open':o,'errors':errs})); await br.close()
asyncio.run(main())
