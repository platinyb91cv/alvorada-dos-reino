import asyncio, json, sys
from playwright.async_api import async_playwright
import os
GAME=os.environ.get("ALV_URL","http://localhost:8777/index.html?bot=teste")  # servidor: python3 -m http.server 8777 --directory www
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":844,"height":390}, device_scale_factor=1, has_touch=True)
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
        await pg.goto(GAME); await pg.wait_for_timeout(4000); await pg.evaluate("startGame(7,{map:'rios',vic:'classico'})"); await pg.wait_for_timeout(300)
        await pg.add_script_tag(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"tests.js"))
        res=await pg.evaluate("window.__results")
        for r in res: print(f"{r['res']:10} {r['name']}: {r['detail']}")
        print("ERRS",errs)
        await b.close()
asyncio.run(main())
