# Capturas da Play Store (1920×1080) tiradas do jogo a correr, com a arte 3D: aldeia, batalha nas muralhas e mercado.
# Uso: servidor em localhost:8777 (www) e  python3 loja/capturas.py [pasta-de-saída]
import asyncio, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else 'loja'
START = """async()=>{startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})}"""
HELP = """()=>{window.__c=ents.find(e=>e.type==='centro'&&e.o===ME);window.__q0=centerOf(__c);
  window.__put=(o,t,near,r0=3)=>{for(let r=r0;r<45;r++)for(let a=0;a<64;a++){const tx=Math.round(near.x+Math.cos(a/64*6.283)*r),ty=Math.round(near.y+Math.sin(a/64*6.283)*r);if(canPlace(t,tx,ty,ME,0,true)){const b=mkBld(o,t,tx,ty,true);return b}}return null};
  window.__free=(x,y,w,h)=>{for(let j=-1;j<=h;j++)for(let i=-1;i<=w;i++){const tx=x+i,ty=y+j;if(!inb(tx,ty)||!okTile(idx(tx,ty))||bldAt[idx(tx,ty)]||resAt[idx(tx,ty)])return false}return true};
  window.__spot=(w,h,near,r0=4)=>{for(let r=r0;r<70;r++)for(let a=0;a<64;a++){const x=Math.round(near.x+Math.cos(a/64*6.283)*r),y=Math.round(near.y+Math.sin(a/64*6.283)*r);if(__free(x,y,w,h))return{x,y}}return null};
  for(const p of P)if(p){p.res.food=1200;p.res.wood=950;p.res.gold=640;p.res.stone=480}}"""
async def cena(br, nome, js, espera=1500):
    pg = await br.new_page(viewport={'width': 960, 'height': 540}, device_scale_factor=2); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(2500)
    await pg.evaluate(START); await pg.wait_for_timeout(2500)
    await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
    await pg.evaluate(HELP); r = await pg.evaluate(js); await pg.wait_for_timeout(espera)
    if isinstance(r, dict) and r.get('depois'): await pg.evaluate(r['depois']); await pg.wait_for_timeout(r.get('espera2', 1500))
    await pg.add_style_tag(content='#toast{display:none!important}')
    await pg.screenshot(path=f'{OUT}/{nome}'); await pg.close(); print(nome, r if not isinstance(r, dict) else {k: v for k, v in r.items() if k != 'depois'}, errs)
    return errs
ALDEIA = """()=>{P[ME].age=2;const q0=__q0,made=[];
  for(const t of ['casa','casa','armazem','quartel','ferreiro','templo','mercado','arquearia','casa','estabulo','casa','oficina']){const b=__put(ME,t,q0,4);if(b)made.push(t)}
  const t1=__put(ME,'torre',q0,8);if(t1)t1.lvl=3;const t2=__put(ME,'torre',q0,9);if(t2)t2.lvl=2;
  for(const e of ents)if(e.kind==='u'&&e.o===ME&&e.type==='aldeao'){}
  for(let k=0;k<8;k++)mkUnit(ME,k%2?'lanceiro':'arqueiro',q0.x+3+k*.5,q0.y+4);
  cam.z=1.05;centerCam(q0.x+1,q0.y+2);for(const k in BCACHE)delete BCACHE[k];return{made:made.length}}"""
BATALHA = """()=>{P[ME].age=2;for(let k=0;k<10;k++)__put(ME,'casa',__q0,3);const q=__spot(14,9,__q0,9);const W=(t,x,y)=>mkBld(ME,t,x,y,true);const S=[];
  S.push(W('muralhaPedra',q.x,q.y+4),W('muralhaPedra',q.x+1,q.y+4),W('portaoPedra',q.x+2,q.y+4),W('muralhaPedra',q.x+3,q.y+4),W('muralhaFort',q.x+4,q.y+4),W('muralhaFort',q.x+5,q.y+4));
  const t=W('torre',q.x+6,q.y+3);t.lvl=3;S.push(t,W('muralhaFort',q.x+8,q.y+4),W('muralhaFort',q.x+9,q.y+4));const t2=W('torre',q.x+10,q.y+3);t2.lvl=2;S.push(t2,W('muralhaPedra',q.x+12,q.y+4));
  for(const b of S){if(!b.d.garr)continue;const us=Array.from({length:b.d.garr},(_,k)=>mkUnit(ME,b.type==='torre'?'besteiro':'arqueiro',b.tx+k*.3,b.ty+2.5));act('garrison',{b:b.id,u:us.map(u=>u.id)})}
  for(let k=0;k<6;k++)mkUnit(ME,k%2?'espadachim':'lanceiro',q.x+3+k*.6,q.y+6.5);
  window.__q=q;cam.z=1.45;centerCam(q.x+6,q.y+3.5);for(const k in BCACHE)delete BCACHE[k];
  return{depois:`()=>{const q=__q;const foe=P.findIndex((p,i)=>i!==ME&&p);for(let k=0;k<14;k++){const f=mkUnit(foe,['guerreiro','espadachim','lanceiro'][k%3],q.x+k*.9,q.y-1.5-(k%3)*.6);orderAttack(f,ents.find(e=>e.kind==='b'&&e.o===ME&&e.type==='portaoPedra'))}}`,espera2:3200}}"""
MERCADO = """()=>{P[ME].age=1;const q0=__q0;const m=__put(ME,'mercado',q0,5);const foe=P.findIndex((p,i)=>i!==ME&&p);
  for(const t of ['quinta','quinta','quinta','casa','casa','armazem','curral'])__put(ME,t,q0,3);
  const vs=ents.filter(e=>e.kind==='u'&&e.o===ME&&e.type==='aldeao');for(let k=0;k<6;k++)mkUnit(ME,'aldeao',q0.x+2+k*.4,q0.y+3);
  const c=mkUnit(ME,'carroca',centerOf(m).x+1,centerOf(m).y+2);
  const farms=ents.filter(e=>e.kind==='b'&&e.o===ME&&e.d.farm);const rs=ents.filter(e=>e.kind==='r'&&alive(e));let fi=0;
  for(const v of ents.filter(e=>e.kind==='u'&&e.o===ME&&e.type==='aldeao')){if(fi<farms.length*2){orderGather(v,farms[fi>>1]);fi++}else{const cv=centerOf(v);const r=rs.sort((a,b)=>hyp(a.tx-cv.x,a.ty-cv.y)-hyp(b.tx-cv.x,b.ty-cv.y))[0];if(r)orderGather(v,r)}}
  const mc=centerOf(m);cam.z=1.3;centerCam((mc.x+q0.x)/2,(mc.y+q0.y)/2);for(const k in BCACHE)delete BCACHE[k];return{mercado:!!m}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); e = []
        e += await cena(br, 'captura-2-aldeia.png', ALDEIA)
        e += await cena(br, 'captura-3-batalha.png', BATALHA)
        e += await cena(br, 'captura-4-mercado.png', MERCADO, 3000)
        await br.close(); print('erros', e)
asyncio.run(main())
