# Missões novas (campanha 12, Reino 12 de história) e bot forte: cada missão nova arranca sem erros e mostra os objetivos;
# o bot constrói uma cidade em grelha, ergue o anel de muralha de pedra com portões e torres. Imagens do bot aos 10 e 18 min.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); R = {}; errs = []
        pg = await br.new_page(viewport={'width': 1280, 'height': 760}); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(2500)
        R['contagem'] = await pg.evaluate("()=>({campanha:CAMP.length,reino_historia:(()=>{let n=0;while(reinoDef(n).story)n++;return n})()})")
        R['campanha_nova'] = []
        for i in range(6, 12):
            r = await pg.evaluate(f"()=>{{campStart({i});for(let k=0;k<60;k++)step(1/20);const ob=campObjs();return CAMP[{i}].t+': '+ob.length+' objetivos'}}")
            R['campanha_nova'].append(r)
        R['reino_novas'] = await pg.evaluate("()=>[2,3,4,5,7,8,9,10].map(n=>{const m=reinoDef(n);return m.t+' ['+m.k+']'})")
        # bot numa partida normal
        await pg.evaluate("startGame(4242,{map:'continental',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(1000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        await pg.evaluate("()=>{botSet(true)}")
        await pg.evaluate("()=>{for(let i=0;i<600*20;i++){step(1/20);if(!running)break}}")
        R['bot_10min'] = await pg.evaluate("()=>{const c=k=>ents.filter(e=>e.o===ME&&e.type===k).length;return{aldeoes:c('aldeao'),casas:c('casa'),muralha_pedra:c('muralhaPedra'),palicada:c('muralhaMadeira'),portoes:c('portaoPedra')+c('portaoMadeira'),torres:c('torre'),exercito:ents.filter(e=>e.o===ME&&e.kind==='u'&&e.d.mil&&!e.d.king).length,idade:P[ME].age}}")
        await pg.evaluate("()=>{const tc=ents.find(e=>e.o===ME&&e.type==='centro');BOT.cam=null;BOT.on=false;cam.z=.8;centerCam(tc.tx+1,tc.ty+1);BOT.on=true;BOT.next=999}"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{OUT}/bot_cidade_10min.png')
        await pg.evaluate("()=>{for(let i=0;i<480*20;i++){step(1/20);if(!running)break}}")
        R['bot_18min'] = await pg.evaluate("()=>{const c=k=>ents.filter(e=>e.o===ME&&e.type===k).length;return{aldeoes:c('aldeao'),edificios:ents.filter(e=>e.o===ME&&e.kind==='b').length,muralha_pedra:c('muralhaPedra'),torres:c('torre'),exercito:ents.filter(e=>e.o===ME&&e.kind==='u'&&e.d.mil&&!e.d.king).length,idade:P[ME].age,rival_cv:ents.some(e=>e.o===1&&e.type==='centro'),partida:running?'a decorrer':(G.won?'vitória':'derrota')}}")
        await pg.evaluate("()=>{const tc=ents.find(e=>e.o===ME&&e.type==='centro');if(tc){BOT.next=999;BOT.cam=null;cam.z=.8;centerCam(tc.tx+1,tc.ty+1)}}"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{OUT}/bot_cidade_18min.png')
        R['erros'] = errs; print(json.dumps(R, ensure_ascii=False, indent=1)); await br.close()
asyncio.run(main())
