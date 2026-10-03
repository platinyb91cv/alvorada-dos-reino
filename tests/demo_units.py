import asyncio, sys
from playwright.async_api import async_playwright
OUT="/tmp/claude-0/-home-claude/415342e0-77a1-5a94-8f8a-71375aa47804/scratchpad/"
SETUP=r"""
(args)=>{const [age,zoom,mode]=args;startGame(12);paused=false;const s=__S();s.AIs[1]=null;s.vis.fill(2);s.P[0].age=age;s.P[1].age=age;
  // área limpa
  const cx=40,cy=58;for(let y=cy-12;y<=cy+12;y++)for(let x=cx-14;x<=cx+14;x++){const i=idx(x,y);const r=s.resAt[i];if(r&&!r.fish)removeRes(r)}
  for(const e of s.ents.slice())if(e.kind==='u'&&Math.abs(e.x-cx)<15&&Math.abs(e.y-cy)<13)kill(e);
  const put=(o,t,sx,row,fn)=>{const dx=sx*.5+row*.5,dy=-sx*.5+row*.5;const u=mkUnit(o,t,cx+dx,cy+dy);u.face=1;u.state='idle';if(fn)fn(u);return u};
  const R=(x,y,w,h,col)=>{};
  if(mode==='lineup'){
    // linha de cima: aldeões (4 variações) + infantaria; linha de baixo: cavalaria, cerco, sacerdote
    const ids=[];for(let v=0;v<4;v++){let u;do{u=put(0,'aldeao',-6+v*1.15,-1.4);if(hash(u.id)%4!==v){kill(u);u=null}}while(!u);}
    ['guerreiro','lanceiro','espadachim','arqueiro','besteiro','sacerdote'].forEach((t,i)=>put(0,t,-1.4+i*1.25,-1.4));
    ['cavaleiro','cavPesada','cavArqueira'].forEach((t,i)=>put(i===1?1:0,t,-6+i*2,1.4));
    ['ariete','catapulta','trebuchet'].forEach((t,i)=>put(0,t,.6+i*2.4,1.6));
    const vr=put(1,'guerreiro',6.2,-1.4);const vl=put(1,'lanceiro',7.4,-1.4);
  }
  if(mode==='jobs'){
    const fake=(rk,extra)=>({kind:'r',rk,amt:50,tx:0,ty:0,w:1,h:1,...(extra||{})});
    const mk=(dx,dy,st,fn)=>{let u=put(0,'aldeao',dx,dy);u.state=st;if(fn)fn(u);return u};
    mk(-6,-1.4,'idle');
    mk(-4.8,-1.4,'gather',u=>{u.gkind='wood';u.gres=fake('wood');u.anim=Math.PI*2*.2});
    mk(-3.6,-1.4,'gather',u=>{u.gkind='wood';u.gres=fake('wood');u.anim=Math.PI*2*.7});
    mk(-2.4,-1.4,'gather',u=>{u.gkind='stone';u.gres=fake('stone');u.anim=Math.PI*2*.7});
    mk(-1.2,-1.4,'gather',u=>{u.gkind='gold';u.gres=fake('gold');u.anim=Math.PI*2*.3});
    mk(0,-1.4,'gather',u=>{u.gkind='food';u.gres={kind:'b',d:{farm:1}};u.anim=Math.PI*2*.25});
    mk(1.2,-1.4,'gather',u=>{u.gkind='food';u.gres=fake('food');u.anim=Math.PI*2*.25});
    mk(2.4,-1.4,'build',u=>{u.anim=Math.PI*2*.25});
    mk(3.6,-1.4,'gather',u=>{u.gkind='food';u.gres=fake('food',{carcass:true});u.anim=Math.PI*2*.75});
    const gz=mkUnit(2,'gazela',cx+3.5-.7,cy-3.5-.7);
    mk(4.8,-1.4,'attack',u=>{u.target=gz;u.cd=u.d.rate*.6});
    mk(6,-1.4,'attack',u=>{u.target=gz;u.cd=u.d.rate*.05});
    for(const [i,ct] of ['wood','stone','gold','food'].entries())mk(-5+i*1.3,1.4,'return',u=>{u.carry=10;u.ctype=ct;u.path=[{x:99,y:99}];u.pi=0;u.anim=Math.PI*2*i/4});
    mk(0.4,1.4,'return',u=>{u.carry=10;u.ctype='food';u.gres={kind:'r',carcass:true};u.path=[{x:99,y:99}];u.pi=0});
    for(let f=0;f<4;f++)mk(1.8+f*1.2,1.4,'move',u=>{u.path=[{x:99,y:99}];u.pi=0;u.anim=Math.PI*2*f/4});
  }
  if(mode==='attack'){
    const en=mkUnit(1,'guerreiro',cx+9,cy);en.state='hold';
    const types=['guerreiro','lanceiro','espadachim','arqueiro','besteiro','cavaleiro','cavArqueira'];
    types.forEach((t,i)=>{for(let k=0;k<3;k++){const u=put(0,t,-6+i*1.9+k*.55,-2+k*1.6);u.state='attack';u.target=en;u.cd=u.d.rate*[.95,.5,.1][k];if(u.d.range===0)u.target={...en,x:u.x+.5,y:u.y,kind:'u',d:en.d,dead:false}}});
    ['ariete','catapulta','trebuchet'].forEach((t,i)=>{for(let k=0;k<2;k++){const u=put(0,t,-5+i*4+k*1.8,3.6);u.state='attack';u.target=en;u.cd=u.d.rate*[.95,.1][k]}});
  }
  s.fx.length=0;{const d2=fogImg.data;for(let i=0;i<80*80;i++)d2[i*4+3]=0;fogCtx.putImageData(fogImg,0,0)}paused=true;cam.z=zoom;centerCam(cx,cy);render();return true}
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":900,"height":420}, device_scale_factor=2)
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
        await pg.goto("file:///home/claude/alvorada/www/index.html"); await pg.click("#lgPreview"); await pg.click("#bPlay"); await pg.wait_for_timeout(300)
        shots=[("lineup",2,1.6),("lineup",0,1.6),("lineup",1,1.6),("jobs",1,1.7),("attack",2,1.2),("lineup",2,2.2),("lineup",2,.6)]
        for mode,age,z in shots:
            await pg.evaluate(SETUP,[age,z,mode]); await pg.evaluate("document.getElementById('bottom').style.display='none';document.getElementById('toast').innerHTML=''")
            await pg.wait_for_timeout(250)
            await pg.screenshot(path=f"{OUT}demo_{mode}_a{age}_z{z}.png")
        print("ERRS",errs); await b.close()
asyncio.run(main())
