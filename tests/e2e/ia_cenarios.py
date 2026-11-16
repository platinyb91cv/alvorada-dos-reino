# Cenários da IA (decisões): melhorias de edifícios até ao castelo, ameaça longe do Centro, reparação abaixo de 60%,
# recuo em desvantagem, avaliação de forças antes de atacar, Maravilha (Difícil) e diferença entre dificuldades.
# Uso: servidor em http://localhost:8777 (python3 -m http.server 8777 --directory www) e depois: python3 tests/e2e/ia_cenarios.py [pasta]
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
SETUP = """([d,seed])=>{startGame(seed,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[0]=null;AIs[1]=mkAI(1,DIFF[d]);AI=AIs[1];
  AI.nextAttack=1e9;AI.raided=true;window.__h=()=>{const c=ents.find(e=>e.o===1&&e.type==='centro');return centerOf(c)};window.__run=s=>{for(let t=0;t<s*30;t++)step(1/30)};return true}"""
CASES = {
 # 1) melhorias: com recursos e Idade do Ferro, a IA melhora o Centro até ao Nv.3 (castelo) e outros edifícios
 'melhorias': """()=>{P[1].age=2;for(const k of KINDS)P[1].res[k]=5000;__run(420);const bl=ents.filter(e=>e.o===1&&e.kind==='b');const c=bl.find(b=>b.type==='centro');
   return {centro:c.lvl||1,nivel2mais:bl.filter(b=>(b.lvl||1)>=2).length,castelo:castleTop(c),vidaCentro:Math.round(c.max),ups:AIs[1].ups||0}}""",
 # 2) ameaça longe do Centro: inimigos atacam um armazém a ~20 casas; a IA reage em poucos segundos com a força necessária (não o exército todo)
 'ameaca_longe': """()=>{const h=__h();P[1].age=1;let spot=null;for(let r=18;r<26&&!spot;r++)for(let a=0;a<32&&!spot;a++){const x=Math.round(h.x+Math.cos(a/32*6.28)*r),y=Math.round(h.y+Math.sin(a/32*6.28)*r);if(canPlace('armazem',x,y,1,0,true))spot={x,y}}
   const b=mkBld(1,'armazem',spot.x,spot.y,true);for(let i=0;i<12;i++)mkUnit(1,'espadachim',h.x+2+(i%4),h.y+3+(i/4|0));
   const foes=[];for(let i=0;i<3;i++){const f=mkUnit(0,'guerreiro',spot.x-1+i,spot.y-1);orderAttack(f,b);foes.push(f)}
   let resp=null,maxDef=0;for(let s=0;s<40;s++){__run(1);const d=ents.filter(e=>e.o===1&&e.kind==='u'&&e.d.mil&&e.state==='attack'&&foes.includes(e.target)).length;if(d>=2&&resp==null)resp=s+1;maxDef=Math.max(maxDef,d)}
   return {dist:Math.round(hyp(spot.x-h.x,spot.y-h.y)),resposta_s:resp,defensores_max:maxDef,de_12:12,inimigos_vivos:foes.filter(f=>!f.dead).length}}""",
 # 3) reparação: edifício a 40% sem perigo → aldeões reparam acima de 60%
 'reparacao': """()=>{__run(60);const b=ents.find(e=>e.o===1&&e.type==='casa'&&e.done)||ents.find(e=>e.o===1&&e.type==='centro');b.hp=b.max*.4;__run(90);
   return {tipo:b.type,vida:Math.round(b.hp/b.max*100),reparacoes:AIs[1].reps||0}}""",
 # 4) recuo: grupo de ataque pequeno vê um exército muito maior → recua antes de ser destruído
 'recuo': """()=>{const h=__h();P[1].age=1;const tx=h.x-24,ty=h.y;const mine=[];for(let i=0;i<6;i++)mine.push(mkUnit(1,'guerreiro',tx+4+(i%3)*.8,ty+(i/3|0)*.8));
   for(let i=0;i<18;i++)mkUnit(0,'espadachim',tx-6+(i%6)*.8,ty-1+(i/6|0)*.8);AIs[1].attacking=true;groupMove(mine,tx-8,ty,true,'livre');
   const d0=hyp(mine[0].x-h.x,mine[0].y-h.y);__run(8);return {recuos:AIs[1].retreats||0,vivos_8s:mine.filter(u=>!u.dead).length,de:6,recuou_casas:Math.round(d0-Math.min(...mine.filter(u=>!u.dead).map(u=>hyp(u.x-h.x,u.y-h.y))))}}""",
 # 5) avaliação: não ataca com exército fraco contra um forte; ataca quando é mais forte
 'avaliacao': """()=>{const h=__h();const A=AIs[1];for(let i=0;i<4;i++)mkUnit(1,'guerreiro',h.x+3+i,h.y+3);const e0=ents.find(e=>e.o===0&&e.type==='centro');const q=centerOf(e0);
   const big=[];for(let i=0;i<20;i++)big.push(mkUnit(0,'espadachim',q.x+3+(i%5),q.y+3+(i/5|0)));const army=ents.filter(e=>e.o===1&&e.kind==='u'&&e.d.mil);
   const fraco=aiCanAttack(A,1,0,army,DIFF[1]);for(const u of big)kill(u);for(let i=0;i<20;i++)mkUnit(1,'espadachim',h.x+3+(i%5),h.y+5+(i/5|0));
   const army2=ents.filter(e=>e.o===1&&e.kind==='u'&&e.d.mil);const forte=aiCanAttack(A,1,0,army2,DIFF[1]);const facil=aiCanAttack(A,1,0,army,DIFF[0]);return {ataca_fraco:fraco,ataca_forte:forte,facil_nao_avalia:facil}}""",
}
WONDER = """()=>{startGame(77,{map:'continental',vic:'classico',civ:['planicies','planicies']});AIs[0]=null;AIs[1]=mkAI(1,DIFF[2]);AI=AIs[1];AI.nextAttack=1e9;AI.raided=true;
  const h=centerOf(ents.find(e=>e.o===1&&e.type==='centro'));P[1].age=2;AI.t=1300;for(let i=0;i<20;i++)mkUnit(1,'aldeao',h.x+3+(i%5),h.y+4+(i/5|0));for(let i=0;i<8;i++)mkUnit(1,'espadachim',h.x-3+(i%4),h.y+4+(i/4|0));
  for(const k of KINDS)P[1].res[k]=2500;for(let t=0;t<240*30;t++)step(1/30);const w=ents.find(e=>e.o===1&&e.type==='maravilha');return {maravilha:!!w,progresso:w?Math.round(w.prog*100):0,construtores:w?ents.filter(v=>v.o===1&&v.state==='build'&&v.bld===w).length:0}}"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={'width': 915, 'height': 412}); pe = []
        pg.on('pageerror', lambda e: pe.append(str(e)[:200]))
        await pg.goto('http://localhost:8777/index.html?bot=teste'); await pg.wait_for_timeout(4000)
        r = {}
        for k, js in CASES.items():
            d = 0 if k == 'facil' else 1
            await pg.evaluate(SETUP, [d, 900 + len(r)]); r[k] = await pg.evaluate(js)
        r['maravilha'] = await pg.evaluate(WONDER)
        r['erros_pagina'] = pe
        ok = {
          'melhorias': r['melhorias']['centro'] == 3 and r['melhorias']['castelo'] and r['melhorias']['nivel2mais'] >= 3,
          'ameaca_longe': r['ameaca_longe']['dist'] >= 15 and r['ameaca_longe']['resposta_s'] is not None and r['ameaca_longe']['resposta_s'] <= 5 and r['ameaca_longe']['defensores_max'] < 12 and r['ameaca_longe']['inimigos_vivos'] == 0,
          'reparacao': r['reparacao']['vida'] >= 60 and r['reparacao']['reparacoes'] >= 1,
          'recuo': r['recuo']['recuos'] >= 1 and r['recuo']['vivos_8s'] >= 5 and r['recuo']['recuou_casas'] >= 6,
          'avaliacao': (not r['avaliacao']['ataca_fraco']) and r['avaliacao']['ataca_forte'] and r['avaliacao']['facil_nao_avalia'],
          'maravilha': r['maravilha']['maravilha'] and (r['maravilha']['progresso'] >= 100 or r['maravilha']['construtores'] >= 4),
          'sem_erros': not pe}
        r['ok'] = ok
        print(json.dumps(r, ensure_ascii=False)); json.dump(r, open(OUT + '/ia_cenarios.json', 'w'), ensure_ascii=False, indent=1)
        print('PASS' if all(ok.values()) else 'FAIL ' + ','.join(k for k, v in ok.items() if not v)); await br.close(); sys.exit(0 if all(ok.values()) else 1)
asyncio.run(main())
