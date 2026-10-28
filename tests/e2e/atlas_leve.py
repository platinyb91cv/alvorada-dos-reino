# Atlas leves e libertação de memória: a aldeia desenha-se igual (paliçada, portão de madeira, muralha e portão de pedra,
# quinta, ruínas) com os atlas aparados; o rei de bronze só carrega quando alguém chega ao Bronze; o rei de pedra e as
# máquinas raras saem da memória quando deixam de aparecer e voltam a carregar quando são precisas; a folha 2D só para o sacerdote.
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 1100, 'height': 620}, device_scale_factor=2); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)))
        await pg.goto('http://localhost:8777/index.html'); await pg.wait_for_timeout(5000)
        await pg.evaluate("startGame(31,{map:'continental',vic:'classico',civ:['planicies','mar']})"); await pg.wait_for_timeout(2500)
        await pg.add_style_tag(content='#sLogin,#menuBg{display:none!important}')
        r = {}
        r['inicio'] = await pg.evaluate("()=>({bart:BART.ready,bronze:BRONZE_ART.ready,anim:ANIM.ready,bldart:BLDART.ready,gate:GATE3D.ready,wall:WALL3D.ready,ficheiros:[BLDART.img&&BLDART.img.src.split('/').pop(),GATE3D_DATA.file,WALL3D_DATA.file]})")
        r['aldeia'] = await pg.evaluate("""()=>{AIs=[null,null];AI=null;const s=G.starts[0],x0=Math.round(s.x)+6,y0=Math.round(s.y)-4,out=[];
          const put=(t,x,y)=>{const b=__alv.placeAt(0,t,x,y);out.push(b?t:'falhou '+t);return b};
          for(let i=0;i<4;i++)put('muralhaMadeira',x0+i,y0);put('portaoMadeira',x0+4,y0);for(let i=0;i<3;i++)put('muralhaMadeira',x0+7+i,y0);
          for(let i=0;i<4;i++)put('muralhaPedra',x0+i,y0+3);put('portaoPedra',x0+4,y0+3);for(let i=0;i<3;i++)put('muralhaPedra',x0+7+i,y0+3);
          put('quinta',x0,y0+6);const c=put('casa',x0+5,y0+6);if(c)kill(c)
          cam.z=1.25;centerCam(x0+5,y0+4);return out}""")
        await pg.wait_for_timeout(3000)
        await pg.screenshot(path=OUT + '/atlas_leve.png')
        r['desenho'] = await pg.evaluate("""()=>{const s=t=>{const b=ents.find(e=>e.kind==='b'&&e.type===t);return b?bldSprite(t,P[0].age,0,bldVariant(b)):null};
          return{palicada:!!s('muralhaMadeira'),portaoMadeira:!!s('portaoMadeira'),muralhaPedra:!!s('muralhaPedra'),portaoPedra:!!s('portaoPedra'),quinta:!!s('quinta'),
            ruina:fx.some(f=>f.type==='rubble'),erros:ERRLOG.length}}""")
        # reis: o de bronze só quando alguém chega ao Bronze; o de pedra sai quando ninguém está na Pedra
        r['bronze_antes'] = await pg.evaluate("BRONZE_ART.ready")
        await pg.evaluate("()=>{P[0].age=1;P[1].age=1;kingAtlasForAge(1)}"); await pg.wait_for_timeout(2500)
        r['reis'] = await pg.evaluate("""()=>{const a=BRONZE_ART.ready;G.agc=-99;G.time+=11;atlasGC();G.time+=41;G.agc=-99;atlasGC();return{bronze:a,pedra_libertado:!BART.ready&&!BART.img}}""")
        await pg.evaluate("()=>{P[0].age=0;kingAtlasForAge(0)}"); await pg.wait_for_timeout(2000)
        r['pedra_volta'] = await pg.evaluate("BART.ready")
        # máquina rara: carrega quando aparece, sai 60 s depois de desaparecer, volta quando é precisa
        await pg.evaluate("()=>{const s=G.starts[0];window.__t=mkUnit(0,'trebuchet',s.x+3,s.y+3);u3ready(UNIT3D.trebuchet)}"); await pg.wait_for_timeout(2500)
        r['trebuchet'] = await pg.evaluate("""()=>{const a=UNIT3D.trebuchet.ready;G.agc=-99;G.time+=11;atlasGC();const u=__t;u.hp=0;u.dead=true;const i=ents.indexOf(u);if(i>=0)ents.splice(i,1);byId.delete(u.id);
          for(const f of fx)if(f.ut==='trebuchet')f.ut=null;G.time+=61;G.agc=-99;atlasGC();return{carregado:a,libertado:!UNIT3D.trebuchet.ready&&!UNIT3D.trebuchet.img}}""")
        await pg.evaluate("()=>u3ready(UNIT3D.trebuchet)"); await pg.wait_for_timeout(2000)
        r['trebuchet_volta'] = await pg.evaluate("UNIT3D.trebuchet.ready")
        r['sacerdote'] = await pg.evaluate("()=>{const s=G.starts[0];mkUnit(0,'sacerdote',s.x+2,s.y+2);G.agc=-99;G.time+=11;atlasGC();return 'pedido'}")
        await pg.wait_for_timeout(2500); r['anim'] = await pg.evaluate("ANIM.ready")
        r['erros_jogo'] = await pg.evaluate("ERRLOG.map(e=>e.m.split('\\n')[0])"); r['erros_pagina'] = pe
        d = r['desenho']; ok = all(d[k] for k in ['palicada','portaoMadeira','muralhaPedra','portaoPedra','quinta','ruina']) and not r['inicio']['bronze'] and not r['inicio']['anim'] \
            and r['reis']['bronze'] and r['reis']['pedra_libertado'] and r['pedra_volta'] and r['trebuchet']['carregado'] and r['trebuchet']['libertado'] and r['trebuchet_volta'] and r['anim'] \
            and not r['erros_jogo'] and not pe and 'falhou' not in ' '.join(r['aldeia'])
        print(json.dumps(r, ensure_ascii=False)); json.dump(r, open(OUT + '/atlas_leve.json', 'w'), ensure_ascii=False, indent=1)
        print('PASS' if ok else 'FAIL'); await br.close(); sys.exit(0 if ok else 1)
asyncio.run(main())
