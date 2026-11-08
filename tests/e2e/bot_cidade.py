# Bot melhorado: cidade em quarteirões (casas alinhadas 2x2, ruas com estrada), muralha sobre as ruas exteriores,
# guerra com reunião/ataque/retirada, missões (campanha "Comércio" e Meu Reino "Fundação") e câmara que respeita o jogador.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
STATS = """()=>{const A=AIs[ME],g=A&&A.grid;const c=k=>ents.filter(e=>e.o===ME&&e.type===k).length;
  const casas=ents.filter(e=>e.o===ME&&e.type==='casa');let alinhadas=0;
  if(g)for(const h of casas){const ox=((h.tx-g.ox-1)%5+5)%5,oy=((h.ty-g.oy-1)%5+5)%5;if((ox===0||ox===2)&&(oy===0||oy===2))alinhadas++}
  let naRua=0;if(g)for(const e of ents)if(e.o===ME&&e.kind==='b'&&!e.d.wall&&!e.d.gate&&e.type!=='torre'&&e.type!=='centro'&&Math.abs(e.tx-g.ox)<=20&&Math.abs(e.ty-g.oy)<=20)for(let y=e.ty;y<e.ty+e.h;y++)for(let x=e.tx;x<e.tx+e.w;x++)if(botStreet(g,x,y))naRua++;
  return{tempo:Math.round(G.time),aldeoes:c('aldeao'),casas:casas.length,casas_alinhadas:alinhadas,edificios_em_rua:naRua,
   estradas:Object.values(G.roads||{}).filter(v=>v===ME+1).length,muralha:c('muralhaPedra')+c('muralhaMadeira'),portoes:c('portaoPedra')+c('portaoMadeira'),torres:c('torre'),
   exercito:ents.filter(e=>e.o===ME&&e.kind==='u'&&e.d.mil&&!e.d.king).length,idade:P[ME].age,guerra:A&&A.ws,pop:P[ME].pop+'/'+P[ME].popCap,
   rival_cv:ents.some(e=>e.o===1&&e.type==='centro'),partida:running?'a decorrer':(G.won?'vitória':'derrota')}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); R = {}; errs = []
        pg = await br.new_page(viewport={'width': 1280, 'height': 760}); pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        await pg.evaluate("startGame(4242,{map:'continental',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{botSet(true)}")
        # câmara: o jogador arrasta; o bot não a puxa de volta durante 15 s
        R['camara'] = await pg.evaluate("""()=>{for(let i=0;i<20;i++)step(1/20);botDirector(1/20);cam.x+=400;const x0=cam.x;BOT.next=0;
            for(let i=0;i<60;i++)botDirector(1/20);const fica=Math.abs(cam.x-x0)<1;BOT.userT=performance.now()-16000;for(let i=0;i<80;i++)botDirector(1/20);const volta=Math.abs(cam.x-x0)>50;
            BOT.free=true;const x1=cam.x;BOT.next=0;for(let i=0;i<60;i++)botDirector(1/20);const livre=Math.abs(cam.x-x1)<1;BOT.free=false;
            return{arrastar_fica:fica,depois_de_15s_volta:volta,modo_livre_fica:livre,botao:getComputedStyle($('bBotCam')).display}}""")
        for t in (8, 16, 24):
            await pg.evaluate("()=>{for(let i=0;i<480*20;i++){step(1/20);if(!running)break}}")
            R[f'bot_{t}min'] = await pg.evaluate(STATS)
            await pg.evaluate("()=>{const tc=ents.find(e=>e.o===ME&&e.type==='centro');if(tc){BOT.free=true;cam.z=.62;centerCam(tc.tx+1,tc.ty+1);BOT.lc=null}}")
            await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{OUT}/bot_cidade_{t}min.png')
            await pg.evaluate("()=>{BOT.free=false}")
            if R[f'bot_{t}min']['partida'] != 'a decorrer': break
        # missão da campanha: Rota do Comércio (2 mercados, carroças, ouro)
        idx = await pg.evaluate("()=>CAMP.findIndex(m=>m.objs.some(o=>String(o[0]).includes('Mercados')))")
        await pg.evaluate(f"()=>{{campStart({idx});botSet(true)}}")
        await pg.evaluate("()=>{for(let i=0;i<1200*20;i++){step(1/20);if(!running)break}}")
        R['campanha_comercio'] = await pg.evaluate("()=>({missao:CAMP[G.camp]?CAMP[G.camp].t:null,objetivos:running?campObjs().map(o=>(o.ok?'✔ ':'· ')+o.d):'acabou: '+(G.won?'vitória':'derrota'),pedido:AIs[ME]&&AIs[ME].need&&{b:AIs[ME].need.b,u:AIs[ME].need.u,res:AIs[ME].need.res},mercados:cntB(ME,'mercado',false),carrocas:cntU(ME,'carroca'),ouro:Math.round(P[ME].res.gold)})")
        R['erros'] = errs; print(json.dumps(R, ensure_ascii=False, indent=1)); await br.close()
asyncio.run(main())
