import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(2500)
        await pg.evaluate("()=>{localStorage.setItem(ukey('alv_camp'),'6');campOpen()}")
        out=[]
        for i in range(6):
            await pg.evaluate(f"()=>{{campSel={i};campRender()}}"); out.append(await pg.evaluate("()=>[...document.querySelectorAll('#cmInfo li')].map(l=>l.textContent)"))
        await pg.evaluate("()=>{$('sCamp').hidden=true;campStart(5);P[0].age=2;const w=mkBld(0,'maravilha',G.starts[0].x+5|0,G.starts[0].y+5|0,true);G.wonder={o:0,id:w.id,t:120};objRender()}")
        lab=await pg.evaluate("()=>[...document.querySelectorAll('#objList li')].map(l=>l.textContent)")
        print(out[1], out[5], lab, errs); await br.close()
asyncio.run(main())
