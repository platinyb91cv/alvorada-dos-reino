# Teste completo dos soldados em cima das defesas: subir pela ordem do jogador (act garrison), quem pode e quem não pode,
# disparos e mortes, sair (ungarrison), muro destruído (descem feridos), guardar/carregar com a guarnição, e imagens de perto.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        R = {}
        R['montar'] = await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=2;
          const ok=(x,y,w,h)=>{for(let j=-1;j<=h;j++)for(let i=-1;i<=w;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
          let q=null;for(let r=4;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(ok(x,y,16,8))q={x,y}}
          const W=(t,x,y)=>mkBld(ME,t,x,y,true);const S={};
          // linha: pedra, portão de madeira, pedra, portão de pedra, fortificada, torre 1/2/3
          S.p1=W('muralhaPedra',q.x,q.y+3);S.gm=W('portaoMadeira',q.x+1,q.y+3);S.p2=W('muralhaPedra',q.x+2,q.y+3);S.gp=W('portaoPedra',q.x+3,q.y+3);
          S.f1=W('muralhaFort',q.x+4,q.y+3);S.f2=W('muralhaFort',q.x+5,q.y+3);S.t1=W('torre',q.x+6,q.y+2);S.t1.lvl=1;S.p3=W('muralhaPedra',q.x+8,q.y+3);
          S.t2=W('torre',q.x+9,q.y+2);S.t2.lvl=2;S.p4=W('muralhaPedra',q.x+11,q.y+3);S.t3=W('torre',q.x+12,q.y+2);S.t3.lvl=3;S.pal=W('muralhaMadeira',q.x+14,q.y+3);
          window.__S=S;window.__q=q;cam.z=1.5;centerCam(q.x+7,q.y+3);
          return Object.fromEntries(Object.entries(S).map(([k,b])=>[k,b.type+' cabe '+(b.d.garr||0)]))}""")
        # ordem do jogador: selecionar arqueiros e mandar subir (como o botão Abrigar)
        R['subir'] = await pg.evaluate("""()=>{const S=__S,q=__q;const res={};
          const mk=(t,n,x,y)=>Array.from({length:n},(_,k)=>mkUnit(ME,t,x+k*.3,y));
          for(const [k,b] of Object.entries(S)){if(!b.d.garr)continue;const us=mk(k.startsWith('t')?'besteiro':'arqueiro',b.d.garr+1,b.tx,b.ty+3.5);act('garrison',{b:b.id,u:us.map(u=>u.id)});res[k]=us.length}
          const v=mkUnit(ME,'aldeao',S.p1.tx,S.p1.ty+4);const cav=mkUnit(ME,'cavaleiro',S.p2.tx,S.p2.ty+4);const lan=mkUnit(ME,'lanceiro',S.p2.tx+.5,S.p2.ty+4);
          act('garrison',{b:S.p2.id,u:[v.id,cav.id]});window.__V={v,cav,lan};return res}""")
        await pg.wait_for_timeout(7000)
        R['em_cima'] = await pg.evaluate("""()=>{const S=__S;const o={};for(const [k,b] of Object.entries(S))o[k]=b.garr?b.garr.length+'/'+(b.d.garr||0):'-';
          o.aldeao_no_muro=S.p2.garr.some(u=>u.type==='aldeao');o.cavalo_no_muro=S.p2.garr.some(u=>u.type==='cavaleiro');o.paliçada_sem_guarnicao=!S.pal.d.garr;return o}""")
        # inimigos a atacar a muralha
        R['ataque_inicio'] = await pg.evaluate("""()=>{const q=__q;window.__F=[];for(let k=0;k<12;k++){const f=mkUnit(1,k%3?'guerreiro':'espadachim',q.x+1+k*1.1,q.y-3);__F.push(f);orderAttack(f,__S.p1)}cam.z=1.5;centerCam(q.x+7,q.y+2);return __F.length}""")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=OUT + '/em_cima_combate.png')
        await pg.wait_for_timeout(9000)
        R['ataque_fim'] = await pg.evaluate("""()=>{const F=__F;return{mortos:F.filter(f=>!alive(f)).length,feridos:F.filter(f=>alive(f)&&f.hp<f.max).length,de:F.length,
          soldados_mortos_em_cima:Object.values(__S).reduce((a,b)=>a+(b.garr?b.garr.filter(u=>u.dead).length:0),0)}}""")
        await pg.evaluate("()=>{cam.z=3.2;centerCam(__q.x+3.5,__q.y+2.6)}"); await pg.wait_for_timeout(600); await pg.screenshot(path=OUT + '/em_cima_perto_portoes.png')
        await pg.evaluate("()=>{cam.z=3.0;centerCam(__q.x+10.5,__q.y+2)}"); await pg.wait_for_timeout(600); await pg.screenshot(path=OUT + '/em_cima_perto_torres.png')
        # guardar e carregar com gente em cima
        R['guardar'] = await pg.evaluate("""()=>{const n0=Object.values(__S).reduce((a,b)=>a+(b.garr?b.garr.length:0),0);const r=saveGame(true);loadGame&&loadGame();
          const bs=ents.filter(e=>e.kind==='b'&&e.garr&&(e.d.wall||e.d.gate||e.type==='torre'));const n1=bs.reduce((a,b)=>a+b.garr.length,0);return{antes:n0,depois:n1,ok:r&&r.ok}}""")
        # sair do muro e muro destruído
        R['sair'] = await pg.evaluate("""()=>{const b=ents.find(e=>e.kind==='b'&&e.type==='portaoPedra'&&e.garr&&e.garr.length);const n=b.garr.length;act('ungarrison',{b:b.id});return{saíram:n,ficaram:b.garr.length}}""")
        R['muro_cai'] = await pg.evaluate("""()=>{const b=ents.find(e=>e.kind==='b'&&e.type==='muralhaFort'&&e.garr&&e.garr.length);if(!b)return 'sem muro com gente';const n=b.garr.length,ids=b.garr.map(u=>u.id);kill(b,null);
          for(let i=0;i<30;i++)step(1/30);const fora=ids.map(i=>byId.get(i)).filter(u=>u&&alive(u)&&ents.includes(u));return{tinham:n,desceram_vivos:fora.length,vida:fora.map(u=>Math.round(u.hp/u.max*100)+'%')}}""")
        R['erros'] = errs
        print(json.dumps(R, indent=1, ensure_ascii=False)); await br.close()
asyncio.run(main())
