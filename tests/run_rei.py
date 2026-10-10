# Testes do Rei herói: editor, níveis/XP, aura, poderes, morte = fim do jogo em todos os modos, gravação, Regicídio, painel e desenho.
import asyncio, os, sys
from playwright.async_api import async_playwright
GAME="file://"+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','www','index.html'))
SHOTS=os.environ.get('SHOTS','/tmp/rei_shots');os.makedirs(SHOTS,exist_ok=True)
R=[]
def rep(ok,name,info):R.append((ok,name,info));print(('PASS' if ok else 'FAIL').ljust(6),name+':',info,flush=True)
ADV="(s)=>{for(let i=0;i<s*30;i++){step(1/30);if(!__S().running||__S().G.over)break}return __S().G.time}"
async def adv(pg,s):return await pg.evaluate(ADV,s)
H="(()=>{const h=__S().G.hero&&__S().G.hero[0];const k=heroKing(0);return h?{lv:h.lv,xp:h.xp,resp:h.resp,cd:h.cd,king:!!k,hp:k&&k.hp,max:k&&k.max,kills:h.kills}:null})()"
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    ctx=await b.new_context(viewport={"width":900,"height":440},device_scale_factor=2)
    pg=await ctx.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:300]))
    await pg.goto(GAME);await pg.wait_for_timeout(600);await pg.evaluate("localStorage.clear()")
    await pg.click("#lgPreview");await pg.wait_for_timeout(200)
    # editor
    await pg.click("#bCamp");await pg.wait_for_timeout(150);await pg.click("#bReinoKing");await pg.wait_for_timeout(300)
    vis=await pg.evaluate("!document.getElementById('sRei').hidden")
    await pg.fill("#krName","Afonso");await pg.evaluate("document.querySelector(\"#krCrown button[data-i='1']\").click()");await pg.click("#krCape button:nth-child(2)");await pg.wait_for_timeout(400)
    await pg.screenshot(path=SHOTS+"/editor.png")
    await pg.click("#krSave");await pg.wait_for_timeout(200)
    look=await pg.evaluate("JSON.parse(localStorage.getItem('alv_rei'))")
    rep(vis and look=={'name':'Afonso','crown':1,'cape':'#6a2a9a'},"Editor do Rei",f"ecrã visível={vis}; guardado {look}")
    nasty=await pg.evaluate("kingLookClean({name:'<b>Xé</b>&\"'+'x'.repeat(30),crown:9,cape:'red'})")
    rep('<' not in nasty['name'] and len(nasty['name'])<=16 and nasty['crown']==3 and nasty['cape']=='#b0202a',"Nome e opções seguros",str(nasty))
    # fundar o reino → Rei desde o início
    await pg.click("#bCampGo");await pg.wait_for_timeout(500)
    h=await pg.evaluate(H)
    rep(h and h['king'] and h['lv']==1 and h['max']==160,"Rei nasce com o reino",str(h))
    kb=await pg.evaluate("!document.getElementById('bKing').hidden")
    await pg.evaluate("document.getElementById('bKing').click()");await pg.wait_for_timeout(300)
    seli=await pg.evaluate("({sel:__S().sel.map(e=>e.type),cmds:[...document.querySelectorAll('#cmds .cmd')].map(b=>b.textContent.trim()).slice(0,4),info:document.getElementById('info').textContent.slice(0,80)})")
    rep(kb and seli['sel']==['rei'] and any('Grito' in c for c in seli['cmds']) and 'nível 1' in seli['info'],"Botão 👑 e painel do Rei",str(seli))
    await pg.evaluate("(()=>{const k=heroKing(0);__S().cam.z=2.2;centerCam(k.x,k.y)})()");await pg.wait_for_timeout(500)
    await pg.screenshot(path=SHOTS+"/rei_jogo.png")
    # XP e níveis
    lv=await pg.evaluate("""(()=>{const k=heroKing(0);let n=0;for(let i=0;i<40;i++){const e=mkUnit(1,'espadachim',k.x+1,k.y+1);kill(e,k);n++}return n})()""")
    await adv(pg,.5);h2=await pg.evaluate(H)
    rep(h2['lv']>=6 and h2['max']>h['max'] and h2['kills']==40,"Sobe de nível com as batalhas",f"{lv} inimigos abatidos pelo Rei → nível {h2['lv']}, vida máx. {h['max']}→{h2['max']}")
    # aura: soldado perto do Rei vs longe
    au=await pg.evaluate("""(()=>{const k=heroKing(0);const a=mkUnit(0,'espadachim',k.x+1,k.y);const f=mkUnit(0,'espadachim',k.x+30,k.y+30);heroTick(1/30);return{perto:atkOf(a),longe:atkOf(f),aid:a.id,fid:f.id,armP:armOf(a),armL:armOf(f)}})()""")
    rep(au['perto']>au['longe'] and au['armP']>au['armL'],"Aura do Rei",f"ataque perto {au['perto']} vs longe {au['longe']}; armadura {au['armP']} vs {au['armL']}")
    # poderes
    g=await pg.evaluate("""(()=>{const s=__S();const k=heroKing(0);const a=s.byId.get(%d);const b0=atkOf(a),v0=spd(a);act('power',{p:'grito'});return{ids:s.G.hero[0].wc&&s.G.hero[0].wc.ids.length,b0,b1:atkOf(a),v0,v1:spd(a),cd:s.G.hero[0].cd.grito}})()"""%au['aid'])
    rep(g['ids']>0 and g['b1']>g['b0'] and g['v1']>g['v0'] and g['cd']==60,"📯 Grito de guerra",str(g))
    again=await pg.evaluate("(()=>{act('power',{p:'grito'});return __S().G.hero[0].wc.until})()")
    await adv(pg,11);g2=await pg.evaluate("(()=>{const a=__S().byId.get(%d);return{wc:__S().G.hero[0].wc,atk:atkOf(a)}})()"%au['aid'])
    rep(g2['wc'] is None and g2['atk']==g['b0'],"Grito acaba ao fim de 10 s e respeita a recarga",str(g2))
    be=await pg.evaluate("""(()=>{const s=__S(),a=s.byId.get(%d);a.hp=10;act('power',{p:'bencao'});return{hp:a.hp,max:a.max}})()"""%au['aid'])
    rep(be['hp']>10,"✨ Bênção real cura",str(be))
    gu=await pg.evaluate("""(()=>{const s=__S();s.P[0].res.food+=500;s.P[0].res.gold+=500;const n0=s.ents.filter(e=>e.o===0&&e.kind==='u').length,f0=s.P[0].res.food;act('power',{p:'guarda'});return{novos:s.ents.filter(e=>e.o===0&&e.kind==='u').length-n0,custo:f0-s.P[0].res.food}})()""")
    rep(gu['novos']==3 and gu['custo']==100,"🛡️ Guarda real",str(gu))
    # gravar e voltar
    lv0=(await pg.evaluate(H))['lv'];d2=await pg.evaluate(H)
    await pg.evaluate("saveGame(true)");await pg.evaluate("document.getElementById('bQuit').click()");await pg.wait_for_timeout(200)
    line=await pg.evaluate("(()=>{document.getElementById('bCamp').click();return document.querySelector('#cmInfo .krline').textContent})()")
    await pg.click("#bCampGo");await pg.wait_for_timeout(400);d3=await pg.evaluate(H)
    rep(d3['lv']==lv0 and d3['king'] and d3['max']==d2['max'],"Rei gravado com o reino",f"ecrã do reino: '{line}'; depois de carregar: nível {d3['lv']}")
    # gravação antiga do Reino (sem Rei) recebe o Rei
    await pg.evaluate("document.getElementById('bQuit').click()");await pg.wait_for_timeout(150)
    await pg.evaluate("(()=>{const s=JSON.parse(localStorage.getItem(reinoKey()));delete s.X.hero;delete s.X.king;s.ents=s.ents.filter(e=>e.t!=='rei');localStorage.setItem(reinoKey(),JSON.stringify(s))})()")
    await pg.evaluate("reinoLoad(false)");await pg.wait_for_timeout(300)
    d4=await pg.evaluate(H);rep(d4 and d4['king'] and not (await pg.evaluate("__S().G.over")),"Reino antigo ganha o Rei",str(d4))
    # o Rei cai no Reino → missão perdida (sem renascer)
    await pg.evaluate("(()=>{kill(heroKing(0),null)})()");await adv(pg,3);await pg.wait_for_timeout(1200)
    rd=await pg.evaluate("({over:__S().G.over,title:document.getElementById('endTitle').textContent,txt:document.getElementById('endText').textContent,king:!!heroKing(0)})")
    rep(rd['over'] and not rd['king'] and 'Rei caiu' in rd['txt'],"Reino: o Rei cai e o jogo acaba",str(rd))
    # partida normal: os dois têm Rei; matar o Rei rival dá a vitória
    await pg.evaluate("(()=>{document.getElementById('sEnd').hidden=true;document.getElementById('bQuit').click()})()");await pg.wait_for_timeout(150)
    await pg.evaluate("(()=>{gameMode='normal';startGame(321,{map:'rios',vic:'classico',civ:['mar','planicies']})})()");await pg.wait_for_timeout(300)
    nm=await pg.evaluate("({kings:__S().ents.filter(e=>e.type==='rei').length,hero:!!__S().G.hero,btn:!document.getElementById('bKing').hidden})")
    await pg.evaluate("(()=>{kill(heroKing(1),heroKing(0))})()");await adv(pg,3);await pg.wait_for_timeout(1200)
    nw=await pg.evaluate("({over:__S().G.over,title:document.getElementById('endTitle').textContent,txt:document.getElementById('endText').textContent})")
    rep(nm['kings']==2 and nm['hero'] and nw['over'] and 'Rei rival caiu' in nw['txt'],"Partida normal: matar o Rei rival ganha",f"{nm}; {nw}")
    # partida normal: perder o teu Rei = derrota
    await pg.evaluate("(()=>{document.getElementById('sEnd').hidden=true;gameMode='normal';startGame(322,{map:'rios',vic:'total',civ:['mar','planicies']})})()");await pg.wait_for_timeout(300)
    await pg.evaluate("(()=>{kill(heroKing(0),null)})()");await adv(pg,3);await pg.wait_for_timeout(1200)
    nl=await pg.evaluate("({over:__S().G.over,title:document.getElementById('endTitle').textContent,txt:document.getElementById('endText').textContent,resp:__S().G.hero[0].resp})")
    rep(nl['over'] and 'teu Rei caiu' in nl['txt'] and nl['resp'] is None,"Guerra total: perder o Rei = derrota, sem renascer",str(nl))
    # gravação antiga de partida normal (sem Rei) recebe Reis ao carregar
    await pg.evaluate("(()=>{document.getElementById('sEnd').hidden=true;gameMode='normal';startGame(323,{map:'rios',vic:'classico',civ:['mar','planicies']});saveGame(true)})()")
    old=await pg.evaluate("(()=>{const K=SAVE_KEY;const s=JSON.parse(localStorage.getItem(K));delete s.X.hero;delete s.X.king;s.ents=s.ents.filter(e=>e.t!=='rei');localStorage.setItem(K,JSON.stringify(s));loadGame(K);return {kings:__S().ents.filter(e=>e.type==='rei').length,over:__S().G.over}})()")
    await adv(pg,2)
    rep(old['kings']==2 and not (await pg.evaluate("__S().G.over")),"Partida antiga ganha os Reis",str(old))
    # Regicídio: Reis heróis, sem renascer e perde
    await pg.evaluate("document.getElementById('bQuit').click()");await pg.wait_for_timeout(150)
    await pg.evaluate("(()=>{gameMode='normal';startGame(123,{map:'rios',vic:'regicidio',civ:['mar','planicies']})})()");await pg.wait_for_timeout(300)
    rg=await pg.evaluate("({kings:__S().ents.filter(e=>e.type==='rei').length,hero:!!__S().G.hero})")
    await pg.evaluate("(()=>{kill(heroKing(0),null)})()");await adv(pg,3);await pg.wait_for_timeout(1200)
    rg2=await pg.evaluate("({over:__S().G.over,title:document.getElementById('endTitle').textContent,resp:__S().G.hero[0].resp})")
    rep(rg['kings']==2 and rg['hero'] and rg2['over'] and rg2['resp'] is None,"Regicídio: Reis heróis, sem renascer",f"{rg}; depois de cair: {rg2}")
    rep(not errs,"Sem erros de JavaScript","; ".join(errs[:3]) or "nenhum")
    await b.close()
  print(f"\n{sum(1 for r in R if r[0])}/{len(R)} testes passaram");sys.exit(0 if all(r[0] for r in R) else 1)
asyncio.run(main())
