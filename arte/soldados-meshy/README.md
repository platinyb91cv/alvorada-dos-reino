# Cinco soldados Meshy — pilotos para revisão

Base: main ae45420. Sem integração no jogo, sem alteração de atlas ou testes.

| Piloto | Unidade a substituir | Modelo 2K | Rig | Caminhada aplicada | Total |
|---|---|---:|---:|---:|---:|
| Guerreiro | guerreiro (infantaria leve) | 30 | 5 | 3 | 38 |
| Lanceiro | lanceiro | 30 | 5 | 3 | 38 |
| Espadachim | espadachim | 30 | 5 | 3 | 38 |
| Arqueiro | arqueiro | 30 | 5 | 3 | 38 |
| Besteiro | besteiro | 30 | 5 | 3 | 38 |

Total efetivamente consumido: **190 créditos**, 15 etapas concluídas, sem repetições. Nenhum piloto substitui cavaleiro ou inclui cavalo. A geração Prime do movimento partilhado foi paga no piloto anterior do aldeão; não integra estes 190 créditos. Recibos sem URLs privados em creditos-confirmados.json.

## Conteúdo e reprodução

Cada GLB é a cópia binária do walk-cycle.glb final: rig, materiais PBR e um clip Meshy. Todos abaixo de 50 MB; não foi necessário reduzir texturas. O ciclo seleciona 39 chaves contíguas de 0,633333 a 1,900000 segundos do movimento original, sem inventar poses, sem offsets nos ossos; apenas reposiciona o início temporal em zero. Os JSON incluem os nomes dos ossos e clips, medidas e SHA-256.

Referências: imagens individuais geradas a partir da folha visual Alvorada dos Reinos. Os prompts de imagem e do movimento estão em cada .prompt.txt. A geração dos corpos Meshy usou a imagem, não text-to-3D.

As folhas PNG têm oito linhas SE, S, SW, W, NW, N, NE, E e oito quadros por linha (fases 0/8 a 7/8), células de 128 px. Render CPU Blender 5.2.2 / Cycles, quatro amostras, duas threads; sem modificar rig ou animação.

Reproduzir folhas e verificação com Python + Pillow e Blender 5.2:

    python scripts/build_review.py --blender "caminho/para/blender" --output "pasta/temporaria"

render_review.py é o renderizador utilizado nesta revisão. Os outros scripts são as fontes históricas de preparação/seleção/validação; usam a estrutura de trabalho outputs/soldados-meshy/<nome>/ e os GLB originais, não incluídos por redundância. prepare_model_blender.py foi usado nos três primeiros corpos. Os dois últimos usaram simplificação meshoptimizer para entrada do rig; os GLB finais aqui não são reotimizados.

## Falta e problemas conhecidos

- Armas, escudos e animações de ataque/combate não incluídos.
- Caminhada Prime partilhada com o aldeão: movimento descontraído, considerado pelo utilizador um desfile; marcha militar ainda não criada. Este ramo preserva o piloto para revisão.
- Deslocamento real da raiz mantido (~0,87 m por ciclo); o jogo ainda precisa adaptar ciclo/velocidade ou compensar root motion. A medida principal usa a origem Hips no GLB; a posição da cabeça do osso importado pelo Blender é registada separadamente porque difere ligeiramente. Coordenadas explicitadas nos JSON: Blender Z-up -Y à frente, glTF Y-up +Z à frente.
- Um ciclo completo de passada esquerda/direita por clip selecionado (1,266667 s); endpoints não são idênticos, diferença máxima de rotação importada ~14,7 graus. Não é um loop perfeito.
- Cerca de 100 mil triângulos por piloto: adequado à revisão, ainda exige orçamento/LOD ou atlas para jogo móvel. Não foi testado em APK.
- Altura medida nas bounds importadas na primeira fase, não a altura nominal de 1,8 m pedida ao rig.

## Validação do ramo

Os cinco testes tests/*.cjs presentes no main passaram sem alterações. O sexto, check_unit3d_second_pass.cjs, existe apenas no ramo anterior correcao-aldeao-guerreiro; depende das correções desse ramo e não está no main. Não foi adicionado nem se declara aprovado nesta base.

A pesquisa global pedida encontra literais de autenticação preexistentes em server/server.js, tests/mock_supabase.js e www/vendor/supabase.js; não foram alterados. A pesquisa no pacote novo não encontra os padrões pedidos. Não se pode declarar zero resultados no ramo inteiro sem alterar ficheiros fora deste trabalho. Nenhuma chave, token, configuração privada, .blend ou ZIP incluído.

Validar novamente o pacote: `python scripts/validate_review.py` (Python + Pillow). Resultados dos testes e limites da verificação: review-validation.json.
