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
  return f"window.ALV_CFG_OVERRIDE={json.dumps(cfg)};"+(f"localStorage.setItem('sb-127-auth-token',{json.dumps(json.dumps(sess))});" if uid else '')+f"if(!localStorage.getItem('alv_net'))localStorage.setItem('alv_net',JSON.stringify({{url:'ws://127.0.0.1:{PORT}/ws'}}));"
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
    for pg,n in ((A,'A'),(B,'B')):pg.on("pageerror",lambda e,n=n:errs.append(n+': '+str(e.stack)[:500]))
    await A.goto(URL);await B.goto(URL);await A.wait_for_timeout(1500)
    async def room(H,J):
      await H.click('#bOnline');await H.wait_for_timeout(600);await H.click('#olCreate')
      await wait(H,"()=>!!NET.room&&!document.getElementById('olRoom').hidden");code=await H.evaluate("()=>NET.room")
      await J.click('#bOnline');await J.wait_for_timeout(600);await J.fill('#olJoin',code);await J.click('#olJoinB')
      return await wait(H,"()=>NET.peerOnline&&!document.getElementById('olStart').disabled")
    ok=await room(A,B);await A.wait_for_timeout(1500)
    # opções: anfitrião escolhe ilhas + guerra total; convidado escolhe Montanha
    await A.click('#olOpts .seg[data-k=map] button[data-v=arquipelago]');await A.click('#olOpts .seg[data-k=vic] button[data-v=total]');await B.click('#olOpts .seg[data-k=civ] button[data-v=montanha]');await A.click('#olOpts .seg[data-k=civ] button[data-v=mar]')
    await A.wait_for_timeout(800);txtB=await B.evaluate("()=>document.getElementById('olOptTxt').textContent")
    await A.click('#olStart');await wait(B,"()=>NET.game&&running")
    st=await asyncio.gather(*[pg.evaluate("()=>({map:G.map,vic:G.vic,civ:G.civ,me:ME})") for pg in (A,B)])
    rep(ok and st[0]==dict(st[1],me=0) and st[0]['map']=='arquipelago' and st[0]['vic']=='total' and st[0]['civ']==['mar','montanha'],'Opções da sala',f"convidado vê: {txtB} | jogo: {st[0]} / {st[1]}")
    await asyncio.sleep(8)
    before=await asyncio.gather(*[pg.evaluate("()=>({t:Math.round(G.time),mine:__S().ents.filter(e=>e.o===ME).length,res:Math.round(P[ME].res.food)})") for pg in (A,B)])
    await B.click('#btnMenu');await B.wait_for_timeout(300);await B.click('#bNetSave');await B.click('#bNetSave')
    left=await wait(A,"()=>!running&&!NET.game&&!document.getElementById('sMenu').hidden",15000)
    left2=await wait(B,"()=>!running&&!NET.game",8000)
    sv=await asyncio.gather(*[pg.evaluate("()=>netSavesList().map(x=>({me:x.me,peer:x.peer.name,time:x.time,kb:Math.round(x.data.length/1024)}))") for pg in (A,B)])
    rep(left and left2 and len(sv[0])==1 and len(sv[1])==1,'Gravar e sair (online)',f"os dois saíram={left and left2}; gravado em A: {sv[0]} | B: {sv[1]}")
    # retomar: desta vez o Rui (antigo convidado) é o anfitrião
    ok=await room(B,A);await B.wait_for_timeout(800)
    vis=await B.evaluate("()=>!document.getElementById('olSaves').hidden&&document.getElementById('olSaves').textContent")
    await B.click('#olSaves button');resumed=await wait(A,"()=>NET.game&&running",15000);await A.wait_for_timeout(1500)
    after=await asyncio.gather(A.evaluate("()=>({t:Math.round(G.time),mine:__S().ents.filter(e=>e.o===ME).length,res:Math.round(P[ME].res.food),me:ME,civ:G.civ[ME]})"),B.evaluate("()=>({t:Math.round(G.time),mine:__S().ents.filter(e=>e.o===ME).length,res:Math.round(P[ME].res.food),me:ME,civ:G.civ[ME]})"))
    good=resumed and abs(after[0]['t']-before[0]['t'])<6 and after[0]['civ']=='mar' and after[1]['civ']=='montanha' and after[0]['me']==1 and after[1]['me']==0
    rep(good,'Continuar partida guardada',f"botão: {vis}; antes A {before[0]} B {before[1]} | depois A {after[0]} B {after[1]}")
    await asyncio.sleep(6)
    hs=await asyncio.gather(*[pg.evaluate("()=>({my:[...NET.myHash],d:NET.desync,t:G.time,over:G.over})") for pg in (A,B)])
    rep(all(h['t']-after[0]['t']>=4 and not h['over'] for h in hs),'Partida retomada continua a andar',f"tempo depois de 6 s: A {round(hs[0]['t'],1)} B {round(hs[1]['t'],1)} (retomada em {after[0]['t']}); terminada: {hs[0]['over']}/{hs[1]['over']}")
    common=[t for t,h in hs[0]['my'] if t in dict(hs[1]['my'])];eq=bool(common) and all(dict(hs[0]['my'])[t]==dict(hs[1]['my'])[t] for t in common)
    rep(eq,'Sincronização após retomar',f"{len(common)} verificações iguais; dessincronizações {hs[0]['d']}/{hs[1]['d']}")
    rep(not errs,'Erros JavaScript',errs[:3] or 'nenhum')
    await b.close()
  finally:
    mock.kill();srv.kill()
  print(f"\n{sum(1 for r in R if r[0])}/{len(R)} PASS")
asyncio.run(main())
