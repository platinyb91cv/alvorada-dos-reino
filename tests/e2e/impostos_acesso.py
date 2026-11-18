# Acesso aos impostos: carinha 🙂💰 na barra de cima, botão 💰 Impostos no Centro da Vila e no menu de pausa;
# aviso a piscar quando a população passa dos 10. Uso: python3 tests/e2e/impostos_acesso.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, is_mobile=True, has_touch=True); pg = await ctx.new_page(); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(3500)
        await pg.evaluate("startGame(5,{map:'rios',vic:'classico'});try{tutEnd(true)}catch(e){};document.querySelectorAll('#sMenu,#sLogin').forEach(x=>x.hidden=true)"); await pg.wait_for_timeout(1000)
        r = {}
        await pg.evaluate("setSel([ents.find(e=>e.o===ME&&e.type==='centro')]);uiDirty=true"); await pg.wait_for_timeout(800)
        r['botao_centro'] = await pg.evaluate("!!document.querySelector('#cmds button[data-k=\"💰\"]')")
        await pg.screenshot(path=OUT + '/impostos_centro.png')
        await pg.click('#cmds button[data-k="💰"]'); await pg.wait_for_timeout(500)
        r['abre_pelo_centro'] = await pg.evaluate("!document.getElementById('mTax').hidden")
        await pg.screenshot(path=OUT + '/impostos_painel.png')
        await pg.evaluate("document.getElementById('mTax').hidden=true"); await pg.click('#rs_hap'); await pg.wait_for_timeout(300)
        r['abre_pela_carinha'] = await pg.evaluate("!document.getElementById('mTax').hidden")
        await pg.evaluate("document.getElementById('mTax').hidden=true;togglePause()"); await pg.wait_for_timeout(500)
        r['botao_pausa_visivel'] = await pg.evaluate("(()=>{const b=document.getElementById('bTaxP');return !!b&&b.offsetWidth>0})()")
        await pg.click('#bTaxP'); await pg.wait_for_timeout(400)
        r['abre_pela_pausa'] = await pg.evaluate("!document.getElementById('mTax').hidden&&!paused")
        await pg.evaluate("document.getElementById('mTax').hidden=true;const h=G.starts[ME];for(let i=0;i<10;i++)mkUnit(ME,'aldeao',h.x+2+i*.4,h.y+3);recount();G.taxSeen=0;G.taxHint=0"); await pg.wait_for_timeout(2500)
        r['aviso'] = await pg.evaluate("!!G.taxHint")
        r['erros'] = pe; ok = all(v for k, v in r.items() if k != 'erros') and not pe
        print(json.dumps(r)); print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
