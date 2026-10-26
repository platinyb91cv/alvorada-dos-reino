# Conjunto modular: torre redonda com muros nas 4 direções (e nas 2 filas de cada lado), anel de muros (4 cantos), cruz e T,
# muro sozinho, portão de madeira; com e sem a depuração (?iso=1). Imagens aproximadas para comparar; sem erros de página.
# Uso: python3 castelo_modular.py <pasta> [teste]   ("teste" = só peças da montagem de teste, sem T nem muro sozinho)
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'; SO_TESTE = len(sys.argv) > 2
CENA = """(teste)=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=2;for(let i=0;i<vis.length;i++)vis[i]=2;
  const ok=(x,y,w,h)=>{for(let j=-1;j<=h;j++)for(let i=-1;i<=w;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
  const used=[];const spot=(w,h)=>{for(let r=6;r<95;r++)for(let a=0;a<72;a++){const x=Math.round(q0.x+Math.cos(a/72*6.283)*r),y=Math.round(q0.y+Math.sin(a/72*6.283)*r);if(ok(x,y,w,h)&&!used.some(u=>Math.abs(x-u.x)<16&&Math.abs(y-u.y)<16)){used.push({x,y});return{x,y}}}return null};
  const W=(t,x,y)=>mkBld(ME,t,x,y,true);
  const q=spot(10,10);const t=W('torre',q.x+4,q.y+4);t.lvl=3;
  for(let i=1;i<=3;i++){W('muralhaPedra',q.x+4-i,q.y+4);W('muralhaPedra',q.x+5+i,q.y+5);W('muralhaPedra',q.x+5,q.y+4-i);W('muralhaPedra',q.x+4,q.y+5+i)}
  const r=spot(8,7);for(let i=0;i<7;i++){W('muralhaPedra',r.x+i,r.y);W('muralhaPedra',r.x+i,r.y+5)}for(let j=1;j<5;j++){W('muralhaPedra',r.x,r.y+j);W('muralhaPedra',r.x+6,r.y+j)}
  for(let j=1;j<5;j++)W('muralhaPedra',r.x+3,r.y+j);for(let i=1;i<6;i++)if(i!==3)W('muralhaPedra',r.x+i,r.y+2);   // cruz no meio e T nas bordas
  if(!teste){const s=spot(9,4);W('muralhaPedra',s.x,s.y+1);for(let i=2;i<9;i++)W(i===5?'portaoMadeira':'muralhaFort',s.x+i,s.y+1);window.__s=s}
  window.__q=q;window.__r=r;for(const k in BCACHE)delete BCACHE[k];CHUNKS.clear();
  const cv=mkCanvas(CMOD.img.width,CMOD.img.height),g=cv.getContext('2d');g.drawImage(CMOD.img,0,0);const D=g.getImageData(0,0,cv.width,cv.height).data;let sombra=0;
  for(let i=0;i<D.length;i+=4)if(D[i+3]>0&&D[i+3]<240&&Math.max(D[i],D[i+1],D[i+2])<=10)sombra++;  // sombra de chão embutida = píxeis pretos meio transparentes
  const v=ents.filter(e=>e.type==='muralhaPedra').map(e=>bldVariant(e)&15);return{cmod:CMOD.ready,block:CMOD.meta.block,sombra_embutida_px:sombra,mascaras:[...new Set(v)].sort((a,b)=>a-b)}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); R = {}
        for dbg in ('', '?iso=1'):
            pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8777/index.html' + dbg); await pg.wait_for_timeout(3000)
            await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
            await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}#top,#bottom,#side,#grp,#toast{display:none!important}')
            R['cena'] = await pg.evaluate(CENA, SO_TESTE); n = 'dbg' if dbg else 'normal'
            await pg.evaluate("()=>{cam.z=3.0;centerCam(__q.x+5,__q.y+5)}"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{OUT}/torre4_{n}.png')
            await pg.evaluate("()=>{cam.z=2.3;centerCam(__q.x+5-1.6,__q.y+5-1.6)}"); await pg.wait_for_timeout(1000); await pg.screenshot(path=f'{OUT}/torre_inteira_{n}.png')
            await pg.evaluate("()=>{cam.z=2.0;centerCam(__r.x+3.5,__r.y+3)}"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{OUT}/cantos_{n}.png')
            for nm, (x, y) in {'canto_tras': (0, 0), 'canto_direita': (6, 0), 'canto_esquerda': (0, 5), 'canto_frente': (6, 5)}.items():
                c = await pg.evaluate(f"()=>{{cam.z=4.0;centerCam(__r.x+{x}+.5,__r.y+{y}+.5);const p=w2s(__r.x+{x}+.5,__r.y+{y}+.5);return [p.x,p.y]}}"); await pg.wait_for_timeout(700)
                cx = max(0, min(1280 - 560, c[0] - 280)); cy = max(0, min(760 - 520, c[1] - 330))
                await pg.screenshot(path=f'{OUT}/{nm}_{n}.png', clip={'x': cx, 'y': cy, 'width': 560, 'height': 520})
            if not SO_TESTE:
                await pg.evaluate("()=>{cam.z=2.6;centerCam(__s.x+4.5,__s.y+1.5)}"); await pg.wait_for_timeout(1000); await pg.screenshot(path=f'{OUT}/fort_portao_{n}.png')
            R['topz'] = await pg.evaluate("()=>({pedra:[...new Set(ents.filter(e=>e.type==='muralhaPedra').map(TOPZ))],torre:TOPZ(ents.find(e=>e.type==='torre'&&e.lvl===3))})")
            R['erros_' + n] = errs; await pg.close()
        print(json.dumps(R)); await br.close()
asyncio.run(main())
