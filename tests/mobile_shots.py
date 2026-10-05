# Capturas em vários telemóveis + medições de problemas de layout
import asyncio,json,sys
from playwright.async_api import async_playwright
OUT="/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/mob/"
DEV=[("pequeno",640,360,2),("se",667,375,2),("medio",740,360,3),("iphone",844,390,3),("pixel",915,412,2.6),("retrato",390,844,3)]
if len(sys.argv)>1:DEV=[d for d in DEV if d[0] in sys.argv[1].split(',')]
AUDIT=r"""()=>{const out=[];const vw=innerWidth,vh=innerHeight;
 const vis=el=>{const r=el.getBoundingClientRect();const st=getComputedStyle(el);return r.width>0&&r.height>0&&st.visibility!=='hidden'&&st.display!=='none'&&!el.closest('[hidden]')};
 for(const el of document.querySelectorAll('button,.cmd,input,.res,#mini')){if(!vis(el))continue;const r=el.getBoundingClientRect();
   const id=el.id||el.className||el.tagName;
   if(r.right>vw+1||r.bottom>vh+1||r.left<-1||r.top<-1)out.push('fora do ecrã: '+id+' '+[r.left,r.top,r.right,r.bottom].map(Math.round));
   if(el.matches('button,.cmd')&&(r.width<38||r.height<36))out.push('alvo pequeno: '+id+' '+Math.round(r.width)+'x'+Math.round(r.height));
   if(el.scrollWidth>el.clientWidth+2&&el.matches('.res,.cmd'))out.push('texto cortado: '+id)}
 const sc=document.querySelector('.screen:not([hidden]) .card,.screen:not([hidden]) .panel');if(sc&&sc.scrollHeight>sc.clientHeight+2)out.push('cartão com scroll: '+(sc.parentElement.id)+' '+sc.scrollHeight+'>'+sc.clientHeight);
 const b=document.getElementById('bottom'),t=document.getElementById('top');if(b&&t&&!b.closest('[hidden]')){out.push('mapa visível: '+Math.round(b.getBoundingClientRect().top-t.getBoundingClientRect().bottom)+'px de '+vh+'px ('+Math.round((b.getBoundingClientRect().top-t.getBoundingClientRect().bottom)/vh*100)+'%)')}
 return out}"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for name,w,h,dpr in DEV:
      ctx=await b.new_context(viewport={"width":w,"height":h},device_scale_factor=dpr,is_mobile=True,has_touch=True)
      pg=await ctx.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
      await pg.goto("file:///home/claude/alvorada/www/index.html");await pg.wait_for_timeout(900)
      rep={}
      async def shot(tag):
        await pg.wait_for_timeout(350);await pg.screenshot(path=f"{OUT}{name}_{tag}.png");rep[tag]=await pg.evaluate(AUDIT)
      await shot("login")
      await pg.click("#lgPreview");await shot("menu")
      await pg.click("#bPlay"); await pg.click("#bSetupGo");await pg.wait_for_timeout(600)
      await pg.evaluate("()=>{const s=__S();for(let i=0;i<30*20;i++)step(1/30);setSel([]);uiDirty=true}");await shot("jogo")
      await pg.evaluate("()=>{const s=__S();const tc=s.ents.find(e=>e.kind==='b'&&e.o===0);setSel([tc]);uiDirty=true}");await shot("centro")
      await pg.evaluate("()=>{const s=__S();const v=s.ents.find(e=>e.kind==='u'&&e.o===0&&e.type==='aldeao');setSel([v]);menuMode='build';uiDirty=true}");await shot("construir")
      await pg.evaluate("()=>{const s=__S();const c=s.G.starts[0];const us=['guerreiro','arqueiro','cavaleiro','lanceiro','catapulta'].flatMap((t,i)=>[__alv.mkUnit(0,t,c.x+3+i*.6,c.y+4),__alv.mkUnit(0,t,c.x+3+i*.6,c.y+4.6)]);setSel(us);uiDirty=true}");await shot("exercito")
      await pg.evaluate("()=>{netQueue=()=>{};NET.on=true;NET.peer='Rui';NET.peerOnline=true;NET.rtt=80;netModeUI()}");await shot("online")
      await pg.evaluate("()=>{NET.on=false;netModeUI()}")
      await pg.evaluate("()=>togglePause()");await shot("pausa");await pg.evaluate("()=>togglePause()")
      await pg.evaluate("()=>{endGame(true)}");await shot("fim")
      print(name,w,h,'erros',errs);
      for k,v in rep.items():print('  ',k,v)
      await ctx.close()
    await b.close()
asyncio.run(main())
