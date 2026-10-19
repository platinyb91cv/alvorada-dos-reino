# Teste no jogo: cria os cinco soldados, faz caminhar nas 8 direções, combate, dano e morte; capturas reais do canvas.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1]; URL = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:8766/index.html'
T = ['guerreiro', 'lanceiro', 'espadachim', 'arqueiro', 'besteiro']
SETUP = """()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);
 const clear=(x,y)=>{for(let j=-5;j<=5;j++)for(let i=-5;i<=14;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty)))return false}return true};
 let q=null;for(let r=4;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(clear(x+5,y+6))q={x,y,found:1}}
 q=q||q0;window.__q=q;window.__U=[];
 for(const e of ents.filter(e=>e.kind==='u'&&e.o===ME&&e.type==='aldeao'))e.state='idle';
 %s.forEach((t,i)=>{const u=mkUnit(ME,t,q.x+5+i*2.2,q.y+6);ents.push(u);byId.set(u.id,u);window.__U.push(u)});
 cam.z=2.2;centerCam(q.x+9,q.y+6.5);
 return [q,...window.__U.map(u=>({t:u.type,file:UNIT3D[u.type]&&UNIT3D[u.type].meta.file,ready:UNIT3D[u.type]&&UNIT3D[u.type].ready}))]}""" % json.dumps(T)
MOVE = """(k)=>{const V=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]];const [dx,dy]=V[k];
 window.__U.forEach((u,i)=>{const bx=window.__q.x+5+i*2.2,by=window.__q.y+6;u.x=bx;u.y=by;u.state='idle';u.path=null;moveTo(u,bx+dx*4,by+dy*4)});
 return window.__U.map(u=>[u.type,u.state,u.path?u.path.length:-1])}"""
PROBE = """()=>window.__U.map(u=>({t:u.type,s:unit3dState(u),dir:unit3dHeading(u),hp:Math.round(u.hp),alive:u.hp>0}))"""
FIGHT = """()=>{const q=window.__q;window.__E=[];window.__U.forEach((u,i)=>{const e=mkUnit(1,'guerreiro',u.x+(u.d.range>1?3:.9),u.y+.6);e.hp=e.max=400;ents.push(e);byId.set(e.id,e);window.__E.push(e);orderAttack(u,e);orderAttack(e,u)});
 cam.z=2.2;centerCam(q.x+9,q.y+6.8);return window.__E.length}"""
KILL = """()=>{window.__E.forEach(e=>{e.state='idle';e.target=null});window.__U.forEach((u,i)=>applyDmg(u,u.hp+5,window.__E[i],false));return window.__U.map(u=>u.hp)}"""
CAM = """()=>{const U=window.__U.filter(u=>ents.includes(u));const L=U.length?U:window.__U;const x=L.reduce((a,u)=>a+u.x,0)/L.length,y=L.reduce((a,u)=>a+u.y,0)/L.length;cam.z=2.4;centerCam(x,y+.5);return [x,y]}"""
async def snap(pg, path):
    await pg.evaluate(CAM); await pg.wait_for_timeout(120); await pg.screenshot(path=path, clip={"x": 240, "y": 120, "width": 800, "height": 460})
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader']); pg = await b.new_page(viewport={'width': 1280, 'height': 760})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        reqs = []; pg.on('response', lambda r: reqs.append((r.url.split('/')[-1].split('?')[0], r.status)) if 'units3d' in r.url else None)
        await pg.goto(URL); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(4000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        res = {'setup': await pg.evaluate(SETUP)}; await pg.wait_for_timeout(1500)
        await snap(pg, f'{OUT}/jogo-1-parados.png'); res['walk'] = {}
        for k, lab in enumerate(['SE', 'S', 'SW', 'W', 'NW', 'N', 'NE', 'E']):
            res.setdefault('orders',{})[lab]=await pg.evaluate(MOVE, k); await pg.wait_for_timeout(700); res['walk'][lab] = await pg.evaluate(PROBE)
            await snap(pg, f'{OUT}/jogo-2-marcha-{lab}.png')
        await pg.wait_for_timeout(2500)
        res['fight'] = await pg.evaluate(FIGHT); await pg.wait_for_timeout(1600); res['attack'] = await pg.evaluate(PROBE)
        await snap(pg, f'{OUT}/jogo-3-combate.png'); await pg.wait_for_timeout(1500); res['damaged'] = await pg.evaluate(PROBE)
        await pg.evaluate(KILL); await pg.wait_for_timeout(900); await snap(pg, f'{OUT}/jogo-4-mortes.png')
        res['dead'] = await pg.evaluate("()=>window.__U.map(u=>({t:u.type,alive:ents.includes(u)&&u.hp>0}))")
        res['corpses'] = await pg.evaluate("()=>fx.filter(f=>f.type==='die'&&"+json.dumps(T)+".includes(f.ut)).map(f=>f.ut)")
        res['atlasRequests'] = sorted(set(reqs)); res['errors'] = errs
        print(json.dumps(res, indent=1)); await b.close()
asyncio.run(main())
