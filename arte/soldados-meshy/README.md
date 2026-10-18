# Cinco soldados Meshy — pilotos com animações de combate

Ramo de revisão: soldados-meshy-piloto. Base do jogo: main ae45420; pilotos originais: commit 45c99b3. Sem integração no jogo, sem alteração de www/, atlas ou testes, sem merge no main.

| Piloto | Unidade do jogo | Clips finais | Walk | Attack |
|---|---|---|---|---|
| Guerreiro | guerreiro, infantaria leve | Idle, Walk, Attack, Hit, Death | 672 Spear Walk | 219 Right-hand Sword Slash |
| Lanceiro | lanceiro | Idle, Walk, Attack, Hit, Death | 672 Spear Walk | 240 Thrust Slash |
| Espadachim | espadachim | Idle, Walk, Attack, Hit, Death | 672 Spear Walk | 219 Right-hand Sword Slash |
| Arqueiro | arqueiro | Idle, Walk, Attack, Hit, Death | Prime original preservado | 224 Archery Shot |
| Besteiro | besteiro | Idle, Walk, Hit, Death | Prime original preservado | Não incluído |

Idle: 89 Combat Idel; Hit: 178 Hit Reaction; Death: 189 Dying Backwards, nos cinco soldados. Os nomes apresentados são os nomes originais da biblioteca, incluindo a grafia Combat Idel. Nenhum piloto representa cavaleiro ou inclui cavalo.

## Créditos reais e revisão da autorização

O piloto original custou 190 créditos: por soldado, modelo 2K 30 + rig 5 + aplicação da caminhada Prime existente 3 = 38; cinco soldados = 190. A geração da caminhada Prime foi paga no piloto anterior do aldeão e não está nestes 190.

A proposta inicial de combate de **75 créditos** foi confirmada pelo utilizador com “sim”. Foram submetidas cinco tarefas com cinco ações cada através do scripts/meshy-motion.mjs do Forge3D, usando o ambiente local. Todas terminaram SUCCEEDED e cada uma confirmou consumedCredits=15.

A revisão para **66 créditos** chegou depois dessas cinco submissões. Não foi possível reduzir retroativamente o custo já submetido: **75 créditos realmente consumidos no combate; 265 no total dos cinco pilotos**. Não houve novo modelo, novo rig nem repetição automática.

| Soldado | Custo original | Combate cobrado | Ações aproveitadas | Equivalente aproveitado |
|---|---:|---:|---:|---:|
| Guerreiro | 38 | 15 | 5 | 15 |
| Lanceiro | 38 | 15 | 5 | 15 |
| Espadachim | 38 | 15 | 5 | 15 |
| Arqueiro | 38 | 15 | 4 | 12 |
| Besteiro | 38 | 15 | 3 | 9 |
| Total | 190 | 75 | 22 | 66 |

Três ações já cobradas foram excluídas dos GLB finais: Walk 672 do arqueiro, Walk 672 do besteiro e 690 Walk Forward While Shooting do besteiro. Equivalente não aproveitado: 9 créditos; não se declara reembolso. O 690 não está publicado como clip. O futuro ataque do besteiro a partir de Combat Idle no Forge3D continua por fazer e não foi substituído por um Attack fictício.

Recibos, IDs das tarefas e separação entre custo cobrado/aproveitado: creditos-confirmados.json. Sem credenciais ou URLs privados.

## Preparação e validação

Foram reutilizados os cinco rigs Meshy existentes, com os mesmos 24 ossos. A geometria, os materiais, as imagens PBR, os nós do esqueleto e os dados originais de skin foram preservados. Os modelos têm aproximadamente 100 mil triângulos, texturas 2K e ficheiros de 14 a 16 MB, abaixo de 50 MB; não foi necessário reduzir texturas.

As ações Meshy foram copiadas para um GLB por soldado, com os nomes exatos indicados na tabela. Em Idle, Attack e Hit, apenas Hips.translation.x e Hips.translation.z foram fixados na origem horizontal comum do rig. A componente vertical e todas as outras curvas foram mantidas. Coordenadas: glTF Y-up, modelo à frente em +Z; Blender Z-up, frente em -Y. Death conserva o deslocamento e a queda para trás.

Nos três soldados de infantaria, Walk é o preset 672 no lugar, com um ciclo de 1,066667 s. A origem Hips ainda tem oscilação horizontal cíclica de cerca de 2,4 cm; não foi aplicada a fixação exigida apenas para Idle/Attack/Hit. É uma aproximação de caminhada de infantaria, não um preset identificado como marcha militar.

Arqueiro e besteiro mantêm exatamente as chaves do Walk Prime anterior, apenas renomeado Walk: um ciclo selecionado de 1,266667 s, deslocamento horizontal de cerca de 0,87 m e extremos imperfeitos. A cadência e a compensação desse deslocamento no jogo continuam pendentes.

Os JSON de verificação incluem nomes dos ossos, duração e hash das curvas de cada clip, deslocamento e amplitude horizontal da raiz, SHA-256 do GLB, preservação das curvas de origem e reimportação no Blender. Os quatro primeiros modelos têm cinco clips distintos; o besteiro tem quatro. A amplitude horizontal da raiz de Idle/Attack/Hit é zero em todas as chaves, não apenas nos extremos.

## Pré-visualizações e reprodução

As folhas <nome>_8dir.png têm oito linhas SE, S, SW, W, NW, N, NE, E e oito fases da caminhada por linha. As três caminhadas novas foram renderizadas novamente; as duas preservadas mantêm as folhas anteriores. <nome>_combate.png mostra seis fases em S por clip de combate, incluindo o último quadro da queda.

Foram verificados 306 quadros novos sem cortes de silhueta. Render CPU Blender 5.2.2, Cycles, quatro amostras e duas threads. O renderizador desativa a ação ativa importada antes de selecionar a pista NLA, para impedir que Idle sobreponha os outros clips. As prévias finais usam essa correção.

Validar os GLB publicados (Python + Pillow):

    python scripts/validate_combat.py

Validar também a preservação contra os ficheiros de origem locais:

    python scripts/validate_combat.py --previous <GLB-do-commit-45c99b3> --source <outputs-Meshy-com-motions.glb-por-soldado>

Recriar os GLB, sem qualquer chamada paga:

    python scripts/build_combat.py --previous <GLB-do-commit-45c99b3> --source <outputs-Meshy> --assets <esta-pasta>

Recriar as folhas com Python + Pillow e Blender 5.2:

    python scripts/build_review.py --blender <executavel-Blender> --output <pasta-temporaria>

build_review.py e validate_review.py encaminham para os scripts atuais. Os scripts históricos de seleção do Walk Prime e preparação do modelo continuam disponíveis; os dois últimos corpos usaram meshoptimizer na preparação anterior do rig. Nenhum script público contém autenticação ou faz submissões Meshy.

## Limitações e estado do jogo

- Não há armas, escudos ou projéteis nos modelos. Os gestos de combate precisam desses acessórios na integração futura.
- O ataque do besteiro a partir do Combat Idle não faz parte deste GLB de quatro clips.
- O custo real desta ronda foi 75, não o teto revisto de 66, pelas submissões já efetuadas antes da revisão.
- O Walk 672 é a aproximação de biblioteca aprovada; o arqueiro e o besteiro ainda usam o Walk descontraído anterior.
- Os modelos continuam pesados para unidades móveis em grande número; falta decidir atlas/LOD e orçamento de memória. Não foi testado APK.
- Os cinco testes tests/*.cjs existentes na base passaram. O sexto check_unit3d_second_pass.cjs não existe nesta base main e não foi adicionado nem declarado aprovado.
- A pesquisa global de padrões de autenticação mantém apenas os literais preexistentes em server/server.js, tests/mock_supabase.js e www/vendor/supabase.js. O pacote arte/soldados-meshy não contém os padrões pesquisados nem credenciais. Nenhum .env, token, ZIP ou .blend foi incluído.

Resultados: review-validation.json. Os prompts e as imagens de referência originais acompanham cada soldado.
