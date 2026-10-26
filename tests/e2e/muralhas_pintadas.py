# Validação das muralhas pintadas + torre redonda: torre 2x2 com muros nas 4 direções, retas em x e y, cantos (4), T, cruz,
# muro sozinho, pontas. Imagens com e sem a depuração (?iso=1: grelha, áreas ocupadas, âncoras). Sem erros de página.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
CENA = """()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=2;for(let i=0;i<vis.length;i++)vis[i]=2;
  const ok=(x,y,w,h)=>{for(let j=-1;j<=h;j++)for(let i=-1;i<=w;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
  const spot=(w,h,skip)=>{for(let r=6;r<90;r++)for(let a=0;a<64;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(ok(x,y,w,h)&&!(skip&&Math.abs(x-skip.x)<14&&Math.abs(y-skip.y)<14))return{x,y}}return null};
  const q=spot(11,11);
  const W=(t,x,y)=>mkBld(ME,t,x,y,true);
  // torre com muros nas 4 direções
  const t=W('torre',q.x+4,q.y+4);t.lvl=3;for(let i=1;i<=3;i++){W('muralhaPedra',q.x+4-i,q.y+4);W('muralhaPedra',q.x+5+i,q.y+5);W('muralhaPedra',q.x+5,q.y+4-i);W('muralhaPedra',q.x+4,q.y+5+i)}
  // retas, cantos, T, cruz, sozinho
  const b=spot(11,7,q);for(let i=0;i<6;i++)W('muralhaPedra',b.x+i,b.y);for(let j=1;j<6;j++)W('muralhaPedra',b.x+5,b.y+j);for(let i=0;i<5;i++)W('muralhaPedra',b.x+i,b.y+5);for(let j=1;j<5;j++)W('muralhaPedra',b.x,b.y+j);
  for(let j=1;j<5;j++)W('muralhaPedra',b.x+2,b.y+j); // T em cima e em baixo
  for(let i=6;i<9;i++)W('muralhaPedra',b.x+i,b.y+3);W('muralhaPedra',b.x+9,b.y+1);   // T ao lado e muro sozinho
  // portão de madeira numa muralha de pedra pintada (o muro da frente pára na face da casa do portão)
  {const g=spot(7,3,q);if(g){window.__g=g;for(let i=0;i<7;i++)W(i===3?'portaoMadeira':'muralhaPedra',g.x+i,g.y+1)}}
  window.__q=q;window.__b=b;for(const k in BCACHE)delete BCACHE[k];CHUNKS.clear();return {q,pw:PWALL.ready}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); R = {}
        for dbg in ('', '?iso=1'):
            pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8777/index.html' + dbg); await pg.wait_for_timeout(3000)
            await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
            await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}#top,#bottom,#side,#grp,#toast{display:none!important}')
            R['cena'] = await pg.evaluate(CENA); n = 'dbg' if dbg else 'normal'
            await pg.evaluate("()=>{cam.z=2.2;centerCam(__q.x+5,__q.y+5)}"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{OUT}/torre4_{n}.png')
            await pg.evaluate("()=>{cam.z=1.6;centerCam(__b.x+4,__b.y+3)}"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{OUT}/combinacoes_{n}.png')
            if await pg.evaluate('()=>!!window.__g'):
                await pg.evaluate("()=>{cam.z=2.6;centerCam(__g.x+3.5,__g.y+1.5)}"); await pg.wait_for_timeout(1000); await pg.screenshot(path=f'{OUT}/portao_madeira_{n}.png')
            R['topz'] = await pg.evaluate("()=>{const w=ents.filter(e=>e.type==='muralhaPedra');return [...new Set(w.map(TOPZ))]}")
            R['erros_' + n] = errs; await pg.close()
        print(json.dumps(R)); await br.close()
asyncio.run(main())
