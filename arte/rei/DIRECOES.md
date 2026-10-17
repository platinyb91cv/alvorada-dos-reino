# Correcao de orientacao dos reis

O renderer anterior usava uma vista isometrica, espelhada apenas na horizontal. Assim, o rei podia deslocar-se para cima sem mostrar as costas. O ciclo Walk original tem o apoio dos pes a deslocar-se para +Y local, atras do corpo que aponta para -Y: a ordem da animacao nao estava invertida.

Pedra e Bronze usam agora oito vistas reais dos modelos existentes. A projecao do mapa e `screen=(x-y,(x+y)/2)`. O Blender usa `forward=(dx,-dy)` e camera ortografica a 30 graus. A ordem e SE, S, SW, W, NW, N, NE, E; cada direcao contem os mesmos 24 estados. O indice final e `direcao*24+estado`: 192 entradas, com os quatro quadros antigos reutilizados dentro de cada vista. Caminhada continua com oito quadros, ataque quatro e parado dois. Altura de referencia 130, altura no jogo 34, ancoras comuns no chao. Sprites direcionais nao sao espelhados; a lanca mantem o lado do corpo.

`follow` guarda a direcao antes de concluir um ponto curto do caminho; `faceTo` atualiza-a ao virar para um alvo. O desenho usa o proximo ponto durante o movimento, o centro do alvo no ataque e a ultima direcao ao parar. A queda conserva direcao e idade do momento da morte. Velocidade, caminho, danos e projecao do jogo nao mudam. Ferro conserva o atlas KART e o comportamento visual legado; ainda nao tem oito vistas reais.

A renderizacao e feita em CPU, Cycles com 16 amostras e denoising, sem novas chamadas nem creditos Meshy. Os modelos 3D nao entram no APK. A imagem traseira continua a ser a interpretacao da Meshy a partir de uma unica referencia.

Validacao: `node tests/check_king_atlas.cjs` verifica os dois payloads WebP e JSON embutidos, 192 entradas e limites, selecao por idade e fallback. Executa as funcoes reais de direcao, movimento (incluindo chegada), ataque, desenho e queda; verifica oito sentidos e que so o atlas legado usa espelhamento. O painel local usa as funcoes reais do renderer e apresenta uma seta de movimento para comparacao visual.

O workflow de revisao compila um APK debug como artifact. Continua necessario validar uma partida completa num dispositivo Android; o teste no navegador e a compilacao nao substituem esse ensaio.
