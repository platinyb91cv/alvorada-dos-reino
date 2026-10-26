# Castelo (Centro da Vila, Idade do Ferro): o Rei e os soldados abrigados aparecem em cima (Rei no terraço da torre de menagem,
# soldados nas torres, casa do portão e caminhos de ronda), disparam contra atacantes, saem com "Sair"; sem erros de página.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}#top,#bottom,#side,#grp,#toast{display:none!important}')
        R = {}
        R['montar'] = await pg.evaluate("""()=>{P[ME].age=2;for(let i=0;i<vis.length;i++)vis[i]=2;for(const k in BCACHE)delete BCACHE[k];CHUNKS.clear();
          const c=ents.find(e=>e.type==='centro'&&e.o===ME);window.__c=c;const q=centerOf(c);
          const k=ents.find(e=>e.kind==='u'&&e.o===ME&&e.d.king);const us=[];for(let i=0;i<11;i++)us.push(mkUnit(ME,i%3===2?'besteiro':'arqueiro',q.x+2+(i%4)*.4,q.y+2.5+(i>>2)*.4));
          const ids=us.map(u=>u.id);if(k)ids.unshift(k.id);act('garrison',{b:c.id,u:ids});return{castelo:castleTop(c),rei:!!k,cabe:c.d.garr||c.d.pop}}""")
        await pg.wait_for_timeout(8000)
        R['dentro'] = await pg.evaluate("()=>({n:__c.garr.length,rei:__c.garr.some(u=>u.d.king),soldados:__c.garr.filter(u=>u.d.mil&&!u.d.king).length})")
        await pg.evaluate("()=>{const q=centerOf(__c);cam.z=2.6;centerCam(q.x,q.y-.9)}"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{OUT}/castelo_guarnicao.png')
        R['ataque'] = await pg.evaluate("""()=>{const q=centerOf(__c);window.__F=[];for(let k=0;k<10;k++){const sp=snapFree?{x:q.x+4.5+(k%5)*.5,y:q.y-1+(k>>2)*.6}:null;const f=mkUnit(1,k%2?'guerreiro':'espadachim',sp.x,sp.y);__F.push(f);orderAttack(f,__c)}return __F.length}""")
        await pg.wait_for_timeout(2500); await pg.evaluate("()=>{const q=centerOf(__c);cam.z=2.2;centerCam(q.x+1,q.y+.6)}"); await pg.wait_for_timeout(600); await pg.screenshot(path=f'{OUT}/castelo_combate.png')
        await pg.wait_for_timeout(14000)
        R['fim'] = await pg.evaluate("()=>({atacantes_mortos:__F.filter(f=>!alive(f)).length,de:__F.length,castelo_vida:Math.round(__c.hp/__c.max*100)+'%',ainda_dentro:__c.garr.length})")
        R['sair'] = await pg.evaluate("()=>{act('ungarrison',{b:__c.id});return __c.garr.length}")
        R['erros'] = errs; print(json.dumps(R, ensure_ascii=False)); await br.close()
asyncio.run(main())
