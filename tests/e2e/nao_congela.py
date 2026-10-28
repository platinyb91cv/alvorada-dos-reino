# O jogo não pode congelar por causa de um erro: antes, uma exceção em step() ou render() parava o ciclo para sempre.
# Aqui força-se um erro na simulação e outro no desenho; o ciclo tem de continuar, o tempo de jogo tem de avançar
# e os erros ficam no registo (botão «Copiar erros» no menu de pausa). Também verifica o caso real que travava com o bot (AI nulo).
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 915, 'height': 412}); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(4000)
        await pg.evaluate("startGame(5,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(1500)
        r = {}
        r['passo'] = await pg.evaluate("""async()=>{const o=window.step;let n=0;window.step=s=>{if(++n%2)throw new Error('teste-step');o(s)};
          const t0=G.time;await new Promise(f=>setTimeout(f,1500));window.step=o;return{avancou:G.time>t0,erros:ERRLOG.length}}""")
        r['desenho'] = await pg.evaluate("""async()=>{const o=window.render;let k=0;window.render=()=>{k++;throw new Error('teste-render')};
          await new Promise(f=>setTimeout(f,600));window.render=o;let f2=0;const t=performance.now();await new Promise(res=>{const L=()=>{f2++;if(performance.now()-t<800)requestAnimationFrame(L);else res()};requestAnimationFrame(L)});
          const t0=G.time;await new Promise(f=>setTimeout(f,800));return{chamadas:k,avancou:G.time>t0,registo:ERRLOG.map(e=>e.m.split('\\n')[0])}}""")
        # caso real: bot ligado numa missão sem rival (AI nulo); um ataque às unidades do jogador fazia applyDmg rebentar
        r['ai_nulo'] = await pg.evaluate("""()=>{ERRLOG.length=0;AI=null;AIs[0]={t:12};const v=ents.find(e=>e.kind==='u'&&e.o===0);const w=mkUnit(1,'guerreiro',v.x+.5,v.y);
          let ok=true;try{applyDmg(v,5,w)}catch(e){ok=false}const al=AIs[0].alarm;AIs[0]=null;return{ok,alarme_t:al&&al.t}}""")
        r['botao'] = await pg.evaluate("()=>{ERRLOG.push({m:'x',n:1,t:0});togglePause();const b=$('bErros');const s={visivel:!b.hidden,texto:b.textContent};togglePause();return s}")
        r['erros_pagina'] = pe
        ok = r['passo']['avancou'] and r['passo']['erros'] >= 1 and r['desenho']['chamadas'] > 3 and r['desenho']['avancou'] \
             and any('teste-render' in m for m in r['desenho']['registo']) and r['ai_nulo']['ok'] and r['ai_nulo']['alarme_t'] == 12 and r['botao']['visivel'] and not pe
        print(json.dumps(r, ensure_ascii=False)); json.dump(r, open(OUT + '/nao_congela.json', 'w'), ensure_ascii=False, indent=1)
        print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
