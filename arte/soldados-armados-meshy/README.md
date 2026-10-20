# Soldados com armas Meshy — integração no jogo

Os cinco soldados piloto (corpos Meshy riggados) passam a usar as cinco armas Meshy do pacote `armas-meshy-cloud.zip`. Os atlas 2D foram renderizados pelo pipeline Forge3D e integrados no jogo com nomes novos. Os atlas anteriores continuam em `www/assets/units3d/<unidade>.webp|json`.

**Custo adicional: 0 créditos Meshy.** Não houve chamadas Meshy, `gerar-piloto.mjs`, rigs novos, animações compradas nem outro gerador pago. Não foi usada nenhuma chave nem `.env`.

## Fontes (hashes)

| Fonte | Referência |
|---|---|
| `origin/main` | `ae45420e2cc3d64a83b4984a014e8580cac83128` |
| `origin/edificios-v2` (base deste ramo) | `28db80d0993955a586f6c576e3151e20073efc5e` |
| `origin/soldados-meshy-piloto` (corpos, importação seletiva de `arte/soldados-meshy/`) | `7cb7cab23dc364f3d2b8928024b3e18d00f8eef4` |
| `armas-meshy-cloud.zip` (29 ficheiros, 75 773 108 bytes) | SHA-256 `c02891b1459a26e42e83bcbf8c4b70b0998f96e774ed59c91134dbd6556196f6` |
| Renderer Forge3D | `platinyb91cv-forge3d-ai` ramo `fase4-imagens` (commit `0425f41` e seguintes), `worker/sprite_atlas.py` |

As 10 armas (5 mestres + 5 otimizadas) foram conferidas com `armas/manifest.json`: os 10 SHA-256 coincidem. Os mestres (`modelos/`, PBR 2K, 66–435 mil triângulos) ficaram intactos no pacote e não entram no repositório nem no APK. Os atlas foram renderizados a partir das versões **otimizadas** (788 triângulos; 1 488 na besta; PBR 2K reprojetado). A 64 px de referência o detalhe é igual ao dos mestres, e o render fica reprodutível só com ficheiros do repositório. `reducao-direta/` e `soldados-armados-revisao/` não foram usados.

## Correspondência e pega

| Soldado | Arma | SHA-256 (otimizada) | Osso | Pose de orientação da pega |
|---|---|---|---|---|
| guerreiro | `axe-2.glb` | `47cc6f1a07800ff7…` | RightHand | neutra (1.º quadro de Death) |
| lanceiro | `spear-2.glb` | `8f8aadcb18546476…` | RightHand | neutra (1.º quadro de Death) |
| espadachim | `sword-2.glb` | `9c45d201f4ea02fd…` | RightHand | neutra (1.º quadro de Death) |
| arqueiro | `bow-2.glb` | `159677ca057bee00…` | LeftHand | disparo (Attack a 50 %) |
| besteiro | `crossbow.glb` | `b622fc6e638c3ef6…` | RightHand | pontaria (Attack local) |

Os hashes completos estão em `atlas/<unidade>.verification.json`.

- **Convenção.** As armas usam a convenção do pacote: pega na origem, cabo em +Z e fio em +Y, em metros (Blender Z-up). O importador glTF converte o Y-up do GLB, e a correção da besta (disparo em +Z) é preservada.
- **Prender à mão.** O Forge3D importa a arma (novo `PROP_MODELS` / `SPRITE_PROP_DIR`) e prende-a rigidamente ao osso com uma transformação explícita. Escolhe o eixo do cabo entre os eixos do osso da mão e coloca o fio para a frente com o cabo em pé, ou para baixo com o cabo deitado.
- **Ossos.** Os 24 ossos foram confirmados nos cinco corpos (`medicoes/<unidade>.json`). Não há ossos de dedos e não foi inventado nenhum.
- **Mão longa.** A `RightHand`/`LeftHand` dos rigs Meshy é muito comprida. A pega é limitada a 0,16 m da base do osso, como no piloto.
- **Rigidez.** O desvio máximo da matriz arma↔osso, em todos os quadros, é ≤ 4×10⁻⁶ (relativo). A arma está presente em todos os quadros dos cinco estados.

## Clips, ataques e correções de pose

| Soldado | Idle | Walk | Attack | Hit | Death |
|---|---|---|---|---|---|
| guerreiro | Idle 40 f | Walk 25,6 f (1,07 s; 1 ciclo; in-place) | Attack 36 f — golpe de machado | Hit 39 f | Death 53 f |
| lanceiro | Idle 40 f | Walk 25,6 f (1,07 s; 1 ciclo; in-place) | Attack 72 f — estocada com passo | Hit 39 f | Death 53 f |
| espadachim | Idle 40 f | Walk 25,6 f (1,07 s; 1 ciclo; in-place) | Attack 36 f — corte | Hit 39 f | Death 53 f |
| arqueiro | Idle 40 f | Walk 30 f (1,25 s; 1 ciclo; avanço 0,866 m removido) | Attack 120 f, troço 40–100 % — puxar e soltar | Hit 39 f | Death 53 f |
| besteiro | Idle 40 f | Walk 30 f (1,25 s; 1 ciclo; avanço 0,864 m removido) | **Adaptação local** do Combat Idle (ver abaixo) | Hit 39 f | Death 53 f |

f = quadros a 24 fps.

- **Infantaria (guerreiro, lanceiro, espadachim).** Em Idle, Walk e Hit, o antebraço direito dobra 85° (camada NLA COMBINE). A arma fica erguida à frente, a ~45°, em vez de espetada na horizontal. O Attack usa a pega neutra, sem a camada.
- **Arqueiro.** Em Idle, Walk e Hit, o antebraço esquerdo dobra 70°, para o arco ficar de pé à frente.
- **Besteiro.** O `Attack` não é uma animação Meshy nova. É o Combat Idle com braços para a frente e tronco a −6°, só nesse estado. A besta aponta para a frente em todos os quadros do ataque: produto escalar do eixo de disparo com a frente ≥ 0,998.
- **Raiz.** A raiz horizontal fica em 0 em Idle, Attack e Hit, e ≤ 0,024 alturas em Walk (balanço natural da anca). Death cai para trás (~0,5 alturas), como permitido.
- **Clips aprovados preservados.** Os GLB não foram alterados; as correções são camadas aplicadas só no render.

## Cadência medida (Walk)

O jogo avança `u.anim += dt · v · 5`. Um ciclo do atlas corresponde a `2π / (5 · phaseScale)` tiles.

Na câmara Forge3D, a altura do modelo H corresponde a 64 px, desenhados a 30 px. Uma tile avança 32 px no ecrã, o que dá 1 tile = 32·√2/30·H = 1,5085 H.

| Soldado | Fonte | Distância/ciclo | strideTiles | phaseScale | fator equivalente |
|---|---|---:|---:|---:|---:|
| guerreiro | pés (in-place) | 0,764 H | 0,5065 | 2,4812 | 12,41 |
| lanceiro | pés (in-place) | 0,763 H | 0,5058 | 2,4844 | 12,42 |
| espadachim | pés (in-place) | 0,766 H | 0,5078 | 2,4747 | 12,37 |
| arqueiro | root motion do clip | 0,535 H | 0,3547 | 3,5432 | 17,72 |
| besteiro | root motion do clip | 0,538 H | 0,3566 | 3,5235 | 17,62 |

`meta.locomotion.walk` leva estes valores. O renderer existente (`unit3dFrame`) já os aplica só ao Walk; a simulação e a velocidade não mudaram.

A infantaria e os atiradores têm clips de andar diferentes, por isso cadências diferentes. Os valores do ramo `soldados-v2` usavam cos 30° a mais na conversão e ficam substituídos aqui. O clip Walk da infantaria fecha com uma pequena descontinuidade dos pés (≈0,15 m entre o último e o primeiro quadro), visível só a 4×.

## Integração

- **Ficheiros.** São cinco atlas WebP sem perdas novos em `www/assets/units3d/<unidade>-armas-meshy.webp|json`. As cinco entradas de `UNIT3D_DATA` ganham `file`, `locomotion` e `atlasSha256`. O carregador usa `meta.file || type`.
- **Unidades.** O `besteiroPesado` continua a reutilizar o besteiro. Rei, aldeão e edifícios não mudaram.
- **Tamanhos.**
  - `www/index.html`: 2 809 582 → 2 806 262 bytes (sem GLB nem base64 novos).
  - WebP novos: 2 598 288 bytes no total; os anteriores mantêm-se em disco.
  - Memória descodificada dos 5 atlas usados: 4 231 168 → 3 842 048 px (16,1 → 14,7 MB RGBA).
- **Medições.** As medições são de browser (Chromium headless, swiftshader). O FPS em Android **não** foi medido.

## Provas

- `provas/<unidade>-antes-depois-30px.png`: antes e depois, SE e S, Idle/Walk/Attack/Hit/Death, a 30 px reais e com os mesmos píxeis a 4× (nearest).
- `provas/<unidade>-8-direcoes-ancoras.png`: as 8 direções (SE, S, SW, W, NW, N, NE, E), com o ponto de chão (cruz vermelha) e o retângulo de cada quadro (amarelo). Nenhum quadro toca a borda do enquadramento.
- `provas/jogo/`: capturas do jogo real (`jogo_soldados.py`) e `resultado.json`:
  - os 5 atlas novos pedidos com HTTP 200;
  - os cinco a andar nas 8 direções, com o estado `walk` e a direção 0…7 corretos;
  - combate (`attack`), dano (`hit`) e morte com cadáver (`die`) para os cinco;
  - zero erros de página.

## Testes

Todos os `tests/*.cjs` passam: bronze, edifícios v2, rei, memória do rei, `check_unit3d` e `check_unit3d_correction`.

`check_unit3d.cjs` passa a verificar, nos soldados com `file`:
- SHA-256 de cada atlas;
- 0 créditos e 24 ossos;
- 5 clips distintos (4 + Attack local documentado no besteiro);
- arma rígida e presente em todos os estados;
- raiz parada fora do Walk;
- cadência coerente com a passada medida;
- besta apontada para a frente;
- atlas anterior preservado.

`check_unit3d_correction.cjs` continua a validar o atlas corrigido anterior do guerreiro e do aldeão, que estão preservados.

## APK

Este ambiente não tem Android SDK (o acesso a `dl.google.com` está bloqueado), por isso não foi compilado aqui.

Foi acrescentado o workflow só de leitura `.github/workflows/soldados-armas-meshy-preview.yml`. Em cada push deste ramo, corre os testes, compila o APK **debug**, confirma no APK os bytes de `index.html` e dos 10 ficheiros novos, e publica-o como artefacto do Actions. Não cria release nem toca no `main`.

## Limitações e acessórios em falta

- **Escudo:** o escudo redondo gerado no site meshy.ai (`Meshy_AI_round_shield_1020033443`) foi reduzido de 290 960 para 1 500 triângulos (`scripts/preparar_escudo.py`) e está no antebraço esquerdo do guerreiro, lanceiro e espadachim, rígido e presente em todos os estados.
- **Aljava, flechas e virotes** continuam sem modelo próprio e não foram inventados.
  - O arqueiro tem só a pequena aljava vazia modelada no corpo Meshy.
  - O disparo do arco não mostra flecha nem corda puxada pela mão direita. O besteiro não mostra virote nem recuo. Os projéteis continuam a ser os do jogo.
  - A relação mão–corda–disparo **não** está validada.
- **Mão de apoio.** O lanceiro, o arqueiro e o besteiro não têm IK da segunda mão: as armas são seguras por uma mão. Os rigs não têm dedos, e uma pega a duas mãos exigiria constraints por quadro que não foram feitas aqui.
- **Leitura a 30 px.** As armas Meshy têm proporções reais e leem-se menos do que o machado procedimental anterior, que estava ampliado 1,8×. Isto vê-se na comparação a 30 px. Se for preciso, a escala das armas é um parâmetro do render (`length`) que exige nova aprovação.
- **Validação em Android.** O APK e a experiência num telemóvel ainda precisam de validação num dispositivo físico.

## Reproduzir

1. Copiar `scripts/renderizar_atlas.ts` para a raiz do Forge3D (`fase4-imagens`) e correr:
   `CORPOS=<repo>/arte/soldados-meshy ARMAS=<repo>/arte/soldados-armados-meshy/armas/otimizados OUT=saida WORKER_MAX_MEMORY_MB=3072 npx tsx renderizar_atlas.ts`
   Usa Blender 5.2 em CPU e demora cerca de 2–3 min por soldado.
2. Medir os clips: `MW_SRC=<corpo.glb> MW_OUT=<unidade>.json blender -b --python scripts/medir_walk.py`.
3. Integrar: `python3 scripts/integrar.py saida <repo> <medicoes>`.
4. Gerar as provas: `python3 scripts/provas.py <repo> provas`. Teste no jogo: `python3 -m http.server 8766` em `www/`, depois `python3 scripts/jogo_soldados.py <saida>`.

`configs/` guarda a configuração exata enviada ao Forge3D por soldado.
