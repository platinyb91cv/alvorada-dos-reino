# "Modo produção": cada missão corre sozinha (sem atalhos) durante vários minutos de jogo, com a IA e as vagas reais.
# Regista erros, tempo por passo da simulação, contagens de unidades e se o jogo acaba/continua bem.
import asyncio, json, time
from playwright.async_api import async_playwright
SIM = 360  # segundos de jogo por missão
RUN = """async(sec)=>{const t0=performance.now();let errs=[];const n=Math.round(sec/0.1);let worst=0;
  for(let i=0;i<n;i++){const a=performance.now();try{step(0.1)}catch(e){errs.push(String(e&&e.stack||e).slice(0,300));break}const d=performance.now()-a;if(d>worst)worst=d;if(G.over)break;
    if(i%300===299){await new Promise(r=>setTimeout(r,0))}}
  return{ms:Math.round(performance.now()-t0),passos:n,piorPassoMs:+worst.toFixed(1),errs,t:Math.round(G.time),over:G.over,
    eu:ents.filter(e=>e.o===0&&e.kind==='u').length,inimigos:ents.filter(e=>e.o===1&&e.kind==='u').length,edif:ents.filter(e=>e.o===0&&e.kind==='b').length,ents:ents.length}}"""
async def main():
    res = {'campanha': [], 'reino': [], 'escaramuca': None, 'pageerrors': []}
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760})
        pg.on('pageerror', lambda e: res['pageerrors'].append(str(e)[:300]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(2500); await pg.evaluate("()=>localStorage.clear()")
        for i in range(6):
            await pg.evaluate(f"()=>campStart({i})"); await pg.wait_for_timeout(300)
            r = await pg.evaluate(RUN, SIM); r['missao'] = i + 1; res['campanha'].append(r); print('CAMP', json.dumps(r)[:300], flush=True)
        # reino: capítulos de combate correm sozinhos
        await pg.evaluate("()=>reinoFound()"); await pg.wait_for_timeout(400)
        for n in (2, 3, 4, 6, 7, 9, 10):
            await pg.evaluate("(n)=>{const R=G.reino;R.ms=null;R.n=n;P[0].age=Math.max(P[0].age,n>=6?1:0);reinoStart(n)}", n)
            r = await pg.evaluate(RUN, 150); r['cap'] = n + 1; r['tipo'] = await pg.evaluate("(n)=>reinoDef(n).k", n); r['objs'] = await pg.evaluate("()=>G.reino.ms?reinoObjs(G.reino.ms):'cumprido'")
            res['reino'].append(r); print('REINO', json.dumps(r)[:300], flush=True)
            if r['over']:
                await pg.evaluate("()=>reinoFound()"); await pg.wait_for_timeout(400)
        # escaramuça normal contra IA difícil (como um jogador)
        await pg.evaluate("()=>{difficulty=2;startGame(777,{map:'continental',vic:'classico',civ:['planicies','montanha']})}"); await pg.wait_for_timeout(300)
        r = await pg.evaluate(RUN, 600); res['escaramuca'] = r; print('ESCARAMUCA', json.dumps(r)[:300], flush=True)
        # desenho: alguns segundos a renderizar de verdade (FPS)
        await pg.evaluate("()=>{running=true;paused=false}")
        fps = await pg.evaluate("""()=>new Promise(r=>{let n=0;const t0=performance.now();function f(){n++;if(performance.now()-t0<3000)requestAnimationFrame(f);else r(Math.round(n/3))}requestAnimationFrame(f)})""")
        res['fpsHeadless'] = fps
        await br.close()
    json.dump(res, open('/tmp/claude-0/missoes/producao.json', 'w'), ensure_ascii=False, indent=1)
    print('PAGEERRORS', len(res['pageerrors']), res['pageerrors'][:3], 'FPS', res['fpsHeadless'])
asyncio.run(main())
