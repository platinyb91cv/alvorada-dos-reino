# Partidas IA contra IA em várias dificuldades e mapas (registo por minuto: aldeões, exército, idade, níveis, castelo, melhorias, reparações, recuos).
# Uso: python3 tests/e2e/ia_partidas.py '[[seed,difAzul,difVermelho,minutos,"mapa"],...]'   (dificuldades: 0 Fácil, 1 Normal, 2 Difícil)
import asyncio, json, sys
from playwright.async_api import async_playwright
JS=r"""
(a)=>{const [seed,d0,d1,mins,map]=a;
  startGame(seed,{map:map||'continental',vic:'classico',civ:['planicies','planicies']});
  AIs[0]=mkAI(0,DIFF[d0]);AIs[1]=mkAI(1,DIFF[d1]);AI=AIs[1];
  const log=[];let maxDmg=[0,0],repairs=[0,0];const T0=performance.now();let over=null;
  for(let t=0;t<mins*60*30;t++){step(1/30);
    if(t%30===0){for(const e of ents)if(e.kind==='u'&&e.o<2&&e.type==='aldeao'&&e.state==='build'&&e.bld&&e.bld.done&&e.bld.hp<e.bld.max)repairs[e.o]++;}
    if(t%(60*30)===0){const m=t/1800;const row={m};for(let o=0;o<2;o++){const mine=ents.filter(e=>e.o===o);
      const bl=mine.filter(e=>e.kind==='b');
      row['p'+o]={v:mine.filter(e=>e.type==='aldeao').length,army:mine.filter(e=>e.kind==='u'&&e.d.mil&&!e.d.king).length,age:P[o].age,
        res:KINDS.map(k=>Math.round(P[o].res[k])).join('/'),b:bl.length,dmg:bl.filter(b=>b.done&&b.hp<b.max*.7).length,lvl:Math.max(1,...bl.map(b=>b.lvl||1)),techs:Object.keys(P[o].techs).length,idle:mine.filter(e=>e.type==='aldeao'&&e.state==='idle').length,
        wonder:bl.some(b=>b.type==='maravilha'),walls:bl.filter(b=>b.d.wall||b.d.gate).length,castle:bl.some(b=>b.type==='centro'&&(b.lvl||1)>=3),ai:(({ups,reps,retreats,recalls,wonderTry,lastEval})=>({ups,reps,retreats,recalls,wonderTry,lastEval}))(AIs[o]||{})}}
      log.push(row)}
    if(G.over){over=(t/1800).toFixed(1);break}}
  return{over,winner:over?(ents.some(e=>e.o===0&&e.type==='centro')?'P0':'P1'):null,repairs,simMs:Math.round(performance.now()-T0),log,errs:ERRLOG.map(e=>e.m.slice(0,120)).slice(0,5)}
}
"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch();pg=await br.new_page(viewport={'width':915,'height':412});pe=[]
        pg.on('pageerror',lambda e:pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste');await pg.wait_for_timeout(4000)
        for args in json.loads(sys.argv[1] if len(sys.argv)>1 else '[[101,1,1,45,"continental"],[303,2,2,45,"rios"],[505,0,1,45,"lagos"]]'):
            r=await pg.evaluate(JS,args)
            print('RUN',args,'over',r['over'],r['winner'],'repairs',r['repairs'],'simMs',r['simMs'],'errs',r['errs'])
            for row in r['log']:
                if row['m']%5==0 or row is r['log'][-1]:print(' ',json.dumps(row,ensure_ascii=False))
        print('PAGEERR',pe[:5]);await br.close()
asyncio.run(main())
