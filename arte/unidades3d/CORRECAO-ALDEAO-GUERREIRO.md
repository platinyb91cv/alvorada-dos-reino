# Correção dos atlas do aldeão e guerreiro

Base: `main` em `0ddc1da498e5cef8f2ec331460fa42f4d89084c8`. Somente estas duas unidades foram renderizadas novamente. Nenhum modelo novo, chamada à Meshy ou crédito gasto.

O clip Walk anterior continha aproximadamente 2,87 ciclos de passada. Amostrar o clip inteiro em oito quadros saltava fases do movimento. A correção extrai um ciclo, mantém o movimento original das pernas e aplica uma camada no tronco/braços. Os braços superiores ficam próximos da vertical, os cotovelos fletidos e o balanço acompanha a perna oposta. Idle e Carry recebem a mesma correção no aldeão. O guerreiro recebe também correção da coluna, pescoço e ombros. A inclinação da coluna medida fica abaixo de 5°.

Chop usa a base em pé de Idle com levantar, bater e recuperar, sem a flexão até ao chão do clip anterior. O machado acompanha a orientação da mão durante todo o ciclo. Machado, picareta, martelo, enxada e faca aumentam 1,8× em torno da pega. Os cabos passam de raio 0,017 m para aproximadamente 0,048 m; as lâminas recebem espessura adicional para não desaparecerem de perfil a 30 px. Forage recebe um cesto aberto com aro e pega, ligado rigidamente à mão esquerda. As ferramentas não são deformadas pelo skin.

## Passada e velocidade do jogo

A referência continua a ser h=64, desenhada a 30 px. A câmara original determina a conversão entre metros do modelo e tiles do jogo. Em 241 amostras por ciclo, medimos a velocidade dos pés para trás quando próximos do chão; a mediana de cada pé, média entre os dois, estima a distância percorrida durante um ciclo completo. O relatório conserva também a amplitude e a dispersão dessas amostras.

| Unidade/estado | Distância por ciclo | Fator equivalente em `u.anim += dt * v * fator` |
|---|---:|---:|
| Aldeão / Walk | 0,375074 tile | 16,751844 |
| Guerreiro / Walk | 0,362909 tile | 17,313378 |
| Aldeão / Carry | 0,311424 tile | 20,175689 |

Com fator 5, o motor avança 1,256637 tiles por ciclo. Manter esse avanço numa única passada exigiria pernas com uma amplitude incompatível com estes modelos. O renderer aplica o multiplicador medido **somente** em Walk/Carry (`meta.locomotion[state].phaseScale`). O acumulador `u.anim`, a velocidade, a simulação e os estados de trabalho/combate permanecem iguais. As outras unidades continuam com fase normal.

Esta é uma calibração da cadência média, não uma garantia de contacto perfeito em todos os instantes: os clips originais têm velocidade de apoio variável e o atlas só tem oito quadros. A velocidade atual do jogo, à escala humana de 30 px, exige uma cadência elevada; para uma caminhada lenta seria necessário reduzir a velocidade do jogo ou usar um clip de corrida apropriado. Não se aumentou artificialmente o tamanho do personagem para disfarçar a diferença.

## Escala, âncoras e compatibilidade

As câmaras foram recuperadas da cena e de todos os estados originais **antes** da correção; `*.camera.json` conserva posição, rotação, escala ortográfica e `bodyReferencePixels`. O render final reutiliza estes valores em vez de voltar a enquadrar as ferramentas maiores. Mantêm-se h=64, as oito direções SE/S/SW/W/NW/N/NE/E, a ordem dos estados e o número de quadros (72 por direção no aldeão e 22 no guerreiro). O ponto de chão é preservado; os valores de recorte `ax/ay` acompanham o novo retângulo de cada sprite para manter esse mesmo ponto de chão.

Os metadados externos e `UNIT3D_DATA` têm os mesmos dados e SHA-256. Os relatórios individuais incluem reimportação do GLB, clips distintos, rigidez das ferramentas, ligação ao osso da mão, erro de fecho do ciclo, postura e medição da passada. Os GLB e cenas corrigidos estão no pacote local de fontes; não são carregados pelo APK.

## Reproduzir com as fontes locais

Preservar primeiro os diretórios originais `aldeao/` e `guerreiro/` num diretório separado. `--baseline` tem de apontar para esses originais, nunca para a saída já corrigida. `--sources` aponta para o pacote expandido que contém `manifest.json` e os diretórios das unidades. Os scripts estão em `fontes-correcao/` no repositório e em `source/` no pacote ZIP.

1. Copiar `aldeao.camera.json` e `guerreiro.camera.json` para `<sources>/<unidade>/fixed-camera.json`.
2. Executar Blender 5.2 em CPU: `blender -b -t 2 --python correct_units.py -- --sources <sources> --baseline <originais>`. O script só processa as duas unidades.
3. Executar `measure_stride.py`, `verify_correction.py`, e `verify_models.py -- --unit aldeao` / `--unit guerreiro`, passando sempre `--sources <sources>`.
4. Executar `render_units.py` com `--sources <sources> --unit aldeao --verify-axe-visibility` para medir a lâmina em todos os quadros e direções. Renderizar sequencialmente: `blender -b -t 2 --python render_units.py -- --sources <sources> --unit aldeao --force-all`, depois guerreiro. São PNG de 192 px, oito amostras Cycles, convertidos para referência h=64 pelo empacotador.
5. Executar Python/Pillow `pack_units.py --sources <sources> --unit aldeao`, depois guerreiro. Executar `integrate_correction.py --sources <sources> --repo <checkout>` para copiar somente os dois WebP/JSON e atualizar os dois metadados embutidos e comprovativos.

## Verificação antes do envio

Executar `node tests/check_unit3d.cjs`, `node tests/check_king_atlas.cjs`, `node tests/check_king_memory.cjs` e `node tests/check_unit3d_correction.cjs`. A folha `comparacao-antes-depois.png` apresenta todos os quadros de Walk/Chop/Mine/Farm/Forage/Carry do aldeão e Walk do guerreiro, em SE e S, reduzidos primeiro a 30 px e ampliados 3× para inspeção. O guerreiro não tem os estados de trabalho do aldeão.

Não foi executada uma partida num aparelho Android físico nesta correção. O ramo é entregue para revisão, sem merge no main.
