# Casa do portão: as casas das torres ao lado do portão são sólidas (ninguém passa "por dentro" das torres);
# portão fechado obriga a contornar, aberto deixa passar pelo arco; muralha pode ser construída por cima de uma torre;
# anel de muralhas com portão fechado não deixa sair ninguém.
# Uso: python3 -m http.server 8777 --directory www  e depois  python3 tests/e2e/portoes_flancos.py
import asyncio, json, sys
from playwright.async_api import async_playwright
FIND = "const h=G.starts[ME];let C=null;for(let d=8;d<30&&!C;d++)for(const [sx,sy] of [[1,0],[0,1],[-1,0],[0,-1],[1,1],[-1,1]]){const cx=Math.round(h.x+sx*d),cy=Math.round(h.y+sy*d);let ok=true;for(let y=cy-4;y<=cy+4&&ok;y++)for(let x=cx-4;x<=cx+4;x++)if(!canPlace('muralhaPedra',x,y,ME,0,true)){ok=false;break}if(ok){C={x:cx,y:cy};break}}"
JS = "()=>{startGame(4242,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[1]=null;AI=null;P[ME].age=2;" + FIND + """
 const res={};for(const lock of [true,false]){for(const e of [...ents])if(e.kind==='b'&&e.d.gate)kill(e);const g=mkBld(ME,'portaoPedra',C.x,C.y,true);g.gdir='y';syncGateFlanks();g.locked=lock;
  const us=[];for(let i=0;i<5;i++){const u=mkUnit(ME,'guerreiro',C.x-2+.5,C.y-1.5+i);moveTo(u,C.x+3.5,C.y-1.5+i);us.push(u)}let bad=0,thru=0;
  for(let t=0;t<25*30;t++){step(1/30);for(const u of us){const tx=Math.floor(u.x),ty=Math.floor(u.y);if(tx===C.x&&ty!==C.y&&Math.abs(ty-C.y)<=2)bad++;if(tx===C.x&&ty===C.y)thru++}}
  res[lock?'fechado':'aberto']={dentro_das_torres:bad,pelo_portao:thru>0,chegaram:us.filter(u=>u.x>C.x+2).length};for(const u of us)kill(u)}
 const g=ents.find(e=>e.d&&e.d.gate);res.flancos=[-2,-1,1,2].map(k=>blk[idx(C.x,C.y+k)]);res.muralha_por_cima=canPlace('muralhaPedra',C.x,C.y+1,ME,0,true);
 const w=mkBld(ME,'muralhaPedra',C.x,C.y+1,true);res.blk_muralha=blk[idx(C.x,C.y+1)];kill(w);res.volta=blk[idx(C.x,C.y+1)];kill(g);res.livres=[-2,-1,1,2].map(k=>blk[idx(C.x,C.y+k)]);
 // anel fechado
 for(let x=C.x-3;x<=C.x+3;x++)for(let y=C.y-3;y<=C.y+3;y++){if(Math.max(Math.abs(x-C.x),Math.abs(y-C.y))!==3)continue;mkBld(ME,(x===C.x+3&&y===C.y)?'portaoPedra':'muralhaPedra',x,y,true)}
 const rg=ents.find(e=>e.d&&e.d.gate);rg.locked=true;const ins=[];for(let i=0;i<6;i++){const u=mkUnit(ME,['guerreiro','cavaleiro','aldeao'][i%3],C.x-1+(i%3)*.8+.2,C.y-.5+(i/3|0)*.8);moveTo(u,C.x+9,C.y+1);ins.push(u)}
 for(let t=0;t<25*30;t++)step(1/30);res.anel_fugiram=ins.filter(u=>Math.max(Math.abs(Math.floor(u.x)-C.x),Math.abs(Math.floor(u.y)-C.y))>=3).length;return res}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(3500)
        r = await pg.evaluate(JS); r['erros'] = pe
        ok = (r['fechado']['dentro_das_torres'] == 0 and not r['fechado']['pelo_portao'] and r['aberto']['dentro_das_torres'] == 0 and r['aberto']['pelo_portao']
              and r['flancos'] == [5, 5, 5, 5] and r['muralha_por_cima'] and r['blk_muralha'] == 3 and r['volta'] == 5 and r['livres'] == [0, 0, 0, 0] and r['anel_fugiram'] == 0 and not pe)
        print(json.dumps(r)); print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
