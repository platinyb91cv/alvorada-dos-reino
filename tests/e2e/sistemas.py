# Sistemas: impostos/felicidade/sustento, melhorias de edifícios, evolução das idades, reparação pelo jogador,
# campanha (todas as missões arrancam e correm), sobrevivência (vagas chegam) e gravação/carregamento com a economia.
# Uso: python3 -m http.server 8777 --directory www  e depois  python3 tests/e2e/sistemas.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
NEW = "startGame(SEED,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[1]=null;AI=null;try{tutEnd(true)}catch(e){};"
def js(seed, body): return "()=>{" + NEW.replace('SEED', str(seed)) + "const run=s=>{for(let t=0;t<s*30;t++)step(1/30)};" + body + "}"
CASES = {
 'impostos': js(11, """const e=econOf(0);const r0=econRates(0);const g0=P[0].res.gold;
   EXEC.tax(0,{v:4});const rAlto=econRates(0);EXEC.tax(0,{v:0});const rIsento=econRates(0);EXEC.tax(0,{v:2});
   // rendimento: imposto Normal com N aldeões
   const vil=rAlto.vil;e.hap=60;const gA=P[0].res.gold;run(60);const ganho=P[0].res.gold-gA;
   return {taxas:[0,1,2,3,4].map(v=>TAX_G[v]),alvo_alto:rAlto.target,alvo_isento:rIsento.target,aldeoes:vil,ouro_1min:Math.round(ganho*10)/10,esperado:Math.round(vil*TAX_G[2]*10)/10}"""),
 'felicidade': js(12, """const e=econOf(0);EXEC.tax(0,{v:4});P[0].res.food=0;e.hap=60;run(90);const h90=e.hap;const vs0=ents.filter(u=>u.o===0&&u.type==='aldeao').length;
   for(let i=0;i<6;i++)mkUnit(0,'aldeao',G.starts[0].x+2+i*.5,G.starts[0].y+3);recount();const n0=ents.filter(u=>u.o===0&&u.type==='aldeao').length;e.hap=10;P[0].res.food=0;run(130);const n1=ents.filter(u=>u.o===0&&u.type==='aldeao').length;
   const m_baixa=(e.hap=30,hapMult(0)),m_alta=(e.hap=80,hapMult(0)),m_normal=(e.hap=55,hapMult(0));
   e.hap=10;for(const u of ents.filter(u=>u.o===0&&u.type==='aldeao').slice(3))kill(u);recount();run(130);const n2=ents.filter(u=>u.o===0&&u.type==='aldeao').length;
   return {desceu_com_fome_e_imposto:Math.round(h90),partiram:n0-n1,minimo_mantido:n2,mult:[m_baixa,m_normal,m_alta]}"""),
 'sustento': js(13, """const h=G.starts[0];for(let i=0;i<20;i++)mkUnit(0,'aldeao',h.x+2+(i%5)*.6,h.y+3+(i/5|0)*.6);for(let i=0;i<10;i++)mkUnit(0,'guerreiro',h.x-2+(i%5)*.6,h.y+5+(i/5|0)*.6);
   for(let i=0;i<8;i++){const x=h.x+6+(i%4)*2,y=h.y-6+(i/4|0)*2;if(canPlace('casa',x,y,0,0,true))mkBld(0,'casa',x,y,true)}recount();EXEC.tax(0,{v:0});
   const r=econRates(0);for(const u of ents)if(u.o===0&&u.kind==='u')stopUnit(u);P[0].res.food=1000;P[0].res.gold=1000;run(60);
   return {pop:P[0].pop,comida_por_min:Math.round(r.food*10)/10,esperado_comida:Math.round(Math.max(0,P[0].pop-10)*2.4*10)/10,soldo_por_min:Math.round(r.soldo*10)/10,comida_restante:Math.round(P[0].res.food),ouro_restante:Math.round(P[0].res.gold),ia_isenta:(()=>{AIs[1]=mkAI(1,DIFF[1]);const x=!econOn(1);AIs[1]=null;return x})()}"""),
 'melhorias': js(14, """const h=G.starts[0];P[0].age=2;for(const k of KINDS)P[0].res[k]=9000;const c=ents.find(e=>e.o===0&&e.type==='centro');
   let sp=null;for(let r=3;r<12&&!sp;r++)for(let a=0;a<16&&!sp;a++){const x=Math.round(h.x+Math.cos(a/16*6.28)*r),y=Math.round(h.y+Math.sin(a/16*6.28)*r);if(canPlace('casa',x,y,0,0,true))sp={x,y}}
   const casa=mkBld(0,'casa',sp.x,sp.y,true);recount();const cap0=P[0].popCap;const ok1=queueUpgrade(casa,true);run(bLvl('casa',2)?120:1);recount();const cap1=P[0].popCap;
   const hp1=c.max;queueUpgrade(c,true);run(200);queueUpgrade(c,true);run(260);
   return {casa_nivel:casa.lvl||1,pop_extra:cap1-cap0,centro_nivel:c.lvl||1,vida_centro:[hp1,c.max],castelo:castleTop(c)}"""),
 'idade_nao_muda_edificios': js(15, """const c=ents.find(e=>e.o===0&&e.type==='centro');for(const k of KINDS)P[0].res[k]=9000;queueAge(c,true);run(AGE_TIME[1]+2);queueAge(c,true);run(AGE_TIME[2]+2);
   return {idade:P[0].age,nivel_centro:c.lvl||1,aspeto_idade:bAge(c),castelo:castleTop(c)}"""),
 'reparacao_jogador': js(16, """const h=G.starts[0];const c=ents.find(e=>e.o===0&&e.type==='centro');c.hp=c.max*.3;const v=ents.find(e=>e.o===0&&e.type==='aldeao');orderBuild(v,c);run(40);
   return {vida:Math.round(c.hp/c.max*100),estado:v.state}"""),
 'combate_basico': js(17, """const h=G.starts[0];const q=ents.find(e=>e.o===1&&e.type==='centro');const m=centerOf(q);const x0=(h.x+m.x)/2,y0=(h.y+m.y)/2;const a=mkUnit(0,'lanceiro',x0,y0),a2=mkUnit(0,'lanceiro',x0,y0+.6),b=mkUnit(1,'cavaleiro',x0+.6,y0);orderAttack(a,b);orderAttack(a2,b);orderAttack(b,a);run(25);
   return {custo:'2 lanceiros (120) contra 1 cavalaria (125)',lanceiro_vivo:!a.dead||!a2.dead,cavaleiro_vivo:!b.dead}"""),
 'gravar_carregar': js(18, """const e=econOf(0);EXEC.tax(0,{v:3});e.hap=42.5;const c=ents.find(x=>x.o===0&&x.type==='centro');c.lvl=2;run(5);const A=JSON.stringify({tax:e.tax,hap:Math.round(e.hap*100),n:ents.length,lvl:c.lvl});
   const r=saveGame(true);loadGame();const e2=econOf(0);const c2=ents.find(x=>x.o===0&&x.type==='centro');const B=JSON.stringify({tax:e2.tax,hap:Math.round(e2.hap*100),n:ents.length,lvl:c2.lvl});return {gravou:r.ok,igual:A===B,antes:A,depois:B}"""),
}
CAMPAIGN = """()=>{const out=[];for(let i=0;i<CAMP.length;i++){try{ERRLOG.length=0;campStart(i);try{tutEnd(true)}catch(e){};for(let t=0;t<90*30&&!G.over;t++)step(1/30);
  const objs=(CAMP[i].objs||[]).map(o=>{try{return !!o[1]()}catch(e){return 'erro'}});out.push({i,t:CAMP[i].t,erros:ERRLOG.length,objs_ok:!objs.includes('erro'),comida:Math.round(P[0].res.food),felic:Math.round(econOf(0).hap)})}catch(e){out.push({i,t:CAMP[i]&&CAMP[i].t,falhou:String(e).slice(0,120)})}}return out}"""
SURV = """()=>{startGame(31,{map:'continental',vic:'sobrevivencia',civ:['planicies','planicies']});try{tutEnd(true)}catch(e){};let maxE=0,first=null;
  for(let t=0;t<8*60*30;t++){step(1/30);if(t%30===0){const n=ents.filter(e=>e.kind==='u'&&e.o===1&&e.d.mil).length;if(n>0&&first==null)first=Math.round(t/30);maxE=Math.max(maxE,n)}if(G.over)break}
  return {primeira_vaga_s:first,max_inimigos:maxE,terminou:!!G.over,erros:ERRLOG.length}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 915, 'height': 412}); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(4000)
        r = {}
        for k, code in CASES.items(): r[k] = await pg.evaluate(code)
        r['campanha'] = await pg.evaluate(CAMPAIGN)
        r['sobrevivencia'] = await pg.evaluate(SURV)
        r['erros_pagina'] = pe
        I, F, S, M = r['impostos'], r['felicidade'], r['sustento'], r['melhorias']
        ok = {
          'impostos': I['alvo_alto'] < I['alvo_isento'] and abs(I['ouro_1min'] - I['esperado']) <= max(1.5, I['esperado'] * .15),
          'felicidade': F['desceu_com_fome_e_imposto'] < 40 and F['partiram'] >= 1 and F['minimo_mantido'] >= 3 and F['mult'] == [0.85, 1, 1.1],
          'sustento': abs(S['comida_por_min'] - S['esperado_comida']) < .5 and S['soldo_por_min'] == 7.0 and S['comida_restante'] < 1000 and S['ia_isenta'],
          'melhorias': M['casa_nivel'] == 2 and M['pop_extra'] == 3 and M['centro_nivel'] == 3 and M['vida_centro'][1] > M['vida_centro'][0] and M['castelo'],
          'idade_nao_muda_edificios': r['idade_nao_muda_edificios']['idade'] == 2 and r['idade_nao_muda_edificios']['nivel_centro'] == 1 and not r['idade_nao_muda_edificios']['castelo'],
          'reparacao_jogador': r['reparacao_jogador']['vida'] >= 60,
          'combate_basico': r['combate_basico']['lanceiro_vivo'] and not r['combate_basico']['cavaleiro_vivo'],
          'gravar_carregar': r['gravar_carregar']['gravou'] and r['gravar_carregar']['igual'],
          'campanha': len(r['campanha']) > 0 and all(('falhou' not in c) and c['erros'] == 0 and c['objs_ok'] for c in r['campanha']),
          'sobrevivencia': r['sobrevivencia']['primeira_vaga_s'] is not None and r['sobrevivencia']['erros'] == 0,
          'sem_erros': not pe}
        r['ok'] = ok
        print(json.dumps(r, ensure_ascii=False)); json.dump(r, open(OUT + '/sistemas.json', 'w'), ensure_ascii=False, indent=1)
        print('PASS' if all(ok.values()) else 'FAIL ' + ','.join(k for k, v in ok.items() if not v)); await br.close(); sys.exit(0 if all(ok.values()) else 1)
asyncio.run(main())
