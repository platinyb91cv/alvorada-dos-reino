// Testes automáticos — Alvorada dos Reinos. Corre dentro da página (window).
(function(){
const S=()=>window.__S();
const T=[];
function rec(name,pass,detail){T.push({name,res:pass===null?'NOT TESTED':pass?'PASS':'FAIL',detail:detail||''})}
function sim(sec){for(let i=0;i<sec*30;i++)step(1/30)}
function fresh(seed){startGame(seed||7);const s=S();s.AIs[1]=null;for(const p of s.P){p.age=2;for(const k in p.res)p.res[k]=20000}s.vis.fill(2);const h=s.G.starts[0];const ox=Math.round(h.x-Math.sign(W/2-h.x)*3),oy=Math.round(h.y-Math.sign(H/2-h.y)*3);for(let i=0;i<14;i++){const sp=freeSpot('casa',0,ox,oy,2);if(sp)mkBld(0,'casa',sp.x,sp.y,true)}recount();return s}
function freeSpot(type,o,cx,cy,r0){for(let r=r0||2;r<30;r++)for(let y=cy-r;y<=cy+r;y++)for(let x=cx-r;x<=cx+r;x++){if(Math.max(Math.abs(x-cx),Math.abs(y-cy))!==r)continue;if(canPlace(type,x,y,o,1,true))return{x,y}}return null}
function freeTile(cx,cy){const s=S();for(let r=0;r<20;r++)for(let y=cy-r;y<=cy+r;y++)for(let x=cx-r;x<=cx+r;x++){if(x<1||y<1||x>W-3||y>H-3)continue;if(s.blk[idx(x,y)]===0&&!s.resAt[idx(x,y)])return{x,y}}}
function home(o){return S().G.starts[o]}
function inward(o,d){const h=home(o);return{x:Math.round(h.x+Math.sign(W/2-h.x)*d),y:Math.round(h.y+Math.sign(H/2-h.y)*d)}}
function clearArea(cx,cy,r){const s=S();for(let y=cy-r;y<=cy+r;y++)for(let x=cx-r;x<=cx+r;x++){const i=idx(x,y);const rr=s.resAt[i];if(rr&&!rr.fish)removeRes(rr)}}
// ---------- 1. produção de cada unidade ----------
try{
  const s=fresh(21);const h=home(0);
  const made={};
  for(const bt of ['quartel','arquearia','estabulo','oficina','templo','mercado']){const sp=freeSpot(bt,0,h.x,h.y,5);const b=mkBld(0,bt,sp.x,sp.y,true);
    for(const t of BLDS[bt].train){b.queue=[];s.P[0].res.food=s.P[0].res.wood=s.P[0].res.gold=s.P[0].res.stone=20000;queueUnit(b,t,true);sim(UNITS[t].time+1);made[t]=s.ents.filter(e=>e.o===0&&e.type===t).length}}
  // doca junto ao lago central
  const L=s.G.lake;let dock=null;for(let r=0;r<16&&!dock;r++)for(let y=Math.floor(L.y)-r-10;y<=L.y+r+10&&!dock;y++)for(let x=Math.floor(L.x)-r-10;x<=L.x+r+10;x++){if(canPlace('doca',x,y,0,0,true)){dock=mkBld(0,'doca',x,y,true);break}}
  for(const t of BLDS.doca.train){dock.queue=[];queueUnit(dock,t,true);sim(UNITS[t].time+1);made[t]=s.ents.filter(e=>e.o===0&&e.type===t).length}
  const all=Object.keys(UNITS).filter(t=>!UNITS[t].gaia&&t!=='aldeao'&&canTrainType(0,t));const miss=all.filter(t=>!made[t]);
  const tc=s.ents.find(e=>e.o===0&&e.type==='centro');queueUnit(tc,'aldeao',true);sim(13);
  rec('Produção de cada unidade',!miss.length&&s.ents.filter(e=>e.o===0&&e.type==='aldeao').length>=4,miss.length?'faltam: '+miss.join(','):all.length+' tipos produzidos + aldeão');
  window.__dock=dock;
}catch(e){rec('Produção de cada unidade',false,String(e))}
// ---------- 2. movimento ----------
try{
  const s=fresh(22);const h=home(0);const t0=freeTile(h.x+3,h.y+3);const u=mkUnit(0,'guerreiro',t0.x+.5,t0.y+.5);const dst=freeTile(h.x+12,h.y+6);
  moveTo(u,dst.x+.5,dst.y+.5);sim(25);const d=Math.hypot(u.x-dst.x-.5,u.y-dst.y-.5);
  rec('Movimento',d<1.2,'distância final '+d.toFixed(2));
}catch(e){rec('Movimento',false,String(e))}
// ---------- 3. ataque, dano, morte ----------
try{
  const s=fresh(23);const h=home(0);const a=freeTile(h.x+6,h.y+6);
  const u=mkUnit(0,'espadachim',a.x+.5,a.y+.5),v=mkUnit(1,'guerreiro',a.x+1.3,a.y+.5);
  const hp0=v.hp;orderAttack(u,v);sim(1.6);const hp1=v.hp;sim(30);
  rec('Ataque',hp1<hp0,'vida do alvo '+hp0+'→'+hp1.toFixed(1));
  rec('Dano',Math.abs((hp0-hp1)-((atkOf(u)+3-armOf(v))))<.01||hp0-hp1>=atkOf(u)+3-armOf(v),'esperado '+(atkOf(u)+3-armOf(v))+' por golpe (bónus +3 vs infantaria)');
  rec('Morte e remoção',v.dead&&!s.ents.includes(v)&&!s.byId.has(v.id),'morto='+!!v.dead);
}catch(e){rec('Ataque',false,String(e))}
// ---------- 4. contra-unidades ----------
try{
  const s=fresh(24);const mk=(o,t)=>mkUnit(o,t,40,40);
  const dmg=(a,b)=>{const A=mk(0,a),B=mk(1,b);const hp=B.hp;applyDmg(B,atkOf(A),A,!!A.d.range);const r=hp-B.hp;kill(A);if(!B.dead)kill(B);return r};
  const c=[['lanceiro','cavaleiro','guerreiro','cavaleiro'],['cavaleiro','arqueiro','cavaleiro','guerreiro'],['arqueiro','guerreiro','arqueiro','cavaleiro'],['espadachim','lanceiro','espadachim','cavaleiro'],['cavaleiro','catapulta','cavaleiro','espadachim']];
  const det=[];let ok=true;
  for(const [a,b,a2,b2] of c){const x=dmg(a,b),y=dmg(a2,b2);det.push(`${a}→${b} ${x} vs ${a2}→${b2} ${y}`);if(!(x>y))ok=false}
  // batalha de custo equivalente: 2 lanceiros vs 1 cavalaria
  const p=freeTile(home(0).x+8,home(0).y+8);const L1=mkUnit(0,'lanceiro',p.x+.5,p.y+.5),L2=mkUnit(0,'lanceiro',p.x+.5,p.y+1.2),C=mkUnit(1,'cavaleiro',p.x+1.4,p.y+.8);
  orderAttack(L1,C);orderAttack(L2,C);orderAttack(C,L1);sim(25);
  const win1=C.dead&&(!L1.dead||!L2.dead);
  // cavalaria contra arqueiros
  const q=freeTile(home(0).x+14,home(0).y+3);const C2=mkUnit(0,'cavaleiro',q.x+.5,q.y+.5),A1=mkUnit(1,'arqueiro',q.x+2,q.y+.5),A2=mkUnit(1,'arqueiro',q.x+2,q.y+1.2);
  orderAttack(C2,A1);sim(40);const win2=A1.dead&&A2.dead&&!C2.dead;
  rec('Contra-unidades',ok&&win1&&win2,det.join(' | ')+` | 2 lanceiros vs cavalaria: ${win1?'lanceiros ganham':'falhou'} | cavalaria vs 2 arqueiros: ${win2?'cavalaria ganha':'falhou'}`);
}catch(e){rec('Contra-unidades',false,String(e))}
// ---------- 5. formação ----------
try{
  const s=fresh(25);const h=home(0);const sx=Math.sign(W/2-h.x),sy=Math.sign(H/2-h.y);const b=freeTile(h.x+5*sx,h.y+5*sy);clearArea(b.x,b.y,3);clearArea(b.x+8*sx,b.y+8*sy,6);
  const us=[];for(let i=0;i<4;i++)us.push(mkUnit(0,'guerreiro',b.x+.5+i*.4,b.y+.5));for(let i=0;i<4;i++)us.push(mkUnit(0,'arqueiro',b.x+.5+i*.4,b.y+1.3));us.push(mkUnit(0,'catapulta',b.x+1,b.y+2));
  const dst={x:b.x+9*sx,y:b.y+9*sy};groupMove(us,dst.x,dst.y,false,'linha');sim(40);
  const dir={x:.707*sx,y:.707*sy};const along=u=>(u.x-dst.x)*dir.x+(u.y-dst.y)*dir.y;
  const inf=us.filter(u=>u.type==='guerreiro').map(along),arc=us.filter(u=>u.type==='arqueiro').map(along),sie=us.filter(u=>u.type==='catapulta').map(along);
  const avg=a=>a.reduce((x,y)=>x+y,0)/a.length;
  let minD=9;for(let i=0;i<us.length;i++)for(let j=i+1;j<us.length;j++)minD=Math.min(minD,Math.hypot(us[i].x-us[j].x,us[i].y-us[j].y));
  const ok=avg(inf)>avg(arc)&&avg(arc)>avg(sie)&&minD>.3;
  // coluna
  groupMove(us,dst.x-6,dst.y+4,false,'coluna');sim(30);let w=0;{const ux=us.map(u=>u.x),uy=us.map(u=>u.y);w=Math.min(Math.max(...ux)-Math.min(...ux),Math.max(...uy)-Math.min(...uy))}
  rec('Formação',ok,`linha: infantaria ${avg(inf).toFixed(2)} > arqueiros ${avg(arc).toFixed(2)} > cerco ${avg(sie).toFixed(2)}; distância mínima ${minD.toFixed(2)}; coluna largura mínima ${w.toFixed(1)}`);
}catch(e){rec('Formação',false,String(e))}
// ---------- 6. muralha ----------
try{
  const s=fresh(26);const h=home(0);const i0=inward(0,10);const c=freeTile(i0.x,i0.y);clearArea(c.x,c.y,8);
  // caixa fechada de muralhas de pedra 7x7 à volta de c
  for(let k=-3;k<=3;k++)for(const [x,y] of [[c.x+k,c.y-3],[c.x+k,c.y+3],[c.x-3,c.y+k],[c.x+3,c.y+k]]){const i=idx(x,y);if(!s.bldAt[i]&&s.blk[i]===0)mkBld(0,'muralhaPedra',x,y,true)}
  const sealed=(()=>{for(let k=-3;k<=3;k++)for(const [x,y] of [[c.x+k,c.y-3],[c.x+k,c.y+3],[c.x-3,c.y+k],[c.x+3,c.y+k]]){if(s.blk[idx(x,y)]===0)return false}return true})();
  const e1=mkUnit(1,'aldeao',c.x+6.5,c.y+.5);moveTo(e1,c.x+.5,c.y+.5);let inside=false,onWall=false;
  for(let i=0;i<30*30;i++){step(1/30);const tx=Math.floor(e1.x),ty=Math.floor(e1.y);if(Math.abs(tx-c.x)<3&&Math.abs(ty-c.y)<3)inside=true;if(s.blk[idx(tx,ty)]===3)onWall=true}
  // soldado inimigo em atacar-mover ataca a muralha que o bloqueia
  const sw=s.ents.find(e=>e.type==='muralhaPedra');const hp0=sw.hp;
  const e2=mkUnit(1,'espadachim',c.x+5.5,c.y+.5);moveTo(e2,c.x+.5,c.y+.5);e2.amove=true;sim(40);
  const dmgd=s.ents.filter(e=>e.type==='muralhaPedra').some(w=>w.hp<w.max)||s.ents.filter(e=>e.type==='muralhaPedra').length<24;
  rec('Muralha',sealed&&!inside&&!onWall&&dmgd,`fechada=${sealed} entrou=${inside} pisou=${onWall} soldado atacou a muralha=${dmgd}`);
  window.__wallC=c;
}catch(e){rec('Muralha',false,String(e))}
// ---------- 7. portão ----------
try{
  const s=fresh(27);const h=home(0);const i0=inward(0,10);const c=freeTile(i0.x,i0.y);clearArea(c.x,c.y,8);
  for(let k=-3;k<=3;k++)for(const [x,y] of [[c.x+k,c.y-3],[c.x+k,c.y+3],[c.x-3,c.y+k],[c.x+3,c.y+k]]){const i=idx(x,y);if(!s.bldAt[i]&&s.blk[i]===0)mkBld(0,'muralhaPedra',x,y,true)}
  const w0=s.byId.get(s.bldAt[idx(c.x+3,c.y)]);kill(w0);const g=mkBld(0,'portaoPedra',c.x+3,c.y,true);
  const a=mkUnit(0,'aldeao',c.x+6.5,c.y+.5);moveTo(a,c.x+.5,c.y+.5);sim(20);const allyIn=Math.abs(a.x-c.x-.5)<1.5&&Math.abs(a.y-c.y-.5)<1.5;
  const opened=g.open>0||true;
  const en=mkUnit(1,'aldeao',c.x+6.5,c.y+1.5);moveTo(en,c.x+.5,c.y+.5);let enIn=false;for(let i=0;i<20*30;i++){step(1/30);if(Math.abs(Math.floor(en.x)-c.x)<3&&Math.abs(Math.floor(en.y)-c.y)<3)enIn=true}
  // fechado: aliado não passa
  g.locked=true;const b=mkUnit(0,'aldeao',c.x+6.5,c.y-1.5);moveTo(b,c.x+.5,c.y+.5);let bIn=false;for(let i=0;i<20*30;i++){step(1/30);if(Math.abs(Math.floor(b.x)-c.x)<3&&Math.abs(Math.floor(b.y)-c.y)<3)bIn=true}
  // animação de abertura
  g.locked=false;const a2=mkUnit(0,'aldeao',c.x+3.5,c.y+1.6);let maxOpen=0;for(let i=0;i<60;i++){step(1/30);maxOpen=Math.max(maxOpen,g.open)}
  // destruir portão
  const r=mkUnit(1,'ariete',c.x+5.5,c.y+.5);orderAttack(r,g);sim(60);
  rec('Portão',allyIn&&!enIn&&!bIn&&maxOpen>.5&&g.dead,`aliado passou=${allyIn} inimigo passou=${enIn} aliado com portão fechado passou=${bIn} abertura=${maxOpen.toFixed(2)} destruído por aríete=${!!g.dead}`);
}catch(e){rec('Portão',false,String(e))}
// ---------- 8. torre ----------
try{
  const s=fresh(28);const h=home(0);const sp=freeSpot('torre',0,h.x,h.y,6);const tw=mkBld(0,'torre',sp.x,sp.y,true);
  const e=mkUnit(1,'cavaleiro',sp.x+5,sp.y+1);e.state='idle';const hp0=e.hp;sim(6);const hit=e.hp<hp0||e.dead;
  const a1=atkOf(tw),r1=brange(tw);queueUpgrade(tw,true);sim(32);const a2=atkOf(tw),r2=brange(tw);queueUpgrade(tw,true);sim(42);
  s.P[0].techs.flechas=true;const a3=atkOf(tw),r3=brange(tw);
  rec('Torre',hit&&tw.lvl===3&&a2>a1&&r2>r1&&a3>atkOf({...tw,o:1,kind:'b',type:'torre',lvl:3,d:tw.d})-0.5,`disparou=${hit} níveis: Vigia ${a1}/${r1} → Flechas ${a2}/${r2} → Fortificada (nível ${tw.lvl}); com Pontas de Ferro ${a3}/${r3}`);
}catch(e){rec('Torre',false,String(e))}
// ---------- 9-10. barcos e pesca ----------
try{
  const s=fresh(29);const L=s.G.lake;let dock=null;
  for(let r=0;r<20&&!dock;r++)for(let y=Math.floor(L.y-L.r-4);y<=L.y+L.r+4&&!dock;y++)for(let x=Math.floor(L.x-L.r-4);x<=L.x+L.r+4;x++){if(canPlace('doca',x,y,0,0,true)){dock=mkBld(0,'doca',x,y,true);break}}
  const food0=s.P[0].res.food;queueUnit(dock,'barcoPesca',true);sim(19);const boat=s.ents.find(e=>e.type==='barcoPesca'&&e.o===0);
  let onLand=0;for(let i=0;i<120*30;i++){step(1/30);for(const e of s.ents)if(e.kind==='u'&&e.d.naval&&s.blk[idx(Math.floor(e.x),Math.floor(e.y))]!==1)onLand++}
  const food1=s.P[0].res.food;
  rec('Barcos',!!boat&&onLand===0,`barco criado=${!!boat}, amostras em terra=${onLand}`);
  rec('Pesca',food1-(food0-0)>0&&boat.state!=='idle',`comida +${(food1-food0+0).toFixed(0)} em 2 min; estado ${boat&&boat.state}`);
  // reaparecimento
  const fish=[...s.byId.values()].find(r=>r.fish);const pos={x:fish.tx,y:fish.ty};fish.amt=1;removeRes(fish);const gone=!s.resAt[idx(pos.x,pos.y)];sim(152);const back=s.resAt[idx(pos.x,pos.y)];
  rec('Pesca: reaparecimento',gone&&!!back&&back.fish,`desapareceu=${gone} reapareceu com ${back?back.amt:0}`);
  // navios de guerra: galé contra barco inimigo
  const g=mkUnit(0,'gale',boat.x+1,boat.y);const eb=mkUnit(1,'barcoPesca',boat.x+1.5,boat.y+.5);setMover(eb);
  const fz=freeTileWater(s,boat.x,boat.y);if(fz){eb.x=fz.x;eb.y=fz.y}orderAttack(g,eb);sim(30);
  rec('Combate naval',eb.dead,'barco inimigo afundado='+!!eb.dead);
  window.__dock2=dock;
}catch(e){rec('Barcos',false,String(e))}
function freeTileWater(s,x,y){for(let r=1;r<6;r++)for(let yy=Math.floor(y)-r;yy<=Math.floor(y)+r;yy++)for(let xx=Math.floor(x)-r;xx<=Math.floor(x)+r;xx++){if(xx<0||yy<0||xx>79||yy>79)continue;if(s.blk[idx(xx,yy)]===1&&!s.resAt[idx(xx,yy)])return{x:xx+.5,y:yy+.5}}return null}
// ---------- 11. transporte ----------
try{
  const s=fresh(30);const L=s.G.lake;let dock=null;
  for(let y=Math.floor(L.y-L.r-4);y<=L.y+L.r+4&&!dock;y++)for(let x=Math.floor(L.x-L.r-4);x<=L.x+L.r+4;x++){if(canPlace('doca',x,y,0,0,true)){dock=mkBld(0,'doca',x,y,true);break}}
  queueUnit(dock,'transporte',true);sim(26);const tb=s.ents.find(e=>e.type==='transporte');
  // levar o barco para junto da margem da doca
  const sw=shoreWaterNear(dock.tx+1,dock.ty+1);moveTo(tb,sw.x,sw.y);sim(10);
  const lt=freeTile(dock.tx+1,dock.ty+3);const us=[mkUnit(0,'aldeao',lt.x+.5,lt.y+.5),mkUnit(0,'guerreiro',lt.x+.5,lt.y+.9),mkUnit(0,'sacerdote',lt.x+.9,lt.y+.5)];
  recount();const pop0=s.P[0].pop;
  command(us,tb,{x:tb.x,y:tb.y});sim(25);const boarded=tb.cargo.length;recount();const pop1=s.P[0].pop;
  const inEnts=us.filter(u=>s.ents.includes(u)).length;
  // atravessar: margem oposta
  const opp={x:L.x*2-tb.x,y:L.y*2-tb.y};const land=freeTile(Math.round(opp.x),Math.round(opp.y));const wsp=shoreWaterNear(land.x,land.y);moveTo(tb,wsp.x,wsp.y);tb.unloadAt=true;sim(40);
  const out=us.filter(u=>s.ents.includes(u)).length;const onLand=us.every(u=>s.blk[idx(Math.floor(u.x),Math.floor(u.y))]===0);
  rec('Transporte',boarded===3&&inEnts===0&&pop1===pop0&&out===3&&onLand,`embarcaram ${boarded}/8, população ${pop0}→${pop1}, desembarcaram ${out} em terra=${onLand}`);
}catch(e){rec('Transporte',false,String(e))}
// ---------- 12. cerco ----------
try{
  const s=fresh(31);const h=home(1);const tc=s.ents.find(e=>e.o===1&&e.type==='centro');
  const p=freeTile(tc.tx+5,tc.ty+1);const ram=mkUnit(0,'ariete',p.x+.5,p.y+.5);const hp0=tc.hp;orderAttack(ram,tc);sim(15);const ramDmg=hp0-tc.hp;kill(ram);
  const g=mkUnit(1,'guerreiro',ram.x+1,ram.y);const gh=g.hp;applyDmg(g,atkOf(ram),ram,false);const ramVsUnit=gh-g.hp;
  // catapulta: não atinge aliados
  const q=freeTile(h.x-12,h.y-12);clearArea(q.x+6,q.y,3);const cat=mkUnit(0,'catapulta',q.x+.5,q.y+.5);const ally=mkUnit(0,'guerreiro',q.x+6.5,q.y+.8);const en1=mkUnit(1,'guerreiro',q.x+6.5,q.y+.5),en2=mkUnit(1,'guerreiro',q.x+6.9,q.y+.5);
  en1.state=en2.state=ally.state='hold';const ah=ally.hp;orderAttack(cat,en1);sim(10);const allyHit=ally.hp<ah;const enHit=en1.hp<en1.max||en1.dead;
  // trebuchet: alcance 12 contra edifícios
  fresh(41);const s2=S();const tg=s2.ents.find(e=>e.o===1&&e.type==='centro');tg.hp=tg.max=5000;const tq=freeTile(tg.tx-10,tg.ty+1);const tr=mkUnit(0,'trebuchet',tq.x+.5,tq.y+.5);const th0=tg.hp;orderAttack(tr,tg);sim(30);const trD=th0-tg.hp;const trDist=distTo(tr,tg);
  rec('Cerco',ramDmg>200&&ramVsUnit<=2&&!allyHit&&enHit&&trD>100,`aríete: ${ramDmg.toFixed(0)} dano no Centro em 15 s, ${ramVsUnit} contra unidade; catapulta acertou inimigo=${enHit} aliado=${allyHit}; trebuchet ${trD.toFixed(0)} dano a ${trDist.toFixed(1)} casas`);
}catch(e){rec('Cerco',false,String(e))}
// ---------- 14. sacerdote, cura, conversão ----------
try{
  const s=fresh(32);const h=home(0);const p=freeTile(h.x+6,h.y+6);
  const pr=mkUnit(0,'sacerdote',p.x+.5,p.y+.5);const en=mkUnit(1,'lanceiro',p.x+5.5,p.y+.5);en.stance='hold';
  command([pr],en,{x:en.x,y:en.y});let t=0;for(;t<20*30&&en.o!==0;t++)step(1/30);
  const conv=en.o===0;const faith=pr.faith;
  const w=mkUnit(0,'guerreiro',pr.x+1,pr.y);w.hp=10;sim(30);const healed=w.hp>10;
  // recua quando ameaçado
  const pr2=mkUnit(0,'sacerdote',p.x+.5,p.y+3.5);const th=mkUnit(1,'guerreiro',p.x+1.5,p.y+3.5);th.stance='hold';const d0=Math.hypot(pr2.x-th.x,pr2.y-th.y);sim(3);const d1=Math.hypot(pr2.x-th.x,pr2.y-th.y);
  rec('Sacerdote',healed&&d1>d0+1,`cura ${w.hp>10?'10→'+w.hp.toFixed(0):'falhou'}; recuo ${d0.toFixed(1)}→${d1.toFixed(1)}`);
  rec('Conversão',conv&&faith<.5,`convertido em ${(t/30).toFixed(1)} s; fé depois ${faith.toFixed(2)}`);
}catch(e){rec('Sacerdote',false,String(e))}
// ---------- 15. tecnologias ----------
try{
  const s=fresh(33);const u=mkUnit(0,'guerreiro',40,40),a=mkUnit(0,'arqueiro',40,41),v=mkUnit(0,'aldeao',40,42);
  const b={atk:atkOf(u),arm:armOf(u),aa:atkOf(a),ar:rangeOf(a),vs:spd(v)};s.P[0].techs={forja:1,cota:1,flechas:1,roda:1};
  const t={atk:atkOf(u),arm:armOf(u),aa:atkOf(a),ar:rangeOf(a),vs:spd(v)};
  rec('Tecnologias',t.atk===b.atk+1&&t.arm===b.arm+1&&t.aa===b.aa+2&&t.ar===b.ar+1&&t.vs>b.vs*1.2,JSON.stringify(b)+' → '+JSON.stringify(t));
}catch(e){rec('Tecnologias',false,String(e))}
// ---------- 16. mudança de idade ----------
try{
  startGame(34);const s=S();s.AIs[1]=null;s.P[0].res.food=5000;s.P[0].res.gold=5000;const tc=s.ents.find(e=>e.o===0&&e.type==='centro');
  const lockB=queueUnit({o:0,queue:[]},'espadachim',true);queueAge(tc,true);sim(41);const a1=s.P[0].age;queueAge(tc,true);sim(56);const a2=s.P[0].age;
  const b={o:0,queue:[]};const okB=queueUnit(b,'besteiro',true);
  rec('Mudança de idade',!lockB&&a1===1&&a2===2&&okB,`espadachim bloqueado na Pedra=${!lockB}; idades ${a1}→${a2}; besteiro desbloqueado=${okB}`);
}catch(e){rec('Mudança de idade',false,String(e))}
// ---------- 17. maravilha ----------
try{
  const s=fresh(35);const h=home(0);const sp=freeSpot('maravilha',0,h.x,h.y,5);const w=mkBld(0,'maravilha',sp.x,sp.y,false);w.prog=.999;
  const v=mkUnit(0,'aldeao',sp.x-.5,sp.y+1.5);orderBuild(v,w);sim(3);const started=!!s.G.wonder;sim(301);
  rec('Maravilha',started&&s.G.over,`contagem iniciada=${started}; vitória aos 5 min=${s.G.over}`);
}catch(e){rec('Maravilha',false,String(e))}
// ---------- 18. save / load ----------
try{
  const s0=fresh(36);const h=home(0);
  const tw=mkBld(0,'torre',freeSpot('torre',0,h.x,h.y,6).x,freeSpot('torre',0,h.x,h.y,6).y,true);tw.lvl=2;
  const c=freeTile(h.x+9,h.y-6);mkBld(0,'muralhaPedra',c.x,c.y,true);const gt=mkBld(0,'portaoPedra',c.x+1,c.y,true);gt.locked=true;
  const L=s0.G.lake;let dock=null;for(let y=Math.floor(L.y-L.r-4);y<=L.y+L.r+4&&!dock;y++)for(let x=Math.floor(L.x-L.r-4);x<=L.x+L.r+4;x++){if(canPlace('doca',x,y,0,0,true)){dock=mkBld(0,'doca',x,y,true);break}}
  const fz=freeNearWater(dock);const tb=mkUnit(0,'transporte',fz.x+.5,fz.y+.5);const lt=freeTile(dock.tx,dock.ty+3);const pas=mkUnit(0,'lanceiro',lt.x+.5,lt.y+.5);boardUnit(pas,tb);
  const pr=mkUnit(0,'sacerdote',lt.x+.5,lt.y+1.5);pr.stance='hold';s0.P[0].techs.forja=true;
  s0.G.wonder={o:1,id:tw.id,t:123};
  const tc=s0.ents.find(e=>e.o===0&&e.type==='centro');queueUnit(tc,'aldeao',true);queueUnit(tc,'aldeao',true);
  sim(2);
  const snap=()=>{const s=S();recount();return JSON.stringify({n:s.ents.length,types:s.ents.map(e=>e.type).sort().join(','),res:s.P.map(p=>Object.values(p.res).map(Math.floor)),age:s.P.map(p=>p.age),techs:Object.keys(s.P[0].techs).sort(),
    walls:s.ents.filter(e=>e.d.wall||e.d.gate).length,locked:s.ents.filter(e=>e.locked).length,lvl:s.ents.filter(e=>e.type==='torre').map(e=>e.lvl),cargo:s.ents.filter(e=>e.cargo).map(e=>e.cargo.length),
    fish:[...s.byId.values()].filter(r=>r.fish).length,animals:s.ents.filter(e=>e.o===2).length,wonder:s.G.wonder&&Math.round(s.G.wonder.t),queue:tc&&s.ents.find(e=>e.id===tc.id).queue.length,pop:s.P.map(p=>p.pop),stance:s.ents.filter(e=>e.stance==='hold').length,hp:Math.round(s.ents.reduce((a,e)=>a+e.hp,0))})};
  const A=snap();saveGame(true);const raw=localStorage.getItem('alv_save_v1');startGame(99);loadGame();const B=snap();
  let parsed=true;try{JSON.parse(raw)}catch(e){parsed=false}
  rec('Save',parsed&&raw.length>1000,'tamanho '+raw.length+' bytes');
  rec('Load',A===B,A===B?'estado idêntico (unidades, edifícios, carga, peixes, fila, Maravilha, posturas)':'antes '+A+'\ndepois '+B);
  sim(20);rec('Continuar depois de carregar',S().ents.length>0&&!S().G.over,'20 s simulados sem erros');
}catch(e){rec('Save',false,String(e))}
// ---------- 22. nevoeiro ----------
try{
  startGame(37);const s=S();s.AIs[1]=null;updVis();const en=s.ents.find(e=>e.o===1&&e.kind==='u');const eb=s.ents.find(e=>e.o===1&&e.kind==='b');
  const hidU=!visibleTo0(en),hidB=!seenBy0(eb);s.vis.fill(2);const shownU=visibleTo0(en),shownB=seenBy0(eb);updVis();const remembered=seenBy0(eb),hidAgain=!visibleTo0(en);
  rec('Nevoeiro',hidU&&hidB&&shownU&&shownB&&remembered&&hidAgain,`unidade escondida=${hidU} edifício escondido=${hidB}; depois de explorado: edifício lembrado=${remembered}, unidade volta a esconder=${hidAgain}`);
}catch(e){rec('Nevoeiro',false,String(e))}
// ---------- 23. vibração ----------
try{
  let n=0;Object.defineProperty(navigator,'vibrate',{value:()=>{n++;return true},configurable:true,writable:true});startGame(38);const s=S();s.AIs[1]=null;
  const tc=s.ents.find(e=>e.o===0&&e.type==='centro');const e=mkUnit(1,'guerreiro',tc.tx+4,tc.ty+1);applyDmg(tc,10,e,false);const n1=n;
  document.getElementById('bVib').click();s.G.time+=20;applyDmg(tc,10,e,false);const n2=n;document.getElementById('bVib').click();
  rec('Vibração',n1>=1&&n2===n1,`vibrou ao atacar o Centro=${n1>=1}; desligada não vibra=${n2===n1}`);
}catch(e){rec('Vibração',false,String(e))}
// ---------- 21. minimapa ----------
try{
  startGame(39);const s=S();s.vis.fill(2);s.AIs[1]=null;const h=home(0);const c=freeTile(h.x+8,h.y+8);for(let k=0;k<5;k++)mkBld(0,'muralhaPedra',c.x+k,c.y,true);
  {const d2=fogImg.data;for(let i=0;i<W*H;i++)d2[i*4+3]=0;fogCtx.putImageData(fogImg,0,0)}renderMini();const m=document.getElementById('mini').getContext('2d');const d=m.getImageData(0,0,320,160).data;let blue=0,cyan=0,red=0;
  for(let i=0;i<d.length;i+=4){if(d[i]<90&&d[i+1]>110&&d[i+2]>200)blue++;if(d[i]>110&&d[i+1]>200&&d[i+2]>230)cyan++;if(d[i]>190&&d[i+1]<110&&d[i+2]<100)red++}
  rec('Minimapa',blue>5&&cyan>3&&red>5,`píxeis: azul(jogador)=${blue} ciano(peixe)=${cyan} vermelho(rival)=${red}`);
}catch(e){rec('Minimapa',false,String(e))}

// ---------- regressão: caça, javali, isométrico, zoom/pan ----------
try{
  startGame(22);const s=S();s.AIs[1]=null;
  const vs=s.ents.filter(e=>e.o===0&&e.type==='aldeao');let g=null,bd=99;for(const e of s.ents)if(e.o===2&&e.type==='gazela'){const d=Math.hypot(e.x-vs[0].x,e.y-vs[0].y);if(d<bd){bd=d;g=e}}
  const f0=s.P[0].res.food;command(vs,g,{x:g.x,y:g.y});sim(120);
  const carc=[...s.byId.values()].some(r=>r.carcass)||s.P[0].res.food>f0;
  rec('Caça e carne',g.dead&&s.P[0].res.food>f0,`gazela abatida=${!!g.dead}; comida ${f0}→${s.P[0].res.food}; aldeões: ${vs.map(v=>v.state).join(',')}`);
  const j=s.ents.find(e=>e.o===2&&e.type==='javali');const v=vs[0];v.x=j.x+1.5;v.y=j.y;const vh=v.hp;command([v],j,{x:j.x,y:j.y});sim(4);
  rec('Javali contra-ataca',j.state==='attack'||v.hp<vh,`estado do javali ${j.state}; vida do aldeão ${vh}→${v.hp.toFixed(0)}`);
}catch(e){rec('Caça e carne',false,String(e))}
try{
  let maxErr=0;for(let k=0;k<200;k++){const x=Math.random()*80,y=Math.random()*80;const p=proj(x,y);const w=unproj(p.x,p.y);maxErr=Math.max(maxErr,Math.abs(w.x-x),Math.abs(w.y-y))}
  const s=S();const z0=cam.z;centerCam(40,40);const c0=s2w(vw/2,(vh-70)/2);
  cam.x+=100;const c1=s2w(vw/2,(vh-70)/2);const wpt=s2p(200,150);cam.z=1.6;cam.x=wpt.x-200/cam.z;cam.y=wpt.y-150/cam.z;const wpt2=s2p(200,150);cam.z=z0;
  rec('Motor isométrico',maxErr<1e-9,'erro máximo projeção/inversa '+maxErr.toExponential(1));
  rec('Zoom e pan',Math.abs(c0.x-40)<.01&&Math.abs(c0.y-40)<.01&&Math.hypot(c1.x-c0.x,c1.y-c0.y)>.5&&Math.hypot(wpt.x-wpt2.x,wpt.y-wpt2.y)<1e-6,`centrar ok; pan move ${Math.hypot(c1.x-c0.x,c1.y-c0.y).toFixed(2)} casas; zoom mantém o ponto sob o dedo`);
}catch(e){rec('Motor isométrico',false,String(e))}
window.__results=T;
})();
