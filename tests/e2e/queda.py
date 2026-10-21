import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(2500); await pg.evaluate("()=>localStorage.clear()")
        await pg.evaluate("()=>reinoFound()"); await pg.wait_for_timeout(500)
        r=[]
        for t in (2,10,40):
            await pg.evaluate(f"()=>{{for(let i=0;i<{t*10};i++)step(.1)}}")
            r.append(await pg.evaluate("()=>({t:Math.round(G.time),kings:ents.filter(e=>e.o===0&&e.kind==='u'&&e.d.king).length,tc:ents.filter(e=>e.o===0&&e.type==='centro').map(e=>e.done),hero:JSON.stringify(G.hero&&G.hero[0]).slice(0,120),ms:G.reino.ms&&G.reino.ms.k})"))
        await pg.evaluate("()=>{for(const e of ents.filter(e=>e.o===0&&e.kind==='u'&&e.d.king))applyDmg(e,1e7,null,false)}")
        await pg.evaluate("()=>{for(let i=0;i<20;i++)step(.1)}"); await pg.wait_for_timeout(1600)
        r.append(await pg.evaluate("()=>({over:G.over,end:!$('sEnd').hidden,title:$('endTitle').textContent,text:$('endText').textContent,again:$('bAgain').textContent,kings:ents.filter(e=>e.o===0&&e.kind==='u'&&e.d.king).length})"))
        print(json.dumps(r,ensure_ascii=False,indent=0), errs); await br.close()
asyncio.run(main())
