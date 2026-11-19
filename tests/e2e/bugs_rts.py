# Cenários de bugs típicos de RTS com muralhas, portões e edifícios (cada um verifica o resultado, não só "sem erros").
# Uso: servidor em http://localhost:8777 (python3 -m http.server 8777 --directory www) e depois python3 tests/e2e/bugs_rts.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
# castelo de teste: anel quadrado de muralha de pedra à volta do Centro do jogador 0, com um portão de pedra a sul (lado +y)
SETUP = r"""
window.__run=s=>{for(let t=0;t<s*30;t++)step(1/30)};
window.__new=(seed)=>{startGame(seed||4242,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[0]=null;AIs[1]=null;AI=null;try{tutEnd(true)}catch(e){};P[0].age=2;vis.fill(2);for(const k of KINDS)P[0].res[k]=50000;
  const tc=ents.find(e=>e.o===0&&e.type==='centro');window.__tc=tc;return tc};
// limpa (recursos, unidades e edifícios que não sejam o Centro) numa caixa à volta do Centro
window.__clear=(tc,R)=>{const cx=tc.tx+1,cy=tc.ty+1;for(const e of ents.slice()){if(e===tc)continue;const x=e.kind==='u'?e.x:e.tx+.5,y=e.kind==='u'?e.y:e.ty+.5;if(Math.abs(x-cx-.5)<=R+2&&Math.abs(y-cy-.5)<=R+2){if(e.kind==='r'){resAt[idx(e.tx,e.ty)]=null;blk[idx(e.tx,e.ty)]=0;byId.delete(e.id)}else kill(e)}}
  G.res=(G.res||[]);for(let y=cy-R-2;y<=cy+R+2;y++)for(let x=cx-R-2;x<=cx+R+2;x++){if(!inb(x,y))continue;const i=idx(x,y);if(resAt[i]){byId.delete(resAt[i].id);resAt[i]=null}if(terr[i]!==1&&!bldAt[i])blk[i]=0}
  if(typeof RES!=='undefined'&&Array.isArray(RES)){}
};
// anel: lado R à volta do centro (cx,cy) = canto superior do Centro + 1; portão no meio do lado +y
window.__ring=(tc,R,gateType,lock)=>{const cx=tc.tx+1,cy=tc.ty+1;__clear(tc,R);const walls=[];let gate=null;
  for(let k=-R;k<=R;k++){for(const [x,y] of [[cx+k,cy-R],[cx+k,cy+R],[cx-R,cy+k],[cx+R,cy+k]]){if(bldAt[idx(x,y)])continue;
    if(gateType&&y===cy+R&&x===cx){gate=mkBld(0,gateType,x,y,true);continue}
    if(gateType&&y===cy+R&&Math.abs(x-cx)<=gateSpan(gateType))continue; // flancos: ficam para a casa do portão
    walls.push(mkBld(0,'muralhaPedra',x,y,true))}}
  if(gate){gate.locked=!!lock}recount();syncGateFlanks();return{cx,cy,walls,gate}};
window.__inside=(r,u)=>Math.abs(u.x-(r.cx+.5))<r.R&&Math.abs(u.y-(r.cy+.5))<r.R;
"""
CASES = {
 # 1) soldados que descem do adarve ficam DENTRO do castelo (antes: casa livre ao calhas, metade ia parar fora da muralha)
 'descer_do_adarve_para_dentro': """()=>{const tc=__new(101);const R=7;const r=__ring(tc,R,'portaoPedra',true);r.R=R;let dentro=0,fora=0,tot=0;
   const ws=r.walls.filter(w=>w.ty===r.cy-R||w.tx===r.cx-R).slice(2,12);
   for(const w of ws){for(let k=0;k<2;k++){const u=mkUnit(0,'arqueiro',r.cx+.5,r.cy+3.5);if(!garrisonIn(u,w)){kill(u);continue}}ungarrison(w,true);}
   for(const u of ents)if(u.kind==='u'&&u.o===0&&u.type==='arqueiro'){tot++;if(__inside(r,u))dentro++;else fora++}
   return{tot,dentro,fora}}""",
 # 2) muralha destruída com soldados em cima: caem para dentro
 'muralha_destruida_soldados_dentro': """()=>{const tc=__new(102);const R=7;const r=__ring(tc,R,'portaoPedra',true);r.R=R;const ws=r.walls.filter(w=>w.tx===r.cx+R).slice(3,9);let n=0;
   for(const w of ws){for(let k=0;k<2;k++){const u=mkUnit(0,'besteiro',r.cx+.5,r.cy+2.5);if(garrisonIn(u,w))n++;else kill(u)}kill(w)}
   const us=ents.filter(u=>u.kind==='u'&&u.o===0&&u.type==='besteiro');return{guarnecidos:n,vivos:us.length,dentro:us.filter(u=>__inside(r,u)||Math.abs(u.x-(r.cx+R+.5))<.6).length}}""",
 # 3) muralha construída por cima de uma unidade: a unidade fica do lado onde estava (não salta para o outro lado)
 'muralha_nova_empurra_para_o_mesmo_lado': """()=>{const tc=__new(103);const cx=tc.tx+1,cy=tc.ty+1;__clear(tc,9);let ok=0,n=0;
   for(let k=0;k<8;k++){const side=k%2?-1:1;const x=cx-4+k,y=cy+6;const u=mkUnit(0,'guerreiro',x+.5,y+.5+side*.38);stopUnit(u);mkBld(0,'muralhaPedra',x,y,true);n++;if(Math.sign(u.y-(y+.5))===side&&!blk[idx(u.x|0,u.y|0)])ok++}
   return{n,mesmo_lado:ok}}""",
 # 4) unidades treinadas num quartel encostado à muralha saem para o lado de dentro
 'treino_sai_para_dentro': """()=>{const tc=__new(104);const R=8;const r=__ring(tc,R,'portaoPedra',true);r.R=R;const q=mkBld(0,'quartel',r.cx+R-3,r.cy-2,true);recount();
   for(let i=0;i<10;i++)spawnUnit(q,'guerreiro');const us=ents.filter(u=>u.kind==='u'&&u.o===0&&u.type==='guerreiro');return{n:us.length,dentro:us.filter(u=>__inside(r,u)).length}}""",
 # 5) unidade parada no arco quando o portão é trancado: consegue sair para os dois lados
 'portao_trancado_com_unidade_no_arco': """()=>{const tc=__new(105);const R=7;const r=__ring(tc,R,'portaoPedra',false);r.R=R;const g=r.gate;
   const a=mkUnit(0,'guerreiro',g.tx+.5,g.ty+.5),b=mkUnit(0,'guerreiro',g.tx+.5,g.ty+.5);g.locked=true;
   moveTo(a,r.cx+.5,r.cy-2.5);moveTo(b,r.cx+.5,r.cy+R+4.5);__run(25);
   return{dentro:hyp(a.x-(r.cx+.5),a.y-(r.cy-2.5))<1.2,fora:hyp(b.x-(r.cx+.5),b.y-(r.cy+R+4.5))<1.2,a:[+a.x.toFixed(1),+a.y.toFixed(1)],b:[+b.x.toFixed(1),+b.y.toFixed(1)]}}""",
 # 6) portão terminado com unidades em cima das casas do lado (flancos): saem e andam normalmente
 'flancos_com_unidades_em_cima': """()=>{const tc=__new(106);const cx=tc.tx+1,cy=tc.ty+1;__clear(tc,9);const y=cy+6;
   for(let k=-6;k<=6;k++)if(Math.abs(k)>2)mkBld(0,'muralhaPedra',cx+k,y,true);
   const us=[];for(const k of [-2,-1,1,2])us.push(mkUnit(0,'lanceiro',cx+k+.5,y+.5));const g=mkBld(0,'portaoPedra',cx,y,false);g.prog=.999;g.hp=g.max;
   __run(1);for(const u of us)if(!g.done)break;if(!g.done){finishBuilding?finishBuilding(g):0}syncGateFlanks();
   const blocked=us.filter(u=>blk[idx(u.x|0,u.y|0)]!==0).length;for(const u of us)moveTo(u,cx+.5,cy-3.5);__run(25);
   return{portao_pronto:g.done,em_casa_bloqueada:blocked,chegaram:us.filter(u=>hyp(u.x-(cx+.5),u.y-(cy-3.5))<2.2).length,de:us.length}}""",
 # 7) grupo grande passa por um portão aberto sem ficar encravado
 'grupo_passa_portao': """()=>{const tc=__new(107);const R=8;const r=__ring(tc,R,'portaoPedra',false);r.R=R;const us=[];
   for(let i=0;i<30;i++)us.push(mkUnit(0,i%3?'espadachim':'arqueiro',r.cx-3+(i%6)+.5,r.cy-6.5+(i/6|0)*.9));
   groupMove(us,r.cx+.5,r.cy+R+6.5,false,'livre');let t50=null;for(let s=0;s<90;s++){__run(1);const n=us.filter(u=>u.y>r.cy+R+1).length;if(n===us.length&&t50==null){t50=s+1;break}}
   return{passaram:us.filter(u=>u.y>r.cy+R+1).length,de:us.length,segundos:t50}}""",
 # 7b) unidade que aparece dentro de um edifício (ex.: script de missão) não fica presa: sai sozinha e cumpre a ordem
 'unidade_dentro_de_edificio_sai': """()=>{const tc=__new(113);const cx=tc.tx+1,cy=tc.ty+1;__clear(tc,9);const u=mkUnit(0,'guerreiro',cx+.5,cy+.5);moveTo(u,cx+.5,cy+6.5);__run(15);
   return{chegou:hyp(u.x-(cx+.5),u.y-(cy+6.5))<1.2,pos:[+u.x.toFixed(2),+u.y.toFixed(2)],estado:u.state}}""",
 # 8) castelo fechado (portão trancado): ninguém entra nem sai; com o portão aberto, entra-se pelo arco
 'castelo_fechado_ninguem_atravessa': """()=>{const tc=__new(108);const R=7;const r=__ring(tc,R,'portaoPedra',true);r.R=R;const us=[];
   for(let i=0;i<12;i++)us.push(mkUnit(0,'guerreiro',r.cx-3+(i%6)+.5,r.cy-2+(i/6|0)+.5));groupMove(us,r.cx+.5,r.cy+R+5.5,false,'livre');__run(30);
   const sairam=us.filter(u=>!__inside(r,u)).length;r.gate.locked=false;groupMove(us,r.cx+.5,r.cy+R+5.5,false,'livre');__run(40);
   return{sairam_trancado:sairam,sairam_aberto:us.filter(u=>!__inside(r,u)).length,de:us.length}}""",
 # 9) torre com guarnição destruída: soldados reaparecem uma vez, vivos e sem duplicados
 'torre_destruida_sem_duplicados': """()=>{const tc=__new(109);const cx=tc.tx+1,cy=tc.ty+1;__clear(tc,9);const t=mkBld(0,'torre',cx+5,cy+5,true);let n=0;
   for(let i=0;i<4;i++){const u=mkUnit(0,'arqueiro',cx+.5,cy+4.5);if(garrisonIn(u,t))n++}const ids=t.garr.map(u=>u.id);kill(t);
   const live=ents.filter(e=>ids.includes(e.id));return{guarnecidos:n,reapareceram:live.length,unicos:new Set(live.map(e=>e.id)).size,byId:ids.every(i=>byId.get(i))}}""",
 # 10) ordem para andar até dentro de um edifício: pára ao lado (não fica a empurrar a parede para sempre)
 'andar_para_dentro_de_edificio': """()=>{const tc=__new(110);const cx=tc.tx+1,cy=tc.ty+1;__clear(tc,9);const q=mkBld(0,'quartel',cx+4,cy+4,true);const u=mkUnit(0,'guerreiro',cx-3.5,cy-3.5);moveTo(u,q.tx+1.5,q.ty+1.5);__run(20);
   return{estado:u.state,dist:+distTo(u,q).toFixed(2),em_bloqueio:blk[idx(u.x|0,u.y|0)]!==0}}""",
 # 11) gravar e carregar com castelo: flancos do portão, portão trancado e guarnição continuam iguais
 'gravar_carregar_castelo': """()=>{const tc=__new(111);const R=7;const r=__ring(tc,R,'portaoPedra',true);const w=r.walls[5];for(let k=0;k<2;k++){const u=mkUnit(0,'arqueiro',r.cx+.5,r.cy+2.5);garrisonIn(u,w)}
   const f0=[...blk].filter(b=>b===5).length,g0=w.garr.length;const sv=saveGame(true);loadGame();const g=ents.find(e=>e.type==='portaoPedra');const w2=ents.find(e=>e.id===w.id);
   return{gravou:sv.ok,flancos:[f0,[...blk].filter(b=>b===5).length],trancado:!!(g&&g.locked),guarnicao:[g0,w2?w2.garr.length:-1]}}""",
 # 12) atacantes contra castelo fechado: atacam a muralha/portão em vez de ficarem parados encostados (só entram depois de partir uma brecha)
 'inimigos_atacam_castelo_fechado': """()=>{const tc=__new(112);const R=7;const r=__ring(tc,R,'portaoPedra',true);r.R=R;AIs[1]=mkAI(1,DIFF[1]);AI=AIs[1];
   const foes=[];for(let i=0;i<8;i++){const f=mkUnit(1,'espadachim',r.cx-2+i+.5,r.cy+R+6.5);foes.push(f);orderAttack(f,tc)}__run(40);
   const st={};for(const f of foes)if(!f.dead){const k=f.state+':'+(f.target?f.target.type:'-');st[k]=(st[k]||0)+1}
   const n0=r.walls.length+1,left=ents.filter(e=>e.o===0&&e.kind==='b'&&(e.d.wall||e.d.gate));const dmg=left.filter(e=>e.hp<e.max).length+(n0-left.length);const destruidos=n0-left.length;const ociosos=foes.filter(f=>!f.dead&&f.state==='idle').length;
   return{estados:st,muros_danificados:dmg,destruidos,ociosos,dentro:foes.filter(f=>!f.dead&&__inside(r,f)).length}}""",
 # 12b) casa que fecha uma bolsa entre árvores com um aldeão lá dentro: o aldeão é tirado para fora (não fica preso)
 'casa_fecha_bolsa_entre_arvores': """()=>{const tc=__new(114);const cx=tc.tx+1,cy=tc.ty+1;__clear(tc,10);const px=cx+6,py=cy+6;
   for(let y=py-1;y<=py+1;y++)for(let x=px-1;x<=px+2;x++){if(x===px&&y===py)continue;if(x===px+1&&y===py)continue;addRes('wood',x,y)}
   const u=mkUnit(0,'aldeao',px+.5,py+.5);stopUnit(u);mkBld(0,'casa',px+1,py,true);// a casa (2x2) tapa a saída
   setMover(u);const pk=pocketOf(u,150);moveTo(u,cx+.5,cy-3.5);__run(25);return{bolsa_depois:!!pk,chegou:hyp(u.x-(cx+.5),u.y-(cy-3.5))<1.5,pos:[+u.x.toFixed(1),+u.y.toFixed(1)]}}""",
 # 12c) árvores que voltam a crescer não fecham passagens: corredor de 1 casa entre árvores e a frente de um portão ficam livres;
 #      na orla de um bosque (sem fechar nada) a árvore cresce normalmente
 'arvores_nao_fecham_passagens': """()=>{const tc=__new(115);const cx=tc.tx+1,cy=tc.ty+1;__clear(tc,12);const y0=cy+6;
   for(let x=cx-4;x<=cx+4;x++){addRes('wood',x,y0-1);addRes('wood',x,y0+1)} // corredor em y0
   const R=7;const g=mkBld(0,'portaoPedra',cx-9,cy-3,true);for(const k of [-4,-3,3,4])mkBld(0,'muralhaPedra',cx-9+k,cy-3,true);syncGateFlanks();
   const ax=bldVariant(g),fx=ax==='y'?g.tx+1:g.tx,fy=ax==='y'?g.ty:g.ty+1; // casa à frente do arco
   G.regrow=[{x:cx,y:y0,t:0},{x:fx,y:fy,t:0},{x:cx+5,y:y0-1,t:0}];__run(2);
   return{corredor_livre:!blk[idx(cx,y0)],frente_portao_livre:!blk[idx(fx,fy)],orla_cresceu:blk[idx(cx+5,y0-1)]===2}}""",
 # 12d) grupo misto (cavalaria + infantaria + arqueiros) a andar junto: a cavalaria não chega sozinha à frente; o grupo não se espalha pelo caminho
 'grupo_anda_junto': """()=>{startGame(31,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[0]=null;AIs[1]=null;AI=null;try{tutEnd(true)}catch(e){};
   const h=G.starts[0];const P0=(x,y)=>{for(let r=0;r<6;r++)for(let a=0;a<12;a++){const X=x+Math.cos(a)*r*.5,Y=y+Math.sin(a)*r*.5;if(inb(X|0,Y|0)&&blk[idx(X|0,Y|0)]===0)return [X,Y]}return [x,y]};const MU=(t,x,y)=>{const q=P0(x,y);return mkUnit(0,t,q[0],q[1])};
   const us=[];for(let i=0;i<10;i++)us.push(MU('espadachim',h.x+4+(i%5)*.7,h.y+5+(i/5|0)*.7));for(let i=0;i<5;i++)us.push(MU('cavaleiro',h.x+4+i*.7,h.y+7));for(let i=0;i<5;i++)us.push(MU('arqueiro',h.x+4+i*.7,h.y+8));
   let dst=null;for(let r=22;r<30&&!dst;r++)for(let a=0;a<24&&!dst;a++){const x=Math.round(h.x+Math.cos(a/24*6.28)*r),y=Math.round(h.y+Math.sin(a/24*6.28)*r);if(inb(x,y)&&blk[idx(x,y)]===0)dst={x:x+.5,y:y+.5}}
   groupMove(us,dst.x,dst.y,false,'livre');const arr=new Map();let spread=0;
   for(let t=0;t<90*30;t++){step(1/30);if(t%15===0){const mv=us.filter(u=>u.state==='move');if(mv.length>3){const r=mv.map(m=>hyp(m.dest.x-m.x,m.dest.y-m.y));spread=Math.max(spread,Math.max(...r)-Math.min(...r))}}for(const u of us)if(!arr.has(u.id)&&hyp(u.x-dst.x,u.y-dst.y)<3)arr.set(u.id,{t:t/30,cav:u.d.cls==='cav'})}
   const V=[...arr.values()],cav=V.filter(v=>v.cav).map(v=>v.t),inf=V.filter(v=>!v.cav).map(v=>v.t);
   return{chegaram:arr.size,de:us.length,cavalaria_antes_s:+(Math.max(...inf)-Math.min(...cav)).toFixed(1),maior_afastamento:+spread.toFixed(1)}}""",
 # 14) quinta com limite: 15 aldeões mandados para UMA quinta -> no máximo 5 em cada; os outros vão para as quintas livres ao lado
 'quinta_limite': """()=>{startGame(31,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[0]=null;AIs[1]=null;AI=null;try{tutEnd(true)}catch(e){};
   const h=G.starts[0];const spot=()=>{for(let r=5;r<20;r++)for(let a=0;a<32;a++){const x=Math.round(h.x+Math.cos(a/32*6.28)*r),y=Math.round(h.y+Math.sin(a/32*6.28)*r);if(canPlace('quinta',x,y,0,0,true))return {x,y}}};
   const F=[];for(let i=0;i<3;i++){const s=spot();F.push(mkBld(0,'quinta',s.x,s.y,true))}
   const vs=[];for(let i=0;i<15;i++){const v=mkUnit(0,'aldeao',h.x+3.5+(i%5)*.6,h.y+4.5+(i/5|0)*.6);stopUnit(v);vs.push(v)}
   command(vs,F[0],centerOf(F[0]));for(let t=0;t<40*30;t++)step(1/30);
   const n=F.map(f=>farmWorkers(f));
   // só uma quinta: os 5 primeiros ficam, os outros não se amontoam
   for(const f of F.slice(1))kill(f);for(const v of vs)stopUnit(v);command(vs,F[0],centerOf(F[0]));for(let t=0;t<20*30;t++)step(1/30);
   return{tres_quintas:n,ocupados:vs.filter(v=>v.state==='gather'||v.state==='return').length,uma_quinta:farmWorkers(F[0])}}""",
 # 15) curral novo: os construtores viram pastores, vão buscar ovelhas (também as mais longe) até o curral encher e depois ordenham
 'curral_enche_sozinho': """()=>{startGame(31,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[0]=null;AIs[1]=null;AI=null;try{tutEnd(true)}catch(e){};
   const h=G.starts[0];let sp=null;for(let r=5;r<20&&!sp;r++)for(let a=0;a<32&&!sp;a++){const x=Math.round(h.x+Math.cos(a/32*6.28)*r),y=Math.round(h.y+Math.sin(a/32*6.28)*r);if(canPlace('curral',x,y,0,0,true))sp={x,y}}
   const b=mkBld(0,'curral',sp.x,sp.y,false);const vs=[];for(let i=0;i<2;i++){const v=mkUnit(0,'aldeao',sp.x-1.5,sp.y+i+.5);stopUnit(v);orderBuild(v,b);vs.push(v)}
   for(let t=0;t<150*30;t++)step(1/30);
   return{dentro:penSheep(b).filter(s=>insidePen(s,b)).length,cap:b.d.pasture,pastores:vs.map(v=>v.state)}}""",
 # 16) muralha paralela encostada à do castelo (por dentro e por fora) e muralha à frente de uma fila de torres: cada uma é uma linha direita
 #     (sem cruzamentos de ameias); as junções verdadeiras (T, esquina, torre no meio do muro) continuam ligadas
 'muralha_paralela': """()=>{const tc=__new(321);const R=9;const r=__ring(tc,R,'portaoPedra',false);const top=r.cy-R;
   const line=(y,x0,x1)=>{const a=[];for(let x=x0;x<=x1;x++)a.push(mkBld(0,'muralhaPedra',x,y,true));return a};
   const dentro=line(top+1,r.cx-6,r.cx+6),fora=line(top-1,r.cx-6,r.cx+6);
   // muro perpendicular que nasce do anel (T) e vai para dentro, a 2 casas do muro paralelo
   const tee=[];for(let x=r.cx-R+1;x<=r.cx-R+5;x++)tee.push(mkBld(0,'muralhaPedra',x,r.cy-3,true));
   recount();const m=b=>bldVariant(b)&15;const reta=a=>a.slice(1,-1).every(b=>m(b)===5);
   const anel=ents.filter(e=>e.d&&e.d.wall&&e.tx===r.cx&&e.ty===top)[0];
   const jT=ents.find(e=>e.d&&e.d.wall&&e.tx===r.cx-R&&e.ty===r.cy-3);
   const cant=ents.find(e=>e.d&&e.d.wall&&e.tx===r.cx-R&&e.ty===top);
   return{dentro_reta:reta(dentro),fora_reta:reta(fora),anel_reto:m(anel)===5,tee_liga:!!(m(tee[0])&4),canto:m(cant),ligT:!!(m(jT)&1)}}""",
 # 13) viagem longa à volta de um lago grande (o A* devolve caminho parcial): a unidade continua até ao destino em vez de parar a meio
 'viagem_longa_a_volta_do_lago': """()=>{startGame(7,{map:'lagos',vic:'classico',civ:['planicies','planicies']});AIs[0]=null;AIs[1]=null;AI=null;try{tutEnd(true)}catch(e){}
   const a=G.starts[0],b=G.starts[1];const u=mkUnit(0,'guerreiro',a.x+3.5,a.y+3.5);let dst=null;for(let r=3;r<10&&!dst;r++)for(let k=0;k<16&&!dst;k++){const x=Math.round(b.x+Math.cos(k)*r),y=Math.round(b.y+Math.sin(k)*r);if(inb(x,y)&&blk[idx(x,y)]===0)dst={x:x+.5,y:y+.5}}
   moveTo(u,dst.x,dst.y);const parcial=!PF_REACHED;for(let t=0;t<240*30&&u.state==='move';t++)step(1/30);return{parcial,falta:+hyp(u.x-dst.x,u.y-dst.y).toFixed(1)}}""",
}
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 915, 'height': 412}); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(4000)
        await pg.evaluate("()=>{" + SETUP + "}")
        r = {}
        for k, js in CASES.items():
            try: r[k] = await pg.evaluate(js)
            except Exception as e: r[k] = {'erro': str(e)[:300]}
            print(k, json.dumps(r[k], ensure_ascii=False), flush=True)
        r['erros'] = await pg.evaluate("()=>ERRLOG.map(e=>e.m.slice(0,160)).slice(0,6)"); r['erros_pagina'] = pe
        g = lambda k: r.get(k, {})
        ok = {
         'descer_do_adarve_para_dentro': g('descer_do_adarve_para_dentro').get('tot', 0) >= 10 and g('descer_do_adarve_para_dentro').get('fora') == 0,
         'muralha_destruida_soldados_dentro': g('muralha_destruida_soldados_dentro').get('vivos') == g('muralha_destruida_soldados_dentro').get('guarnecidos', -1) > 0 and g('muralha_destruida_soldados_dentro').get('dentro') == g('muralha_destruida_soldados_dentro').get('vivos'),
         'muralha_nova_empurra_para_o_mesmo_lado': g('muralha_nova_empurra_para_o_mesmo_lado').get('mesmo_lado') == g('muralha_nova_empurra_para_o_mesmo_lado').get('n', -1),
         'treino_sai_para_dentro': g('treino_sai_para_dentro').get('n') == 10 and g('treino_sai_para_dentro').get('dentro') == 10,
         'portao_trancado_com_unidade_no_arco': g('portao_trancado_com_unidade_no_arco').get('dentro') is True and g('portao_trancado_com_unidade_no_arco').get('fora') is True,
         'flancos_com_unidades_em_cima': g('flancos_com_unidades_em_cima').get('chegaram') == g('flancos_com_unidades_em_cima').get('de', -1) and g('flancos_com_unidades_em_cima').get('em_casa_bloqueada') == 0,
         'grupo_passa_portao': g('grupo_passa_portao').get('passaram') == g('grupo_passa_portao').get('de', -1),
        'unidade_dentro_de_edificio_sai': g('unidade_dentro_de_edificio_sai').get('chegou') is True,
         'castelo_fechado_ninguem_atravessa': g('castelo_fechado_ninguem_atravessa').get('sairam_trancado') == 0 and g('castelo_fechado_ninguem_atravessa').get('sairam_aberto', 0) >= 10,
         'torre_destruida_sem_duplicados': g('torre_destruida_sem_duplicados').get('reapareceram') == g('torre_destruida_sem_duplicados').get('guarnecidos', -1) == g('torre_destruida_sem_duplicados').get('unicos') and g('torre_destruida_sem_duplicados').get('byId') is True,
         'andar_para_dentro_de_edificio': g('andar_para_dentro_de_edificio').get('estado') == 'idle' and g('andar_para_dentro_de_edificio').get('dist', 9) < 1.2 and g('andar_para_dentro_de_edificio').get('em_bloqueio') is False,
         'gravar_carregar_castelo': g('gravar_carregar_castelo').get('gravou') is True and len(set(g('gravar_carregar_castelo').get('flancos', [0, 1]))) == 1 and g('gravar_carregar_castelo').get('trancado') is True and len(set(g('gravar_carregar_castelo').get('guarnicao', [0, 1]))) == 1,
         'inimigos_atacam_castelo_fechado': g('inimigos_atacam_castelo_fechado').get('muros_danificados', 0) >= 1 and (g('inimigos_atacam_castelo_fechado').get('dentro') == 0 or g('inimigos_atacam_castelo_fechado').get('destruidos', 0) > 0) and g('inimigos_atacam_castelo_fechado').get('ociosos', 9) <= 2,
         'casa_fecha_bolsa_entre_arvores': g('casa_fecha_bolsa_entre_arvores').get('chegou') is True and g('casa_fecha_bolsa_entre_arvores').get('bolsa_depois') is False,
         'arvores_nao_fecham_passagens': g('arvores_nao_fecham_passagens').get('corredor_livre') is True and g('arvores_nao_fecham_passagens').get('frente_portao_livre') is True and g('arvores_nao_fecham_passagens').get('orla_cresceu') is True,
         'grupo_anda_junto': g('grupo_anda_junto').get('chegaram') == g('grupo_anda_junto').get('de', -1) and g('grupo_anda_junto').get('cavalaria_antes_s', 99) < 8 and g('grupo_anda_junto').get('maior_afastamento', 99) < 8,
         'quinta_limite': max(g('quinta_limite').get('tres_quintas', [99])) <= 5 and sum(g('quinta_limite').get('tres_quintas', [0])) == 15 and g('quinta_limite').get('uma_quinta', 99) <= 5,
         'curral_enche_sozinho': g('curral_enche_sozinho').get('dentro', 0) == g('curral_enche_sozinho').get('cap', -1) and all(x in ('gather', 'return') for x in g('curral_enche_sozinho').get('pastores', ['x'])),
         'muralha_paralela': (lambda q: q.get('dentro_reta') and q.get('fora_reta') and q.get('anel_reto') and q.get('tee_liga') and q.get('ligT') and q.get('canto') == 3)(g('muralha_paralela')),
         'viagem_longa_a_volta_do_lago': g('viagem_longa_a_volta_do_lago').get('falta', 99) < 1.5,
         'sem_erros': not r['erros'] and not pe}
        r['ok'] = ok
        json.dump(r, open(OUT + '/bugs_rts.json', 'w'), ensure_ascii=False, indent=1)
        print(json.dumps(ok, ensure_ascii=False))
        print('PASS' if all(ok.values()) else 'FAIL ' + ','.join(k for k, v in ok.items() if not v)); await br.close(); sys.exit(0 if all(ok.values()) else 1)
asyncio.run(main())
