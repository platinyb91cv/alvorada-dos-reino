# Bot que joga sozinho: só aparece para a conta do criador (aqui simulada com ?bot=teste em localhost); sem isso o botão não existe.
# Com o bot ligado, o reino cresce sozinho (aldeões, edifícios, exército) e a câmara segue a ação; a partida não conta para a pontuação.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); R = {}
        pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(2500)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(1500)
        R['sem_conta'] = await pg.evaluate("()=>{togglePause();const h=$('bBot').hidden;togglePause();botSet(true);return{botao_escondido:h,ligou:BOT.on}}")
        await pg.close()
        pg = await br.new_page(viewport={'width': 1280, 'height': 760})
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(2500)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(1500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        R['antes'] = await pg.evaluate("()=>{togglePause();const vis=!$('bBot').hidden;$('bBot').click();const c=k=>ents.filter(e=>e.o===ME&&(e.type===k)).length;return{botao_visivel:vis,ligou:BOT.on,pausa:paused,aldeoes:c('aldeao'),edificios:ents.filter(e=>e.o===ME&&e.kind==='b').length}}")
        # acelera o tempo: corre a simulação 6 minutos de jogo
        await pg.evaluate("()=>{for(let i=0;i<360*20;i++)step(1/20)}")
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{OUT}/bot_6min.png')
        R['depois_6min'] = await pg.evaluate("()=>{const c=k=>ents.filter(e=>e.o===ME&&e.type===k).length;return{aldeoes:c('aldeao'),edificios:ents.filter(e=>e.o===ME&&e.kind==='b').length,exercito:ents.filter(e=>e.o===ME&&e.kind==='u'&&e.d.mil&&!e.d.king).length,idade:P[ME].age,etiqueta:getComputedStyle($('botTag')).display,conta:G.botUsed}}")
        await pg.evaluate("()=>{for(let i=0;i<360*20;i++)step(1/20)}")
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{OUT}/bot_12min.png')
        R['depois_12min'] = await pg.evaluate("()=>{const c=k=>ents.filter(e=>e.o===ME&&e.type===k).length;return{aldeoes:c('aldeao'),edificios:ents.filter(e=>e.o===ME&&e.kind==='b').length,exercito:ents.filter(e=>e.o===ME&&e.kind==='u'&&e.d.mil&&!e.d.king).length,idade:P[ME].age,rival_edificios:ents.filter(e=>e.o===1&&e.kind==='b').length,acabou:!running}}")
        R['desligar'] = await pg.evaluate("()=>{if(running){botSet(false);return{ligado:BOT.on,ia_do_jogador:!!AIs[ME]}}return 'partida acabou'}")
        R['erros'] = errs; print(json.dumps(R, ensure_ascii=False, indent=1)); await br.close()
asyncio.run(main())
