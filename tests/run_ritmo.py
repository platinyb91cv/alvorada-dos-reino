# Ritmo do início: o computador manda um assalto pequeno cedo (sem acabar logo com o jogo)
import asyncio, os, sys
from playwright.async_api import async_playwright
GAME="file://"+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','www','index.html'))
R=[]
def rep(ok,name,info):R.append(ok);print(('PASS' if ok else 'FAIL').ljust(6),name+':',info,flush=True)
LIM={0:(9,14),1:(7,11),2:(4.5,8)}
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await (await b.new_context(viewport={"width":900,"height":440})).new_page()
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
    await pg.goto(GAME);await pg.wait_for_timeout(500);await pg.click("#lgPreview")
    for d in [0,1,2]:
      r=await pg.evaluate("""(d)=>{gameMode='normal';difficulty=d;startGame(3000+d,{map:'rios',vic:'classico',civ:['planicies','montanha']});const s=__S();let first=null;const tc=s.ents.find(e=>e.o===0&&e.type==='centro');
        while(s.G.time<25*60&&!s.G.over){step(1/20);if(first==null&&s.ents.some(e=>e.o===1&&e.kind==='u'&&e.d.mil&&hyp(e.x-tc.tx,e.y-tc.ty)<14))first=s.G.time;if(first!=null&&s.G.time>first+120)break}
        return {first:first&&+(first/60).toFixed(1),aliveAfter2min:!s.G.over}}""",d)
      lo,hi=LIM[d];rep(r['first'] is not None and lo<=r['first']<=hi and r['aliveAfter2min'],f"Primeiro assalto ({['Fácil','Normal','Difícil'][d]})",f"chega aos {r['first']} min (alvo {lo}-{hi}); jogador parado ainda vivo 2 min depois: {r['aliveAfter2min']}")
    rep(not errs,"Sem erros de JavaScript","; ".join(errs[:3]) or "nenhum")
    await b.close()
  print(f"\n{sum(R)}/{len(R)} testes passaram");sys.exit(0 if all(R) else 1)
asyncio.run(main())
