import asyncio, json
from playwright.async_api import async_playwright
OUT='/tmp/claude-0/cerco_'
SETUP="""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);const clear=(x,y)=>{for(let j=-4;j<=10;j++)for(let i=-4;i<=12;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty)))return false}return true};
 let q=null;for(let r=5;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(clear(x,y))q={x,y}}
 window.__q=q;P[ME].age=2;const ram=mkUnit(ME,'ariete',q.x+1,q.y+1),tre=mkUnit(ME,'trebuchet',q.x+5,q.y+1),sol=mkUnit(ME,'guerreiro',q.x+3,q.y+3);window.__S=[ram,tre];cam.z=1.6;centerCam(q.x+3,q.y+2);
 return {q,ready:[UNIT3D.ariete.ready,UNIT3D.trebuchet.ready],types:[ram.type,tre.type]}}"""
async def snap(pg,name):
    await pg.wait_for_timeout(150); await pg.screenshot(path=OUT+name+'.png', clip={'x':240,'y':120,'width':800,'height':480})
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
            await pg.evaluate("(k)=>{const V=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]][k];const q=window.__q;window.__S.forEach((u,i)=>{u.x=q.x+1+i*4.5;u.y=q.y+3;u.state='idle';u.path=null;moveTo(u,u.x+V[0]*3,u.y+V[1]*3)})}",k)
            await pg.wait_for_timeout(900); R['walk'][lab]=await pg.evaluate("()=>window.__S.map(u=>[u.type,unit3dState(u),unit3dHeading(u)])")
            if lab in ('SE','W','NE'): await snap(pg,'marcha-'+lab)
        await pg.wait_for_timeout(3500)
        R['atk']=await pg.evaluate("""()=>{const q=window.__q;const [ram,tre]=window.__S;ram.x=q.x+1;ram.y=q.y+1;tre.x=q.x+5;tre.y=q.y+1;
          let h=null;for(let r=2;r<9&&!h;r++)for(let a=0;a<24&&!h;a++){const tx=Math.round(q.x+1+Math.cos(a/24*6.283)*r),ty=Math.round(q.y+5+Math.sin(a/24*6.283)*r);if(canPlace('casa',tx,ty,1,0,true))h=mkBld(1,'casa',tx,ty,true)}
          window.__h=h;orderAttack(ram,h);orderAttack(tre,h);return {h:[h.tx,h.ty,h.hp]}}""")
        await pg.wait_for_timeout(2500); R['atk2']=await pg.evaluate("()=>({states:window.__S.map(u=>unit3dState(u)),hp:Math.round(window.__h.hp)})"); await snap(pg,'ataque')
        await pg.wait_for_timeout(3000); await snap(pg,'ataque2')
        await pg.evaluate("()=>window.__S.forEach(u=>applyDmg(u,999,null,false))"); await pg.wait_for_timeout(1200); await snap(pg,'destruidos')
        R['errors']=errs; print(json.dumps(R,indent=1)); await br.close()
asyncio.run(main())
