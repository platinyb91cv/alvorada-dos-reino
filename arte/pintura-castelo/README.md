# Castelo pintado: portão de pedra e torre de nível 3

**Versão atual (v2):** `fonte/portao_v2.png` e `fonte/torre_v2.png`, feitas com os prompts de isometria 2:1, pedra cinzenta e sem chão.
- **Portão:** casa do portão de 5 casas. As torres ficam a 2 casas do centro do portão.
  - Os muros a 1 ou 2 casas ficam debaixo dela: os de trás são tapados, os da frente não se desenham.
  - O muro a 3 casas é cortado na parede da torre.
  - Fechado, a grade de ferro desce no arco.
- **Torre redonda:** raio do corpo 0,85, varanda a 3,3.

Os scripts reconhecem a v2 pelo nome do ficheiro. A v1 (folhas de 4 vistas) continua em `fonte/`.

As pinturas de 4 vistas estão em `fonte/`.

- **Portão de pedra:** a vista "lado direito" serve o portão ao longo de x; o espelho dessa vista serve a direção y.
  - As duas torres redondas ficam nas casas de muralha ao lado do portão. Esses muros deixam de ser desenhados (bit 256 do `bldVariant`), mas continuam a bloquear e a aceitar soldados.
  - O estado 0 (fechado) tem portas desenhadas no arco.
- **Torre de nível 3:** vem da vista frontal da torre redonda, sem o chão pintado. A varanda fica a 2,85, a altura onde ficam os soldados.

## Gerar de novo
```
python3 arte/pintura-castelo/scripts/portao_pintado.py arte/pintura-castelo/fonte/portao_v2.png .
python3 arte/pintura-castelo/scripts/torre_pintada.py arte/pintura-castelo/fonte/torre_v2.png /tmp/torre
python3 arte/edificios-3d/scripts/trocar_no_atlas.py /tmp/torre . torre_3
```

## Testes
- `tests/check_castelo_pintado.cjs`
- `tests/e2e/castelo_pintado.py`

As imagens das provas estão em `provas/`.

## v3: muralhas e torre redonda pintadas (pedido de 26/10)
- **Escala única:** 2× = 64 px por passo de casa em x ou y e 78,4 px por unidade de altura.
  - A torre é escalada só pelo diâmetro do corpo (1,7 casas), igual em todas as direções.
  - Os muros são endireitados por homografia: os 4 cantos da face da frente, medidos na pintura, vão para o retângulo certo no plano do jogo, com o caminho de ronda a 1,3. A perspetiva da pintura (a ponta perto ~1,3× maior) desaparece e os eixos ficam 2:1.
- **Âncora:** canto de cima da casa. A base fica sempre no chão; as margens transparentes não contam.
- **Segmentos sem torres:**
  - fatias de 1 casa ao longo de x (`x_mid_0..3`) e de y (`y_mid_0`), escolhidas por `tx % nx` para as ameias emendarem;
  - pontas verdadeiras da pintura (`*_fim`, `*_ini`) e muro sozinho (`*_iso`);
  - a torre é um objeto à parte.
- **Ligação à torre:** os muros entram na torre e são recortados pela forma do muro (`clipBox`). Os de trás passam por trás da torre e os da frente param na parede dela.
- **Faixas pretas:** eram a sombra do "apanha-sombras" do Blender, embutida nos atlas 3D (até 82 % de opacidade), mais a sombra do jogo por cima. Não eram nevoeiro, terreno nem sombra do jogo. O `scripts/../../muralhas-3d/scripts/tirar_sombra_embutida.py` tira-a dos 3 atlas.
- **Depuração:** `?iso=1` mostra a grelha, as áreas ocupadas (laranja = muro, azul = portão, amarelo = edifício), a âncora (quadrado amarelo), o centro da base (cruz ciano) e a linha do meio dos muros.
- Gerar: `python3 arte/pintura-castelo/scripts/muros_pintados.py .` (as medidas ficam em `muros_medidas.json`)
- Teste: `tests/e2e/muralhas_pintadas.py`. As provas estão em `provas/v3/`.
