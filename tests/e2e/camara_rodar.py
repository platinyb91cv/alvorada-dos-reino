# Câmara a rodar 90° (4 vistas, como no Stronghold): em cada vista verifica
#  - ecrã ↔ mundo coerentes (o ponto tocado é o ponto do mundo que está debaixo do dedo);
#  - rodar mantém o mesmo sítio no centro do ecrã;
#  - tocar num edifício e numa unidade seleciona-os; colocar uma casa põe-na na casa do mapa debaixo do dedo;
#  - ordem de desenho: o que está mais perto da câmara (nesta vista) desenha-se depois;
#  - o jogo (simulação) não muda com a vista: a mesma partida dá o mesmo resultado em qualquer rotação;
#  - desenho sem erros e imagens das 4 vistas (camara_rodar_rN.png) com muralhas, portão, torres e castelo.
# Uso: servidor em http://localhost:8777 (python3 -m http.server 8777 --directory www) e depois python3 tests/e2e/camara_rodar.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
SETUP = open(__file__.replace('camara_rodar.py', 'bugs_rts.py'), encoding='utf-8').read().split('SETUP = r"""')[1].split('"""')[0]
SCENE = """()=>{const tc=__new(321);const R=6;const r=__ring(tc,R,'portaoPedra',false);r.R=R;
  for(const [dx,dy] of [[-R,-R],[R-1,-R],[-R,R-1],[R-1,R-1]]){const x=r.cx+dx,y=r.cy+dy;for(const [a,b] of [[0,0],[1,0],[0,1],[1,1]]){const n=byId.get(bldAt[idx(x+a,y+b)]);if(n&&n.d.wall)kill(n)}const t=mkBld(0,'torre',x,y,true);t.lvl=3}
  fx.length=0;mkBld(0,'quartel',r.cx+2,r.cy+2,true);window.__q=mkBld(0,'quartel',r.cx+R+6,r.cy+4,true); // fora do castelo: nada à frente em nenhuma vista
  mkBld(0,'casa',r.cx-4,r.cy-4,true);tc.lvl=3;recount();syncGateFlanks();
  for(const w of r.walls.filter(w=>w.ty===r.cy-R).slice(2,6))for(let k=0;k<2;k++){const u=mkUnit(0,'arqueiro',r.cx+.5,r.cy+3.5);garrisonIn(u,w)}
  window.__u=mkUnit(0,'espadachim',r.cx+R+3.5,r.cy+.5);stopUnit(__u);cam.z=1.1;centerCam(r.cx+.5,r.cy+.5);window.__r=r;return true}"""
CHECK = """(k)=>{const out={rot:ROT};
  // ecrã ↔ mundo
  let err=0;for(const [x,y] of [[10.3,20.7],[55.5,55.5],[80.2,30.9]]){const s=w2s(x,y),w=s2w(s.x,s.y);err=Math.max(err,hyp(w.x-x,w.y-y))}out.erro_ida_volta=+err.toFixed(6);
  // seleção por toque
  const q=__q,qc=w2s(q.tx+q.w/2,q.ty+q.h/2);const pb=pickAt(qc.x,qc.y-10*cam.z,true);out.toca_quartel=!!pb&&pb.id===q.id;
  const us=w2s(__u.x,__u.y);const pu=pickAt(us.x,us.y-12*cam.z,true);out.toca_unidade=!!pu&&pu.id===__u.id;
  // colocar uma casa onde está o dedo
  const tx=__r.cx+__r.R+5,ty=__r.cy-3;const s0=w2s(tx+.5,ty+.5);placing={type:'casa'};setPlaceAt(s2w(s0.x,s0.y));out.casa_no_sitio=placing.tx===tx&&placing.ty===ty;placing=null;
  // ordem de desenho: de dois pontos, o de maior y no ecrã tem maior profundidade
  const a={x:__r.cx,y:__r.cy},b={x:__r.cx+3,y:__r.cy+1};const sa=w2s(a.x,a.y),sb=w2s(b.x,b.y);out.ordem_ok=(sa.y<sb.y)===(dep(a.x,a.y)<dep(b.x,b.y));
  // canto de cima do edifício (âncora): é mesmo o canto com menor y no ecrã
  const cs=[[q.tx,q.ty],[q.tx+q.w,q.ty],[q.tx,q.ty+q.h],[q.tx+q.w,q.ty+q.h]].map(([x,y])=>proj(x,y));const top=cs.reduce((m,p)=>p.y<m.y?p:m),an=bAnch(q);out.ancora_ok=Math.abs(top.x-an.x)<1e-6&&Math.abs(top.y-an.y)<1e-6;
  return out}"""
SIM = """(rot)=>{ROT=rot;startGame(77,{map:'rios',vic:'classico',civ:['mar','planicies']});try{tutEnd(true)}catch(e){};AIs[0]=mkAI(0,DIFF[1]);AIs[1]=mkAI(1,DIFF[1]);AI=AIs[1];
  for(let t=0;t<4*60*30;t++){step(1/30);if(t%300===0)render()}const h=ents.reduce((a,e)=>a+(e.kind==='u'?Math.round(e.x*100)+Math.round(e.y*100)*7:e.kind==='b'?e.tx*3+e.ty:0),0);
  return {n:ents.length,h,ouro:Math.round(P[0].res.gold),madeira:Math.round(P[1].res.wood)}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={'width': 1000, 'height': 560}); pg = await ctx.new_page(); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(3500)
        await pg.evaluate("()=>{" + SETUP + "}")
        await pg.evaluate(SCENE)
        r = {'vistas': []}
        for k in range(4):
            c0 = await pg.evaluate("()=>s2w(vw/2,(vh-70)/2)")
            await pg.wait_for_timeout(900)
            r['vistas'].append(await pg.evaluate(CHECK, k))
            await pg.evaluate("()=>{const cv=document.querySelector('canvas');for(const e of document.body.querySelectorAll('*'))if(e!==cv&&!e.contains(cv))e.style.visibility='hidden'}")
            await pg.screenshot(path=f'{OUT}/camara_rodar_r{k}.png')
            await pg.evaluate("()=>{for(const e of document.body.querySelectorAll('*'))e.style.visibility=''}")
            await pg.evaluate("()=>$('bRot').click()")  # o botão (toque curto roda no sentido dos ponteiros)
            await pg.wait_for_timeout(200)
            c1 = await pg.evaluate("()=>s2w(vw/2,(vh-70)/2)")
            r['vistas'][-1]['centro_mantido'] = abs(c0['x'] - c1['x']) < .6 and abs(c0['y'] - c1['y']) < .6
        r['volta_completa'] = await pg.evaluate("()=>ROT")
        r['simulacao'] = [await pg.evaluate(SIM, k) for k in (0, 1, 2, 3)]
        await pg.evaluate("()=>{ROT=0}")
        r['erros'] = await pg.evaluate("()=>ERRLOG.map(e=>e.m.slice(0,160)).slice(0,6)"); r['erros_pagina'] = pe
        V = r['vistas']
        ok = {'ida_volta': all(v['erro_ida_volta'] < 1e-6 for v in V), 'toque_edificio': all(v['toca_quartel'] for v in V), 'toque_unidade': all(v['toca_unidade'] for v in V),
              'colocar_casa': all(v['casa_no_sitio'] for v in V), 'ordem_desenho': all(v['ordem_ok'] for v in V), 'ancora': all(v['ancora_ok'] for v in V),
              'centro_mantido': all(v['centro_mantido'] for v in V), 'quatro_vistas': r['volta_completa'] == 0,
              'simulacao_igual': len({json.dumps(s) for s in r['simulacao']}) == 1, 'sem_erros': not r['erros'] and not pe}
        r['ok'] = ok
        print(json.dumps(r, ensure_ascii=False)); json.dump(r, open(OUT + '/camara_rodar.json', 'w'), ensure_ascii=False, indent=1)
        print('PASS' if all(ok.values()) else 'FAIL ' + ','.join(k for k, v in ok.items() if not v)); await br.close(); sys.exit(0 if all(ok.values()) else 1)
asyncio.run(main())
