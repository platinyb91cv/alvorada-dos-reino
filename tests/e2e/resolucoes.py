# Interface em várias resoluções (telemóvel pequeno, telemóvel, tablet, computador): sem deslocamento horizontal,
# barra de cima, painel de comandos, minimapa e objetivo dentro do ecrã e sem sobreposição entre a barra e o objetivo.
# Uso: python3 -m http.server 8777 --directory www  e depois  python3 tests/e2e/resolucoes.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
SIZES = [(640, 360, 2, True), (844, 390, 3, True), (1280, 800, 2, True), (1600, 900, 1, False)]
CHECK = """()=>{const R=id=>{const e=document.getElementById(id)||document.querySelector(id);if(!e||e.hidden)return null;const b=e.getBoundingClientRect();return b.width?{l:b.left,t:b.top,r:b.right,b:b.bottom}:null};
  const inside=b=>!b||(b.l>=-1&&b.t>=-1&&b.r<=innerWidth+1&&b.b<=innerHeight+1);
  const top=R('.resbar')||R('#rs_food'),goal=R('#goal'),cmds=R('#cmds'),mini=R('#mini')||R('#minimap');
  return {scrollX:document.documentElement.scrollWidth>innerWidth+1,top:inside(top),goal:inside(goal),cmds:inside(cmds),mini:inside(mini),
    sobreposicao:!!(top&&goal&&goal.t<top.b-1&&goal.l<top.r&&goal.r>top.l),goal_visivel:!!goal}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); res = {}; pe = []
        for w, h, dpr, mob in SIZES:
            ctx = await br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr, is_mobile=mob, has_touch=mob); pg = await ctx.new_page()
            pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
            await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(3500)
            await pg.evaluate("startGame(5,{map:'rios',vic:'classico'});try{tutEnd(true)}catch(e){};document.querySelectorAll('#sMenu,#sLogin').forEach(x=>x.hidden=true);setSel([ents.find(e=>e.o===ME&&e.type==='centro')]);uiDirty=true")
            await pg.wait_for_timeout(3000); k = f'{w}x{h}'; res[k] = await pg.evaluate(CHECK)
            await pg.screenshot(path=f'{OUT}/ui_{k}.png'); await ctx.close()
        ok = all(not v['scrollX'] and v['top'] and v['goal'] and v['cmds'] and v['mini'] and not v['sobreposicao'] and v['goal_visivel'] for v in res.values()) and not pe
        print(json.dumps({'resultados': res, 'erros': pe})); json.dump(res, open(OUT + '/resolucoes.json', 'w'), indent=1)
        print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
