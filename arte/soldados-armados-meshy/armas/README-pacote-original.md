# Piloto Meshy — cinco armas de Ferro

Cinco modelos independentes criados com Meshy 7.1 Text to 3D e texturização PBR 2K. Este é um piloto para revisão visual, sem integração no jogo, no Forge3D, em atlas ou APK, e sem commit/push.

## Entrega

| Ficheiro | Mestre normalizado (triângulos) | Candidato otimizado (triângulos) | Créditos |
|---|---:|---:|---:|
| axe-2.glb | 79,040 | 788 | 20 + 10 = 30 |
| spear-2.glb | 109,052 | 788 | 20 + 10 = 30 |
| sword-2.glb | 103,692 | 788 | 20 + 10 = 30 |
| bow-2.glb | 66,476 | 788 | 20 + 10 = 30 |
| crossbow.glb | 434,902 | 1,488 | 20 + 10 = 30 |

- `originais/`: GLB recebidos do Meshy, sem alterações, com proveniência, IDs e SHA-256.
- `modelos/`: versões de detalhe preservado, com orientação, escala em metros e origem de pega ajustadas no Blender.
- `otimizados/`: cópias com até 800 triângulos, ou 1.500 para a besta, sem substituir os mestres. Os vértices coincidentes das costuras UV foram unidos antes da redução para evitar fendas. Foram criadas novas UVs e reprojetados base color, normal e metallic/roughness do mestre em mapas 2K, por Cycles selected-to-active em CPU.
- `comparacao-piloto.png`: antes, Meshy com detalhe preservado e versão otimizada. Cada coluna mantém a mesma câmara, luz e escala entre versões; as diferentes armas são ampliadas para caberem na coluna.
- `comparacao-jogo-30px.png`: leitura com humano de referência de 30 px e ampliação dos mesmos píxeis a 4×. Texturas detalhadas não acrescentam píxeis à silhueta nessa escala.
- `index.html`: visualizador 3D local, com rotação, troca de arma/versão, eixos na origem e downloads.
- `manifest.json`, `verificacao.json`, `verificacao/` e `visualizador.verification.json`: medições, hashes, validação dos ficheiros e teste do visualizador.
- `reducao-direta/`: histórico da redução anterior à reprojeção, com artefactos visuais; não usar para integração. As versões finais são exclusivamente as de `modelos/` e `otimizados/`.

## Créditos e autorização

A primeira submissão foi rejeitada com HTTP 400: 824 caracteres excediam o limite de 800. O saldo permaneceu em 386 e não foi criado um ID de tarefa. O lote foi interrompido e os pedidos só foram retomados depois da autorização expressa do utilizador. O registo anterior permanece em `arquivo-tentativa-rejeitada/`.

Na retoma autorizada, cada arma teve uma geração de geometria (20 créditos) e uma texturização (10), todas SUCCEEDED, sem repetição paga. **Consumo real: 150 créditos. Saldo inicial: 386; saldo final: 236.** A soma dos créditos confirmados pelas dez tarefas coincide com a diferença do saldo. Recibo completo em `creditos.json`.

Não houve rig, animação, Ultra, remesh pago, lote adicional ou outra despesa Meshy. Os scripts carregam a chave apenas do ambiente local; nenhuma chave ou .env foi copiada para esta pasta. As respostas guardadas excluem URLs assinados de download.

## Medidas, origem e limites da validação

As coordenadas de modelação/medição são Blender Z-up, em metros; os GLB são exportados Y-up. A origem está no ponto de pega estimado a partir da secção do cabo. Rotação e escala foram aplicadas. As dimensões exteriores foram ajustadas ao piloto e verificadas diretamente nos GLB, incluindo o limite de triângulos e mapas PBR 2048×2048. A espada tem guarda de 0,25 m em X e lâmina ajustada a 0,07 m em X; a ponta da besta aponta para +Z.

A classificação automática da forma não certifica todas as medidas internas de cada componente, por exemplo o início exato da lâmina no cabo. A direção genérica do fio +Y precisa de revisão no caso da espada de dois gumes: a sua face larga/guarda seguem X. A origem foi verificada geometricamente perto do cabo, mas nenhuma pega animada foi adaptada a soldados neste piloto.

A aprovação de texturas PBR 2K substitui o requisito anterior de cores lisas sem imagens. Os materiais PBR fornecidos pelo Meshy e o material reprojetado foram preservados; não se declara cumprimento dos nomes antigos `madeira/metal/detalhe` separados por região.

As texturas 2K continuam a dominar o tamanho e a memória destas cópias. Não se afirma desempenho validado num telemóvel nem que os cinco GLB devam ser carregados simultaneamente no jogo. A integração final poderá usar estes modelos para renderizar os atlas existentes.

## Reprodução local sem novos créditos

```powershell
blender -b -t 2 --python preparar_blender.py
blender -b -t 2 --python reprojetar_pbr.py
python verificar_piloto.py
blender -b -t 2 --python renderizar_blender.py
python montar_comparacao.py
```

`gerar-piloto.mjs` é o registo do cliente usado para as tarefas pagas; não faz parte da reprodução local. As reservas exclusivas dos pedidos impedem repetir as submissões por acidente. Não voltar a executar o gerador para este lote concluído.

O visualizador reutiliza Three.js de `../soldados-meshy/vendor/`, com a pasta `outputs` como raiz HTTP. Teste automatizado: `testar-visualizador.cjs` com Playwright e Chrome.

Aguardam-se a revisão e aprovação do piloto antes de qualquer lote adicional.
