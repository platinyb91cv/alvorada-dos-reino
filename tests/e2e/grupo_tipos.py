# Seleção em grupo: com o exército todo selecionado, tocar num tipo (ex.: arqueiro) deixa só esse tipo; "Todos" volta ao grupo.
# Uso: python3 -m http.server 8777 --directory www  e depois  python3 tests/e2e/grupo_tipos.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, is_mobile=True, has_touch=True); pg = await ctx.new_page(); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(3500)
        await pg.evaluate("""()=>{startGame(5,{map:'rios',vic:'classico'});try{tutEnd(true)}catch(e){};document.querySelectorAll('#sMenu,#sLogin').forEach(x=>x.hidden=true);
          const h=centerOf(ents.find(e=>e.o===ME&&e.type==='centro'));const T=['guerreiro','guerreiro','guerreiro','arqueiro','arqueiro','lanceiro','lanceiro','lanceiro','lanceiro','cavaleiro'];T.forEach((t,i)=>mkUnit(ME,t,h.x+2+(i%5)*.7,h.y+3+(i/5|0)*.7))}""")
        await pg.wait_for_timeout(500); await pg.click('#bArmy'); await pg.wait_for_timeout(800)
        r = {'todos': await pg.evaluate("sel.length")}
        await pg.screenshot(path=OUT + '/grupo_antes.png')
        await pg.click('#info [data-gt="arqueiro"]'); await pg.wait_for_timeout(600)
        r['so_arqueiros'] = await pg.evaluate("({n:sel.length,tipos:[...new Set(sel.map(u=>u.type))]})")
        r['botao_todos'] = await pg.evaluate("!!document.querySelector('#info [data-gt=\"*\"]')")
        await pg.screenshot(path=OUT + '/grupo_arqueiros.png')
        await pg.click('#info [data-gt="*"]'); await pg.wait_for_timeout(600)
        r['de_volta'] = await pg.evaluate("sel.length")
        await pg.click('#info [data-gt="lanceiro"]'); await pg.wait_for_timeout(400); r['so_lanceiros'] = await pg.evaluate("sel.length")
        r['erros'] = pe
        ok = r['todos'] >= 10 and r['so_arqueiros'] == {'n': 2, 'tipos': ['arqueiro']} and r['botao_todos'] and r['de_volta'] == r['todos'] and r['so_lanceiros'] == 4 and not pe
        print(json.dumps(r)); print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
