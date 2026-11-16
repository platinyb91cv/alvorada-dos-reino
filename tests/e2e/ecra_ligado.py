# Ecrã sempre ligado só durante a partida: imita o plugin nativo Ecra (Android) e verifica as mudanças
# menu → partida (liga) → pausa (desliga) → retomar (liga) → fim da partida (desliga) → app em segundo plano (desliga).
# Uso: python3 -m http.server 8777 --directory www  e depois  python3 tests/e2e/ecra_ligado.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 915, 'height': 412}); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.add_init_script("window.__ecra=[];window.Capacitor={Plugins:{Ecra:{ligado:o=>{window.__ecra.push(o.on);return Promise.resolve()}}}}")
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(3500)
        r = {'menu': await pg.evaluate("window.__ecra.slice()")}
        await pg.evaluate("startGame(5,{map:'rios',vic:'classico'});try{tutEnd(true)}catch(e){}"); await pg.wait_for_timeout(1500)
        r['partida'] = await pg.evaluate("window.__ecra.at(-1)")
        await pg.evaluate("togglePause()"); await pg.wait_for_timeout(1500); r['pausa'] = await pg.evaluate("window.__ecra.at(-1)")
        await pg.evaluate("togglePause()"); await pg.wait_for_timeout(1500); r['retomar'] = await pg.evaluate("window.__ecra.at(-1)")
        await pg.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))"); await pg.wait_for_timeout(1200)
        r['segundo_plano'] = await pg.evaluate("window.__ecra.at(-1)")
        await pg.evaluate("Object.defineProperty(document,'hidden',{value:false,configurable:true});document.dispatchEvent(new Event('visibilitychange'));if(paused)togglePause()"); await pg.wait_for_timeout(1500)
        await pg.evaluate("G.over=true"); await pg.wait_for_timeout(1500); r['fim'] = await pg.evaluate("window.__ecra.at(-1)")
        r['erros'] = pe
        ok = all(v is not True for v in r['menu']) and r['partida'] is True and r['pausa'] is False and r['retomar'] is True and r['segundo_plano'] is False and r['fim'] is False and not pe
        print(json.dumps(r)); json.dump(r, open(OUT + '/ecra_ligado.json', 'w'))
        print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
