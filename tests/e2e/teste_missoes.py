# Teste automático de TODAS as missões: Campanha (6) e O meu Reino (capítulos 0-15, todos os tipos).
# Para cada missão: começa, cumpre os objetivos (atalhos de teste), corre a simulação e confirma a vitória,
# o progresso gravado e que não há erros. Também testa derrotas, gravar/continuar e o botão Guardar.
import asyncio, json, sys
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8777/index.html'
HELP = r"""()=>{window.QA={errs:[],
 run(sec){const n=Math.round(sec/0.1);for(let i=0;i<n;i++){try{step(0.1)}catch(e){QA.errs.push(String(e&&e.stack||e).slice(0,400));break}}},
 home(){const tc=ents.find(e=>e.o===0&&e.kind==='b'&&e.type==='centro');return tc?centerOf(tc):G.starts[0]},
 place(o,type,n,at){let k=0;const c=at||QA.home();for(let r=3;r<45&&k<n;r++)for(let a=0;a<28&&k<n;a++){const tx=Math.round(c.x+Math.cos(a/28*6.283)*r),ty=Math.round(c.y+Math.sin(a/28*6.283)*r);if(canPlace(type,tx,ty,o,0,true)){mkBld(o,type,tx,ty,true);k++}}recount();return k},
 spawn(o,type,n){const c=QA.home(),us=[];for(let i=0;i<n;i++){const u=mkUnit(o,type,c.x+2.5+(i%6)*.55,c.y+2.5+Math.floor(i/6)*.55);us.push(u)}recount();return us},
 killId(id,src){const e=byId.get(id);if(e&&!e.dead)applyDmg(e,1e7,src||null,false)},
 kill(e,src){if(e&&!e.dead)applyDmg(e,1e7,src||null,false)},
 our(){return ents.find(e=>e.o===0&&e.kind==='u'&&e.d.mil)||ents.find(e=>e.o===0&&e.kind==='u')},
 st(){return{over:G.over,won:G.won,end:!$('sEnd').hidden,title:$('endTitle').textContent,text:$('endText').textContent,running,camp:G.camp,
   reino:G.reino?{n:G.reino.n,ms:G.reino.ms?{k:G.reino.ms.k,n:G.reino.ms.n,objs:reinoObjs(G.reino.ms)}:null}:null,
   objs:G.camp!=null&&CAMP[G.camp]?campObjs():null}}};
 const oe=window.onerror;window.addEventListener('error',ev=>QA.errs.push('onerror '+ev.message));return true}"""
CAMP_SOLVE = {
0: r"""()=>{const n=12-cntU(0,'aldeao');QA.spawn(0,'aldeao',Math.max(0,n));QA.place(0,'casa',4);QA.place(0,'quartel',1);P[0].res.wood=Math.max(P[0].res.wood,300);return QA.st().objs}""",
1: r"""()=>{QA.spawn(0,'guerreiro',6);const me=QA.our();for(const w of ents.filter(e=>e.type==='lobo'))QA.kill(w,me);const extra=8-kills('lobo');for(let i=0;i<extra;i++){const w=mkUnit(2,'lobo',QA.home().x+6,QA.home().y+6);QA.kill(w,me)}P[0].age=1;recount();return QA.st().objs}""",
2: r"""()=>{QA.run(3);G.surv=G.surv||{wave:0,next:200};G.surv.wave=6;G.surv.next=9999;for(const e of ents.filter(e=>e.o===1&&e.kind==='u'))QA.kill(e);recount();return QA.st().objs}""",
3: r"""()=>{QA.place(0,'doca',1)||mkBld(0,'doca',Math.round(QA.home().x+4),Math.round(QA.home().y+4),true);QA.spawn(0,'transporte',1);G.time=Math.max(G.time,61);const me=QA.our();for(const e of ents.filter(e=>e.o===1&&e.type==='centro'))QA.kill(e,me);recount();return QA.st().objs}""",
4: r"""()=>{QA.run(4);const me=QA.our();for(const e of ents.filter(e=>e.o===1&&e.kind==='u'&&e.d.king))QA.kill(e,me);recount();return QA.st().objs}""",
5: r"""()=>{P[0].age=2;const k=QA.place(0,'maravilha',1);const w=ents.find(e=>e.o===0&&e.type==='maravilha');G.wonder={o:0,id:w.id,t:2};return [k,QA.st().objs]}""",
}
REINO_SOLVE = r"""(n)=>{const R=G.reino,m=R.ms;if(!m)return 'sem missão';const me=QA.our();
 if(m.k==='fund'){QA.spawn(0,'aldeao',Math.max(0,12-cntU(0,'aldeao')));QA.place(0,'casa',Math.max(0,4-cntB(0,'casa')));if(!cntB(0,'quartel'))QA.place(0,'quartel',1);P[0].res.wood=Math.max(P[0].res.wood,300)}
 if(m.k==='lobos'){QA.spawn(0,'guerreiro',6);for(const w of ents.filter(e=>e.type==='lobo'))QA.kill(w,me);const extra=8-kills('lobo');for(let i=0;i<extra;i++){const w=mkUnit(2,'lobo',QA.home().x+6,QA.home().y+6);QA.kill(w,me)}P[0].age=Math.max(P[0].age,1)}
 if(m.k==='raids'){QA.run(Math.max(1,(m.nx||0)+1));m.wv=m.waves;for(const id of m.ids||[])QA.killId(id,me)}
 if(m.k==='rival'||m.k==='rei'||m.k==='boss'||m.k==='fort'){for(const id of m.ids||[])QA.killId(id,me)}
 if(m.k==='maravilha'){P[0].age=2;if(!ents.some(e=>e.o===0&&e.type==='maravilha'))QA.place(0,'maravilha',1);R.wb=1;R.wok=1}
 if(m.k==='econ'){P[0].stats.gathered=(m.g0||0)+m.gather+1;const need=m.pop-P[0].pop;if(need>0){QA.place(0,'casa',Math.ceil(need/5)+2);QA.spawn(0,'aldeao',need+1)}}
 if(m.k==='cerco'){m.t0=G.time-m.secs-1;for(const e of ents.filter(e=>e.o===1&&e.kind==='u'))QA.kill(e,me);if(!cntB(0,'centro')){P[0].age=Math.max(P[0].age,1);QA.place(0,'centro',1);window.__reconstruiu=1}}
 recount();return reinoObjs(m)}"""

async def main():
    out = {'camp': [], 'campDerrota': None, 'reino': [], 'save': {}, 'erros': []}
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1280, 'height': 760})
        pg.on('pageerror', lambda e: out['erros'].append('pageerror ' + str(e)[:300]))
        async def boot():
            await pg.goto(URL); await pg.wait_for_timeout(2500)
            await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
            await pg.evaluate("()=>{try{localStorage.clear()}catch(e){}}"); await pg.evaluate(HELP)
        await boot()
        # ---------- Campanha ----------
        for i in range(6):
            await pg.evaluate(f"()=>{{campStart({i})}}"); await pg.wait_for_timeout(400); await pg.evaluate(HELP)
            await pg.evaluate("()=>QA.run(2)")
            objs = await pg.evaluate(CAMP_SOLVE[i])
            await pg.evaluate("()=>QA.run(3)"); await pg.wait_for_timeout(1500)
            st = await pg.evaluate("()=>({...QA.st(),done:campDone(),errs:QA.errs})")
            out['camp'].append({'missao': i + 1, 'objetivos': objs, 'resultado': st})
            print('CAMP', i + 1, st['won'], st['title'], st['done'], st['errs'][:1], flush=True)
        # derrota: regicídio com o próprio Rei morto
        await pg.evaluate("()=>{campStart(4)}"); await pg.wait_for_timeout(400); await pg.evaluate(HELP); await pg.evaluate("()=>QA.run(4)")
        await pg.evaluate("()=>{for(const e of ents.filter(e=>e.o===0&&e.kind==='u'&&e.d.king))QA.kill(e)}"); await pg.evaluate("()=>QA.run(2)"); await pg.wait_for_timeout(1500)
        out['campDerrota'] = await pg.evaluate("()=>QA.st()"); print('DERROTA', out['campDerrota']['title'], out['campDerrota']['text'][:60], flush=True)
        # ---------- Gravar / continuar a meio de uma missão ----------
        await pg.evaluate("()=>{campStart(1)}"); await pg.wait_for_timeout(400); await pg.evaluate(HELP); await pg.evaluate("()=>QA.run(3)")
        await pg.evaluate("()=>{QA.spawn(0,'guerreiro',3);const me=QA.our();const w=ents.filter(e=>e.type==='lobo').slice(0,2);for(const x of w)QA.kill(x,me)}")
        before = await pg.evaluate("()=>({camp:G.camp,k:kills('lobo'),time:Math.round(G.time),units:ents.filter(e=>e.o===0&&e.kind==='u').length})")
        await pg.evaluate("()=>{paused=true;$('sPause').hidden=false}")
        await pg.click('#bSave'); await pg.wait_for_timeout(300)
        vis = await pg.evaluate("""()=>{const t=[...document.querySelectorAll('#toast div')].map(d=>d.textContent);const d=document.querySelector('#toast div');let top=null;
          if(d){const r=d.getBoundingClientRect();const el=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);top=!!el&&(el===d||d.contains(el))}
          return{toasts:t,toastVisivelPorCima:top,botao:$('bSave').textContent,gravado:!!localStorage.getItem(SAVE_KEY)}}""")
        await pg.screenshot(path='/tmp/claude-0/missoes/guardar.png', clip={'x': 340, 'y': 0, 'width': 600, 'height': 420})
        await pg.reload(); await pg.wait_for_timeout(2500); await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        await pg.evaluate("()=>{$('bCont').click()}"); await pg.wait_for_timeout(1500); await pg.evaluate(HELP)
        after = await pg.evaluate("()=>({camp:G.camp,k:kills('lobo'),time:Math.round(G.time),units:ents.filter(e=>e.o===0&&e.kind==='u').length,running})")
        out['save'] = {'antes': before, 'ui': vis, 'depoisDeContinuar': after}; print('SAVE', json.dumps(out['save'])[:400], flush=True)
        # ---------- O meu Reino: capítulos 0..15 (todos os tipos) ----------
        await pg.evaluate("()=>{$('sPause').hidden=true;paused=false;reinoFound()}"); await pg.wait_for_timeout(600); await pg.evaluate(HELP)
        for n in range(16):
            await pg.evaluate("(n)=>{const R=G.reino;if(!R.ms){R.n=n;reinoStart(n)}}", n)
            await pg.evaluate("()=>QA.run(2)")
            objs = await pg.evaluate(REINO_SOLVE, n)
            await pg.evaluate("()=>QA.run(2.5)")
            st = await pg.evaluate("()=>({...QA.st(),errs:QA.errs.slice(-2),gl:G.reino.gl||0})")
            ok = st['reino'] and st['reino']['n'] == n + 1 and not st['over']
            out['reino'].append({'cap': n + 1, 'tipo': (await pg.evaluate("(n)=>reinoDef(n).k", n)), 'objetivos': objs, 'ok': ok, 'estado': st})
            print('REINO', n + 1, out['reino'][-1]['tipo'], 'OK' if ok else 'FALHOU', st['reino'], st['errs'][:1], flush=True)
            if st['over']: break
        # reino: queda e retoma do ponto de controlo
        await pg.evaluate("()=>{for(const e of ents.filter(e=>e.o===0&&e.kind==='u'&&e.d.king))QA.kill(e)}"); await pg.evaluate("()=>QA.run(2)"); await pg.wait_for_timeout(1500)
        out['reinoQueda'] = await pg.evaluate("()=>QA.st()"); print('QUEDA', out['reinoQueda']['title'], flush=True)
        out['errosFinais'] = await pg.evaluate("()=>QA.errs")
        await br.close()
    json.dump(out, open('/tmp/claude-0/missoes/resultado.json', 'w'), ensure_ascii=False, indent=1)
    print('ERROS', len(out['erros']), out['erros'][:3], out['errosFinais'][:3])
asyncio.run(main())
