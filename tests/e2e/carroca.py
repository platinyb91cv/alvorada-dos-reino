# Carroça de carga: aldeões a cortar madeira longe do Centro descarregam na carroça; ela leva ao armazém e volta.
import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(2500); await pg.evaluate("()=>localStorage.clear()")
        await pg.evaluate("()=>{campStart(0)}"); await pg.wait_for_timeout(300)
        setup = await pg.evaluate("""()=>{P[0].age=1;const tc=ents.find(e=>e.o===0&&e.type==='centro');const c=centerOf(tc);
          // árvore longe (14-22 casas) do Centro
          let tree=null,bd=0;for(const r of byId.values()){if(r.kind!=='r'||r.rk!=='wood')continue;const d=hyp(r.tx-c.x,r.ty-c.y);if(d>14&&d<22&&(!tree||d<bd)){tree=r;bd=d}}
          const vs=[];for(let i=0;i<5;i++){const v=mkUnit(0,'aldeao',tree.tx+.5+(i%3)*.4,tree.ty+1.5);orderGather(v,tree);vs.push(v.id)}
          const cart=mkUnit(0,'carrocaCarga',tree.tx+2.5,tree.ty+2.5);window.__c=cart;window.__vs=vs;window.__w0=P[0].res.wood;
          return{dist:Math.round(bd),cart:cart.type,cargo:cart.d.cargo,treinoArmazem:BLDS.armazem.train}}""")
        log=[]
        for k in range(14):
            await pg.evaluate("()=>{for(let i=0;i<50;i++)step(.1)}")
            log.append(await pg.evaluate("""()=>{const c=window.__c,vs=window.__vs.map(id=>byId.get(id)).filter(Boolean);const tc=ents.find(e=>e.o===0&&e.type==='centro');const cc=centerOf(tc);
              return{t:Math.round(G.time),carga:c.cargaN||0,estado:c.state,distCarroCentro:Math.round(hyp(c.x-cc.x,c.y-cc.y)),madeiraGanha:P[0].res.wood-window.__w0,
                aldeoesPertoDoCentro:vs.filter(v=>hyp(v.x-cc.x,v.y-cc.y)<5).length,estados:vs.map(v=>v.state).join(',')}}"""))
        # gravar e carregar com carga
        info = await pg.evaluate("()=>{selected=[window.__c];uiDirty=true;return JSON.parse(serialize()).ents.find(e=>e.t==='carrocaCarga')}")
        print(json.dumps({'setup':setup,'log':log,'gravado':info and info.get('ca'),'errs':errs},ensure_ascii=False,indent=0)); await br.close()
asyncio.run(main())
