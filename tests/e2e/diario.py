import asyncio, json, sys
sys.path.insert(0, '/tmp/claude-0/missoes')
from playwright.async_api import async_playwright
src = open('/tmp/claude-0/missoes/teste_missoes.py').read()
HELP = src.split('HELP = r"""')[1].split('"""')[0]; SOLVE = src.split('REINO_SOLVE = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(2500); await pg.evaluate("()=>localStorage.clear()")
        await pg.evaluate("()=>reinoFound()"); await pg.wait_for_timeout(400); await pg.evaluate(HELP)
        await pg.evaluate("()=>{const R=G.reino;R.n=3;reinoStart(3)}")  # missão normal em curso (rival)
        before = await pg.evaluate("()=>({n:G.reino.n,ms:G.reino.ms.k})")
        await pg.evaluate("()=>reinoDailyStart()"); await pg.evaluate("()=>QA.run(2)")
        d = await pg.evaluate("()=>({k:G.reino.ms.k,daily:G.reino.ms.daily,t:G.reino.ms.t,susp:G.reino.susp&&G.reino.susp.k})")
        objs = await pg.evaluate(SOLVE, 0); await pg.evaluate("()=>QA.run(2.5)")
        after = await pg.evaluate("()=>({n:G.reino.n,ms:G.reino.ms&&G.reino.ms.k,daily:G.reino.ms&&G.reino.ms.daily,best:JSON.parse(localStorage.getItem(ukey('alv_daily'))||'null'),errs:QA.errs})")
        print(json.dumps({'antes':before,'diario':d,'objs':objs,'depois':after,'pageerrors':errs},ensure_ascii=False)); await br.close()
asyncio.run(main())
