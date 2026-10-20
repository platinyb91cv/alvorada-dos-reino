import asyncio, json, sys
from playwright.async_api import async_playwright
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/claude-0/portao_'
SETUP="""(age)=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);const clear=(x,y)=>{for(let j=-2;j<=12;j++)for(let i=-2;i<=12;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
 let q=window.__q;if(!q){for(let r=6;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(clear(x,y))q={x,y}}window.__q=q}
 for(const e of ents.slice())if(e.kind==='b'&&e.__test){killB?killB(e):0}
 P[ME].age=age;for(const k in BCACHE)delete BCACHE[k];
 const mk=(t,x,y,gd)=>{const b=mkBld(ME,t,q.x+x,q.y+y,true);b.__test=1;if(gd)b.gdir=gd;return b};
 // linha ao longo de x: madeira, pedra, fortificada; e uma ao longo de y
 for(let i=0;i<7;i++)mk(i===3?'portaoMadeira':'muralhaMadeira',i,0);
 for(let i=0;i<7;i++)mk(i===3?'portaoPedra':'muralhaPedra',i,3);
 for(let i=0;i<7;i++)mk(i===3?'portaoPedra':'muralhaFort',i,6);
 for(let j=0;j<7;j++)mk(j===3?'portaoMadeira':'muralhaMadeira',9,j);
 for(let j=0;j<7;j++)mk(j===3?'portaoPedra':'muralhaPedra',11,j);
 cam.z=1.6;centerCam(q.x+6,q.y+4);return q}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(3000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        for age in (0,1,2):
            await pg.goto('http://localhost:8777/index.html') if age else None
            if age:
                await pg.wait_for_timeout(3000); await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(3000)
                await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
            q=await pg.evaluate(SETUP,age); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=f'{OUT}era{age}.png', clip={'x':240,'y':100,'width':800,'height':560})
        print(json.dumps({'errors':errs})); await br.close()
asyncio.run(main())
