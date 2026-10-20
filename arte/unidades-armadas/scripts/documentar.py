from pathlib import Path
import json,hashlib,subprocess,re,shutil
R=Path(__file__).resolve().parent;repo=R.parent/'alvorada-dos-reino';dest=repo/'arte/unidades-armadas';dest.mkdir(exist_ok=True)
units=['aldeao','guerreiro','lanceiro','espadachim','arqueiro','besteiro'];oldindex=subprocess.check_output(['git','show','HEAD:www/index.html'],cwd=repo);newindex=(repo/'www/index.html').read_bytes();tree=subprocess.check_output(['git','ls-tree','-rl','HEAD','www/assets'],cwd=repo,text=True);baseline_assets=sum(int(l.split()[3]) for l in tree.splitlines() if len(l.split())>=5);current_assets=sum(p.stat().st_size for p in (repo/'www/assets').rglob('*') if p.is_file());assert len(newindex)<len(oldindex)*1.1
grips=json.loads((R/'grip-directions.verification.json').read_text());assert all(x['passed'] for x in grips);shutil.copyfile(R/'grip-directions.verification.json',dest/'grip-directions.verification.json');shutil.copyfile(R/'aim.json',dest/'aim.verification.json')
rows=[];models=0;atlas=0
for u in units:
 p=json.loads((dest/(u+'.verification.json')).read_text());s=json.loads((dest/(u+'.stride.json')).read_text());m=json.loads((repo/'www/assets/units3d-armados'/(u+'.json')).read_text());models+=p['bytes'];atlas+=(repo/'www/assets/units3d-armados'/(u+'.webp')).stat().st_size;rows.append(f"| {u} | {s['strideMeters']:.3f} | {s['strideTiles']:.3f} | {s['recommendedAnimFactor']:.4f} | {p['bytes']/1048576:.2f} |")
report={'htmlBeforeBytes':len(oldindex),'htmlAfterBytes':len(newindex),'htmlGrowthPercent':100*(len(newindex)/len(oldindex)-1),'assetsBeforeBytes':baseline_assets,'assetsAfterBytes':current_assets,'assetsGrowthPercent':100*(current_assets/baseline_assets-1),'sixModelBytesOutsideWWW':models,'sixAtlasWebpBytes':atlas,'additionalMeshyCredits':0,'allSevenTestsPassed':False,'androidSDKAvailableLocally':False};(dest/'tamanhos.verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
game=json.loads((R/'jogo.verification.json').read_text());assert game['passed']
tests=json.loads((R/'testes.verification.json').read_text());assert tests['passed'] and len(tests['tests'])==7
report['allSevenTestsPassed']=True
(dest/'tamanhos.verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for name in ['jogo.verification.json','testes.verification.json']:
 shutil.copyfile(R/name,dest/name)
captures=dest/'capturas';captures.mkdir(exist_ok=True)
for file in R.glob('jogo-*.png'):shutil.copyfile(file,captures/file.name)
for name in ['corrigir_parent.py','verificar_direcoes.py','testar_jogo.cjs','documentar.py']:
 shutil.copyfile(R/name,dest/'scripts'/name)
text='''# Unidades armadas — integração local sem novos créditos

Cinco soldados Meshy existentes e o aldeão Meshy já criado, com equipamento e movimentos reutilizados. As seis unidades usam os novos atlas no jogo neste ramo. O besteiro pesado reutiliza o besteiro. Não foram gerados novos personagens, armas, rigs ou movimentos na Meshy. **Créditos adicionais: 0.**

## Âmbito e fontes

- Guerreiro: machado Meshy; guarda e pulso adaptados localmente.
- Lanceiro: lança Meshy; apoio das duas mãos adaptado ao movimento.
- Espadachim: variante com a guarda aprovada; caminhada reutilizada sem criar poses novas.
- Arqueiro: arco Meshy; ataque existente alinhado para a direção correta.
- Besteiro: besta Meshy; Attack local derivado do Combat Idle, conforme autorizado anteriormente.
- Aldeão: corpo Meshy novo, movimentos de trabalho Meshy já pagos adaptados ao seu esqueleto. Machado Meshy; picareta, enxada, martelo, faca, cesto, lança de caça e caixa reaproveitados do projeto. Não se declara que todas essas ferramentas antigas sejam Meshy.

Reis, cavalaria, navios, sacerdote, edifícios, mapa, desbloqueios e equilíbrio não foram substituídos. Não existem modelos novos dessas famílias nesta entrega. Não foram adicionados escudos nem aljavas independentes. Arco e besta reutilizam os movimentos existentes; não foi criada uma nova simulação de corda ou recarga. A unidade continua a cerca de 30 px no jogo.

## Integração

`www/assets/units3d-armados/` contém seis WebP e seis JSON novos. `UNIT3D_ARMED_DATA` seleciona estes atlas; `UNIT3D_DATA` e os ficheiros antigos ficam preservados. Se um atlas novo falhar, o carregador tenta o atlas anterior. A troca altera o desenho efetivo das unidades e cadáveres, mantendo seleção, tarefas, movimento e combate do jogo.

Foram renderizados 1 456 quadros: 576 do aldeão e 176 de cada soldado. O contrato mantém h=64, estados/ordem, âncoras e oito direções SE, S, SW, W, NW, N, NE, E. Render local CPU Ultra Light: Cycles CPU, duas threads, dois samples com denoise, imagem intermediária 128×128. Os GLB detalhados são fontes de renderização, fora de `www/`; o Android recebe sprites e não carrega os GLB.

A validação visual inicial encontrou armas que não herdavam a rotação do rig. A ligação ao objeto do rig foi corrigida, mantendo os pesos rígidos na mão; os atlas afetados foram renderizados novamente. `grip-directions.verification.json` confere a proximidade mão/ferramenta e a invariância ao rodar as oito direções, em duas poses por unidade. O teste CJS também rejeita malhas com skin fora da hierarquia do rig.

## Cadência medida

Estimativa baseada na velocidade para trás dos pés perto do chão, durante um ciclo normalizado, convertida pela projeção do jogo a 30 px. A posição da unidade não foi acelerada ou alterada. O motor conserva `u.anim += dt * v * 5`; o `phaseScale` do atlas aplica o fator medido a cada Walk. Carry do aldeão tem medição própria. São estimativas cinemáticas documentadas, sem afirmação de contato perfeito dos pés em todos os frames.

| Unidade | Passada estimada (m/clip) | Tiles/clip | Fator equivalente de u.anim | GLB (MiB) |
|---|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

## Verificação e revisão

- Cada GLB foi reimportado e verificado: 24 ossos, clips distintos, coordenadas finitas, raiz horizontal fixa nos clips ativos; Death preserva a queda.
- Os testes antigos continuam a validar os assets preservados. `tests/check_unit3d_armed.cjs` valida os novos hashes, limites, cadência, hierarquia e fallback.
- A galeria em `www/demo/unidades-armadas.html` usa o renderer e os atlas reais do jogo, a 30 px e a 4×.
- `jogo.verification.json` e as capturas são produzidos pelo teste de browser; não constituem medição num telemóvel Android.
- O SDK Android/JDK não está disponível neste PC. O workflow `unidades-armadas-preview.yml` prepara um APK debug e confere os ficheiros dentro do APK quando executado no GitHub. Um APK só deve ser anunciado depois de esse workflow passar; não há release nem merge automático.

## Reprodução

Os GLB finais são fontes autocontidas, com materiais e texturas. Os JSON `.build` identificam os meshes, ferramentas e estados; `.stride` documenta a medição; `.verification` contém hashes e reimportação.

Os scripts em `scripts/` preservam o processo local. `construir.py` requer o pacote de trabalho original das pastas irmãs descritas no script; essas cenas `.blend` não foram copiadas para o Git. Para refazer somente os atlas a partir desta entrega, importar o GLB correspondente, restaurar a visibilidade por estado conforme `.build`, e aplicar câmara/projeção e empacotamento dos scripts. A fonte completa de trabalho permanece no PC do autor em `outputs/integracao-soldados-armados/`. Nenhum cliente pago ou `.env` é necessário para rever os GLB e os sprites entregues.

Todos os ficheiros devem ser revistos no ramo `integracao-soldados-armados`, sem merge no main. A pasta não rastreada `arte/natureza-v2/` não faz parte desta alteração.
'''
perf=game['performanceComparison']
text+=f"\n## Tamanhos e medição local\n\nHTML: {len(oldindex):,} → {len(newindex):,} bytes (+{report['htmlGrowthPercent']:.2f}%). Os seis novos WebP somam {atlas/1048576:.2f} MiB. Os assets em www aumentam {report['assetsGrowthPercent']:.2f}%, porque as versões anteriores foram preservadas para fallback; não se afirma um limite de 15% nesta entrega. Os GLB de fontes somam {models/1048576:.2f} MiB e ficam fora do pacote web.\n\nNa cena de teste com 24 unidades, Chrome headless neste PC: média de {perf['before']['meanMs']:.3f} ms com atlas anteriores e {perf['after']['meanMs']:.3f} ms com os novos (40 quadros por amostra após aquecimento). É uma medição local de desenho, sem avaliação de FPS num Android. Os sete testes CJS passaram; os scripts e relatórios identificam os ficheiros verificados.\n"
(dest/'README.md').write_text(text,encoding='utf-8');print(json.dumps(report))
