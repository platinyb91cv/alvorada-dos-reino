# Tutorial completo (12 passos originais + 6 novos: impostos, defesas, torre, sino ligar/desligar, crescimento)
# e o "próximo objetivo" depois do tutorial. Cada passo é cumprido por código e o teste confirma que o tutorial avança.
# Uso: python3 -m http.server 8777 --directory www  e depois  python3 tests/e2e/tutorial.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
H = "const c=ents.find(e=>e.o===ME&&e.type==='centro'),h=centerOf(c);const vil=()=>ents.filter(e=>e.o===ME&&e.type==='aldeao');const spot=t=>{for(let r=3;r<14;r++)for(let a=0;a<24;a++){const x=Math.round(h.x+Math.cos(a/24*6.28)*r),y=Math.round(h.y+Math.sin(a/24*6.28)*r);if(canPlace(t,x,y,ME,0,true))return{x,y}}};const rr=f=>[...byId.values()].filter(r=>r.kind==='r'&&f(r)).sort((a,b)=>hyp(a.tx-h.x,a.ty-h.y)-hyp(b.tx-h.x,b.ty-h.y))[0];"
ACTIONS = [
 "setSel([c])", "queueUnit(c,'aldeao',true)", "setSel([vil()[0]])",
 "orderGather(vil()[0],rr(r=>r.rk==='food'&&!r.fish&&!r.carcass&&!r.walk))", "setSel([vil()[1]]);orderGather(vil()[1],rr(r=>r.rk==='wood'))",
 "setSel([vil()[2]]);menuMode='build';uiDirty=true", "const s=spot('casa');mkBld(ME,'casa',s.x,s.y,true)", "0",
 "const s=spot('quartel');mkBld(ME,'quartel',s.x,s.y,true);mkUnit(ME,'guerreiro',h.x+3,h.y+3)", "P[ME].age=1",
 "const k=ents.find(e=>e.o===ME&&e.type==='casa');for(const q of KINDS)P[ME].res[q]+=500;queueUpgrade(k,true)",
 "document.getElementById('rs_hap').click();document.getElementById('txClose').click()",
 "setSel([vil()[2]]);menuMode='def';uiDirty=true", "const s=spot('torre');mkBld(ME,'torre',s.x,s.y,true)",
 "setSel([c]);act('bell',{on:true})", "act('bell',{on:false})",
 "for(let i=0;i<12;i++)mkUnit(ME,'aldeao',h.x+2+(i%4)*.5,h.y+3+(i/4|0)*.5);for(let i=0;i<5;i++)mkUnit(ME,'guerreiro',h.x-2+i*.5,h.y+4)",
]
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 915, 'height': 412}); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(3500)
        await pg.evaluate("startGame(5,{map:'rios',vic:'classico',civ:['planicies','mar']});document.querySelectorAll('#sMenu,#sLogin').forEach(x=>x.hidden=true);tutStart()"); await pg.wait_for_timeout(800)
        n = await pg.evaluate("TUT_STEPS.length"); passos = []
        for i, a in enumerate(ACTIONS):
            before = await pg.evaluate("G.tut?G.tut.i:-1")
            await pg.evaluate("()=>{" + H + a + "}"); await pg.wait_for_timeout(1300)
            after = await pg.evaluate("G.tut?G.tut.i:-1"); txt = await pg.evaluate("document.querySelector('#coach').innerText.slice(0,70)")
            passos.append({'acao': i, 'de': before, 'para': after, 'texto': txt})
        final = await pg.evaluate("({i:G.tut&&G.tut.i,fim:!!(G.tut&&TUT_STEPS[G.tut.i].end)})")
        await pg.evaluate("tutEnd(false)"); await pg.wait_for_timeout(2600)
        goal = await pg.evaluate("({vis:!document.getElementById('goal').hidden,txt:document.querySelector('#goal .gt').textContent})")
        await pg.screenshot(path=OUT + '/tutorial_objetivo.png')
        r = {'passos_total': n, 'passos': passos, 'final': final, 'objetivo': goal, 'erros': pe}
        ok = n == 18 and final['fim'] and all(x['para'] == x['de'] + 1 for x in passos if x['acao'] != 6 and x['acao'] != 7) and goal['vis'] and len(goal['txt']) > 5 and not pe
        print(json.dumps(r, ensure_ascii=False)); json.dump(r, open(OUT + '/tutorial.json', 'w'), ensure_ascii=False, indent=1)
        print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
