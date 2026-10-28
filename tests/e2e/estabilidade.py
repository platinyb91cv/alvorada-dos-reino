"""Full-game regression: live cargo atlas, end screen, camera travel and error recovery."""
import asyncio,json,os,sys
from pathlib import Path
from playwright.async_api import async_playwright
OUT=Path(sys.argv[1] if len(sys.argv)>1 else 'test-results');OUT.mkdir(parents=True,exist_ok=True)
async def main():
 async with async_playwright() as p:
  br=await p.chromium.launch(executable_path=os.environ.get('ALV_BROWSER'))
  pg=await br.new_page(viewport={'width':915,'height':412},device_scale_factor=2.6,is_mobile=True,has_touch=True)
  await pg.add_init_script("window.ALV_CFG_OVERRIDE={supabaseUrl:''}")
  errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
  await pg.goto('http://localhost:8777/index.html');await pg.wait_for_function('()=>!!window.__alv')
  await pg.evaluate("startGame(4242,{map:'continental',vic:'classico',civ:['planicies','mar']})")
  await pg.wait_for_timeout(1200)
  await pg.evaluate("()=>{paused=true;u3ready(UNIT3D.carroca)}");await pg.wait_for_function('UNIT3D.carroca.ready')
  result={}
  result['cargoAtlas']=await pg.evaluate("""()=>{const s=G.starts[0];mkUnit(0,'carrocaCarga',s.x+3,s.y+2);const src=UNIT3D.carroca;src.seen=G.time-80;G.agc=G.time-11;atlasGC();return{present:ents.some(e=>e.type==='carrocaCarga'),retained:src.ready&&!!src.img}}""")
  result['localAccounts']=await pg.evaluate("""()=>{ACC.user={id:'local-a'};saveGame(true);const a=hasSave();ACC.user={id:'local-b'};const b=hasSave();ACC.user={id:'local-a'};const restored=hasSave();ACC.user=null;return{a,b,restored}}""")
  result['legacyClear']=await pg.evaluate("""()=>{ACC.user={id:'legacy-a'};localStorage.setItem(SAVE_KEY,serialize());localStorage.removeItem(SAVE_KEY+'__dono');localStorage.removeItem(SAVE_KEY+'_legacy-a');const migrated=hasSave();clearSave();const cleared=!hasSave();ACC.user=null;return{migrated,cleared}}""")
  result['endRating']=await pg.evaluate("()=>{$('endRate').hidden=false;$('endRate').textContent='Previous rating';endGame(false,false);return{hidden:$('endRate').hidden}}")
  await pg.evaluate("startGame(4242,{map:'continental',vic:'classico',civ:['planicies','mar']})")
  await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
  t0=await pg.evaluate('G.time')
  for x,y in [(8,8),(72,8),(72,72),(8,72),(40,40)]:
   await pg.evaluate('([x,y])=>{cam.z=1.4;centerCam(x,y)}',[x,y]);await pg.wait_for_timeout(500)
  result['camera']=await pg.evaluate("()=>({time:G.time,cacheBytes:[...CHUNKS.values()].reduce((a,v)=>a+v.b,0),errors:ERRLOG.map(x=>x.m)})")
  result['camera']['advanced']=result['camera']['time']>t0
  await pg.screenshot(path=str(OUT/'estabilidade-mobile.png'))
  result['pageErrors']=errors
  (OUT/'estabilidade.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
  assert result['cargoAtlas']['present'] and result['cargoAtlas']['retained'],result
  assert result['legacyClear']=={'migrated':True,'cleared':True},result
  assert result['localAccounts']=={'a':True,'b':False,'restored':True},result
  assert result['endRating']['hidden'] and result['camera']['advanced'] and not result['camera']['errors'] and not errors,result
  print(json.dumps(result,ensure_ascii=False));print('PASS stability in the complete game')
  await br.close()
asyncio.run(main())
