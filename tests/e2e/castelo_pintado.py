# Prova do castelo pintado: muralha com portão de pedra ao longo de x e de y, torres nível 3, portão aberto/fechado,
# muros debaixo das torres escondidos, soldados em cima do portão e das torres dele, passagem (dono passa, inimigo não), sem erros.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        R = {}
        R['montar'] = await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);P[ME].age=2;
          const ok=(x,y,w,h)=>{for(let j=-1;j<=h;j++)for(let i=-1;i<=w;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
          let q=null;for(let r=4;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(ok(x,y,14,10))q={x,y}}
          const W=(t,x,y)=>mkBld(ME,t,x,y,true);const S={};
          for(let i=0;i<9;i++)S['m'+i]=W(i===4?'portaoPedra':'muralhaPedra',q.x+i,q.y+3);          // ao longo de x
          S.t=W('torre',q.x+9,q.y+2);S.t.lvl=3;S.ta=W('muralhaPedra',q.x+11,q.y+3);S.tb=W('muralhaPedra',q.x+9,q.y+4);S.tc=W('muralhaPedra',q.x+10,q.y+1);
          for(let j=0;j<7;j++)S['n'+j]=W(j===3?'portaoPedra':'muralhaPedra',q.x+12,q.y+3+j);    // ao longo de y
          window.__S=S;window.__q=q;for(const k in BCACHE)delete BCACHE[k];
          const gx=S.m4,gy=S.n3;return{pintado:PGATE.ready,dir_x:bldVariant(gx),dir_y:bldVariant(gy),debaixo_das_torres:[S.m3,S.m5,S.n2,S.n4].map(b=>bldVariant(b)&768),
            longe:[S.m2,S.m6].map(b=>bldVariant(b)&768),topz_portao:TOPZ(gx),topz_torre_do_portao:TOPZ(S.m3),topz_torre3:TOPZ(S.t)}}""")
        await pg.evaluate("()=>{cam.z=1.6;centerCam(__q.x+6,__q.y+5)}"); await pg.wait_for_timeout(1200); await pg.screenshot(path=OUT + '/castelo_geral.png')
        # soldados em cima e porta aberta (dono ao pé)
        R['subir'] = await pg.evaluate("""()=>{const S=__S;for(const b of [S.m4,S.m3,S.m5,S.t]){const us=Array.from({length:b.d.garr},(_,k)=>mkUnit(ME,'arqueiro',b.tx+k*.3,b.ty+2));act('garrison',{b:b.id,u:us.map(u=>u.id)})}
          for(let k=0;k<4;k++)mkUnit(ME,'lanceiro',S.m4.tx+.5,S.m4.ty+1.6+k*.2);return true}""")
        await pg.wait_for_timeout(5000)
        await pg.evaluate("()=>{cam.z=3;centerCam(__q.x+4.5,__q.y+3.5)}"); await pg.wait_for_timeout(900); await pg.screenshot(path=OUT + '/castelo_portao_x.png')
        await pg.evaluate("()=>{cam.z=3;centerCam(__q.x+12.5,__q.y+6.5)}"); await pg.wait_for_timeout(900); await pg.screenshot(path=OUT + '/castelo_portao_y.png')
        await pg.evaluate("()=>{cam.z=3.2;centerCam(__q.x+10,__q.y+3)}"); await pg.wait_for_timeout(900); await pg.screenshot(path=OUT + '/castelo_torre3.png')
        R['em_cima'] = await pg.evaluate("()=>[__S.m4,__S.m3,__S.m5,__S.t].map(b=>b.garr.length+'/'+b.d.garr)")
        R['passagem'] = await pg.evaluate("""()=>{const g=__S.n3,i=idx(g.tx,g.ty);const t=o=>{const m0=MV.o,n0=MV.nav;MV.o=o;MV.nav=false;const r=okTile(i);MV.o=m0;MV.nav=n0;return r};const w=idx(__S.n2.tx,__S.n2.ty);return{dono:t(ME),inimigo:t(1),muro_escondido_bloqueia:blk[w]!==0&&blk[w]!==4}}""")
        R['erros'] = errs; print(json.dumps(R, ensure_ascii=False, indent=1)); await br.close()
asyncio.run(main())
