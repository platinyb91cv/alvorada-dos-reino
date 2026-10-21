import asyncio, json
from playwright.async_api import async_playwright
OUT='/tmp/claude-0/cav/jogo_'
SETUP="""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);const clear=(x,y)=>{for(let j=-4;j<=10;j++)for(let i=-4;i<=12;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
 let q=null;for(let r=5;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(clear(x,y))q={x,y}}
 window.__q=q;P[ME].age=2;const S=['cavaleiro','cavPesada','cavArqueira'].map((t,i)=>mkUnit(ME,t,q.x+1+i*2.4,q.y+1));mkUnit(ME,'guerreiro',q.x+2,q.y+3);window.__S=S;cam.z=1.9;centerCam(q.x+3.5,q.y+2);
 return {q,ready:S.map(u=>UNIT3D[u.type]&&UNIT3D[u.type].ready)}}"""
async def snap(pg,name):
    await pg.wait_for_timeout(150); await pg.screenshot(path=OUT+name+'.png', clip={'x':340,'y':160,'width':620,'height':400})
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(3000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        R={'setup':await pg.evaluate(SETUP)}; await pg.wait_for_timeout(1500); await snap(pg,'parados')
        R['walk']={}
        for k,lab in enumerate(['SE','S','SW','W','NW','N','NE','E']):
            await pg.evaluate("(k)=>{const V=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]][k];const q=window.__q;window.__S.forEach((u,i)=>{u.x=q.x+1+i*2.4;u.y=q.y+2;u.state='idle';u.path=null;moveTo(u,u.x+V[0]*3,u.y+V[1]*3)})}",k)
            await pg.wait_for_timeout(450); R['walk'][lab]=await pg.evaluate("()=>window.__S.map(u=>[unit3dState(u),unit3dHeading(u)])")
            if lab in ('SE','W','NE'): await snap(pg,'galope-'+lab)
        await pg.wait_for_timeout(2500)
        R['atk']=await pg.evaluate("""()=>{const q=window.__q;const S=window.__S;const en=[0,1,2].map(i=>mkUnit(1,'guerreiro',q.x+1+i*2.4,q.y+4.2));S.forEach((u,i)=>{u.x=q.x+1+i*2.4;u.y=q.y+2;u.path=null;orderAttack(u,en[i])});window.__E=en;return en.map(e=>e.hp)}""")
        await pg.wait_for_timeout(2200); R['atk2']=await pg.evaluate("()=>({st:window.__S.map(u=>unit3dState(u)),hp:window.__E.map(e=>Math.round(e.hp))})"); await snap(pg,'ataque')
        await pg.evaluate("()=>window.__S.forEach(u=>applyDmg(u,999,null,false))"); await pg.wait_for_timeout(1500); await snap(pg,'mortos')
        R['errors']=errs; print(json.dumps(R)); await br.close()
asyncio.run(main())
