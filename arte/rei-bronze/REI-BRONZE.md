# Rei animado da Idade do Bronze

Referencia fornecida pelo utilizador e convertida em 3D pela Meshy, com armadura/elmo de bronze, lanca e capa. O modelo otimizado tem 16.028 vertices, 7.987 triangulos, 25 ossos, quatro mapas PBR e sete clips: parado, andar, ataque, grito, conjuracao, golpe e queda. A lanca usa um osso rigido proprio.

Os sprites foram renderizados em CPU para o contrato de 24 quadros do jogo. `rei.webp`, `rei_atlas.png` e `rei.json` correspondem ao payload BRONZE_ART embutido no HTML. A Idade da Pedra continua com BART; a Idade do Ferro conserva KART. O GLB nao e carregado pelo jogo Canvas nem incluido no APK.

O teste `node tests/check_king_atlas.cjs` verifica os dois atlas, limites e ancoras dos quadros, payloads embutidos e executa o desenho real do rei vivo e morto para as tres idades, incluindo fallback de carregamento.

Geracao, rig e sete animacoes custaram 56 creditos. Nenhuma chave foi incluida. A parte traseira foi inferida da unica imagem; a capa nao tem simulacao fisica. A partida completa num dispositivo Android ainda requer validacao.
