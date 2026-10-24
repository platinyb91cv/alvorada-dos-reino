# HUD leve: esconder/mostrar a interface (olho), recolher o minimapa (fica guardado), ilha do menu com a arte 3D; sem erros de página.
import asyncio, sys, json
from playwright.async_api import async_playwright
OUT=sys.argv[1]
async def main():
  async with async_playwright() as p:
    br=await p.chromium.launch();R={}
    pg=await br.new_page(viewport={'width':800,'height':360},device_scale_factor=2,is_mobile=True,has_touch=True);errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)[:200]));pg.on('console',lambda m:errs.append(m.text[:200]) if m.type=='error' else None)
    await pg.goto('http://localhost:8777/index.html');await pg.wait_for_timeout(5000)
    await pg.screenshot(path=f'{OUT}/menu.png')
    await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})");await pg.wait_for_timeout(2500)
    await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
    await pg.evaluate("()=>{sel.length=0}");await pg.wait_for_timeout(600)
    await pg.screenshot(path=f'{OUT}/ocioso.png')
    await pg.tap('#bHud');await pg.wait_for_timeout(500);await pg.screenshot(path=f'{OUT}/hudoff.png')
    R['hudoff']=await pg.evaluate("()=>({cls:document.body.classList.contains('hudoff'),top:getComputedStyle($('top')).display,bHud:getComputedStyle($('bHud')).display})")
    await pg.tap('#bHud');await pg.wait_for_timeout(300)
    R['hudon']=await pg.evaluate("()=>getComputedStyle($('bottom')).display")
    await pg.tap('#bMini');await pg.wait_for_timeout(400);await pg.screenshot(path=f'{OUT}/minioff.png')
    R['mini']=await pg.evaluate("()=>({off:document.body.classList.contains('mmoff'),mini:getComputedStyle($('mini')).display,guardado:localStorage.getItem('alv_mmoff')})")
    await pg.tap('#bMini');await pg.wait_for_timeout(300)
    R['mini2']=await pg.evaluate("()=>getComputedStyle($('mini')).display")
    R['errs']=errs;print(json.dumps(R));await br.close()
asyncio.run(main())
