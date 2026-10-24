# Medição de desempenho tipo telemóvel: CPU 4x mais lenta, ecrã 900x420 com DPR 2, batalha com unidades 3D de vários tipos.
# Mostra ms por frame (média e p95), memória JS e as funções que mais gastam (perfil de CPU).
import asyncio, json, sys
from playwright.async_api import async_playwright
THR = float(sys.argv[1]) if len(sys.argv) > 1 else 4
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--enable-precise-memory-info'])
        ctx = await br.new_context(viewport={'width': 900, 'height': 420}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(3500)
        await pg.evaluate("startGame(4242,{map:'rios',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        await pg.evaluate("""()=>{const c=ents.find(e=>e.type==='centro'&&e.o===ME);const q=centerOf(c);P[ME].age=2;P[1].age=2;
          const T=['guerreiro','espadachim','lanceiro','arqueiro','besteiro','cavaleiro','cavPesada','cavArqueira','catapulta','ariete','aldeao','carrocaCarga'];
          let k=0;for(let i=0;i<36;i++){const t=T[i%T.length];const a=mkUnit(ME,t,q.x+3+(i%6),q.y+4+(i/6|0));const b=mkUnit(1,t,q.x+10+(i%6),q.y+4+(i/6|0));orderAttack&&orderAttack(a,b)}
          for(const t of ['casa','quartel','armazem','torre','casa','arquearia']){for(let r=4;r<30;r++){let ok=false;for(let a=0;a<24&&!ok;a++){const tx=Math.round(q.x+Math.cos(a/24*6.28)*r),ty=Math.round(q.y+Math.sin(a/24*6.28)*r);if(canPlace(t,tx,ty,1,0,true)){mkBld(1,t,tx,ty,true);ok=true}}if(ok)break}}
          cam.z=1.3;centerCam(q.x+8,q.y+6)}""")
        await pg.wait_for_timeout(4000)  # aquecer caches
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': THR})
        await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', {'interval': 500}); await cdp.send('Profiler.start')
        r = await pg.evaluate("""()=>new Promise(res=>{const d=[];let l=performance.now();const t0=l;function f(t){d.push(t-l);l=t;if(t-t0<15000)requestAnimationFrame(f);else{d.sort((a,b)=>a-b);res({n:d.length,avg:d.reduce((a,b)=>a+b,0)/d.length,p95:d[Math.floor(d.length*.95)],heap:performance.memory?Math.round(performance.memory.usedJSHeapSize/1e6):null,units:ents.filter(e=>e.kind==='u').length,dpr:DPR})}}requestAnimationFrame(f)})""")
        prof = (await cdp.send('Profiler.stop'))['profile']
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 1})
        nodes = {n['id']: n for n in prof['nodes']}; self_t = {}
        dts = prof['timeDeltas']; samples = prof['samples']
        for s, dt in zip(samples, dts):
            n = nodes[s]; k = n['callFrame']['functionName'] or '(anon)'; self_t[k] = self_t.get(k, 0) + dt
        par = {}
        for n in prof['nodes']:
            for ch in n.get('children', []): par[ch] = n['id']
        callers = {}
        for s_, dt in zip(samples, dts):
            n = nodes[s_]; k = n['callFrame']['functionName']
            if k in ('fill', 'drawImage', 'restore', 'stroke', 'fillRect', 'putImageData', 'getImageData'):
                q = nodes.get(par.get(s_)); cf = q['callFrame'] if q else {}
                kk = k + '<-' + (cf.get('functionName') or '(anon)') + ':' + str(cf.get('lineNumber', 0) + 1); callers[kk] = callers.get(kk, 0) + dt
        tot = sum(self_t.values())
        top = sorted(self_t.items(), key=lambda x: -x[1])[:18]
        r['top'] = [(k, round(v / tot * 100, 1)) for k, v in top]; r['errs'] = errs; r['callers'] = [(k, round(v / tot * 100, 1)) for k, v in sorted(callers.items(), key=lambda x: -x[1])[:12]]
        print(json.dumps(r, indent=1)); await br.close()
asyncio.run(main())
