# Loja (desligada por defeito e em modo de teste com ?loja=teste): itens, compra simulada, cores/capas desbloqueadas,
# anúncio com recompensa (+ouro só contra a IA, uma vez por partida), sem erros de página.
import asyncio, sys, json
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); R = {}
        # 1) normal: loja visível mas sem compras, sem botão de anúncio
        pg = await br.new_page(viewport={'width': 800, 'height': 360}, device_scale_factor=2); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(2500)
        R['normal'] = await pg.evaluate("""()=>{lojaOpen();return{itens:document.querySelectorAll('#ljList .lj').length,comprar:document.querySelectorAll('#ljList button[data-id]').length,aviso:$('ljAviso').textContent,anuncio:ADS.pode()}}""")
        await pg.screenshot(path=OUT + '/loja_desligada.png')
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2000)
        R['normal_pausa'] = await pg.evaluate("()=>{togglePause();return $('bAdGold').hidden}")
        await pg.close()
        # 2) teste: compra simulada, desbloqueio e anúncio
        pg = await br.new_page(viewport={'width': 800, 'height': 360}, device_scale_factor=2)
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?loja=teste'); await pg.wait_for_timeout(2500)
        await pg.evaluate("()=>{try{localStorage.removeItem(ukey('alv_loja'))}catch(e){}lojaOpen()}"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=OUT + '/loja_teste.png')
        R['antes'] = await pg.evaluate("()=>({turquesa:cosmOk(999,'cor_turquesa'),capas:LOJA.has('capas_reais'),comprar:document.querySelectorAll('#ljList button[data-id]').length})")
        await pg.click('#ljList button[data-id="pacote_real"]'); await pg.wait_for_timeout(1200)
        R['depois_pacote'] = await pg.evaluate("()=>({turquesa:cosmOk(999,'cor_turquesa'),indigo:cosmOk(999,'cor_indigo'),capas:LOJA.has('capas_reais'),fundador:LOJA.has('fr4'),ja_tens:[...document.querySelectorAll('#ljList .lj.own')].length})")
        R['cor_aplicada'] = await pg.evaluate("()=>{cosmSet('col','#1fb3c6');return myColor()[2]}")
        R['capa_guardada'] = await pg.evaluate("()=>{const L=kingLookClean({name:'Teste',crown:0,cape:'#12a5b8'});return L.cape}")
        await pg.evaluate("()=>{$('sLoja').hidden=true}")
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        R['cor_no_jogo'] = await pg.evaluate("()=>P[ME].col")
        g0 = await pg.evaluate("()=>P[ME].res.gold")
        await pg.evaluate("()=>togglePause()"); await pg.wait_for_timeout(300)
        R['botao_anuncio'] = await pg.evaluate("()=>!$('bAdGold').hidden&&$('bAdGold').textContent")
        await pg.click('#bAdGold'); await pg.wait_for_timeout(600); await pg.screenshot(path=OUT + '/anuncio_teste.png'); await pg.wait_for_timeout(3200)
        R['ouro'] = await pg.evaluate("(g0)=>({ganho:P[ME].res.gold-g0,botao_escondido:$('bAdGold').hidden,segunda_vez:adGoldOk()})", g0)
        R['online_sem_anuncio'] = await pg.evaluate("()=>{const a=NET.on;NET.on=true;const r=adGoldOk();NET.on=a;return r}")
        await pg.evaluate("()=>togglePause()")
        R['errs'] = errs; print(json.dumps(R, ensure_ascii=False, indent=1)); await br.close()
asyncio.run(main())
