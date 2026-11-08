import asyncio
from playwright.async_api import async_playwright
async def shot(br,dsf,out):
    ctx=await br.new_context(viewport={'width':780,'height':360},device_scale_factor=dsf,is_mobile=True,has_touch=True)
    pg=await ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
    await pg.goto('http://localhost:8777/index.html');await pg.wait_for_timeout(2500)
    await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
    await pg.evaluate("startGame(4242,{map:'continental',vic:'classico',civ:['planicies','mar']})")
    await pg.evaluate("()=>{const tc=ents.find(e=>e.o===ME&&e.type==='centro');for(const [t,dx,dy] of [['casa',4,0],['quartel',-5,0],['mercado',0,4]])mkBld(ME,t,tc.tx+dx,tc.ty+dy,true);cam.z=1.1;centerCam(tc.tx+1,tc.ty+1)}")
    await pg.wait_for_timeout(4000)
    r=await pg.evaluate("()=>({DPR,canvas:cv.width+'x'+cv.height})")
    await pg.screenshot(path=out);print(dsf,r,errs);await ctx.close()
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch()
        await shot(br,1,'/tmp/claude-0/sp/hd_antes_1x.png');await shot(br,3,'/tmp/claude-0/sp/hd_depois_3x.png');await br.close()
asyncio.run(main())
