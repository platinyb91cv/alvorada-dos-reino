import asyncio, json
from playwright.async_api import async_playwright
OUT='/tmp/claude-0/veado_'
SETUP="""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q0=centerOf(c);const clear=(x,y)=>{for(let j=-4;j<=8;j++)for(let i=-4;i<=10;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty)))return false}return true};
 let q=null;for(let r=5;r<70&&!q;r++)for(let a=0;a<64&&!q;a++){const x=Math.round(q0.x+Math.cos(a/64*6.283)*r),y=Math.round(q0.y+Math.sin(a/64*6.283)*r);if(clear(x,y))q={x,y}}
 window.__q=q;const S=[];for(let i=0;i<4;i++)S.push(mkUnit(2,'gazela',q.x+1+i*1.6,q.y+1+(i%2)));const v=mkUnit(ME,'aldeao',q.x+2,q.y+4);const s=mkUnit(ME,'guerreiro',q.x+4,q.y+4);window.__S=S;cam.z=1.8;centerCam(q.x+3,q.y+2);
 return {q,ready:UNIT3D.gazela.ready}}"""
async def snap(pg,name):
    await pg.wait_for_timeout(150); await pg.screenshot(path=OUT+name+'.png', clip={'x':340,'y':180,'width':600,'height':360})
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(viewport={'width':1280,'height':760}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3000)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(3000)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        R={'setup':await pg.evaluate(SETUP)}; await pg.wait_for_timeout(1500)
        R['parados']=await pg.evaluate("()=>window.__S.map(u=>unit3dState(u))"); await snap(pg,'parados')
        R['walk']={}
        for k,lab in enumerate(['SE','S','SW','W','NW','N','NE','E']):
            await pg.evaluate("(k)=>{const V=[[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]][k];const q=window.__q;window.__S.forEach((u,i)=>{u.x=q.x+1+i*1.6;u.y=q.y+1+(i%2);u.state='idle';u.path=null;moveTo(u,u.x+V[0]*3,u.y+V[1]*3)})}",k)
            await pg.wait_for_timeout(500); R['walk'][lab]=await pg.evaluate("()=>window.__S.map(u=>[unit3dState(u),unit3dHeading(u)])")
            if lab in ('SE','W','NE'): await snap(pg,'corre-'+lab)
        await pg.wait_for_timeout(2500)
        await pg.evaluate("()=>window.__S.slice(0,2).forEach(u=>applyDmg(u,999,null,false))"); await pg.wait_for_timeout(300); await snap(pg,'morte0')
        await pg.wait_for_timeout(2500); await snap(pg,'carcacas')
        R['carc']=await pg.evaluate("()=>{const out=[];for(const r of byId.values())if(r.kind==='r'&&r.carcass)out.push([r.var,r.dir,r.amt]);return out}")
        R['errors']=errs; print(json.dumps(R)); await br.close()
asyncio.run(main())
