# Testes do sistema de som (PASS/FAIL)
import asyncio,json
from playwright.async_api import async_playwright
R=[]
def rep(ok,name,info):R.append((ok,name,info));print(('PASS' if ok else 'FAIL').ljust(10),name+':',info,flush=True)
SETUP_BATTLE=r"""
(args)=>{const [N,seed]=args;startGame(seed);const s=__S();s.AIs[1]=null;s.vis.fill(2);s.P[0].age=2;s.P[1].age=2;
 const cx=40,cy=40;for(let y=cy-12;y<=cy+12;y++)for(let x=cx-14;x<=cx+14;x++){const r=s.resAt[idx(x,y)];if(r&&!r.fish)removeRes(r)}
 const T=['guerreiro','lanceiro','espadachim','arqueiro','besteiro','cavaleiro','cavPesada','cavArqueira','aldeao','sacerdote','catapulta','ariete'];
 const A=[],B=[];for(let i=0;i<N;i++){const side=i%2,k=(i>>1);const u=mkUnit(side?1:0,T[k%T.length],cx+(side?3:-3)+(k%6)*.6,cy-5+Math.floor(k/6)*.6);(side?B:A).push(u)}
 for(const u of A)orderAttack(u,B[k_(u.id,B.length)]);for(const u of B)orderAttack(u,A[k_(u.id,A.length)]);
 function k_(i,n){return (i*7919)%n}
 paused=false;cam.z=1;centerCam(cx,cy);return true}
"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]);pg=await b.new_page(viewport={"width":900,"height":420},device_scale_factor=2)
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:300]))
    await pg.goto("file:///home/claude/alvorada/www/index.html");await pg.wait_for_timeout(300)
    # 1 desbloqueio e música do menu
    st=await pg.evaluate("()=>({ctx:!!__AUD().AUD.ctx})")
    await pg.mouse.click(5,300);await pg.wait_for_timeout(600)
    r=await pg.evaluate("()=>{const A=__AUD();return{ctx:A.AUD.ctx&&A.AUD.ctx.state,mood:A.MUS.mood}}")
    rep(not st['ctx'] and r['ctx']=='running' and r['mood']=='menu','Arranque',f"sem áudio antes do 1.º toque={not st['ctx']}; depois: contexto {r['ctx']}, música '{r['mood']}'")
    # 2 síntese de todos os sons
    r=await pg.evaluate("""()=>{const A=__AUD();const bad=[];let n=0,ms=0,bytes=0;for(const k of Object.keys(A.SND))for(let v=0;v<A.SND[k].v;v++){const t=performance.now();const b=sndBuf(k,v);ms+=performance.now()-t;n++;const d=b.getChannelData(0);bytes+=d.length*4;let pk=0,nan=0;for(const x of d){if(!isFinite(x))nan=1;else pk=Math.max(pk,Math.abs(x))}if(nan||pk<.05||pk>1)bad.push(k+v)}
      const ins=[];for(const i of ['dum','tak','shaker']){const t=performance.now();instBuf(i,0);ms+=performance.now()-t}
      return{types:Object.keys(A.SND).length,n,ms:Math.round(ms),mb:+(bytes/1e6).toFixed(1),bad}}""")
    rep(not r['bad'] and r['types']>=60,'Síntese',f"{r['types']} tipos de som, {r['n']} variações, sem silêncio/NaN/saturação; tempo total {r['ms']} ms; memória dos efeitos {r['mb']} MB")
    # 3 entrar no jogo → música 'paz' e ambiente
    await pg.click("#lgPreview"); await pg.click("#bPlay");await pg.wait_for_timeout(1500)
    r=await pg.evaluate("()=>{const A=__AUD();return{mood:A.MUS.mood,amb:!!A.AUD.amb,by:A.AUD.stats.by}}")
    rep(r['mood']=='paz' and r['amb'] and r['by'].get('research',0)>=1,'Início de partida',f"música '{r['mood']}', ambiente ligado={r['amb']}, som de seleção do Centro tocou={r['by'].get('research',0)>=1}")
    # 4 espacial
    r=await pg.evaluate("""()=>{const A=__AUD(),s=__S();const c=s2w(vw/2,vh/2);const far=s2w(vw*4,vh*4);A.AUD.last={};
      const a=A.spatial(c.x,c.y,true),b=A.spatial(far.x,far.y,true);const l=s2w(vw*.1,vh/2),rr=s2w(vw*.9,vh/2);const pl=A.spatial(l.x,l.y,true),pr=A.spatial(rr.x,rr.y,true);
      // nevoeiro: casa não visível
      let hid=null;for(let y=0;y<80&&!hid;y++)for(let x=0;x<80;x++)if(s.vis[idx(x,y)]!==2){hid=[x,y];break}
      const z0=cam.z;cam.z=.5;const hv=A.spatial(c.x,c.y,true).g;cam.z=z0;
      return{center:a&&a.g,far:b,panL:pl&&pl.pan,panR:pr&&pr.pan,fog:A.spatial(hid[0]+.5,hid[1]+.5,false),zoomOut:hv}}""")
    rep(r['center']>.9 and r['far'] is None and r['panL']<-.4 and r['panR']>.4 and r['fog'] is None,'Som posicional',f"centro ganho {r['center']:.2f}; longe do ecrã cortado={r['far'] is None}; pan esquerda {r['panL']:.2f} / direita {r['panR']:.2f}; no nevoeiro cortado={r['fog'] is None}; zoom afastado ganho {r['zoomOut']:.2f}")
    # 5 limites
    r=await pg.evaluate("""()=>{const A=__AUD();A.AUD.last={};A.AUD.fnew=0;let ok=0;for(let i=0;i<50;i++)if(A.snd('clash'))ok++;
      A.AUD.fnew=0;let k=0;for(const n of ['chop','hammer','hoe','bow','club','stab','boom','splash','heal','pop'])if(A.snd(n))k++;return{same:ok,frame:k}}""")
    rep(r['same']==1 and r['frame']<=7,'Limites',f"50 pedidos do mesmo som no mesmo instante → {r['same']} tocado; 10 sons diferentes no mesmo frame → {r['frame']} tocados (máx. 7)")
    # 6 sons de trabalho ligados à animação
    r=await pg.evaluate("""async()=>{const A=__AUD(),s=__S();A.AUD.stats.by={};const vs=s.ents.filter(e=>e.kind==='u'&&e.o===0&&e.type==='aldeao');
      const t=__alv.res().filter(e=>e.rk==='wood').sort((a,b)=>Math.hypot(a.tx-vs[0].x,a.ty-vs[0].y)-Math.hypot(b.tx-vs[0].x,b.ty-vs[0].y))[0];for(const v of vs){orderGather(v,t);v.carry=9;v.ctype='wood'}centerCam(t.tx,t.ty);
      await new Promise(r=>setTimeout(r,9000));return A.AUD.stats.by}""")
    rep(r.get('chop',0)>=3 and r.get('dep_wood',0)>=1,'Trabalho',f"aldeões a cortar madeira à vista: {r.get('chop',0)} golpes de machado ouvidos em 9 s; depósitos: {r.get('dep_wood',0)}")
    # 7 batalha → música de batalha, sons de combate, limites de vozes
    await pg.evaluate(SETUP_BATTLE,[120,5])
    await pg.evaluate("()=>{const A=__AUD();A.AUD.stats.by={};window.__vmax=0;window.__fmax=0;const f=window.audioFrame;window.audioFrame=function(r){f(r);window.__vmax=Math.max(__vmax,A.AUD.voices)}}")
    moods=[]
    for i in range(10):
      await pg.wait_for_timeout(1000);moods.append(await pg.evaluate("()=>__AUD().MUS.mood"))
    r=await pg.evaluate("()=>({by:__AUD().AUD.stats.by,vmax:__vmax,stats:__AUD().AUD.stats})")
    by=r['by'];kinds=[k for k in ['clash','stab','bow','xbow','arrow_hit','death','death_horse','cat_launch','boom','ram_hit','gallop','v_attack','heal','chant','convert','siege_break'] if by.get(k)]
    rep('batalha' in moods and len(kinds)>=8 and r['vmax']<=28,'Batalha (120 unidades)',f"música passou a 'batalha'={('batalha' in moods)} (sequência {','.join(m[0] for m in moods)}); tipos de som ouvidos: {', '.join(kinds)}; vozes simultâneas máx. {r['vmax']} (limite 28)")
    # 8 pausa e regresso
    r=await pg.evaluate("async()=>{togglePause();await new Promise(r=>setTimeout(r,300));const a=__AUD().AUD.ctx.state;togglePause();await new Promise(r=>setTimeout(r,300));return{p:a,r:__AUD().AUD.ctx.state}}")
    rep(r['p']=='suspended' and r['r']=='running','Pausa',f"em pausa: {r['p']}; ao continuar: {r['r']}")
    # 9 silenciar e volumes guardados
    r=await pg.evaluate("""async()=>{togglePause();document.getElementById('bSound').click();const A=__AUD();const off=A.AUD.on;A.AUD.last={};const played=A.snd('ui_click',null,null,{force:1});
      const el=document.getElementById('vMusic');el.value=23;el.dispatchEvent(new Event('input'));el.dispatchEvent(new Event('change'));document.getElementById('bSound').click();togglePause();
      const saved=JSON.parse(localStorage.getItem('alv_audio'));return{off,played,saved}}""")
    rep(r['off'] is False and r['played'] is False and abs(r['saved']['music']-.23)<1e-6 and r['saved']['on'] is True,'Silenciar e volumes',f"silenciado não toca={not r['played']}; volume da música guardado={r['saved']['music']}; som religado={r['saved']['on']}")
    await pg.reload();await pg.wait_for_timeout(300)
    r=await pg.evaluate("()=>({m:__AUD().AUD.vol.music,s:document.getElementById('vMusic').value})")
    rep(abs(r['m']-.23)<1e-6 and r['s']=='23','Preferências após reabrir',f"volume da música {r['m']} e barra {r['s']}")
    # 10 determinismo: som ligado vs desligado → simulação idêntica
    r=await pg.evaluate(r"""(SB)=>{const run=on=>{const A=__AUD();A.AUD.on=on;eval('('+SB+')')([60,9]);for(let i=0;i<900;i++){step(1/30);if(i%3===0){render();audioFrame(.1)}}const s=__S();
        let h=0;for(const e of s.ents){h=(h*31+Math.round((e.x||e.tx)*1000)+Math.round(e.hp*100))|0}return h+':'+s.ents.length};
      audioInit();const a=run(true),b=run(false);__AUD().AUD.on=true;return{a,b}}""",SETUP_BATTLE)
    rep(r['a']==r['b'],'Jogabilidade inalterada',f"mesma batalha 30 s com som ligado vs desligado → estado {r['a']} vs {r['b']}")
    # 11 custo por frame
    r=await pg.evaluate(r"""(SB)=>{eval('('+SB+')')([200,3]);const A=__AUD();for(let i=0;i<30;i++){step(1/30);render()}
      let t=0;for(let i=0;i<120;i++){step(1/30);render();const t0=performance.now();audioFrame(1/30);t+=performance.now()-t0}return{ms:+(t/120).toFixed(3)}}""",SETUP_BATTLE)
    rep(r['ms']<1.5,'Desempenho do som',f"200 unidades em combate: lógica de som {r['ms']} ms por frame")
    # 12 fim de jogo
    r=await pg.evaluate("()=>{const A=__AUD();A.AUD.stats.by={};A.AUD.last={};endGame(true);return{by:A.AUD.stats.by,want:A.MUS.want,amb:!!A.AUD.amb}}")
    rep(r['by'].get('victory')==1 and r['want']=='menu' and not r['amb'],'Fim de jogo',f"fanfarra de vitória tocou; música volta ao menu; ambiente parado")
    rep(not errs,'Erros JavaScript',str(errs) if errs else 'nenhum')
    await b.close()
asyncio.run(main())
print(f"\n{sum(1 for x in R if x[0])}/{len(R)} PASS")
