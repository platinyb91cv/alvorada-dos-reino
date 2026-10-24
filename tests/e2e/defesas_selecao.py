# Seleção de uma muralha com soldados em cima: o painel mostra a guarnição e o botão Sair; tocar em Sair faz descer.
import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        r = await pg.evaluate("""async()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q=centerOf(c);P[ME].age=2;
          let w=null;for(let r=4;r<40&&!w;r++)for(let a=0;a<48&&!w;a++){const x=Math.round(q.x+Math.cos(a/48*6.28)*r),y=Math.round(q.y+Math.sin(a/48*6.28)*r);if(canPlace('muralhaPedra',x,y,ME,0,true))w=mkBld(ME,'muralhaPedra',x,y,true)}
          const a1=mkUnit(ME,'arqueiro',w.tx+.5,w.ty+2),a2=mkUnit(ME,'arqueiro',w.tx+.5,w.ty+2.4);garrisonIn(a1,w);garrisonIn(a2,w);
          sel=[w];uiDirty=true;updateUI();await new Promise(r=>setTimeout(r,300));
          const txt=document.body.innerText;const btn=[...document.querySelectorAll('#cmds *')].find(b=>/Sair \\(2\\)/.test(b.textContent||''));
          const res={painel_guarnicao:/Guarnição: 2\\/2/.test(txt),botao_sair:!!btn};if(btn)btn.click();await new Promise(r=>setTimeout(r,300));res.depois_de_sair=w.garr.length;return res}""")
        print(json.dumps({'r': r, 'errs': errs}, ensure_ascii=False)); await br.close()
asyncio.run(main())
