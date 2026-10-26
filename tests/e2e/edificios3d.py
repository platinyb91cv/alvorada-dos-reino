# Prova visual: uma aldeia com os edifícios 3D (idade 1 e 2, torre nos 3 níveis), sem erros de página.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/edificios3d'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        res = {}
        for age in (0, 1, 2):
            await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
            await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(3000)
            await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
            r = await pg.evaluate("""(age)=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=age;
              const list=['casa','armazem','quartel','arquearia','estabulo','ferreiro','templo','mercado','oficina','torre','torre','torre','casa','casa'];const made=[];
              for(const t of list){let ok=null;for(let r=3;r<40&&!ok;r++)for(let a=0;a<48&&!ok;a++){const tx=Math.round(q0.x+Math.cos(a/48*6.283)*r),ty=Math.round(q0.y+Math.sin(a/48*6.283)*r);if(canPlace(t,tx,ty,ME,0,true)){ok=mkBld(ME,t,tx,ty,true);ok.__qa=1}}
                if(ok){if(t==='torre'){const n=made.filter(x=>x==='torre').length+1;ok.lvl=n}made.push(t)}}
              cam.z=1.25;centerCam(q0.x,q0.y);for(const k in BCACHE)delete BCACHE[k];
              return{ready:BLD3D.ready,made,key:bld3dKey('quartel',age,0),usa3d:!!bld3dSprite('casa',age,ME,0)}}""", age)
            await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{OUT}/aldeia_idade{age}.png'); res[age] = r
        print(json.dumps({'res': res, 'errs': errs})); await br.close()
asyncio.run(main())
