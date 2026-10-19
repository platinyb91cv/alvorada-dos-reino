# Edifícios v2 — 37 peças integradas

Ramo `edificios-v2`, sem merge no `main`. Arte criada exclusivamente com o gerador integrado `image_gen`, aprovada por etapas pelo utilizador, incluindo as oito correções finais. Zero chamadas/créditos Meshy nesta iniciativa.

## Integração

O jogo carrega `www/assets/edificios-v2/bld-atlas-v2.webp`. Os metadados das 37 peças estão em `www/assets/edificios-v2/bld-v2.json`, no formato existente `xl`, `xr`, `yb`, `yl`, `f`. A cópia de revisão está em `publicacao/bld-v2.json`. A versão embutida no HTML é gerada pelo mesmo script e validada contra estes JSON.

O atlas inclui ainda três frames legados preservados: `mercado|1`, `mercado|2`, `oficina|2`, com metadados em `bld-compatibilidade.json`. O mercado e a oficina superior já existiam fora da lista das 37 peças; mantêm a arte anterior, sem geração adicional. São 37 frames novos e três de compatibilidade, não 40 edifícios novos.

Os ficheiros atuais de `arte/edificios/` não foram alterados nem apagados. `publicacao/legacy/` preserva também o atlas WebP e os 40 metadados que estavam realmente embutidos no jogo, pois diferiam da antiga versão independente. Só a inicialização do atlas e os metadados de BLDART mudaram no HTML; as fórmulas de projeção, escala, implantação e orientação mantêm-se.

## Imagens e prompts

`publicacao/sprites/` contém os 37 PNG recortados, com resolução suficiente para a tela supersampled SS=2 do jogo. `publicacao/manifest.json` contém medidas, âncoras, máscaras das bandeiras e SHA-256 de cada PNG. `publicacao/prompts.json` regista prompts e correções. As fontes brutas de alta resolução e todas as rondas descartadas foram preservadas localmente em `outputs/edificios-v2-trabalho/rascunhos-completos-aprovados`, fora do pacote Git; os PNG finais necessários para reconstruir o atlas estão neste ramo.

O azul recolorível fica no pano das bandeiras; ambas as ruínas não têm bandeira. O recorte elimina magenta e limpa os pequenos píxeis de cor introduzidos pela redução. A iluminação, os materiais e a evolução Pedra/Bronze/Ferro seguem a revisão aprovada. A torre `torre|3` é uma melhoria fortificada e `ruina|1` uma variante para lotes maiores, não idades históricas adicionais.

## Verificação no jogo

Capturas reais do Chrome, com o motor do jogo e entidades de uma vila de teste determinística, semente 48172:

- [Pedra](publicacao/capturas/vila-idade-0.png)
- [Bronze](publicacao/capturas/vila-idade-1.png)
- [Ferro](publicacao/capturas/vila-idade-2.png)
- [37 peças com grelha de implantação](publicacao/capturas/calibracao-37-pecas.png)

As três vilas cobrem todas as 37 chaves, incluindo as duas ruínas. O teste usa uma sessão offline isolada para dispor edifícios e ocultar os ecrãs de conta/menu; não modifica autenticação nem o fluxo normal do produto. As capturas foram inspecionadas visualmente. O relatório `jogo.verification.json` regista as 37 verificações de dimensões e âncoras, sem erros JavaScript. A diferença de arredondamento da âncora vertical é no máximo 0,5 px; a preparação das imagens conserva as dimensões lógicas aprovadas com até 2 px de arredondamento. Muralhas e portões mantêm as regras especiais de escala e orientação do jogo.

Todos os `tests/*.cjs` passaram: cinco testes existentes e o novo teste de integridade, metadados, compatibilidade e orçamento dos edifícios. `publicacao/integracao.verification.json` e `atlas.verification.json` contêm as medições e hashes.

## Tamanhos

| Medida | Antes | Depois | Variação |
|---|---:|---:|---:|
| index.html | 4 119 695 B | 2 815 793 B | −31,65% |
| Todo o www | 14 787 032 B | 14 840 140 B | +0,36% |
| www/assets | 9 867 468 B | 11 224 478 B | +13,75% |
| Atlas RGBA descodificado | 18 956 288 B | 18 669 568 B | −1,51% |

Atlas WebP novo: 2048×2279, 1 353 454 bytes. O crescimento de assets decorre de externalizar o atlas que antes estava dentro do HTML; o total distribuído cresce apenas 53 108 bytes. O pacote não carrega os sprites de fonte nem o backup legado como recursos adicionais do jogo.

## Reproduzir

Dependências técnicas: Python com Pillow e NumPy; Node.js; Playwright e Chrome para as capturas. A compilação Android usa Node 22, Java 21 e o wrapper Gradle já existente.

```sh
python arte/edificios-v2/scripts/sanitize_sprites.py
python arte/edificios-v2/scripts/pack_release.py
node arte/edificios-v2/scripts/capture_villages.cjs
python arte/edificios-v2/scripts/verify_release.py
```

O workflow `Edificios v2 - APK de teste` compila apenas o APK debug do ramo. Não publica Release, não altera tags, não usa a chave de assinatura de produção e não faz merge. Confere por SHA-256 o HTML, o atlas e os dois JSON dentro do APK, e disponibiliza `app-debug.apk` e `apk-verification.json` no artifact `alvorada-edificios-v2-apk`.

O APK ainda precisa de uma partida num dispositivo Android físico; as verificações visuais desta entrega foram feitas no Chrome. Não se afirma desempenho medido num telemóvel.

## Lista das 37 imagens

| Chave (tipo / variante) | Tiles | PNG em publicacao |
|---|---|---|
| centro / 0 | 3×3 | sprites/centro-0.png |
| centro / 1 | 3×3 | sprites/centro-1.png |
| centro / 2 | 3×3 | sprites/centro-2.png |
| casa / 0 | 2×2 | sprites/casa-0.png |
| casa / 1 | 2×2 | sprites/casa-1.png |
| casa / 2 | 2×2 | sprites/casa-2.png |
| armazem / 0 | 2×2 | sprites/armazem-0.png |
| armazem / 1 | 2×2 | sprites/armazem-1.png |
| armazem / 2 | 2×2 | sprites/armazem-2.png |
| quartel / 0 | 3×3 | sprites/quartel-0.png |
| quartel / 1 | 3×3 | sprites/quartel-1.png |
| quartel / 2 | 3×3 | sprites/quartel-2.png |
| arquearia / 0 | 3×3 | sprites/arquearia-0.png |
| arquearia / 1 | 3×3 | sprites/arquearia-1.png |
| arquearia / 2 | 3×3 | sprites/arquearia-2.png |
| estabulo / 0 | 3×3 | sprites/estabulo-0.png |
| estabulo / 1 | 3×3 | sprites/estabulo-1.png |
| estabulo / 2 | 3×3 | sprites/estabulo-2.png |
| ferreiro / 0 | 2×2 | sprites/ferreiro-0.png |
| ferreiro / 1 | 2×2 | sprites/ferreiro-1.png |
| ferreiro / 2 | 2×2 | sprites/ferreiro-2.png |
| quinta / 0 | 3×3 | sprites/quinta-0.png |
| quinta / 1 | 3×3 | sprites/quinta-1.png |
| templo / 1 | 3×3 | sprites/templo-1.png |
| templo / 2 | 3×3 | sprites/templo-2.png |
| doca / 0 | 2×2 | sprites/doca-0.png |
| torre / 1 | 2×2 | sprites/torre-1.png |
| torre / 2 | 2×2 | sprites/torre-2.png |
| torre / 3 | 2×2 | sprites/torre-3.png |
| oficina / 1 | 3×3 | sprites/oficina-1.png |
| maravilha / 2 | 4×4 | sprites/maravilha-2.png |
| portaoMadeira / 0 | 1×1 | sprites/portaoMadeira-0.png |
| portaoPedra / 0 | 1×1 | sprites/portaoPedra-0.png |
| muralhaMadeira / 0 | 1×1 | sprites/muralhaMadeira-0.png |
| muralhaPedra / 0 | 1×1 | sprites/muralhaPedra-0.png |
| ruina / 0 | 2×2 | sprites/ruina-0.png |
| ruina / 1 | 3×3 | sprites/ruina-1.png |
