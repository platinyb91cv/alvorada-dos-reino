# Gera uma amostra áudio (efeitos + música) usando o próprio motor do jogo, renderizado offline.
import asyncio,base64,subprocess,sys,json
from playwright.async_api import async_playwright
OUT=sys.argv[1] if len(sys.argv)>1 else "/tmp/amostra"
JS=r"""
async()=>{
  const seq=[ // [som, variante]
   ['ui_click',0],['v_sel_vill',0],['v_ok_vill',4],['chop',0],['chop',1],['chop',2],['mine_stone',0],['mine_stone',1],['mine_gold',0],['mine_gold',2],['hoe',0],['forage',0],['hammer',0],['hammer',1],['hammer',2],['butcher',0],['dep_wood',0],['dep_gold',0],
   ['spear_throw',0],['hit_flesh',0],['death_deer',0],['boar',1],['splash',0],
   ['v_sel_mil',0],['v_ok_mil',1],['v_attack',0],['march',0],['club',0],['clash',0],['clash',2],['clash',4],['stab',0],['bow',0],['arrow_hit',0],['xbow',0],['arrow_wood',1],
   ['snort',0],['gallop',0],['gallop',1],['neigh',0],['death',0],['death',3],['death_horse',0],
   ['v_sel_siege',0],['wheel',0],['ram_hit',0],['cat_launch',0],['boom',0],['treb_launch',0],['boom',2],['siege_break',0],['collapse',0],
   ['v_sel_priest',0],['heal',0],['chant',0],['convert',0],['v_sel_ship',0],['oars',0],['fire',0],['sink',0],
   ['place',0],['ready_vill',0],['ready_mil',0],['build_done',0],['research',0],['pop',0],['alarm',0],['age_up',0],['wonder',0],['victory',0],['defeat',0]];
  const plan=[];let t=.3;const marks=[];
  for(const [n,v] of seq){plan.push({sfx:n,v,at:t});marks.push([+t.toFixed(2),n]);const d=sndBuf(n,v).duration;t+=Math.max(.45,Math.min(d,2.2))+.25}
  t+=1;marks.push([+t.toFixed(2),'MÚSICA: paz']);plan.push({music:'paz',at:t,dur:34});t+=35;
  marks.push([+t.toFixed(2),'MÚSICA: batalha']);plan.push({music:'batalha',at:t,dur:24});t+=25;
  marks.push([+t.toFixed(2),'MÚSICA: menu']);plan.push({music:'menu',at:t,dur:22});t+=24;
  const buf=await audioRenderDemo(plan,t);
  const L=buf.getChannelData(0),R=buf.getChannelData(1),n=L.length;const pcm=new Int16Array(n*2);let pk=0;
  for(let i=0;i<n;i++){pk=Math.max(pk,Math.abs(L[i]),Math.abs(R[i]))}const g=pk>.98?.98/pk:1;
  for(let i=0;i<n;i++){pcm[2*i]=Math.max(-32767,Math.min(32767,L[i]*g*32767));pcm[2*i+1]=Math.max(-32767,Math.min(32767,R[i]*g*32767))}
  const u8=new Uint8Array(pcm.buffer);let s='';for(let i=0;i<u8.length;i+=0x8000)s+=String.fromCharCode.apply(null,u8.subarray(i,i+0x8000));
  return {b64:btoa(s),sr:buf.sampleRate,secs:t,marks,peak:pk}}
"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page()
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:300]))
    await pg.goto("file:///home/claude/alvorada/www/index.html");await pg.wait_for_timeout(300)
    await pg.evaluate("()=>{audioInit()}")
    r=await pg.evaluate(JS)
    raw=base64.b64decode(r['b64']);open(OUT+'.pcm','wb').write(raw)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','s16le','-ar',str(r['sr']),'-ac','2','-i',OUT+'.pcm','-b:a','128k',OUT+'.mp3'],check=True)
    json.dump(r['marks'],open(OUT+'_marcas.json','w'),ensure_ascii=False)
    print('secs',round(r['secs'],1),'peak',round(r['peak'],2),'ERRS',errs)
    await b.close()
asyncio.run(main())
