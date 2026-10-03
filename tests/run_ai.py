import asyncio, json, sys
from playwright.async_api import async_playwright
GAME="file:///home/claude/alvorada/www/index.html"
SEEDS=[int(x) for x in sys.argv[1:]] or [101,202,303,404]
JS=r"""
(seed)=>{
  startGame(seed);let s=__S();s.AIs[0]=mkAI(0,DIFF[1]);
  const st={conv:0,shipKills:0,wallsBuilt:[0,0],gatePass:0,siege:[0,0],priests:[0,0],ships:[0,0],stuck:new Set(),idleV:0,cross:0,shipLand:0,neg:0,pop:0,dup:0,bad:0,saveOk:null,maxEnts:0,types:[new Set(),new Set()],attacks:0,overT:null,winner:null,techs:[0,0],ages:[0,0],fish:[0,0],dmgWall:0};
  const oc=convertUnit;window.convertUnit=function(t,o){st.conv++;return oc(t,o)};
  const ok=kill;window.kill=function(e,src){if(e.kind==='u'&&e.d.naval&&src&&src.d&&src.d.naval)st.shipKills++;return ok(e,src)};
  const last=new Map(),idleSince=new Map();let t=0;
  const DT=1/30;
  for(;t<60*60*30;t++){
    step(DT);
    if(t%30!==0)continue;const sec=t/30;
    recount();
    const ids=new Set();
    for(const e of s.ents){
      if(ids.has(e.id))st.dup++;ids.add(e.id);if(s.byId.get(e.id)!==e)st.bad++;
      if(e.kind==='u'){
        const i=idx(Math.floor(e.x),Math.floor(e.y));const b=s.blk[i];
        if(e.d.naval){if(b!==1)st.shipLand++}
        else{if(b===3){st.cross++;if(!st.ci)st.ci=[];if(st.ci.length<6){const g=s.byId.get(s.bldAt[i]);st.ci.push(`${sec}s ${e.type}#${e.id} o${e.o} ${e.state} @${e.x.toFixed(2)},${e.y.toFixed(2)} em ${g?g.type+(g.done?'':'*')+' o'+g.o:'?'} path=${e.path?e.path.length+'/'+e.pi:'-'}`)}}else if(b===4){const g=s.byId.get(s.bldAt[i]);if(!g||g.o!==e.o)st.cross++;else st.gatePass++}else if(b===1||b===2){st.cross++;if(!st.ci)st.ci=[];if(st.ci.length<6)st.ci.push(`${sec}s ${e.type} ${e.state} blk${b} @${e.x.toFixed(2)},${e.y.toFixed(2)}`)}}
        if(e.o<2){st.types[e.o].add(e.type);if(e.d.siege)st.siege[e.o]=Math.max(st.siege[e.o],1);if(e.d.convert)st.priests[e.o]=1;if(e.d.naval)st.ships[e.o]=1}
        if((e.state==='move'||e.state==='return'||e.state==='board')&&e.o<2){const L=last.get(e.id);if(L&&L.st===e.state&&sec-L.t>=25&&Math.hypot(L.x-e.x,L.y-e.y)<.3){st.stuck.add(e.type+'@'+e.state);if(!st.si)st.si=[];if(st.si.length<4){const dp=nearestDrop(e.o,e.x,e.y,!!e.d.naval);st.si.push(`${sec}s ${e.type}#${e.id} @${e.x.toFixed(1)},${e.y.toFixed(1)} drop ${dp?dp.type+'@'+dp.tx+','+dp.ty:'-'} path ${e.path?e.path.length+'/'+e.pi:'-'} fails ${e.fails}`)}}if(!L||L.st!==e.state||Math.hypot(L.x-e.x,L.y-e.y)>=.3)last.set(e.id,{x:e.x,y:e.y,t:sec,st:e.state})}else last.delete(e.id);
        if(e.type==='aldeao'&&e.o<2){if(e.state==='idle'){if(!idleSince.has(e.id))idleSince.set(e.id,sec);else if(sec-idleSince.get(e.id)>45&&['wood','food','gold','stone'].some(k=>findRes(k,e.x,e.y,80,e.o))){st.idleV++;if(!st.ii)st.ii=[];if(st.ii.length<4)st.ii.push(`${sec}s #${e.id} o${e.o} @${e.x.toFixed(1)},${e.y.toFixed(1)} gk=${e.gkind} aiIdle=${e.aiIdle}`)}}else idleSince.delete(e.id)}
        if(e.d.fish&&e.state==='gather')st.fish[e.o]=1;
      }else{if(e.hp>e.max+.01||!(e.max>0))st.bad++;if((e.d.wall||e.d.gate)&&e.done&&e.o<2)st.wallsBuilt[e.o]=Math.max(st.wallsBuilt[e.o],s.ents.filter(w=>w.o===e.o&&(w.d.wall||w.d.gate)&&w.done).length);if((e.d.wall||e.d.gate)&&e.hp<e.max)st.dmgWall=1}
    }
    for(let o=0;o<2;o++){for(const k in s.P[o].res)if(s.P[o].res[k]<-0.001)st.neg++;
      let n=0;for(const e of s.ents)if(e.kind==='u'&&e.o===o){n++;if(e.cargo)n+=e.cargo.length}if(n!==s.P[o].pop)st.pop++;
      st.techs[o]=Object.keys(s.P[o].techs).length;st.ages[o]=s.P[o].age;}
    st.maxEnts=Math.max(st.maxEnts,s.ents.length);
    if(sec===900){const A=JSON.stringify({n:s.ents.length,res:s.P.map(p=>Object.values(p.res).map(Math.floor))});saveGame(true);const raw=localStorage.getItem('alv_save_v1');loadGame();
      s=__S();const s2=s;const B=JSON.stringify({n:s2.ents.length,res:s2.P.map(p=>Object.values(p.res).map(Math.floor))});st.saveOk=A===B?'ok':'diff '+A+' / '+B;
      // depois de carregar, s aponta para o estado novo
      last.clear();idleSince.clear();}
    if(s.G.over||__S().G.over){st.overT=(sec/60).toFixed(1);const S2=__S();st.winner=S2.ents.some(e=>e.o===0&&e.kind==='b'&&e.type==='centro')?'Azul':'Vermelho';break}
  }
  window.convertUnit=oc;window.kill=ok;
  const r={...st,stuck:[...st.stuck],types:st.types.map(x=>[...x].sort().join(','))};return r;
}
"""
WONDER=r"""
(seed)=>{
  startGame(seed);const s=__S();s.AIs[0]=mkAI(0,DIFF[1]);
  for(let t=0;t<14*60*30;t++)step(1/30);
  const S2=__S();const h=S2.G.starts[0];let w=null;
  for(let r=3;r<16&&!w;r++)for(let y=h.y-r;y<=h.y+r&&!w;y++)for(let x=h.x-r;x<=h.x+r;x++){if(canPlace('maravilha',x,y,0,0,true)){w=mkBld(0,'maravilha',x,y,true);break}}
  if(!w)return {err:'sem espaço para maravilha'};
  S2.G.wonder={o:0,id:w.id,t:300};const hp0=w.hp;let minHp=w.hp;let picks=new Set();let sent=0,siegeMax=0,wallHits=0;const wallHp0=__S().ents.filter(e=>e.o===0&&(e.d.wall||e.d.gate)).reduce((a,e)=>a+e.hp,0);
  for(let t=0;t<300*30;t++){step(1/30);if(t%30===0){const A=__S().AIs[1];if(A&&A.picks)A.picks.forEach(p=>picks.add(p));sent=Math.max(sent,__S().ents.filter(e=>e.o===1&&e.kind==='u'&&e.d.mil&&(e.target===w||(e.target&&e.target.o===0&&e.target.kind==='b'&&(e.target.d.wall||e.target.d.gate)))).length);siegeMax=Math.max(siegeMax,__S().ents.filter(e=>e.o===1&&e.d.siege).length);minHp=Math.min(minHp,w.dead?0:w.hp)}if(__S().G.over||w.dead)break}
  const wallHp1=__S().ents.filter(e=>e.o===0&&(e.d.wall||e.d.gate)).reduce((a,e)=>a+e.hp,0);return {hp0,minHp:Math.round(minHp),destroyed:!!w.dead,over:__S().G.over,picks:[...picks].join(','),maxUnitsOnWonderOrWalls:sent,siegeMax,wallDamage:Math.round(wallHp0-wallHp1),p0walls:__S().ents.filter(e=>e.o===0&&(e.d.wall||e.d.gate)).length};
}
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":844,"height":390})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
        await pg.goto(GAME); await pg.click("#lgPreview"); await pg.click("#bPlay"); await pg.wait_for_timeout(300)
        for sd in SEEDS:
            r=await pg.evaluate(JS, sd)
            print("SEED",sd,json.dumps(r,ensure_ascii=False))
        r=await pg.evaluate(WONDER, 505)
        print("WONDER",json.dumps(r,ensure_ascii=False))
        print("ERRS",errs[:5])
        await b.close()
asyncio.run(main())
