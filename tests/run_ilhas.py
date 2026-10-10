# Arquipélago: o computador tem de conseguir levar o exército de barco e atacar a ilha do jogador
import asyncio, os, sys, json
from playwright.async_api import async_playwright
GAME="file://"+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','www','index.html'))
SEEDS=[1003,3131,6767,7878]
R=[]
def rep(ok,name,info):R.append(ok);print(('PASS' if ok else 'FAIL').ljust(6),name+':',info,flush=True)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await (await b.new_context(viewport={"width":900,"height":440})).new_page()
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
    await pg.goto(GAME);await pg.wait_for_timeout(500);await pg.click("#lgPreview")
    # mapas: a partir de cada início chega-se a pé ao mar
    bad=await pg.evaluate("""()=>{const out=[];for(let seed=3100;seed<3140;seed++){gameMode='normal';startGame(seed,{map:'arquipelago',vic:'classico',civ:['planicies','mar']});
      for(const o of [0,1]){const st=__S().G.starts[o];const v=__S().ents.find(e=>e.o===o&&e.type==='aldeao');setMover(v);const R=reachFrom(st.x,st.y+3);let coast=0;const MW=mainWater(),WL=waterLab();
        for(let i=0;i<R.length&&coast<3;i++)if(R[i]){const x=i%W,y=(i/W)|0;for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const xx=x+dx,yy=y+dy;if(inb(xx,yy)&&terr[idx(xx,yy)]===1&&WL[idx(xx,yy)]===MW){coast++;break}}}
        if(coast<3)out.push(seed+':'+o)}}return out}""")
    rep(not bad,"Ilhas: do início chega-se a pé ao mar",f"40 mapas, sem saída: {bad or 'nenhum'}")
    for seed in SEEDS:
      r=await pg.evaluate("""(seed)=>{gameMode='normal';difficulty=1;startGame(seed,{map:'arquipelago',vic:'classico',civ:['planicies','mar']});const s=__S();let land=null;
        const L0=landOf(s.G.starts[0].x,s.G.starts[0].y);
        while(s.G.time<35*60&&!s.G.over){step(1/20);if(land==null&&s.ents.some(e=>e.o===1&&e.kind==='u'&&!e.d.naval&&landOf(e.x,e.y)===L0))land=s.G.time}
        return {land:land&&+(land/60).toFixed(1),end:+(s.G.time/60).toFixed(1),over:s.G.over}}""",seed)
      rep(r['land'] is not None and r['land']<30 and r['over'],f"Ilhas: o computador desembarca e ataca (mapa {seed})",f"desembarque aos {r['land']} min; partida acabou aos {r['end']} min")
    rep(not errs,"Sem erros de JavaScript","; ".join(errs[:3]) or "nenhum")
    await b.close()
  print(f"\n{sum(R)}/{len(R)} testes passaram");sys.exit(0 if all(R) else 1)
asyncio.run(main())
