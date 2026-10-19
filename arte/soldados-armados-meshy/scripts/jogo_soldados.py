# Teste no jogo: cria os cinco soldados, faz caminhar nas 8 direções, combate, dano e morte; capturas reais do canvas.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1]; URL = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:8766/index.html'
T = ['guerreiro', 'lanceiro', 'espadachim', 'arqueiro', 'besteiro']
SETUP = """()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q=centerOf(c);window.__q=q;window.__U=[];
 for(const e of ents.filter(e=>e.kind==='u'&&e.o===ME&&e.type==='aldeao'))e.state='idle';
 %s.forEach((t,i)=>{const u=mkUnit(ME,t,q.x+4+i*1.6,q.y+4);ents.push(u);byId.set(u.id,u);window.__U.push(u)});
 cam.z=2.2;centerCam(q.x+7,q.y+4.5);
 return window.__U.map(u=>({t:u.type,file:UNIT3D[u.type]&&UNIT3D[u.type].meta.file,ready:UNIT3D[u.type]&&UNIT3D[u.type].ready}))}""" % json.dumps(T)
MOVE = """(k)=>{const V=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]];const [dx,dy]=V[k];
 window.__U.forEach((u,i)=>{const bx=window.__q.x+4+i*1.6,by=window.__q.y+4;u.x=bx;u.y=by;moveTo(u,bx+dx*3,by+dy*3)});
 return window.__U.map(u=>[u.type,u.state])}"""
PROBE = """()=>window.__U.map(u=>({t:u.type,s:unit3dState(u),dir:unit3dHeading(u),hp:Math.round(u.hp),alive:u.hp>0}))"""
FIGHT = """()=>{const q=window.__q;window.__E=[];window.__U.forEach((u,i)=>{const e=mkUnit(1,'guerreiro',u.x+(u.d.range>1?3:.9),u.y+.6);e.hp=e.max=400;ents.push(e);byId.set(e.id,e);window.__E.push(e);orderAttack(u,e);orderAttack(e,u)});
 cam.z=2.2;centerCam(q.x+7,q.y+4.8);return window.__E.length}"""
KILL = """()=>{window.__U.forEach(u=>{u.hp=Math.min(u.hp,3)});return window.__U.map(u=>u.hp)}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader']); pg = await b.new_page(viewport={'width': 1280, 'height': 760})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        reqs = []; pg.on('response', lambda r: reqs.append((r.url.split('/')[-1].split('?')[0], r.status)) if 'units3d' in r.url else None)
        await pg.goto(URL); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(4000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        res = {'setup': await pg.evaluate(SETUP)}; await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{OUT}/jogo-1-parados.png'); res['walk'] = {}
        for k, lab in enumerate(['SE', 'S', 'SW', 'W', 'NW', 'N', 'NE', 'E']):
            await pg.evaluate(MOVE, k); await pg.wait_for_timeout(450); res['walk'][lab] = await pg.evaluate(PROBE)
            if lab in ('SE', 'W', 'NE'): await pg.screenshot(path=f'{OUT}/jogo-2-marcha-{lab}.png')
        await pg.wait_for_timeout(2500)
        res['fight'] = await pg.evaluate(FIGHT); await pg.wait_for_timeout(1600); res['attack'] = await pg.evaluate(PROBE)
        await pg.screenshot(path=f'{OUT}/jogo-3-combate.png'); await pg.wait_for_timeout(1500); res['damaged'] = await pg.evaluate(PROBE)
        await pg.evaluate(KILL); await pg.wait_for_timeout(2200); await pg.screenshot(path=f'{OUT}/jogo-4-mortes.png')
        res['dead'] = await pg.evaluate("()=>window.__U.map(u=>({t:u.type,alive:ents.includes(u)&&u.hp>0}))")
        res['corpses'] = await pg.evaluate("()=>fx.filter(f=>f.type==='die'&&"+json.dumps(T)+".includes(f.ut)).map(f=>f.ut)")
        res['atlasRequests'] = sorted(set(reqs)); res['errors'] = errs
        print(json.dumps(res, indent=1)); await b.close()
asyncio.run(main())
