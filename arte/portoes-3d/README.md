# Portões 3D (Blender + texturas Poly Haven CC0)

5 variantes: madeira nas 3 idades, pedra no Bronze e no Ferro. Cada uma tem 2 direções (`x`, `y`) e 3 estados das portas
(fechada, a meio, aberta), num total de 30 quadros em `www/assets/edificios-extra/portoes-3d.webp`.

- `scripts/montar_portao2.py`: modelação por código, texturas reais com projeção em caixa, câmara isométrica do jogo (2:1, 2× do ecrã),
  contorno escuro e sombra neutra. Corre no Blender do PC (GPU): `TEX_DIR`, `OUT`, `VARS`, `SAMPLES`, `GPU=1`.
- `scripts/integrar_portao.py`: recorta, empacota e escreve `GATE3D_DATA` no `index.html`.
- No jogo: `gate3dSprite` escolhe a variante pela idade, a direção pela muralha vizinha e a porta por `e.open`
  (as portas abrem quando passam unidades do dono). As bandeiras azuis tomam a cor da equipa.
- `scripts/montar_portao.py` é a v1 (só texturas procedurais, corre sem GPU nem downloads).

Texturas (CC0, polyhaven.com): large_sandstone_blocks_01, medieval_blocks_02, weathered_brown_planks, brown_planks_05,
bark_brown_02, thatch_roof_angled, clay_roof_tiles_02, roof_slates_02.
