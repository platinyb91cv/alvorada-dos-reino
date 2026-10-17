# Guerreiro com lanca

Acrescenta o atlas BART para o rei da Idade da Pedra, com sprites renderizados do personagem Meshy criado a partir da imagem fornecida pelo utilizador. Ferro mantem o atlas KART original do cavaleiro. Bronze usa o novo BRONZE_ART, documentado em ../rei-bronze/REI-BRONZE.md. Usa oito vistas reais, com 24 quadros por direcao (192 entradas); ver DIRECOES.md. Mantem referencia 130 px, altura de jogo 34 px e ancoras por quadro. O payload WebP e os metadados BART de `www/index.html` correspondem aos arquivos desta pasta. O personagem vivo e a queda selecionam o atlas pela idade; enquanto o novo atlas carrega, existe fallback para KART.

Estados: andar antigo 0–3, ataque 4–7, parado 8–9, grito 10, conjuracao/bencao 11, golpe 12, queda 13–15, andar atual 16–23. As duas faixas do cinto recebem as cores de equipa/capa pelas funcoes existentes; pele e pelos conservam as texturas.

Fonte 3D validada no Blender: 16.623 vertices, 9.367 triangulos, 25 ossos, sete movimentos distintos, quatro mapas PBR. A lanca tem um osso rigido proprio. O GLB nao e carregado pelo jogo Canvas e nao e incluido no APK; o jogo usa somente o atlas.

Verificacoes locais: oito quadros de caminhada diferentes, quatro de ataque diferentes, dois parados diferentes, sem cortes no atlas, recoloracao independente e ausencia de espelhamento nos sprites direcionais testadas no painel com as funcoes reais do jogo. `node tests/check_king_atlas.cjs` verifica payload embutido, metadados, limites dos quadros, contrato do motor e executa o dispatcher real `drawKing` para as tres idades. O atlas original KART foi preservado integralmente; as funcoes de atlas/desenho receberam um argumento de fonte para reutilizar o mesmo renderer.

O workflow `APK de revisao do guerreiro` compila somente um APK debug como artifact; nao usa chaves de assinatura nem publica Releases. A rotina original de publicacao foi preservada.

Limites: nao houve simulacao de tecido/pelos; a parte traseira e inferida da unica imagem; o punho e ombros podem precisar de acabamento no GLB ampliado. A validacao de partida completa num dispositivo continua necessaria.
