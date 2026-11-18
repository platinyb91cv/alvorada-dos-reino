# Pré-visualização do portão de pedra: vermelho quando a casa do portão (arco + 2 casas de cada lado, na orientação dele)
# encosta a uma torre de canto (torre até 3 casas na mesma linha) ou a uma esquina de muralha; válido ao ligar muralhas em linha reta.
# Testa as duas orientações (x e y) e os dois cantos de cada lado. Uso: python3 tests/e2e/portao_previa.py
import asyncio, json, sys
from playwright.async_api import async_playwright
JS = """()=>{startGame(4242,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[1]=null;AI=null;P[ME].age=2;vis.fill(2);
 const h=G.starts[ME];const free=(x0,y0,x1,y1)=>{for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++)if(!canPlace('muralhaPedra',x,y,ME,0,true))return false;return true};
 let C=null;for(let d=8;d<45&&!C;d++)for(const [sx,sy] of [[1,0],[0,1],[-1,0],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1]]){const cx=Math.round(h.x+sx*d),cy=Math.round(h.y+sy*d);if(free(cx-7,cy-7,cx+7,cy+7)){C={x:cx,y:cy};break}}
 const out={};const clear=()=>{for(const e of [...ents])if(e.kind==='b'&&e.o===ME&&(e.d.wall||e.d.gate||e.type==='torre')&&Math.abs(e.tx-C.x)<9&&Math.abs(e.ty-C.y)<9)kill(e)};
 for(const ax of ['x','y']){const L=(k)=>ax==='x'?[C.x+k,C.y]:[C.x,C.y+k];
   // linha reta de muralha de -6 a +6 com torres de canto nas pontas (-6 e +6); o portão vai-se movendo ao longo dela
   clear();for(let k=-6;k<=6;k++){const [x,y]=L(k);if(Math.abs(k)===6){const t=mkBld(ME,'torre',x,y,true);t.lvl=3}else mkBld(ME,'muralhaPedra',x,y,true)}
   const res={};for(let k=-5;k<=5;k++){const [x,y]=L(k);const w=byId.get(bldAt[idx(x,y)]);if(w)kill(w);
     res[k]={vermelho:gateTowerClash('portaoPedra',x,y,ME,ax),eixo:gateDirAt(x,y,ax),pode:canPlace('portaoPedra',x,y,ME)};mkBld(ME,'muralhaPedra',x,y,true)}
   out[ax]=res;
   // esquina de muralha (L) a 2 casas do portão, sem torre
   clear();for(let k=-4;k<=4;k++){const [x,y]=L(k);if(k!==0)mkBld(ME,'muralhaPedra',x,y,true)}const [ex,ey]=L(2);mkBld(ME,'muralhaPedra',ax==='x'?ex:ex+1,ax==='x'?ey+1:ey,true);
   out[ax+'_esquina_a_2']=gateTowerClash('portaoPedra',C.x,C.y,ME,ax);
   // portão isolado no campo (só a ligar muralhas depois): válido
   clear();out[ax+'_isolado']=gateTowerClash('portaoPedra',C.x,C.y,ME,ax)}
 return out}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(3500)
        r = await pg.evaluate(JS); r['erros'] = pe; ok = not pe
        for ax in ('x', 'y'):
            for k, v in r[ax].items():
                k = int(k); esperado = abs(k) >= 3  # torre a 6-|k| casas: até 3 casas → vermelho
                if v['vermelho'] != esperado or v['eixo'] != ax: ok = False
            if not r[ax + '_esquina_a_2'] or r[ax + '_isolado']: ok = False
        print(json.dumps(r, ensure_ascii=False)); print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
