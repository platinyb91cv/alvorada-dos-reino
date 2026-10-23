# Auditoria — muralhas, torres e portões

Ramo `vida-aldeia-curral`. Corrigido o que existia, sem reconstruir e sem mudar mecânicas que já funcionavam.

## Causas encontradas

1. **Escala da câmara do Blender errada.** Com `sensor_fit = AUTO`, o `ortho_scale` era aplicado à dimensão maior da imagem (a altura). Resultado: muros e portões (360×400) saíam **11% maiores** e os edifícios **5% maiores**. Por isso a base do muro ocupava 0,80 de um tile em vez de 0,64 e o topo ficava acima do que o jogo esperava. Correção: `sensor_fit = 'HORIZONTAL'` em `montar_portao2.py`.
2. **Âncora do muro calculada antes de atualizar a cena.** O `world_to_camera_view` corria antes de `view_layer.update()`, e a âncora caía 16 px acima do sítio certo. Correção: atualizar a cena antes de projetar.
3. **Muro desenhado por cima da casa do portão.** O braço do muro ia até ao centro do tile do portão e pintava parede por cima da abertura. Agora há variantes `_g4`, `_g8` e `_g12` que param na face da casa do portão. O `bldVariant` marca os bits 64/128 quando o vizinho é um portão do mesmo dono na mesma direção.
4. **Altura dos soldados em cima compensada à mão.** O `drawGarrTop` tinha um fator de correção para esconder os erros 1 e 2. Foi removido: o `ZP` é agora o valor exato, e o `TOPZ` corresponde à altura real do modelo (muro 1,30 / fortificado 1,50, +0,44 nos pilares de canto e nas pontas).
5. **Torres não assentavam no chão.** Era o mesmo erro de escala; as torres foram renderizadas outra vez à escala certa.

## Ficheiros modificados

- `www/index.html`: `bldVariant` (bits de portão), `wall3dSprite` (escolhe a variante `_g`), `TOPZ`, `drawGarrTop` (sem fator de correção).
- `arte/portoes-3d/scripts/montar_portao2.py`: câmara.
- `arte/muralhas-3d/scripts/montar_muro.py`: corte junto ao portão (`GCUT`), variantes `_g`, ordem de atualização da âncora.
- `arte/muralhas-3d/scripts/integrar_muro.py`: recorte de cada coluna com ±3 px de sobreposição, para não haver frinchas.
- `arte/edificios-3d/scripts/montar_edificios.py`: torres.
- Atlas novos: muros (108 peças), portões e edifícios-3d, com os JSON de verificação atualizados.
- Testes:
  - novos: `tests/check_defesas.cjs`, `tests/e2e/defesas_auditoria.py`, `tests/e2e/defesas_selecao.py`;
  - ajustados: `tests/check_muralhas3d.cjs`, `tests/check_portoes3d.cjs`.
- Provas: `arte/muralhas-3d/provas/auditoria/*.png`, `tests/e2e/defesas_auditoria_{antes,depois}.json`, `tests/e2e/soldados_em_cima_resultado.json`.

## Resultados dos testes (todos executados)

### Medição de forma e assentamento (`defesas_auditoria.py`)

A medição é feita sobre a geometria exata da coluna de cada peça.

| Peça | Antes | Depois |
|---|---|---|
| Muro de pedra (altura / base) | 1,56 / 0,80 — FAIL | 1,43 / 0,63 — **PASS** |
| Muro fortificado | FAIL | 1,60 / 0,69 — **PASS** |
| Portão de pedra | 2,46 / 1,17 — FAIL | 2,21 / 0,94 — **PASS** |
| Portão de madeira | base FAIL | **PASS** |
| Paliçada | PASS | **PASS** |
| Torres (topo, medido vs esperado) | não assentavam | 3,28 / 3,33 / 3,56 vs 3,28 / 3,39 / 3,53 — **PASS** |
| Torres (base no chão) | não assentavam | 3,93–4,02 vs 4 — **PASS** |

A medição de altura inclui os merlões, por isso o muro de pedra mede 1,43 contra a referência de 1,30.

| Outras verificações de montagem | Resultado |
|---|---|
| Variantes de muro encostadas ao portão, na disposição de combinações | 4 usadas (antes 0) — **PASS** |
| Cada tipo construído sozinho | **PASS** |
| Combinações de retas, cantos, torres e portões | **PASS** (ver `combinacoes.png`) |

### Passagem pelo portão

| Caso | Resultado |
|---|---|
| Unidade do dono entra pelo portão | PASS |
| Inimigo entra | bloqueado — PASS |
| Portão trancado, unidade do dono | bloqueada — PASS |
| Portão destrancado, unidade do dono | passa — PASS |
| A porta abre até 1 e fecha quando não há ninguém perto | PASS |

### Soldados em cima (`soldados_em_cima.py`, `defesas_selecao.py`)

| Verificação | Resultado |
|---|---|
| Capacidades: muro de pedra 2, fortificado 3, portão de pedra 4, portão de madeira 2, torre 5 | PASS |
| Aldeão e cavalaria recusados | PASS |
| Combate: 11 de 12 atacantes mortos, 0 baixas em cima | PASS |
| Gravar/carregar mantém 35 de 35 | PASS |
| Botão "Sair" | PASS |
| Muro destruído deixa cair 3 soldados vivos a 70% de vida | PASS |
| Painel "Guarnição: 2/2", botão "Sair (2)", 0 em cima depois de sair | PASS |
| Erros de consola | 0 |

### Restantes testes

| Verificação | Resultado |
|---|---|
| 21 testes `tests/*.cjs` | todos PASS |
| Desempenho (`desempenho.py`) | ~56 ms contra ~53–55 ms antes — sem regressão |

### APK

Compilação confirmada: run 39945404370 terminou com **success** (commit 3a90c5d). O jogo não foi testado num telemóvel real.

## NOT TESTED / problemas restantes

- **Andar ao longo do topo do muro: NÃO IMPLEMENTADO / NOT TESTED.** A guarnição é estática: os soldados ficam no segmento onde subiram, não caminham de segmento em segmento. Implementá-lo seria uma mecânica nova, porque o pathfinding em cima do muro não existe.
- **Degrau de 0,2 entre o muro fortificado (1,50) e a base da torre redonda (1,30).** É visível de perto. Corrige-se subindo a base da torre de nível 3 para 1,5, se quiseres.
- **Teste num telemóvel real: NOT TESTED.** Só foi testado no Chromium em modo telemóvel.
- **Câmara isométrica:** a escala ficou consistente (todas as peças com o mesmo PXU), confirmada por medição. Não foi feita uma revisão visual em todos os níveis de zoom.
