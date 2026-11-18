# Montagem de teste da fortificação com portão de pedra central (para comparar o encaixe):
# frente com torre grande de canto, troço de muralha, casa do portão (2 torres pequenas + arco), troço de muralha, torre grande de canto.
# Uso: python3 tests/e2e/castelo_portao.py <D: casas do centro do portão até cada canto> <zoom> <imagem.png> [porta do servidor] [muralha]
#   D=3 é a montagem da versão 10 (anel 7×7); D=5 é a corrigida (frente de 11 casas).
import asyncio, json, sys
from playwright.async_api import async_playwright
D = int(sys.argv[1]); Z = float(sys.argv[2]); OUT = sys.argv[3]; PORT = sys.argv[4] if len(sys.argv) > 4 else '8777'; WALL = sys.argv[5] if len(sys.argv) > 5 else 'muralhaFort'
JS = """([D,Z,WALL])=>{startGame(4242,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[1]=null;AI=null;try{tutEnd(true)}catch(e){};P[ME].age=2;vis.fill(2);
  document.querySelectorAll('#sMenu,#sLogin,#goal,#coach').forEach(x=>x.hidden=true);
  // sítio fixo e livre (o mesmo nas duas versões): procura a partir do Centro uma área de (2*6+1)×9 casas
  const h=G.starts[ME];let C=null;
  for(let d=8;d<40&&!C;d++)for(const [sx,sy] of [[1,0],[0,1],[-1,0],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1]]){const cx=Math.round(h.x+sx*d),cy=Math.round(h.y+sy*d);let ok=true;
    for(let y=cy-4;y<=cy+4&&ok;y++)for(let x=cx-6;x<=cx+6;x++)if(!canPlace('muralhaPedra',x,y,ME,0,true)){ok=false;break}if(ok){C={x:cx,y:cy};break}}
  const put=(t,x,y)=>{const b=mkBld(ME,t,x,y,true);if(t==='torre')b.lvl=3;return b};
  const Y0=C.y-3,Y1=C.y+3;const X0=C.x-D,X1=C.x+D;let gate=null;
  for(let x=X0;x<=X1;x++)for(let y=Y0;y<=Y1;y++){const edge=x===X0||x===X1||y===Y0||y===Y1;if(!edge)continue;const corner=(x===X0||x===X1)&&(y===Y0||y===Y1);
    if(corner)put('torre',x,y);else if(x===C.x&&y===Y1)gate=put('portaoPedra',x,y);else put(WALL,x,y)}
  recount();if(typeof syncGateFlanks==='function')syncGateFlanks();
  cam.z=Z;centerCam(C.x,Y1);for(const k in BCACHE)delete BCACHE[k];
  return {C,gate:[gate.tx,gate.ty],eixo:bldVariant(gate),frente:X1-X0+1,dist_canto:D}}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1000, 'height': 560}, device_scale_factor=2); pg = await ctx.new_page(); err = []
        pg.on('pageerror', lambda e: err.append(str(e)[:200]))
        await pg.goto(f'http://localhost:{PORT}/index.html?bot=teste'); await pg.wait_for_timeout(4000)
        r = await pg.evaluate(JS, [D, Z, WALL]); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{const cv=document.querySelector('canvas');const keep=new Set();let n=cv;while(n){keep.add(n);n=n.parentElement}for(const e of document.body.querySelectorAll('*'))if(!keep.has(e)&&e!==cv&&!cv.contains(e)&&!e.contains(cv))e.style.visibility='hidden'}")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=OUT)
        print(json.dumps(r), err[:3]); await b.close()
asyncio.run(main())
