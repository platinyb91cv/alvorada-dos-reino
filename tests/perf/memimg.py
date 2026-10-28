# Memória das imagens vivas (descodificadas) e das telas numa partida com o bot, em vários momentos. Uso: memimg.py <porta> <saida.json>
import asyncio, json, sys
from playwright.async_api import async_playwright
PORT=sys.argv[1]; OUT=sys.argv[2]
INIT=r"""(()=>{const live=[],cvs=[];const OI=window.Image;window.Image=function(...a){const im=new OI(...a);live.push(new WeakRef(im));return im};window.Image.prototype=OI.prototype;
 const oc=document.createElement.bind(document);document.createElement=function(t,...a){const e=oc(t,...a);if(String(t).toLowerCase()==='canvas')cvs.push(new WeakRef(e));if(String(t).toLowerCase()==='img')live.push(new WeakRef(e));return e};
 window.__mem=()=>{let im=0,n=0,cv=0;for(const r of live){const i=r.deref();if(i&&i.complete&&i.naturalWidth){im+=i.naturalWidth*i.naturalHeight*4;n++}}for(const r of cvs){const c=r.deref();if(c)cv+=c.width*c.height*4}return{imagens_mb:Math.round(im/1048576),imagens_n:n,telas_mb:Math.round(cv/1048576)}}})();"""
async def main():
  async with async_playwright() as p:
    br=await p.chromium.launch(args=['--js-flags=--expose-gc']); ctx=await br.new_context(viewport={'width':915,'height':412},device_scale_factor=2.6,is_mobile=True,has_touch=True)
    await ctx.add_init_script(INIT); pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)[:200]))
    await pg.goto(f'http://localhost:{PORT}/index.html?bot=teste'); await pg.wait_for_timeout(6000)
    await pg.evaluate("startGame(4242,{map:'continental',vic:'total',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
    await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
    await pg.evaluate("()=>{botSet(true);speed=8}"); rows=[]
    for tgt in [60,300,600,900,1200]:
      while True:
        t=await pg.evaluate("G.over?-1:G.time")
        if t<0 or t>=tgt: break
        await pg.wait_for_timeout(3000)
      await pg.evaluate("()=>{try{gc()}catch(e){}}"); await pg.wait_for_timeout(1500); await pg.evaluate("()=>{try{gc()}catch(e){}}")
      r=await pg.evaluate("()=>({t:G.time|0,idades:[P[0].age,P[1].age],unidades:ents.filter(e=>e.kind==='u').length,...__mem()})"); rows.append(r); print(json.dumps(r),flush=True)
      if t<0: break
    json.dump({'rows':rows,'erros':errs},open(OUT,'w'),indent=1); await br.close()
asyncio.run(main())
