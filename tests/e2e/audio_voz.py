# Áudio do conselheiro: volume próprio (guardado no aparelho), voz desligada não descodifica nada,
# as 23 falas existem e são descodificadas só quando são precisas; limite de sons simultâneos.
# Uso: python3 -m http.server 8777 --directory www  e depois  python3 tests/e2e/audio_voz.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg = await br.new_page(viewport={'width': 915, 'height': 412}); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(3500)
        await pg.mouse.click(400, 200)
        r = await pg.evaluate("""async()=>{startGame(5,{map:'rios',vic:'classico'});try{tutEnd(true)}catch(e){};audioInit();const out={falas:Object.keys(VOZ.data).length,descodificadas_inicio:VOZ.buf.size};
          VOZ.on=false;voz('construido',true);out.desligada_descodificou=VOZ.buf.size;VOZ.on=true;
          let gain=null;const og=AUD.ctx.createGain.bind(AUD.ctx);AUD.ctx.createGain=()=>{const g=og();gain=g;return g};
          AUD.vol.voz=.3;voz('construido',true);await new Promise(f=>setTimeout(f,900));out.ganho_com_volume_30=gain?Math.round(gain.gain.value*100)/100:null;AUD.ctx.createGain=og;
          out.descodificadas_depois=VOZ.buf.size;audioSave();AUD.vol.voz=.9;audioLoad();out.volume_guardado=AUD.vol.voz;out.slider=document.getElementById('vVoz')?true:false;
          out.max_vozes=typeof AUD_MAXV!=='undefined'?AUD_MAXV:null;return out}""")
        r['erros'] = pe
        ok = r['falas'] == 23 and r['descodificadas_inicio'] == 0 and r['desligada_descodificou'] == 0 and r['ganho_com_volume_30'] is not None and abs(r['ganho_com_volume_30'] - 0.35) < 0.02 and r['descodificadas_depois'] == 1 and abs(r['volume_guardado'] - 0.3) < 1e-6 and r['slider'] and not pe
        print(json.dumps(r)); json.dump(r, open(OUT + '/audio_voz.json', 'w'))
        print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
