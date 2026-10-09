# Testes do modo online: servidor real + dois jogadores em navegadores separados
import asyncio,json,subprocess,os,time,sys
from urllib.request import urlopen
from playwright.async_api import async_playwright
PORT=8791;MOCK=8795;LAG=int(os.environ.get('LAG','0'))
import base64
def jwt(uid):
  b=lambda o:base64.urlsafe_b64encode(json.dumps(o).encode()).decode().rstrip('=')
  return b({'alg':'none'})+'.'+b({'sub':uid,'exp':int(time.time())+7200,'role':'authenticated'})+'.x'
def init(uid):
  sess={'access_token':jwt(uid or 'x'),'token_type':'bearer','expires_in':7200,'expires_at':int(time.time())+7200,'refresh_token':'r-'+str(uid),'user':{'id':uid,'aud':'authenticated','email':str(uid)+'@teste','app_metadata':{},'user_metadata':{}}}
  cfg={'supabaseUrl':f'http://127.0.0.1:{MOCK}','supabaseKey':'sb_publishable_teste'}
  rei={'u-ana':'Ana I','u-rui':'Rui II'}.get(uid)
  extra=f"localStorage.setItem('alv_rei_{uid}',JSON.stringify({{name:'{rei}',crown:1,cape:'#1f4fa8'}}));" if rei else ''
  return extra+f"window.ALV_CFG_OVERRIDE={json.dumps(cfg)};"+(f"localStorage.setItem('sb-127-auth-token',{json.dumps(json.dumps(sess))});" if uid else '')+f"if(!localStorage.getItem('alv_net'))localStorage.setItem('alv_net',JSON.stringify({{url:'ws://127.0.0.1:{PORT}/ws'}}));"
R=[]
def rep(ok,name,info):R.append((ok,name,info));print(('PASS' if ok else 'FAIL').ljust(10),name+':',info,flush=True)
URL=f"http://127.0.0.1:{PORT}/"
async def wait(pg,cond,ms=15000):
  t=time.time()
  while time.time()-t<ms/1000:
    if await pg.evaluate(cond):return True
    await asyncio.sleep(.2)
  return False
RANDOM_ORDERS=r"""(n)=>{const s=__S();const mine=s.ents.filter(e=>e.kind==='u'&&e.o===ME);const en=s.ents.filter(e=>e.o!==ME&&e.o!==2&&(e.kind==='u'||e.kind==='b'));
  for(let k=0;k<n;k++){const r=Math.random();const us=mine.filter(()=>Math.random()<.4);if(!us.length)continue;
    if(r<.35){const w={x:10+Math.random()*60,y:10+Math.random()*60};issueCmd(us,null,w)}
    else if(r<.6&&en.length){const t=en[Math.floor(Math.random()*en.length)];issueCmd(us,t,{x:t.x??t.tx,y:t.y??t.ty})}
    else if(r<.75){const tc=s.ents.find(e=>e.kind==='b'&&e.o===ME&&e.type==='centro');if(tc)act('train',{b:tc.id,t:'aldeao'})}
    else if(r<.85){act('stop',{u:ids(us)})}
    else if(r<.9){act('power',{p:Math.random()<.7?'grito':'bencao'})}
    else{const v=us.find(u=>u.type==='aldeao');if(v){const tx=Math.floor(v.x)+2,ty=Math.floor(v.y)+2;if(canPlace('casa',tx,ty,ME))act('place',{t:'casa',tx,ty,u:[v.id]})}}}
  return mine.length}"""
async def main():
  env=dict(os.environ,PORT=str(PORT),HOST='127.0.0.1',FAKE_LAG=str(LAG),SUPABASE_URL=f'http://127.0.0.1:{MOCK}',SUPABASE_KEY='sb_publishable_teste',ALV_SERVER_SECRET='s3cr3t',FORFEIT_MS='12000',MOCK_MIN_DUR='30',MOCK_PORT=str(MOCK))
  mock=subprocess.Popen(['node','mock_supabase.js'],env=env,stdout=subprocess.DEVNULL)
  srv=subprocess.Popen(['node','../server/server.js'],env=env,stdout=open('/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/srv.log','w'),stderr=subprocess.STDOUT)
  time.sleep(1)
  try:
   async with async_playwright() as p:
    b=await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    ctxA=await b.new_context(viewport={"width":900,"height":420});ctxB=await b.new_context(viewport={"width":900,"height":420})
    await ctxA.add_init_script(init('u-ana'));await ctxB.add_init_script(init('u-rui'))
    # -1 sem sessão: ecrã de login obrigatório
    ctxN=await b.new_context(viewport={"width":900,"height":420});await ctxN.add_init_script(init(None));N=await ctxN.new_page();await N.goto(URL);await N.wait_for_timeout(1200)
    st=await N.evaluate("()=>({login:!document.getElementById('sLogin').hidden,menu:!document.getElementById('sMenu').hidden,prev:!document.getElementById('lgPreview').hidden,btn:!document.getElementById('lgGoogle').disabled})")
    await N.screenshot(path='/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/acc_login.png');await ctxN.close()
    rep(st['login'] and not st['menu'] and not st['prev'] and st['btn'],'Login obrigatório',f"sem sessão: ecrã de login visível, menu escondido, botão Google ativo, sem atalho 'sem conta' no site oficial")
    A=await ctxA.new_page();B=await ctxB.new_page();errs=[]
    for pg,n in ((A,'A'),(B,'B')):pg.on("pageerror",lambda e,n=n:errs.append(n+': '+str(e)[:300]))
    await A.goto(URL);await B.goto(URL);await A.wait_for_timeout(1500)
    st=await asyncio.gather(*[pg.evaluate("()=>({menu:!document.getElementById('sMenu').hidden,chip:document.getElementById('accChip').textContent,authed:NET.authed})") for pg in (A,B)])
    rep(st[0]['menu'] and 'Ana' in st[0]['chip'] and 'Rui' in st[1]['chip'] and st[0]['authed'],'Sessão e perfil',f"com sessão entra direto no menu: {st[0]['chip']} | {st[1]['chip']}; servidor aceitou a conta={st[0]['authed']}")
    # 0 estado completo exato (sem rede)
    r=await A.evaluate("""()=>{startGame(77);AIs=[null,null];AI=null;const s=__S();const c0=s.G.starts[0],c1=s.G.starts[1];
      const us=[];for(let i=0;i<10;i++){us.push(__alv.mkUnit(0,['guerreiro','arqueiro','cavaleiro','lanceiro','catapulta'][i%5],c0.x+3+i%3,c0.y+3+(i/3|0)));us.push(__alv.mkUnit(1,['guerreiro','arqueiro','cavaleiro','sacerdote','ariete'][i%5],c1.x+3+i%3,c1.y+3+(i/3|0)))}
      for(const u of us)orderAttack(u,us.find(v=>v.o!==u.o));for(let i=0;i<450;i++)step(1/30);
      const S=JSON.parse(JSON.stringify(snapState()));for(let i=0;i<600;i++)step(1/30);const h1=stateHash(),n1=ents.length;
      applySnap(S,false);const h0=stateHash();for(let i=0;i<600;i++)step(1/30);const h2=stateHash();return{h1,h2,n1,kb:Math.round(JSON.stringify(S).length/1024)}}""")
    rep(r['h1']==r['h2'],'Estado completo exato',f"guardar → continuar 20 s → repor → continuar 20 s: hash {r['h1']} vs {r['h2']} ({r['n1']} entidades, {r['kb']} KB)")
    await A.reload();await A.wait_for_timeout(1500)
    # 1 criar e entrar na sala
    async def lobby(pg,name):
      await pg.click('#bOnline');await pg.wait_for_timeout(600)
    await lobby(A,'Fabis');await A.click('#olCreate')
    ok=await wait(A,"()=>!!NET.room&&!document.getElementById('olRoom').hidden")
    code=await A.evaluate("()=>NET.room")
    await lobby(B,'Amigo');await B.fill('#olJoin',code.lower());await B.click('#olJoinB')
    ok2=await wait(A,"()=>NET.peerOnline&&!document.getElementById('olStart').disabled")
    pn=await A.evaluate("()=>document.getElementById('olPlayers').textContent")
    rep(ok and ok2 and 'Rui' in pn,'Sala',f"código {code}; convidado entrou com o código em minúsculas; anfitrião vê: {pn.strip()[:60]}")
    await A.wait_for_timeout(2500) # medir ping
    await A.click('#olStart')
    ok=await wait(B,"()=>NET.game&&running")
    st=await asyncio.gather(A.evaluate("()=>({me:ME,seed:__S().G.seed,d:NET.delay,cam:centerOf(__S().ents.find(e=>e.kind==='b'&&e.o===ME))})"),B.evaluate("()=>({me:ME,seed:__S().G.seed,d:NET.delay})"))
    rep(ok and st[0]['me']==0 and st[1]['me']==1 and st[0]['seed']==st[1]['seed'],'Início',f"anfitrião joga com {st[0]['me']} (azul), amigo com {st[1]['me']} (vermelho); mesmo mapa (semente {st[0]['seed']}); atraso {st[0]['d']} turnos")
    kk=await asyncio.gather(*[pg.evaluate("()=>({kings:__S().ents.filter(e=>e.type==='rei').map(e=>e.o),hero:!!__S().G.hero,looks:__S().G.kingLook.map(l=>l.name)})") for pg in (A,B)])
    rep(sorted(kk[0]['kings'])==[0,1] and kk[0]['hero'] and kk[1]['hero'] and kk[0]['looks']==kk[1]['looks']==['Ana I','Rui II'],'Rei herói no online',f"Reis em jogo {kk[0]['kings']}; nomes vistos pela Ana {kk[0]['looks']} e pelo Rui {kk[1]['looks']}")
    # 2 jogar 60 s com ordens aleatórias dos dois lados
    t0=time.time();turns0=await A.evaluate("()=>NET.turn")
    for k in range(30):
      await asyncio.gather(A.evaluate(RANDOM_ORDERS,3),B.evaluate(RANDOM_ORDERS,3));await asyncio.sleep(2)
    hs=await asyncio.gather(*[pg.evaluate("()=>({t:NET.turn,my:[...NET.myHash],peer:[...NET.peerHash],d:NET.desync,rs:NET.resync,ents:__S().ents.length,tick:NET.stats.turns})") for pg in (A,B)])
    common=[t for t,h in hs[0]['my'] if t in dict(hs[1]['my'])];eq=all(dict(hs[0]['my'])[t]==dict(hs[1]['my'])[t] for t in common)
    rate=(hs[0]['t']-turns0)/(time.time()-t0)
    rep(eq and hs[0]['d']==0 and hs[1]['d']==0 and len(common)>=8,'Sincronização (60 s, ordens aleatórias)',f"{len(common)} verificações de estado iguais, dessincronizações 0/0; {hs[0]['ents']} entidades; ritmo {rate:.1f} turnos/s (alvo 10)")
    # 3 dessincronização forçada → anfitrião envia o estado → recupera
    await B.evaluate("()=>{__S().P[1].res.food+=7;__S().ents.find(e=>e.kind==='u'&&e.o===1).hp-=3}")
    ok=await wait(A,"()=>NET.resync>=1",15000)
    snapT=await A.evaluate("()=>NET.lastSnapT")
    ok2=await wait(A,f"()=>[...NET.myHash.keys()].some(t=>t>{snapT}&&NET.peerHash.has(t))",15000)
    hs=await asyncio.gather(*[pg.evaluate("()=>({my:[...NET.myHash],d:NET.desync,rs:NET.resync})") for pg in (A,B)])
    after=[t for t in dict(hs[0]['my']) if t>snapT and t in dict(hs[1]['my'])];same=bool(after) and all(dict(hs[0]['my'])[t]==dict(hs[1]['my'])[t] for t in after)
    rep(ok and same and hs[0]['rs']==1,'Recuperação de dessincronização',f"diferença detetada pelos dois; estado completo reenviado {hs[0]['rs']} vez (turno {snapT}); verificações seguintes iguais={same} ({len(after)})")
    # 3b batota: um cliente alterado diz "ganhei" a meio da partida; o outro continua ligado
    await A.evaluate("()=>netSend({type:'result',winner:0,reason:'normal',dur:999})");await asyncio.sleep(7)
    stt=json.loads(urlopen(f'http://127.0.0.1:{MOCK}/__state').read());still=await B.evaluate("()=>NET.game&&running")
    rep(len(stt['M'])==0 and still,'Resultado falso recusado',f"partidas registadas: {len(stt['M'])} (o outro jogador continua ligado e não confirmou); jogo continua={still}")
    # 4 conversa
    await B.evaluate("()=>chatSend('Olá do outro lado!')");await asyncio.sleep(1.5)
    got=await A.evaluate("()=>[...document.querySelectorAll('#toast .chat')].map(d=>d.textContent).join('|')")
    rep('Olá do outro lado!' in got,'Conversa',got)
    # 5 queda da ligação → volta sozinho
    await B.evaluate("()=>NET.ws.close()");w=await wait(A,"()=>!document.getElementById('netWait').hidden",6000)
    back=await wait(B,"()=>NET.ws&&NET.ws.readyState===1&&!NET.awaitSnap",20000)
    await asyncio.sleep(8)
    hs=await asyncio.gather(*[pg.evaluate("()=>({my:[...NET.myHash],t:NET.turn})") for pg in (A,B)])
    last=sorted(set(dict(hs[0]['my']))&set(dict(hs[1]['my'])))[-1];same=dict(hs[0]['my'])[last]==dict(hs[1]['my'])[last]
    rep(back and same and hs[0]['t']>0,'Queda de ligação',f"anfitrião mostrou 'à espera'={w}; amigo voltou sozinho={back}; continua sincronizado (turno {last})={same}")
    # 6 o amigo fecha a aplicação e volta a abrir → Voltar à partida
    await B.close();B=await ctxB.new_page();B.on("pageerror",lambda e:errs.append('B2: '+str(e.stack)[:600]))
    await asyncio.sleep(3);await B.goto(URL);await B.wait_for_timeout(400);await B.wait_for_timeout(1500);await B.click('#bOnline')
    vis=await B.evaluate("()=>!document.getElementById('olRejoin').hidden");await B.click('#olRejoin')
    ok=await wait(B,"()=>NET.game&&running&&!NET.awaitSnap",20000);await asyncio.sleep(8)
    hs=await asyncio.gather(*[pg.evaluate("()=>({my:[...NET.myHash],me:ME})") for pg in (A,B)])
    com=sorted(set(dict(hs[0]['my']))&set(dict(hs[1]['my'])));same=bool(com) and dict(hs[0]['my'])[com[-1]]==dict(hs[1]['my'])[com[-1]]
    rep(vis and ok and same and hs[1]['me']==1,'Fechar e reabrir a app',f"botão 'Voltar à partida' visível={vis}; retomou como jogador {hs[1]['me']}; sincronizado={same}")
    await B.screenshot(path='/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/online_guest.png');await A.screenshot(path='/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/online_host.png')
    # 7 desistir → vitória do outro → revanche
    await B.evaluate("()=>act('resign',{})");await asyncio.sleep(2)
    ta=await A.evaluate("()=>document.getElementById('endTitle').textContent+' — '+document.getElementById('endText').textContent")
    tb=await B.evaluate("()=>document.getElementById('endTitle').textContent+' — '+document.getElementById('endText').textContent")
    rep(ta.startswith('Vitória') and tb.startswith('Derrota'),'Desistir',f"anfitrião: {ta} | amigo: {tb}")
    await asyncio.sleep(1.5)
    ra=await A.evaluate("()=>document.getElementById('endRate').textContent");rb=await B.evaluate("()=>document.getElementById('endRate').textContent")
    rep('+16' in ra and '-16' in rb,'Pontuação Elo',f"anfitrião: {ra} | amigo: {rb}")
    await A.click('#bAgain');await B.click('#bAgain');await asyncio.sleep(.5);await A.click('#olStart')
    ok=await wait(B,"()=>NET.game&&running&&NET.turn>20",15000)
    rep(ok,'Revanche','nova partida na mesma sala sem voltar a escrever o código')
    # 8 adversário não volta → vitória por desistência
    await B.evaluate("()=>{NET.closing=true;NET.ws.close()}");await asyncio.sleep(1.5)
    await A.evaluate("()=>{NET.lostT=Date.now()-91000}");await asyncio.sleep(1)
    ta=await A.evaluate("()=>document.getElementById('endText').textContent")
    rep('desistência' in ta,'Adversário não volta',ta)
    await asyncio.sleep(16)
    stt=json.loads(urlopen(f'http://127.0.0.1:{MOCK}/__state').read())
    reasons=[m['reason'] for m in stt['M']]
    rep(len(stt['M'])==2 and reasons==['resign','abandono'],'Registo das partidas',f"partidas registadas no Supabase: {reasons}; pontos: "+', '.join(f"{p['username']} {p['rating']} ({p['wins']}V/{p['losses']}D)" for p in stt['P']))
    await A.click('#bEndMenu');await A.wait_for_timeout(400);await A.click('#accChip');await A.wait_for_timeout(1200)
    hist=await A.evaluate("()=>document.getElementById('pfHist').innerText.split(String.fromCharCode(10)).join(' ')")
    await A.screenshot(path='/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/acc_profile.png')
    rep('Vitória' in hist and 'Rui' in hist,'Perfil e histórico',hist[:120])
    await A.click('#pfBack');await A.click('#bRank');await A.wait_for_timeout(1000)
    rk=await A.evaluate("()=>[...document.querySelectorAll('#rkList .krow')].map(r=>r.innerText.split(String.fromCharCode(10)).join(' '))")
    await A.screenshot(path='/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/acc_rank.png')
    rep(len(rk)==2 and 'Ana' in rk[0],'Classificação',' | '.join(rk))
    # amigos: pedido, aceitar, ver ligado, convidar e jogar
    await A.click('#rkBack');await A.click('#bFriends');await A.wait_for_timeout(500);await A.fill('#frCode','bbbbbb');await A.click('#frAdd');await A.wait_for_timeout(800)
    B=await ctxB.new_page();await B.goto(URL);await B.wait_for_timeout(1500);await B.click('#bFriends');await B.wait_for_timeout(800)
    inc=await B.evaluate("()=>document.getElementById('frList').innerText");await B.click('[data-ok]');await B.wait_for_timeout(800)
    await A.click('#frBack');await A.click('#bFriends');await A.wait_for_timeout(1800)
    fl=await A.evaluate("()=>document.getElementById('frList').innerText.split(String.fromCharCode(10)).join(' ')")
    await A.screenshot(path='/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/acc_friends.png')
    rep('Ana' in inc and 'Rui' in fl and 'ligado' in fl,'Amigos',f"Rui recebeu o pedido e aceitou; a Ana vê: {fl[:80]}")
    await A.click('[data-inv]');ok=await wait(B,"()=>!document.getElementById('invite').hidden",8000)
    await B.screenshot(path='/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/acc_invite.png')
    await B.click('#ivYes');ok2=await wait(A,"()=>NET.peerOnline&&!document.getElementById('olStart').disabled",8000);await A.click('#olStart')
    ok3=await wait(B,"()=>NET.game&&running&&NET.turn>10",10000)
    rep(ok and ok2 and ok3,'Convidar um amigo',f"convite chegou={ok}; amigo entrou na sala={ok2}; partida começou={ok3}")
    # salas públicas
    ctxE=await b.new_context(viewport={"width":900,"height":420});await ctxE.add_init_script(init('u-eva'));E=await ctxE.new_page();await E.goto(URL);await E.wait_for_timeout(1500)
    await E.click('#bOnline');await E.wait_for_timeout(500);await E.check('#olPublic');await E.click('#olCreate');await E.wait_for_timeout(600)
    ctxF=await b.new_context(viewport={"width":900,"height":420});await ctxF.add_init_script(init('u-ana'));F=await ctxF.new_page()
    # (a mesma conta noutro aparelho vê a lista de salas)
    await F.goto(URL);await F.wait_for_timeout(1500);await F.click('#bOnline');await F.wait_for_timeout(1000)
    rl=await F.evaluate("()=>document.getElementById('olRooms').innerText.split(String.fromCharCode(10)).join(' ')")
    await F.screenshot(path='/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/acc_rooms.png')
    rep('Eva' in rl and '1200' in rl,'Salas públicas',rl[:80])
    # Eva não é amiga da Ana: não vê se está ligada nem a pode convidar
    pres=await E.evaluate("async()=>{NET.presence=null;netSend({type:'presence',ids:['u-ana','u-rui']});await new Promise(r=>setTimeout(r,800));return NET.presence}")
    errE=await E.evaluate("async()=>{const t=[];const o=toast;toast=(m,b)=>{t.push(m);o(m,b)};netSend({type:'invite',to:'u-ana',room:NET.room});await new Promise(r=>setTimeout(r,800));toast=o;return t.join('|')}")
    gotInv=await F.evaluate("()=>!document.getElementById('invite').hidden")
    rep(pres=={} and 'amigos' in errE and not gotInv,'Só amigos',f"estado dos não-amigos devolvido: {pres}; convite recusado: {errE}")
    # jogo contra o computador conta no perfil
    await F.click('#olBack');await F.click("#bPlay");await F.click("#bSetupGo");await F.wait_for_timeout(500);await F.evaluate("()=>endGame(true)");await F.wait_for_timeout(800)
    stt=json.loads(urlopen(f'http://127.0.0.1:{MOCK}/__state').read());ana=[p for p in stt['P'] if p['id']=='u-ana'][0]
    rep(ana['sp_wins']==1,'Vitória contra o computador',f"sp_wins={ana['sp_wins']}")
    # apagar a conta (exigido pela Play Store): dois toques em Apagar → volta ao login e o perfil desaparece
    await E.evaluate("()=>{netLeaveGame&&netLeaveGame();document.getElementById('sOnline').hidden=true;profileOpen()}");await E.wait_for_timeout(800)
    await E.click('#pfDelete');t1=await E.evaluate("()=>document.getElementById('pfDelete').textContent");await E.click('#pfDelete')
    okDel=await wait(E,"()=>!document.getElementById('sLogin').hidden",6000)
    stt=json.loads(urlopen(f'http://127.0.0.1:{MOCK}/__state').read());gone=not any(p['id']=='u-eva' for p in stt['P'])
    rep(okDel and gone and 'outra vez' in t1,'Apagar conta',f"1.º toque pede confirmação ({t1}); depois volta ao login={okDel}; perfil apagado no servidor={gone}")
    rep(not errs,'Erros JavaScript',str(errs[:3]) if errs else 'nenhum')
    await b.close()
  finally:
    srv.terminate();mock.terminate()
  print(f"\n{sum(1 for x in R if x[0])}/{len(R)} PASS")
asyncio.run(main())
