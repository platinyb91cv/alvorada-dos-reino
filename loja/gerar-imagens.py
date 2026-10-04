# Gera ícone, ícones adaptativos, ecrãs de arranque e imagens da Play Store a partir do brasão
import asyncio,os
from playwright.async_api import async_playwright
from PIL import Image
ROOT='/home/claude/alvorada'
CREST='''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="cgS" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff2cf"/><stop offset="1" stop-color="#f5a04e"/></linearGradient><linearGradient id="cgB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a2c6e"/><stop offset="1" stop-color="#1a1840"/></linearGradient></defs><path d="M32 3l25 8v19c0 15-10.5 25-25 31C17.5 55 7 45 7 30V11z" fill="url(#cgB)" stroke="#ffcf7d" stroke-width="2.5"/><g stroke="#ffcf7d" stroke-width="2.2" stroke-linecap="round"><path d="M32 15v6M18.5 21l4 4.2M45.5 21l-4 4.2M13 33h5M46 33h5"/></g><path d="M20 35a12 12 0 0 1 24 0z" fill="url(#cgS)"/><path d="M13 39c4-2.6 7-2.6 10 0s7 2.6 10 0 7-2.6 10 0 5 2 8 0" fill="none" stroke="#7fd3e8" stroke-width="2.4" stroke-linecap="round"/><path d="M17 45.5c3.5-2 6-2 9 0s6 2 9 0 6-2 9 0" fill="none" stroke="#5aa9c9" stroke-width="2" stroke-linecap="round" opacity=".8"/></svg>'''
import base64
def _f(n):return 'data:font/woff2;base64,'+base64.b64encode(open(f'{ROOT}/www/fonts/{n}','rb').read()).decode()
FONTS=f'''@font-face{{font-family:Cinzel;font-weight:800;src:url({_f('cinzel-latin-800-normal.woff2')})}}@font-face{{font-family:Cinzel;font-weight:600;src:url({_f('cinzel-latin-600-normal.woff2')})}}@font-face{{font-family:Alegreya;font-weight:700;src:url({_f('alegreya-sans-latin-700-normal.woff2')})}}'''
SKY='radial-gradient(ellipse at 50% 92%,#ffd286 0%,#f4874c 22%,#b14a6c 46%,#3a2a66 72%,#14143a 100%)'
def page(w,h,body,extra=''):
  return f'<html><head><style>{FONTS}html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:transparent}}{extra}</style></head><body>{body}</body></html>'
JOBS=[]
def icon(size,full=True,crest=.62,rounded=False):
  bg=f'background:{SKY};' if full else ''
  r='border-radius:22%;' if rounded else ''
  return page(size,size,f'<div style="width:{size}px;height:{size}px;{bg}{r}display:flex;align-items:center;justify-content:center;overflow:hidden"><div style="width:{size*crest}px;height:{size*crest}px;filter:drop-shadow(0 {size*.02}px {size*.04}px rgba(20,8,40,.55))">{CREST}</div></div>')
def splash(w,h):
  m=min(w,h);port=h>w
  return page(w,h,f'''<div style="width:{w}px;height:{h}px;background:{SKY};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:{m*.03}px">
   <div style="width:{m*.26}px;height:{m*.26}px;filter:drop-shadow(0 {m*.012}px {m*.03}px rgba(20,8,40,.6))">{CREST}</div>
   <div style="font:800 {m*(.1 if port else .095)}px Cinzel;line-height:.95;background:linear-gradient(180deg,#fff6e0,#ffd286 55%,#f4874c);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 {m*.006}px 0 rgba(48,20,52,.6))">Alvorada</div>
   <div style="font:600 {m*.038}px Cinzel;letter-spacing:.3em;color:#ffe2b6;margin-left:.3em">DOS REINOS</div></div>''')
def feature(w=1024,h=500):
  BATTLE='data:image/png;base64,'+base64.b64encode(open(f'{ROOT}/loja/_battle.png','rb').read()).decode()
  return page(w,h,f'''<div style="width:{w}px;height:{h}px;background:radial-gradient(ellipse at 70% 110%,#ffd286 0%,#f4874c 20%,#b14a6c 45%,#3a2a66 72%,#14143a 100%);position:relative;overflow:hidden">
   <img src="{BATTLE}" style="position:absolute;right:-24px;bottom:-26px;width:520px;border-radius:18px;opacity:.95;box-shadow:0 20px 60px rgba(0,0,0,.5);transform:rotate(-2deg)">
   <div style="position:absolute;left:56px;top:110px;display:flex;flex-direction:column;gap:8px">
    <div style="width:92px;height:92px">{CREST}</div>
    <div style="font:800 64px Cinzel;line-height:.95;background:linear-gradient(180deg,#fff6e0,#ffd286 55%,#f4874c);-webkit-background-clip:text;color:transparent">Alvorada</div>
    <div style="font:600 26px Cinzel;letter-spacing:.3em;color:#ffe2b6">DOS REINOS</div>
    <div style="font:700 21px Alegreya;color:#fbe9d6;margin-top:10px">Estratégia em tempo real · online com amigos</div></div></div>''')
async def shot(b,html,w,h,out,transparent=True):
  pg=await b.new_page(viewport={'width':w,'height':h});await pg.set_content(html);await pg.evaluate('document.fonts.ready');await pg.wait_for_timeout(300)
  await pg.screenshot(path=out,omit_background=transparent);await pg.close()
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    res=f'{ROOT}/android/app/src/main/res'
    await shot(b,icon(1024),1024,1024,f'{ROOT}/www/icon.png',False)
    await shot(b,icon(512),512,512,f'{ROOT}/loja/icone-512.png',False)
    for d,lg,fg in [('mdpi',48,108),('hdpi',72,162),('xhdpi',96,216),('xxhdpi',144,324),('xxxhdpi',192,432)]:
      await shot(b,icon(lg,crest=.66,rounded=True),lg,lg,f'{res}/mipmap-{d}/ic_launcher.png')
      await shot(b,icon(lg,crest=.66,rounded=True).replace('border-radius:22%','border-radius:50%'),lg,lg,f'{res}/mipmap-{d}/ic_launcher_round.png')
      await shot(b,icon(fg,crest=.42),fg,fg,f'{res}/mipmap-{d}/ic_launcher_foreground.png',False)
    for d in os.listdir(res):
      f=f'{res}/{d}/splash.png'
      if os.path.exists(f):
        w,h=Image.open(f).size;await shot(b,splash(w,h),w,h,f,False)
    await shot(b,feature(),1024,500,f'{ROOT}/loja/grafico-destaque-1024x500.png',False)
    await b.close()
asyncio.run(main())
