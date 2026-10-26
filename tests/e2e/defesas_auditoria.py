# Auditoria das defesas (muralhas, portões, torres): alturas e assentamento no chão medidos nos sprites do jogo, encaixes,
# passagem pelos portões (dono passa; inimigo e portão trancado bloqueiam), soldados em cima, guardar/carregar. Escreve imagens.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def boot(pg):
    await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
    await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
    await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
    await pg.evaluate("""()=>{window.__spot=(w,h)=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);
      const ok=(x,y)=>{for(let j=-1;j<=h;j++)for(let i=-1;i<=w;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
      for(let r=4;r<90;r++)for(let a=0;a<96;a++){const x=Math.round(q0.x+Math.cos(a/96*6.283)*r),y=Math.round(q0.y+Math.sin(a/96*6.283)*r);if(ok(x,y))return{x,y}}return null};
      window.__W=(t,x,y,o=ME)=>mkBld(o,t,x,y,true);P[ME].age=2;P[1].age=2}""")
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await boot(pg); R = {}
        # 1) cada peça isolada: altura acima do chão e base assente no chão (medido no sprite que o jogo desenha)
        R['isoladas'] = await pg.evaluate("""async()=>{await new Promise(r=>setTimeout(r,1500));const out={};const ZP=HW*2/Math.SQRT2*Math.cos(Math.PI/6);
          const meas=(s,colX)=>{const c=s.cv.getContext('2d'),W2=s.cv.width,H2=s.cv.height,sc=W2/s.CW;const x=Math.round(colX*sc);const d=c.getImageData(x,0,1,H2).data;let top=-1,bot=-1;
            for(let y=0;y<H2;y++){const a=d[y*4+3],l=(d[y*4]+d[y*4+1]+d[y*4+2])/3;if(a>200&&!(l<60&&a<250)){if(top<0)top=y;bot=y}}return{top:top/sc,bot:bot/sc}};
          // portão de pedra pintado (arte/pintura-castelo): valores de referência medidos na pintura integrada (regressão), não no modelo 3D
          // geometria (unidades do jogo): na coluna do centro do ecrã (x=y) o topo é a aresta de trás (y=.5-hw) e a base é a aresta da frente (y=.5+hw+sapata)
          const cases=[['muralhaPedra',5,[1.35,1.45],.28,.04],['muralhaFort',5,[1.55,1.65],.32,.04],['muralhaMadeira',5,[.95,1.15],.055,0],['portaoPedra','x',PGATE.ready?[1.0,1.2]:[2.0,2.25],.46,PGATE.ready?-.36:.03],['portaoMadeira','x',[1.8,2.1],.44,.03]];
          for(const [t,v,[h0,h1],hw,sp] of cases){const s=bldSprite(t,2,ME,v);if(!s||!s.cv){out[t]='SEM SPRITE';continue}
            const m=meas(s,s.ox),groundC=s.oy+HH;
            const alt=(groundC-m.top-2*hw*HH)/ZP, base=(m.bot-groundC)/HH, eb=2*(hw+sp);
            out[t]={altura:+alt.toFixed(2),esperado:[h0,h1],altura_ok:alt>=h0-.06&&alt<=h1+.06,base_casas:+base.toFixed(2),base_esperada:+eb.toFixed(2),assente_ok:Math.abs(base-eb)<=.1}}
          const TT={1:3.28,2:3.39,3:4.5},FB={1:4,2:4,3:2.88}; // nível 3 = torre redonda pintada: o topo é a ponta da bandeira e a base redonda fica centrada na pegada
          for(const lv of [1,2,3]){const s=bldSprite('torre',2,ME,lv);const m=meas(s,s.ox),top=(s.oy+2*HH-m.top)/ZP,fundo=(m.bot-s.oy)/HH;
            out['torre'+lv]={topo:+top.toFixed(2),topo_esperado:TT[lv],topo_ok:Math.abs(top-TT[lv])<=.12,fundo_casas:+fundo.toFixed(2),assente_ok:Math.abs(fundo-FB[lv])<=.12}}
          return out}""")
        # 2) combinações: retas, cantos, torres, portões; imagem
        R['combinacoes'] = await pg.evaluate("""()=>{const q=__spot(16,10);const S={};
          for(let i=0;i<14;i++){const x=q.x+i,y=q.y+3;if(i===3)S.gp=__W('portaoPedra',x,y);else if(i===6){S.t2=__W('torre',x,y-1);S.t2.lvl=2}else if(i===7){}else if(i===10){S.gm=__W('portaoMadeira',x,y)}else __W(i>10?'muralhaFort':'muralhaPedra',x,y)}
          for(let j=4;j<10;j++){const x=q.x,y=q.y+j;if(j===6)__W('portaoPedra',x,y);else __W('muralhaPedra',x,y)}
          S.t3=__W('torre',q.x+13,q.y+9);S.t3.lvl=3;for(let j=4;j<9;j++)__W('muralhaFort',q.x+13,q.y+j);for(let i=1;i<13;i++)__W(i===6?'portaoMadeira':'muralhaMadeira',q.x+i,q.y+9);
          window.__C=q;cam.z=1.25;centerCam(q.x+7,q.y+6);for(const k in BCACHE)delete BCACHE[k];
          const g=ents.filter(e=>e.kind==='b'&&(e.d.wall||e.d.gate)).map(e=>[e.type,bldVariant(e)]);return{pecas:g.length,variantes_portao_lado:g.filter(([t,v])=>typeof v==='number'&&v>=64).length}}""")
        await pg.wait_for_timeout(1500); await pg.screenshot(path=OUT + '/combinacoes.png')
        await pg.evaluate("()=>{cam.z=2.6;centerCam(__C.x+3.5,__C.y+3)}"); await pg.wait_for_timeout(700); await pg.screenshot(path=OUT + '/portao_pedra_perto.png')
        await pg.evaluate("()=>{cam.z=2.6;centerCam(__C.x+7,__C.y+2.5)}"); await pg.wait_for_timeout(700); await pg.screenshot(path=OUT + '/torre_quadrada_perto.png')
        await pg.evaluate("()=>{cam.z=2.4;centerCam(__C.x+12.5,__C.y+8.5)}"); await pg.wait_for_timeout(700); await pg.screenshot(path=OUT + '/torre_redonda_perto.png')
        # 3) passagem: cerca fechada 7x7 com um portão a sul
        R['passagem'] = await pg.evaluate("""async()=>{const q=__spot(9,9);const x0=q.x+1,y0=q.y+1,N=7;let gate=null;
          for(let i=0;i<N;i++)for(let j=0;j<N;j++){if(i>0&&i<N-1&&j>0&&j<N-1)continue;const x=x0+i,y=y0+j;if(j===N-1&&i===3)gate=__W('portaoPedra',x,y);else __W('muralhaPedra',x,y)}
          const inside={x:x0+3.5,y:y0+3.5},outs={x:x0+3.5,y:y0+N+1.5};
          const own=mkUnit(ME,'guerreiro',outs.x,outs.y);moveTo(own,inside.x,inside.y);
          const isIn=u=>u.x>x0+1&&u.x<x0+N-1&&u.y>y0+1&&u.y<y0+N-1;
          for(let k=0;k<30*25;k++)step(1/30);const r={dono_entrou:isIn(own)};
          // inimigo sozinho (sem ninguém para combater por perto): não pode entrar
          own.x=inside.x;own.y=inside.y;const foe=mkUnit(1,'lanceiro',outs.x+3,outs.y+2);moveTo(foe,inside.x,inside.y);
          for(let k=0;k<30*25;k++)step(1/30);r.inimigo_entrou=isIn(foe);r.inimigo_vivo=alive(foe);
          // portão trancado: um segundo soldado do dono não entra
          gate.locked=true;const own2=mkUnit(ME,'guerreiro',outs.x-1,outs.y);moveTo(own2,inside.x,inside.y);for(let k=0;k<30*20;k++)step(1/30);r.trancado_dono_entrou=isIn(own2);
          // portão aberto com unidade a passar
          gate.locked=false;const own3=mkUnit(ME,'lanceiro',outs.x-1.5,outs.y);moveTo(own3,inside.x,inside.y);let maxOpen=0;for(let k=0;k<30*20;k++){step(1/30);maxOpen=Math.max(maxOpen,gate.open||0)}
          r.aberto_dono_entrou=isIn(own3);r.porta_abriu=+maxOpen.toFixed(2);for(const u of [own,own2,own3])kill(u,null);for(let k=0;k<30*4;k++)step(1/30);r.porta_fechou_sem_ninguem=+(gate.open||0).toFixed(2)===0;
          window.__ring={x0,y0,N};cam.z=1.8;centerCam(x0+3.5,y0+4);return r}""")
        await pg.wait_for_timeout(800); await pg.screenshot(path=OUT + '/cerca_portao.png')
        R['erros'] = errs
        print(json.dumps(R, indent=1, ensure_ascii=False)); await br.close()
asyncio.run(main())
