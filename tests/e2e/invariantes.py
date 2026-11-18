# Caça a bugs: partidas IA contra IA aceleradas em vários mapas e civilizações, com verificação de invariantes a cada segundo de jogo.
# Procura: unidades dentro de casas bloqueadas (presas em muralhas/edifícios), unidades com ordem de andar que não saem do sítio,
# posições NaN ou fora do mapa, recursos negativos/NaN, população diferente da contagem real, alvos mortos agarrados,
# mapa de bloqueios incoerente (casas "fantasma" bloqueadas sem edifício ou edifício sem bloqueio), edifícios sobrepostos,
# guarnições incoerentes, entidades duplicadas e erros de JavaScript.
# Uso: servidor em http://localhost:8777 (python3 -m http.server 8777 --directory www) e depois
#      python3 tests/e2e/invariantes.py '[[seed,"mapa","civ0","civ1",dif0,dif1,minutos,caos],...]' [pasta]   (caos=1: jogador 0 também recebe ordens ao calhas)
import asyncio, json, sys
from playwright.async_api import async_playwright
CHECK = r"""
(a)=>{const [seed,map,c0,c1,d0,d1,mins,caos]=a;ERRLOG.length=0;
  startGame(seed,{map,vic:'classico',civ:[c0,c1]});try{tutEnd(true)}catch(e){};AIs[0]=mkAI(0,DIFF[d0]);AIs[1]=mkAI(1,DIFF[d1]);AI=AIs[1];
  // modo caos: além da IA, um "jogador" faz ordens ao calhas como um humano (andar, atacar, muralhas à volta, portões, guarnecer/sair, apagar, sino)
  const R=mulberry32(seed*7+1),pick=a=>a[Math.floor(R()*a.length)],cmds={};
  const chaos=()=>{const mine=ents.filter(e=>e.o===0&&e.kind==='u'&&!e.d.naval),bl=ents.filter(e=>e.o===0&&e.kind==='b');if(!mine.length)return;const tc=bl.find(b=>b.type==='centro');const c=tc?centerOf(tc):{x:mine[0].x,y:mine[0].y};
    const k=pick(['move','move','amove','attack','wall','wall','gate','garr','ungarr','del','bell','gather']);cmds[k]=(cmds[k]||0)+1;const grp=mine.filter(()=>R()<.35).slice(0,25);const ids=(grp.length?grp:[pick(mine)]).map(u=>u.id);
    const rp=()=>({x:clamp(c.x+(R()-.5)*30,1,W-1),y:clamp(c.y+(R()-.5)*30,1,H-1)});
    try{if(k==='move'||k==='amove')EXEC.cmd(0,{u:ids,e:null,w:rp(),m:k==='amove'?'amove':null});
    else if(k==='attack'){const en=ents.filter(e=>e.o===1);if(en.length){const t=pick(en);EXEC.cmd(0,{u:ids,e:t.id,w:centerOf(t)})}}
    else if(k==='wall'){const vs=mine.filter(u=>u.type==='aldeao').slice(0,4).map(u=>u.id);for(const kk of KINDS)P[0].res[kk]=Math.max(P[0].res[kk],600);const r0=4+Math.floor(R()*6),ax=R()<.5,sx=Math.round(c.x+(R()-.5)*2*r0),sy=Math.round(c.y+(R()-.5)*2*r0),L=3+Math.floor(R()*8);
      const t=pick(['muralhaMadeira','muralhaPedra','muralhaPedra','portaoMadeira','portaoPedra']);EXEC.wall(0,{u:vs,t,a:{x:sx,y:sy},b:{x:ax?sx+L:sx,y:ax?sy:sy+L}})}
    else if(k==='gate'){const g=bl.filter(b=>b.d.gate);if(g.length)EXEC.gate(0,{b:pick(g).id,lock:R()<.5})}
    else if(k==='garr'){const g=bl.filter(b=>b.done&&b.d.garr);if(g.length)EXEC.garrison(0,{b:pick(g).id,u:ids})}
    else if(k==='ungarr'){const g=bl.filter(b=>b.garr&&b.garr.length);if(g.length)EXEC.ungarrison(0,{b:pick(g).id})}
    else if(k==='del'){const g=bl.filter(b=>b.d.wall||b.d.gate||b.type==='casa');if(g.length&&R()<.5)EXEC.del(0,{u:[pick(g).id]})}
    else if(k==='bell')EXEC.bell(0,{on:R()<.5});
    else if(k==='gather'){const r=ents.filter(e=>e.kind==='r'&&hyp(e.tx-c.x,e.ty-c.y)<15);if(r.length){const t=pick(r);EXEC.cmd(0,{u:ids.filter(i=>byId.get(i)&&byId.get(i).type==='aldeao'),e:t.id,w:{x:t.tx+.5,y:t.ty+.5}})}}
    }catch(err){note('excecao_ordem_'+k,String(err).slice(0,160))}};
  const issues={},samples={};const note=(k,s)=>{issues[k]=(issues[k]||0)+1;if(!samples[k])samples[k]=[];if(samples[k].length<4)samples[k].push(s)};
  const hist=new Map();let over=null;const T0=performance.now();
  const desc=u=>({id:u.id,o:u.o,t:u.type,st:u.state,x:+u.x.toFixed(2),y:+u.y.toFixed(2),blk:inb(u.x|0,u.y|0)?blk[idx(u.x|0,u.y|0)]:'fora',b:inb(u.x|0,u.y|0)&&bldAt[idx(u.x|0,u.y|0)]?(byId.get(bldAt[idx(u.x|0,u.y|0)])||{}).type:null,tgt:u.target?(u.target.type||u.target.kind):null,path:u.path?u.path.length-u.pi:null,m:+(G.time/60).toFixed(1)});
  for(let t=0;t<mins*60*30;t++){step(1/30);
    if(caos&&t%60===0)chaos();
    if(t%30)continue;
    // --- entidades ---
    const seen=new Set();
    for(const e of ents){if(seen.has(e.id))note('entidade_duplicada',{id:e.id});seen.add(e.id);if(byId.get(e.id)!==e)note('byId_incoerente',{id:e.id,t:e.type});if(e.dead)note('morto_em_ents',{id:e.id,t:e.type})
      if(e.kind==='u'){
        if(!isFinite(e.x)||!isFinite(e.y))note('posicao_nan',desc(e));
        else if(e.x<0||e.y<0||e.x>=W||e.y>=H)note('fora_do_mapa',desc(e));
        if(!isFinite(e.hp)||e.hp>e.max+1e-6)note('vida_invalida',{id:e.id,t:e.type,hp:e.hp,max:e.max});
        if(e.o===2||!isFinite(e.x))continue;
        // dentro de casa bloqueada para esta unidade
        setMover(e);const tx=e.x|0,ty=e.y|0;const bad=!e.d.naval&&inb(tx,ty)&&!okTile(idx(tx,ty))&&!curTile(e);
        let h=hist.get(e.id);if(!h){h={bad:0,x:e.x,y:e.y,still:0,st:e.state};hist.set(e.id,h)}
        h.bad=bad?h.bad+1:0;if(h.bad===4)note('preso_em_bloqueio',desc(e));
        // ordem de andar sem progresso
        const moved=hyp(e.x-h.x,e.y-h.y);
        if(e.state==='move'&&e.path&&e.pi<e.path.length&&moved<.05){h.still++;if(h.still===12)note('parado_com_ordem_de_andar',desc(e))}else h.still=0;
        h.x=e.x;h.y=e.y;
        if(e.state==='attack'&&e.target&&e.target.dead){h.dt=(h.dt||0)+1;if(h.dt===4)note('alvo_morto_agarrado',desc(e))}else h.dt=0;
        // tarefa sem progresso: mesma tarefa, sem andar, sem carregar mais e sem o alvo mudar de vida/progresso durante 60 s
        if(e.state==='gather'||e.state==='build'||e.state==='attack'||e.state==='return'){const tg=e.state==='gather'?e.gres:e.state==='build'?e.bld:e.target;
          const k=e.state+':'+(tg?tg.id:'')+':'+(e.carry||0)+':'+(tg?Math.round((tg.hp||0)*10)+'/'+Math.round((tg.prog||0)*1000)+'/'+(tg.amt||0):'');if(h.k===k&&moved<.02){h.sk=(h.sk||0)+1}else{h.sk=0;h.k=k}}else h.sk=0
      }}
    // --- edifícios e mapa de bloqueios ---
    if(t%(30*10)===0){
      const own=new Int32Array(W*H);
      for(const b of ents){if(b.kind!=='b')continue;for(let y=b.ty;y<b.ty+b.h;y++)for(let x=b.tx;x<b.tx+b.w;x++){if(!inb(x,y)){note('edificio_fora',{t:b.type});continue}const i=idx(x,y);
        if(own[i])note('edificios_sobrepostos',{a:b.type,b:(byId.get(own[i])||{}).type,x,y});own[i]=b.id;if(bldAt[i]!==b.id)note('bldAt_incoerente',{t:b.type,x,y,bldAt:bldAt[i]});
        if(!b.d.walk&&blk[i]!==3&&blk[i]!==4)note('edificio_sem_bloqueio',{t:b.type,x,y,blk:blk[i],done:b.done})}
        if(b.garr)for(const u of b.garr){if(u.dead)note('guarnicao_morta',{b:b.type,u:u.type});if(ents.includes(u))note('guarnecido_no_mapa',{b:b.type,u:u.type})}}
      for(let i=0;i<W*H;i++){if((blk[i]===3||blk[i]===4)&&!own[i])note('bloqueio_fantasma',{x:i%W,y:(i/W)|0,blk:blk[i],bldAt:bldAt[i]});if(bldAt[i]&&!own[i]&&!byId.get(bldAt[i]))note('bldAt_morto',{x:i%W,y:(i/W)|0})}
      // unidades de terra fechadas num sítio sem saída para nenhum Centro do dono (muralhas sem portão, edifícios a tapar) há 60 s
      if(t%(30*30)===0&&map!=='arquipelago')for(let o=caos?1:0;o<2;o++){ // no modo caos o jogador 0 fecha-se a si próprio com muralhas ao calhas: só se verifica a IA
       const tcs=ents.filter(e=>e.kind==='b'&&e.o===o&&e.type==='centro');if(!tcs.length)continue;MV.o=o;MV.nav=0;const m=new Uint8Array(W*H),q=[];
        for(const c of tcs)for(let y=c.ty-1;y<=c.ty+c.h;y++)for(let x=c.tx-1;x<=c.tx+c.w;x++)if(inb(x,y)&&okTile(idx(x,y))&&!m[idx(x,y)]){m[idx(x,y)]=1;q.push(idx(x,y))}
        while(q.length){const c=q.pop(),x=c%W,y=(c/W)|0;for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const nx=x+dx,ny=y+dy;if(!inb(nx,ny))continue;const n=idx(nx,ny);if(!m[n]&&okTile(n)){m[n]=1;q.push(n)}}}
        for(const u of ents){if(u.kind!=='u'||u.o!==o||u.d.naval||u.inBoat)continue;const i=idx(clamp(u.x|0,0,W-1),clamp(u.y|0,0,H-1));const h=hist.get(u.id);if(!h)continue;if(!m[i]&&!(curTile(u)&&m[idx(curTile(u).x,curTile(u).y)])){h.iso=(h.iso||0)+1;if(h.iso===2)note('isolado_sem_saida',desc(u))}else h.iso=0}}
      for(let o=0;o<2;o++){const p=P[o];for(const k of KINDS)if(!(p.res[k]>=-1e-6)||!isFinite(p.res[k]))note('recurso_invalido',{o,k,v:p.res[k]});
        const pop0=p.pop;recount();if(p.pop!==pop0)note('populacao_desatualizada',{o,antes:pop0,depois:p.pop});
        }
    }
    if(G.over){over=+(G.time/60).toFixed(1);break}}
  // unidades com o mesmo trabalho e sem se mexer muito tempo (encravadas a meio de uma tarefa)
  const stuck=[];for(const e of ents)if(e.kind==='u'&&e.o<2){const h=hist.get(e.id);if(h&&h.sk>60)stuck.push(desc(e))}
  if(stuck.length){issues.tarefa_encravada=stuck.length;samples.tarefa_encravada=stuck.slice(0,4)}
  const sum=o=>({ald:ents.filter(e=>e.o===o&&e.type==='aldeao').length,exe:ents.filter(e=>e.o===o&&e.kind==='u'&&e.d.mil).length,ed:ents.filter(e=>e.o===o&&e.kind==='b').length,idade:P[o].age,parados:ents.filter(e=>e.o===o&&e.type==='aldeao'&&e.state==='idle').length});
  return{args:a,cmds,over,min:+(G.time/60).toFixed(1),ms:Math.round(performance.now()-T0),issues,samples,erros:ERRLOG.map(e=>e.m.slice(0,160)).slice(0,6),p0:sum(0),p1:sum(1)}}
"""
RUNS = [[11,"continental","planicies","montanha",2,2,30],[22,"rios","mar","planicies",1,2,30],[33,"lagos","montanha","mar",2,1,30],
        [44,"arquipelago","mar","mar",2,2,30],[55,"reino","planicies","montanha",1,1,30],[66,"continental","montanha","montanha",0,2,30]]
async def main():
    runs = json.loads(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].startswith('[') else RUNS
    out = sys.argv[2] if len(sys.argv) > 2 else '/tmp'
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 915, 'height': 412}); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(4000)
        res = []
        for a in runs:
            r = await pg.evaluate(CHECK, a); res.append(r)
            print(json.dumps({k: r[k] for k in ('args','cmds','over','min','ms','issues','erros','p0','p1')}, ensure_ascii=False), flush=True)
            for k, v in r['samples'].items(): print('   ', k, json.dumps(v[:3], ensure_ascii=False))
        json.dump({'runs': res, 'pageerrors': pe}, open(out + '/invariantes.json', 'w'), ensure_ascii=False, indent=1)
        tot = {}
        for r in res:
            for k, v in r['issues'].items(): tot[k] = tot.get(k, 0) + v
        print('TOTAL', json.dumps(tot, ensure_ascii=False), 'PAGEERR', pe[:3])
        ok = not tot and not pe and not any(r['erros'] for r in res)
        print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
