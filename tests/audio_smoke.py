import asyncio,json
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]);pg=await b.new_page(viewport={"width":900,"height":420})
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:300]));pg.on("console",lambda m:errs.append(m.text[:200]) if m.type=="error" else None)
    await pg.goto("file:///home/claude/alvorada/www/index.html");await pg.mouse.click(5,300);await pg.wait_for_timeout(300)
    r=await pg.evaluate("()=>{const A=__AUD();return {state:A.AUD.ctx&&A.AUD.ctx.state,mood:A.MUS.mood}}");print("menu",r)
    await pg.click("#lgPreview"); await pg.click("#bPlay");await pg.wait_for_timeout(1500)
    r=await pg.evaluate("""()=>{const A=__AUD();const s=__S();const out={state:A.AUD.ctx.state,mood:A.MUS.mood,want:A.MUS.want,amb:!!A.AUD.amb};
      const bad=[];for(const k of Object.keys(A.SND)){for(let v=0;v<A.SND[k].v;v++){try{const t=performance.now();const bb=sndBuf(k,v);const d=bb.getChannelData(0);let nan=false,pk=0;for(let i=0;i<d.length;i++){if(!isFinite(d[i]))nan=true;pk=Math.max(pk,Math.abs(d[i]))}if(nan||pk<0.05)bad.push(k+v+' pk'+pk.toFixed(2))}catch(e){bad.push(k+':'+e.message)}}}
      out.n=Object.keys(A.SND).length;out.bad=bad;return out}""");print(json.dumps(r))
    await pg.wait_for_timeout(4000)
    r=await pg.evaluate("()=>{const A=__AUD();return {stats:A.AUD.stats,voices:A.AUD.voices,bar:A.MUS.bar,step:A.MUS.step,bufs:A.AUD.buf.size}}");print(json.dumps(r))
    print("ERRS",errs);await b.close()
asyncio.run(main())
