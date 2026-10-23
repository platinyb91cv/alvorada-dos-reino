# Soldados em cima da muralha e da torre: arqueiros sobem ao muro de pedra e ao portão, disparam contra o inimigo e aparecem lá em cima.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/soldados_muro.png'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        r = await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=2;
          const ok=(x,y,w,h)=>{for(let j=-1;j<=h;j++)for(let i=-1;i<=w;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
          let q=null;for(let r=4;r<60&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(ok(x,y,12,8))q={x,y}}
          const W=(t,x,y)=>mkBld(ME,t,x,y,true);const walls=[];
          for(let i=0;i<10;i++){const x=q.x+i,y=q.y+2;if(i===4)walls.push(W('portaoPedra',x,y));else if(i===7){const t=W('torre',x,y-1);t.lvl=2;walls.push(t)}else if(i===8){}else walls.push(W('muralhaPedra',x,y))}
          const archers=[];for(const b of walls){for(let k=0;k<(b.type==='torre'?3:b.d.garr);k++){const u=mkUnit(ME,k%2?'besteiro':'arqueiro',b.tx+.5,b.ty+3);if(garrisonIn(u,b))archers.push(u)}}
          const vil=mkUnit(ME,'aldeao',q.x+2,q.y+4);const refused=!garrisonIn(vil,walls[0]);
          const foes=[];for(let k=0;k<5;k++)foes.push(mkUnit(1,'guerreiro',q.x+2+k,q.y-2));
          cam.z=1.8;centerCam(q.x+5,q.y+2);window.__T={foes,walls};
          return{garrisoned:archers.length,villagerRefused:refused,hp:BLDS.muralhaPedra.hp}}""")
        await pg.wait_for_timeout(4000)
        st = await pg.evaluate("()=>({proj:projs.length,foesHurt:window.__T.foes.filter(f=>f.hp<f.max||!alive(f)).length,onWalls:window.__T.walls.reduce((a,b)=>a+(b.garr?b.garr.length:0),0)})")
        await pg.screenshot(path=OUT)
        print(json.dumps({'setup': r, 'after4s': st, 'errs': errs})); await br.close()
asyncio.run(main())
