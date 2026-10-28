# Meu Reino não pode perder a gravação:
#  1) jogar no reino, sair para o menu, jogar e acabar uma partida normal, voltar ao reino -> continua onde estava;
#  2) nuvem com dois lugares: a partida normal (guardar ou acabar) já não apaga nem substitui a cópia do reino;
#     «Continuar (da nuvem)» só carrega a partida normal e nunca escreve um reino antigo por cima do atual;
#  3) telemóvel sem o reino (dados apagados) recupera-o da nuvem; uma cópia da nuvem mais atrasada é ignorada;
#  4) gravação feita sem sessão (sem rede / sessão expirada) e com sessão: fica a mais avançada; sem sessão usa a última conta.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
FAKE = r"""()=>{const db={row:null,revision:null,n:0};window.__db=db;
const fetch=async(url,opt={})=>{const u=new URL(url),v=opt.body?JSON.parse(opt.body):null;let data=[],status=200;
 if(u.pathname.endsWith('/cloud_saves')){if(!opt.method||opt.method==='GET')data=db.row?[{data:db.row,updated_at:db.revision}]:[];
 else if(opt.method==='POST'){if(db.row){data={code:'23505',message:'duplicate'};status=409}else{db.row=v.data;db.revision=new Date(++db.n).toISOString();data=[{user_id:v.user_id}]}}
 else if(opt.method==='PATCH'&&u.searchParams.get('updated_at')==='eq.'+db.revision){db.row=v.data;db.revision=new Date(++db.n).toISOString();data=[{user_id:'u1'}]}}
 return new Response(JSON.stringify(data),{status,headers:{'content-type':'application/json'}})};
 ACC.sb=window.supabase.createClient('http://cloud.test','sb_publishable_test',{auth:{persistSession:false,autoRefreshToken:false,detectSessionInUrl:false},global:{fetch}});ACC.user={id:'u1'};ACC.preview=false;}"""
ST = "()=>({reino:!!(G&&G.reino),t:Math.round(G.time),casas:ents.filter(e=>e.kind==='b'&&e.o===0&&e.type==='casa').length,n:G.reino?G.reino.n:null})"
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 915, 'height': 412}); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(5000)
        await pg.add_style_tag(content='#sLogin{display:none!important}'); await pg.evaluate(FAKE)
        r = {}
        await pg.evaluate("()=>reinoFound()"); await pg.wait_for_timeout(3500); await pg.evaluate("()=>{speed=8}"); await pg.wait_for_timeout(6000)
        await pg.evaluate("()=>{const s=G.starts[0];for(let i=0;i<3;i++)__alv.placeAt(0,'casa',Math.round(s.x)+8+i*3,Math.round(s.y)+8)}"); await pg.wait_for_timeout(1500)
        r['reino_antes'] = await pg.evaluate(ST)
        await pg.evaluate("()=>{togglePause();$('bQuit').onclick()}"); await pg.wait_for_timeout(2500)
        r['nuvem_depois_sair_reino'] = await pg.evaluate("async()=>{const w=await cloudRow();return{reino:!!w.reino,normal:!!w.normal}}")
        # partida normal: guardar (vai para a nuvem) e acabar
        await pg.evaluate("()=>{$('bSetupGo').onclick()}"); await pg.wait_for_timeout(4500); await pg.evaluate("()=>{speed=8}"); await pg.wait_for_timeout(5000)
        await pg.evaluate("()=>{$('bSave').onclick()}"); await pg.wait_for_timeout(2000)
        r['nuvem_normal_guardada'] = await pg.evaluate("async()=>{const w=await cloudRow();return{reino:!!w.reino,normal:!!w.normal}}")
        await pg.evaluate("()=>endGame(false,false)"); await pg.wait_for_timeout(2500)
        r['nuvem_normal_acabada'] = await pg.evaluate("async()=>{const w=await cloudRow();return{reino:!!w.reino,normal:!!w.normal}}")
        await pg.evaluate("()=>{$('bEndMenu').onclick()}"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{$('bCamp').onclick()}"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{$('bCampGo').onclick()}"); await pg.wait_for_timeout(4500)
        r['reino_volta'] = await pg.evaluate(ST)
        # «Continuar (da nuvem)» com só o reino na nuvem: não aparece e não mexe no reino
        r['continuar_nuvem'] = await pg.evaluate("async()=>{running=false;localStorage.removeItem(normalSaveKey());const b=$('bCont');delete b.dataset.cloud;await cloudCheck();return b.dataset.cloud||'nao'}")
        # telemóvel sem o reino: recupera da nuvem; cópia mais atrasada na nuvem é ignorada
        r['recupera'] = await pg.evaluate("""async()=>{const t0=reinoScore(localStorage.getItem(reinoKey()));localStorage.removeItem(reinoKey());localStorage.removeItem(reinoMetaKey());
          const ok=await reinoCloudSync();return{ok,igual:reinoScore(localStorage.getItem(reinoKey()))>0,tem:reinoHas()}}""")
        r['ignora_atrasada'] = await pg.evaluate("""async()=>{const cur=JSON.parse(localStorage.getItem(reinoKey()));const old=JSON.parse(JSON.stringify(cur));old.G.time=1;await cloudPut('reino',old);
          cur.G.time+=500;localStorage.setItem(reinoKey(),JSON.stringify(cur));const ch=await reinoCloudSync();return{mudou:ch,tempo:JSON.parse(localStorage.getItem(reinoKey())).G.time===cur.G.time}}""")
        # gravação mais avançada feita sem sessão (chave base) é recuperada quando a sessão volta
        r['juntar'] = await pg.evaluate("""()=>{const cur=JSON.parse(localStorage.getItem(reinoKey()));const adv=JSON.parse(JSON.stringify(cur));adv.X.reino.n=(adv.X.reino.n||0)+2;
          localStorage.setItem('alv_reino_v1',JSON.stringify(adv));localStorage.removeItem('alv_reino_v1__dono');reinoMerge();return{n:JSON.parse(localStorage.getItem(reinoKey())).X.reino.n===adv.X.reino.n,chave:reinoKey()}}""")
        r['sem_sessao'] = await pg.evaluate("()=>{ACC.user=null;const k=reinoKey();ACC.user={id:'u1'};return k}")
        r['erros_jogo'] = await pg.evaluate("ERRLOG.map(e=>e.m.split('\\n')[0])"); r['erros_pagina'] = pe
        a, v = r['reino_antes'], r['reino_volta']
        ok = v['reino'] and v['casas'] == a['casas'] and v['t'] >= a['t'] - 1 and r['nuvem_depois_sair_reino']['reino'] and r['nuvem_normal_guardada'] == {'reino': True, 'normal': True} \
             and r['nuvem_normal_acabada'] == {'reino': True, 'normal': False} and r['continuar_nuvem'] == 'nao' and r['recupera']['ok'] and r['recupera']['tem'] \
             and not r['ignora_atrasada']['mudou'] and r['ignora_atrasada']['tempo'] and r['juntar']['n'] and r['sem_sessao'] == 'alv_reino_v1_u1' and not r['erros_jogo'] and not pe
        print(json.dumps(r, ensure_ascii=False)); json.dump(r, open(OUT + '/reino_save.json', 'w'), ensure_ascii=False, indent=1)
        print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
