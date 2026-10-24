# Muralhas 3D (paliçada, pedra, fortificada)

Mesmo estilo dos portões 3D (`arte/portoes-3d`): Blender por código, texturas Poly Haven CC0, câmara isométrica do jogo.
São 48 peças: 3 tipos × 16 ligações a vizinhos (a máscara de `bldVariant`: 1=+x, 2=+y, 4=−x, 8=−y).

- `scripts/montar_muro.py` corre no Blender do PC e usa as primitivas de `arte/portoes-3d/scripts/montar_portao2.py`
  (variáveis `WORK`, `OUT`, `TYPES`, `MASKS`, `TEX_DIR`, `GPU=1`). Cada braço é prolongado para lá da casa e o render
  é recortado à coluna de ecrã da casa, por isso as peças vizinhas encaixam sem costura. As retas são uma peça única
  e os braços dos cantos sobrepõem-se no centro, sem faces coplanares.
- `scripts/integrar_muro.py` recorta, empacota em `www/assets/edificios-extra/muralhas-3d.webp` e escreve `WALL3D_DATA`.
- No jogo: `wall3dSprite(type,o,mask)` em `bldSprite`; as bandeiras azuis das pontas tomam a cor da equipa.
