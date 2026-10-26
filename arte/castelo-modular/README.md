# Castelo modular: muralhas e torre redonda numa só cena do Blender

Substitui as muralhas de pedra e fortificada e a torre de nível 3. As pinturas em `arte/pintura-castelo/` serviram só de referência visual.

## Regras da cena (`scripts/montar_modular.py`)
- **Câmara:** ortográfica, azimute 45°, elevação 30° (eixos do chão 2:1). PXU = 90,5 px por casa a 2×, igual em todas as peças.
- **Luz e material:** uma luz e o mesmo material de pedra para tudo. A textura está presa ao mundo, com período de 1 casa, por isso as peças vizinhas emendam sem costura.
- **Sem sombra de chão:** fundo transparente e nenhum apanha-sombras. Verificado: 0 píxeis de sombra embutida no atlas. O jogo projeta a sua própria sombra.
- **Medidas comuns:**
  - espessura 0,62;
  - caminho de ronda a 1,3 na pedra e a 1,5 na fortificada;
  - torre com diâmetro 1,7 e piso a 3,3 numa pegada 2×2.
- **Peças de muro:** 16 máscaras de vizinhos (1 = +x, 2 = +y, 4 = −x, 8 = −y): retas, 4 pontas, 4 cantos, 4 T, cruz e muro sozinho. Há ainda variantes `_g4`/`_g8`/`_g12` junto a um portão. As retas não têm torreões.
- **Junções:**
  - cada peça é a união dos braços numa só malha, só com faces de fronteira (sem faces internas nem paredes sobrepostas);
  - o parapeito e as ameias só existem nos lados sem braço, por isso o caminho de ronda fica livre;
  - as ameias têm período de 0,25 preso ao mundo e não se repetem.
- **Encaixe entre casas:** o braço para um vizinho continua para lá da casa. O integrador corta a coluna de ecrã da casa (±32 px + 3 px de sobreposição) só nesse lado.
- **Torre:** é um objeto à parte. Os pedaços de muro que entram nela (2 por lado) são renderizados com a mesma câmara da torre.
  - A torre funciona como recorte: tem material holdout, não recebe nem devolve luz e não desenha contornos.
  - Assim cada pedaço só mostra o que está à frente da torre, com o recorte exato e curvo, sem cortes retos nem faixas verticais.
  - Os dois pedaços de trás (mx0 e my0) ficam totalmente escondidos e não são exportados.

## Exportação (`scripts/integrar_modular.py`)
- **Atlas:** `www/assets/edificios-extra/castelo-modular.webp` e `CMOD_DATA` no `index.html`. Cada peça regista [x, y, w, h, âncora x, âncora y].
- **Âncora:** o canto de cima da casa, ou da pegada no caso da torre e dos seus pedaços.
- **Pontos de ligação:** `links`, no caminho de ronda à borda da casa, em píxeis da peça.
- **Medidas brutas:** `anchors.json`.

## No jogo
- **Muros:** `wall3dSprite` usa estas peças para a muralha de pedra e para a fortificada.
- **Torre:** a torre de nível 3 usa `torre3`. Os pedaços `tw_<tipo>_<lado><fila>` desenham-se logo depois dela, para cada muro ligado.
- **Caminho de ronda:** `TOPZ` dá 1,3 e 1,5 nos muros e 3,3 na torre.
- **Depuração:** `?iso=1` mostra a grelha, as áreas ocupadas e as âncoras.

## Gerar de novo
```
WORK=<pasta com montar_portao2.py> OUT=/tmp/mod TEX_DIR=<texturas Poly Haven> blender -b --python arte/castelo-modular/scripts/montar_modular.py
python3 arte/castelo-modular/scripts/integrar_modular.py /tmp/mod .
```
- `BLOCK=1 ONLY=testes`: montagem de teste com geometria simples.

## Provas e testes
- Montagem de teste: `provas/teste/`. Resultado final: `provas/final/`.
- Testes: `tests/check_castelo_modular.cjs` e `tests/e2e/castelo_modular.py`.

## Tom areia
Depois de `integrar_modular.py`, `scripts/tom_areia.py` põe a pedra no tom areia das peças pintadas (torre de menagem e Torre de Catapulta).
